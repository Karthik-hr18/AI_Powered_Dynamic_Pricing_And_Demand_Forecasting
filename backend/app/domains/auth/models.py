"""
Beanie document models for the `auth` domain.

Covers the `users` collection (Section 2.3.1 of the frozen System Design)
refactored for Firebase UID mapping. Password storage, hashing, and token
lifetimes are fully delegated to Firebase, keeping the application stateless.

Indexes are created via app/core/db/init_indexes.py.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from beanie import Document
from pydantic import EmailStr, Field, field_validator, model_validator

from app.core.constants import CollectionNames, UserRole


class UserDocument(Document):
    """
    Single source of truth for user profile mapping and role-based permissions.
    
    Links direct identity control to Firebase UID via `firebase_uid`.
    RETAILER accounts must carry a `business_name`; ADMIN accounts do not.
    """

    firebase_uid: str
    email: EmailStr
    role: UserRole = UserRole.RETAILER
    business_name: Optional[str] = None
    is_email_verified: bool = False
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login_at: Optional[datetime] = None

    class Settings:
        name = CollectionNames.USERS
        # Index creation is owned by init_indexes.py
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