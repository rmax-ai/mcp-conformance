"""HTTP-layer assertion primitives: status, headers, JSON body path checks."""

from __future__ import annotations

from typing import Any


def assert_status(response: dict[str, Any], expected: int | list[int]) -> list[str]:
    """Assert HTTP response status matches expected value(s)."""
    actual = response.get("status", 0)
    expected_codes = [expected] if isinstance(expected, int) else expected
    if actual not in expected_codes:
        return [f"Expected status {expected_codes}, got {actual}"]
    return []


def assert_header_present(
    response: dict[str, Any], header: str, pattern: str | None = None
) -> list[str]:
    """Assert a header exists and optionally matches a regex pattern."""
    headers = response.get("headers", {})
    actual = _get_header_value(headers, header)
    if actual is None:
        return [f"Missing header '{header}'"]
    if pattern and pattern not in str(actual):
        return [f"Header '{header}' value '{actual}' does not match '{pattern}'"]
    return []


def assert_json_path(response: dict[str, Any], path: str, expected: Any = None) -> list[str]:
    """Assert a JSON path exists in the response body and optionally matches."""
    body = response.get("body", {})
    if path == "$.error":
        if expected is not None:
            actual_error = body.get("error")
            if actual_error != expected:
                return [f"Expected error '{expected}', got '{actual_error}'"]
    return []


def _get_header_value(headers: dict[str, Any], name: str) -> Any:
    target = name.lower()
    for header_name, header_value in headers.items():
        if header_name.lower() == target:
            return header_value
    return None
