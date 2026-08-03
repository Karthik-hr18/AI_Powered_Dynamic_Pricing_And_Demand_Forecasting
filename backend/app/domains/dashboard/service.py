import asyncio
from datetime import datetime, timedelta
from typing import Dict, List

from beanie import PydanticObjectId

from app.domains.products.models import ProductDocument
from app.domains.forecasting.models import ForecastCurrentDocument, ForecastHistoryDocument
from app.domains.pricing.models import PricingCurrentDocument
from app.domains.inventory.models import InventoryCurrentDocument
from app.domains.anomaly.models import AnomalyCurrentDocument
from app.domains.sales_data.models import ProcessedSaleDocument
from app.domains.dashboard.schemas import (
    DashboardOverviewResponse,
    DashboardProductRow,
    ForecastVsActualPoint,
    KpiMetrics,
)


async def get_dashboard_overview_data(
    retailer_id: PydanticObjectId,
) -> DashboardOverviewResponse:
    """
    Orchestrates concurrent queries to aggregate KPIs, forecast comparison timelines,
    and product tables for the retailer's dashboard overview.
    """
    now = datetime.utcnow()
    start_date_30d = now - timedelta(days=30)

    # 1. Run KPI aggregates concurrently
    kpi_revenue_coro = ProcessedSaleDocument.get_pymongo_collection().aggregate(
        [
            {"$match": {"retailer_id": retailer_id, "date": {"$gte": start_date_30d}}},
            {
                "$group": {
                    "_id": None,
                    "total_revenue": {"$sum": {"$multiply": ["$quantity_sold", "$selling_price"]}},
                    "total_units": {"$sum": "$quantity_sold"},
                }
            },
        ]
    ).to_list(length=1)

    kpi_alerts_coro = AnomalyCurrentDocument.find(
        AnomalyCurrentDocument.retailer_id == retailer_id,
        AnomalyCurrentDocument.has_unreviewed_alerts == True,
    ).count()

    kpi_confidence_coro = ForecastCurrentDocument.get_pymongo_collection().aggregate(
        [
            {"$match": {"retailer_id": retailer_id}},
            {"$group": {"_id": "$confidence_label", "count": {"$sum": 1}}},
        ]
    ).to_list(length=100)

    revenue_res, alerts_count, confidence_res = await asyncio.gather(
        kpi_revenue_coro, kpi_alerts_coro, kpi_confidence_coro
    )

    # KPI Calculation mapping
    total_revenue_30d = 0.0
    total_units_30d = 0.0
    if revenue_res:
        total_revenue_30d = float(revenue_res[0].get("total_revenue", 0.0))
        total_units_30d = float(revenue_res[0].get("total_units", 0.0))

    avg_price_30d = (
        total_revenue_30d / total_units_30d if total_units_30d > 0 else 0.0
    )

    confidence_breakdown = {"HIGH": 0, "LOW": 0, "NONE": 0}
    for res in confidence_res:
        lbl = str(res.get("_id", "NONE"))
        if lbl in confidence_breakdown:
            confidence_breakdown[lbl] = res.get("count", 0)

    kpis = KpiMetrics(
        total_revenue_30d=round(total_revenue_30d, 2),
        total_units_30d=total_units_30d,
        avg_price_30d=round(avg_price_30d, 2),
        active_alerts_count=alerts_count,
        confidence_breakdown=confidence_breakdown,
    )

    # 2. Build 7-day Forecast vs Actual Timeline
    forecast_vs_actual: List[ForecastVsActualPoint] = []
    # For each of the last 7 calendar days
    for i in range(7, 0, -1):
        target_date = now.date() - timedelta(days=i)
        target_datetime_start = datetime(
            target_date.year, target_date.month, target_date.day, 0, 0, 0
        )
        target_datetime_end = datetime(
            target_date.year, target_date.month, target_date.day, 23, 59, 59
        )

        # Actual sales for target_date
        actuals_task = ProcessedSaleDocument.find(
            ProcessedSaleDocument.retailer_id == retailer_id,
            ProcessedSaleDocument.date >= target_datetime_start,
            ProcessedSaleDocument.date <= target_datetime_end,
        ).to_list()

        # Forecasts active/produced for target_date
        forecasts_task = ForecastHistoryDocument.find(
            {
                "retailer_id": retailer_id,
                "run_timestamp": {"$lte": target_datetime_end},
                "$or": [
                    {"superseded_at": None},
                    {"superseded_at": {"$gt": target_datetime_start}},
                ],
            }
        ).to_list()

        actuals, hist_forecasts = await asyncio.gather(actuals_task, forecasts_task)

        actual_units = sum(float(r.quantity_sold) for r in actuals)

        forecasted_units = 0.0
        for doc in hist_forecasts:
            predictions = []
            if doc.horizon_7d:
                predictions.extend(doc.horizon_7d.predictions)
            if doc.horizon_30d:
                predictions.extend(doc.horizon_30d.predictions)

            # Sum prediction matching this date
            for pred in predictions:
                if pred.date.date() == target_date:
                    forecasted_units += float(pred.predicted_quantity)
                    break

        forecast_vs_actual.append(
            ForecastVsActualPoint(
                date=target_datetime_start,
                actual_units=actual_units,
                forecasted_units=round(forecasted_units, 2),
            )
        )

    # 3. Build Product Table Overview Grid (bulk query fan-out)
    products_task = ProductDocument.find(
        ProductDocument.retailer_id == retailer_id, ProductDocument.is_active == True
    ).to_list()
    fc_task = ForecastCurrentDocument.find(
        ForecastCurrentDocument.retailer_id == retailer_id
    ).to_list()
    pr_task = PricingCurrentDocument.find(
        PricingCurrentDocument.retailer_id == retailer_id
    ).to_list()
    inv_task = InventoryCurrentDocument.find(
        InventoryCurrentDocument.retailer_id == retailer_id
    ).to_list()
    anom_task = AnomalyCurrentDocument.find(
        AnomalyCurrentDocument.retailer_id == retailer_id
    ).to_list()

    db_products, db_forecasts, db_pricings, db_inventories, db_anomalies = (
        await asyncio.gather(products_task, fc_task, pr_task, inv_task, anom_task)
    )

    forecast_map = {f.product_id: f for f in db_forecasts}
    pricing_map = {p.product_id: p for p in db_pricings}
    inventory_map = {i.product_id: i for i in db_inventories}
    anomaly_map = {a.product_id: a for a in db_anomalies}

    product_table: List[DashboardProductRow] = []
    for p in db_products:
        fc = forecast_map.get(p.id)
        pr = pricing_map.get(p.id)
        inv = inventory_map.get(p.id)
        anom = anomaly_map.get(p.id)

        forecast_7d = (
            sum(item.predicted_quantity for item in fc.horizon_7d.predictions)
            if fc and fc.horizon_7d
            else None
        )
        recommended_price = pr.recommended_price if pr else None

        inventory_status = "UNKNOWN"
        if inv:
            if inv.mode == "TRUE_RISK" and inv.true_risk:
                inventory_status = inv.true_risk.classification.value
            elif inv.mode == "ADVISORY" and inv.advisory:
                inventory_status = inv.advisory.demand_trend.value

        alert_status = anom.has_unreviewed_alerts if anom else False

        product_table.append(
            DashboardProductRow(
                id=p.id,
                sku=p.sku,
                sku_display=p.sku_display,
                product_name=p.product_name,
                category=p.category,
                forecast_7d=round(forecast_7d, 2) if forecast_7d is not None else None,
                recommended_price=recommended_price,
                inventory_status=inventory_status,
                alert_status=alert_status,
            )
        )

    return DashboardOverviewResponse(
        kpis=kpis, forecast_vs_actual=forecast_vs_actual, product_table=product_table
    )
