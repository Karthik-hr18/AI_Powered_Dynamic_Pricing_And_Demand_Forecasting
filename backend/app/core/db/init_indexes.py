"""
Master index initialization.

Creates every index defined in the frozen System Design's Master
Indexing Strategy (Section 3 / 4). Run once at application and worker
startup — safe to call repeatedly (MongoDB treats a `create_index` call
with an identical name/keys/options as a no-op).

This module intentionally operates on raw collection names rather than
Beanie Document classes: index creation is a property of the underlying
MongoDB collection, not the ODM layer, and this keeps index setup fully
independent of model definition order.

Usage:
    # app/main.py (API) and app/worker/main.py (worker), after connect_to_mongo()
    await create_all_indexes()
"""

from __future__ import annotations

import logging
from typing import Dict, List

from pymongo import ASCENDING, DESCENDING, IndexModel

from app.core.db.connection import get_database

logger = logging.getLogger(__name__)


# --------------------------------------------------------------------------
# Collection names
#
# Declared locally for now. Once the shared enums/constants module exists,
# these should be replaced with imports from there so there is a single
# source of truth for collection names across models, repositories, and
# this index script.
# --------------------------------------------------------------------------
COLL_USERS = "users"
COLL_REFRESH_TOKENS = "refresh_tokens"
COLL_PRODUCTS = "products"
COLL_UPLOADS = "uploads"
COLL_RAW_SALES = "raw_sales"
COLL_PROCESSED_SALES = "processed_sales"
COLL_FORECAST_CURRENT = "forecast_current"
COLL_FORECAST_HISTORY = "forecast_history"
COLL_PRICING_CURRENT = "pricing_current"
COLL_PRICING_HISTORY = "pricing_history"
COLL_INVENTORY_CURRENT = "inventory_current"
COLL_ANOMALY_CURRENT = "anomaly_current"


# --------------------------------------------------------------------------
# Index definitions, grouped by collection.
#
# Field order in every compound index follows the System Design's
# governing rule: equality predicates (retailer_id, product_id) precede
# range/sort fields (date, run_timestamp). Every tenant-scoped collection
# leads with retailer_id.
# --------------------------------------------------------------------------

_USERS_INDEXES: List[IndexModel] = [
    IndexModel([("email", ASCENDING)], name="idx_email_unique", unique=True),
    IndexModel([("role", ASCENDING)], name="idx_role"),
    IndexModel([("is_active", ASCENDING)], name="idx_is_active"),
]

_REFRESH_TOKENS_INDEXES: List[IndexModel] = [
    IndexModel(
        [("token_hash", ASCENDING)], name="idx_token_hash_unique", unique=True
    ),
    IndexModel([("family_id", ASCENDING)], name="idx_family_id"),
    IndexModel([("user_id", ASCENDING)], name="idx_user_id"),
    # TTL index: MongoDB auto-deletes documents once expires_at is in the
    # past. expireAfterSeconds=0 means "expire exactly at the stored date".
    IndexModel(
        [("expires_at", ASCENDING)],
        name="idx_ttl_expires_at",
        expireAfterSeconds=0,
    ),
]

_PRODUCTS_INDEXES: List[IndexModel] = [
    IndexModel(
        [("retailer_id", ASCENDING), ("sku", ASCENDING)],
        name="idx_retailer_sku_unique",
        unique=True,
    ),
    IndexModel(
        [("retailer_id", ASCENDING), ("is_active", ASCENDING)],
        name="idx_retailer_active",
    ),
]

_UPLOADS_INDEXES: List[IndexModel] = [
    IndexModel([("upload_id", ASCENDING)], name="idx_upload_id_unique", unique=True),
    IndexModel(
        [("retailer_id", ASCENDING), ("created_at", DESCENDING)],
        name="idx_retailer_created",
    ),
    IndexModel([("status", ASCENDING)], name="idx_status"),
]

_RAW_SALES_INDEXES: List[IndexModel] = [
    IndexModel(
        [
            ("retailer_id", ASCENDING),
            ("product_id", ASCENDING),
            ("date", ASCENDING),
        ],
        name="idx_retailer_product_date",
    ),
    IndexModel([("upload_id", ASCENDING)], name="idx_upload_id"),
    IndexModel(
        [("retailer_id", ASCENDING), ("date", ASCENDING)],
        name="idx_retailer_date",
    ),
]

