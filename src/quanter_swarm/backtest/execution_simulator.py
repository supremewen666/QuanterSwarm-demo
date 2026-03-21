"""Simulation helpers for backtest fills."""

from __future__ import annotations

from typing import Any

from quanter_swarm.execution.fills import decide_fill_status, estimate_fill_ratio
from quanter_swarm.execution.slippage import apply_slippage, estimate_slippage_bps


class ExecutionSimulator:
    def simulate(self, order: dict[str, Any]) -> dict[str, Any]:
        decision_price = float(order.get("decision_price", order.get("reference_price", 0.0)))
        notional = float(order.get("notional", 0.0))
        avg_volume = max(1.0, float(order.get("avg_volume", 1_000_000.0)))
        participation_rate = max(0.0, min(2.0, notional / avg_volume))
        volatility = max(0.0, float(order.get("volatility", 0.0)))
        event_window = bool(order.get("event_window", False))
        is_open = bool(order.get("is_open_session", False))
        slippage_bps = estimate_slippage_bps(
            base_bps=float(order.get("base_slippage_bps", 5.0)),
            volatility=volatility,
            participation_rate=participation_rate,
            is_open=is_open,
        )
        fill_ratio = estimate_fill_ratio(
            participation_rate=participation_rate,
            volatility=volatility,
            fill_model=str(order.get("fill_model", "partial")),
        )
        status = decide_fill_status(
            participation_rate=participation_rate,
            volatility=volatility,
            event_window=event_window,
            fill_ratio=fill_ratio,
        )
        if status == "unfilled":
            fill_ratio = 0.0
        if status == "delayed":
            fill_ratio = min(fill_ratio, 0.5)
        fill_price = apply_slippage(decision_price, slippage_bps)
        return {
            "status": status,
            "fill_ratio": fill_ratio,
            "fill_price": round(fill_price, 6),
            "slippage_bps": slippage_bps,
            "filled_notional": round(notional * fill_ratio, 6),
        }
