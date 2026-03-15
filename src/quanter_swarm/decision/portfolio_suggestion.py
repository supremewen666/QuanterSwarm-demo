"""Portfolio suggestion."""

from __future__ import annotations


def build_portfolio(
    ideas: list[dict],
    cash_buffer: float = 0.1,
    max_single_weight: float = 0.25,
    exposure_multiplier: float = 1.0,
    target_positions: int | None = None,
) -> dict:
    tradable = [idea for idea in ideas if idea.get("score", 0.0) >= 0.5]
    if target_positions is not None:
        tradable = tradable[:target_positions]
    if not tradable or exposure_multiplier <= 0:
        return {
            "positions": [],
            "cash_buffer": 1.0,
            "gross_exposure": 0.0,
            "mode": "no_trade",
            "rationale": "no qualified ideas after risk review",
        }

    gross_exposure = round(max(0.0, 1 - cash_buffer) * min(exposure_multiplier, 1.0), 4)
    raw_weight = min(max_single_weight, round(gross_exposure / len(tradable), 4))
    positions = [{"symbol": idea["symbol"], "leader": idea["leader"], "weight": raw_weight} for idea in tradable]
    deployed = round(raw_weight * len(positions), 4)
    mode = "reduced_exposure" if exposure_multiplier < 1 else "paper"
    return {
        "positions": positions,
        "cash_buffer": round(1 - deployed, 4),
        "gross_exposure": deployed,
        "mode": mode,
        "rationale": "risk-adjusted allocation across active leaders",
    }
