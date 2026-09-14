import logging
from typing import Optional

from beanie import PydanticObjectId
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.domains.auth.dependencies import get_current_user
from app.domains.auth.models import UserDocument
from app.domains.marketing_insights.schemas import MarketingInsightsResponse
from app.domains.marketing_insights.service import get_product_marketing_insights

logger = logging.getLogger("app.domains.marketing_insights.router")

router = APIRouter()


@router.get(
    "/{productId}/marketing-insights",
    response_model=MarketingInsightsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get 10-section Marketing Insights Panel for a product SKU",
)
async def get_marketing_insights_endpoint(
    productId: PydanticObjectId,
    start_date: Optional[str] = Query(default=None, description="Start date in ISO YYYY-MM-DD format"),
    end_date: Optional[str] = Query(default=None, description="End date in ISO YYYY-MM-DD format"),
    current_user: UserDocument = Depends(get_current_user),
) -> MarketingInsightsResponse:
    """
    Returns the comprehensive 10-section marketing insights payload for a product,
    combining verified transactional telemetry (sales trend, weekday velocity, price buckets)
    with AI-generated recommendations, promotional timing, audience profile, and competitor benchmarks.
    """
    try:
        return await get_product_marketing_insights(
            retailer_id=current_user.id,
            product_id=productId,
            start_date=start_date,
            end_date=end_date,
        )
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(ve),
        )
    except Exception as exc:
        logger.exception(f"Error computing marketing insights for product {productId}: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to compute marketing insights for the selected product.",
        )
