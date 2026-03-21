"""Risk specialist."""

from __future__ import annotations

from quanter_swarm.specialists.base_specialist import BaseSpecialist


class RiskSpecialist(BaseSpecialist):
    name = "risk"
    supported_tasks = ("risk_assessment", "guardrail_check")
    cost_hint = "low"
    priority = 95

    def assess(self, proposal: dict) -> dict:
        return self._run_tool("risk_assessment", proposal)

    def execute(self, payload: dict) -> dict:
        return self.assess(payload)
