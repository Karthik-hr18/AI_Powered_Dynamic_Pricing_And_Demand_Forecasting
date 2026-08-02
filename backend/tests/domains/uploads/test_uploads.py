import io
import os
import pytest
from httpx import AsyncClient, ASGITransport
from beanie import PydanticObjectId

from app.core.config import settings
from app.core.constants import UploadStatus, UserRole
from app.domains.auth.models import UserDocument
from app.domains.products.models import ProductDocument
from app.domains.uploads.models import UploadDocument
from app.domains.sales_data.models import RawSaleDocument
from app.worker.main import process_single_upload
from app.main import app


@pytest.fixture(autouse=True)
async def clean_collections():
    """Fixture to clean collections between tests."""
    await UserDocument.find_all().delete()
    await UploadDocument.find_all().delete()
    await ProductDocument.find_all().delete()
    await RawSaleDocument.find_all().delete()
    yield
    await UserDocument.find_all().delete()
    await UploadDocument.find_all().delete()
    await ProductDocument.find_all().delete()
    await RawSaleDocument.find_all().delete()


@pytest.fixture
def transport():
    return ASGITransport(app=app)


# --------------------------------------------------------------------------
# Router API Tests
# --------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_upload_csv_success(transport):
    """Verify that a valid CSV file upload is accepted and stored."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Create mock retailer user
        headers = {"Authorization": "Bearer mock-token-upload_retailer"}
        await client.post("/api/v1/auth/sync", json={"role": "RETAILER", "business_name": "Test Shop"}, headers=headers)

        # Valid CSV content
        csv_data = "date,sku,quantity_sold,selling_price\n2026-06-01,prod-100,10,19.99\n"
        files = {"file": ("sales_data.csv", io.BytesIO(csv_data.encode()), "text/csv")}
        data = {"schema_mapping_used": "standard"}

        response = await client.post("/api/v1/uploads/", files=files, data=data, headers=headers)
        assert response.status_code == 202
        
        res_data = response.json()
        assert res_data["status"] == "UPLOADED"
        assert res_data["original_filename"] == "sales_data.csv"
        
        # Verify file exists on local storage
        filepath = os.path.join(settings.UPLOAD_STORAGE_DIR, f"{res_data['upload_id']}.csv")
        assert os.path.exists(filepath)
        
        # Clean up file on disk
        if os.path.exists(filepath):
            os.remove(filepath)


@pytest.mark.asyncio
async def test_upload_csv_missing_headers_rejected(transport):
    """Verify that an invalid CSV file upload missing mandatory headers is rejected immediately."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        headers = {"Authorization": "Bearer mock-token-upload_retailer_fail"}
        await client.post("/api/v1/auth/sync", json={"role": "RETAILER", "business_name": "Test Shop"}, headers=headers)

        # Missing 'selling_price' column
        csv_data = "date,sku,quantity_sold\n2026-06-01,prod-100,10\n"
        files = {"file": ("sales_data_bad.csv", io.BytesIO(csv_data.encode()), "text/csv")}
        
        response = await client.post("/api/v1/uploads/", files=files, headers=headers)
        assert response.status_code == 422
        
        detail = response.json()["detail"]
        assert "Missing mandatory column header" in str(detail["errors"])
        
        # Check DB status is REJECTED
        upload = await UploadDocument.find_one(UploadDocument.upload_id == detail["upload_id"])
        assert upload.status == UploadStatus.REJECTED
        assert len(upload.validation_errors) > 0

        # Clean up file on disk
        filepath = os.path.join(settings.UPLOAD_STORAGE_DIR, f"{detail['upload_id']}.csv")
        if os.path.exists(filepath):
            os.remove(filepath)


