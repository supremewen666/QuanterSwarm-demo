"""Transaction cost analysis helpers."""

from __future__ import annotations

from typing import Any


def summarize_tca(execution: dict[str, Any]) -> dict[str, Any]:
    filled_notional = float(execution.get("filled_notional", 0.0))
    total_cost = float(execution.get("total_cost", 0.0))
    return {
        "filled_notional": round(filled_notional, 6),
        "total_cost": round(total_cost, 6),
        "cost_bps": round(0.0 if filled_notional <= 0 else total_cost / filled_notional * 10_000, 4),
        "fill_ratio": float(execution.get("fill_ratio", 0.0)),
        "status": execution.get("status", "unknown"),
    }
