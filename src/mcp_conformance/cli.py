"""CLI entry point for mcp-conformance."""

from __future__ import annotations

import argparse
import asyncio
import inspect
import json
import sys
from pathlib import Path
from typing import Any

from mcp_conformance.partners.mcp_auth_test_server import AuthTestServerPartner
from mcp_conformance.reports.json_report import format_json
from mcp_conformance.reports.markdown_report import format_markdown
from mcp_conformance.runner import ExitCode, ScenarioRunner
from mcp_conformance.scenario.models import ScenarioDef


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="mcp-conformance",
        description="Scenario-driven test runner for MCP implementations",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    run = sub.add_parser("run", help="Run one or more scenarios")
    run.add_argument(
        "paths",
        nargs="*",
        type=Path,
        help="Scenario YAML file(s) or directories. Defaults to ./scenarios",
    )
    run.add_argument(
        "--partner",
        default="mcp-auth-test-server",
        choices=["mcp-auth-test-server", "generic-mcp"],
        help="Partner adapter to use",
    )
    run.add_argument(
        "--base-url",
        default="http://127.0.0.1:8765",
        help="Base URL of the test partner",
    )
    run.add_argument(
        "--output",
        choices=["json", "markdown"],
        default="markdown",
        help="Report output format",
    )
    run.add_argument(
        "--include",
        action="append",
        default=[],
        metavar="capability:X",
        help="Only run scenarios that declare the given capability. May be repeated.",
    )
    run.add_argument(
        "--exclude",
        action="append",
        default=[],
        metavar="capability:X",
        help="Skip scenarios that declare the given capability. May be repeated.",
    )

    compare = sub.add_parser("compare", help="Compare two conformance report files")
    compare.add_argument("files", nargs=2, type=Path, help="Two JSON report files to compare")

    return parser


async def _run(args: argparse.Namespace) -> int:
    from mcp_conformance.scenario.loader import load_scenarios

    try:
        scenario_paths = _expand_scenario_paths(args.paths)
        scenarios = load_scenarios(scenario_paths)
        scenarios = _filter_scenarios_for_partner(scenarios, args.partner)
        scenarios = _filter_scenarios(
            scenarios,
            [_normalize_capability(cap) for cap in args.include],
            [_normalize_capability(cap) for cap in args.exclude],
        )
        if not scenarios:
            print(
                f"No scenarios matched partner '{args.partner}' and the selected filters.",
                file=sys.stderr,
            )
            return int(ExitCode.CONFIG_ERROR)
    except Exception as exc:
        print(f"Failed to load scenarios: {exc}", file=sys.stderr)
        return int(ExitCode.CONFIG_ERROR)

    partner = _build_partner(args)
    runner = ScenarioRunner(partner)

    try:
        healthy = await partner.health()
        if not healthy:
            print(
                f"Partner '{args.partner}' at {args.base_url} is unavailable. "
                "Verify the server is running and reachable.",
                file=sys.stderr,
            )
            return int(ExitCode.PARTNER_UNAVAILABLE)

        results = []
        for scenario in scenarios:
            result = await runner.run(scenario)
            results.append(result)

        if args.output == "json":
            print(format_json(results))
        else:
            print(format_markdown(results))

        if all(r.passed for r in results):
            return int(ExitCode.ALL_PASSED)
        return int(ExitCode.SOME_FAILED)
    finally:
        await _close_partner(partner)


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "run":
        exit_code = asyncio.run(_run(args))
    elif args.command == "compare":
        exit_code = _compare(args)
    else:
        parser.print_help()
        exit_code = int(ExitCode.CONFIG_ERROR)

    sys.exit(exit_code)


def _compare(args: argparse.Namespace) -> int:
    try:
        left_report = _load_report(args.files[0])
        right_report = _load_report(args.files[1])
    except Exception as exc:
        print(f"Failed to load report files: {exc}", file=sys.stderr)
        return int(ExitCode.CONFIG_ERROR)

    print(_format_report_comparison(args.files[0], left_report, args.files[1], right_report))
    return int(ExitCode.ALL_PASSED)


