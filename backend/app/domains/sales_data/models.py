"""
Beanie document models for the `sales_data` domain.

Covers both `raw_sales` and `processed_sales` collections (Section 2.3.5 / 2.3.6
of the frozen System Design).
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

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
    ingested_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = CollectionNames.RAW_SALES
        # Index creation is owned by init_indexes.py, not Beanie.
        indexes: list = []


class ProcessedSaleDocument(Document):
    """
    Cleaned, daily-aggregated, feature-engineered sales record.

    One document per (retailer_id, product_id, date) — enforced by the
    unique compound index idx_retailer_product_date_unique, which also
    serves as the upsert key during reprocessing.
    """

    retailer_id: PydanticObjectId
    product_id: PydanticObjectId
    date: datetime
    quantity_sold: int = Field(ge=0)
    selling_price: Optional[float] = None
    unit_cost: Optional[float] = None
    discount: Optional[float] = None
    category: Optional[str] = None
    store_id: Optional[str] = None
    inventory_level: Optional[int] = None
    promotion_flag: Optional[bool] = None
    holiday_flag: Optional[bool] = None
    day_of_week: int = Field(ge=0, le=6)
    is_weekend: bool
    rolling_avg_7d: Optional[float] = None
    rolling_avg_30d: Optional[float] = None
    lag_1d_quantity: Optional[int] = None
    price_change_flag: Optional[bool] = None
    source_upload_ids: List[PydanticObjectId] = Field(default_factory=list)
    feature_engineering_version: str
    processed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = CollectionNames.PROCESSED_SALES
        # Index creation is owned by init_indexes.py, not Beanie.
        indexes: list = []
