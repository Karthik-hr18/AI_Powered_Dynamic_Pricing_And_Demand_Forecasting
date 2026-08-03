import pytest
from datetime import datetime, timedelta
from httpx import AsyncClient, ASGITransport
from beanie import PydanticObjectId

from app.core.constants import (
    ForecastConfidenceLabel,
    ForecastPipelineType,
    ForecastTriggeredBy,
    InventoryClassification,
    InventoryDemandTrend,
    InventoryMode,
    UserRole,
)
from app.domains.auth.models import UserDocument
from app.domains.products.models import ProductDocument
from app.domains.sales_data.models import ProcessedSaleDocument
from app.domains.forecasting.models import (
    ForecastCurrentDocument,
    ForecastHistoryDocument,
    ForecastHorizon,
    ForecastPrediction,
)
from app.domains.pricing.models import PricingCurrentDocument
from app.domains.inventory.models import (
    InventoryCurrentDocument,
    TrueRiskDetail,
    AdvisoryDetail,
)
from app.domains.anomaly.models import (
    AnomalyCurrentDocument,
    AnomalyStage,
    AnomalyType,
    FlaggedAnomaly,
)
from app.main import app


@pytest.fixture(autouse=True)
async def clean_collections():
    """Fixture to clean collections between tests."""
    await UserDocument.find_all().delete()
    await ProductDocument.find_all().delete()
    await ProcessedSaleDocument.find_all().delete()
    await ForecastCurrentDocument.find_all().delete()
    await ForecastHistoryDocument.find_all().delete()
    await PricingCurrentDocument.find_all().delete()
    await InventoryCurrentDocument.find_all().delete()
    await AnomalyCurrentDocument.find_all().delete()
    yield
    await UserDocument.find_all().delete()
    await ProductDocument.find_all().delete()
    await ProcessedSaleDocument.find_all().delete()
    await ForecastCurrentDocument.find_all().delete()
    await ForecastHistoryDocument.find_all().delete()
    await PricingCurrentDocument.find_all().delete()
    await InventoryCurrentDocument.find_all().delete()
    await AnomalyCurrentDocument.find_all().delete()


@pytest.fixture
def transport():
    return ASGITransport(app=app)


@pytest.mark.asyncio
async def test_get_products_list_pagination_and_search(transport):
    """Verify listing products paginates, filters by category, and searches correctly."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Setup retailer user
        headers = {"Authorization": "Bearer mock-token-products_retailer"}
        sync_res = await client.post(
            "/api/v1/auth/sync",
            json={"role": "RETAILER", "business_name": "Product Shop"},
            headers=headers,
        )
        retailer_id = PydanticObjectId(sync_res.json()["id"])
        upload_id = PydanticObjectId()

        # 2. Insert dummy products
        p1 = ProductDocument(
            retailer_id=retailer_id,
            sku="sku-apple",
            sku_display="Sku-Apple",
            product_name="Fresh Red Apples",
            category="Fruits",
            first_seen_upload_id=upload_id,
            last_seen_upload_id=upload_id,
        )
        p2 = ProductDocument(
            retailer_id=retailer_id,
            sku="sku-banana",
            sku_display="Sku-Banana",
            product_name="Organic Bananas",
            category="Fruits",
            first_seen_upload_id=upload_id,
            last_seen_upload_id=upload_id,
        )
        p3 = ProductDocument(
            retailer_id=retailer_id,
            sku="sku-carrot",
            sku_display="Sku-Carrot",
            product_name="Sweet Carrots",
            category="Vegetables",
            first_seen_upload_id=upload_id,
            last_seen_upload_id=upload_id,
        )
        await p1.insert()
        await p2.insert()
        await p3.insert()

        # 3. Test list products default pagination
        res_list = await client.get("/api/v1/products", headers=headers)
        assert res_list.status_code == 200
        data = res_list.json()
        assert data["total_count"] == 3
        assert len(data["items"]) == 3

        # 4. Test category filter
        res_cat = await client.get("/api/v1/products?category=Fruits", headers=headers)
        assert res_cat.status_code == 200
        data_cat = res_cat.json()
        assert data_cat["total_count"] == 2
        skus = [item["sku"] for item in data_cat["items"]]
        assert "sku-apple" in skus
        assert "sku-banana" in skus

        # 5. Test search filter
        res_search = await client.get("/api/v1/products?search=Banana", headers=headers)
        assert res_search.status_code == 200
        data_search = res_search.json()
        assert data_search["total_count"] == 1
        assert data_search["items"][0]["sku"] == "sku-banana"


@pytest.mark.asyncio
async def test_get_product_by_id_tenant_isolation(transport):
    """Verify GET product by ID enforces strict tenant boundaries (returns 404 on cross-tenant)."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Setup Retailer A
        headers_a = {"Authorization": "Bearer mock-token-retailer_a"}
        sync_a = await client.post(
            "/api/v1/auth/sync",
            json={"role": "RETAILER", "business_name": "Shop A"},
            headers=headers_a,
        )
        retailer_a_id = PydanticObjectId(sync_a.json()["id"])

        # 2. Setup Retailer B
        headers_b = {"Authorization": "Bearer mock-token-retailer_b"}
        sync_b = await client.post(
            "/api/v1/auth/sync",
            json={"role": "RETAILER", "business_name": "Shop B"},
            headers=headers_b,
        )
        retailer_b_id = PydanticObjectId(sync_b.json()["id"])

        upload_id = PydanticObjectId()

        # 3. Create Product A (Retailer A)
        p_a = ProductDocument(
            retailer_id=retailer_a_id,
            sku="prod-a",
            sku_display="Prod-A",
            product_name="Product A",
            first_seen_upload_id=upload_id,
            last_seen_upload_id=upload_id,
        )
        await p_a.insert()

        # 4. Retailer A fetches Product A -> Success
        res_a_success = await client.get(f"/api/v1/products/{p_a.id}", headers=headers_a)
        assert res_a_success.status_code == 200
        assert res_a_success.json()["sku"] == "prod-a"

        # 5. Retailer B fetches Product A -> 404 Not Found (Tenant isolation)
        res_b_fail = await client.get(f"/api/v1/products/{p_a.id}", headers=headers_b)
        assert res_b_fail.status_code == 404