def _load_report(path: Path) -> dict[str, Any]:
    with path.open() as fh:
        return json.load(fh)


def _format_report_comparison(
    left_path: Path,
    left_report: dict[str, Any],
    right_path: Path,
    right_report: dict[str, Any],
) -> str:
    left_statuses = _scenario_statuses(left_report)
    right_statuses = _scenario_statuses(right_report)
    scenario_ids = sorted(set(left_statuses) | set(right_statuses))

    left_label = left_path.name
    right_label = right_path.name
    rows = [
        ["Scenario", left_label, right_label, "Changed"],
        ["-" * 8, "-" * len(left_label), "-" * len(right_label), "-" * 7],
    ]
    for scenario_id in scenario_ids:
        left_status = left_statuses.get(scenario_id, "missing")
        right_status = right_statuses.get(scenario_id, "missing")
        rows.append(
            [
                scenario_id,
                left_status,
                right_status,
                "yes" if left_status != right_status else "no",
            ]
        )

    widths = [max(len(row[index]) for row in rows) for index in range(len(rows[0]))]
    return "\n".join(
        "  ".join(value.ljust(widths[index]) for index, value in enumerate(row)) for row in rows
    )


def _scenario_statuses(report: dict[str, Any]) -> dict[str, str]:
    statuses: dict[str, str] = {}
    for scenario in report.get("scenarios", []):
        scenario_id = scenario.get("id")
        if not scenario_id:
            continue
        statuses[str(scenario_id)] = "passed" if scenario.get("passed") else "failed"
    return statuses


def _normalize_capability(value: str) -> str:
    if value.startswith("capability:"):
        return value.removeprefix("capability:")
    return value


def _filter_scenarios(
    scenarios: list[ScenarioDef],
    include: list[str],
    exclude: list[str],
) -> list[ScenarioDef]:
    result = scenarios
    if include:
        result = [
            scenario
            for scenario in result
            if any(cap in include for caps in scenario.capabilities.values() for cap in caps)
        ]
    if exclude:
        result = [
            scenario
            for scenario in result
            if not any(cap in exclude for caps in scenario.capabilities.values() for cap in caps)
        ]
    return result


def _filter_scenarios_for_partner(
    scenarios: list[ScenarioDef],
    partner_name: str,
) -> list[ScenarioDef]:
    return [scenario for scenario in scenarios if _scenario_matches_partner(scenario, partner_name)]


def _scenario_matches_partner(scenario: ScenarioDef, partner_name: str) -> bool:
    scenario_partner = str(scenario.partner.get("type", "")).strip()
    if not scenario_partner:
        return True
    return scenario_partner in _partner_aliases(partner_name)


def _partner_aliases(partner_name: str) -> set[str]:
    aliases = {
        "mcp-auth-test-server": {"mcp-auth-test-server", "mcp_auth_test_server"},
        "generic-mcp": {"generic-mcp", "generic-mcp-server", "generic_mcp_server"},
    }
    return aliases.get(partner_name, {partner_name})


def _build_partner(args: argparse.Namespace) -> object:
    if args.partner == "generic-mcp":
        from mcp_conformance.partners.generic_mcp import GenericMCPServerPartner

        return GenericMCPServerPartner(base_url=args.base_url)
    return AuthTestServerPartner(base_url=args.base_url)


def _expand_scenario_paths(paths: list[Path]) -> list[Path]:
    requested_paths = paths or [Path("scenarios")]
    discovered: list[Path] = []

    for path in requested_paths:
        if not path.exists():
            raise FileNotFoundError(f"Scenario path does not exist: {path}")
        if path.is_dir():
            matches = sorted(path.rglob("*.yaml"))
            if not matches:
                raise ValueError(f"No scenario files found in directory: {path}")
            discovered.extend(matches)
            continue
        if path.suffix != ".yaml":
            raise ValueError(
                f"Unsupported scenario path '{path}'; expected a .yaml file or directory"
            )
        discovered.append(path)

    return list(dict.fromkeys(discovered))


async def _close_partner(partner: object) -> None:
    close = getattr(partner, "close", None)
    if close is None:
        return
    result = close()
    if inspect.isawaitable(result):
        await result
