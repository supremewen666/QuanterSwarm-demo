"""Risk budgeting helpers for portfolio construction."""

from __future__ import annotations


def resolve_regime_controls(
    regime: str | None,
    *,
    base_cash_buffer: float,
    base_exposure_multiplier: float,
    base_target_positions: int,
    regime_overrides: dict | None,
) -> dict[str, float | int]:
    override = (regime_overrides or {}).get(regime or "", {})
    return {
        "cash_buffer": float(override.get("cash_buffer", base_cash_buffer)),
        "exposure_multiplier": float(override.get("exposure_multiplier", base_exposure_multiplier)),
        "target_positions": int(override.get("target_positions", base_target_positions)),
    }


def apply_concentration_penalty(
    score: float,
    *,
    correlation: float,
    event_risk: float,
    correlation_penalty: float,
    event_penalty: float,
) -> float:
    corr_discount = max(0.15, 1 - correlation_penalty * max(0.0, min(1.0, correlation)))
    event_discount = max(0.2, 1 - event_penalty * max(0.0, min(1.0, event_risk)))
    return max(0.0, score * corr_discount * event_discount)
