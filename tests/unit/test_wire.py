"""Tests for wire capture and redaction utilities."""

from mcp_conformance.wire.redact import fingerprint, redact_headers


class TestRedaction:
    def test_redact_authorization(self) -> None:
        headers = {"Authorization": "Bearer secret-token-123", "Content-Type": "application/json"}
        result = redact_headers(headers)
        assert result["Authorization"].startswith("[REDACTED")
        assert not result["Authorization"].startswith("Bearer")
        assert result["Content-Type"] == "application/json"

    def test_fingerprint_deterministic(self) -> None:
        fp1 = fingerprint("secret-value")
        fp2 = fingerprint("secret-value")
        assert fp1 == fp2
        assert len(fp1) == 64  # SHA-256 hex

    def test_redact_cookie(self) -> None:
        headers = {"Cookie": "session=abc123"}
        result = redact_headers(headers)
        assert result["Cookie"].startswith("[REDACTED")
