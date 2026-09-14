import pytest
from datetime import datetime, timedelta, timezone
from httpx import AsyncClient, ASGITransport
from beanie import PydanticObjectId

from app.core.constants import UserRole, UploadStatus, PricingEligibilityStatus
from app.domains.auth.models import UserDocument
from app.domains.products.models import ProductDocument
from app.domains.sales_data.models import ProcessedSaleDocument
from app.domains.pricing.models import PricingCurrentDocument, BoundRange, CandidateGridEntry
from app.domains.uploads.models import UploadDocument
from app.domains.marketing_insights.schemas import GenerationMode
from app.domains.marketing_insights.service import _INSIGHTS_CACHE
from app.main import app


@pytest.fixture(autouse=True)
async def clean_collections():
    """Clean all relevant collections before and after each test."""
    _INSIGHTS_CACHE.clear()
    await UserDocument.find_all().delete()
    await ProductDocument.find_all().delete()
    await ProcessedSaleDocument.find_all().delete()
    await PricingCurrentDocument.find_all().delete()
    await UploadDocument.find_all().delete()
    yield
    _INSIGHTS_CACHE.clear()
    await UserDocument.find_all().delete()
    await ProductDocument.find_all().delete()
    await ProcessedSaleDocument.find_all().delete()
    await PricingCurrentDocument.find_all().delete()
    await UploadDocument.find_all().delete()


@pytest.fixture
def transport():
    return ASGITransport(app=app)


@pytest.mark.asyncio
async def test_weekday_normalization_and_seeding(transport):
    """
    Asserts exact Day-of-Week indexing:
    - 2026-06-07 is a known Sunday -> MUST land in bucket index 6 ('Sun')
    - 2026-06-10 is a known Wednesday -> MUST land in bucket index 2 ('Wed')
    """
    headers = {"Authorization": "Bearer mock-token-marketing-user"}
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Create authenticated retailer
        auth_res = await client.post(
            "/api/v1/auth/sync",
            json={"role": "RETAILER", "business_name": "Kirana Insights Mart"},
            headers=headers,
        )
        assert auth_res.status_code == 200
        retailer_id = PydanticObjectId(auth_res.json()["id"])
        upload_id = PydanticObjectId()

        # Create Product
        product = ProductDocument(
            retailer_id=retailer_id,
            sku="TEA-MASALA-500G",
            sku_display="Tea Masala 500g",
            product_name="Premium Assam Tea Masala",
            category="Beverages",
            current_price=120.0,
            original_price=150.0,
            first_seen_upload_id=upload_id,
            last_seen_upload_id=upload_id,
        )
        await product.insert()

        # Seed known Sunday: 2026-06-07
        sunday_dt = datetime(2026, 6, 7, 10, 0, 0, tzinfo=timezone.utc)
        sale_sunday = ProcessedSaleDocument(
            retailer_id=retailer_id,
            product_id=product.id,
            date=sunday_dt,
            quantity_sold=10,
            selling_price=120.0,
            day_of_week=6,  # Sunday
            is_weekend=True,
            feature_engineering_version="v1",
        )
        await sale_sunday.insert()

        # Seed known Wednesday: 2026-06-10
        wednesday_dt = datetime(2026, 6, 10, 15, 0, 0, tzinfo=timezone.utc)
        sale_wednesday = ProcessedSaleDocument(
            retailer_id=retailer_id,
            product_id=product.id,
            date=wednesday_dt,
            quantity_sold=25,
            selling_price=120.0,
            day_of_week=2,  # Wednesday
            is_weekend=False,
            feature_engineering_version="v1",
        )
        await sale_wednesday.insert()

        # Query marketing insights endpoint spanning 2026-06-01 to 2026-06-15
        res = await client.get(
            f"/api/v1/products/{product.id}/marketing-insights?start_date=2026-06-01&end_date=2026-06-15",
            headers=headers,
        )
        assert res.status_code == 200
        data = res.json()

        # Check Weekday Breakdown
        weekdays = data["sales_by_day_of_week"]
        assert len(weekdays) == 7

        # Index 2 = Wednesday -> 25 units
        assert weekdays[2]["day_name"] == "Wed"
        assert weekdays[2]["day_of_week"] == 2
        assert weekdays[2]["total_units_sold"] == 25

        # Index 6 = Sunday -> 10 units
        assert weekdays[6]["day_name"] == "Sun"
        assert weekdays[6]["day_of_week"] == 6
        assert weekdays[6]["total_units_sold"] == 10

        # Other days must be 0
        for dow in [0, 1, 3, 4, 5]:
            assert weekdays[dow]["total_units_sold"] == 0

        # Check Total Units Sold in trend
        trend = data["sales_trend_30d"]
        total_trend_units = sum(pt["units_sold"] for pt in trend)
        assert total_trend_units == 35


