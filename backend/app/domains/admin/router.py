from typing import List, Optional
from beanie import PydanticObjectId
from fastapi import APIRouter, Depends, Query, Response, status

from app.core.constants import UserRole
from app.domains.admin.schemas import (
    AdminActivityLogResponse,
    AdminDataOperationsResponse,
    AdminOverviewResponse,
    AdminRetailerDetailResponse,
    AdminRetailerItem,
    PlatformHealthResponse,
    RetailerStatusUpdate,
)
from app.domains.admin.service import (
    check_platform_health,
    generate_admin_csv_report,
    get_activity_logs,
    get_admin_overview,
    get_data_operations,
    get_retailer_detail,
    list_retailers_with_metrics,
    toggle_retailer_status,
)
from app.domains.auth.dependencies import get_current_user, require_role
from app.domains.auth.models import UserDocument
from app.domains.auth.schemas import UserResponse

router = APIRouter()


@router.get(
    "/overview",
    response_model=AdminOverviewResponse,
    status_code=status.HTTP_200_OK,
    summary="Platform-wide operational overview dashboard (Admin only)",
    dependencies=[Depends(require_role([UserRole.ADMIN]))],
)
async def get_overview():
    """
    Returns platform-level KPIs, 30-day retailer registration growth series,
    upload lifecycle breakdown, and recent platform activity feed.
    """
    return await get_admin_overview()


@router.get(
    "/retailers",
    response_model=List[AdminRetailerItem],
    status_code=status.HTTP_200_OK,
    summary="List all registered retailers enriched with usage metrics (Admin only)",
    dependencies=[Depends(require_role([UserRole.ADMIN]))],
)
async def get_retailers():
    """
    Returns master retailer directory with dataset counts, sales rows, and last active dates.
    """
    return await list_retailers_with_metrics()


@router.get(
    "/retailers/{userId}/details",
    response_model=AdminRetailerDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Get extended retailer profile for detail drawer (Admin only)",
    dependencies=[Depends(require_role([UserRole.ADMIN]))],
)
async def get_retailer_profile(userId: PydanticObjectId):
    """
    Returns full profile information, recent uploads, and activity logs for a specific retailer.
    """
    return await get_retailer_detail(retailer_id=userId)


@router.patch(
    "/retailers/{userId}/status",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Enable or disable a retailer user account (Admin only)",
)
async def patch_retailer_status(
    userId: PydanticObjectId,
    status_data: RetailerStatusUpdate,
    admin_user: UserDocument = Depends(require_role([UserRole.ADMIN])),
):
    """
    Toggles the active state of a retailer user account and writes an audit event.
    """
    return await toggle_retailer_status(
        user_id=userId,
        is_active=status_data.is_active,
        admin_user=admin_user,
    )


@router.get(
    "/data-operations",
    response_model=AdminDataOperationsResponse,
    status_code=status.HTTP_200_OK,
    summary="Monitor all CSV upload and dataset ingestion jobs (Admin only)",
    dependencies=[Depends(require_role([UserRole.ADMIN]))],
)
async def get_operations(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    status: Optional[str] = Query(default=None),
    search: Optional[str] = Query(default=None),
):
    """
    Returns paginated CSV ingestion operations across all retailers with failure reasons.
    """
    return await get_data_operations(
        page=page,
        limit=limit,
        status_filter=status,
        search=search,
    )


@router.get(
    "/activity-log",
    response_model=AdminActivityLogResponse,
    status_code=status.HTTP_200_OK,
    summary="Server-paginated audit trail of platform events (Admin only)",
    dependencies=[Depends(require_role([UserRole.ADMIN]))],
)
async def get_activity(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=25, ge=1, le=100),
    action: Optional[str] = Query(default=None),
    status: Optional[str] = Query(default=None),
    search: Optional[str] = Query(default=None),
):
    """
    Returns server-paginated platform activity log entries with filtering.
    """
    return await get_activity_logs(
        page=page,
        limit=limit,
        action_filter=action,
        status_filter=status,
        search=search,
    )


@router.get(
    "/platform-health",
    response_model=PlatformHealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Live subsystem health checks for API, MongoDB, Worker, and ML engine (Admin only)",
    dependencies=[Depends(require_role([UserRole.ADMIN]))],
)
async def get_health():
    """
    Executes live subsystem health checks and returns response latencies and status.
    """
    return await check_platform_health()


@router.get(
    "/reports/export",
    status_code=status.HTTP_200_OK,
    summary="Export administrative datasets as downloadable CSVs (Admin only)",
    dependencies=[Depends(require_role([UserRole.ADMIN]))],
)
async def export_report(
    type: str = Query(default="retailers", pattern="^(retailers|uploads|activity)$"),
):
    """
    Exports platform datasets into CSV stream for download.
    """
    csv_content = await generate_admin_csv_report(report_type=type)
    filename = f"profitsync_admin_{type}_{PydanticObjectId()}.csv"
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
