"""Application settings."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from quanter_swarm.config.defaults import (
    DEFAULT_BACKTEST_WINDOW,
    DEFAULT_MAX_SPECIALISTS_PER_CYCLE,
    DEFAULT_RISK_THRESHOLDS,
    DEFAULT_SYMBOLS,
    DEFAULT_TOKEN_BUDGET,
)


@dataclass
class Settings:
    environment: str = "dev"
    execution_mode: str = "paper"
    data_dir: Path = Path("data")
    config_dir: Path = Path("configs")
    default_symbols: list[str] = field(default_factory=lambda: list(DEFAULT_SYMBOLS))
    starting_capital: float = 100_000.0
    token_budget: str = DEFAULT_TOKEN_BUDGET
    max_specialists_per_cycle: int = DEFAULT_MAX_SPECIALISTS_PER_CYCLE
    risk_thresholds: dict[str, float] = field(default_factory=lambda: dict(DEFAULT_RISK_THRESHOLDS))
    backtest_window: dict[str, int] = field(default_factory=lambda: dict(DEFAULT_BACKTEST_WINDOW))
    data_provider: dict = field(default_factory=dict)
