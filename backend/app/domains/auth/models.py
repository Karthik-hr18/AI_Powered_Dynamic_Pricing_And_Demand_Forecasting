# Placeholder for User database model
"""
Beanie document models for the `auth` domain.

Covers the `users` and `refresh_tokens` collections (Section 2.3.1 /
2.3.2 of the frozen System Design). Both collections share the
Authentication ownership boundary and are kept in a single file per
the Implementation Blueprint's model list for this domain.

Indexes are NOT declared on these Document classes. init_indexes.py
(operating via raw Motor IndexModel registries) is the single source
of truth for index creation — duplicating index definitions here would
create two independently-maintained descriptions of the same indexes.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from beanie import Document
from pydantic import EmailStr, Field, field_validator, model_validator

from app.core.constants import CollectionNames, UserRole
from datetime import datetime, timedelta


class UserDocument(Document):
    """
    Single source of truth for authentication and account identity.

    Covers both RETAILER and ADMIN roles via the `role` field (Section
    2.3.1). RETAILER accounts must carry a `business_name`; ADMIN
    accounts do not require one.
    """

    email: EmailStr
    password_hash: str
    role: UserRole = UserRole.RETAILER
    business_name: Optional[str] = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login_at: Optional[datetime] = None

    class Settings:
        name = CollectionNames.USERS
        # Index creation is owned by init_indexes.py, not Beanie.
        indexes: list = []

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        """Store email lowercase so uniqueness matching is case-insensitive."""
        return value.lower()

    @model_validator(mode="after")
    def require_business_name_for_retailer(self) -> "UserDocument":
        """Section 2.3.1: business_name is required for RETAILER, optional for ADMIN."""
        if self.role == UserRole.RETAILER and not self.business_name:
            raise ValueError("business_name is required when role is RETAILER.")
        return self
"""
(continues app/domains/auth/models.py — appended below UserDocument)
"""

import uuid
from typing import Optional

from beanie import Document, PydanticObjectId
from pydantic import Field

from app.core.config import settings
from app.core.constants import CollectionNames, RefreshTokenRevokedReason


def _default_refresh_token_expiry() -> datetime:
    """now + REFRESH_TOKEN_EXPIRE_DAYS, read from config rather than hardcoded."""
    return datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)


class RefreshTokenDocument(Document):
    """
    Tracks issued refresh tokens for rotation + reuse-detection with
    family-based revocation (Section 2.3.2).

    Every refresh exchange issues a new token and invalidates the
    previous one (same `family_id`). If a superseded token is ever
    presented again, the entire family is revoked, forcing re-login.
    """

    user_id: PydanticObjectId
    token_hash: str
    family_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    issued_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime = Field(default_factory=_default_refresh_token_expiry)
    revoked: bool = False
    revoked_reason: Optional[RefreshTokenRevokedReason] = None
    replaced_by: Optional[PydanticObjectId] = None
    created_ip: Optional[str] = None
    user_agent: Optional[str] = None

    class Settings:
        name = CollectionNames.REFRESH_TOKENS
        # Index creation is owned by init_indexes.py, not Beanie.
        indexes: list = []