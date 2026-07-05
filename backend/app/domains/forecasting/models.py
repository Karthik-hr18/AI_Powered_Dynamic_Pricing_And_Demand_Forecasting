# Placeholder for ForecastCurrent and ForecastHistory database models
"""
Beanie document models for the `forecasting` domain.

Covers `forecast_current` (this file) and `forecast_history` (appended
next) — Section 2.3.7 / 2.3.8 of the frozen System Design.

forecast_current: latest forecast per product, overwritten on each
successful run, structured to make the three-tier eligibility model
(FULL / FALLBACK / INSUFFICIENT_DATA) impossible to represent
incorrectly — see the model_validator below.
"""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from beanie import Document, PydanticObjectId
from pydantic import BaseModel, Field, model_validator

from app.core.constants import (
    CollectionNames,
    ForecastConfidenceLabel,
    ForecastPipelineType,
)


class ForecastPrediction(BaseModel):
    """A single predicted-quantity point within a forecast horizon."""

    date: datetime
    predicted_quantity: float = Field(ge=0)


class ForecastHorizon(BaseModel):
    """
    One forecast horizon's output (7-day or 30-day).

    `confidence` here is the per-horizon descriptor produced by the
    composer (e.g. "high" for FULL, "low" for FALLBACK) — distinct from
    the document-level `confidence_label` enum, which summarizes the
    overall pipeline tier for dashboard display.
    """

    predictions: List[ForecastPrediction]
    confidence: str


class ForecastCurrentDocument(Document):
    """
    Latest forecast result per product.

    Structural invariant (Section 2.3.7): when pipeline_type is
    INSUFFICIENT_DATA, both horizon_7d and horizon_30d MUST be None and
    eligibility_reason MUST be a non-empty string. When pipeline_type is
    FALLBACK, horizon_30d MUST be None (Section 6.4 — projecting a flat
    weighted-moving-average 30 days forward from <30 days of history is
    not scientifically defensible). Both rules are enforced below rather
    than left to service-layer discipline.
    """

    retailer_id: PydanticObjectId
    product_id: PydanticObjectId
    pipeline_type: ForecastPipelineType
    eligibility_reason: Optional[str] = None
    history_days_available: int = Field(ge=0)
    horizon_7d: Optional[ForecastHorizon] = None
    horizon_30d: Optional[ForecastHorizon] = None
    confidence_label: ForecastConfidenceLabel
    model_version: str
    run_id: PydanticObjectId
    upload_id: PydanticObjectId
    run_timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = CollectionNames.FORECAST_CURRENT
        # Index creation is owned by init_indexes.py, not Beanie.
        indexes: list = []

    @model_validator(mode="after")
    def enforce_eligibility_structure(self) -> "ForecastCurrentDocument":
        """
        Section 2.3.7 structural rule + Section 6.4 fallback-horizon rule.
        """
        if self.pipeline_type == ForecastPipelineType.INSUFFICIENT_DATA:
            if self.horizon_7d is not None or self.horizon_30d is not None:
                raise ValueError(
                    "INSUFFICIENT_DATA requires both horizon_7d and "
                    "horizon_30d to be null."
                )
            if not self.eligibility_reason or not self.eligibility_reason.strip():
                raise ValueError(
                    "INSUFFICIENT_DATA requires a non-empty eligibility_reason."
                )

        if self.pipeline_type == ForecastPipelineType.FALLBACK:
            if self.horizon_30d is not None:
                raise ValueError(
                    "FALLBACK pipeline_type requires horizon_30d to be null "
                    "(insufficient history for a 30-day projection)."
                )

        return self
"""
(continues app/domains/forecasting/models.py)

Update: ForecastCurrentDocument's model_validator now delegates to the
shared _validate_forecast_eligibility_structure() function below, so
the identical invariant on ForecastHistoryDocument doesn't drift from
it over time. No behavioral change to ForecastCurrentDocument.
"""

from typing import Optional  # already imported above; shown for clarity

from app.core.constants import ForecastTriggeredBy  # add to existing import line


def _validate_forecast_eligibility_structure(
    pipeline_type: ForecastPipelineType,
    horizon_7d: Optional[ForecastHorizon],
    horizon_30d: Optional[ForecastHorizon],
    eligibility_reason: Optional[str],
) -> None:
    """
    Shared invariant for both forecast_current and forecast_history
    (Section 2.3.7 / 2.3.8):

      - INSUFFICIENT_DATA: both horizons must be null, and
        eligibility_reason must be a non-empty string.
      - FALLBACK: horizon_30d must be null (Section 6.4 — projecting a
        flat weighted-moving-average 30 days forward from <30 days of
        history is not scientifically defensible).

    Raises ValueError on violation; callers surface this via Pydantic's
    model_validator so it becomes a normal ValidationError.
    """
    if pipeline_type == ForecastPipelineType.INSUFFICIENT_DATA:
        if horizon_7d is not None or horizon_30d is not None:
            raise ValueError(
                "INSUFFICIENT_DATA requires both horizon_7d and "
                "horizon_30d to be null."
            )
        if not eligibility_reason or not eligibility_reason.strip():
            raise ValueError(
                "INSUFFICIENT_DATA requires a non-empty eligibility_reason."
            )

    if pipeline_type == ForecastPipelineType.FALLBACK:
        if horizon_30d is not None:
            raise ValueError(
                "FALLBACK pipeline_type requires horizon_30d to be null "
                "(insufficient history for a 30-day projection)."
            )


# --- Replace ForecastCurrentDocument's existing validator body with: ---
#
#     @model_validator(mode="after")
#     def enforce_eligibility_structure(self) -> "ForecastCurrentDocument":
#         _validate_forecast_eligibility_structure(
#             self.pipeline_type, self.horizon_7d, self.horizon_30d,
#             self.eligibility_reason,
#         )
#         return self


class ForecastHistoryDocument(Document):
    """
    Immutable, append-only log of every forecasting run per product.

    Same shape as ForecastCurrentDocument plus superseded_at (stamped
    once a later run takes over as forecast_current) and triggered_by
    (what caused this run — a new upload, or a scheduled re-run).
    Carries the identical eligibility invariant as forecast_current.
    """

    retailer_id: PydanticObjectId
    product_id: PydanticObjectId
    pipeline_type: ForecastPipelineType
    eligibility_reason: Optional[str] = None
    history_days_available: int = Field(ge=0)
    horizon_7d: Optional[ForecastHorizon] = None
    horizon_30d: Optional[ForecastHorizon] = None
    confidence_label: ForecastConfidenceLabel
    model_version: str
    run_id: PydanticObjectId
    upload_id: PydanticObjectId
    run_timestamp: datetime = Field(default_factory=datetime.utcnow)
    superseded_at: Optional[datetime] = None
    triggered_by: ForecastTriggeredBy

    class Settings:
        name = CollectionNames.FORECAST_HISTORY
        # Index creation is owned by init_indexes.py, not Beanie.
        indexes: list = []

    @model_validator(mode="after")
    def enforce_eligibility_structure(self) -> "ForecastHistoryDocument":
        _validate_forecast_eligibility_structure(
            self.pipeline_type,
            self.horizon_7d,
            self.horizon_30d,
            self.eligibility_reason,
        )
        return self