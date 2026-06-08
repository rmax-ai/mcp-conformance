"""Tests for scenario models and YAML loading."""

import yaml

from mcp_conformance.scenario.models import (
    ScenarioDef,
    ScenarioResult,
    StepDef,
    StepType,
)


def test_scenario_model_creation() -> None:
    scenario = ScenarioDef(
        id="test-scenario",
        title="Test Scenario",
        partner={"type": "mcp_auth_test_server"},
        steps=[
            StepDef(type=StepType.CLIENT_REQUEST, action="partner.health"),
        ],
    )
    assert scenario.id == "test-scenario"
    assert len(scenario.steps) == 1


def test_scenario_step_defaults() -> None:
    step = StepDef(type=StepType.ASSERT)
    assert step.params == {}
    assert step.assert_ == []


def test_scenario_result_aggregation() -> None:
    result = ScenarioResult(
        scenario_id="test",
        scenario_title="Test",
        passed=True,
        total_steps=2,
        passed_steps=2,
    )
    assert result.passed
    assert result.total_steps == 2


def test_minimal_yaml_roundtrip() -> None:
    """Load a minimal scenario from YAML and validate."""
    raw = """
id: test-minimal
title: Minimal Test Scenario
version: "0.1"
partner:
  type: mcp_auth_test_server
steps:
  - id: health
    type: client_request
    action: partner.health
    assert:
      - type: status
        expected: 200
"""
    data = yaml.safe_load(raw)
    scenario = ScenarioDef.model_validate(data)
    assert scenario.id == "test-minimal"
    assert len(scenario.steps) == 1
    assert scenario.steps[0].assert_[0].expected == 200


def test_assertion_def_aliases() -> None:
    """Verify 'assert' YAML key maps to assert_ field."""
    raw = """
id: test-assert-aliases
title: Assert Aliases
partner:
  type: generic_mcp_server
steps:
  - id: check
    type: client_request
    action: partner.health
    assert:
      - type: status
        expected: 200
"""
    data = yaml.safe_load(raw)
    scenario = ScenarioDef.model_validate(data)
    assert len(scenario.steps[0].assert_) == 1
