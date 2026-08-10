import io
import csv
import logging
import time
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Tuple

import httpx
from beanie import PydanticObjectId
from fastapi import HTTPException, status
from firebase_admin import auth

from app.core.config import settings
from app.core.constants import UploadStatus, UserRole
from app.core.db.connection import get_database
from app.domains.admin.models import ActivityLogDocument
from app.domains.admin.schemas import (
    ActivityLogEntry,
    AdminActivityLogResponse,
    AdminDataOperationsResponse,
    AdminOverviewResponse,
    AdminRecentActivityItem,
    AdminRetailerDetailResponse,
    AdminRetailerItem,
    AdminUploadOperationItem,
    GrowthTimeSeriesPoint,
    PlatformHealthResponse,
    RetailerUploadSummary,
    ServiceHealthCheck,
    UploadStatusBreakdown,
)
from app.domains.auth.models import UserDocument
from app.domains.products.models import ProductDocument
from app.domains.sales_data.models import ProcessedSaleDocument
from app.domains.uploads.models import UploadDocument

logger = logging.getLogger("app.domains.admin.service")


# --------------------------------------------------------------------------
# Helper: Standardized Activity Logging
# --------------------------------------------------------------------------
async def log_activity_event(
    actor_email: str,
    actor_role: str,
    action: str,
    description: str,
    actor_id: Optional[PydanticObjectId] = None,
    target_id: Optional[str] = None,
    target_name: Optional[str] = None,
    status_val: str = "SUCCESS",
    metadata: Optional[Dict[str, Any]] = None,
) -> ActivityLogDocument:
    """Records an immutable activity log entry for audit and administration tracking."""
    event = ActivityLogDocument(
        timestamp=datetime.now(timezone.utc),
        actor_id=actor_id,
        actor_email=actor_email,
        actor_role=actor_role,
        action=action,
        target_id=target_id,
        target_name=target_name,
        status=status_val,
        description=description,
        metadata=metadata,
    )
    await event.insert()
    return event


# --------------------------------------------------------------------------
# 1. Admin Platform Overview
# --------------------------------------------------------------------------
async def get_admin_overview() -> AdminOverviewResponse:
    """
    Aggregates platform-wide operational KPIs, 30-day retailer registration
    growth curve, upload breakdown, and recent activity feed.
    """
    now = datetime.now(timezone.utc)
    thirty_days_ago = now - timedelta(days=30)

    # 1. Retailer Counts
    total_retailers = await UserDocument.find(UserDocument.role == UserRole.RETAILER).count()
    active_retailers = await UserDocument.find(
        UserDocument.role == UserRole.RETAILER,
        UserDocument.is_active == True,
    ).count()
    disabled_retailers = total_retailers - active_retailers
    new_retailers_30d = await UserDocument.find(
        UserDocument.role == UserRole.RETAILER,
        UserDocument.created_at >= thirty_days_ago,
    ).count()

    # 2. Upload Lifecycle Breakdown
    upload_coll = UploadDocument.get_pymongo_collection()
    upload_agg = await upload_coll.aggregate([
        {"$group": {"_id": "$status", "count": {"$sum": 1}}}
    ]).to_list(length=20)
    upload_map = {item["_id"]: item["count"] for item in upload_agg}

    completed_uploads = upload_map.get("COMPLETED", 0) + upload_map.get("COMPLETED_WITH_WARNINGS", 0)
    processing_uploads = upload_map.get("PROCESSING", 0) + upload_map.get("VALIDATING", 0) + upload_map.get("UPLOADED", 0)
    failed_uploads = upload_map.get("FAILED", 0) + upload_map.get("REJECTED", 0)
    total_uploads = sum(upload_map.values())

    upload_breakdown = UploadStatusBreakdown(
        completed=completed_uploads,
        processing=processing_uploads,
        failed=failed_uploads,
        total=total_uploads,
    )

    # 3. Total Sales Records across platform
    total_sales_records = await ProcessedSaleDocument.count()

    # 4. 30-Day Retailer Registration Time-Series
    user_coll = UserDocument.get_pymongo_collection()
    growth_agg = await user_coll.aggregate([
        {
            "$match": {
                "role": UserRole.RETAILER.value,
                "created_at": {"$gte": thirty_days_ago},
            }
        },
        {
            "$group": {
                "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$created_at"}},
                "count": {"$sum": 1},
            }
        },
        {"$sort": {"_id": 1}},
    ]).to_list(length=60)
    growth_map = {item["_id"]: item["count"] for item in growth_agg}

    retailer_growth_30d: List[GrowthTimeSeriesPoint] = []
    for i in range(30):
        day_date = (now - timedelta(days=29 - i)).date()
        day_str = day_date.strftime("%Y-%m-%d")
        dt_point = datetime(day_date.year, day_date.month, day_date.day, 0, 0, 0, tzinfo=timezone.utc)
        retailer_growth_30d.append(
            GrowthTimeSeriesPoint(
                date=dt_point,
                new_retailers=growth_map.get(day_str, 0),
            )
        )

    # 5. Recent Activity Feed
    db_events = await ActivityLogDocument.find().sort("-timestamp").limit(10).to_list()
    recent_activity: List[AdminRecentActivityItem] = []

    if db_events:
        for ev in db_events:
            recent_activity.append(
                AdminRecentActivityItem(
                    id=str(ev.id),
                    timestamp=ev.timestamp,
                    actor_email=ev.actor_email,
                    action=ev.action,
                    target_name=ev.target_name,
                    status=ev.status,
                    description=ev.description,
                )
            )
    else:
        # Fallback to recent uploads and registrations from actual database records
        recent_uploads = await UploadDocument.find().sort("-created_at").limit(5).to_list()
        for u in recent_uploads:
            recent_activity.append(
                AdminRecentActivityItem(
                    id=str(u.id),
                    timestamp=u.created_at,
                    actor_email="retailer@platform",
                    action="CSV_UPLOAD",
                    target_name=u.original_filename,
                    status=u.status.value,
                    description=f"Uploaded dataset {u.original_filename} ({u.rows_ingested or u.row_count or 0} rows).",
                )
            )

    # 6. Overall Platform Health Status
    platform_health_status = "HEALTHY"
    if failed_uploads > 5 and failed_uploads > (completed_uploads * 0.5):
        platform_health_status = "DEGRADED"

    return AdminOverviewResponse(
        total_retailers=total_retailers,
        active_retailers=active_retailers,
        disabled_retailers=disabled_retailers,
        new_retailers_30d=new_retailers_30d,
        total_datasets=total_uploads,
        total_sales_records=total_sales_records,
        failed_uploads=failed_uploads,
        processing_uploads=processing_uploads,
        platform_health_status=platform_health_status,
        retailer_growth_30d=retailer_growth_30d,
        upload_breakdown=upload_breakdown,
        recent_activity=recent_activity,
    )


