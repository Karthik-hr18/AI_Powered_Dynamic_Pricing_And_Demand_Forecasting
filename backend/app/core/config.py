import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # TODO: Add validators and defaults in Milestone 2 / Milestone 3
    APP_ENV: str = "development"
    MONGODB_URL: str = "mongodb://localhost:27017/pricing_platform"
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173"
    SENTRY_DSN: Optional[str] = None
    FIREBASE_PROJECT_ID: Optional[str] = None
    FIREBASE_CLIENT_EMAIL: Optional[str] = None
    FIREBASE_PRIVATE_KEY: Optional[str] = None
    WORKER_POLL_INTERVAL_SECONDS: int = 10
    FORECAST_FULL_PIPELINE_MIN_DAYS: int = 14
    FORECAST_FALLBACK_FLOOR_DAYS: int = 7
    PRICING_BOUND_PCT: float = 0.20
    PRICING_PRICE_VARIATION_THRESHOLD: float = 0.05
    PRICING_N_CANDIDATES: int = 5
    ANOMALY_SPIKE_THRESHOLD: float = 2.0
    ANOMALY_DROP_THRESHOLD: float = 0.5
    UPLOAD_STORAGE_DIR: str = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "storage", "uploads")
    HF_API_URL: Optional[str] = None
    HF_API_TOKEN: Optional[str] = None

    class Config:
        env_file = ".env"
        case_sensitive = True

# TODO: Reference settings instance in main and other domains
settings = Settings()
