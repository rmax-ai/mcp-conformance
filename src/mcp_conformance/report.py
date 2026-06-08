"""Result reporting — collect, format, and output scenario results."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from typing import Any

from .scenario import ScenarioResult, StepResult


def format_summary(results: list[ScenarioResult]) -> str:
    """Format a human-readable summary of scenario results."""
    total = len(results)
    passed = sum(1 for r in results if r.passed)
    failed = total - passed
    total_steps = sum(r.total_steps for r in results)
    passed_steps = sum(r.passed_steps for r in results)
    lines = [
        f"MCP Conformance Report — {datetime.now(UTC).isoformat()}",
        "",
        f"Scenarios: {passed}/{total} passed ({failed} failed)",
        f"Steps:     {passed_steps}/{total_steps} passed",
        "",
    ]
    for result in results:
        status = "PASS" if result.passed else "FAIL"
        lines.append(f"  [{status}] {result.scenario_name}")
        for sr in result.step_results:
            if not sr.passed:
                for err in sr.errors:
                    lines.append(f"          step {sr.step_index}: {err}")
    return "\n".join(lines)


def format_json(results: list[ScenarioResult]) -> str:
    """Format results as JSON."""
    return json.dumps(
        {
            "generated_at": datetime.now(UTC).isoformat(),
            "summary": {
                "total_scenarios": len(results),
                "passed": sum(1 for r in results if r.passed),
                "failed": sum(1 for r in results if not r.passed),
            },
            "scenarios": [_scenario_to_dict(r) for r in results],
        },
        indent=2,
    )


def _scenario_to_dict(result: ScenarioResult) -> dict[str, Any]:
    return {
        "name": result.scenario_name,
        "passed": result.passed,
        "total_steps": result.total_steps,
        "passed_steps": result.passed_steps,
        "failed_steps": result.failed_steps,
        "steps": [_step_to_dict(s) for s in result.step_results],
    }


def _step_to_dict(step: StepResult) -> dict[str, Any]:
    return {
        "step_index": step.step_index,
        "passed": step.passed,
        "errors": step.errors,
        "elapsed_ms": step.elapsed_ms,
    }
