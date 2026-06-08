"""Runner — orchestrates scenario steps against a test partner."""

from __future__ import annotations

import asyncio
from enum import IntEnum
from time import perf_counter
from typing import Any
from urllib.parse import urlencode

from mcp_conformance.assertions.http import assert_json_path, assert_status
from mcp_conformance.assertions.mcp import (
    assert_error_code,
    assert_error_message,
    assert_jsonrpc_version,
    assert_result_exists,
    assert_result_shape,
)
from mcp_conformance.assertions.oauth import (
    assert_response_contains_keys,
    assert_scope_contains,
    assert_token_type,
)
from mcp_conformance.assertions.wire import (
    assert_content_type,
    assert_header,
    assert_header_absent,
    assert_redirect_location_contains,
)
from mcp_conformance.partners.base import AuthStep, FaultConfig, TestPartner
from mcp_conformance.scenario.models import (
    ScenarioDef,
    ScenarioResult,
    StepDef,
    StepResult,
    StepType,
)
from mcp_conformance.wire.capture import WireTrace


class ExitCode(IntEnum):
    ALL_PASSED = 0
    SOME_FAILED = 1
    CONFIG_ERROR = 2
    PARTNER_UNAVAILABLE = 3


_ACTION_MAPPING = {
    "oauth.dcr.register": "/register",
    "oauth.auth_code.authorize": "/authorize",
    "oauth.token.exchange": "/token",
    "oauth.discover": "/.well-known/oauth-authorization-server",
    "partner.health": "/health",
    "mcp.request": "/mcp/oauth",
    "mcp.initialize": "/mcp/oauth",
    "mcp.bearer_request": "/mcp/bearer-token",
    "test.tokens.mint_expired": "/test/tokens/expired",
    "test.faults.configure": "/test/faults",
    "test.reset": "/test/reset",
    "test.state": "/test/state",
}