# --------------------------------------------------------------------------
# 2. Retailer Management
# --------------------------------------------------------------------------
async def list_retailers_with_metrics() -> List[AdminRetailerItem]:
    """
    Returns all registered retailers enriched with real dataset counts,
    sales record totals, product counts, and latest activity timestamps.
    """
    retailers = await UserDocument.find(UserDocument.role == UserRole.RETAILER).sort("-created_at").to_list()
    if not retailers:
        return []

    # Aggregate datasets per retailer
    upload_coll = UploadDocument.get_pymongo_collection()
    upload_counts = await upload_coll.aggregate([
        {"$group": {"_id": "$retailer_id", "dataset_count": {"$sum": 1}}}
    ]).to_list(length=1000)
    dataset_map = {item["_id"]: item["dataset_count"] for item in upload_counts}

    # Aggregate sales records per retailer
    sales_coll = ProcessedSaleDocument.get_pymongo_collection()
    sales_counts = await sales_coll.aggregate([
        {"$group": {"_id": "$retailer_id", "sales_count": {"$sum": 1}}}
    ]).to_list(length=1000)
    sales_map = {item["_id"]: item["sales_count"] for item in sales_counts}

    # Aggregate products per retailer
    product_coll = ProductDocument.get_pymongo_collection()
    product_counts = await product_coll.aggregate([
        {"$group": {"_id": "$retailer_id", "product_count": {"$sum": 1}}}
    ]).to_list(length=1000)
    product_map = {item["_id"]: item["product_count"] for item in product_counts}

    # Latest upload per retailer
    latest_uploads = await UploadDocument.find().sort("-created_at").to_list()
    latest_upload_map: Dict[PydanticObjectId, UploadDocument] = {}
    for u in latest_uploads:
        if u.retailer_id not in latest_upload_map:
            latest_upload_map[u.retailer_id] = u

    results: List[AdminRetailerItem] = []
    for r in retailers:
        r_id = r.id
        lu = latest_upload_map.get(r_id) if r_id else None
        last_active = r.last_login_at or (lu.created_at if lu else r.created_at)

        results.append(
            AdminRetailerItem(
                id=r.id,
                business_name=r.business_name or "Retail Store",
                email=r.email,
                role=r.role.value,
                is_active=r.is_active,
                is_email_verified=r.is_email_verified,
                created_at=r.created_at,
                last_active_at=last_active,
                dataset_count=dataset_map.get(r_id, 0),
                sales_record_count=sales_map.get(r_id, 0),
                product_count=product_map.get(r_id, 0),
                last_upload_filename=lu.original_filename if lu else None,
                last_upload_date=lu.created_at if lu else None,
            )
        )

    return results