@pytest.mark.asyncio
async def test_get_product_summary_data_aggregation(transport):
    """Verify summary endpoint aggregates all pipeline current status records + sparkline."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Setup retailer user
        headers = {"Authorization": "Bearer mock-token-summary_retailer"}
        sync_res = await client.post(
            "/api/v1/auth/sync",
            json={"role": "RETAILER", "business_name": "Summary Shop"},
            headers=headers,
        )
        retailer_id = PydanticObjectId(sync_res.json()["id"])
        upload_id = PydanticObjectId()
        run_id = PydanticObjectId()

        # 2. Insert product
        p = ProductDocument(
            retailer_id=retailer_id,
            sku="prod-summary",
            sku_display="Prod-Summary",
            product_name="Summary Item",
            first_seen_upload_id=upload_id,
            last_seen_upload_id=upload_id,
        )
        await p.insert()

        # 3. Insert pipeline status documents
        fc = ForecastCurrentDocument(
            retailer_id=retailer_id,
            product_id=p.id,
            pipeline_type=ForecastPipelineType.FULL,
            history_days_available=35,
            confidence_label=ForecastConfidenceLabel.HIGH,
            horizon_7d=ForecastHorizon(
                confidence="high",
                predictions=[
                    ForecastPrediction(
                        date=datetime.utcnow() + timedelta(days=i),
                        predicted_quantity=10.0 + i,
                    )
                    for i in range(7)
                ],
            ),
            model_version="1.0.0-test",
            run_id=run_id,
            upload_id=upload_id,
        )
        await fc.insert()

        pr = PricingCurrentDocument(
            retailer_id=retailer_id,
            product_id=p.id,
            eligibility_status="ELIGIBLE",
            current_price=10.0,
            recommended_price=11.50,
            expected_revenue=150.00,
            bound_pct=0.20,
            bound_range={"min": 8.0, "max": 12.0},
            candidate_grid=[
                {"candidate_price": 8.0, "estimated_demand": 15.0, "estimated_revenue": 120.0},
                {"candidate_price": 10.0, "estimated_demand": 12.0, "estimated_revenue": 120.0},
                {"candidate_price": 11.5, "estimated_demand": 13.0, "estimated_revenue": 149.5},
            ],
            model_version="1.0.0-test",
            run_id=run_id,
            upload_id=upload_id,
        )
        await pr.insert()

        inv = InventoryCurrentDocument(
            retailer_id=retailer_id,
            product_id=p.id,
            mode=InventoryMode.TRUE_RISK,
            true_risk=TrueRiskDetail(
                days_of_cover=12.5,
                classification=InventoryClassification.STOCKOUT_RISK,
                current_inventory_level=120,
                horizon_used="30d",
            ),
            forecast_run_id=run_id,
            upload_id=upload_id,
        )
        await inv.insert()

        anom = AnomalyCurrentDocument(
            retailer_id=retailer_id,
            product_id=p.id,
            total_flagged_count=1,
            has_unreviewed_alerts=True,
            flagged_anomalies=[
                FlaggedAnomaly(
                    date=datetime.utcnow() - timedelta(days=2),
                    stage=AnomalyStage.POST_UPLOAD_ALERT,
                    anomaly_type=AnomalyType.SPIKE,
                    severity_score=0.9,
                    explanation="Quantity is 10x historical average.",
                )
            ],
            model_version="1.0.0-test",
            run_id=run_id,
            upload_id=upload_id,
        )
        await anom.insert()

        # 4. Insert 3 days of historical processed sales (sparkline)
        sale1 = ProcessedSaleDocument(
            retailer_id=retailer_id,
            product_id=p.id,
            date=datetime.utcnow() - timedelta(days=3),
            quantity_sold=5.0,
            selling_price=10.0,
            day_of_week=0,
            is_weekend=False,
            feature_engineering_version="1.0.0-test",
        )
        sale2 = ProcessedSaleDocument(
            retailer_id=retailer_id,
            product_id=p.id,
            date=datetime.utcnow() - timedelta(days=2),
            quantity_sold=8.0,
            selling_price=10.0,
            day_of_week=1,
            is_weekend=False,
            feature_engineering_version="1.0.0-test",
        )
        await sale1.insert()
        await sale2.insert()

        # 5. Fetch product summary
        res = await client.get(f"/api/v1/products/{p.id}/summary", headers=headers)
        assert res.status_code == 200
        data = res.json()

        assert data["product"]["sku"] == "prod-summary"
        assert data["forecast"]["pipeline_type"] == "FULL"
        assert data["pricing"]["recommended_price"] == 11.50
        assert data["inventory"]["true_risk"]["classification"] == "STOCKOUT_RISK"
        assert len(data["anomaly"]["flagged_anomalies"]) == 1
        assert len(data["sparkline"]) == 2
        assert data["sparkline"][0]["quantity_sold"] == 5.0


@pytest.mark.asyncio
async def test_dashboard_overview_aggregation(transport):
    """Verify dashboard overview aggregates active alerts, confidence breakdown, KPIs and comparisons."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Setup retailer user
        headers = {"Authorization": "Bearer mock-token-dashboard_retailer"}
        sync_res = await client.post(
            "/api/v1/auth/sync",
            json={"role": "RETAILER", "business_name": "Dashboard Shop"},
            headers=headers,
        )
        retailer_id = PydanticObjectId(sync_res.json()["id"])
        upload_id = PydanticObjectId()
        run_id = PydanticObjectId()

        # 2. Setup 2 products
        p1 = ProductDocument(
            retailer_id=retailer_id,
            sku="p1",
            sku_display="P1",
            first_seen_upload_id=upload_id,
            last_seen_upload_id=upload_id,
        )
        p2 = ProductDocument(
            retailer_id=retailer_id,
            sku="p2",
            sku_display="P2",
            first_seen_upload_id=upload_id,
            last_seen_upload_id=upload_id,
        )
        await p1.insert()
        await p2.insert()

        # 3. Processed sales over last 30 days (total units = 10 + 20 = 30, revenue = 100 + 400 = 500)
        s1 = ProcessedSaleDocument(
            retailer_id=retailer_id,
            product_id=p1.id,
            date=datetime.utcnow() - timedelta(days=10),
            quantity_sold=10.0,
            selling_price=10.0,
            day_of_week=0,
            is_weekend=False,
            feature_engineering_version="1.0.0",
        )
        s2 = ProcessedSaleDocument(
            retailer_id=retailer_id,
            product_id=p2.id,
            date=datetime.utcnow() - timedelta(days=5),
            quantity_sold=20.0,
            selling_price=20.0,
            day_of_week=0,
            is_weekend=False,
            feature_engineering_version="1.0.0",
        )
        await s1.insert()
        await s2.insert()

        anom = AnomalyCurrentDocument(
            retailer_id=retailer_id,
            product_id=p1.id,
            total_flagged_count=0,
            has_unreviewed_alerts=True,
            flagged_anomalies=[],
            model_version="1.0.0-test",
            run_id=run_id,
            upload_id=upload_id,
        )
        await anom.insert()

        # 5. Confidence breakdown doc (one HIGH confidence, one LOW confidence)
        fc1 = ForecastCurrentDocument(
            retailer_id=retailer_id,
            product_id=p1.id,
            pipeline_type=ForecastPipelineType.FULL,
            history_days_available=35,
            confidence_label=ForecastConfidenceLabel.HIGH,
            model_version="1.0.0-test",
            run_id=run_id,
            upload_id=upload_id,
        )
        fc2 = ForecastCurrentDocument(
            retailer_id=retailer_id,
            product_id=p2.id,
            pipeline_type=ForecastPipelineType.FALLBACK,
            history_days_available=15,
            confidence_label=ForecastConfidenceLabel.LOW,
            model_version="1.0.0-test",
            run_id=run_id,
            upload_id=upload_id,
        )
        await fc1.insert()
        await fc2.insert()

        # 6. Fetch dashboard overview
        res = await client.get("/api/v1/dashboard/overview", headers=headers)
        assert res.status_code == 200
        data = res.json()

        assert data["kpis"]["total_revenue_30d"] == 500.0
        assert data["kpis"]["total_units_30d"] == 30.0
        # Avg price = 500 / 30 = 16.67
        assert data["kpis"]["avg_price_30d"] == 16.67
        assert data["kpis"]["active_alerts_count"] == 1
        assert data["kpis"]["confidence_breakdown"]["HIGH"] == 1
        assert data["kpis"]["confidence_breakdown"]["LOW"] == 1

        assert len(data["forecast_vs_actual"]) == 7
        assert len(data["product_table"]) == 2


