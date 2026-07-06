# Placeholder for PricingCurrent and PricingHistory database models
"""
Beanie document models for the `pricing` domain.

Covers `pricing_current` (this file) and `pricing_history` (appended
next) — Section 2.3.9 / 2.3.10 of the frozen System Design.

pricing_current: latest pricing recommendation per product, including
the full evaluated candidate grid for explainability. Structured so
that "ineligible" and "eligible" states are structurally distinct,
mirroring the forecast_current pattern.
"""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from beanie import Document, PydanticObjectId
from pydantic import BaseModel, Field, model_validator

from app.core.constants import CollectionNames, PricingEligibilityStatus


class BoundRange(BaseModel):
    """Effective price bound: intersection of ±bound_pct and historical range."""

    min: float = Field(ge=0)
    max: float = Field(ge=0)


class CandidateGridEntry(BaseModel):
    """One evaluated candidate price and its projected outcome."""

    candidate_price: float = Field(ge=0)
    estimated_demand: float = Field(ge=0)
    estimated_revenue: float = Field(ge=0)


def _validate_pricing_eligibility_structure(
    eligibility_status: PricingEligibilityStatus,
    eligibility_reason: Optional[str],
    bound_range: Optional[BoundRange],
    candidate_grid: Optional[List[CandidateGridEntry]],
    recommended_price: Optional[float],
    expected_revenue: Optional[float],
) -> None:
    """
    Shared invariant for both pricing_current and pricing_history
    (Section 2.3.9 / 2.3.10):

      - Not ELIGIBLE: eligibility_reason must be non-empty, and
        bound_range / candidate_grid / recommended_price /
        expected_revenue must all be null.
      - ELIGIBLE: bound_range, candidate_grid, recommended_price, and
        expected_revenue must all be populated.

    Raises ValueError on violation; surfaced via Pydantic's
    model_validator as a normal ValidationError.
    """
    is_eligible = eligibility_status == PricingEligibilityStatus.ELIGIBLE

    if not is_eligible:
        if not eligibility_reason or not eligibility_reason.strip():
            raise ValueError(
                f"eligibility_status={eligibility_status.value} requires a "
                "non-empty eligibility_reason."
            )
        if any(
            field is not None
            for field in (bound_range, candidate_grid, recommended_price, expected_revenue)
        ):
            raise ValueError(
                f"eligibility_status={eligibility_status.value} requires "
                "bound_range, candidate_grid, recommended_price, and "
                "expected_revenue to all be null."
            )
    else:
        if any(
            field is None
            for field in (bound_range, candidate_grid, recommended_price, expected_revenue)
        ):
            raise ValueError(
                "eligibility_status=ELIGIBLE requires bound_range, "
                "candidate_grid, recommended_price, and expected_revenue "
                "to all be populated."
            )


class PricingCurrentDocument(Document):
    """
    Latest pricing recommendation per product.

    Full candidate_grid is persisted (not just the winning price) to
    support explainability and the Section 10.5 sanity-check evaluation.
    """

    retailer_id: PydanticObjectId
    product_id: PydanticObjectId
    eligibility_status: PricingEligibilityStatus
    eligibility_reason: Optional[str] = None
    current_price: float = Field(ge=0)
    bound_pct: float = Field(gt=0, le=1)
    bound_range: Optional[BoundRange] = None
    candidate_grid: Optional[List[CandidateGridEntry]] = None
    recommended_price: Optional[float] = Field(default=None, ge=0)
    expected_revenue: Optional[float] = Field(default=None, ge=0)
    elasticity_model_type: Optional[str] = None
    model_version: str
    run_id: PydanticObjectId
    upload_id: PydanticObjectId
    run_timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = CollectionNames.PRICING_CURRENT
        # Index creation is owned by init_indexes.py, not Beanie.
        indexes: list = []

    @model_validator(mode="after")
    def enforce_eligibility_structure(self) -> "PricingCurrentDocument":
        _validate_pricing_eligibility_structure(
            self.eligibility_status,
            self.eligibility_reason,
            self.bound_range,
            self.candidate_grid,
            self.recommended_price,
            self.expected_revenue,
        )
        return self
"""
(continues app/domains/pricing/models.py)
"""

from app.core.constants import ForecastTriggeredBy  # add to existing import line


class PricingHistoryDocument(Document):
    """
    Immutable, append-only log of every pricing run per product.

    Same shape as PricingCurrentDocument plus superseded_at (stamped
    once a later run takes over as pricing_current) and triggered_by.
    Reuses ForecastTriggeredBy since both forecast and pricing runs are
    triggered by the identical two events (an upload or a scheduled
    re-run) — a separate enum would just duplicate the same values.
    """

    retailer_id: PydanticObjectId
    product_id: PydanticObjectId
    eligibility_status: PricingEligibilityStatus
    eligibility_reason: Optional[str] = None
    current_price: float = Field(ge=0)
    bound_pct: float = Field(gt=0, le=1)
    bound_range: Optional[BoundRange] = None
    candidate_grid: Optional[List[CandidateGridEntry]] = None
    recommended_price: Optional[float] = Field(default=None, ge=0)
    expected_revenue: Optional[float] = Field(default=None, ge=0)
    elasticity_model_type: Optional[str] = None
    model_version: str
    run_id: PydanticObjectId
    upload_id: PydanticObjectId
    run_timestamp: datetime = Field(default_factory=datetime.utcnow)
    superseded_at: Optional[datetime] = None
    triggered_by: ForecastTriggeredBy

    class Settings:
        name = CollectionNames.PRICING_HISTORY
        # Index creation is owned by init_indexes.py, not Beanie.
        indexes: list = []

    @model_validator(mode="after")
    def enforce_eligibility_structure(self) -> "PricingHistoryDocument":
        _validate_pricing_eligibility_structure(
            self.eligibility_status,
            self.eligibility_reason,
            self.bound_range,
            self.candidate_grid,
            self.recommended_price,
            self.expected_revenue,
        )
        return self