"""Workflow-style application use cases built on top of shared services."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class RunBacktest:
    """Execute the backtest use case through the application layer."""

    def execute(
        self,
        *,
        source: str = "internal_sim",
        symbols: list[str] | None = None,
        config_path: str | None = None,
        capital: float = 100_000.0,
    ) -> dict:
        from app.services.backtest_service import run_backtest

        return run_backtest(source=source, symbols=symbols, config_path=config_path, capital=capital)


@dataclass(slots=True)
class RunReplay:
    """Execute replay through the application layer."""

    def execute(self, *, run_id: str, capital: float = 100_000.0) -> dict:
        from app.services.replay_service import run_replay

        return run_replay(run_id=run_id, capital=capital)


@dataclass(slots=True)
class GenerateSignals:
    """Generate signals through the application layer."""

    def execute(
        self,
        *,
        source: str = "internal_sim",
        symbols: list[str] | None = None,
        as_of_date: str | None = None,
    ) -> dict:
        from app.services.signal_service import generate_signals

        return generate_signals(source=source, symbols=symbols, as_of_date=as_of_date)


@dataclass(slots=True)
class BuildDashboardData:
    """Build dashboard data through the application layer."""

    def execute(
        self,
        *,
        source: str = "internal_sim",
        symbols: list[str] | None = None,
        with_alpaca_readonly: bool = False,
    ) -> dict:
        from app.services.dashboard_service import build_dashboard_dataset

        return build_dashboard_dataset(
            source=source,
            symbols=symbols,
            with_alpaca_readonly=with_alpaca_readonly,
        )
