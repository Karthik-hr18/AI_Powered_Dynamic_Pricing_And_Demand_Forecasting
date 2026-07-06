# Placeholder for InventoryCurrent database model
"""
Beanie document model for the `inventory` domain.

Covers `inventory_current` — Section 2.3.9 (System Design) / 3.11
(Architecture reference) of the frozen System Design. Current-only
collection for MVP; no history sibling.

Mode-segregated nested objects make it structurally impossible to
confuse a soft advisory (no inventory data) with a true risk
classification (inventory data present) — Section 8.5's "structural
honesty" requirement.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from beanie import Document, PydanticObjectId
from pydantic import BaseModel, Field, model_validator

from app.core.constants import (
    CollectionNames,
    InventoryClassification,
    InventoryDemandTrend,
    InventoryMode,
)


class TrueRiskDetail(BaseModel):
    """Populated only when mode=TRUE_RISK (inventory_level was present)."""

    days_of_cover: float = Field(ge=0)
    classification: InventoryClassification
    current_inventory_level: int = Field(ge=0)
    horizon_used: str


class AdvisoryDetail(BaseModel):
    """
    Populated only when mode=ADVISORY (inventory_level was absent).

    `message` must explicitly state that inventory data was not
    provided — it must never imply knowledge of actual stock risk
    (Section 8.5 / FR-23).
    """

    demand_trend: InventoryDemandTrend
    message: str


class InventoryCurrentDocument(Document):
    """
    Latest inventory risk assessment per product.

    Invariant: exactly one of true_risk / advisory is non-null.
    Both populated or both null is a service-layer error, not an
    acceptable edge case (Section 2.3.9), and is rejected here.
    """

    retailer_id: PydanticObjectId
    product_id: PydanticObjectId
    mode: InventoryMode
    true_risk: Optional[TrueRiskDetail] = None
    advisory: Optional[AdvisoryDetail] = None
    forecast_horizon_used: str = "30d"
    forecast_run_id: PydanticObjectId
    upload_id: PydanticObjectId
    run_timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = CollectionNames.INVENTORY_CURRENT
        # Index creation is owned by init_indexes.py, not Beanie.
        indexes: list = []

    @model_validator(mode="after")
    def enforce_exactly_one_mode_populated(self) -> "InventoryCurrentDocument":
        """
        Section 2.3.9: exactly one of true_risk / advisory must be
        non-null, and it must match `mode`.
        """
        populated_count = sum(
            field is not None for field in (self.true_risk, self.advisory)
        )
        if populated_count != 1:
            raise ValueError(
                "Exactly one of true_risk / advisory must be populated "
                f"(found {populated_count}). Both null or both populated "
                "is invalid."
            )

        if self.mode == InventoryMode.TRUE_RISK and self.true_risk is None:
            raise ValueError("mode=TRUE_RISK requires true_risk to be populated.")

        if self.mode == InventoryMode.ADVISORY and self.advisory is None:
            raise ValueError("mode=ADVISORY requires advisory to be populated.")

        return self