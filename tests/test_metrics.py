from quanter_swarm.services.backtest.metrics import summarize_metrics


def test_summarize_metrics_returns_expected_keys() -> None:
    metrics = summarize_metrics([0.1, -0.05, 0.02])
    assert {
        "pnl",
        "annualized_return",
        "drawdown",
        "sharpe",
        "sortino",
        "stability",
        "win_rate",
        "turnover_proxy",
    } <= metrics.keys()
    assert abs(metrics["annualized_return"]) < 100
