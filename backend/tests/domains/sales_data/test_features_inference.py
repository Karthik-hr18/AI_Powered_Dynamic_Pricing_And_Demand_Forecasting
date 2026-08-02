import io
import os
import sys
import pytest
import pandas as pd
from datetime import datetime, timedelta

# Add parent directory containing 'ml' to sys.path
curr = os.path.abspath(__file__)
parent_dir = None
for _ in range(10):
    curr = os.path.dirname(curr)
    if os.path.isdir(os.path.join(curr, "ml")):
        parent_dir = curr
        break

if parent_dir and parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from httpx import AsyncClient, ASGITransport
from beanie import PydanticObjectId

from app.core.config import settings
from app.core.constants import (
    UploadStatus,
    ForecastPipelineType,
    ForecastConfidenceLabel,
    PricingEligibilityStatus,
    AnomalyStage,
    AnomalyType
)
from app.domains.auth.models import UserDocument
from app.domains.products.models import ProductDocument
from app.domains.uploads.models import UploadDocument
from app.domains.sales_data.models import RawSaleDocument, ProcessedSaleDocument
from app.domains.forecasting.models import ForecastCurrentDocument, ForecastHistoryDocument
from app.domains.pricing.models import PricingCurrentDocument, PricingHistoryDocument
from app.domains.anomaly.models import AnomalyCurrentDocument

from ml.shared.feature_engineering import aggregate_raw_sales_daily, compute_rolling_features
from ml.forecasting.inference.predict import predict_demand
from ml.pricing.inference.predict import recommend_price
from ml.anomaly.inference.predict import detect_anomalies
from app.worker.main import process_single_upload, run_downstream_pipeline
from app.main import app


@pytest.fixture(autouse=True)
async def clean_collections():
    """Clean all relevant collection documents between runs."""
    await UserDocument.find_all().delete()
    await UploadDocument.find_all().delete()
    await ProductDocument.find_all().delete()
    await RawSaleDocument.find_all().delete()
    await ProcessedSaleDocument.find_all().delete()
    await ForecastCurrentDocument.find_all().delete()
    await ForecastHistoryDocument.find_all().delete()
    await PricingCurrentDocument.find_all().delete()
    await PricingHistoryDocument.find_all().delete()
    await AnomalyCurrentDocument.find_all().delete()
    yield
    await UserDocument.find_all().delete()
    await UploadDocument.find_all().delete()
    await ProductDocument.find_all().delete()
    await RawSaleDocument.find_all().delete()
    await ProcessedSaleDocument.find_all().delete()
    await ForecastCurrentDocument.find_all().delete()
    await ForecastHistoryDocument.find_all().delete()
    await PricingCurrentDocument.find_all().delete()
    await PricingHistoryDocument.find_all().delete()
    await AnomalyCurrentDocument.find_all().delete()


@pytest.fixture
def transport():
    return ASGITransport(app=app)


# --------------------------------------------------------------------------
# Unit Tests: Feature Engineering
# --------------------------------------------------------------------------

def test_daily_sales_aggregation_weighted_price():
    """Verify that daily aggregation sums quantity and computes quantity-weighted average price."""
    # Build list of raw sales mocks
    pid = PydanticObjectId()
    raw_sales = [
        RawSaleDocument(
            retailer_id=PydanticObjectId(),
            upload_id=PydanticObjectId(),
            product_id=pid,
            sku="prod-a",
            date=datetime(2026, 6, 1, 10, 0, 0),
            quantity_sold=5,
            selling_price=10.00,
            unit_cost=5.00,
            row_number_in_file=1,
            source_row_raw={}
        ),
        RawSaleDocument(
            retailer_id=PydanticObjectId(),
            upload_id=PydanticObjectId(),
            product_id=pid,
            sku="prod-a",
            date=datetime(2026, 6, 1, 15, 30, 0),
            quantity_sold=15,
            selling_price=8.00,
            unit_cost=5.00,
            row_number_in_file=2,
            source_row_raw={}
        )
    ]

    df_agg = aggregate_raw_sales_daily(raw_sales)
    assert not df_agg.empty
    assert len(df_agg) == 1
    
    row = df_agg.iloc[0]
    assert row["quantity_sold"] == 20
    # Weighted average: (5 * 10 + 15 * 8) / 20 = (50 + 120) / 20 = 170 / 20 = 8.5
    assert row["selling_price"] == 8.5
    assert row["unit_cost"] == 5.0


