"""
MongoDB Client
---------------
Singleton MongoDB client for the science-agents backend.
Connects to MongoDB Atlas using the MONGO_DB_URI env var.
"""

from __future__ import annotations

from pymongo import MongoClient
from pymongo.database import Database

from science_agents.config.settings import MONGO_DB_URI, MONGO_DB_NAME, logger

_client: MongoClient | None = None


def get_mongo_client() -> MongoClient:
    """Return the singleton MongoDB client, creating it on first call."""
    global _client
    if _client is None:
        if not MONGO_DB_URI:
            raise ValueError("MONGO_DB_URI is not set")
        logger.info("Connecting to MongoDB Atlas...")
        _client = MongoClient(MONGO_DB_URI)
        # Verify connection
        _client.admin.command("ping")
        logger.info("MongoDB Atlas connection verified ✓")
    return _client


def get_database() -> Database:
    """Return the science_agents database."""
    return get_mongo_client()[MONGO_DB_NAME]


def close_mongo_client() -> None:
    """Close the MongoDB client connection."""
    global _client
    if _client is not None:
        _client.close()
        _client = None
        logger.info("MongoDB client connection closed")