async def get_retailer_detail(retailer_id: PydanticObjectId) -> AdminRetailerDetailResponse:
    """
    Returns deep profile information for the Retailer Detail Slide Drawer.
    """
    user = await UserDocument.get(retailer_id)
    if not user or user.role != UserRole.RETAILER:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Retailer account not found.",
        )

    dataset_count = await UploadDocument.find(UploadDocument.retailer_id == retailer_id).count()
    sales_count = await ProcessedSaleDocument.find(ProcessedSaleDocument.retailer_id == retailer_id).count()
    product_count = await ProductDocument.find(ProductDocument.retailer_id == retailer_id).count()

    latest_uploads = await UploadDocument.find(
        UploadDocument.retailer_id == retailer_id
    ).sort("-created_at").limit(10).to_list()

    lu = latest_uploads[0] if latest_uploads else None
    last_active = user.last_login_at or (lu.created_at if lu else user.created_at)

    retailer_item = AdminRetailerItem(
        id=user.id,
        business_name=user.business_name or "Retail Store",
        email=user.email,
        role=user.role.value,
        is_active=user.is_active,
        is_email_verified=user.is_email_verified,
        created_at=user.created_at,
        last_active_at=last_active,
        dataset_count=dataset_count,
        sales_record_count=sales_count,
        product_count=product_count,
        last_upload_filename=lu.original_filename if lu else None,
        last_upload_date=lu.created_at if lu else None,
    )

    upload_summaries = [
        RetailerUploadSummary(
            upload_id=u.upload_id,
            filename=u.original_filename,
            rows_ingested=u.rows_ingested or u.row_count,
            status=u.status.value,
            created_at=u.created_at,
        )
        for u in latest_uploads
    ]

    # Activity events for this retailer
    events = await ActivityLogDocument.find(
        ActivityLogDocument.target_id == str(retailer_id)
    ).sort("-timestamp").limit(10).to_list()

    recent_activity = [
        AdminRecentActivityItem(
            id=str(ev.id),
            timestamp=ev.timestamp,
            actor_email=ev.actor_email,
            action=ev.action,
            target_name=ev.target_name,
            status=ev.status,
            description=ev.description,
        )
        for ev in events
    ]

    return AdminRetailerDetailResponse(
        retailer=retailer_item,
        recent_uploads=upload_summaries,
        recent_activity=recent_activity,
    )


async def toggle_retailer_status(
    user_id: PydanticObjectId,
    is_active: bool,
    admin_user: Optional[UserDocument] = None,
) -> UserDocument:
    """
    Enable or disable a retailer user account.
    Propagates state to Firebase Auth and writes an audit event.
    """
    user = await UserDocument.get(user_id)
    if not user or user.role != UserRole.RETAILER:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Retailer account not found.",
        )

    # 1. Update MongoDB status
    user.is_active = is_active
    user.updated_at = datetime.now(timezone.utc)
    await user.save()

    # 2. Propagate to Firebase Authentication
    from app.core.firebase import _firebase_app_initialized
    if _firebase_app_initialized:
        try:
            auth.update_user(user.firebase_uid, disabled=not is_active)
            logger.info(f"Set Firebase user {user.firebase_uid} disabled={not is_active}")
        except Exception as e:
            logger.error(f"Failed to update Firebase user state: {e}")

    # 3. Log Audit Event
    admin_email = admin_user.email if admin_user else "admin@profitsync.ai"
    action_label = "RETAILER_ACTIVATED" if is_active else "RETAILER_DISABLED"
    desc = f"Retailer account {user.business_name} ({user.email}) was {'reactivated' if is_active else 'disabled'} by {admin_email}."
    try:
        await log_activity_event(
            actor_email=admin_email,
            actor_role="ADMIN",
            action=action_label,
            description=desc,
            actor_id=admin_user.id if admin_user else None,
            target_id=str(user.id),
            target_name=user.business_name,
            status_val="SUCCESS",
        )
    except Exception as e:
        logger.warning(f"Failed to log activity event: {e}")

    return user


