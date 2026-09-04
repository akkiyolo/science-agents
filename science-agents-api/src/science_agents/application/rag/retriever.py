"""
RAG Retriever
--------------
Per-scientist namespaced retrieval from MongoDB Atlas vector index.
Queries only the target scientist's collection to prevent cross-contamination.
"""

from __future__ import annotations

import asyncio
from langchain_mongodb import MongoDBAtlasVectorSearch

from science_agents.config.settings import logger
from science_agents.domain.scientist_factory import load_scientist
from science_agents.infrastructure.mongo.client import get_database
from science_agents.application.rag.ingestion import get_embeddings


async def retrieve(scientist_id: str, query: str, top_k: int = 5) -> list[str]:
    """Retrieve relevant document chunks for a scientist given a query."""
    logger.info("Retrieving top %d context chunks for '%s' with query: '%s'", top_k, scientist_id, query)
    
    try:
        scientist = load_scientist(scientist_id)
        db = get_database()
        collection = db[scientist.collection_name]
        
        embeddings = get_embeddings()
        
        vector_store = MongoDBAtlasVectorSearch(
            collection=collection,
            embedding=embeddings,
            index_name="default"
        )
        
        # Perform similarity search
        docs = await asyncio.to_thread(
            vector_store.similarity_search,
            query=query,
            k=top_k
        )
        
        context_chunks = [doc.page_content for doc in docs]
        logger.info("Retrieved %d chunks for '%s'", len(context_chunks), scientist_id)
        return context_chunks
        
    except Exception as e:
        logger.error("Error during retrieval for '%s': %s", scientist_id, e)
        return []
