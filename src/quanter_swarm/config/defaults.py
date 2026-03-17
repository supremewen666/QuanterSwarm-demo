"""Centralized default configuration values."""

from typing import Final

DEFAULT_TOKEN_BUDGET: Final[str] = "medium"
DEFAULT_MAX_SPECIALISTS_PER_CYCLE: Final[int] = 3
DEFAULT_SYMBOLS: Final[tuple[str, ...]] = ("AAPL", "MSFT", "NVDA")
DEFAULT_RISK_THRESHOLDS: Final[dict[str, float]] = {
    "max_risk_penalty": 0.6,
    "risk_penalty_per_warning": 0.2,
    "default_regime_fit": 0.8,
    "leader_score_confidence_weight": 0.8,
    "regime_confidence_weight": 0.2,
    "minimum_signal_confidence": 0.1,
    "event_window_density": 0.6,
}
DEFAULT_BACKTEST_WINDOW: Final[dict[str, int]] = {
    "steps": 20,
    "train_window": 60,
    "test_window": 20,
    "rolling_window": 20,
}