_PROCESSED_SALES_INDEXES: List[IndexModel] = [
    IndexModel(
        [
            ("retailer_id", ASCENDING),
            ("product_id", ASCENDING),
            ("date", ASCENDING),
        ],
        name="idx_retailer_product_date_unique",
        unique=True,
    ),
    IndexModel(
        [("retailer_id", ASCENDING), ("date", ASCENDING)],
        name="idx_retailer_date",
    ),
]

_FORECAST_CURRENT_INDEXES: List[IndexModel] = [
    IndexModel(
        [("retailer_id", ASCENDING), ("product_id", ASCENDING)],
        name="idx_retailer_product_unique",
        unique=True,
    ),
    IndexModel(
        [("retailer_id", ASCENDING), ("pipeline_type", ASCENDING)],
        name="idx_retailer_pipeline_type",
    ),
]

_FORECAST_HISTORY_INDEXES: List[IndexModel] = [
    IndexModel(
        [
            ("retailer_id", ASCENDING),
            ("product_id", ASCENDING),
            ("run_timestamp", DESCENDING),
        ],
        name="idx_retailer_product_run_desc",
    ),
]

_PRICING_CURRENT_INDEXES: List[IndexModel] = [
    IndexModel(
        [("retailer_id", ASCENDING), ("product_id", ASCENDING)],
        name="idx_retailer_product_unique",
        unique=True,
    ),
    IndexModel(
        [("retailer_id", ASCENDING), ("eligibility_status", ASCENDING)],
        name="idx_retailer_eligibility",
    ),
]

_PRICING_HISTORY_INDEXES: List[IndexModel] = [
    IndexModel(
        [
            ("retailer_id", ASCENDING),
            ("product_id", ASCENDING),
            ("run_timestamp", DESCENDING),
        ],
        name="idx_retailer_product_run_desc",
    ),
]

_INVENTORY_CURRENT_INDEXES: List[IndexModel] = [
    IndexModel(
        [("retailer_id", ASCENDING), ("product_id", ASCENDING)],
        name="idx_retailer_product_unique",
        unique=True,
    ),
    IndexModel(
        [
            ("retailer_id", ASCENDING),
            ("mode", ASCENDING),
            ("true_risk.classification", ASCENDING),
        ],
        name="idx_retailer_mode_classification",
    ),
]

_ANOMALY_CURRENT_INDEXES: List[IndexModel] = [
    IndexModel(
        [("retailer_id", ASCENDING), ("product_id", ASCENDING)],
        name="idx_retailer_product_unique",
        unique=True,
    ),
    IndexModel(
        [("retailer_id", ASCENDING), ("has_unreviewed_alerts", ASCENDING)],
        name="idx_retailer_unreviewed",
    ),
]


# --------------------------------------------------------------------------
# Master registry: collection name -> its index definitions.
# This is the single lookup table create_all_indexes() iterates over.
# --------------------------------------------------------------------------
COLLECTION_INDEXES: Dict[str, List[IndexModel]] = {
    COLL_USERS: _USERS_INDEXES,
    COLL_REFRESH_TOKENS: _REFRESH_TOKENS_INDEXES,
    COLL_PRODUCTS: _PRODUCTS_INDEXES,
    COLL_UPLOADS: _UPLOADS_INDEXES,
    COLL_RAW_SALES: _RAW_SALES_INDEXES,
    COLL_PROCESSED_SALES: _PROCESSED_SALES_INDEXES,
    COLL_FORECAST_CURRENT: _FORECAST_CURRENT_INDEXES,
    COLL_FORECAST_HISTORY: _FORECAST_HISTORY_INDEXES,
    COLL_PRICING_CURRENT: _PRICING_CURRENT_INDEXES,
    COLL_PRICING_HISTORY: _PRICING_HISTORY_INDEXES,
    COLL_INVENTORY_CURRENT: _INVENTORY_CURRENT_INDEXES,
    COLL_ANOMALY_CURRENT: _ANOMALY_CURRENT_INDEXES,
}


async def create_all_indexes() -> None:
    """
    Create every index in COLLECTION_INDEXES against the connected database.

    Idempotent: safe to call on every application/worker startup. MongoDB
    treats a `create_indexes` call describing an index that already exists
    with the same name and options as a no-op; it only raises if an index
    of the same name exists with *different* options, which surfaces a
    genuine drift between this file and the live database rather than
    silently masking it.
    """
    db = get_database()

    for collection_name, indexes in COLLECTION_INDEXES.items():
        created_names = await db[collection_name].create_indexes(indexes)
        logger.info(
            "Indexes ensured on collection=%s names=%s",
            collection_name,
            created_names,
        )

    logger.info(
        "Index initialization complete. collections=%d",
        len(COLLECTION_INDEXES),
    )