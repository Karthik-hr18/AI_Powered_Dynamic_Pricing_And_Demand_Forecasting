# Placeholder for RawSales database model
"""
Beanie document model for the `raw_sales` collection (sales_data domain).

Covers Section 2.3.5 of the frozen System Design — the immutable,
per-row record of every uploaded sales transaction, exactly as mapped
from the source CSV.

IMMUTABILITY RULE: documents in this collection are never updated after
insertion. Corrections require a new upload, not an edit. This is a
service-layer/operational discipline — no code path should ever call
update_one() or replace_one() against raw_sales.

processed_sales (not raw_sales) is the single input source read by all
ML pipelines; raw_sales exists purely as the auditable source of truth.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional

from beanie import Document, PydanticObjectId
from pydantic import Field

from app.core.constants import CollectionNames


class RawSaleDocument(Document):
    """
    Immutable, per-row record of one uploaded sales transaction.

    Known Section 9.1 schema fields are typed top-level keys, uniform
    regardless of source dataset format. `source_row_raw` separately
    preserves the verbatim original CSV row for forensics/debugging —
    it is never read by any ML pipeline.
    """

    retailer_id: PydanticObjectId
    upload_id: PydanticObjectId
    product_id: PydanticObjectId
    sku: str
    date: datetime
    quantity_sold: int = Field(ge=0)
    selling_price: Optional[float] = None
    category: Optional[str] = None
    unit_cost: Optional[float] = None
    discount: Optional[float] = None
    store_id: Optional[str] = None
    inventory_level: Optional[int] = None
    promotion_flag: Optional[bool] = None
    holiday_flag: Optional[bool] = None
    row_number_in_file: int
    source_row_raw: Dict[str, Any]
    ingested_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = CollectionNames.RAW_SALES
        # Index creation is owned by init_indexes.py, not Beanie.
        indexes: list = []