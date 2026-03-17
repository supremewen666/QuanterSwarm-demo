from quanter_swarm.backtest.metrics import summarize_backtest_metrics, turnover


def test_backtest_metrics_expose_required_metrics() -> None:
    metrics = summarize_backtest_metrics([0.02, -0.01, 0.015, -0.005, 0.01])
    assert set(metrics) == {"sharpe", "sortino", "max_drawdown", "turnover", "win_rate"}
    assert metrics["win_rate"] > 0.0
    assert metrics["turnover"] == turnover([0.02, -0.01, 0.015, -0.005, 0.01])


def test_backtest_metrics_handle_empty_returns() -> None:
    metrics = summarize_backtest_metrics([])
    assert metrics["sharpe"] == 0.0
    assert metrics["sortino"] == 0.0
    assert metrics["max_drawdown"] == 0.0
    assert metrics["turnover"] == 0.0
    assert metrics["win_rate"] == 0.0
