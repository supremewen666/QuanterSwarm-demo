"""Replay execution helpers for walk-forward backtests."""

from __future__ import annotations

from typing import Any


def replay_report(report: dict[str, Any], capital: float) -> dict[str, Any]:
    evaluation = report.get("evaluation_summary", {})
    top_signal = evaluation.get("top_signal") or {}
    portfolio = report.get("portfolio_suggestion", {})
    actions = report.get("paper_trade_actions", [])
    gross_exposure = float(portfolio.get("gross_exposure", 0.0))
    signal_edge = float(top_signal.get("composite_rank_score", 0.5)) - 0.5
    if actions:
        avg_fill_ratio = sum(float(action.get("fill_ratio", 0.0)) for action in actions) / len(actions)
    else:
        avg_fill_ratio = 0.0
    total_cost = sum(float(action.get("total_cost", 0.0)) for action in actions)
    cost_ratio = total_cost / max(1.0, capital)
    realized_return = signal_edge * gross_exposure * avg_fill_ratio - cost_ratio

    leader_attribution: dict[str, float] = {}
    for position in portfolio.get("positions", []):
        leader = str(position.get("leader", "unknown"))
        weight = float(position.get("weight", 0.0))
        leader_attribution[leader] = round(
            leader_attribution.get(leader, 0.0) + signal_edge * weight * avg_fill_ratio,
            6,
        )

    allocation_mode = str(portfolio.get("allocation_mode", "simple"))
    return {
        "signal_edge": round(signal_edge, 6),
        "avg_fill_ratio": round(avg_fill_ratio, 6),
        "gross_exposure": round(gross_exposure, 6),
        "cost_ratio": round(cost_ratio, 6),
        "realized_return": round(realized_return, 6),
        "leader_attribution": leader_attribution,
        "portfolio_attribution": {
            "allocation_mode": allocation_mode,
            "mode": portfolio.get("mode", "no_trade"),
        },
    }

