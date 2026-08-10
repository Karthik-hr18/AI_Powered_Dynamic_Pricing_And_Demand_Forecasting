from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional
from beanie import PydanticObjectId
from pydantic import BaseModel, Field


class RetailerStatusUpdate(BaseModel):
    """Payload to enable or disable a retailer user account."""
    is_active: bool


# --------------------------------------------------------------------------
# 1. Admin Platform Overview Schemas
# --------------------------------------------------------------------------
class GrowthTimeSeriesPoint(BaseModel):
    """Daily retailer registration count point for time-series charts."""
    date: datetime
    new_retailers: int = 0


class UploadStatusBreakdown(BaseModel):
    """Aggregation of all CSV uploads across the platform by lifecycle status."""
    completed: int = 0
    processing: int = 0
    failed: int = 0
    total: int = 0


class AdminRecentActivityItem(BaseModel):
    """Recent platform-wide operational event for the overview feed."""
    id: str
    timestamp: datetime
    actor_email: str
    action: str
    target_name: Optional[str] = None
    status: str
    description: str


class AdminOverviewResponse(BaseModel):
    """Master platform overview response for SaaS administrators."""
    total_retailers: int
    active_retailers: int
    disabled_retailers: int
    new_retailers_30d: int
    total_datasets: int
    total_sales_records: int
    failed_uploads: int
    processing_uploads: int
    platform_health_status: str  # "HEALTHY", "DEGRADED", "UNAVAILABLE"
    retailer_growth_30d: List[GrowthTimeSeriesPoint] = Field(default_factory=list)
    upload_breakdown: UploadStatusBreakdown
    recent_activity: List[AdminRecentActivityItem] = Field(default_factory=list)


# --------------------------------------------------------------------------
# 2. Retailer Management Schemas
# --------------------------------------------------------------------------
class AdminRetailerItem(BaseModel):
    """Summary item for the retailer management table."""
    id: PydanticObjectId
    business_name: str
    email: str
    role: str
    is_active: bool
    is_email_verified: bool
    created_at: datetime
    last_active_at: Optional[datetime] = None
    dataset_count: int = 0
    sales_record_count: int = 0
    product_count: int = 0
    last_upload_filename: Optional[str] = None
    last_upload_date: Optional[datetime] = None


class RetailerUploadSummary(BaseModel):
    """Upload dataset entry within the retailer detail drawer."""
    upload_id: str
    filename: str
    rows_ingested: Optional[int] = None
    status: str
    created_at: datetime


class AdminRetailerDetailResponse(BaseModel):
    """Complete deep-dive profile for the retailer detail drawer."""
    retailer: AdminRetailerItem
    recent_uploads: List[RetailerUploadSummary] = Field(default_factory=list)
    recent_activity: List[AdminRecentActivityItem] = Field(default_factory=list)


# --------------------------------------------------------------------------
# 3. Data Operations / Ingestion Monitoring Schemas
# --------------------------------------------------------------------------
class AdminUploadOperationItem(BaseModel):
    """Detailed row item for the Data Operations CSV ingestion monitoring table."""
    id: PydanticObjectId
    upload_id: str
    retailer_id: PydanticObjectId
    retailer_business_name: Optional[str] = None
    retailer_email: Optional[str] = None
    original_filename: str
    file_size_bytes: int
    row_count: Optional[int] = None
    rows_ingested: Optional[int] = None
    rows_rejected: int = 0
    status: str
    current_stage: Optional[str] = None
    failed_stage: Optional[str] = None
    error_reason_safe: Optional[str] = None
    duration_seconds: Optional[float] = None
    created_at: datetime
    processing_completed_at: Optional[datetime] = None


class AdminDataOperationsResponse(BaseModel):
    """Paginated response for the Data Operations monitor."""
    uploads: List[AdminUploadOperationItem] = Field(default_factory=list)
    total_count: int
    page: int
    limit: int
    total_pages: int
    stats: UploadStatusBreakdown


# --------------------------------------------------------------------------
# 4. Activity Log Audit Trail Schemas
# --------------------------------------------------------------------------
class ActivityLogEntry(BaseModel):
    """Single audit log entry."""
    id: PydanticObjectId
    timestamp: datetime
    actor_email: str
    actor_role: str
    action: str
    target_id: Optional[str] = None
    target_name: Optional[str] = None
    status: str
    description: str
    metadata: Optional[Dict[str, Any]] = None


class AdminActivityLogResponse(BaseModel):
    """Paginated activity log audit trail."""
    events: List[ActivityLogEntry] = Field(default_factory=list)
    total_count: int
    page: int
    limit: int
    total_pages: int


# --------------------------------------------------------------------------
# 5. Platform Health Schemas
# --------------------------------------------------------------------------
class ServiceHealthCheck(BaseModel):
    """Health check outcome for an individual platform subsystem."""
    service_name: str
    status: str  # "HEALTHY", "DEGRADED", "UNAVAILABLE", "UNKNOWN"
    latency_ms: Optional[float] = None
    last_checked: datetime
    details: str


class PlatformHealthResponse(BaseModel):
    """Comprehensive system-level health telemetry for administrators."""
    overall_status: str
    checked_at: datetime
    services: List[ServiceHealthCheck] = Field(default_factory=list)
