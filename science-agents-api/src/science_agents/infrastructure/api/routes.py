"""
REST Routes
-------------
REST endpoints for listing scientists, session management, etc.

Will be fully implemented in Step 4.
"""

from __future__ import annotations

from fastapi import APIRouter

from science_agents.domain.scientist_factory import load_all_scientists
from science_agents.config.settings import logger

router = APIRouter(tags=["scientists"])


@router.get("/scientists")
async def list_scientists():
    """Return metadata for all available scientist NPCs."""
    scientists = load_all_scientists()
    return {
        "scientists": [
            {
                "id": s.scientist_id,
                "name": s.name,
                "era": s.era,
                "field": s.field,
                "nationality": s.nationality,
            }
            for s in scientists.values()
        ]
    }


@router.get("/scientists/{scientist_id}")
async def get_scientist(scientist_id: str):
    """Return detailed metadata for a specific scientist NPC."""
    from science_agents.domain.scientist_factory import load_scientist

    try:
        s = load_scientist(scientist_id)
        return {
            "id": s.scientist_id,
            "name": s.name,
            "era": s.era,
            "field": s.field,
            "nationality": s.nationality,
            "personality_traits": s.personality_traits,
            "key_contributions": s.key_contributions,
        }
    except FileNotFoundError:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail=f"Scientist '{scientist_id}' not found")
