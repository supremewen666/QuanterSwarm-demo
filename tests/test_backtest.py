from pathlib import Path

from quanter_swarm.backtest.walk_forward import WalkForwardBacktester


def test_walk_forward_backtest_outputs_artifacts(tmp_path: Path) -> None:
    payload = WalkForwardBacktester(data_dir=tmp_path).run(
        symbols=["AAPL", "MSFT"],
        steps=6,
        train_window=4,
        test_window=2,
        rolling_window=2,
        capital=100_000,
    )
    assert payload["steps"] == 6
    assert payload["train_window"] == 4
    assert payload["test_window"] == 2
    assert payload["rolling_window"] == 2
    assert len(payload["step_results"]) == 6
    assert "summary_metrics" in payload
    assert "sharpe" in payload["summary_metrics"]
    assert "sortino" in payload["summary_metrics"]
    assert "max_drawdown" in payload["summary_metrics"]
    assert "turnover" in payload["summary_metrics"]
    assert "win_rate" in payload["summary_metrics"]
    assert "leader_attribution" in payload
    assert "portfolio_attribution" in payload
    assert (tmp_path / f"{payload['backtest_id']}.json").exists()
    assert (tmp_path / f"{payload['backtest_id']}.md").exists()


def test_walk_forward_backtest_step_has_replay_fields(tmp_path: Path) -> None:
    payload = WalkForwardBacktester(data_dir=tmp_path).run(
        symbols=["NVDA"],
        steps=3,
        train_window=2,
        test_window=1,
        rolling_window=1,
        capital=50_000,
    )
    step = payload["step_results"][0]
    assert "realized_return" in step
    assert "leader_attribution" in step
    assert "events" in step
    assert step["event_count"] == len(step["events"])
    assert step["phase"] in {"train", "test"}
    assert "window_index" in step
    assert "rolling_start" in step
    assert "portfolio_attribution" in step
