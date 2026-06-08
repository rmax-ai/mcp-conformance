"""Tests for scenario model and YAML parsing."""

from mcp_conformance.scenario import (
    Assertion,
    Scenario,
    ScenarioStep,
    StepType,
)


def test_scenario_creation(happy_path_scenario: Scenario) -> None:
    assert happy_path_scenario.name == "auth-code-happy-path"
    assert len(happy_path_scenario.steps) == 2
    assert happy_path_scenario.steps[0].step_type == StepType.CLIENT_REQUEST


def test_scenario_step_defaults() -> None:
    step = ScenarioStep(step_type=StepType.ASSERT)
    assert step.params == {}
    assert step.assertions == []


def test_assertion_creation() -> None:
    a = Assertion(type="status", expected=200)
    assert a.type == "status"
    assert a.expected == 200
