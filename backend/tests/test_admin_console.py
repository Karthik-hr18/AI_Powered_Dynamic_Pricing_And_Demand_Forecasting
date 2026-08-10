import pytest
from httpx import AsyncClient, ASGITransport
from beanie import PydanticObjectId

from app.main import app
from app.domains.auth.models import UserDocument
from app.domains.uploads.models import UploadDocument
from app.domains.admin.models import ActivityLogDocument
from app.core.constants import UploadStatus, UserRole


@pytest.fixture
def transport():
    return ASGITransport(app=app)


@pytest.mark.asyncio
async def test_admin_console_full_suite(transport):
    """
    Comprehensive tests for the Admin Console API suite:
    - Overview metrics and time-series
    - Retailers list and detail drawer
    - Data operations monitoring and sanitized errors
    - Activity log audit trail
    - Platform health checks
    - Administrative CSV reports export
    - Strict 403 authorization rejection for non-admins
    """
    # Clean up test collections
    await UserDocument.find_all().delete()
    await UploadDocument.find_all().delete()
    await ActivityLogDocument.find_all().delete()

    # 1. Directly insert Admin user with ADMIN role
    admin_user = UserDocument(
        firebase_uid="admin_saas_ops",
        email="admin_saas_ops@example.com",
        role=UserRole.ADMIN,
        is_active=True,
    )
    await admin_user.insert()
    headers_admin = {"Authorization": "Bearer mock-token-admin_saas_ops"}

    # 2. Directly insert Retailer user
    retailer_user = UserDocument(
        firebase_uid="retailer_shop_1",
        email="retailer_shop_1@example.com",
        business_name="Metro Hypermarket",
        role=UserRole.RETAILER,
        is_active=True,
    )
    await retailer_user.insert()
    retailer_id = retailer_user.id
    headers_retailer = {"Authorization": "Bearer mock-token-retailer_shop_1"}

    # Seed sample upload document for retailer
    test_upload = UploadDocument(
        retailer_id=retailer_id,
        original_filename="metro_sales_aug2026.csv",
        file_size_bytes=102400,
        row_count=500,
        rows_ingested=500,
        schema_mapping_used="STANDARD",
        status=UploadStatus.COMPLETED,
        current_stage="COMPLETED",
    )
    await test_upload.insert()

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # ----------------------------------------------------------------------
        # A. Non-admin access tests (Strict 403 Forbidden)
        # ----------------------------------------------------------------------
        res = await client.get("/api/v1/admin/overview", headers=headers_retailer)
        assert res.status_code == 403

        res = await client.get("/api/v1/admin/retailers", headers=headers_retailer)
        assert res.status_code == 403

        res = await client.get(f"/api/v1/admin/retailers/{retailer_id}/details", headers=headers_retailer)
        assert res.status_code == 403

        res = await client.get("/api/v1/admin/data-operations", headers=headers_retailer)
        assert res.status_code == 403

        res = await client.get("/api/v1/admin/activity-log", headers=headers_retailer)
        assert res.status_code == 403

        res = await client.get("/api/v1/admin/platform-health", headers=headers_retailer)
        assert res.status_code == 403

        res = await client.get("/api/v1/admin/reports/export?type=retailers", headers=headers_retailer)
        assert res.status_code == 403

        # ----------------------------------------------------------------------
        # B. Admin Authorized Endpoints Verification
        # ----------------------------------------------------------------------
        # 1. Admin Overview
        res = await client.get("/api/v1/admin/overview", headers=headers_admin)
        assert res.status_code == 200
        overview = res.json()
        assert overview["total_retailers"] >= 1
        assert overview["active_retailers"] >= 1
        assert "upload_breakdown" in overview
        assert len(overview["retailer_growth_30d"]) == 30
        assert overview["platform_health_status"] in ("HEALTHY", "DEGRADED")

        # 2. Retailers List
        res = await client.get("/api/v1/admin/retailers", headers=headers_admin)
        assert res.status_code == 200
        retailers = res.json()
        assert len(retailers) >= 1
        metro = next((r for r in retailers if r["business_name"] == "Metro Hypermarket"), None)
        assert metro is not None
        assert metro["dataset_count"] >= 1

        # 3. Retailer Detail Drawer
        res = await client.get(f"/api/v1/admin/retailers/{retailer_id}/details", headers=headers_admin)
        assert res.status_code == 200
        detail = res.json()
        assert detail["retailer"]["business_name"] == "Metro Hypermarket"
        assert len(detail["recent_uploads"]) >= 1

        # 4. Retailer Status Toggle
        res = await client.patch(
            f"/api/v1/admin/retailers/{retailer_id}/status",
            json={"is_active": False},
            headers=headers_admin,
        )
        assert res.status_code == 200
        assert res.json()["is_active"] is False

        # Reactivate
        res = await client.patch(
            f"/api/v1/admin/retailers/{retailer_id}/status",
            json={"is_active": True},
            headers=headers_admin,
        )
        assert res.status_code == 200
        assert res.json()["is_active"] is True

        # 5. Data Operations Monitoring
        res = await client.get("/api/v1/admin/data-operations", headers=headers_admin)
        assert res.status_code == 200
        ops = res.json()
        assert ops["total_count"] >= 1
        assert len(ops["uploads"]) >= 1
        assert ops["stats"]["total"] >= 1

        # 6. Activity Log Audit Trail
        res = await client.get("/api/v1/admin/activity-log", headers=headers_admin)
        assert res.status_code == 200
        logs = res.json()
        assert logs["total_count"] >= 1
        assert len(logs["events"]) >= 1

        # 7. Platform Health Checks
        res = await client.get("/api/v1/admin/platform-health", headers=headers_admin)
        assert res.status_code == 200
        health = res.json()
        assert health["overall_status"] in ("HEALTHY", "DEGRADED", "UNAVAILABLE")
        assert len(health["services"]) >= 4

        # 8. Admin Reports Export
        res = await client.get("/api/v1/admin/reports/export?type=retailers", headers=headers_admin)
        assert res.status_code == 200
        assert "text/csv" in res.headers["content-type"]
        assert "Retailer ID,Business Name" in res.text

        res = await client.get("/api/v1/admin/reports/export?type=uploads", headers=headers_admin)
        assert res.status_code == 200
        assert "Upload ID,Retailer Business Name" in res.text

        res = await client.get("/api/v1/admin/reports/export?type=activity", headers=headers_admin)
        assert res.status_code == 200
        assert "Timestamp (UTC),Actor Email" in res.text
