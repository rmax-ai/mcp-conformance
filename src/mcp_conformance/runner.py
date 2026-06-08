"""Scenario runner — orchestrates scenario steps, delegates to partner adapters,
collects results."""

from __future__ import annotations

from typing import Any

from mcp_conformance.partners.base import AuthStep, FaultConfig, TestPartner
from mcp_conformance.scenario import Scenario, ScenarioResult, StepResult


class ScenarioRunner:
    """Loads and executes scenarios against a test partner."""

    def __init__(self, partner: TestPartner) -> None:
        self._partner = partner

    async def run(self, scenario: Scenario) -> ScenarioResult:
        """Execute a scenario against the configured partner."""
        step_results: list[StepResult] = []
        all_passed = True

        for i, step in enumerate(scenario.steps):
            result = await self._execute_step(i, step)
            step_results.append(result)
            if not result.passed:
                all_passed = False
                break

        passed_count = sum(1 for r in step_results if r.passed)
        return ScenarioResult(
            scenario_name=scenario.name,
            passed=all_passed,
            step_results=step_results,
            total_steps=len(scenario.steps),
            passed_steps=passed_count,
            failed_steps=len(step_results) - passed_count,
        )

    async def _execute_step(self, index: int, step: Any) -> StepResult:
        """Execute a single scenario step."""
        errors: list[str] = []

        if step.step_type == "client_request":
            resp = await self._partner.send_auth_request(
                AuthStep(
                    method=step.params.get("method", "GET"),
                    url=step.params.get("url", ""),
                    headers=step.params.get("headers", {}),
                    body=step.params.get("body"),
                )
            )
            response_dict = {
                "status": resp.status,
                "headers": resp.headers,
                "body": resp.body,
            }

            for assertion in step.assertions:
                if assertion.type == "status":
                    from mcp_conformance.assertions.http import assert_status

                    errors.extend(assert_status(response_dict, assertion.expected))
                elif assertion.type == "body_json_path":
                    from mcp_conformance.assertions.http import assert_json_path

                    errors.extend(
                        assert_json_path(
                            response_dict,
                            assertion.expected if isinstance(assertion.expected, str) else "",
                        )
                    )

        elif step.step_type == "inject_fault":
            await self._partner.configure_injection(
                FaultConfig(
                    endpoint=step.params.get("endpoint", ""),
                    behavior=step.params.get("behavior", ""),
                    params=step.params.get("params", {}),
                )
            )

        elif step.step_type == "wait":
            import asyncio

            await asyncio.sleep(step.params.get("seconds", 1))

        return StepResult(
            step_index=index,
            passed=len(errors) == 0,
            errors=errors,
        )
