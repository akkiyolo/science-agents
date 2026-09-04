"""
Vector Index Setup
-------------------
Creates MongoDB Atlas vector search indexes per scientist collection.
Uses the createSearchIndexes command available on Atlas M0+ clusters.

Will be fully implemented in Step 2.
"""

from __future__ import annotations

from science_agents.config.settings import EMBEDDING_DIMENSION, logger
from science_agents.infrastructure.mongo.client import get_database


def ensure_vector_index(collection_name: str) -> None:
    """
    Ensure a vector search index exists for the given collection.

    On Atlas free tier (M0), vector search indexes must be created via
    the Atlas UI or Atlas CLI. This function checks if data exists and
    logs instructions if the index needs manual creation.
    """
    db = get_database()
    collection = db[collection_name]

    # Log information about the collection
    doc_count = collection.count_documents({})
    logger.info(
        "Collection '%s': %d documents. "
        "Vector search index must be created via Atlas UI with field 'embedding' "
        "(dimensions=%d, similarity=cosine, type=vector).",
        collection_name,
        doc_count,
        EMBEDDING_DIMENSION,
    )
