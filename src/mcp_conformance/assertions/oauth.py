"""OAuth-specific assertion primitives."""

from __future__ import annotations

from typing import Any


def assert_token_type(response: dict[str, Any], expected: str = "Bearer") -> list[str]:
    """Assert token response declares expected token type."""
    body = response.get("body", {})
    actual = body.get("token_type")
    if actual != expected:
        return [f"Expected token_type '{expected}', got '{actual}'"]
    return []


def assert_response_contains_keys(response: dict[str, Any], keys: list[str]) -> list[str]:
    """Assert response body contains all expected keys."""
    body = response.get("body", {})
    missing = [k for k in keys if k not in body]
    if missing:
        return [f"Response missing expected keys: {missing}"]
    return []


def assert_scope_contains(response: dict[str, Any], expected: str) -> list[str]:
    """Assert scope string contains expected scope value."""
    body = response.get("body", {})
    scope = body.get("scope", "")
    if expected not in str(scope):
        return [f"Scope '{scope}' does not contain '{expected}'"]
    return []


def assert_oauth_error(response: dict[str, Any], expected: str) -> list[str]:
    """Assert OAuth error field matches expected."""
    body = response.get("body", {})
    error = body.get("error", "")
    if error != expected:
        return [f"Expected OAuth error '{expected}', got '{error}'"]
    return []
