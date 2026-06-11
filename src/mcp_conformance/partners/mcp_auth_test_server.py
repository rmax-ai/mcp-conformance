"""Partner adapter for the mcp-auth-test-server."""

from __future__ import annotations

import json
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

import httpx

from .base import AuthStep, FaultConfig, MCPResponse, TestPartner


class AuthTestServerPartner(TestPartner):
    """Adapter for the mcp-auth-test-server (FastAPI-based OAuth test server)."""

    def __init__(self, base_url: str = "http://127.0.0.1:8765", timeout: float = 10.0) -> None:
        self.base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._client = httpx.AsyncClient(timeout=timeout)
        self._cimd_fixture_server = _CimdFixtureServer()

    async def health(self) -> bool:
        try:
            r = await self._client.get(f"{self.base_url}/health")
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
        r = await self._client.post(
            f"{self.base_url}{endpoint or '/mcp/oauth'}",
            json=body,
            headers=req_headers or None,
        )
        return MCPResponse(
            status=r.status_code,
            headers=dict(r.headers),
            body=_decode_body(r),
        )

    async def send_auth_request(self, step: AuthStep) -> MCPResponse:
        request_url = f"{self.base_url}{self._rewrite_cimd_fixture_url(step.url)}"
        request_kwargs: dict[str, Any] = {
            "method": step.method,
            "url": request_url,
            "headers": step.headers,
        }
        content_type = _header_value(step.headers, "content-type")
        if step.body is not None:
            if content_type and "application/x-www-form-urlencoded" in content_type:
                request_kwargs["data"] = step.body
            else:
                request_kwargs["json"] = step.body
        r = await self._client.request(
            **request_kwargs,
        )
        return MCPResponse(
            status=r.status_code,
            headers=dict(r.headers),
            body=_decode_body(r),
        )

    async def reset_state(self) -> None:
        await self._client.post(f"{self.base_url}/test/reset")

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
        self._cimd_fixture_server.close()

    def _rewrite_cimd_fixture_url(self, url: str) -> str:
        parsed = urlparse(url)
        if parsed.path != "/oauth/authorize":
            return url

        query = parse_qs(parsed.query, keep_blank_values=True)
        client_id = query.get("client_id", [None])[0]
        redirect_uri = query.get("redirect_uri", [None])[0]
        if not isinstance(client_id, str) or not isinstance(redirect_uri, str):
            return url

        fixture_prefix = f"{self.base_url}/test/cimd/"
        if not client_id.startswith(fixture_prefix):
            return url

        fixture_name = client_id.removeprefix(fixture_prefix)
        if fixture_name not in {"valid.json", "mismatched.json"}:
            return url

        query["client_id"] = [self._cimd_fixture_server.fixture_url(fixture_name, redirect_uri)]
        return urlunparse(parsed._replace(query=urlencode(query, doseq=True)))


def _decode_body(response: httpx.Response) -> dict[str, Any]:
    if not response.text:
        return {}
    try:
        return response.json()
    except ValueError:
        return {"raw": response.text}


def _header_value(headers: dict[str, str], name: str) -> str | None:
    target = name.lower()
    for header_name, header_value in headers.items():
        if header_name.lower() == target:
            return header_value
    return None


class _CimdFixtureServer:
    def __init__(self) -> None:
        self._fixture_redirects: dict[str, str] = {}
        self._server = ThreadingHTTPServer(("127.0.0.1", 0), self._build_handler())
        self._thread = threading.Thread(target=self._server.serve_forever, daemon=True)
        self._thread.start()

    def fixture_url(self, fixture_name: str, redirect_uri: str) -> str:
        self._fixture_redirects[fixture_name] = redirect_uri
        return f"http://127.0.0.1:{self._server.server_port}/test/cimd/{fixture_name}"

    def close(self) -> None:
        self._server.shutdown()
        self._server.server_close()
        self._thread.join(timeout=1)

    def _build_handler(self) -> type[BaseHTTPRequestHandler]:
        fixture_redirects = self._fixture_redirects

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self) -> None:  # noqa: N802
                parsed = urlparse(self.path)
                if not parsed.path.startswith("/test/cimd/"):
                    self.send_response(404)
                    self.end_headers()
                    return

                fixture_name = parsed.path.removeprefix("/test/cimd/")
                redirect_uri = fixture_redirects.get(fixture_name, "http://127.0.0.1:9876/callback")
                document_url = f"http://127.0.0.1:{self.server.server_port}{parsed.path}"

                if fixture_name == "slow.json":
                    time.sleep(5)
                    payload = _build_valid_cimd_document(document_url, redirect_uri)
                elif fixture_name == "valid.json":
                    payload = _build_valid_cimd_document(document_url, redirect_uri)
                elif fixture_name == "mismatched.json":
                    payload = _build_valid_cimd_document(document_url, redirect_uri)
                    payload["client_id"] = document_url.replace("mismatched.json", "valid.json")
                else:
                    self.send_response(404)
                    self.end_headers()
                    return

                body = json.dumps(payload).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def log_message(self, format: str, *args: object) -> None:  # noqa: A003
                return

        return Handler


def _build_valid_cimd_document(document_url: str, redirect_uri: str) -> dict[str, object]:
    return {
        "client_id": document_url,
        "client_name": "mcp-conformance CIMD client",
        "redirect_uris": [redirect_uri],
        "grant_types": ["authorization_code"],
        "response_types": ["code"],
        "token_endpoint_auth_method": "none",
        "scope": "mcp:read",
    }
