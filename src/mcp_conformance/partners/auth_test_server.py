"""Partner adapter for the mcp-auth-test-server."""

from __future__ import annotations

from typing import Any

import httpx

from .base import AuthStep, FaultConfig, MCPResponse, TestPartner


class AuthTestServerPartner(TestPartner):
    """Adapter for the mcp-auth-test-server (FastAPI-based OAuth test server)."""

    def __init__(self, base_url: str = "http://127.0.0.1:8765", timeout: float = 10.0) -> None:
        self.base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._client = httpx.AsyncClient(timeout=timeout)

    async def health(self) -> bool:
        try:
            r = await self._client.get(f"{self.base_url}/health")
            return r.status_code == 200
        except httpx.RequestError:
            return False

    async def send_mcp_request(self, method: str, params: dict[str, Any]) -> MCPResponse:
        body = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
            "id": 1,
        }
        r = await self._client.post(
            f"{self.base_url}/mcp/oauth",
            json=body,
        )
        return MCPResponse(
            status=r.status_code,
            headers=dict(r.headers),
            body=r.json() if r.text else {},
        )

    async def send_auth_request(self, step: AuthStep) -> MCPResponse:
        r = await self._client.request(
            method=step.method,
            url=f"{self.base_url}{step.url}",
            headers=step.headers,
            json=step.body,
        )
        return MCPResponse(
            status=r.status_code,
            headers=dict(r.headers),
            body=r.json() if r.text else {},
        )

    async def reset_state(self) -> None:
        await self._client.post(f"{self.base_url}/debug/reset")

    async def get_debug_state(self, endpoint: str) -> dict[str, Any]:
        r = await self._client.get(f"{self.base_url}{endpoint}")
        return r.json() if r.text else {}

    async def configure_injection(self, fault: FaultConfig) -> None:
        await self._client.post(
            f"{self.base_url}/test/faults",
            json={
                "endpoint": fault.endpoint,
                "behavior": fault.behavior,
                "params": fault.params,
            },
        )

    async def close(self) -> None:
        await self._client.aclose()
