"""Scenario loader — loads and validates YAML scenario files."""

from __future__ import annotations

from pathlib import Path

import yaml

from .models import ScenarioDef
from .schema import validate_scenario


def load_scenario(path: str | Path) -> ScenarioDef:
    """Load a YAML scenario file and return a validated ScenarioDef."""
    raw = Path(path).read_text()
    data = yaml.safe_load(raw)
    return validate_scenario(data)


def load_scenarios(paths: list[str | Path]) -> list[ScenarioDef]:
    """Load multiple scenario files."""
    return [load_scenario(p) for p in paths]
