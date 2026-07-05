# Placeholder for Upload database model
"""
Beanie document model for the `uploads` domain.

Covers the `uploads` collection (Section 2.3.4 of the frozen System
Design) — tracks each CSV upload as both a file/dataset record and the
background processing job's lifecycle state machine:

    UPLOADED -> VALIDATING -> REJECTED (validation fail)
                            -> PROCESSING -> COMPLETED
                                           -> COMPLETED_WITH_WARNINGS
                                           -> FAILED

State transitions are enforced by the worker/service layer (M4+), not
by this model.
"""

from __future__ import annotations

import secrets
from datetime import datetime
from typing import List, Optional

from beanie import Document, PydanticObjectId
from pydantic import BaseModel, Field

from app.core.constants import CollectionNames, UploadStatus


def _generate_upload_id() -> str:
    """
    Generate a human-readable business ID, e.g. UPL-20260630-7f3a.

    Distinct from the MongoDB _id — used for support/debugging and
    surfaced to the retailer, per Section 2.3.4.
    """
    date_part = datetime.utcnow().strftime("%Y%m%d")
    suffix = secrets.token_hex(2)  # 4 hex characters
    return f"UPL-{date_part}-{suffix}"


class RowWarning(BaseModel):
    """A single row-level issue surfaced on COMPLETED_WITH_WARNINGS."""

    row: int
    reason: str


class UploadDocument(Document):
    """
    Tracks one CSV upload's file metadata and background job lifecycle.

    Two-tier status model: `status` is the coarse enum that business
    logic branches on; `current_stage` is an informational string for
    progress UI (e.g. "forecasting") that can evolve without breaking
    the API contract.
    """

    upload_id: str = Field(default_factory=_generate_upload_id)
    retailer_id: PydanticObjectId
    original_filename: str
    file_size_bytes: int
    row_count: Optional[int] = None
    schema_mapping_used: str
    status: UploadStatus = UploadStatus.UPLOADED
    current_stage: Optional[str] = None
    validation_errors: List[str] = Field(default_factory=list)
    row_warnings: List[RowWarning] = Field(default_factory=list)
    error_reason: Optional[str] = None
    rows_ingested: Optional[int] = None
    rows_rejected: int = 0
    processing_started_at: Optional[datetime] = None
    processing_completed_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = CollectionNames.UPLOADS
        # Index creation is owned by init_indexes.py, not Beanie.
        indexes: list = []