class ScenarioRunner:
    """Loads and executes scenarios against a test partner."""

    def __init__(self, partner: TestPartner) -> None:
        self._partner = partner
        self._step_results: dict[str, Any] = {}

    async def run(self, scenario: ScenarioDef) -> ScenarioResult:
        """Execute a scenario against the configured partner."""
        self._step_results = {}
        step_results: list[StepResult] = []
        all_passed = True

        for i, step in enumerate(scenario.steps):
            result = await self._execute_step(i, step)
            step_results.append(result)
            if step.id and result.response is not None:
                self._step_results[step.id] = result.response.get("body")
            if not result.passed:
                all_passed = False
                break

        passed_count = sum(1 for r in step_results if r.passed)
        failed_count = sum(1 for r in step_results if not r.passed)
        return ScenarioResult(
            scenario_id=scenario.id,
            scenario_title=scenario.title,
            passed=all_passed,
            step_results=step_results,
            total_steps=len(scenario.steps),
            passed_steps=passed_count,
            failed_steps=failed_count,
            skipped_steps=len(scenario.steps) - len(step_results),
            total_elapsed_ms=sum(result.elapsed_ms for result in step_results),
        )

    async def _execute_step(self, index: int, step: StepDef) -> StepResult:
        """Execute a single scenario step."""
        errors: list[str] = []
        trace = WireTrace()
        started = perf_counter()

        try:
            if step.type == StepType.CLIENT_REQUEST:
                trace = await self._execute_client_request(step)
                errors.extend(_evaluate_assertions(step.assert_, _trace_to_response_dict(trace)))
            elif step.type == StepType.LOG_DEBUG:
                endpoint = step.endpoint or _action_to_url(step.action)
                trace.request_method = "GET"
                trace.request_url = self._full_url(endpoint)
                trace.response_body = await self._partner.get_debug_state(endpoint)
                trace.response_status = 200
            elif step.type == StepType.INJECT_FAULT:
                payload = {
                    "endpoint": step.params.get("endpoint", ""),
                    "behavior": step.params.get("behavior", ""),
                    "params": step.params.get("params", {}),
                }
                trace.request_method = "POST"
                trace.request_url = self._full_url(_action_to_url("test.faults.configure"))
                trace.request_body = payload
                await self._partner.configure_injection(FaultConfig(**payload))
                trace.response_status = 200
                trace.response_body = {"configured": True}
            elif step.type == StepType.WAIT:
                await asyncio.sleep(step.seconds or 1)
            else:
                errors.append(f"Unsupported step type '{step.type}'")
        except Exception as exc:
            errors.append(f"Step execution error: {exc}")

        trace.elapsed_ms = (perf_counter() - started) * 1000

        return StepResult(
            step_index=index,
            step_id=step.id,
            passed=len(errors) == 0,
            errors=errors,
            request=_trace_to_request_dict(trace),
            response=_trace_to_response_dict(trace),
            wire_trace=trace,
            elapsed_ms=trace.elapsed_ms,
        )

    async def _execute_client_request(self, step: StepDef) -> WireTrace:
        trace = WireTrace()
        request = step.request or {}

        if step.action == "partner.health":
            trace.request_method = "GET"
            trace.request_url = self._full_url(_action_to_url(step.action))
            healthy = await self._partner.health()
            trace.response_status = 200 if healthy else 503
            trace.response_body = {"ok": healthy}
            return trace

        if step.action.startswith("oauth.") or step.action == "test.tokens.mint_expired":
            method = _default_http_method(step)
            params, body = _resolve_auth_request_payload(step)
            path = _build_url(_action_to_url(step.action), params)
            trace.request_method = method
            trace.request_url = self._full_url(path)
            trace.request_headers = dict(request.get("headers", {}))
            trace.request_body = body
            response = await self._partner.send_auth_request(
                AuthStep(
                    method=method,
                    url=path,
                    headers=trace.request_headers,
                    body=body,
                )
            )
            _populate_trace_from_response(trace, response)
            return trace

        if step.action == "test.reset":
            trace.request_method = "POST"
            trace.request_url = self._full_url(_action_to_url(step.action))
            await self._partner.reset_state()
            trace.response_status = 200
            trace.response_body = {"reset": True}
            return trace

        if step.action == "test.state":
            trace.request_method = "GET"
            trace.request_url = self._full_url(_action_to_url(step.action))
            trace.response_body = await self._partner.get_debug_state(_action_to_url(step.action))
            trace.response_status = 200
            return trace

        if step.action == "test.faults.configure":
            payload = _resolve_fault_payload(step)
            trace.request_method = request.get("method", "POST").upper()
            trace.request_url = self._full_url(_action_to_url(step.action))
            trace.request_body = payload
            await self._partner.configure_injection(FaultConfig(**payload))
            trace.response_status = 200
            trace.response_body = {"configured": True}
            return trace

        if step.action.startswith("mcp."):
            endpoint = _action_to_url(step.action) if step.action == "mcp.bearer_request" else None
            auth = self._resolve_step_auth(step.auth)
            trace.request_method = "POST"
            trace.request_url = (
                self._full_url(endpoint) if endpoint else self._default_mcp_url(step.action)
            )
            trace.request_headers = dict(request.get("headers", {}))
            if auth and "bearer_token" in auth:
                trace.request_headers["Authorization"] = f"Bearer {auth['bearer_token']}"
            trace.request_body = {
                "jsonrpc": "2.0",
                "method": request.get("method", ""),
                "params": request.get("params", {}),
                "id": 1,
            }
            response = await self._partner.send_mcp_request(
                method=request.get("method", ""),
                params=request.get("params", {}),
                auth=auth,
                headers=request.get("headers"),
                endpoint=endpoint,
            )
            _populate_trace_from_response(trace, response)
            return trace

        raise ValueError(f"Unsupported action '{step.action}'")

    def _resolve_step_auth(self, auth: dict[str, Any] | None) -> dict[str, Any] | None:
        if not auth:
            return auth

        bearer_token = auth.get("bearer_token")
        if bearer_token is None:
            return auth
        if isinstance(bearer_token, str):
            return auth
        if not isinstance(bearer_token, dict):
            raise ValueError("Unsupported bearer_token auth configuration")

        step_id = bearer_token.get("from_step")
        if not step_id:
            raise ValueError("bearer_token auth reference is missing 'from_step'")

        source = self._step_results.get(step_id)
        if source is None:
            raise ValueError(f"No stored step result found for '{step_id}'")

        path = bearer_token.get("path", "$.access_token")
        token = _extract_path_value(source, path)
        if not token:
            raise ValueError(f"No bearer token found at path '{path}' in step '{step_id}'")

        resolved_auth = dict(auth)
        resolved_auth["bearer_token"] = str(token)
        return resolved_auth

    def _default_mcp_url(self, action: str) -> str:
        path = _action_to_url(action)
        if path.startswith("/mcp/"):
            partner_name = type(self._partner).__name__
            if partner_name == "GenericMCPServerPartner":
                return getattr(self._partner, "base_url", path)
            return self._full_url(path)
        return self._full_url(path)

    def _full_url(self, path: str) -> str:
        if path.startswith(("http://", "https://")):
            return path
        base_url = getattr(self._partner, "base_url", "")
        if not base_url:
            return path
        return f"{base_url.rstrip('/')}{path}"


