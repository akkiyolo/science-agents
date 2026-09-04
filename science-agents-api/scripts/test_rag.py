#!/usr/bin/env python3
"""
Test RAG standalone
--------------------
CLI script to test RAG retrieval standalone (Step 2).
"""

import asyncio
import sys
from pathlib import Path

# Ensure the src directory is on the path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from science_agents.config.settings import validate_settings, logger
from science_agents.application.rag.retriever import retrieve


async def main():
    validate_settings()
    
    query = "What is the theory of relativity?"
    scientist_id = "einstein"
    
    print(f"\n--- Testing RAG Retrieval for {scientist_id} ---")
    print(f"Query: '{query}'\n")
    
    chunks = await retrieve(scientist_id, query, top_k=2)
    
    for i, chunk in enumerate(chunks):
        print(f"\n[Chunk {i+1}]")
        print(chunk[:500] + "..." if len(chunk) > 500 else chunk)
        
    print("\n-------------------------------------------")


if __name__ == "__main__":
    asyncio.run(main())
