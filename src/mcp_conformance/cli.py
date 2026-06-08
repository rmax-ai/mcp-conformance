"""CLI entry point for mcp-conformance."""

from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

from mcp_conformance.partners.mcp_auth_test_server import AuthTestServerPartner
from mcp_conformance.reports.json_report import format_json
from mcp_conformance.reports.markdown_report import format_markdown
from mcp_conformance.runner import ScenarioRunner


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="mcp-conformance",
        description="Scenario-driven test runner for MCP implementations",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    run = sub.add_parser("run", help="Run one or more scenarios")
    run.add_argument("paths", nargs="+", type=Path, help="Scenario YAML file(s)")
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

    scenarios = load_scenarios(args.paths)

    partner_cls = AuthTestServerPartner
    partner = partner_cls(base_url=args.base_url)
    runner = ScenarioRunner(partner)

    healthy = await partner.health()
    if not healthy:
        print(f"Partner at {args.base_url} is unavailable", file=sys.stderr)
        return 3

    results = []
    for scenario in scenarios:
        result = await runner.run(scenario)
        results.append(result)

    if args.output == "json":
        print(format_json(results))
    else:
        print(format_markdown(results))

    if all(r.passed for r in results):
        return 0
    return 1


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "run":
        exit_code = asyncio.run(_run(args))
        sys.exit(exit_code)
    else:
        parser.print_help()
        sys.exit(2)
