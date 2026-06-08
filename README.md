# MCP Conformance

Scenario-driven test runner for evaluating MCP (Model Context Protocol) client and server implementations.

## What is this?

MCP Conformance is a declarative test framework that verifies MCP implementations against the protocol specification. It runs scenarios — sequences of HTTP and JSON-RPC interactions with assertions at each step — against configurable test partners (servers, gateways, or client runtimes).

Designed for:

- **MCP client developers** — verify your client handles every OAuth error path
- **MCP server developers** — confirm tools/list responses match JSON-RPC schema
- **Gateway/platform operators** — certify servers before onboarding
- **Enterprise compliance teams** — produce audit-grade pass/fail reports
- **Open-source evaluators** — compare implementations side-by-side

## Quickstart

```bash
uv sync --dev
uv run pytest tests/ -v
```

## Architecture

```
scenarios/ (YAML)  →  Scenario Runner  →  Partner Adapter  →  Test Server
                               ↓
                      Assertion Library
                               ↓
                         JSON Report
```

- **Scenarios** — declarative YAML describing test sequences
- **Runner** — loads scenarios, iterates steps, delegates to partner, collects results
- **Partner Adapter** — abstraction over the system under test (default: mcp-auth-test-server)
- **Assertion Library** — HTTP status, headers, JSON body, JSON-RPC schema, OAuth specifics
- **Reporter** — JSON and human-readable pass/fail output

## Project Structure

```
mcp-conformance/
├── src/mcp_conformance/
│   ├── runner.py              # Scenario orchestrator
│   ├── scenario.py            # Scenario models
│   ├── assertions/            # HTTP + JSON-RPC assertion primitives
│   ├── partners/              # Partner adapters (auth test server, etc.)
│   └── report.py              # Result formatters
├── scenarios/                 # YAML scenario definitions
│   ├── auth/                  # OAuth, DCR, CIMD scenarios
│   ├── no-auth/               # No-auth MCP scenarios
│   ├── bearer/                # Bearer token auth MCP scenarios
│   ├── protocol/              # tools/list, tools/call, resources scenarios
│   └── errors/                # Error and edge-case scenarios
├── tests/                     # Test suite
├── fixtures/                  # Test fixtures (certs, JWKs)
└── docs/                      # Documentation
```

## License

MIT
