# Reports Guide

## Output Formats

- **JSON** — canonical machine-readable format with scenario IDs, step traces, timing
- **Markdown** — human-readable console summary
- **JUnit XML** — CI-friendly format (GitHub Actions, Jenkins)

## Assertion Catalog

### HTTP Layer
- `status` — exact or list match
- `header` — header exists with optional regex
- `header_absent` — header must not exist
- `content_type` — Content-Type compatibility check
- `body_json_path` — JSON path check
- `redirect_location_contains` — redirect URL substring

### JSON-RPC Layer
- `jsonrpc_version` — envelope contains "2.0"
- `result_exists` — successful result response
- `result_shape` — JSON Schema validation
- `error_code` — exact error code match
- `error_message` — error message substring match

### OAuth Layer
- `token_type` — token response declares bearer
- `response_contains_keys` — required fields present
- `scope_contains` — scope string contains expected
- `oauth_error` — error exact match

