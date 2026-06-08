"""Reports package — output formatters."""

from __future__ import annotations

from .json_report import format_json
from .junit_report import format_junit
from .markdown_report import format_markdown

__all__ = ["format_json", "format_markdown", "format_junit"]
