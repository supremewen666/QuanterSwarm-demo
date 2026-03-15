from quanter_swarm.evaluation.metrics import summarize_metrics


def test_summarize_metrics_returns_expected_keys() -> None:
    metrics = summarize_metrics([0.1, -0.05, 0.02])
    assert {"pnl", "drawdown", "sharpe", "sortino", "stability", "win_rate"} <= metrics.keys()
