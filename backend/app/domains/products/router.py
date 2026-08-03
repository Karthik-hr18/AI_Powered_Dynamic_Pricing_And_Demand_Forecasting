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

    return ProductSummaryResponse(
        product=product,
        forecast=forecast,
        pricing=pricing,
        inventory=inventory,
        anomaly=anomaly,
        sparkline=sparkline,
    )
