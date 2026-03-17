"""Memory compression specialist."""

from quanter_swarm.specialists.base_specialist import BaseSpecialist


class MemoryCompressionSpecialist(BaseSpecialist):
    name = "memory_compression"
    supported_tasks = ("context_compression", "memory_summarization")
    cost_hint = "low"
    priority = 75

    def compress(self, payload: dict) -> dict:
        news = payload.get("news_inputs", [])
        return {
            "compressed": True,
            "summary": "; ".join(news[:2]),
            "payload": payload,
        }

    def execute(self, payload: dict) -> dict:
        return self.compress(payload)
