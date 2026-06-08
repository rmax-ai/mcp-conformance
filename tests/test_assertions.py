"""Tests for HTTP and JSON-RPC assertion primitives."""

from mcp_conformance.assertions.http import assert_header_present, assert_status
from mcp_conformance.assertions.jsonrpc import (
    assert_error_code,
    assert_jsonrpc_version,
    assert_result_shape,
)


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
        response = {
            "status": 401,
            "headers": {"WWW-Authenticate": 'Bearer realm="mcp"'},
        }
        errors = assert_header_present(response, "WWW-Authenticate", "Bearer")
        assert errors == []


class TestJsonRpcAssertions:
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
        response = {
            "status": 200,
            "body": {"result": {"tools": [{"name": "test"}]}},
        }
        errors = assert_result_shape(response, ["tools"])
        assert errors == []

    def test_result_shape_missing_keys(self) -> None:
        response = {"status": 200, "body": {"result": {}}}
        errors = assert_result_shape(response, ["tools", "resources"])
        assert len(errors) == 1
        assert "tools" in errors[0]
