"""Memory compression specialist."""

from quanter_swarm.agents.specialists.base_specialist import BaseSpecialist


class MemoryCompressionSpecialist(BaseSpecialist):
    name = "memory_compression"
    supported_tasks = ("context_compression", "memory_summarization")
    cost_hint = "low"
    priority = 75

    def compress(self, payload: dict) -> dict:
        return self._run_tool("memory_compression", payload)

    def execute(self, payload: dict) -> dict:
        return self.compress(payload)
