"""Tests for report formatters."""

from mcp_conformance.reports.json_report import format_json
from mcp_conformance.reports.markdown_report import format_markdown
from mcp_conformance.scenario.models import ScenarioResult, StepResult


class TestReports:
    def test_json_report(self) -> None:
        results = [
            ScenarioResult(
                scenario_id="test-1",
                scenario_title="Test One",
                passed=True,
                total_steps=1,
                passed_steps=1,
                step_results=[StepResult(step_index=0, passed=True)],
            )
        ]
        output = format_json(results)
        assert '"passed": true' in output
        assert "test-1" in output

    def test_markdown_report(self) -> None:
        results = [
            ScenarioResult(
                scenario_id="test-1",
                scenario_title="Test One",
                passed=True,
                total_steps=1,
                passed_steps=1,
                step_results=[StepResult(step_index=0, passed=True)],
            )
        ]
        output = format_markdown(results)
        assert "✅" in output
        assert "Test One" in output
