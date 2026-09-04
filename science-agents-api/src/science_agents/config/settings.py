"""
Central settings module.
Loads all environment variables and provides them as typed constants.
"""

import os
import logging
from pathlib import Path

from dotenv import load_dotenv

# Load .env from project root (science-agents-api/) or repo root
_env_paths = [
    Path(__file__).resolve().parents[3] / ".env",   # science-agents-api/.env
    Path(__file__).resolve().parents[4] / ".env",   # repo root .env
]
for _p in _env_paths:
    if _p.exists():
        load_dotenv(_p)
        break

# --- API Keys ---
GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
MONGO_DB_URI: str = os.getenv("MONGO_DB_URI", "")

GROQ_MODEL: str = "qwen/qwen3.8-27b"
EMBEDDING_MODEL: str = "gemini-embedding-001"
EMBEDDING_DIMENSION: int = 768

# --- MongoDB ---
MONGO_DB_NAME: str = "science_agents"

# --- Paths ---
PROJECT_ROOT: Path = Path(__file__).resolve().parents[3]
SCIENTISTS_CONFIG_DIR: Path = Path(__file__).resolve().parent / "scientists"

# --- Logging ---
LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("science_agents")


def validate_settings() -> None:
    """Raise if any required env var is missing."""
    missing = []
    if not GROQ_API_KEY:
        missing.append("GROQ_API_KEY")
    if not GOOGLE_API_KEY:
        missing.append("GOOGLE_API_KEY")
    if not MONGO_DB_URI:
        missing.append("MONGO_DB_URI")
    if missing:
        raise EnvironmentError(f"Missing required environment variables: {', '.join(missing)}")
