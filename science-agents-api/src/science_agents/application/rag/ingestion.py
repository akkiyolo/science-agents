"""
RAG Ingestion Pipeline
-----------------------
Downloads content from scientist source URLs (Wikipedia, etc.),
chunks text, embeds via Google Gemini, and stores vectors in
MongoDB Atlas with per-scientist namespaced collections.
"""

from __future__ import annotations

import asyncio
from langchain_community.document_loaders import WebBaseLoader
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_mongodb import MongoDBAtlasVectorSearch

from science_agents.config.settings import (
    GOOGLE_API_KEY,
    EMBEDDING_MODEL,
    logger,
)
from science_agents.domain.scientist_factory import load_scientist, load_all_scientists
from science_agents.application.rag.splitters import get_text_splitter
from science_agents.infrastructure.mongo.client import get_database
from science_agents.infrastructure.mongo.vector_index import ensure_vector_index


def get_embeddings() -> GoogleGenerativeAIEmbeddings:
    """Return the configured Gemini embeddings model."""
    if not GOOGLE_API_KEY:
        raise ValueError("GOOGLE_API_KEY is not set")
    return GoogleGenerativeAIEmbeddings(
        model=EMBEDDING_MODEL,
        google_api_key=GOOGLE_API_KEY,
    )


async def ingest_scientist(scientist_id: str) -> None:
    """Download, chunk, embed, and store documents for a single scientist."""
    logger.info("Starting ingestion for scientist '%s'...", scientist_id)
    scientist = load_scientist(scientist_id)
    
    if not scientist.source_urls:
        logger.warning("No source URLs configured for scientist '%s', skipping ingestion.", scientist_id)
        return

    # 1. Download content
    logger.info("Downloading content from %d URLs...", len(scientist.source_urls))
    loader = WebBaseLoader(scientist.source_urls)
    # Using sync load in a thread to avoid blocking if loader doesn't support async well
    docs = await asyncio.to_thread(loader.load)
    logger.info("Downloaded %d documents.", len(docs))

    # 2. Chunk text
    splitter = get_text_splitter(chunk_size=1000, chunk_overlap=200)
    chunks = splitter.split_documents(docs)
    
    # LIMIT chunks to avoid Gemini free tier rate limit (100 req/min)
    chunks = chunks[:20]
    logger.info("Split into %d chunks (limited to 20 to avoid rate limits).", len(chunks))

    # Add metadata to chunks
    for i, chunk in enumerate(chunks):
        chunk.metadata["scientist_id"] = scientist_id
        chunk.metadata["chunk_index"] = i

    # 3. Store in MongoDB
    db = get_database()
    collection = db[scientist.collection_name]
    
    # Clear existing documents for this scientist to avoid duplicates
    collection.delete_many({})
    logger.info("Cleared existing documents in collection '%s'", scientist.collection_name)
    
    embeddings = get_embeddings()
    
    logger.info("Embedding and storing %d chunks to MongoDB collection '%s'...", len(chunks), scientist.collection_name)
    await asyncio.to_thread(
        MongoDBAtlasVectorSearch.from_documents,
        documents=chunks,
        embedding=embeddings,
        collection=collection,
        index_name="default" # Name of the Atlas Vector Search Index
    )
    
    # Ensure index check is logged
    ensure_vector_index(scientist.collection_name)
    logger.info("Ingestion completed for scientist '%s'.", scientist_id)


async def ingest_all() -> None:
    """Run ingestion for all configured scientists."""
    scientists = load_all_scientists()
    for scientist_id in scientists.keys():
        await ingest_scientist(scientist_id)
