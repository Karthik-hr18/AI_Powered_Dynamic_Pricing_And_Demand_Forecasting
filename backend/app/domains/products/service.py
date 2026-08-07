import asyncio
from datetime import datetime, timezone, timedelta
from typing import List, Optional, Tuple

from beanie import PydanticObjectId
from fastapi import HTTPException, status

from app.core.db.connection import get_database
from app.domains.products.models import ProductDocument
from app.domains.forecasting.models import ForecastCurrentDocument
from app.domains.pricing.models import PricingCurrentDocument
from app.domains.inventory.models import InventoryCurrentDocument
from app.domains.anomaly.models import AnomalyCurrentDocument
from app.domains.sales_data.models import ProcessedSaleDocument
from app.domains.products.schemas import ProductResponse, SparklinePoint


async def list_products(
    retailer_id: PydanticObjectId,
    page: int = 1,
    limit: int = 20,
    search: Optional[str] = None,
    category: Optional[str] = None,
) -> Tuple[List[ProductResponse], int]:
    """
    List all active products for a retailer with optional search and category filters.
    Enriches products with current pricing, forecast, inventory, and 30-day sales metrics.
    """
    # Enforce positive integers
    page = max(1, page)
    limit = max(1, limit)

    page = max(1, page)
    limit = max(1, limit)

    query_filter: Dict[str, Any] = {
        "retailer_id": retailer_id,
        "is_active": True,
    }

    if category:
        query_filter["category"] = category

    if search:
        search_escaped = search.replace("\\", "\\\\") # simple escape
        query_filter["$or"] = [
            {"sku": {"$regex": search_escaped, "$options": "i"}},
            {"product_name": {"$regex": search_escaped, "$options": "i"}},
        ]

    query = ProductDocument.find(query_filter)
    total_count = await query.count()

    products = await query.sort("-created_at").skip((page - 1) * limit).limit(limit).to_list()
    if not products:
        return [], total_count

    pids = [p.id for p in products]
    skus = [p.sku for p in products]
    db = get_database()

    pricing_task = PricingCurrentDocument.find({"retailer_id": retailer_id, "$or": [{"product_id": {"$in": pids}}, {"sku": {"$in": skus}}]}).to_list()
    forecast_task = ForecastCurrentDocument.find({"retailer_id": retailer_id, "$or": [{"product_id": {"$in": pids}}, {"sku": {"$in": skus}}]}).to_list()
    inventory_task = InventoryCurrentDocument.find({"retailer_id": retailer_id, "$or": [{"product_id": {"$in": pids}}, {"sku": {"$in": skus}}]}).to_list()

    sales_pipeline = [
        {
            "$match": {
                "retailer_id": retailer_id,
                "$or": [{"product_id": {"$in": pids}}, {"sku": {"$in": skus}}]
            }
        },
        {
            "$group": {
                "_id": {"$ifNull": ["$sku", "$product_id"]},
                "sales_30d": {"$sum": "$quantity_sold"},
                "revenue_30d": {"$sum": {"$multiply": ["$quantity_sold", "$selling_price"]}},
                "avg_price": {"$avg": "$selling_price"}
            }
        }
    ]
    sales_task = db["processed_sales"].aggregate(sales_pipeline).to_list()
    raw_sales_task = db["raw_sales"].aggregate(sales_pipeline).to_list()

    pricing_list, forecast_list, inventory_list, sales_agg, raw_sales_agg = await asyncio.gather(
        pricing_task, forecast_task, inventory_task, sales_task, raw_sales_task
    )

    pricing_map: Dict[Any, Any] = {}
    for pr in pricing_list:
        pricing_map[pr.product_id] = pr
        if hasattr(pr, "sku") and pr.sku:
            pricing_map[pr.sku] = pr

    forecast_map: Dict[Any, Any] = {}
    for fc in forecast_list:
        forecast_map[fc.product_id] = fc
        if hasattr(fc, "sku") and fc.sku:
            forecast_map[fc.sku] = fc

    inventory_map: Dict[Any, Any] = {}
    for inv in inventory_list:
        inventory_map[inv.product_id] = inv
        if hasattr(inv, "sku") and inv.sku:
            inventory_map[inv.sku] = inv

    sales_map: Dict[Any, Any] = {str(s["_id"]): s for s in sales_agg}
    raw_sales_map: Dict[Any, Any] = {str(r["_id"]): r for r in raw_sales_agg}

    items: List[ProductResponse] = []
    for p in products:
        pr = pricing_map.get(p.id) or pricing_map.get(p.sku)
        fc = forecast_map.get(p.id) or forecast_map.get(p.sku)
        inv = inventory_map.get(p.id) or inventory_map.get(p.sku)
        sl = sales_map.get(str(p.id)) or sales_map.get(p.sku, {})
        r_sl = raw_sales_map.get(str(p.id)) or raw_sales_map.get(p.sku, {})

        current_price = (pr.current_price if pr else None) or sl.get("avg_price") or r_sl.get("avg_price") or p.current_price or 0.0
        rec_price = pr.recommended_price if pr else None

        sales_30d = sl.get("sales_30d") or r_sl.get("sales_30d") or 0
        revenue_30d = sl.get("revenue_30d") or r_sl.get("revenue_30d") or 0.0

        f_7d = 0.0
        if fc and fc.horizon_7d and fc.horizon_7d.predictions:
            f_7d = sum(pt.predicted_quantity for pt in fc.horizon_7d.predictions)

        stock = inv.true_risk.current_inventory_level if (inv and inv.true_risk) else 0
        inv_status = inv.true_risk.classification.value if (inv and inv.true_risk) else (inv.mode.value if inv else "HEALTHY")

        item = ProductResponse(
            id=p.id,
            retailer_id=p.retailer_id,
            sku=p.sku,
            sku_display=p.sku_display,
            product_name=p.product_name,
            category=p.category,
            brand=p.brand,
            is_active=p.is_active,
            created_at=p.created_at,
            updated_at=p.updated_at,
            current_price=round(current_price, 2) if current_price is not None else None,
            recommended_price=round(rec_price, 2) if rec_price is not None else None,
            sales_30d=sales_30d,
            revenue_30d=round(revenue_30d, 2),
            forecast_7d=float(f_7d),
            stock_level=stock,
            inventory_status=inv_status,
        )
        items.append(item)

    return items, total_count


