"""Scorecard builder."""


def build_scorecard(symbol: str, score: float) -> dict:
    return {"symbol": symbol, "composite_score": score}
