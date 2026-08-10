from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

# ProfitSync Production Release v1.0.1 - Models verified & deployed


import asyncio
from typing import Any, cast
from contextlib import asynccontextmanager
from fastapi import FastAPI, Response
from fastapi.responses import JSONResponse
from beanie import init_beanie

from app.core.firebase import initialize_firebase, seed_admin_user
from app.core.ml import get_artifact_loader
from app.core.db.connection import connect_to_mongo, close_mongo_connection, get_database
from app.core.db.init_indexes import create_all_indexes

# Import all Beanie document models
from app.domains.auth.models import UserDocument
from app.domains.products.models import ProductDocument
from app.domains.uploads.models import UploadDocument
from app.domains.sales_data.models import RawSaleDocument, ProcessedSaleDocument
from app.domains.forecasting.models import ForecastCurrentDocument, ForecastHistoryDocument
from app.domains.pricing.models import PricingCurrentDocument, PricingHistoryDocument
from app.domains.inventory.models import InventoryCurrentDocument
from app.domains.anomaly.models import AnomalyCurrentDocument

from app.domains.admin.models import ActivityLogDocument
from app.domains.auth.service import seed_admin_to_mongo
from app.domains.auth.router import router as auth_router
from app.domains.uploads.router import router as uploads_router
from app.domains.products.router import router as products_router
from app.domains.dashboard.router import router as dashboard_router
from app.domains.admin.router import router as admin_router
from app.domains.reports.router import router as reports_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Initialize Firebase
    initialize_firebase()
    # 2. Connect to MongoDB
    await connect_to_mongo()
    # 3. Initialize Beanie ODM
    db = get_database()
    document_models = [
        UserDocument,
        ProductDocument,
        UploadDocument,
        RawSaleDocument,
        ProcessedSaleDocument,
        ForecastCurrentDocument,
        ForecastHistoryDocument,
        PricingCurrentDocument,
        PricingHistoryDocument,
        InventoryCurrentDocument,
        AnomalyCurrentDocument,
        ActivityLogDocument
    ]
    await init_beanie(database=cast(Any, db), document_models=document_models)
    # 4. Generate master indexes
    await create_all_indexes()
    # 5. Seed admin account (Firebase + MongoDB)
    admin_uid = seed_admin_user()
    if admin_uid:
        await seed_admin_to_mongo(admin_uid)
    # 6. Preload ML models in memory cache
    loader = get_artifact_loader()
    loader.load_all()
    # 7. Start background worker loop automatically inside web service process
    from app.worker.main import worker_loop
    worker_task = asyncio.create_task(worker_loop())
    yield
    # 8. Cancel worker task and disconnect on shutdown
    worker_task.cancel()
    await close_mongo_connection()

app = FastAPI(
    title="AI-Powered Dynamic Pricing & Demand Forecasting Platform",
    lifespan=lifespan
)

# CORS: allow all origins unconditionally with dynamic origin mirroring.
# Security is enforced via Firebase JWT tokens on every protected route.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def cors_handler_middleware(request, call_next):
    """
    Middleware guaranteeing Access-Control-Allow-Origin headers are attached
    to ALL HTTP responses, including unhandled exceptions and preflight OPTIONS.
    """
    origin = request.headers.get("origin")
    if request.method == "OPTIONS":
        response = Response(status_code=204)
    else:
        try:
            response = await call_next(request)
        except Exception as exc:
            import logging
            logging.getLogger("app.main").exception("Unhandled server exception", exc_info=exc)
            response = JSONResponse(
                status_code=500,
                content={"detail": "Internal Server Error"}
            )

    if origin:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Allow-Methods"] = "*"
        response.headers["Access-Control-Allow-Headers"] = "*"
    else:
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "*"
        response.headers["Access-Control-Allow-Headers"] = "*"

    # Enterprise security response headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"

    return response

# Register routers
app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(uploads_router, prefix="/api/v1/uploads", tags=["uploads"])
app.include_router(products_router, prefix="/api/v1/products", tags=["products"])
app.include_router(dashboard_router, prefix="/api/v1/dashboard", tags=["dashboard"])
app.include_router(admin_router, prefix="/api/v1/admin", tags=["admin"])
app.include_router(reports_router, prefix="/api/v1/reports", tags=["reports"])

from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.core.errors import create_error_response, ErrorCode, generate_reference_id
import logging

logger = logging.getLogger("app.main")

# Exception handlers for uniform error envelopes across all endpoints
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc: StarletteHTTPException):
    return create_error_response(
        status_code=exc.status_code,
        message=str(exc.detail) if exc.detail else None,
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc: RequestValidationError):
    # Extract clean, human-readable validation error summaries
    details = []
    for err in exc.errors():
        field = " -> ".join(str(loc) for loc in err.get("loc", []) if loc != "body")
        msg = err.get("msg", "Invalid value")
        details.append(f"{field}: {msg}" if field else msg)
    
    return create_error_response(
        status_code=422,
        code=ErrorCode.VALIDATION_ERROR,
        message="The provided information contains validation errors. Please review and correct the fields.",
        details=details[:5],
    )

@app.exception_handler(Exception)
async def unhandled_exception_handler(request, exc: Exception):
    ref_id = generate_reference_id()
    logger.exception(f"Unhandled server error [Ref: {ref_id}] on {request.method} {request.url.path}: {exc}")
    return create_error_response(
        status_code=500,
        code=ErrorCode.UNKNOWN_ERROR,
        message="We could not complete your request. Please try again.",
        reference_id=ref_id,
    )

@app.get("/")
def read_root():
    return {"status": "ok"}

@app.get("/health")
def read_health():
    return {"status": "ok"}

