import logging
from typing import List
from beanie import PydanticObjectId
from fastapi import HTTPException, status
from firebase_admin import auth

from app.core.constants import UserRole
from app.domains.auth.models import UserDocument

logger = logging.getLogger("app.domains.admin.service")


async def list_retailers() -> List[UserDocument]:
    """
    Lists all retailer user accounts in the system.
    """
    return await UserDocument.find(UserDocument.role == UserRole.RETAILER).to_list()


async def toggle_retailer_status(
    user_id: PydanticObjectId, is_active: bool
) -> UserDocument:
    """
    Enable or disable a retailer user account.
    Propagates the state toggle to Firebase Authentication to revoke/allow sessions.
    """
    user = await UserDocument.get(user_id)
    if not user or user.role != UserRole.RETAILER:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Retailer account not found."
        )

    # 1. Update MongoDB status
    user.is_active = is_active
    await user.save()

    # 2. Propagate deactivation to Firebase if Admin SDK is initialized
    from app.core.firebase import _firebase_app_initialized
    if _firebase_app_initialized:
        try:
            # Firebase update_user takes standard firebase_uid
            auth.update_user(user.firebase_uid, disabled=not is_active)
            logger.info(
                f"Successfully set Firebase user {user.firebase_uid} disabled={not is_active}"
            )
        except Exception as e:
            logger.error(
                f"Failed to update Firebase state for user {user.firebase_uid}: {e}"
            )
            # We do not crash the request if Firebase deactivation fails,
            # as local is_active = False check in get_current_user middleware
            # is our primary security guard.

    return user
