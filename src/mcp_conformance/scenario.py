"""Scenario model — YAML-serializable definition of a conformance scenario."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class StepType(StrEnum):
    CLIENT_REQUEST = "client_request"
    SERVER_RESPOND = "server_respond"
    ASSERT = "assert"
    WAIT = "wait"
    INJECT_FAULT = "inject_fault"
    LOG_DEBUG = "log_debug"


@dataclass
class Assertion:
    """An assertion to check against a step result."""

    type: str  # e.g. "status", "header", "body_json_path", "jsonrpc_version"
    expected: Any


@dataclass
class ScenarioStep:
    """A single step in a scenario."""

    step_type: StepType
    params: dict[str, Any] = field(default_factory=dict)
    assertions: list[Assertion] = field(default_factory=list)


@dataclass
class Scenario:
    """A complete conformance scenario."""

    name: str
    description: str
    steps: list[ScenarioStep]


@dataclass
class StepResult:
    """Result of executing a single scenario step."""

    step_index: int
    passed: bool
    errors: list[str]
    request: dict[str, Any] | None = None
    response: dict[str, Any] | None = None
    elapsed_ms: float = 0.0


@dataclass
class ScenarioResult:
    """Aggregated result for a complete scenario run."""

    scenario_name: str
    passed: bool
    step_results: list[StepResult]
    total_steps: int
    passed_steps: int
    failed_steps: int
