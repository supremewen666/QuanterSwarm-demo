"""Backtest performance metrics."""

from __future__ import annotations

from quanter_swarm.services.backtest.drawdown import max_drawdown
from quanter_swarm.services.backtest.sharpe import sharpe_ratio
from quanter_swarm.services.backtest.sortino import sortino_ratio
from quanter_swarm.services.backtest.win_rate import win_rate


def turnover(returns: list[float]) -> float:
    return round(sum(abs(value) for value in returns) / max(1, len(returns)), 4)


def summarize_backtest_metrics(returns: list[float]) -> dict[str, float]:
    return {
        "sharpe": sharpe_ratio(returns),
        "sortino": round(sortino_ratio(returns), 4),
        "max_drawdown": max_drawdown(returns),
        "turnover": turnover(returns),
        "win_rate": round(win_rate(returns), 4),
    }
