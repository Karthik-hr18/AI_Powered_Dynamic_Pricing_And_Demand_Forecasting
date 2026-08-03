import asyncio
from datetime import datetime, timedelta
from typing import List, Optional, Tuple

from beanie import PydanticObjectId
from fastapi import HTTPException, status

from app.domains.products.models import ProductDocument
from app.domains.forecasting.models import ForecastCurrentDocument
from app.domains.pricing.models import PricingCurrentDocument
from app.domains.inventory.models import InventoryCurrentDocument
from app.domains.anomaly.models import AnomalyCurrentDocument
from app.domains.sales_data.models import ProcessedSaleDocument
from app.domains.products.schemas import SparklinePoint


async def list_products(
    retailer_id: PydanticObjectId,
    page: int = 1,
    limit: int = 20,
    search: Optional[str] = None,
    category: Optional[str] = None,
) -> Tuple[List[ProductDocument], int]:
    """
    List all active products for a retailer with optional search and category filters.
    """
    # Enforce positive integers
    page = max(1, page)
    limit = max(1, limit)

    query_filter = {
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

    items = await query.sort(-ProductDocument.created_at).skip((page - 1) * limit).limit(limit).to_list()
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

    # 2. Parallel query all pipeline current tables + 30d sales sparkline
    start_date = datetime.utcnow() - timedelta(days=30)

    forecast_task = ForecastCurrentDocument.find_one(
        ForecastCurrentDocument.retailer_id == retailer_id,
        ForecastCurrentDocument.product_id == product_id,
    )
    pricing_task = PricingCurrentDocument.find_one(
        PricingCurrentDocument.retailer_id == retailer_id,
        PricingCurrentDocument.product_id == product_id,
    )
    inventory_task = InventoryCurrentDocument.find_one(
        InventoryCurrentDocument.retailer_id == retailer_id,
        InventoryCurrentDocument.product_id == product_id,
    )
    anomaly_task = AnomalyCurrentDocument.find_one(
        AnomalyCurrentDocument.retailer_id == retailer_id,
        AnomalyCurrentDocument.product_id == product_id,
    )
    sales_task = ProcessedSaleDocument.find(
        ProcessedSaleDocument.retailer_id == retailer_id,
        ProcessedSaleDocument.product_id == product_id,
        ProcessedSaleDocument.date >= start_date,
    ).sort(ProcessedSaleDocument.date).to_list()

    forecast, pricing, inventory, anomaly, sales_records = await asyncio.gather(
        forecast_task, pricing_task, inventory_task, anomaly_task, sales_task
    )

    # 3. Format sales timeline into SparklinePoints
    sparkline = [
        SparklinePoint(
            date=record.date,
            quantity_sold=record.quantity_sold,
            selling_price=record.selling_price,
        )
        for record in sales_records
    ]

    return product, forecast, pricing, inventory, anomaly, sparkline
