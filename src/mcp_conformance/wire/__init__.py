"""Wire capture and redaction package."""

from __future__ import annotations

from .capture import WireTrace
from .redact import redact_headers

__all__ = ["WireTrace", "redact_headers"]
