"""
FastAPI Application Entrypoint
-------------------------------
Creates and configures the FastAPI app with CORS, lifespan events,
and route/WebSocket mounting.

Will be fully implemented in Step 4.
"""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from science_agents.config.settings import logger, validate_settings
from science_agents.infrastructure.mongo.client import close_mongo_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown lifecycle."""
    logger.info("🔬 ScienceAgents API starting up...")
    validate_settings()
    yield
    logger.info("🔬 ScienceAgents API shutting down...")
    close_mongo_client()


app = FastAPI(
    title="ScienceAgents API",
    description="AI-powered scientist NPC conversation engine",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS — allow the Phaser.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount routes and websocket handlers
from science_agents.infrastructure.api.routes import router  # noqa: E402
from science_agents.infrastructure.api.websocket import ws_router  # noqa: E402

app.include_router(router, prefix="/api")
app.include_router(ws_router)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "service": "science-agents-api"}
