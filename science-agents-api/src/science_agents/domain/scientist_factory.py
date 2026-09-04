"""
Scientist Factory — loads YAML persona configs into structured domain objects.
"""

from __future__ import annotations

import yaml
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from science_agents.config.settings import SCIENTISTS_CONFIG_DIR, logger


@dataclass
class ScientistPersona:
    """Immutable domain object representing a scientist NPC's persona."""

    name: str
    scientist_id: str
    era: str
    field: str
    nationality: str
    personality_traits: list[str]
    speaking_style: str
    key_contributions: list[str]
    system_prompt: str
    source_urls: list[str] = field(default_factory=list)

    @property
    def collection_name(self) -> str:
        """MongoDB collection name for this scientist's memory/vectors."""
        return f"memory_{self.scientist_id}"


def load_scientist(scientist_id: str) -> ScientistPersona:
    """Load a single scientist persona from its YAML config file."""
    config_path = SCIENTISTS_CONFIG_DIR / f"{scientist_id}.yaml"
    if not config_path.exists():
        raise FileNotFoundError(f"No config found for scientist '{scientist_id}' at {config_path}")

    with open(config_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    logger.info("Loaded scientist persona: %s (%s)", data["name"], scientist_id)
    return ScientistPersona(
        name=data["name"],
        scientist_id=data["scientist_id"],
        era=data["era"],
        field=data["field"],
        nationality=data["nationality"],
        personality_traits=data["personality_traits"],
        speaking_style=data["speaking_style"],
        key_contributions=data["key_contributions"],
        system_prompt=data["system_prompt"],
        source_urls=data.get("source_urls", []),
    )


def load_all_scientists() -> dict[str, ScientistPersona]:
    """Load all scientist personas from the config directory."""
    scientists: dict[str, ScientistPersona] = {}
    for yaml_file in sorted(SCIENTISTS_CONFIG_DIR.glob("*.yaml")):
        scientist_id = yaml_file.stem
        try:
            scientists[scientist_id] = load_scientist(scientist_id)
        except Exception as e:
            logger.error("Failed to load scientist '%s': %s", scientist_id, e)
    logger.info("Loaded %d scientist personas: %s", len(scientists), list(scientists.keys()))
    return scientists