def test_compute_rolling_features_insufficient_history():
    """Verify that rolling features remain None when history is shorter than the windows (7 and 30 days)."""
    pid = PydanticObjectId()
    # 3 days of sales
    df_agg = pd.DataFrame([
        {"product_id": str(pid), "date": pd.Timestamp("2026-06-01"), "quantity_sold": 10.0, "selling_price": 5.0, "unit_cost": 3.0, "discount": 0.0, "store_id": "S1", "inventory_level": 100.0, "promotion_flag": False, "holiday_flag": False, "category": "Electronics"},
        {"product_id": str(pid), "date": pd.Timestamp("2026-06-02"), "quantity_sold": 12.0, "selling_price": 5.0, "unit_cost": 3.0, "discount": 0.0, "store_id": "S1", "inventory_level": 90.0, "promotion_flag": False, "holiday_flag": False, "category": "Electronics"},
        {"product_id": str(pid), "date": pd.Timestamp("2026-06-03"), "quantity_sold": 15.0, "selling_price": 5.5, "unit_cost": 3.0, "discount": 0.0, "store_id": "S1", "inventory_level": 80.0, "promotion_flag": False, "holiday_flag": False, "category": "Electronics"}
    ])

    features = compute_rolling_features(df_agg)
    assert len(features) == 3
    
    # 1st row should have lag_1d_quantity as None
    assert features[0]["lag_1d_quantity"] is None
    assert features[1]["lag_1d_quantity"] == 10
    
    # All 3 rows should have rolling averages as None
    for row in features:
        assert row["rolling_avg_7d"] is None
        assert row["rolling_avg_30d"] is None

    # Price changed on day 3: 5.0 -> 5.5
    assert features[0]["price_change_flag"] is False
    assert features[1]["price_change_flag"] is False
    assert features[2]["price_change_flag"] is True


# --------------------------------------------------------------------------
# Unit Tests: Models / Inference Skeletons
# --------------------------------------------------------------------------

def _create_mock_processed_sale(
    retailer_id, product_id, date, quantity_sold, selling_price
) -> ProcessedSaleDocument:
    return ProcessedSaleDocument(
        retailer_id=retailer_id,
        product_id=product_id,
        date=date,
        quantity_sold=quantity_sold,
        selling_price=selling_price,
        day_of_week=date.weekday(),
        is_weekend=date.weekday() in (5, 6),
        feature_engineering_version="1.0.0-mock"
    )


def test_predict_demand_eligibility():
    """Verify three-tier demand forecasting selection logic and schemas."""
    retailer_id = PydanticObjectId()
    product_id = PydanticObjectId()
    upload_id = PydanticObjectId()
    run_id = PydanticObjectId()
    trigger = "UPLOAD"

    # 1. Test Insufficient (5 days)
    history_short = [
        _create_mock_processed_sale(retailer_id, product_id, datetime(2026,6,1)+timedelta(days=i), 10.0, 5.0)
        for i in range(5)
    ]
    curr, hist = predict_demand(retailer_id, product_id, history_short, upload_id, run_id, trigger)
    assert curr.pipeline_type == ForecastPipelineType.INSUFFICIENT_DATA
    assert curr.horizon_7d is None
    assert curr.horizon_30d is None
    assert curr.eligibility_reason is not None

    # 2. Test Fallback (20 days)
    history_medium = [
        _create_mock_processed_sale(retailer_id, product_id, datetime(2026,6,1)+timedelta(days=i), 10.0, 5.0)
        for i in range(20)
    ]
    curr, hist = predict_demand(retailer_id, product_id, history_medium, upload_id, run_id, trigger)
    assert curr.pipeline_type == ForecastPipelineType.FALLBACK
    assert curr.horizon_7d is not None
    assert len(curr.horizon_7d.predictions) == 7
    assert curr.horizon_30d is None

    # 3. Test Full (35 days)
    history_long = [
        _create_mock_processed_sale(retailer_id, product_id, datetime(2026,6,1)+timedelta(days=i), 10.0, 5.0)
        for i in range(35)
    ]
    curr, hist = predict_demand(retailer_id, product_id, history_long, upload_id, run_id, trigger)
    assert curr.pipeline_type == ForecastPipelineType.FULL
    assert curr.horizon_7d is not None
    assert curr.horizon_30d is not None
    assert len(curr.horizon_7d.predictions) == 7
    assert len(curr.horizon_30d.predictions) == 30


