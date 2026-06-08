"""Scenario schema — Pydantic-based validation of scenario YAML files."""

from __future__ import annotations

from typing import Any

from .models import ScenarioDef


def validate_scenario(data: dict[str, Any]) -> ScenarioDef:
    """Parse and validate raw YAML data into a ScenarioDef model.

    Raises pydantic.ValidationError on invalid input.
    """
    return ScenarioDef.model_validate(data)