@pytest.mark.asyncio
async def test_admin_retailers_list_and_status_toggle(transport):
    """Verify admin list and status update endpoints restrict access to admins and invalidate sessions."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Setup Admin user
        headers_admin = {"Authorization": "Bearer mock-token-test_admin"}
        await client.post(
            "/api/v1/auth/sync",
            json={"role": "ADMIN"},
            headers=headers_admin,
        )

        # 2. Setup Retailer user
        headers_retailer = {"Authorization": "Bearer mock-token-test_retailer"}
        sync_ret = await client.post(
            "/api/v1/auth/sync",
            json={"role": "RETAILER", "business_name": "Deactivate Shop"},
            headers=headers_retailer,
        )
        retailer_profile = sync_ret.json()
        retailer_id = PydanticObjectId(retailer_profile["id"])

        # 3. Test Retailer user tries to access admin list -> 403 Forbidden
        res_ret_list = await client.get("/api/v1/admin/retailers", headers=headers_retailer)
        assert res_ret_list.status_code == 403

        # 4. Admin accesses admin list -> Success (lists Retailer profile)
        res_admin_list = await client.get("/api/v1/admin/retailers", headers=headers_admin)
        assert res_admin_list.status_code == 200
        list_data = res_admin_list.json()
        assert len(list_data) == 1
        assert list_data[0]["email"] == "test_retailer@example.com"
        assert list_data[0]["is_active"] is True

        # 5. Admin updates status to False -> Success
        res_patch = await client.patch(
            f"/api/v1/admin/retailers/{retailer_id}/status",
            json={"is_active": False},
            headers=headers_admin,
        )
        assert res_patch.status_code == 200
        assert res_patch.json()["is_active"] is False

        # 6. Deactivated Retailer tries to call /auth/me -> 403 Forbidden (Blocked immediately)
        res_blocked = await client.get("/api/v1/auth/me", headers=headers_retailer)
        assert res_blocked.status_code == 403
        assert "deactivated" in res_blocked.json()["detail"]