def test_recommend_price_eligibility():
    """Verify pricing recommendation elastic candidate grid selection."""
    retailer_id = PydanticObjectId()
    product_id = PydanticObjectId()
    upload_id = PydanticObjectId()
    run_id = PydanticObjectId()
    trigger = "UPLOAD"

    # 1. Test Insufficient History (<7 days)
    history_short = [
        _create_mock_processed_sale(retailer_id, product_id, datetime(2026,6,1)+timedelta(days=i), 10.0, 5.0)
        for i in range(5)
    ]
    curr, hist = recommend_price(retailer_id, product_id, history_short, 5.0, upload_id, run_id, trigger)
    assert curr.eligibility_status == PricingEligibilityStatus.INSUFFICIENT_HISTORY
    assert curr.recommended_price is None

    # 2. Test Incomplete Price Variation (flat price history)
    history_flat_price = [
        _create_mock_processed_sale(retailer_id, product_id, datetime(2026,6,1)+timedelta(days=i), 10.0, 5.0)
        for i in range(10)
    ]
    curr, hist = recommend_price(retailer_id, product_id, history_flat_price, 5.0, upload_id, run_id, trigger)
    assert curr.eligibility_status == PricingEligibilityStatus.INSUFFICIENT_PRICE_VARIATION

    # 3. Test Eligible (varying prices)
    history_eligible = [
        _create_mock_processed_sale(retailer_id, product_id, datetime(2026,6,1)+timedelta(days=i), 10.0, (5.0 if i%2==0 else 6.0))
        for i in range(10)
    ]
    curr, hist = recommend_price(retailer_id, product_id, history_eligible, 5.0, upload_id, run_id, trigger)
    assert curr.eligibility_status == PricingEligibilityStatus.ELIGIBLE
    assert curr.bound_range is not None
    assert len(curr.candidate_grid) == 5
    assert curr.recommended_price > 0


def test_detect_anomalies_zscore():
    """Verify statistical Z-score outlier detection flags spike/drop anomalies."""
    retailer_id = PydanticObjectId()
    product_id = PydanticObjectId()
    upload_id = PydanticObjectId()

    # Create 10 days of flat history with one massive spike
    history = [
        _create_mock_processed_sale(retailer_id, product_id, datetime(2026,6,1)+timedelta(days=i), (10.0 if i != 8 else 100.0), 5.0)
        for i in range(10)
    ]

    doc = detect_anomalies(retailer_id, product_id, history, upload_id)
    assert doc.total_flagged_count == 1
    anomaly = doc.flagged_anomalies[0]
    assert anomaly.anomaly_type == AnomalyType.SPIKE
    assert anomaly.stage == AnomalyStage.POST_UPLOAD_ALERT
    assert "above the historical mean" in anomaly.explanation


