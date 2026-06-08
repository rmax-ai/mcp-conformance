# Scenario Authoring Guide

Scenarios are declarative YAML files that define a sequence of test steps with assertions.

## Scenario Structure

```yaml
id: unique.scenario.id
title: "Human-readable title"
version: "0.1"
spec_refs:
  - rfc6749
  - rfc7636
capabilities:
  required:
    - oauth.auth_code_pkce
partner:
  type: mcp_auth_test_server
steps:
  - id: discover
    type: client_request
    action: oauth.discover
    assert:
      - type: status
        expected: 200
```

## Step Types

| Type | Description |
|---|---|
| `client_request` | HTTP request to the partner |
| `server_respond` | Model expected server behavior |
| `assert` | Evaluate assertions over captured data |
| `wait` | Sleep or poll (async behavior) |
| `inject_fault` | Configure partner fault injection |
| `log_debug` | Pull debug state into trace |

## Assertion Types

See `reports.md` for the full catalog.
