"""JSON-RPC assertion primitives: version, result shape, error codes."""

from __future__ import annotations

from typing import Any


def assert_jsonrpc_version(response: dict[str, Any]) -> list[str]:
    """Assert the response has jsonrpc: \"2.0\"."""
    body = response.get("body", {})
    version = body.get("jsonrpc")
    if version != "2.0":
        return [f"Expected jsonrpc '2.0', got '{version}'"]
    return []


def assert_error_code(response: dict[str, Any], expected: int) -> list[str]:
    """Assert JSON-RPC error code matches."""
    error = response.get("body", {}).get("error", {})
    code = error.get("code")
    if code != expected:
        return [f"Expected error code {expected}, got {code}"]
    return []


def assert_error_message(response: dict[str, Any], expected: str) -> list[str]:
    """Assert JSON-RPC error message matches."""
    error = response.get("body", {}).get("error", {})
    msg = error.get("message", "")
    if expected not in str(msg):
        return [f"Expected error message containing '{expected}', got '{msg}'"]
    return []


def assert_result_shape(response: dict[str, Any], expected_keys: list[str]) -> list[str]:
    """Assert the result object contains expected keys."""
    result = response.get("body", {}).get("result", {})
    missing = [k for k in expected_keys if k not in result]
    if missing:
        return [f"Result missing expected keys: {missing}"]
    return []
