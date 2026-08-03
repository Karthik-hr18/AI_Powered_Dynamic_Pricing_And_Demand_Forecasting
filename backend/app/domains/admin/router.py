from typing import List
from fastapi import APIRouter, Depends, status
from beanie import PydanticObjectId

from app.core.constants import UserRole
from app.domains.auth.dependencies import require_role
from app.domains.auth.schemas import UserResponse
from app.domains.admin.schemas import RetailerStatusUpdate
from app.domains.admin.service import list_retailers, toggle_retailer_status

router = APIRouter()


@router.get(
    "/retailers",
    response_model=List[UserResponse],
    status_code=status.HTTP_200_OK,
    summary="List all registered retailer user profiles (Admin only)",
    dependencies=[Depends(require_role([UserRole.ADMIN]))],
)
async def get_retailers():
    """
    Returns a list of all retailer user profiles in the database. Restricted to ADMIN users.
    """
    return await list_retailers()


@router.patch(
    "/retailers/{userId}/status",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Enable or disable a retailer user account (Admin only)",
    dependencies=[Depends(require_role([UserRole.ADMIN]))],
)
async def patch_retailer_status(
    userId: PydanticObjectId,
    status_data: RetailerStatusUpdate,
):
    """
    Toggles the active state of a retailer user account. Restricted to ADMIN users.
    """
    return await toggle_retailer_status(user_id=userId, is_active=status_data.is_active)