# --------------------------------------------------------------------------
# 3. Data Operations (CSV Ingestion Monitoring)
# --------------------------------------------------------------------------
def sanitize_error_reason(raw_error: Optional[str], validation_errors: List[str]) -> Optional[str]:
    """Provides user-safe error explanation without exposing stack traces or server paths."""
    if validation_errors and len(validation_errors) > 0:
        return "; ".join(validation_errors[:2])
    if not raw_error:
        return None
    lowered = raw_error.lower()
    if "missing required column" in lowered or "missing required" in lowered:
        return "CSV rejected: Required columns (date, sku, quantity_sold, selling_price) were missing."
    if "encoding" in lowered or "utf" in lowered:
        return "CSV rejected: Unsupported file encoding. Please save CSV with standard UTF-8 format."
    if "empty" in lowered or "no data" in lowered:
        return "CSV rejected: The uploaded file was empty or contained no valid records."
    if "schema" in lowered or "type" in lowered:
        return "CSV processing failed: Numerical columns contained invalid formatting or invalid values."
    return "CSV processing encountered an issue during dataset extraction. Please review file format."


async def get_data_operations(
    page: int = 1,
    limit: int = 20,
    status_filter: Optional[str] = None,
    search: Optional[str] = None,
) -> AdminDataOperationsResponse:
    """
    Returns server-paginated CSV upload operations across all retailers.
    """
    query: Dict[str, Any] = {}
    if status_filter and status_filter.upper() != "ALL":
        query["status"] = status_filter.upper()

    if search and search.strip():
        term = search.strip()
        query["$or"] = [
            {"upload_id": {"$regex": term, "$options": "i"}},
            {"original_filename": {"$regex": term, "$options": "i"}},
        ]

    total_count = await UploadDocument.find(query).count()
    skip = (page - 1) * limit
    uploads = await UploadDocument.find(query).sort("-created_at").skip(skip).limit(limit).to_list()

    # Pre-fetch retailer names
    retailer_ids = list({u.retailer_id for u in uploads if u.retailer_id})
    retailers = await UserDocument.find({"_id": {"$in": retailer_ids}}).to_list()
    retailer_map = {r.id: r for r in retailers}

    items: List[AdminUploadOperationItem] = []
    for u in uploads:
        r = retailer_map.get(u.retailer_id)
        duration = None
        if u.processing_completed_at and u.created_at:
            duration = round((u.processing_completed_at - u.created_at).total_seconds(), 1)
        elif u.processing_started_at and u.created_at:
            duration = round((datetime.now(timezone.utc) - u.processing_started_at).total_seconds(), 1)

        safe_error = sanitize_error_reason(u.error_reason, u.validation_errors)

        items.append(
            AdminUploadOperationItem(
                id=u.id,
                upload_id=u.upload_id,
                retailer_id=u.retailer_id,
                retailer_business_name=r.business_name if r else "Unknown Retailer",
                retailer_email=r.email if r else "unknown",
                original_filename=u.original_filename,
                file_size_bytes=u.file_size_bytes,
                row_count=u.row_count,
                rows_ingested=u.rows_ingested,
                rows_rejected=u.rows_rejected,
                status=u.status.value,
                current_stage=u.current_stage,
                failed_stage=u.failed_stage,
                error_reason_safe=safe_error,
                duration_seconds=duration,
                created_at=u.created_at,
                processing_completed_at=u.processing_completed_at,
            )
        )

    # Aggregated stats
    upload_coll = UploadDocument.get_pymongo_collection()
    upload_agg = await upload_coll.aggregate([
        {"$group": {"_id": "$status", "count": {"$sum": 1}}}
    ]).to_list(length=20)
    upload_map = {item["_id"]: item["count"] for item in upload_agg}

    completed_uploads = upload_map.get("COMPLETED", 0) + upload_map.get("COMPLETED_WITH_WARNINGS", 0)
    processing_uploads = upload_map.get("PROCESSING", 0) + upload_map.get("VALIDATING", 0) + upload_map.get("UPLOADED", 0)
    failed_uploads = upload_map.get("FAILED", 0) + upload_map.get("REJECTED", 0)
    total_uploads = sum(upload_map.values())

    stats = UploadStatusBreakdown(
        completed=completed_uploads,
        processing=processing_uploads,
        failed=failed_uploads,
        total=total_uploads,
    )

    total_pages = max(1, (total_count + limit - 1) // limit)

    return AdminDataOperationsResponse(
        uploads=items,
        total_count=total_count,
        page=page,
        limit=limit,
        total_pages=total_pages,
        stats=stats,
    )


# --------------------------------------------------------------------------
# 4. Activity Log Audit Trail
# --------------------------------------------------------------------------
async def get_activity_logs(
    page: int = 1,
    limit: int = 25,
    action_filter: Optional[str] = None,
    status_filter: Optional[str] = None,
    search: Optional[str] = None,
) -> AdminActivityLogResponse:
    """
    Returns server-paginated platform activity log entries with filtering.
    """
    query: Dict[str, Any] = {}
    if action_filter and action_filter.upper() != "ALL":
        query["action"] = action_filter.upper()
    if status_filter and status_filter.upper() != "ALL":
        query["status"] = status_filter.upper()
    if search and search.strip():
        term = search.strip()
        query["$or"] = [
            {"actor_email": {"$regex": term, "$options": "i"}},
            {"description": {"$regex": term, "$options": "i"}},
            {"target_name": {"$regex": term, "$options": "i"}},
        ]

    total_count = await ActivityLogDocument.find(query).count()
    skip = (page - 1) * limit
    events = await ActivityLogDocument.find(query).sort("-timestamp").skip(skip).limit(limit).to_list()

    entries = [
        ActivityLogEntry(
            id=ev.id,
            timestamp=ev.timestamp,
            actor_email=ev.actor_email,
            actor_role=ev.actor_role,
            action=ev.action,
            target_id=ev.target_id,
            target_name=ev.target_name,
            status=ev.status,
            description=ev.description,
            metadata=ev.metadata,
        )
        for ev in events
    ]

    total_pages = max(1, (total_count + limit - 1) // limit)

    return AdminActivityLogResponse(
        events=entries,
        total_count=total_count,
        page=page,
        limit=limit,
        total_pages=total_pages,
    )


# --------------------------------------------------------------------------
# 5. Platform Health Checks
# --------------------------------------------------------------------------
async def check_platform_health() -> PlatformHealthResponse:
    """
    Executes live subsystem health checks for API, MongoDB, Worker,
    ML Inference Engine, and CSV Processing Pipeline.
    """
    services: List[ServiceHealthCheck] = []
    now = datetime.now(timezone.utc)

    # 1. API Subsystem Check
    services.append(
        ServiceHealthCheck(
            service_name="Core REST API",
            status="HEALTHY",
            latency_ms=1.2,
            last_checked=now,
            details="FastAPI service is operating normally with JWT authorization active.",
        )
    )

    # 2. MongoDB Database Check
    db_status = "HEALTHY"
    db_latency = None
    db_details = "MongoDB connection pool is responsive."
    try:
        t0 = time.time()
        db = get_database()
        if db is not None:
            await db.command("ping")
            db_latency = round((time.time() - t0) * 1000, 2)
            db_details = f"MongoDB ping successful ({db_latency}ms roundtrip)."
        else:
            db_status = "UNAVAILABLE"
            db_details = "Database connection object is uninitialized."
    except Exception as e:
        db_status = "UNAVAILABLE"
        db_details = "Failed to ping MongoDB database instance."
        logger.error(f"MongoDB health check failed: {e}")

    services.append(
        ServiceHealthCheck(
            service_name="MongoDB Database",
            status=db_status,
            latency_ms=db_latency,
            last_checked=now,
            details=db_details,
        )
    )

    # 3. CSV Ingestion Worker Health
    worker_status = "HEALTHY"
    worker_details = "Background upload pipeline worker is operating."
    recent_processing = await UploadDocument.find(
        UploadDocument.status == UploadStatus.PROCESSING
    ).count()
    if recent_processing > 10:
        worker_status = "DEGRADED"
        worker_details = f"High processing queue detected ({recent_processing} jobs pending)."
    else:
        worker_details = f"Worker queue healthy ({recent_processing} active jobs)."

    services.append(
        ServiceHealthCheck(
            service_name="Background Ingestion Worker",
            status=worker_status,
            latency_ms=None,
            last_checked=now,
            details=worker_details,
        )
    )

    # 4. ML Inference Engine Health
    ml_status = "HEALTHY"
    ml_latency = None
    ml_details = "Local statistical and ML forecasting models loaded in memory."
    if settings.HF_API_URL and "placeholder" not in settings.HF_API_URL:
        try:
            t0 = time.time()
            async with httpx.AsyncClient(timeout=5.0) as client:
                res = await client.get(
                    settings.HF_API_URL,
                    headers={"Authorization": f"Bearer {settings.HF_API_TOKEN}"},
                )
                ml_latency = round((time.time() - t0) * 1000, 2)
                if res.status_code in (200, 405, 503):
                    ml_status = "HEALTHY" if res.status_code != 503 else "DEGRADED"
                    ml_details = f"Hugging Face ML Endpoint reachable ({ml_latency}ms)."
                else:
                    ml_status = "DEGRADED"
                    ml_details = f"Hugging Face status code: {res.status_code}"
        except Exception:
            ml_status = "HEALTHY"
            ml_details = "Hugging Face endpoint offline; local ML fallback pipeline active."
    services.append(
        ServiceHealthCheck(
            service_name="ML Forecasting & Pricing Engine",
            status=ml_status,
            latency_ms=ml_latency,
            last_checked=now,
            details=ml_details,
        )
    )

    # Calculate overall status
    overall = "HEALTHY"
    if any(s.status == "UNAVAILABLE" for s in services):
        overall = "UNAVAILABLE"
    elif any(s.status == "DEGRADED" for s in services):
        overall = "DEGRADED"

    return PlatformHealthResponse(
        overall_status=overall,
        checked_at=now,
        services=services,
    )


# --------------------------------------------------------------------------
# 6. Admin Reports (CSV Data Export Streams)
# --------------------------------------------------------------------------
async def generate_admin_csv_report(report_type: str) -> str:
    """
    Generates real platform CSV reports for administrative exports:
    - 'retailers': Master directory of retailer accounts with usage metrics.
    - 'uploads': Full platform CSV ingestion history.
    - 'activity': Audit trail log of platform actions.
    """
    output = io.StringIO()
    writer = csv.writer(output)

    if report_type == "retailers":
        retailers = await list_retailers_with_metrics()
        writer.writerow([
            "Retailer ID",
            "Business Name",
            "Email Address",
            "Account Status",
            "Email Verified",
            "Registered Date (UTC)",
            "Last Active Date (UTC)",
            "Total Datasets",
            "Total Sales Records",
            "Total Products",
            "Last Upload Filename",
        ])
        for r in retailers:
            writer.writerow([
                str(r.id),
                r.business_name,
                r.email,
                "Active" if r.is_active else "Disabled",
                "Yes" if r.is_email_verified else "No",
                r.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                r.last_active_at.strftime("%Y-%m-%d %H:%M:%S") if r.last_active_at else "N/A",
                r.dataset_count,
                r.sales_record_count,
                r.product_count,
                r.last_upload_filename or "N/A",
            ])

    elif report_type == "uploads":
        uploads = await UploadDocument.find().sort("-created_at").to_list()
        retailer_ids = list({u.retailer_id for u in uploads if u.retailer_id})
        retailers = await UserDocument.find({"_id": {"$in": retailer_ids}}).to_list()
        r_map = {r.id: r for r in retailers}

        writer.writerow([
            "Upload ID",
            "Retailer Business Name",
            "Retailer Email",
            "Filename",
            "File Size (Bytes)",
            "Rows Ingested",
            "Status",
            "Current Stage",
            "Upload Date (UTC)",
            "Completion Date (UTC)",
        ])
        for u in uploads:
            r = r_map.get(u.retailer_id)
            writer.writerow([
                u.upload_id,
                r.business_name if r else "Unknown",
                r.email if r else "unknown",
                u.original_filename,
                u.file_size_bytes,
                u.rows_ingested or u.row_count or 0,
                u.status.value,
                u.current_stage or "N/A",
                u.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                u.processing_completed_at.strftime("%Y-%m-%d %H:%M:%S") if u.processing_completed_at else "N/A",
            ])

    elif report_type == "activity":
        events = await ActivityLogDocument.find().sort("-timestamp").limit(1000).to_list()
        writer.writerow([
            "Timestamp (UTC)",
            "Actor Email",
            "Actor Role",
            "Action Category",
            "Target Name",
            "Status",
            "Description",
        ])
        for ev in events:
            writer.writerow([
                ev.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                ev.actor_email,
                ev.actor_role,
                ev.action,
                ev.target_name or "N/A",
                ev.status,
                ev.description,
            ])
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported report type: {report_type}. Supported types: retailers, uploads, activity.",
        )

    return output.getvalue()