# --------------------------------------------------------------------------
# End-to-End Integration Test: Worker Ingestion Downstream Pipeline
# --------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_worker_downstream_pipeline_execution(transport):
    """Verify end-to-end background ingestion runs preprocessors and generates forecast/pricing/anomaly documents."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Sync retailer user
        headers = {"Authorization": "Bearer mock-token-worker_pipeline_retailer"}
        sync_res = await client.post("/api/v1/auth/sync", json={"role": "RETAILER", "business_name": "MegaMart"}, headers=headers)
        retailer_id = PydanticObjectId(sync_res.json()["id"])

        # 2. Register upload job tracker
        upload = UploadDocument(
            retailer_id=retailer_id,
            original_filename="large_sales_history.csv",
            file_size_bytes=1000,
            schema_mapping_used="standard",
            status=UploadStatus.UPLOADED
        )
        await upload.insert()

        # 3. Write 35 rows of sales to generate sufficient history for FULL forecast pipeline
        # Alternate price between 9.99 and 10.99 to pass pricing elasticity variation requirement
        csv_rows = ["date,sku,quantity_sold,selling_price,category"]
        start_date = datetime(2026, 6, 1)
        for i in range(35):
            day_str = (start_date + timedelta(days=i)).strftime("%Y-%m-%d")
            price = "9.99" if i % 2 == 0 else "10.99"
            qty = "10"
            # Introduce a massive spike on day 30 to test anomaly capture
            if i == 29:
                qty = "100"
            csv_rows.append(f"{day_str},prod-xyz,{qty},{price},Groceries")

        csv_content = "\n".join(csv_rows) + "\n"
        
        os.makedirs(settings.UPLOAD_STORAGE_DIR, exist_ok=True)
        filepath = os.path.join(settings.UPLOAD_STORAGE_DIR, f"{upload.upload_id}.csv")
        with open(filepath, "w") as f:
            f.write(csv_content)

        try:
            # 4. Trigger the worker ingestion process
            await process_single_upload(upload)

            # 5. Assert Upload document finished successfully
            refreshed_upload = await UploadDocument.get(upload.id)
            assert refreshed_upload.status == UploadStatus.COMPLETED
            assert refreshed_upload.rows_ingested == 35

            # 6. Assert ProcessedSaleDocument rows are created and feature columns are calculated
            processed_sales = await ProcessedSaleDocument.find(
                ProcessedSaleDocument.retailer_id == retailer_id
            ).sort(ProcessedSaleDocument.date).to_list()
            assert len(processed_sales) == 35
            
            # Check calendar day continuity
            assert processed_sales[0].lag_1d_quantity is None
            assert processed_sales[1].lag_1d_quantity == 10
            
            # Check 7d rolling average was calculated for rows >= index 6
            assert processed_sales[5].rolling_avg_7d is None
            assert processed_sales[6].rolling_avg_7d is not None

            # 7. Assert Forecast current model has run and chosen the FULL pipeline tier
            forecast = await ForecastCurrentDocument.find_one(
                ForecastCurrentDocument.retailer_id == retailer_id
            )
            assert forecast is not None
            assert forecast.pipeline_type == ForecastPipelineType.FULL
            assert forecast.horizon_7d is not None
            assert forecast.horizon_30d is not None
            assert len(forecast.horizon_30d.predictions) == 30

            # 8. Assert Pricing optimization is eligible and evaluated candidate entries
            pricing = await PricingCurrentDocument.find_one(
                PricingCurrentDocument.retailer_id == retailer_id
            )
            assert pricing is not None
            assert pricing.eligibility_status == PricingEligibilityStatus.ELIGIBLE
            assert len(pricing.candidate_grid) == 5
            assert pricing.recommended_price > 0
            assert pricing.expected_revenue > 0

            # 9. Assert Anomaly detection was triggered and captured the spike on day 30
            anomaly = await AnomalyCurrentDocument.find_one(
                AnomalyCurrentDocument.retailer_id == retailer_id
            )
            assert anomaly is not None
            assert anomaly.total_flagged_count >= 1
            assert any(a.anomaly_type == AnomalyType.SPIKE for a in anomaly.flagged_anomalies)

        finally:
            if os.path.exists(filepath):
                os.remove(filepath)
