"""
Smoke tests for the scaffold — verifies configs load and structure is intact.
"""

import pytest
from pathlib import Path


def test_scientist_configs_exist():
    """All three scientist YAML configs should exist."""
    config_dir = Path(__file__).resolve().parents[1] / "src" / "science_agents" / "config" / "scientists"
    assert (config_dir / "einstein.yaml").exists()
    assert (config_dir / "newton.yaml").exists()
    assert (config_dir / "curie.yaml").exists()


def test_load_scientist_factory():
    """scientist_factory should load all three scientists."""
    from science_agents.domain.scientist_factory import load_all_scientists

    scientists = load_all_scientists()
    assert "einstein" in scientists
    assert "newton" in scientists
    assert "curie" in scientists
    assert scientists["einstein"].name == "Albert Einstein"
    assert scientists["newton"].field == "Physics, Mathematics, Astronomy"
    assert scientists["curie"].scientist_id == "curie"


def test_scientist_collection_names():
    """Each scientist should have a unique MongoDB collection name."""
    from science_agents.domain.scientist_factory import load_all_scientists

    scientists = load_all_scientists()
    assert scientists["einstein"].collection_name == "memory_einstein"
    assert scientists["newton"].collection_name == "memory_newton"
    assert scientists["curie"].collection_name == "memory_curie"
