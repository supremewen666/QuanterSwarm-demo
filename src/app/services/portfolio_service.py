"""Portfolio extraction helpers for research outputs."""

from __future__ import annotations

from typing import Any


def portfolio_plan_from_report(report: dict[str, Any]) -> dict[str, Any]:
    suggestion = report.get("portfolio_suggestion", {})
    return {
        "symbol": report.get("symbol"),
        "regime": report.get("active_regime"),
        "positions": suggestion.get("positions", []),
        "gross_exposure": suggestion.get("gross_exposure", 0.0),
        "cash_buffer": suggestion.get("cash_buffer", 1.0),
        "allocation_mode": suggestion.get("allocation_mode", "simple"),
        "mode": suggestion.get("mode", "no_trade"),
        "rationale": suggestion.get("rationale", ""),
    }


def mock_execution_from_report(report: dict[str, Any]) -> dict[str, Any]:
    return {
        "symbol": report.get("symbol"),
        "orders": report.get("paper_trade_actions", []),
        "status": report.get("risk_check", {}).get("status", "unknown"),
        "reason": report.get("risk_check", {}).get("reason", ""),
    }
