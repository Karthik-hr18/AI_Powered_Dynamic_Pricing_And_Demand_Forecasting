import pytest
import os
import sys

# Force testing environment flag
os.environ["APP_ENV"] = "test"
os.environ["TESTING"] = "1"

from app.core.config import settings
from app.core.db.connection import connect_to_mongo, close_mongo_connection, get_database
from beanie import init_beanie

# Import document models for test Beanie registration
from app.domains.auth.models import UserDocument
from app.domains.products.models import ProductDocument
from app.domains.uploads.models import UploadDocument
from app.domains.sales_data.models import RawSaleDocument, ProcessedSaleDocument
from app.domains.forecasting.models import ForecastCurrentDocument, ForecastHistoryDocument
from app.domains.pricing.models import PricingCurrentDocument, PricingHistoryDocument
from app.domains.inventory.models import InventoryCurrentDocument
from app.domains.anomaly.models import AnomalyCurrentDocument


@pytest.fixture(scope="session", autouse=True)
async def close_connection_after_session():
    """Closes the process-wide MongoDB connection at the end of the test session."""
    yield
    await close_mongo_connection()


@pytest.fixture(autouse=True)
async def setup_test_database():
    """
    Function-scoped fixture to register Beanie models on the current test's event loop.
    Resets the cached MongoDB client first to align connection pool futures with the active loop.
    Redirects writes to 'test_pricing_platform' database.
    """
    url = settings.MONGODB_URL
    if "pricing_platform" in url:
        settings.MONGODB_URL = url.replace("/pricing_platform", "/test_pricing_platform")
    
    # Force connection reset to bind client to the current test event loop
    await close_mongo_connection()
    await connect_to_mongo()
    
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
