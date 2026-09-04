#!/usr/bin/env python3
"""
Ingest All Scientists
-----------------------
One-off script to run the RAG ingestion pipeline for all configured scientists.
Downloads source URLs, chunks text, embeds via Gemini, stores in MongoDB Atlas.

Usage:
    cd science-agents-api
    uv run python scripts/ingest_all.py
"""

import asyncio
import sys
from pathlib import Path

# Ensure the src directory is on the path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from science_agents.config.settings import validate_settings, logger
from science_agents.application.rag.ingestion import ingest_all


async def main():
    logger.info("=" * 60)
    logger.info("ScienceAgents — RAG Ingestion Pipeline")
    logger.info("=" * 60)

    validate_settings()
    await ingest_all()

    logger.info("=" * 60)
    logger.info("Ingestion complete!")
    logger.info("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
