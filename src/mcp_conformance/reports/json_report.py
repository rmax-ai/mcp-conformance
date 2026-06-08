"""JSON report — canonical machine-readable output."""

from __future__ import annotations

import json
from datetime import UTC, datetime

from mcp_conformance.scenario.models import ScenarioResult, StepResult


def format_json(results: list[ScenarioResult]) -> str:
    """Format scenario results as canonical JSON."""
    return json.dumps(
        {
            "generated_at": datetime.now(UTC).isoformat(),
            "format_version": "0.1",
            "summary": {
                "total_scenarios": len(results),
                "passed": sum(1 for r in results if r.passed),
                "failed": sum(1 for r in results if not r.passed),
            },
            "scenarios": [_scenario_to_dict(r) for r in results],
        },
        indent=2,
    )


def _scenario_to_dict(result: ScenarioResult) -> dict:
    return {
        "id": result.scenario_id,
        "title": result.scenario_title,
        "passed": result.passed,
        "total_steps": result.total_steps,
        "passed_steps": result.passed_steps,
        "failed_steps": result.failed_steps,
        "skipped_steps": result.skipped_steps,
        "total_elapsed_ms": result.total_elapsed_ms,
        "steps": [_step_to_dict(s) for s in result.step_results],
    }


def _step_to_dict(step: StepResult) -> dict:
    return {
        "step_index": step.step_index,
        "step_id": step.step_id,
        "passed": step.passed,
        "skipped": step.skipped,
        "errors": step.errors,
        "elapsed_ms": step.elapsed_ms,
        "request": step.request,
        "response": step.response,
    }
