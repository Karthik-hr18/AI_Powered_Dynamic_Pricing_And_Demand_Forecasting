from fastapi import APIRouter, Depends, HTTPException, status

from app.domains.auth.dependencies import get_current_user, get_firebase_token_payload
from app.domains.auth.schemas import UserResponse, UserSyncRequest
from app.domains.auth.service import sync_firebase_user

router = APIRouter()


@router.post(
    "/sync",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Sync Firebase authenticated user with MongoDB"
)
async def sync_user(
    sync_data: UserSyncRequest,
    claims: dict = Depends(get_firebase_token_payload)
):
    """
    Synchronizes the Firebase ID token claims with the MongoDB user profile.
    Used during initial registration sync to pass the custom role/business name metadata.
    """
    try:
        user = await sync_firebase_user(claims, sync_data)
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get current user profile"
)
async def get_me(user = Depends(get_current_user)):
    """Returns the authenticated user's profile details."""
    return user
