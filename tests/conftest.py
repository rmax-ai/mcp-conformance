"""Test configuration and shared fixtures."""

from __future__ import annotations

import pytest
import pytest_asyncio

from mcp_conformance.scenario import (
    Assertion,
    Scenario,
    ScenarioStep,
    StepType,
)


@pytest_asyncio.fixture
async def scenario_parser() -> None:
    """Fixture for testing scenario parsing."""
    pass


@pytest.fixture
def happy_path_scenario() -> Scenario:
    """A minimal happy-path scenario for testing."""
    return Scenario(
        name="auth-code-happy-path",
        description="Discover → DCR register → authorize → consent → token exchange → MCP call",
        steps=[
            ScenarioStep(
                step_type=StepType.CLIENT_REQUEST,
                params={"method": "GET", "url": "/.well-known/oauth-authorization-server"},
                assertions=[Assertion(type="status", expected=200)],
            ),
            ScenarioStep(
                step_type=StepType.CLIENT_REQUEST,
                params={
                    "method": "POST",
                    "url": "/register",
                    "body": {
                        "redirect_uris": ["http://127.0.0.1:9999/callback"],
                        "grant_types": ["authorization_code"],
                        "token_endpoint_auth_method": "none",
                    },
                },
                assertions=[
                    Assertion(type="status", expected=201),
                    Assertion(type="body_json_path", expected="client_id"),
                ],
            ),
        ],
    )
