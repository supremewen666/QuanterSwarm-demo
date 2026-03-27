"""Sentiment specialist."""

from quanter_swarm.agents.specialists.base_specialist import BaseSpecialist


class SentimentSpecialist(BaseSpecialist):
    name = "sentiment"
    supported_tasks = ("sentiment_analysis", "news_scoring")
    cost_hint = "medium"
    priority = 70

    def score(self, text: str) -> float:
        return float(self._run_tool("sentiment_analysis", {"text": text})["score"])

    def execute(self, payload: dict) -> dict:
        text = str(payload.get("text") or payload.get("compressed_context") or "")
        return self._run_tool("sentiment_analysis", {"text": text})
