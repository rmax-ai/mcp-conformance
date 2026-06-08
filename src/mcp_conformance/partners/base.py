"""Partner adapter interface — abstract base for test infrastructure adapters."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class AuthStep:
    """Parameters for an OAuth/HTTP interaction step."""

    method: str = "GET"
    url: str = ""
    headers: dict[str, str] = field(default_factory=dict)
    body: dict[str, Any] | None = None


@dataclass
class MCPResponse:
    """Response from an MCP request."""

    status: int
    headers: dict[str, str]
    body: dict[str, Any]


@dataclass
class FaultConfig:
    """Configuration for fault injection on the test partner."""

    endpoint: str = ""
    behavior: str = ""  # e.g. "delay", "error", "timeout"
    params: dict[str, Any] = field(default_factory=dict)


class TestPartner(ABC):
    """Abstract interface for a test partner (the system under test + infra)."""

    @abstractmethod
    async def health(self) -> bool:
        """Check if the partner is reachable and operational."""
        ...

    @abstractmethod
    async def send_mcp_request(
        self,
        method: str,
        params: dict[str, Any] | None = None,
        *,
        auth: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> MCPResponse:
        """Send an MCP JSON-RPC request to the partner."""
        ...

    @abstractmethod
    async def send_auth_request(self, step: AuthStep) -> MCPResponse:
        """Send an HTTP request to the partner's auth endpoints."""
        ...

    @abstractmethod
    async def reset_state(self) -> None:
        """Reset partner state for a clean test run."""
        ...

    @abstractmethod
    async def get_debug_state(self, endpoint: str) -> dict[str, Any]:
        """Retrieve debug state from the partner."""
        ...

    @abstractmethod
    async def configure_injection(self, fault: FaultConfig) -> None:
        """Configure fault injection for subsequent requests."""
        ...
