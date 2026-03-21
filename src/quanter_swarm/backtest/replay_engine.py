"""Replay execution helpers for walk-forward backtests."""

from __future__ import annotations

from typing import Any

from quanter_swarm.backtest.cost_model import BacktestCostModel
from quanter_swarm.backtest.events import (
    FillEvent,
    MarketEvent,
    OrderEvent,
    PortfolioUpdateEvent,
    SignalEvent,
)
from quanter_swarm.backtest.execution_simulator import ExecutionSimulator
from quanter_swarm.backtest.models import Fill, Order, Portfolio
from quanter_swarm.backtest.validator import BacktestValidator


def emit_replay_events(report: dict[str, Any], capital: float) -> list[dict[str, Any]]:
    symbol = str(report.get("symbol", "UNKNOWN"))
    trace_id = report.get("decision_trace_summary", {}).get("trace_id")
    market_summary = report.get("market_summary", {})
    top_signal = report.get("evaluation_summary", {}).get("top_signal") or {}
    portfolio = Portfolio.model_validate(report.get("portfolio_suggestion", {}))
    actions = report.get("paper_trade_actions", [])
    events: list[dict[str, Any]] = [
        MarketEvent(symbol=symbol, trace_id=trace_id, payload=market_summary).model_dump(),
        MarketEvent(symbol=symbol, trace_id=trace_id, payload=report.get("evidence_summary", {})).model_dump(),
        SignalEvent(symbol=symbol, trace_id=trace_id, payload=top_signal).model_dump(),
        PortfolioUpdateEvent(
            symbol=symbol,
            trace_id=trace_id,
            payload={
                "capital": capital,
                "mode": portfolio.mode,
                "gross_exposure": portfolio.gross_exposure,
                "positions": [position.model_dump() for position in portfolio.positions],
            },
        ).model_dump(),
    ]
    for action in actions:
        order = Order.model_validate(action.get("order", action))
        fill = Fill.model_validate(action)
        events.append(OrderEvent(symbol=symbol, trace_id=trace_id, payload=order.model_dump()).model_dump())
        events.append(FillEvent(symbol=symbol, trace_id=trace_id, payload=fill.model_dump()).model_dump())
    return events


def replay_report(report: dict[str, Any], capital: float) -> dict[str, Any]:
    BacktestValidator().validate_report(report)
    evaluation = report.get("evaluation_summary", {})
    top_signal = evaluation.get("top_signal") or {}
    portfolio = Portfolio.model_validate(report.get("portfolio_suggestion", {}))
    actions = [Fill.model_validate(action) for action in report.get("paper_trade_actions", [])]
    cost_model = BacktestCostModel()
    gross_exposure = float(portfolio.gross_exposure)
    signal_edge = float(top_signal.get("composite_rank_score", 0.5)) - 0.5
    if actions:
        avg_fill_ratio = sum(float(action.fill_ratio) for action in actions) / len(actions)
    else:
        avg_fill_ratio = 0.0
    total_transaction_fee = cost_model.transaction_cost(actions)
    total_slippage = cost_model.slippage_cost(actions)
    spread_cost = cost_model.spread_cost(actions)
    total_cost = total_transaction_fee + total_slippage + spread_cost
    cost_ratio = total_cost / max(1.0, capital)
    realized_return = signal_edge * gross_exposure * avg_fill_ratio - cost_ratio
    simulator = ExecutionSimulator()

    leader_attribution: dict[str, float] = {}
    for position in portfolio.positions:
        leader = str(position.leader)
        weight = float(position.weight)
        leader_attribution[leader] = round(
            leader_attribution.get(leader, 0.0) + signal_edge * weight * avg_fill_ratio,
            6,
        )

    allocation_mode = str(portfolio.allocation_mode)
    return {
        "signal_edge": round(signal_edge, 6),
        "avg_fill_ratio": round(avg_fill_ratio, 6),
        "gross_exposure": round(gross_exposure, 6),
        "transaction_fee": round(total_transaction_fee, 6),
        "slippage": round(total_slippage, 6),
        "spread_cost": round(spread_cost, 6),
        "cost_ratio": round(cost_ratio, 6),
        "realized_return": round(realized_return, 6),
        "leader_attribution": leader_attribution,
        "events": emit_replay_events(report, capital),
        "execution_summary": [simulator.simulate(action.get("order", {})) for action in report.get("paper_trade_actions", [])],
        "portfolio_attribution": {
            "allocation_mode": allocation_mode,
            "mode": portfolio.mode,
        },
    }
