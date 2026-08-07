from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from beanie import PydanticObjectId

from app.domains.auth.dependencies import get_current_user
from app.domains.auth.models import UserDocument
from app.domains.products.schemas import (
    PaginatedProductsResponse,
    ProductResponse,
    ProductSummaryResponse,
)
from app.domains.products.service import (
    get_product_by_id,
    get_product_summary_data,
    list_products,
)

router = APIRouter()


@router.get(
    "",
    response_model=PaginatedProductsResponse,
    status_code=status.HTTP_200_OK,
    summary="List all active products for the retailer",
)
async def get_products(
    page: int = Query(default=1, ge=1, description="Page number"),
    limit: int = Query(default=20, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(default=None, description="Search sku or name"),
    category: Optional[str] = Query(default=None, description="Filter by category"),
    user: UserDocument = Depends(get_current_user),
):
    """
    Returns a paginated list of active products owned by the authenticated retailer.
    """
    items, total_count = await list_products(
        retailer_id=user.id,
        page=page,
        limit=limit,
        search=search,
        category=category,
    )

    pages_count = (total_count + limit - 1) // limit

    return PaginatedProductsResponse(
        items=items,
        total_count=total_count,
        page=page,
        limit=limit,
        pages_count=pages_count,
    )


@router.get(
    "/{productId}",
    response_model=ProductResponse,
    status_code=status.HTTP_200_OK,
    summary="Get single product metadata",
)
async def get_product(
    productId: PydanticObjectId,
    user: UserDocument = Depends(get_current_user),
):
    """
    Returns a single active product's metadata. Enforces tenant ownership checks.
    """
    return await get_product_by_id(retailer_id=user.id, product_id=productId)


@router.get(
    "/{productId}/summary",
    response_model=ProductSummaryResponse,
    status_code=status.HTTP_200_OK,
    summary="Aggregate detail view for a product",
)
async def get_product_summary(
    productId: PydanticObjectId,
    user: UserDocument = Depends(get_current_user),
):
    """
    Fans out to collect current forecast, pricing, inventory, anomaly states,
    and returns a 30-day actual sales sparkline. Enforces tenant ownership checks.
    """
    product, forecast, pricing, inventory, anomaly, sparkline = await get_product_summary_data(
        retailer_id=user.id, product_id=productId
    )

    current_price = pricing.current_price if pricing else None
    rec_price = pricing.recommended_price if pricing else None
    f_7d = sum(pt.predicted_quantity for pt in forecast.horizon_7d.predictions) if (forecast and forecast.horizon_7d and forecast.horizon_7d.predictions) else 0.0
    stock = inventory.true_risk.current_inventory_level if (inventory and inventory.true_risk) else 0
    inv_status = inventory.true_risk.classification.value if (inventory and inventory.true_risk) else (inventory.mode.value if inventory else "HEALTHY")
    
    sales_30d = sum(int(s.quantity_sold) for s in sparkline)
    revenue_30d = sum(float(s.quantity_sold * s.selling_price) for s in sparkline)

    prod_response = ProductResponse(
        id=product.id,
        retailer_id=product.retailer_id,
        sku=product.sku,
        sku_display=product.sku_display,
        product_name=product.product_name,
        category=product.category,
        brand=product.brand,
        is_active=product.is_active,
        created_at=product.created_at,
        updated_at=product.updated_at,
        current_price=round(current_price, 2) if current_price is not None else None,
        recommended_price=round(rec_price, 2) if rec_price is not None else None,
        sales_30d=sales_30d,
        revenue_30d=round(revenue_30d, 2),
        forecast_7d=float(f_7d),
        stock_level=int(stock),
        inventory_status=inv_status,
    )

    return ProductSummaryResponse(
        product=prod_response,
        forecast=forecast,
        pricing=pricing,
        inventory=inventory,
        anomaly=anomaly,
        sparkline=sparkline,
    )
