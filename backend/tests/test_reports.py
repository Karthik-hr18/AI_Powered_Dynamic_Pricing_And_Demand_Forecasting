import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_pdf_report_unauthorized():
    """Verify that unauthenticated requests to /api/v1/reports/pdf are rejected with 401."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/v1/reports/pdf")
        assert response.status_code == 401

@pytest.mark.asyncio
async def test_pdf_report_structure():
    """Verify PDF generator output bytes and headers."""
    from app.domains.reports.pdf_generator import build_analytics_pdf
    
    mock_dashboard_data = {
        "kpis": {"total_revenue_30d": 48320.0, "total_units_30d": 12450, "avg_price_30d": 3.88, "potential_revenue_gain": 2130.0, "potential_revenue_gain_pct": 5.6},
        "business_health": {"score": 94, "rating": "Excellent"},
        "goal_progress": {"target_revenue": 50000, "current_revenue": 48320.0, "progress_pct": 96.6},
        "highest_opportunity": {"sku": "SKU-0042", "product_name": "Organic Whole Milk 1L", "action_label": "Increase price by 6%", "current_price": 3.99, "recommended_price": 4.25, "expected_revenue_gain": 2130.0, "confidence_score": 92.0},
        "data_quality": {"quality_score_pct": 98.4, "total_rows": 14820, "duplicates_count": 12},
        "system_status": {"backend_status": "Running"},
        "inventory_health": {"healthy_pct": 80.0, "overstock_risk_pct": 15.0, "stockout_risk_pct": 5.0},
        "category_performance": [{"category": "Dairy", "revenue": 14200.0, "units": 3500}],
        "top_opportunities": [{"sku": "SKU-0042", "product_name": "Organic Whole Milk 1L", "current_price": 3.99, "recommended_price": 4.25, "expected_revenue_gain": 2130.0, "action_label": "Increase price"}],
        "critical_risks": [{"title": "Stockout Risk", "description": "Depleted in 4 days", "severity": "CRITICAL"}],
        "product_table": [{"sku_display": "SKU-0042", "product_name": "Organic Whole Milk 1L", "category": "Dairy", "forecast_7d": 318, "recommended_price": 4.25, "inventory_status": "HEALTHY"}],
        "forecast_vs_actual": [{"date": "Aug 01", "actual": 420, "forecast": 410}],
        "daily_sales": [{"date": "2026-08-01", "revenue": 1600.0}],
    }

    pdf_bytes = build_analytics_pdf(
        dashboard_data=mock_dashboard_data,
        retailer_name="test@retailer.com",
        business_name="Test Retailer Store",
    )

    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 5000  # Multi-page PDF output
    assert pdf_bytes.startswith(b"%PDF")  # Valid PDF header magic bytes
