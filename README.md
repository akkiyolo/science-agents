# ScienceAgents

**Walk up to Einstein. Argue with Darwin. Ask Curie about radium.**

ScienceAgents is a top-down RPG where you talk to embodied historical scientists — powered by real LLM agents grounded in their actual ideas, not generic chatbot personas.

<p align="center">
  <img alt="python" src="https://img.shields.io/badge/python-3.11+-3776AB?logo=python&logoColor=white">
  <img alt="fastapi" src="https://img.shields.io/badge/FastAPI-WebSockets-009688?logo=fastapi&logoColor=white">
  <img alt="langgraph" src="https://img.shields.io/badge/LangGraph-agents-1C3C3C">
  <img alt="phaser" src="https://img.shields.io/badge/Phaser-3.80-8ED6FB?logo=phaser&logoColor=black">
  <img alt="mongodb" src="https://img.shields.io/badge/MongoDB-Atlas%20Vector%20Search-47A248?logo=mongodb&logoColor=white">
</p>

---

## What's inside

- **7 scientist NPCs** — Einstein, Newton, Curie, Darwin, Galileo, Lovelace, and Tesla — each with a hand-written persona (era, field, personality, speaking style, key contributions).
- **RAG-grounded conversations** — every reply is backed by retrieval over the scientist's own writings, not just a system prompt.
- **Real-time dialogue** over WebSockets, streamed token-by-token into the game UI.
- **Per-player memory** — conversations persist so a scientist remembers who you are across sessions.
- **A real 2D game** — Phaser.js overworld where you walk up to a sprite to trigger dialogue, not a chat widget bolted onto a webpage.

## Architecture

```
learn-world-agents/
├── science-agents-api/      # FastAPI + LangGraph backend
│   └── src/science_agents/
│       ├── config/          # Settings + one YAML persona per scientist
│       ├── domain/          # ScientistPersona models + factory
│       ├── application/     # RAG pipeline, LangGraph conversation graph, memory
│       └── infrastructure/  # MongoDB client, REST routes, WebSocket endpoint
│
├── science-agents-ui/        # Phaser.js game client
│   └── src/game/             # Scene, character sprites, dialogue UI
│
└── Dockerfile                 # Multi-stage build: UI → static files served by the API
```

**Flow:** player walks up to an NPC in Phaser → UI opens a WebSocket to `/ws/dialogue/{scientist_id}` → LangGraph pulls relevant context via RAG from MongoDB Atlas Vector Search → Groq LLM streams a response back in character.

## Tech stack

| Layer | Choice |
|---|---|
| Agent framework | LangGraph + LangChain |
| LLM | Groq |
| Embeddings | Google Gemini (`gemini-embedding-001`) |
| Vector store | MongoDB Atlas Vector Search |
| Backend | FastAPI + WebSockets |
| Frontend | Phaser 3 (vanilla JS, Webpack) |
| Package manager | uv (Python), npm (JS) |

## Quick start

**Backend**
```bash
cd science-agents-api
cp .env.example .env      # add GROQ_API_KEY, GOOGLE_API_KEY, MONGO_DB_URI
uv sync
uv run python scripts/ingest_all.py     # embed scientist source material
uv run uvicorn science_agents.infrastructure.api.main:app --reload --port 8000
```

**Frontend**
```bash
cd science-agents-ui
npm install
npm start
```

**Or run the whole thing in one container:**
```bash
docker build -t science-agents .
docker run -p 8000:8000 --env-file science-agents-api/.env science-agents
```
The Docker build compiles the Phaser UI first, then serves it as static files straight from the FastAPI app — one image, one port.

## Environment variables

```env
GROQ_API_KEY=...
GOOGLE_API_KEY=...
MONGO_DB_URI=mongodb+srv://user:pass@cluster.mongodb.net/?appName=cluster
LOG_LEVEL=INFO   # optional
```

## Testing

```bash
cd science-agents-api
uv run pytest
```

## Roadmap

- [ ] Pixel-art sprites + idle/walk/talk animations per scientist
- [ ] Dialogue portraits
- [ ] More scientists (Turing, Feynman, Hypatia?)
- [ ] Voice output for responses
