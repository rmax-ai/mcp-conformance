# Partner Adapter Guide

Partner adapters translate generic scenario operations into the concrete API of the system under test.

## Built-in Adapters

- `mcp-auth-test-server` — connects to mcp-auth-test-server (OAuth, DCR, CIMD, debug endpoints)
- `generic-mcp-server` — connects to any MCP server with basic JSON-RPC over HTTP

## Writing Custom Adapters

Implement the `TestPartner` ABC from `mcp_conformance.partners.base`.
