"""Assertion primitives for evaluating HTTP and JSON-RPC responses."""

from __future__ import annotations

from .http import (
    assert_header_present,
    assert_json_path,
    assert_status,
)
from .mcp import (
    assert_error_code,
    assert_error_message,
    assert_jsonrpc_version,
    assert_result_exists,
    assert_result_shape,
)
from .oauth import (
    assert_oauth_error,
    assert_response_contains_keys,
    assert_scope_contains,
    assert_token_type,
)
from .wire import (
    assert_content_type,
    assert_header,
    assert_header_absent,
    assert_redirect_location_contains,
)

__all__ = [
    "assert_status",
    "assert_header_present",
    "assert_json_path",
    "assert_jsonrpc_version",
    "assert_error_code",
    "assert_error_message",
    "assert_result_exists",
    "assert_result_shape",
    "assert_token_type",
    "assert_response_contains_keys",
    "assert_scope_contains",
    "assert_oauth_error",
    "assert_header",
    "assert_header_absent",
    "assert_content_type",
    "assert_redirect_location_contains",
]
