from pathlib import Path

import pytest

from quanter_swarm.errors import BacktestError
from quanter_swarm.services.backtest.configured_runner import ConfiguredExperimentRunner


def test_configured_experiment_runner_executes_baseline_config(tmp_path: Path) -> None:
    payload = ConfiguredExperimentRunner(data_dir=tmp_path).run("baseline_single_agent")
    assert payload["experiment_name"] == "baseline_single_agent"
    assert payload["mode"] == "single_agent"
    assert len(payload["results"]) == 3
    assert {row["symbol"] for row in payload["results"]} == {"AAPL", "MSFT", "NVDA"}
    assert (tmp_path / f"{payload['experiment_id']}.json").exists()
    assert (tmp_path / f"{payload['experiment_id']}.md").exists()
    artifact_dir = tmp_path / payload["experiment_id"]
    assert (artifact_dir / "experiment_table.csv").exists()
    assert (artifact_dir / "equity_curve.png").exists()
    assert (artifact_dir / "drawdown_curve.png").exists()


def test_configured_experiment_runner_rejects_unknown_config(tmp_path: Path) -> None:
    with pytest.raises(BacktestError, match="Unknown experiment config"):
        ConfiguredExperimentRunner(data_dir=tmp_path).run("missing_config")