@pytest.mark.asyncio
async def test_price_buckets_and_fallback_labeling(transport):
    """
    Asserts price histogram distribution, price psychology, and truthful rule-based fallback branding.
    """
    headers = {"Authorization": "Bearer mock-token-price-user"}
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        auth_res = await client.post(
            "/api/v1/auth/sync",
            json={"role": "RETAILER", "business_name": "Price Test Shop"},
            headers=headers,
        )
        retailer_id = PydanticObjectId(auth_res.json()["id"])
        upload_id = PydanticObjectId()

        product = ProductDocument(
            retailer_id=retailer_id,
            sku="BASMATI-RICE-5KG",
            sku_display="Basmati Rice 5kg",
            product_name="Royal Basmati Rice",
            category="Staples",
            first_seen_upload_id=upload_id,
            last_seen_upload_id=upload_id,
        )
        await product.insert()

        pricing_curr = PricingCurrentDocument(
            retailer_id=retailer_id,
            product_id=product.id,
            upload_id=upload_id,
            eligibility_status=PricingEligibilityStatus.INSUFFICIENT_HISTORY,
            eligibility_reason="TEST_BASE",
            current_price=450.0,
            bound_pct=0.15,
            model_version="v1",
            run_id=PydanticObjectId(),
        )
        await pricing_curr.insert()

        # Seed 3 sales with different prices: $400 (discount), $450 (regular), $500 (peak)
        base_dt = datetime(2026, 8, 1, 12, 0, 0, tzinfo=timezone.utc)
        for i, (p, q) in enumerate([(400.0, 15), (450.0, 30), (500.0, 5)]):
            sale = ProcessedSaleDocument(
                retailer_id=retailer_id,
                product_id=product.id,
                date=base_dt + timedelta(days=i),
                quantity_sold=q,
                selling_price=p,
                day_of_week=(base_dt + timedelta(days=i)).weekday(),
                is_weekend=False,
                feature_engineering_version="v1",
            )
            await sale.insert()

        res = await client.get(
            f"/api/v1/products/{product.id}/marketing-insights?start_date=2026-08-01&end_date=2026-08-10",
            headers=headers,
        )
        assert res.status_code == 200
        data = res.json()

        # Verify truthful fallback labeling
        assert data["generation_mode"] == GenerationMode.RULE_BASED_FALLBACK.value
        assert "Deterministic Rule-based Heuristic" in data["data_source"]

        # Verify Price Psychology
        psych = data["price_psychology"]
        assert psych["current_price"] == 450.0
        assert psych["original_price"] == 500.0
        assert psych["discount_pct"] == 10.0

        # Verify Price Buckets
        buckets = data["sales_by_price_range"]
        assert len(buckets) == 3
        total_bucket_units = sum(b["units_sold"] for b in buckets)
        assert total_bucket_units == 50  # 15 + 30 + 5

        # Verify All 10 Sections are present
        assert len(data["recommendations"]) >= 3
        assert data["promotion_timing"]["best_days"]
        assert "Household" in data["audience_profile"]["primary_users"] or "Consumers" in data["audience_profile"]["primary_users"]
        assert data["competitor_benchmark"]["rows"]
        assert "Rule-Based Market Simulation" in data["competitor_benchmark"]["disclaimer"]
        assert len(data["risks_watchouts"]) >= 2
        assert data["expected_impact_30d"]["revenue_uplift_pct_range"]


@pytest.mark.asyncio
async def test_cache_invalidation_on_new_upload(transport):
    """
    Asserts caching behavior and cache invalidation when a new upload is registered for the retailer.
    """
    headers = {"Authorization": "Bearer mock-token-cache-user"}
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        auth_res = await client.post(
            "/api/v1/auth/sync",
            json={"role": "RETAILER", "business_name": "Cache Test Mart"},
            headers=headers,
        )
        retailer_id = PydanticObjectId(auth_res.json()["id"])
        upload_id = PydanticObjectId()

        product = ProductDocument(
            retailer_id=retailer_id,
            sku="SNACK-CHIPS-100G",
            sku_display="Snack Chips 100g",
            product_name="Spicy Potato Crisps",
            category="Snacks",
            current_price=30.0,
            first_seen_upload_id=upload_id,
            last_seen_upload_id=upload_id,
        )
        await product.insert()

        # Seed initial sale
        sale = ProcessedSaleDocument(
            retailer_id=retailer_id,
            product_id=product.id,
            date=datetime(2026, 8, 15, 10, 0, 0, tzinfo=timezone.utc),
            quantity_sold=20,
            selling_price=30.0,
            day_of_week=5,
            is_weekend=True,
            feature_engineering_version="v1",
        )
        await sale.insert()

        # 1. First call -> not cached
        res1 = await client.get(
            f"/api/v1/products/{product.id}/marketing-insights?start_date=2026-08-01&end_date=2026-08-20",
            headers=headers,
        )
        assert res1.status_code == 200
        assert res1.json()["is_cached"] is False

        # 2. Second immediate call -> is_cached == True
        res2 = await client.get(
            f"/api/v1/products/{product.id}/marketing-insights?start_date=2026-08-01&end_date=2026-08-20",
            headers=headers,
        )
        assert res2.status_code == 200
        assert res2.json()["is_cached"] is True

        # 3. Simulate new upload being processed for this retailer
        new_upload = UploadDocument(
            retailer_id=retailer_id,
            original_filename="new_batch.csv",
            file_size_bytes=5000,
            schema_mapping_used="standard",
            status=UploadStatus.COMPLETED,
        )
        await new_upload.insert()

        # 4. Third call -> cache busted due to new upload ID -> returns fresh response (is_cached is False)
        res3 = await client.get(
            f"/api/v1/products/{product.id}/marketing-insights?start_date=2026-08-01&end_date=2026-08-20",
            headers=headers,
        )
        assert res3.status_code == 200
        assert res3.json()["is_cached"] is False
