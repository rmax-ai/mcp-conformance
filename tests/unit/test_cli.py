"""Tests for CLI filtering and report comparison helpers."""

from __future__ import annotations

from pathlib import Path

from mcp_conformance.cli import (
    _filter_scenarios,
    _format_report_comparison,
    _normalize_capability,
    build_parser,
)
from mcp_conformance.scenario.models import ScenarioDef


def test_filter_scenarios_include_and_exclude() -> None:
    scenarios = [
        ScenarioDef(
            id="tools",
            title="Tools",
            capabilities={"required": ["mcp.tools"]},
            steps=[],
        ),
        ScenarioDef(
            id="oauth",
            title="OAuth",
            capabilities={"required": ["oauth.dcr", "oauth.auth_code_pkce"]},
            steps=[],
        ),
        ScenarioDef(
            id="resources",
            title="Resources",
            capabilities={"required": ["mcp.resources"]},
            steps=[],
        ),
    ]

    included = _filter_scenarios(scenarios, include=["oauth.dcr"], exclude=[])
    filtered = _filter_scenarios(scenarios, include=[], exclude=["mcp.tools"])

    assert [scenario.id for scenario in included] == ["oauth"]
    assert [scenario.id for scenario in filtered] == ["oauth", "resources"]


def test_normalize_capability_strips_prefix() -> None:
    assert _normalize_capability("capability:oauth.dcr") == "oauth.dcr"
    assert _normalize_capability("mcp.tools") == "mcp.tools"


def test_compare_format_reports_changed_and_missing_scenarios() -> None:
    output = _format_report_comparison(
        Path("a.json"),
        {"scenarios": [{"id": "one", "passed": True}, {"id": "two", "passed": False}]},
        Path("b.json"),
        {"scenarios": [{"id": "one", "passed": False}, {"id": "three", "passed": True}]},
    )

    assert "Scenario" in output
    assert "a.json" in output
    assert "b.json" in output
    assert "one" in output and "yes" in output
    assert "two" in output and "missing" in output
    assert "three" in output and "missing" in output


def test_build_parser_supports_compare_and_filters() -> None:
    parser = build_parser()

    args = parser.parse_args(
        [
            "run",
            "--include",
            "capability:oauth.dcr",
            "--exclude",
            "mcp.tools",
        ]
    )
    compare_args = parser.parse_args(["compare", "left.json", "right.json"])

    assert args.command == "run"
    assert args.include == ["capability:oauth.dcr"]
    assert args.exclude == ["mcp.tools"]
    assert compare_args.command == "compare"
    assert compare_args.files == [Path("left.json"), Path("right.json")]
