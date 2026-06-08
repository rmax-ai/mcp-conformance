"""Wire-level assertions for HTTP request/response capture."""

from __future__ import annotations

from typing import Any


def assert_header(response: dict[str, Any], name: str, matches: str | None = None) -> list[str]:
    """Assert a header exists and optionally matches a regex pattern."""
    headers = response.get("headers", {})
    actual = headers.get(name)
    if actual is None:
        return [f"Missing header '{name}'"]
    if matches and matches not in str(actual):
        return [f"Header '{name}' value '{actual}' does not match '{matches}'"]
    return []


def assert_header_absent(response: dict[str, Any], name: str) -> list[str]:
    """Assert a header must not be present."""
    headers = response.get("headers", {})
    if name in headers:
        return [f"Header '{name}' should be absent but was present"]
    return []


def assert_content_type(response: dict[str, Any], expected: str) -> list[str]:
    """Assert Content-Type header compatibility."""
    headers = response.get("headers", {})
    actual = headers.get("content-type", headers.get("Content-Type", ""))
    if expected not in str(actual):
        return [f"Expected Content-Type containing '{expected}', got '{actual}'"]
    return []


def assert_redirect_location_contains(response: dict[str, Any], substring: str) -> list[str]:
    """Assert redirect URL contains expected substring."""
    headers = response.get("headers", {})
    location = headers.get("location", headers.get("Location", ""))
    if substring not in str(location):
        return [f"Redirect location '{location}' does not contain '{substring}'"]
    return []
