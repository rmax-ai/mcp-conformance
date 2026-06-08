"""Runner — orchestrates scenario steps against a test partner."""

from __future__ import annotations

from enum import StrEnum
from typing import Any

from mcp_conformance.assertions.http import assert_json_path, assert_status
from mcp_conformance.assertions.mcp import assert_jsonrpc_version, assert_result_exists
from mcp_conformance.assertions.oauth import assert_response_contains_keys
from mcp_conformance.assertions.wire import assert_header
from mcp_conformance.partners.base import AuthStep, FaultConfig, TestPartner
from mcp_conformance.scenario.models import (
    ScenarioDef,
    ScenarioResult,
    StepDef,
    StepResult,
    StepType,
)


class ExitCode(StrEnum):
    ALL_PASSED = "0"
    SOME_FAILED = "1"
    CONFIG_ERROR = "2"
    PARTNER_UNAVAILABLE = "3"


class ScenarioRunner:
    """Loads and executes scenarios against a test partner."""

    def __init__(self, partner: TestPartner) -> None:
        self._partner = partner

    async def run(self, scenario: ScenarioDef) -> ScenarioResult:
        """Execute a scenario against the configured partner."""
        step_results: list[StepResult] = []
        all_passed = True

        for i, step in enumerate(scenario.steps):
            result = await self._execute_step(i, step)
            step_results.append(result)
            if not result.passed:
                all_passed = False
                break

        passed_count = sum(1 for r in step_results if r.passed)
        return ScenarioResult(
            scenario_id=scenario.id,
            scenario_title=scenario.title,
            passed=all_passed,
            step_results=step_results,
            total_steps=len(scenario.steps),
            passed_steps=passed_count,
            failed_steps=len(step_results) - passed_count,
        )

    async def _execute_step(self, index: int, step: StepDef) -> StepResult:
        """Execute a single scenario step."""
        errors: list[str] = []
        trace_request: dict[str, Any] | None = None
        trace_response: dict[str, Any] | None = None

        if step.type == StepType.CLIENT_REQUEST:
            if step.action in ("partner.health",):
                healthy = await self._partner.health()
                if not healthy:
                    errors.append("Partner health check failed")

            elif step.action.startswith("oauth."):
                resp = await self._partner.send_auth_request(
                    AuthStep(
                        method=step.request.get("method", "POST") if step.request else "POST",
                        url=_action_to_url(step.action),
                        headers=step.request.get("headers", {}) if step.request else {},
                        body=step.request.get("json", step.request) if step.request else None,
                    )
                )
                trace_request = {"url": _action_to_url(step.action), "method": "POST"}
                trace_response = {
                    "status": resp.status,
                    "headers": dict(resp.headers),
                    "body": resp.body,
                }
                errors.extend(_evaluate_assertions(step.assert_, trace_response))

            elif step.action.startswith("test.") or step.action.startswith("mcp."):
                auth_config = step.auth if step.auth else None
                resp = await self._partner.send_mcp_request(
                    method=step.request.get("method", "") if step.request else "",
                    params=step.request.get("params", {}) if step.request else {},
                    auth=auth_config,
                )
                trace_request = {"method": step.request.get("method", "") if step.request else ""}
                trace_response = {
                    "status": resp.status,
                    "headers": dict(resp.headers),
                    "body": resp.body,
                }
                errors.extend(_evaluate_assertions(step.assert_, trace_response))

        elif step.type == StepType.LOG_DEBUG:
            if step.endpoint:
                state = await self._partner.get_debug_state(step.endpoint)
                trace_response = {"body": state}

        elif step.type == StepType.INJECT_FAULT:
            await self._partner.configure_injection(
                FaultConfig(
                    endpoint=step.params.get("endpoint", ""),
                    behavior=step.params.get("behavior", ""),
                    params=step.params.get("params", {}),
                )
            )

        elif step.type == StepType.WAIT:
            import asyncio

            await asyncio.sleep(step.seconds or 1)

        return StepResult(
            step_index=index,
            step_id=step.id,
            passed=len(errors) == 0,
            errors=errors,
            request=trace_request,
            response=trace_response,
        )


def _action_to_url(action: str) -> str:
    """Map scenario action names to endpoint paths."""
    mapping = {
        "oauth.dcr.register": "/register",
        "oauth.auth_code.authorize": "/authorize",
        "oauth.token.exchange": "/token",
        "oauth.discover": "/.well-known/oauth-authorization-server",
        "test.tokens.mint_expired": "/test/tokens/expired",
    }
    return mapping.get(action, f"/{action.replace('.', '/')}")


def _evaluate_assertions(assertions: list[Any], response: dict[str, Any]) -> list[str]:
    """Evaluate assertions against a response."""
    errors: list[str] = []
    for a in assertions:
        if a.type == "status":
            errors.extend(assert_status(response, a.expected))
        elif a.type == "jsonrpc_version":
            errors.extend(assert_jsonrpc_version(response))
        elif a.type == "result_exists":
            errors.extend(assert_result_exists(response))
        elif a.type == "response_contains_keys":
            errors.extend(assert_response_contains_keys(response, a.expected))
        elif a.type == "body_json_path":
            path = a.path or a.expected if isinstance(a.expected, str) else "$"
            errors.extend(assert_json_path(response, path, a.expected))
        elif a.type == "header":
            errors.extend(assert_header(response, a.name or "", a.matches))
    return errors
