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


def test_no_auth_scenario_yaml_roundtrip() -> None:
    """Verify a no-auth scenario YAML parses correctly."""
    raw = """
id: no_auth.tools_list
title: "tools/list succeeds on a no-auth MCP server"
version: "0.1"
spec_refs:
  - mcp.tools
  - jsonrpc.2_0
capabilities:
  required:
    - mcp.no_auth
    - mcp.tools
partner:
  type: generic_mcp_server
steps:
  - id: list_tools
    type: client_request
    action: mcp.request
    request:
      method: tools/list
      params: {}
    assert:
      - type: jsonrpc_version
      - type: result_exists
      - type: result_shape
        expected:
          - tools
"""
    data = yaml.safe_load(raw)
    scenario = ScenarioDef.model_validate(data)
    assert scenario.id == "no_auth.tools_list"
    assert scenario.partner["type"] == "generic_mcp_server"
    assert scenario.capabilities == {"required": ["mcp.no_auth", "mcp.tools"]}
    assert len(scenario.steps) == 1
    assert scenario.steps[0].auth is None  # no auth for no-auth scenario


def test_bearer_scenario_yaml_roundtrip() -> None:
    """Verify a bearer-token scenario YAML parses correctly with from_env."""
    raw = """
id: bearer.valid_token
title: "Bearer token auth happy path"
version: "0.1"
spec_refs:
  - rfc6750
  - mcp.authorization
capabilities:
  required:
    - mcp.bearer_auth
partner:
  type: generic_mcp_server
steps:
  - id: call
    type: client_request
    action: mcp.request
    auth:
      bearer_token:
        from_env: MCP_BEARER_TOKEN
    request:
      method: tools/list
      params: {}
    assert:
      - type: jsonrpc_version
      - type: result_exists
"""
    data = yaml.safe_load(raw)
    scenario = ScenarioDef.model_validate(data)
    assert scenario.id == "bearer.valid_token"
    assert scenario.capabilities == {"required": ["mcp.bearer_auth"]}
    assert len(scenario.steps) == 1
    assert scenario.steps[0].auth == {"bearer_token": {"from_env": "MCP_BEARER_TOKEN"}}


def test_bearer_inline_token_parses() -> None:
    """Verify a bearer token provided as a raw string parses."""
    raw = """
id: bearer.invalid_token
title: "Invalid bearer token"
partner:
  type: generic_mcp_server
steps:
  - id: call
    type: client_request
    action: mcp.request
    auth:
      bearer_token: "garbage-token"
    request:
      method: tools/list
      params: {}
    assert:
      - type: status
        expected: 401
"""
    data = yaml.safe_load(raw)
    scenario = ScenarioDef.model_validate(data)
    assert scenario.steps[0].auth == {"bearer_token": "garbage-token"}
