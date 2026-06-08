"""CLI entry point for mcp-conformance."""

from __future__ import annotations

import argparse
import asyncio
import inspect
import sys
from pathlib import Path

from mcp_conformance.partners.mcp_auth_test_server import AuthTestServerPartner
from mcp_conformance.reports.json_report import format_json
from mcp_conformance.reports.markdown_report import format_markdown
from mcp_conformance.runner import ExitCode, ScenarioRunner


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

    return parser


async def _run(args: argparse.Namespace) -> int:
    from mcp_conformance.scenario.loader import load_scenarios

    try:
        scenario_paths = _expand_scenario_paths(args.paths)
        scenarios = load_scenarios(scenario_paths)
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
        sys.exit(exit_code)
    else:
        parser.print_help()
        sys.exit(int(ExitCode.CONFIG_ERROR))


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
