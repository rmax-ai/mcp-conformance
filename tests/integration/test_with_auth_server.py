"""Integration smoke test for the auth test server partner."""

from __future__ import annotations

from pathlib import Path

import httpx
import pytest

from mcp_conformance.partners.mcp_auth_test_server import AuthTestServerPartner
from mcp_conformance.runner import ScenarioRunner
from mcp_conformance.scenario.loader import load_scenario

AUTH_SERVER_URL = "http://127.0.0.1:8765"
SCENARIO_PATH = (
    Path(__file__).resolve().parents[2] / "scenarios" / "auth" / "auth-code-pkce-happy-path.yaml"
)


def _auth_server_available() -> bool:
    try:
        response = httpx.get(f"{AUTH_SERVER_URL}/health", timeout=1.0)
    except httpx.RequestError:
        return False
    return response.status_code == 200


pytestmark = pytest.mark.skipif(
    not _auth_server_available(),
    reason="mcp-auth-test-server is not running on http://127.0.0.1:8765",
)


@pytest.mark.asyncio
async def test_auth_server_smoke() -> None:
    partner = AuthTestServerPartner(base_url=AUTH_SERVER_URL)
    try:
        assert await partner.health()
        scenario = load_scenario(SCENARIO_PATH)
        result = await ScenarioRunner(partner).run(scenario)
    finally:
        await partner.close()

    assert result.scenario_id == scenario.id
    assert result.step_results
    assert result.passed
