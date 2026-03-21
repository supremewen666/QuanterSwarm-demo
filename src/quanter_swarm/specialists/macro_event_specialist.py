"""Macro event specialist."""

from quanter_swarm.specialists.base_specialist import BaseSpecialist


class MacroEventSpecialist(BaseSpecialist):
    name = "macro_event"
    supported_tasks = ("macro_event_analysis", "event_impact")
    cost_hint = "medium"
    priority = 80

    def analyze(self, event: dict) -> dict:
        return self._run_tool("macro_event_analysis", event)

    def execute(self, payload: dict) -> dict:
        return self.analyze(payload)
