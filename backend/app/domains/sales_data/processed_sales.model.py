# Placeholder for ProcessedSales database model
"""
Beanie document model for the `processed_sales` collection (sales_data domain).

Covers Section 2.3.6 of the frozen System Design — cleaned,
daily-aggregated, feature-engineered sales records. This is the single
input source read by every ML pipeline (forecasting, pricing, anomaly
detection) and by dashboard aggregation.

Unlike raw_sales, this collection IS mutable: reprocessing upserts
existing (retailer_id, product_id, date) documents rather than
appending new ones.

IMPORTANT — null vs zero: rolling_avg_7d, rolling_avg_30d, and
lag_1d_quantity must be left as None until sufficient history exists
for that product. They must never be zero-filled — a null communicates
"not enough data yet," while a zero would look like a real computed
value of zero. This discipline is enforced by the feature-engineering
code that populates these fields (ml/shared/feature_engineering.py,
built in M5), not by this model.
"""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from beanie import Document, PydanticObjectId
from pydantic import Field

from app.core.constants import CollectionNames


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
    processed_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = CollectionNames.PROCESSED_SALES
        # Index creation is owned by init_indexes.py, not Beanie.
        indexes: list = []