from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # TODO: Add validators and defaults in Milestone 2 / Milestone 3
    APP_ENV: str = "development"
    MONGODB_URL: str = "mongodb://localhost:27017/pricing_platform"
    JWT_SECRET: str = "dev_secret_key"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173"
    SENTRY_DSN: Optional[str] = None
    WORKER_POLL_INTERVAL_SECONDS: int = 10
    FORECAST_FULL_PIPELINE_MIN_DAYS: int = 14
    FORECAST_FALLBACK_FLOOR_DAYS: int = 7
    PRICING_BOUND_PCT: float = 0.20
    PRICING_PRICE_VARIATION_THRESHOLD: float = 0.05
    PRICING_N_CANDIDATES: int = 5
    ANOMALY_SPIKE_THRESHOLD: float = 2.0
    ANOMALY_DROP_THRESHOLD: float = 0.5

    class Config:
        env_file = ".env"
        case_sensitive = True

# TODO: Reference settings instance in main and other domains
settings = Settings()
