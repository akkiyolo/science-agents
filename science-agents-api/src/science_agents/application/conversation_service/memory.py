"""
Memory Management
------------------
Short-term (per-session) and long-term (MongoDB) conversation memory.
Keyed by (player_id, scientist_id) to prevent context leaking between NPCs.

Will be fully implemented in Step 3.
"""

from __future__ import annotations
import asyncio

from science_agents.config.settings import logger
from science_agents.infrastructure.mongo.client import get_database

class ConversationMemory:
    """Manages short-term and long-term memory for scientist conversations."""

    def __init__(self, player_id: str, scientist_id: str):
        self.player_id = player_id
        self.scientist_id = scientist_id
        self._short_term: list[dict[str, str]] = []
        self._collection_name = f"conversations_{scientist_id}"
        logger.info("ConversationMemory initialized for player=%s, scientist=%s", player_id, scientist_id)

    def add_message(self, role: str, content: str) -> None:
        """Add a message to short-term memory."""
        self._short_term.append({"role": role, "content": content})

    def get_history(self) -> list[dict[str, str]]:
        """Return current session's message history."""
        return self._short_term.copy()

    async def save_to_long_term(self) -> None:
        """Persist current session to MongoDB long-term memory."""
        if not self._short_term:
            return
            
        logger.info("Saving session to long term memory for %s", self.player_id)
        db = get_database()
        collection = db[self._collection_name]
        
        doc = {
            "player_id": self.player_id,
            "scientist_id": self.scientist_id,
            "messages": self._short_term,
        }
        
        await asyncio.to_thread(
            collection.update_one,
            {"player_id": self.player_id},
            {"$push": {"sessions": doc}},
            upsert=True
        )

    async def load_from_long_term(self) -> list[dict[str, str]]:
        """Load past conversation summaries from MongoDB."""
        db = get_database()
        collection = db[self._collection_name]
        
        doc = await asyncio.to_thread(
            collection.find_one,
            {"player_id": self.player_id}
        )
        
        if not doc or "sessions" not in doc:
            return []
            
        # Return a flattened list of recent messages or a summary
        # For MVP, we'll just return the last session's messages if they exist
        sessions = doc["sessions"]
        if sessions:
            return sessions[-1]["messages"]
        return []

    def clear(self) -> None:
        """Clear short-term memory (session end)."""
        self._short_term.clear()
