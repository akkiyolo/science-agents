# ScienceAgents API

AI-powered backend for the ScienceAgents game — real-time conversations with embodied historical scientist NPCs (Einstein, Newton, Curie).

## Architecture

```
src/science_agents/
├── config/          # Settings + scientist YAML personas
├── domain/          # ScientistPersona models + factory
├── application/     # RAG pipeline + LangGraph conversation graph + memory
└── infrastructure/  # MongoDB client + FastAPI/WebSocket endpoints
```

## Quick Start

```bash
# Install dependencies
uv sync

# Run the API
uv run uvicorn science_agents.infrastructure.api.main:app --reload --port 8000

# Run ingestion (after implementing Step 2)
uv run python scripts/ingest_all.py

# Run tests
uv run pytest
```

## Tech Stack

- **LLM**: Groq (llama-3.3-70b-versatile)
- **Embeddings**: Google Gemini (text-embedding-004)
- **Vector Store**: MongoDB Atlas (free tier M0)
- **Agent Framework**: LangGraph + LangChain
- **API**: FastAPI + WebSockets
- **Package Manager**: uv
