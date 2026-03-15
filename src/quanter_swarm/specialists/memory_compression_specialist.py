"""Memory compression specialist."""

from quanter_swarm.specialists.base_specialist import BaseSpecialist


class MemoryCompressionSpecialist(BaseSpecialist):
    name = "memory_compression"

    def compress(self, payload: dict) -> dict:
        news = payload.get("news_inputs", [])
        return {
            "compressed": True,
            "summary": "; ".join(news[:2]),
            "payload": payload,
        }
