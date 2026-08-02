import logging
from typing import List
from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.constants import UserRole
from app.core.firebase import verify_firebase_token
from app.domains.auth.models import UserDocument
from app.domains.auth.service import sync_firebase_user

logger = logging.getLogger("app.domains.auth.dependencies")

# Instantiate HTTPBearer security scheme
bearer_scheme = HTTPBearer(auto_error=True)


async def get_firebase_token_payload(
    credentials: HTTPAuthorizationCredentials = Security(bearer_scheme)
) -> dict:
    """
    FastAPI security dependency to verify the Firebase ID token in Authorization header.
    Returns the decoded Firebase claims dictionary if valid.
    """
    id_token = credentials.credentials
    try:
        claims = verify_firebase_token(id_token)
        return claims
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    claims: dict = Depends(get_firebase_token_payload)
) -> UserDocument:
    """
    Dependency that retrieves the current MongoDB User profile linked to the Firebase token.
    Triggers an auto-sync to register the user in MongoDB with defaults if not already present.
    """
    try:
        user = await sync_firebase_user(claims)
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is deactivated."
            )
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


def require_email_verified(
    user: UserDocument = Depends(get_current_user)
) -> UserDocument:
    """Dependency filter restricting access to users with verified emails in Firebase."""
    if not user.is_email_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email verification required. Please verify your email via the confirmation link."
        )
    return user


class RoleChecker:
    """Dependency helper to enforce Role-Based Access Control (RBAC)."""
    
    def __init__(self, allowed_roles: List[UserRole]):
        self.allowed_roles = allowed_roles

    def __call__(self, user: UserDocument = Depends(get_current_user)) -> UserDocument:
        if user.role not in self.allowed_roles:
            role_values = [r.value for r in self.allowed_roles]
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access forbidden: requires role in {role_values}."
            )
        return user


def require_role(allowed_roles: List[UserRole]) -> RoleChecker:
    """Convenience decorator helper for route endpoints dependency injection."""
    return RoleChecker(allowed_roles)
