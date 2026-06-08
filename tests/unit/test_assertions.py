"""Tests for HTTP, JSON-RPC, OAuth, and wire assertion primitives."""

from mcp_conformance.assertions.http import assert_header_present, assert_json_path, assert_status
from mcp_conformance.assertions.mcp import (
    assert_error_code,
    assert_jsonrpc_version,
    assert_result_exists,
    assert_result_shape,
)
from mcp_conformance.assertions.oauth import (
    assert_response_contains_keys,
    assert_scope_contains,
    assert_token_type,
)
from mcp_conformance.assertions.wire import assert_content_type, assert_header, assert_header_absent


class TestHttpAssertions:
    def test_status_exact_match(self) -> None:
        response = {"status": 200, "headers": {}, "body": {}}
        errors = assert_status(response, 200)
        assert errors == []

    def test_status_mismatch(self) -> None:
        response = {"status": 404, "headers": {}, "body": {}}
        errors = assert_status(response, 200)
        assert len(errors) == 1
        assert "200" in errors[0]

    def test_status_any_of(self) -> None:
        response = {"status": 201, "headers": {}, "body": {}}
        errors = assert_status(response, [200, 201])
        assert errors == []

    def test_header_present(self) -> None:
        response = {"status": 200, "headers": {"Content-Type": "application/json"}}
        errors = assert_header_present(response, "Content-Type")
        assert errors == []

    def test_header_missing(self) -> None:
        response = {"status": 200, "headers": {}}
        errors = assert_header_present(response, "WWW-Authenticate")
        assert len(errors) == 1

    def test_header_with_pattern(self) -> None:
        response = {"status": 401, "headers": {"WWW-Authenticate": 'Bearer realm="mcp"'}}
        errors = assert_header_present(response, "WWW-Authenticate", "Bearer")
        assert errors == []

    def test_json_path_exists(self) -> None:
        response = {"status": 200, "body": {"error": "invalid_request"}}
        errors = assert_json_path(response, "$.error")
        assert errors == []


class TestMcpAssertions:
    def test_version_match(self) -> None:
        response = {"status": 200, "body": {"jsonrpc": "2.0"}}
        errors = assert_jsonrpc_version(response)
        assert errors == []

    def test_version_mismatch(self) -> None:
        response = {"status": 200, "body": {"jsonrpc": "1.0"}}
        errors = assert_jsonrpc_version(response)
        assert len(errors) == 1

    def test_error_code_match(self) -> None:
        response = {"status": 200, "body": {"error": {"code": -32601}}}
        errors = assert_error_code(response, -32601)
        assert errors == []

    def test_error_code_mismatch(self) -> None:
        response = {"status": 200, "body": {"error": {"code": -32602}}}
        errors = assert_error_code(response, -32601)
        assert len(errors) == 1

    def test_result_shape(self) -> None:
        response = {"status": 200, "body": {"result": {"tools": [{"name": "test"}]}}}
        errors = assert_result_shape(response, ["tools"])
        assert errors == []

    def test_result_exists(self) -> None:
        response = {"status": 200, "body": {"result": {"tools": []}}}
        errors = assert_result_exists(response)
        assert errors == []

    def test_result_and_error_mutual_exclusion(self) -> None:
        response = {"status": 200, "body": {"result": {}, "error": {"code": -32601}}}
        errors = assert_result_exists(response)
        assert len(errors) == 1


class TestOAuthAssertions:
    def test_token_type(self) -> None:
        response = {"body": {"token_type": "Bearer", "access_token": "abc"}}
        errors = assert_token_type(response, "Bearer")
        assert errors == []

    def test_response_contains_keys(self) -> None:
        response = {"body": {"access_token": "abc", "token_type": "Bearer", "expires_in": 3600}}
        errors = assert_response_contains_keys(response, ["access_token", "token_type"])
        assert errors == []

    def test_scope_contains(self) -> None:
        response = {"body": {"scope": "mcp:tools:list mcp:tools:read"}}
        errors = assert_scope_contains(response, "mcp:tools:list")
        assert errors == []

    def test_scope_missing(self) -> None:
        response = {"body": {"scope": "openid profile"}}
        errors = assert_scope_contains(response, "mcp:tools")
        assert len(errors) == 1


class TestWireAssertions:
    def test_header_check(self) -> None:
        response = {"status": 401, "headers": {"WWW-Authenticate": 'Bearer realm="mcp"'}}
        errors = assert_header(response, "WWW-Authenticate", "Bearer")
        assert errors == []

    def test_header_absent(self) -> None:
        response = {"status": 200, "headers": {"Content-Type": "application/json"}}
        errors = assert_header_absent(response, "Set-Cookie")
        assert errors == []

    def test_content_type(self) -> None:
        response = {"status": 200, "headers": {"Content-Type": "application/json"}}
        errors = assert_content_type(response, "json")
        assert errors == []
