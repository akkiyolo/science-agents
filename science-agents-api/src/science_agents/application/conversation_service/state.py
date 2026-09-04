"""
Conversation State
-------------------
Typed state definition for the LangGraph conversation graph.

Will be fully implemented in Step 3.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ConversationState:
    """State object passed through the LangGraph conversation graph nodes."""

    scientist_id: str = ""
    player_id: str = ""
    user_message: str = ""
    retrieved_context: list[str] = field(default_factory=list)
    persona_filtered_context: str = ""
    response: str = ""
    chat_history: list[dict[str, str]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
