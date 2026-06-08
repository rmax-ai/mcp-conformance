"""Generic MCP server adapter — works against any MCP JSON-RPC endpoint."""

from __future__ import annotations

from typing import Any

import httpx

from mcp_conformance.partners.base import AuthStep, FaultConfig, MCPResponse, TestPartner


class GenericMCPServerPartner(TestPartner):
    """Adapter for any generic MCP server exposing JSON-RPC over HTTP."""

    def __init__(
        self,
        base_url: str = "http://127.0.0.1:8080",
        timeout: float = 10.0,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._client = httpx.AsyncClient(timeout=timeout)

    async def health(self) -> bool:
        try:
            r = await self._client.get(f"{self.base_url}/health", timeout=5)
            return r.status_code == 200
        except httpx.RequestError:
            return False

    async def send_mcp_request(
        self,
        method: str,
        params: dict[str, Any] | None = None,
        *,
        auth: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        endpoint: str | None = None,
    ) -> MCPResponse:
        body = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params or {},
            "id": 1,
        }
        req_headers = dict(headers or {})
        if auth and "bearer_token" in auth:
            req_headers["Authorization"] = f"Bearer {auth['bearer_token']}"
        url = self.base_url
        if endpoint:
            url = f"{self.base_url}{endpoint}" if endpoint.startswith("/") else endpoint
        r = await self._client.post(
            url,
            json=body,
            headers=req_headers,
        )
        return MCPResponse(
            status=r.status_code,
            headers=dict(r.headers),
            body=_decode_body(r),
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
            body=_decode_body(r),
        )

    async def reset_state(self) -> None:
        pass  # Generic server may not support state reset

    async def get_debug_state(self, endpoint: str) -> dict[str, Any]:
        return {}

    async def configure_injection(self, fault: FaultConfig) -> None:
        pass  # Generic server likely doesn't support fault injection

    async def close(self) -> None:
        await self._client.aclose()


def _decode_body(response: httpx.Response) -> dict[str, Any]:
    if not response.text:
        return {}
    try:
        return response.json()
    except ValueError:
        return {"raw": response.text}
