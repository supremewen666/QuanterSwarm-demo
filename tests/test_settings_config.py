from pathlib import Path

from quanter_swarm.config.defaults import (
    DEFAULT_BACKTEST_WINDOW,
    DEFAULT_MAX_SPECIALISTS_PER_CYCLE,
    DEFAULT_RISK_THRESHOLDS,
    DEFAULT_SYMBOLS,
    DEFAULT_TOKEN_BUDGET,
)
from quanter_swarm.utils.config import load_settings


def test_load_settings_uses_centralized_defaults(monkeypatch) -> None:
    monkeypatch.delenv("CONFIG_DIR", raising=False)
    monkeypatch.delenv("DEFAULT_SYMBOLS", raising=False)
    monkeypatch.delenv("TOKEN_BUDGET", raising=False)
    monkeypatch.delenv("MAX_SPECIALISTS_PER_CYCLE", raising=False)

    settings = load_settings()

    assert settings.default_symbols == list(DEFAULT_SYMBOLS)
    assert settings.token_budget == DEFAULT_TOKEN_BUDGET
    assert settings.max_specialists_per_cycle == DEFAULT_MAX_SPECIALISTS_PER_CYCLE
    assert settings.risk_thresholds == DEFAULT_RISK_THRESHOLDS
    assert settings.backtest_window == DEFAULT_BACKTEST_WINDOW


def test_load_settings_merges_yaml_and_env_overrides(tmp_path: Path, monkeypatch) -> None:
    (tmp_path / "app.yaml").write_text(
        "\n".join(
            [
                "app:",
                "  environment: stage",
                "  token_budget: low",
                "  max_specialists_per_cycle: 2",
                "  default_symbols: [TSLA, AMD]",
                "  risk_thresholds:",
                "    max_risk_penalty: 0.4",
                "  backtest_window:",
                "    steps: 12",
            ]
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv("CONFIG_DIR", str(tmp_path))
    monkeypatch.setenv("DEFAULT_SYMBOLS", "QQQ,SPY")
    monkeypatch.setenv("TOKEN_BUDGET", "high")

    settings = load_settings()

    assert settings.environment == "stage"
    assert settings.default_symbols == ["QQQ", "SPY"]
    assert settings.token_budget == "high"
    assert settings.max_specialists_per_cycle == 2
    assert settings.risk_thresholds["max_risk_penalty"] == 0.4
    assert settings.risk_thresholds["event_window_density"] == DEFAULT_RISK_THRESHOLDS["event_window_density"]
    assert settings.backtest_window["steps"] == 12
    assert settings.backtest_window["train_window"] == DEFAULT_BACKTEST_WINDOW["train_window"]