async def get_product_by_id(
    retailer_id: PydanticObjectId, product_id: PydanticObjectId
) -> ProductDocument:
    """
    Retrieve product metadata by product_id and validate tenant ownership.
    Raises 404 if product does not exist or belongs to another tenant.
    """
    product = await ProductDocument.get(product_id)
    if not product or product.retailer_id != retailer_id or not product.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    return product


async def get_product_summary_data(
    retailer_id: PydanticObjectId, product_id: PydanticObjectId
) -> Tuple[
    ProductDocument,
    Optional[ForecastCurrentDocument],
    Optional[PricingCurrentDocument],
    Optional[InventoryCurrentDocument],
    Optional[AnomalyCurrentDocument],
    List[SparklinePoint],
]:
    """
    Execute fanned-out parallel lookups across product metadata, pipelines,
    and historical sparkline data. Enforces tenant protection.
    """
    # 1. First fetch product and validate ownership
    product = await get_product_by_id(retailer_id, product_id)

    # 2. Parallel query all pipeline current tables + 30d sales sparkline with dual product_id/sku lookup
    match_query = {"retailer_id": retailer_id, "$or": [{"product_id": product_id}, {"sku": product.sku}]}

    forecast_task = ForecastCurrentDocument.find_one(match_query)
    pricing_task = PricingCurrentDocument.find_one(match_query)
    inventory_task = InventoryCurrentDocument.find_one(match_query)
    anomaly_task = AnomalyCurrentDocument.find_one(match_query)
    sales_task = ProcessedSaleDocument.find(match_query).sort("-date").limit(30).to_list()

    forecast, pricing, inventory, anomaly, sales_desc = await asyncio.gather(
        forecast_task, pricing_task, inventory_task, anomaly_task, sales_task
    )

    db = get_database()
    sales_records = list(reversed(sales_desc))

    if not sales_records:
        raw_sales_desc = await db["raw_sales"].find(match_query).sort("date", -1).limit(30).to_list()
        sales_records_raw = list(reversed(raw_sales_desc))
        sparkline = [
            SparklinePoint(
                date=r.get("date") or datetime.now(timezone.utc),
                quantity_sold=int(r.get("quantity_sold") or 0),
                selling_price=float(r.get("unit_price") or r.get("selling_price") or 0.0),
            )
            for r in sales_records_raw
        ]
    else:
        sparkline = [
            SparklinePoint(
                date=record.date,
                quantity_sold=record.quantity_sold,
                selling_price=float(record.selling_price or 0.0),
            )
            for record in sales_records
        ]

    return product, forecast, pricing, inventory, anomaly, sparkline
