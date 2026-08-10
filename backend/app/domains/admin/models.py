from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Optional
from beanie import Document, PydanticObjectId
from pydantic import Field


class ActivityLogDocument(Document):
    """
    Immutable audit trail document for platform-level activity and admin operations.
    Tracks user actions, data ingestion milestones, and administrative changes.
    """
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    actor_id: Optional[PydanticObjectId] = None
    actor_email: str
    actor_role: str
    action: str  # USER_REGISTER, USER_LOGIN, RETAILER_STATUS_CHANGE, CSV_UPLOAD, CSV_PROCESS_COMPLETED, CSV_PROCESS_FAILED, REPORT_EXPORT, ADMIN_ACTION
    target_id: Optional[str] = None
    target_name: Optional[str] = None
    status: str = "SUCCESS"  # SUCCESS, FAILED, WARNING, INFO
    description: str
    metadata: Optional[Dict[str, Any]] = None

    class Settings:
        name = "activity_logs"
        indexes: list = []
