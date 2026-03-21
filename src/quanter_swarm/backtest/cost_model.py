"""Explicit cost model for backtest replay."""

from __future__ import annotations

from collections.abc import Iterable

from quanter_swarm.backtest.models import Fill


class BacktestCostModel:
    def __init__(self, *, spread_bps: float = 2.0) -> None:
        self.spread_bps = spread_bps

    def transaction_cost(self, fills: Iterable[Fill]) -> float:
        return round(sum(float(fill.total_cost) for fill in fills), 6)

    def spread_cost(self, fills: Iterable[Fill]) -> float:
        total = 0.0
        for fill in fills:
            notional = float(fill.filled_notional or 0.0)
            total += notional * self.spread_bps / 10_000
        return round(total, 6)

    def slippage_cost(self, fills: Iterable[Fill]) -> float:
        total = 0.0
        for fill in fills:
            if fill.filled_notional is None or fill.fill_ratio <= 0:
                continue
            total += max(0.0, float(fill.total_cost))
        return round(total, 6)
