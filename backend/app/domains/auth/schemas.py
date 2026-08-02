from datetime import datetime
from typing import Optional
from beanie import PydanticObjectId
from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator

from app.core.constants import UserRole


class UserSyncRequest(BaseModel):
    """
    Schema for synchronizing a Firebase user with the MongoDB database.
    Submitted by the client after client-side sign-up to register custom role
    and metadata properties.
    """
    role: UserRole = Field(default=UserRole.RETAILER)
    business_name: Optional[str] = Field(default=None, description="Required if role is RETAILER.")

    @model_validator(mode="after")
    def require_business_name_for_retailer(self) -> "UserSyncRequest":
        """Ensures RETAILER users supply a business name on registration sync."""
        if self.role == UserRole.RETAILER and not self.business_name:
            raise ValueError("business_name is required when role is RETAILER.")
        return self


class UserResponse(BaseModel):
    """Sanitized user profile data returned in API responses."""
    model_config = ConfigDict(from_attributes=True)

    id: PydanticObjectId
    firebase_uid: str
    email: EmailStr
    role: UserRole
    business_name: Optional[str] = None
    is_email_verified: bool
    is_active: bool
    created_at: datetime
    last_login_at: Optional[datetime] = None
