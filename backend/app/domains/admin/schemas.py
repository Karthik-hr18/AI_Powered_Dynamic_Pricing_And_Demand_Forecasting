from pydantic import BaseModel, Field


class RetailerStatusUpdate(BaseModel):
    """Payload schema for updates to a retailer's active account state."""
    is_active: bool = Field(..., description="Set active status for the account")
