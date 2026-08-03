from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

# pyrefly: ignore [missing-import]
from contextlib import asynccontextmanager
from fastapi import FastAPI
from beanie import init_beanie

from app.core.firebase import initialize_firebase
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

from app.domains.auth.router import router as auth_router
from app.domains.uploads.router import router as uploads_router
from app.domains.products.router import router as products_router
from app.domains.dashboard.router import router as dashboard_router
from app.domains.admin.router import router as admin_router

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
        AnomalyCurrentDocument
    ]
    await init_beanie(database=db, document_models=document_models)
    # 4. Generate master indexes
    await create_all_indexes()
    # 5. Preload ML models in memory cache
    loader = get_artifact_loader()
    loader.load_all()
    yield
    # 6. Disconnect on shutdown
    await close_mongo_connection()

app = FastAPI(
    title="AI-Powered Dynamic Pricing & Demand Forecasting Platform",
    lifespan=lifespan
)

# Configure CORS origins
origins = [origin.strip() for origin in settings.CORS_ORIGINS.split(",") if origin.strip()]
extended_origins = []
for origin in origins:
    extended_origins.append(origin)
    if "localhost" in origin:
        extended_origins.append(origin.replace("localhost", "127.0.0.1"))

app.add_middleware(
    CORSMiddleware,
    allow_origins=extended_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(uploads_router, prefix="/api/v1/uploads", tags=["uploads"])
app.include_router(products_router, prefix="/api/v1/products", tags=["products"])
app.include_router(dashboard_router, prefix="/api/v1/dashboard", tags=["dashboard"])
app.include_router(admin_router, prefix="/api/v1/admin", tags=["admin"])

@app.get("/")
def read_root():
    return {"status": "ok"}

@app.get("/health")
def read_health():
    return {"status": "ok"}
