"""JUnit XML report — CI-friendly output."""

from __future__ import annotations

from mcp_conformance.scenario.models import ScenarioResult


def format_junit(results: list[ScenarioResult]) -> str:
    """Format scenario results as JUnit XML for CI integration."""
    lines = ['<?xml version="1.0" encoding="UTF-8"?>']
    errors = sum(1 for r in results if not r.passed)
    tests = len(results)
    lines.append(
        f'<testsuite name="mcp-conformance" tests="{tests}" errors="{errors}" '
        f'failures="{errors}" skipped="0">'
    )
    for result in results:
        lines.append(
            f'  <testcase classname="{result.scenario_id}" '
            f'name="{result.scenario_title}" '
            f'time="{result.total_elapsed_ms / 1000:.3f}">'
        )
        if not result.passed:
            failures = []
            for sr in result.step_results:
                failures.extend(sr.errors)
            msg = "; ".join(failures) if failures else "Scenario failed"
            lines.append(f'    <failure message="{msg}" type="AssertionError"/>')
        lines.append("  </testcase>")
    lines.append("</testsuite>")
    return "\n".join(lines)
