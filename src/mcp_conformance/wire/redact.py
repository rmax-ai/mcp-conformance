"""Redaction utilities — deterministic secret masking for wire traces."""

from __future__ import annotations

import hashlib

REDACTED_HEADERS = frozenset(
    {
        "authorization",
        "cookie",
        "set-cookie",
        "x-api-key",
    }
)


def redact_headers(
    headers: dict[str, str],
    extra: set[str] | None = None,
) -> dict[str, str]:
    """Replace sensitive header values with SHA-256 fingerprints."""
    sensitive = REDACTED_HEADERS | (extra or set())
    result = {}
    for key, value in headers.items():
        if key.lower() in sensitive:
            fp = fingerprint(value)
            result[key] = f"[REDACTED {fp[:8]}]"
        else:
            result[key] = value
    return result


def fingerprint(value: str) -> str:
    """SHA-256 hash of a value for correlation without revealing the secret."""
    return hashlib.sha256(value.encode("utf-8")).hexdigest()
