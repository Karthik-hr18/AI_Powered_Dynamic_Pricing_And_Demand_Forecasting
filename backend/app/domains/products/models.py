# Placeholder for Product database model
"""
Beanie document model for the `products` domain.

Covers the `products` collection (Section 2.3.3 of the frozen System
Design) — the master registry of retailer-owned SKUs, auto-populated
during CSV ingestion. No public router exists for writes; all creation
is implicit, driven by the uploads pipeline (M4+).
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from beanie import Document, PydanticObjectId
from pydantic import Field, field_validator

from app.core.constants import CollectionNames


class ProductDocument(Document):
    """
    Master registry of retailer-owned products/SKUs.

    `sku` is normalized (trimmed, case-folded) since it is the identity
    key used on every CSV row during ingestion; `sku_display` preserves
    the original as-uploaded casing for UI presentation. Forecast and
    pricing eligibility are derived analytical state owned by their
    respective pipelines and are never stored here.
    """

    retailer_id: PydanticObjectId
    sku: str
    sku_display: str
    product_name: Optional[str] = None
    category: Optional[str] = None
    brand: Optional[str] = None
    is_active: bool = True
    first_seen_upload_id: PydanticObjectId
    last_seen_upload_id: PydanticObjectId
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = CollectionNames.PRODUCTS
        # Index creation is owned by init_indexes.py, not Beanie.
        indexes: list = []

    @field_validator("sku")
    @classmethod
    def normalize_sku(cls, value: str) -> str:
        """Trim and case-fold sku so it matches consistently during ingestion lookups."""
        return value.strip().lower()