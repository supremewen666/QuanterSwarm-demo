"""Fundamentals parser."""


def parse_fundamentals(raw_payload: dict) -> dict:
    valuation = raw_payload.get("valuation", 0.0)
    growth = raw_payload.get("growth", 0.0)
    quality = raw_payload.get("quality", 0.0)
    leverage = raw_payload.get("leverage", 0.0)
    return {
        "valuation_score": round(max(0.0, 1 - valuation / 4), 2),
        "growth_score": round(min(1.0, growth / 2), 2),
        "quality_score": round(min(1.0, quality / 2), 2),
        "leverage_penalty": round(leverage / 2, 2),
    }
