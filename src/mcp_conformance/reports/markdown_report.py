"""Markdown report — human-readable console output."""

from __future__ import annotations

from datetime import UTC, datetime

from mcp_conformance.scenario.models import ScenarioResult


def format_markdown(results: list[ScenarioResult]) -> str:
    """Format scenario results as human-readable Markdown."""
    total = len(results)
    passed = sum(1 for r in results if r.passed)
    failed = total - passed
    total_steps = sum(r.total_steps for r in results)
    passed_steps = sum(r.passed_steps for r in results)
    lines = [
        "# MCP Conformance Report",
        "",
        f"**Generated:** {datetime.now(UTC).isoformat()}",
        "",
        "## Summary",
        "",
        f"- Scenarios: {passed}/{total} passed ({failed} failed)",
        f"- Steps:     {passed_steps}/{total_steps} passed",
        "",
        "## Details",
        "",
    ]
    for result in results:
        status = "✅ PASS" if result.passed else "❌ FAIL"
        lines.append(f"### {status} — {result.scenario_title} (`{result.scenario_id}`)")
        lines.append("")
        for sr in result.step_results:
            if not sr.passed:
                for err in sr.errors:
                    lines.append(f"- Step {sr.step_index} (`{sr.step_id}`): {err}")
            else:
                lines.append(f"- Step {sr.step_index} (`{sr.step_id}`): OK ({sr.elapsed_ms:.0f}ms)")
        lines.append("")
    return "\n".join(lines)
