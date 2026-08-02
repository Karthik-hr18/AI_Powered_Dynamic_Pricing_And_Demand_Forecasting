from datetime import datetime
from typing import List, Optional
from beanie import PydanticObjectId
from pydantic import BaseModel, ConfigDict, Field

from app.core.constants import UploadStatus
from app.domains.uploads.models import RowWarning


class UploadResponse(BaseModel):
    """API response schema for tracking upload jobs and dataset ingestion state."""
    model_config = ConfigDict(from_attributes=True)

    id: PydanticObjectId
    upload_id: str
    retailer_id: PydanticObjectId
    original_filename: str
    file_size_bytes: int
    row_count: Optional[int] = None
    schema_mapping_used: str
    status: UploadStatus
    current_stage: Optional[str] = None
    validation_errors: List[str] = Field(default_factory=list)
    row_warnings: List[RowWarning] = Field(default_factory=list)
    error_reason: Optional[str] = None
    rows_ingested: Optional[int] = None
    rows_rejected: int = 0
    processing_started_at: Optional[datetime] = None
    processing_completed_at: Optional[datetime] = None
    created_at: datetime
