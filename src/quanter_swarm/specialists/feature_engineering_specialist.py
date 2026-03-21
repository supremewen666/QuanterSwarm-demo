"""Feature engineering specialist."""

from quanter_swarm.specialists.base_specialist import BaseSpecialist


class FeatureEngineeringSpecialist(BaseSpecialist):
    name = "feature_engineering"
    supported_tasks = ("feature_engineering", "signal_features")
    cost_hint = "medium"
    priority = 85

    def build(self, packet: dict) -> dict:
        return self._run_tool("feature_engineering", packet)

    def execute(self, payload: dict) -> dict:
        return self.build(payload)
