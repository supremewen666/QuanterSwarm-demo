"""Validation helpers for backtest runs."""

from __future__ import annotations

from typing import Any

from quanter_swarm.errors import BacktestError


class BacktestValidator:
    def validate_run(self, run_config: dict[str, Any]) -> None:
        symbols = list(run_config.get("symbols", []))
        if not symbols:
            raise BacktestError("Backtest requires at least one symbol.")
        for key in ("steps", "train_window", "test_window", "rolling_window"):
            value = int(run_config.get(key, 0))
            if value <= 0:
                raise BacktestError(f"{key} must be > 0.")
        if float(run_config.get("capital", 0.0)) <= 0.0:
            raise BacktestError("capital must be > 0.")

    def validate_report(self, report: dict[str, Any]) -> None:
        if "portfolio_suggestion" not in report:
            raise BacktestError("Backtest report missing portfolio_suggestion.")
        if "paper_trade_actions" not in report:
            raise BacktestError("Backtest report missing paper_trade_actions.")
