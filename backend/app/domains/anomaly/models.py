# Placeholder for AnomalyCurrent database model
"""
Beanie document model for the `anomaly` domain.

Covers `anomaly_current` — Section 2.3.12 of the frozen System Design.
Current-only collection for MVP; no history sibling.

CRITICAL SERVICE-LAYER INVARIANTS (Section 8.4 / 13, NOT enforceable
by this model — these are worker/service-layer disciplines, not data
shape rules):

  - The anomaly detection service has zero write access to raw_sales
    or processed_sales. Flagging is purely additive; anomalies are
    never auto-excluded from training data, since an anomaly may
    reflect a genuine business event (festival, promotion, bulk order)
    rather than bad data.
  - Stage 2 (POST_UPLOAD_ALERT) results are always APPENDED to
    flagged_anomalies via $push — Stage 1 (PRE_FORECAST_HISTORICAL)
    results must never be overwritten.

What IS enforced here: total_flagged_count must always equal
len(flagged_anomalies), since it exists purely as a denormalized count
for fast KPI/sort and must never be allowed to drift from the array
it summarizes.
"""

from __future__ import annotations

from datetime import datetime
from typing import List

from beanie import Document, PydanticObjectId
from pydantic import BaseModel, Field, model_validator

from app.core.constants import AnomalyStage, AnomalyType, CollectionNames


class FlaggedAnomaly(BaseModel):
    """
    One flagged anomaly entry.

    `stage` distinguishes which detection pass found it
    (PRE_FORECAST_HISTORICAL vs POST_UPLOAD_ALERT); `acknowledged`
    defaults to False and is purely a retailer-review flag — it never
    removes the entry from history or excludes it from training data.
    """

    date: datetime
    stage: AnomalyStage
    anomaly_type: AnomalyType
    severity_score: float
    explanation: str
    acknowledged: bool = False


class AnomalyCurrentDocument(Document):
    """
    Currently-flagged anomalies per product, covering both detection
    stages in a single embedded array.

    total_flagged_count is denormalized for fast KPI/sort without
    client-side counting, and is validated below to always match
    len(flagged_anomalies).
    """

    retailer_id: PydanticObjectId
    product_id: PydanticObjectId
    flagged_anomalies: List[FlaggedAnomaly] = Field(default_factory=list)
    total_flagged_count: int = Field(ge=0)
    has_unreviewed_alerts: bool = False
    model_version: str
    upload_id: PydanticObjectId
    run_timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = CollectionNames.ANOMALY_CURRENT
        # Index creation is owned by init_indexes.py, not Beanie.
        indexes: list = []

    @model_validator(mode="after")
    def enforce_count_matches_array(self) -> "AnomalyCurrentDocument":
        """total_flagged_count must never drift from the actual array length."""
        actual_count = len(self.flagged_anomalies)
        if self.total_flagged_count != actual_count:
            raise ValueError(
                f"total_flagged_count ({self.total_flagged_count}) must equal "
                f"len(flagged_anomalies) ({actual_count})."
            )
        return self