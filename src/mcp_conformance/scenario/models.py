"""Scenario data models — Pydantic models for scenario YAML deserialization."""

from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field

from mcp_conformance.wire.capture import WireTrace


class StepType(StrEnum):
    CLIENT_REQUEST = "client_request"
    SERVER_RESPOND = "server_respond"
    ASSERT = "assert"
    WAIT = "wait"
    INJECT_FAULT = "inject_fault"
    LOG_DEBUG = "log_debug"


class AssertionDef(BaseModel):
    """A single assertion to check against a step result."""

    type: str
    expected: Any = None
    path: str | None = None
    exists: bool | None = None
    equals: Any = None
    matches: str | None = None
    name: str | None = None


class StepDef(BaseModel):
    """A single step within a scenario."""

    id: str = ""
    type: StepType
    action: str = ""
    request: dict[str, Any] | None = None
    endpoint: str | None = None
    assert_: list[AssertionDef] = Field(default_factory=list, alias="assert")
    auth: dict[str, Any] | None = None
    params: dict[str, Any] = Field(default_factory=dict)
    seconds: float | None = None


class ScenarioDef(BaseModel):
    """Top-level scenario definition loaded from YAML."""

    id: str
    title: str
    version: str = "0.1"
    spec_refs: list[str] = Field(default_factory=list)
    capabilities: dict[str, list[str]] = Field(default_factory=dict)
    partner: dict[str, Any] = Field(default_factory=dict)
    steps: list[StepDef]


class StepResult(BaseModel):
    """Result of executing a single scenario step."""

    step_index: int
    step_id: str = ""
    passed: bool = False
    errors: list[str] = Field(default_factory=list)
    request: dict[str, Any] | None = None
    response: dict[str, Any] | None = None
    wire_trace: WireTrace | None = None
    elapsed_ms: float = 0.0
    skipped: bool = False


class ScenarioResult(BaseModel):
    """Aggregated result for a complete scenario run."""

    scenario_id: str
    scenario_title: str = ""
    passed: bool = False
    step_results: list[StepResult] = Field(default_factory=list)
    total_steps: int = 0
    passed_steps: int = 0
    failed_steps: int = 0
    skipped_steps: int = 0
    total_elapsed_ms: float = 0.0