def _action_to_url(action: str) -> str:
    """Map scenario action names to endpoint paths."""
    return _ACTION_MAPPING.get(action, f"/{action.replace('.', '/')}")


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
        elif a.type == "result_shape":
            errors.extend(assert_result_shape(response, a.expected or []))
        elif a.type == "response_contains_keys":
            errors.extend(assert_response_contains_keys(response, a.expected))
        elif a.type == "body_json_path":
            path = a.path or (a.expected if isinstance(a.expected, str) else "$")
            errors.extend(assert_json_path(response, path, a.expected))
        elif a.type == "header":
            errors.extend(assert_header(response, a.name or "", a.matches))
        elif a.type == "header_absent":
            errors.extend(assert_header_absent(response, a.name or ""))
        elif a.type == "content_type":
            errors.extend(assert_content_type(response, str(a.expected or "")))
        elif a.type == "token_type":
            errors.extend(assert_token_type(response, str(a.expected or "Bearer")))
        elif a.type == "scope_contains":
            errors.extend(assert_scope_contains(response, str(a.expected or "")))
        elif a.type == "error_code":
            errors.extend(assert_error_code(response, int(a.expected)))
        elif a.type == "error_message":
            errors.extend(assert_error_message(response, str(a.expected or "")))
        elif a.type == "redirect_location_contains":
            errors.extend(assert_redirect_location_contains(response, str(a.expected or "")))
        else:
            errors.append(f"Unsupported assertion type '{a.type}'")
    return errors


def _build_url(path: str, params: dict[str, Any]) -> str:
    if not params:
        return path
    return f"{path}?{urlencode(params, doseq=True)}"


def _default_http_method(step: StepDef) -> str:
    request = step.request or {}
    if "method" in request:
        return str(request["method"]).upper()
    if step.action in {
        "oauth.discover",
        "oauth.auth_code.authorize",
        "partner.health",
        "test.state",
    }:
        return "GET"
    if "params" in request and "json" not in request and "body" not in request:
        return "GET"
    return "POST"


def _resolve_auth_request_payload(step: StepDef) -> tuple[dict[str, Any], Any]:
    request = step.request or {}
    if step.action == "oauth.auth_code.authorize":
        params = request.get("params")
        if params is None:
            params = request.get("json", request.get("body", {}))
        return dict(params or {}), None
    return dict(request.get("params", {})), request.get("json", request.get("body"))


def _resolve_fault_payload(step: StepDef) -> dict[str, Any]:
    request = step.request or {}
    request_body = request.get("json", request.get("body"))
    if isinstance(request_body, dict):
        payload = dict(request_body)
    else:
        payload = {
            "endpoint": request.get("endpoint", step.params.get("endpoint", "")),
            "behavior": request.get("behavior", step.params.get("behavior", "")),
            "params": request.get("params", step.params.get("params", {})),
        }

    payload.setdefault("endpoint", step.params.get("endpoint", ""))
    payload.setdefault("behavior", step.params.get("behavior", ""))
    payload.setdefault("params", step.params.get("params", {}))
    return payload


def _extract_path_value(data: Any, path: str) -> Any:
    if path == "$":
        return data
    if not path.startswith("$."):
        raise ValueError(f"Unsupported path '{path}'")

    current = data
    for key in path[2:].split("."):
        if not isinstance(current, dict):
            return None
        current = current.get(key)
        if current is None:
            return None
    return current


def _populate_trace_from_response(trace: WireTrace, response: Any) -> None:
    trace.response_status = response.status
    trace.response_headers = dict(response.headers)
    trace.response_body = response.body


def _trace_to_request_dict(trace: WireTrace) -> dict[str, Any] | None:
    if not any(
        [
            trace.request_method,
            trace.request_url,
            trace.request_headers,
            trace.request_body is not None,
        ]
    ):
        return None
    return {
        "method": trace.request_method,
        "url": trace.request_url,
        "headers": trace.request_headers,
        "body": trace.request_body,
    }


def _trace_to_response_dict(trace: WireTrace) -> dict[str, Any] | None:
    if trace.response_status == 0 and not trace.response_headers and trace.response_body is None:
        return None
    return {
        "status": trace.response_status,
        "headers": trace.response_headers,
        "body": trace.response_body,
    }
