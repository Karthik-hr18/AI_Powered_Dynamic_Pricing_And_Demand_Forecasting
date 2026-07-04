"""
Database connection management.

Owns the single Motor (AsyncIOMotorClient) instance shared by the
FastAPI process and the background worker process. This module is
deliberately limited to connection lifecycle (connect / disconnect /
get a database handle) — Beanie document-model registration happens
separately, once the Document classes exist, per the frozen
Implementation Blueprint (Section 2.1 / M2).

Usage:
    # FastAPI lifespan (app/main.py) or worker startup (app/worker/main.py)
    await connect_to_mongo()
    ...
    await close_mongo_connection()

    # Anywhere else in the app that needs the database handle
    db = get_database()
"""

from __future__ import annotations

import logging
from typing import Optional

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo.errors import PyMongoError

from app.core.config import settings

logger = logging.getLogger(__name__)


class _MongoConnection:
    """
    Process-wide holder for the Motor client and database handle.

    A plain class with class-level attributes (rather than module-level
    globals) so the connection state is easy to reset in tests via
    monkeypatching, without relying on `global` statements.
    """

    client: Optional[AsyncIOMotorClient] = None
    database: Optional[AsyncIOMotorDatabase] = None


_connection = _MongoConnection()


async def connect_to_mongo() -> None:
    """
    Initialize the Motor client and verify connectivity.

    Idempotent: if a connection has already been established in this
    process, calling this again is a no-op. This matters because both
    `app/main.py` (API) and `app/worker/main.py` (worker) call this on
    startup, and some test setups may call it multiple times.

    Raises:
        RuntimeError: if `MONGODB_URL` is not configured.
        PyMongoError: if the initial connectivity check (ping) fails.
    """
    if _connection.client is not None:
        logger.info("MongoDB connection already initialized; skipping reconnect.")
        return

    if not settings.MONGODB_URL:
        raise RuntimeError(
            "MONGODB_URL is not configured. Set it in the environment "
            "or backend/.env before starting the API or worker process."
        )

    logger.info("Connecting to MongoDB...")

    client: AsyncIOMotorClient = AsyncIOMotorClient(settings.MONGODB_URL)

    try:
        # get_default_database() resolves the database name embedded in
        # the connection string path (e.g. mongodb://host:27017/pricing_platform).
        database = client.get_default_database()

        # Fail fast on misconfiguration rather than discovering a bad
        # connection string on the first real query later.
        await client.admin.command("ping")
    except PyMongoError:
        logger.exception("Failed to connect to MongoDB.")
        client.close()
        raise

    _connection.client = client
    _connection.database = database

    logger.info(
        "Connected to MongoDB. database=%s",
        database.name,
    )


async def close_mongo_connection() -> None:
    """
    Close the Motor client and clear the cached connection state.

    Safe to call even if no connection was ever established.
    """
    if _connection.client is None:
        return

    logger.info("Closing MongoDB connection...")
    _connection.client.close()
    _connection.client = None
    _connection.database = None
    logger.info("MongoDB connection closed.")


def get_database() -> AsyncIOMotorDatabase:
    """
    Return the active database handle.

    Every domain model / repository / service should obtain the
    database through this function rather than importing a module-level
    global directly, so connection lifecycle stays centralized here.

    Raises:
        RuntimeError: if called before `connect_to_mongo()` has
            completed (e.g. a startup-ordering bug).
    """
    if _connection.database is None:
        raise RuntimeError(
            "Database is not connected. Ensure connect_to_mongo() has "
            "been awaited during application/worker startup before any "
            "database access is attempted."
        )
    return _connection.database


def get_client() -> AsyncIOMotorClient:
    """
    Return the active Motor client.

    Needed by `init_indexes.py` and by Beanie's `init_beanie()` call
    (once document models exist), both of which require the client
    itself rather than just the database handle.

    Raises:
        RuntimeError: if called before `connect_to_mongo()` has completed.
    """
    if _connection.client is None:
        raise RuntimeError(
            "MongoDB client is not connected. Ensure connect_to_mongo() "
            "has been awaited during application/worker startup."
        )
    return _connection.client