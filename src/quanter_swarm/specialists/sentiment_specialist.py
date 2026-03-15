"""Sentiment specialist."""

from quanter_swarm.specialists.base_specialist import BaseSpecialist


class SentimentSpecialist(BaseSpecialist):
    name = "sentiment"

    def score(self, text: str) -> float:
        if not text:
            return 0.0
        lower = text.lower()
        score = 0.5
        for token in ("stable", "momentum", "growth", "strong"):
            if token in lower:
                score += 0.1
        for token in ("risk", "uncertainty", "weak", "decline"):
            if token in lower:
                score -= 0.1
        return round(max(0.0, min(1.0, score)), 2)
