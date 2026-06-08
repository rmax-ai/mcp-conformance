"""Tests for ScenarioRunner request execution and auth resolution."""

from __future__ import annotations

from typing import Any

import pytest

from mcp_conformance.partners.base import AuthStep, FaultConfig, MCPResponse, TestPartner
from mcp_conformance.runner import ScenarioRunner
from mcp_conformance.scenario.models import ScenarioDef, StepDef, StepType


class StubPartner(TestPartner):
    def __init__(self) -> None:
        self.base_url = "http://example.test"
        self.last_auth_step: AuthStep | None = None
        self.last_fault: FaultConfig | None = None
        self.last_mcp_auth: dict[str, Any] | None = None
        self.last_mcp_headers: dict[str, str] | None = None
        self.reset_calls = 0
        self.debug_calls: list[str] = []

    async def health(self) -> bool:
        return True

    async def send_mcp_request(
        self,
        method: str,
        params: dict[str, Any] | None = None,
        *,
        auth: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        endpoint: str | None = None,
    ) -> MCPResponse:
        self.last_mcp_auth = auth
        self.last_mcp_headers = headers
        return MCPResponse(status=401, headers={}, body={"error": {"code": 401}})

    async def send_auth_request(self, step: AuthStep) -> MCPResponse:
        self.last_auth_step = step
        if step.url.startswith("/test/tokens/expired"):
            return MCPResponse(
                status=201,
                headers={},
                body={"access_token": "expired-token", "token_type": "Bearer"},
            )
        return MCPResponse(status=200, headers={}, body={"ok": True})

    async def reset_state(self) -> None:
        self.reset_calls += 1

    async def get_debug_state(self, endpoint: str) -> dict[str, Any]:
        self.debug_calls.append(endpoint)
        return {"endpoint": endpoint}

    async def configure_injection(self, fault: FaultConfig) -> None:
        self.last_fault = fault


@pytest.mark.asyncio
async def test_authorize_uses_query_params_and_no_body() -> None:
    partner = StubPartner()
    runner = ScenarioRunner(partner)
    step = StepDef(
        id="authorize",
        type=StepType.CLIENT_REQUEST,
        action="oauth.auth_code.authorize",
        request={
            "params": {
                "response_type": "code",
                "client_id": "test-client",
                "redirect_uri": "http://127.0.0.1/callback",
            }
        },
    )

    trace = await runner._execute_client_request(step)

    assert partner.last_auth_step is not None
    assert partner.last_auth_step.method == "GET"
    assert partner.last_auth_step.url.startswith("/authorize?")
    assert "response_type=code" in partner.last_auth_step.url
    assert partner.last_auth_step.body is None
    assert trace.request_body is None


@pytest.mark.asyncio
async def test_authorize_converts_json_body_to_query_params() -> None:
    partner = StubPartner()
    runner = ScenarioRunner(partner)
    step = StepDef(
        id="authorize",
        type=StepType.CLIENT_REQUEST,
        action="oauth.auth_code.authorize",
        request={
            "json": {
                "response_type": "code",
                "client_id": "test-client",
            }
        },
    )

    await runner._execute_client_request(step)

    assert partner.last_auth_step is not None
    assert partner.last_auth_step.method == "GET"
    assert partner.last_auth_step.url == "/authorize?response_type=code&client_id=test-client"
    assert partner.last_auth_step.body is None


@pytest.mark.asyncio
async def test_runner_stores_step_results_and_resolves_bearer_token() -> None:
    partner = StubPartner()
    runner = ScenarioRunner(partner)
    scenario = ScenarioDef(
        id="expired-token",
        title="Expired token",
        steps=[
            StepDef(
                id="mint_expired",
                type=StepType.CLIENT_REQUEST,
                action="test.tokens.mint_expired",
                request={
                    "json": {
                        "subject": "test-user",
                        "scope": "mcp:tools:read",
                        "audience": "http://example.test/mcp/oauth",
                    }
                },
                assert_=[],
            ),
            StepDef(
                id="call",
                type=StepType.CLIENT_REQUEST,
                action="mcp.request",
                auth={"bearer_token": {"from_step": "mint_expired", "path": "$.access_token"}},
                request={"method": "tools/list", "params": {}},
                assert_=[],
            ),
        ],
    )

    result = await runner.run(scenario)

    assert result.passed is True
    assert runner._step_results["mint_expired"]["access_token"] == "expired-token"
    assert partner.last_mcp_auth == {"bearer_token": "expired-token"}


@pytest.mark.asyncio
async def test_test_faults_configure_uses_json_payload() -> None:
    partner = StubPartner()
    runner = ScenarioRunner(partner)
    step = StepDef(
        id="fault",
        type=StepType.CLIENT_REQUEST,
        action="test.faults.configure",
        request={
            "json": {
                "endpoint": "/test/cimd/slow.json",
                "behavior": "delay",
                "params": {"delay_seconds": 10},
            }
        },
    )

    trace = await runner._execute_client_request(step)

    assert trace.request_body == {
        "endpoint": "/test/cimd/slow.json",
        "behavior": "delay",
        "params": {"delay_seconds": 10},
    }
    assert partner.last_fault is not None
    assert partner.last_fault.endpoint == "/test/cimd/slow.json"
    assert partner.last_fault.behavior == "delay"


@pytest.mark.asyncio
async def test_test_reset_and_state_use_partner_hooks() -> None:
    partner = StubPartner()
    runner = ScenarioRunner(partner)

    reset_trace = await runner._execute_client_request(
        StepDef(id="reset", type=StepType.CLIENT_REQUEST, action="test.reset")
    )
    state_trace = await runner._execute_client_request(
        StepDef(id="state", type=StepType.CLIENT_REQUEST, action="test.state")
    )

    assert partner.reset_calls == 1
    assert partner.debug_calls == ["/test/state"]
    assert reset_trace.response_body == {"reset": True}
    assert state_trace.response_body == {"endpoint": "/test/state"}
