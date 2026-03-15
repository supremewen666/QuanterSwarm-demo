from pathlib import Path

from quanter_swarm.cli import render_report, validate_repo_configs


def test_render_report_supports_markdown() -> None:
    rendered = render_report(
        {
            "symbol": "AAPL",
            "active_regime": "trend_up",
            "active_strategy_teams": ["momentum"],
            "market_summary": {"price": 100, "change_pct": 0.01, "volatility": 0.02},
            "factor_scorecard": {"composite_score": 0.7},
            "risk_alerts": {"status": "clear", "warnings": []},
            "portfolio_suggestion": {"mode": "paper", "gross_exposure": 0.5, "cash_buffer": 0.5, "positions": []},
            "paper_trade_actions": [],
            "evaluation_summary": {"signal_count": 1, "execution_reason": "paper_mode"},
            "one_page_summary": {"highlights": ["leaders=momentum"]},
        },
        "markdown",
    )
    assert rendered.startswith("# AAPL Research Cycle")


def test_validate_repo_configs_accepts_current_repo() -> None:
    validation = validate_repo_configs(Path("configs"))
    assert validation["ok"] is True
