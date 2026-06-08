# Developer Guide for AI Coding Assistants

## Project Overview

MCP Conformance is a scenario-driven test runner for evaluating MCP (Model Context Protocol) client and server implementations. It loads declarative YAML scenarios, executes them against configurable test partners, and produces pass/fail reports.

## Architecture

```text
mcp-conformance/
├── src/mcp_conformance/
│   ├── __init__.py          # Package root
│   ├── runner.py            # ScenarioRunner — orchestrates steps, delegates to partner
│   ├── scenario.py          # Scenario models (Scenario, ScenarioStep, ScenarioResult, etc.)
│   ├── report.py            # Result formatters (human-readable + JSON)
│   ├── assertions/
│   │   ├── __init__.py      # Re-exports assertion functions
│   │   ├── http.py          # assert_status, assert_header_present, assert_json_path
│   │   └── jsonrpc.py       # assert_jsonrpc_version, assert_error_code, assert_result_shape
│   └── partners/
│       ├── __init__.py      # Re-exports base interfaces
│       ├── base.py          # TestPartner ABC, AuthStep, FaultConfig, MCPResponse
│       └── auth_test_server.py  # AuthTestServerPartner — httpx-based adapter
├── tests/
│   ├── conftest.py          # Shared fixtures
│   ├── test_scenario_parser.py  # Scenario model tests
│   └── test_assertions.py   # Assertion primitive tests
├── scenarios/               # YAML scenario definitions
│   ├── auth/                # OAuth, DCR, CIMD scenarios
│   ├── protocol/            # JSON-RPC shape scenarios
│   └── errors/              # Error/edge case scenarios
├── fixtures/                # Test collateral (certs, JWKs)
└── docs/                    # Documentation
```

## Design Principles

1. **Scenarios are declarative, not imperative** — users describe what to assert, not how to test.
2. **Always surface the raw wire** — every scenario step logs the actual HTTP request/response and JSON-RPC messages.
3. **Test partners are swappable** — the auth test server is the default partner, but scenarios work against any conformant implementation.
4. **Fail fast on step failure** — a scenario stops at the first failed assertion.

## Key Dependencies

- httpx — async HTTP client for partner interactions
- pydantic — data validation
- pyyaml — YAML scenario parsing
- jsonpath-ng — JSON path assertions
- pytest — test runner
- ruff — linter + formatter

## Environment Setup

```bash
uv sync --dev
```

## Running Tests

```bash
uv run pytest tests/ -v                    # all tests
uv run pytest tests/test_assertions.py -v  # assertion primitives
uv run pytest tests/test_scenario_parser.py -v  # scenario model tests
```

## Commands

```bash
uv run pytest tests/ -v            # run all tests
uv run ruff check src/ tests/      # ruff check
uv run ruff format src/ tests/     # ruff format
```

## Running Against a Test Partner

```bash
# Start the mcp-auth-test-server first:
cd ../mcp-auth-test-server && uv run uvicorn mcp_auth_test_server.app:app --port 8765

# Then run scenarios:
uv run python -c "
import asyncio
from mcp_conformance.partners.auth_test_server import AuthTestServerPartner
from mcp_conformance.runner import ScenarioRunner

async def main():
    partner = AuthTestServerPartner()
    runner = ScenarioRunner(partner)
    print(await partner.health())

asyncio.run(main())
"
```
