"""Cost models for backtest replay."""

from __future__ import annotations

from collections.abc import Iterable

from quanter_swarm.backtest.models import Fill


def transaction_fee(fills: Iterable[Fill]) -> float:
    return round(sum(float(fill.total_cost) for fill in fills), 6)


def slippage(fills: Iterable[Fill]) -> float:
    total = 0.0
    for fill in fills:
        if fill.filled_notional is None or fill.fill_ratio <= 0:
            continue
        total += max(0.0, float(fill.total_cost))
    return round(total, 6)
