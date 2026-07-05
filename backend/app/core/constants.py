"""
Shared enums and collection-name constants.

Single source of truth for every string-enum field and collection name
used across the twelve MongoDB collections defined in the frozen System
Design (Section 2.3). Centralizing these here means:

  - Document models, Pydantic schemas, and service-layer logic all
    validate against the same enum values — no risk of a typo'd literal
    string drifting from the schema spec.
  - init_indexes.py and every domain model import collection names from
    one place instead of redeclaring them locally.

ML threshold constants (e.g. FORECAST_FULL_PIPELINE_MIN_DAYS,
PRICING_BOUND_PCT) are NOT defined here — per the frozen architecture
(Section 6.4 / 13), those live exclusively in core/config.py and are
read from the environment, never hardcoded.
"""

from __future__ import annotations

from enum import Enum


# --------------------------------------------------------------------------
# Collection names
# --------------------------------------------------------------------------
class CollectionNames:
    """Canonical MongoDB collection name for each of the twelve collections."""

    USERS = "users"
    REFRESH_TOKENS = "refresh_tokens"
    PRODUCTS = "products"
    UPLOADS = "uploads"
    RAW_SALES = "raw_sales"
    PROCESSED_SALES = "processed_sales"
    FORECAST_CURRENT = "forecast_current"
    FORECAST_HISTORY = "forecast_history"
    PRICING_CURRENT = "pricing_current"
    PRICING_HISTORY = "pricing_history"
    INVENTORY_CURRENT = "inventory_current"
    ANOMALY_CURRENT = "anomaly_current"


# --------------------------------------------------------------------------
# users
# --------------------------------------------------------------------------
class UserRole(str, Enum):
    RETAILER = "RETAILER"
    ADMIN = "ADMIN"


# --------------------------------------------------------------------------
# refresh_tokens
# --------------------------------------------------------------------------
class RefreshTokenRevokedReason(str, Enum):
    LOGOUT = "LOGOUT"
    ROTATED = "ROTATED"
    REUSE_DETECTED = "REUSE_DETECTED"
    EXPIRED = "EXPIRED"
    ADMIN_DISABLE = "ADMIN_DISABLE"


# --------------------------------------------------------------------------
# uploads
# --------------------------------------------------------------------------
class UploadStatus(str, Enum):
    UPLOADED = "UPLOADED"
    VALIDATING = "VALIDATING"
    REJECTED = "REJECTED"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    COMPLETED_WITH_WARNINGS = "COMPLETED_WITH_WARNINGS"
    FAILED = "FAILED"


# --------------------------------------------------------------------------
# forecast_current / forecast_history
# --------------------------------------------------------------------------
class ForecastPipelineType(str, Enum):
    FULL = "FULL"
    FALLBACK = "FALLBACK"
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"


class ForecastConfidenceLabel(str, Enum):
    HIGH = "HIGH"
    LOW = "LOW"
    NONE = "NONE"


class ForecastTriggeredBy(str, Enum):
    UPLOAD = "UPLOAD"
    SCHEDULED = "SCHEDULED"


# --------------------------------------------------------------------------
# pricing_current / pricing_history
# --------------------------------------------------------------------------
class PricingEligibilityStatus(str, Enum):
    ELIGIBLE = "ELIGIBLE"
    INSUFFICIENT_HISTORY = "INSUFFICIENT_HISTORY"
    INSUFFICIENT_PRICE_VARIATION = "INSUFFICIENT_PRICE_VARIATION"


# pricing_history reuses ForecastTriggeredBy for its `triggered_by` field
# (same UPLOAD / SCHEDULED semantics as forecast_history) — no separate
# enum needed.


# --------------------------------------------------------------------------
# inventory_current
# --------------------------------------------------------------------------
class InventoryMode(str, Enum):
    TRUE_RISK = "TRUE_RISK"
    ADVISORY = "ADVISORY"


class InventoryClassification(str, Enum):
    STOCKOUT_RISK = "STOCKOUT_RISK"
    OVERSTOCK_RISK = "OVERSTOCK_RISK"
    HEALTHY = "HEALTHY"


class InventoryDemandTrend(str, Enum):
    RISING = "RISING"
    FALLING = "FALLING"
    STABLE = "STABLE"


# --------------------------------------------------------------------------
# anomaly_current
# --------------------------------------------------------------------------
class AnomalyStage(str, Enum):
    PRE_FORECAST_HISTORICAL = "PRE_FORECAST_HISTORICAL"
    POST_UPLOAD_ALERT = "POST_UPLOAD_ALERT"


class AnomalyType(str, Enum):
    SPIKE = "SPIKE"
    DROP = "DROP"
    UNUSUAL = "UNUSUAL"