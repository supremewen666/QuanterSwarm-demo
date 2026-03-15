"""Metric registry."""

from __future__ import annotations

from quanter_swarm.evaluation.drawdown import max_drawdown
from quanter_swarm.evaluation.pnl import pnl
from quanter_swarm.evaluation.sharpe import sharpe_ratio
from quanter_swarm.evaluation.sortino import sortino_ratio
from quanter_swarm.evaluation.stability import stability_score
from quanter_swarm.evaluation.win_rate import win_rate


def list_metrics() -> list[str]:
    return [
        "pnl",
        "annualized_return",
        "drawdown",
        "sharpe",
        "sortino",
        "stability",
        "win_rate",
        "turnover_proxy",
    ]


def summarize_metrics(returns: list[float]) -> dict[str, float]:
    annualized_return = 0.0
    if returns:
        annualized_return = (sum(returns) / len(returns)) * 252
    turnover = round(sum(abs(value) for value in returns) / max(1, len(returns)), 4)
    return {
        "pnl": round(pnl(returns), 4),
        "annualized_return": round(annualized_return, 4),
        "drawdown": max_drawdown(returns),
        "sharpe": sharpe_ratio(returns),
        "sortino": round(sortino_ratio(returns), 4),
        "stability": stability_score(returns),
        "win_rate": round(win_rate(returns), 4),
        "turnover_proxy": turnover,
    }
