"""Wire capture — records HTTP request/response traces."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class WireTrace:
    """Captured HTTP request/response trace for a single step."""

    request_method: str = ""
    request_url: str = ""
    request_headers: dict[str, str] = field(default_factory=dict)
    request_body: Any = None
    response_status: int = 0
    response_headers: dict[str, str] = field(default_factory=dict)
    response_body: Any = None
    elapsed_ms: float = 0.0
    redirect_chain: list[str] = field(default_factory=list)