@pytest.mark.asyncio
async def test_list_and_get_uploads(transport):
    """Verify listing and detail endpoints for uploads."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        headers = {"Authorization": "Bearer mock-token-retailer_history"}
        await client.post("/api/v1/auth/sync", json={"role": "RETAILER", "business_name": "Test Shop"}, headers=headers)

        # Upload a dummy file first
        csv_data = "date,sku,quantity_sold,selling_price\n2026-06-01,prod-100,10,19.99\n"
        files = {"file": ("history.csv", io.BytesIO(csv_data.encode()), "text/csv")}
        
        upload_res = await client.post("/api/v1/uploads/", files=files, headers=headers)
        upload_id = upload_res.json()["upload_id"]

        # 1. Test List route
        list_res = await client.get("/api/v1/uploads/", headers=headers)
        assert list_res.status_code == 200
        assert len(list_res.json()) >= 1
        
        # 2. Test Get detail route
        detail_res = await client.get(f"/api/v1/uploads/{upload_id}", headers=headers)
        assert detail_res.status_code == 200
        assert detail_res.json()["upload_id"] == upload_id

        # Clean up file
        filepath = os.path.join(settings.UPLOAD_STORAGE_DIR, f"{upload_id}.csv")
        if os.path.exists(filepath):
            os.remove(filepath)


# --------------------------------------------------------------------------
# Background Worker Ingestion Tests
# --------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_worker_ingestion_success(transport):
    """Verify background worker processes valid CSV rows, registers SKUs, and saves raw sales."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        headers = {"Authorization": "Bearer mock-token-worker_retailer"}
        sync_res = await client.post("/api/v1/auth/sync", json={"role": "RETAILER", "business_name": "Test Shop"}, headers=headers)
        retailer_id = PydanticObjectId(sync_res.json()["id"])

        # 1. Create upload job tracker
        upload = UploadDocument(
            retailer_id=retailer_id,
            original_filename="dataset.csv",
            file_size_bytes=100,
            schema_mapping_used="standard",
            status=UploadStatus.UPLOADED
        )
        await upload.insert()

        # 2. Save mock CSV file on disk
        os.makedirs(settings.UPLOAD_STORAGE_DIR, exist_ok=True)
        filepath = os.path.join(settings.UPLOAD_STORAGE_DIR, f"{upload.upload_id}.csv")
        csv_content = (
            "date,sku,quantity_sold,selling_price,category,holiday_flag\n"
            "2026-06-01,SKU-A,5,10.99,Electronics,1\n"
            "2026-06-02,SKU-A,15,9.99,Electronics,0\n"
            "2026-06-02,SKU-B,3,15.50,Apparel,0\n"
        )
        with open(filepath, "w") as f:
            f.write(csv_content)

        try:
            # 3. Call process task directly (simulating worker polling pick up)
            await process_single_upload(upload)

            # 4. Assert updated job tracking status
            refreshed_upload = await UploadDocument.get(upload.id)
            assert refreshed_upload.status == UploadStatus.COMPLETED
            assert refreshed_upload.row_count == 3
            assert refreshed_upload.rows_ingested == 3
            assert refreshed_upload.rows_rejected == 0
            assert len(refreshed_upload.row_warnings) == 0

            # 5. Assert product auto-registrations
            sku_a = await ProductDocument.find_one(ProductDocument.sku == "sku-a")
            assert sku_a is not None
            assert sku_a.sku_display == "SKU-A"
            assert sku_a.category == "Electronics"

            sku_b = await ProductDocument.find_one(ProductDocument.sku == "sku-b")
            assert sku_b is not None
            assert sku_b.sku_display == "SKU-B"

            # 6. Assert raw sales ingestion rows
            sales = await RawSaleDocument.find(RawSaleDocument.upload_id == upload.id).to_list()
            assert len(sales) == 3
            # Check values of first row
            assert sales[0].sku == "sku-a"
            assert sales[0].quantity_sold == 5
            assert sales[0].selling_price == 10.99
            assert sales[0].holiday_flag is True

        finally:
            if os.path.exists(filepath):
                os.remove(filepath)


@pytest.mark.asyncio
async def test_worker_ingestion_with_warnings(transport):
    """Verify background worker processes valid rows while gracefully recording warnings for malformed rows."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        headers = {"Authorization": "Bearer mock-token-worker_retailer_warn"}
        sync_res = await client.post("/api/v1/auth/sync", json={"role": "RETAILER", "business_name": "Test Shop"}, headers=headers)
        retailer_id = PydanticObjectId(sync_res.json()["id"])

        upload = UploadDocument(
            retailer_id=retailer_id,
            original_filename="dataset_warnings.csv",
            file_size_bytes=100,
            schema_mapping_used="standard",
            status=UploadStatus.UPLOADED
        )
        await upload.insert()

        filepath = os.path.join(settings.UPLOAD_STORAGE_DIR, f"{upload.upload_id}.csv")
        csv_content = (
            "date,sku,quantity_sold,selling_price\n"
            "2026-06-01,SKU-A,5,10.99\n"
            "invalid-date,SKU-A,15,9.99\n" # bad date
            "2026-06-02,,10,5.00\n"        # bad sku
            "2026-06-02,SKU-B,-5,15.50\n"  # bad negative qty
            "2026-06-03,SKU-B,2,-1.50\n"   # bad negative price
        )
        with open(filepath, "w") as f:
            f.write(csv_content)

        try:
            await process_single_upload(upload)

            refreshed_upload = await UploadDocument.get(upload.id)
            assert refreshed_upload.status == UploadStatus.COMPLETED_WITH_WARNINGS
            assert refreshed_upload.row_count == 5
            assert refreshed_upload.rows_ingested == 1
            assert refreshed_upload.rows_rejected == 4
            assert len(refreshed_upload.row_warnings) == 4

            # Check specific warnings rows
            warnings = refreshed_upload.row_warnings
            assert warnings[0].row == 3
            assert "Date format must be YYYY-MM-DD" in warnings[0].reason
            assert warnings[1].row == 4
            assert "Missing mandatory row values: sku" in warnings[1].reason
            assert warnings[2].row == 5
            assert "quantity_sold must be a non-negative integer" in warnings[2].reason
            assert warnings[3].row == 6
            assert "selling_price must be a non-negative float" in warnings[3].reason

        finally:
            if os.path.exists(filepath):
                os.remove(filepath)
