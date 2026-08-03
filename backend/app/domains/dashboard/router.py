from fastapi import APIRouter, Depends, status

from app.domains.auth.dependencies import get_current_user
from app.domains.auth.models import UserDocument
from app.domains.dashboard.schemas import DashboardOverviewResponse
from app.domains.dashboard.service import get_dashboard_overview_data

router = APIRouter()


@router.get(
    "/overview",
    response_model=DashboardOverviewResponse,
    status_code=status.HTTP_200_OK,
    summary="Get dashboard aggregated KPIs and comparisons",
)
async def get_dashboard_overview(
    user: UserDocument = Depends(get_current_user),
):
    """
    Returns high-level retail metrics, actual vs forecast tracking, and the summary table.
    """
    return await get_dashboard_overview_data(retailer_id=user.id)
