from pathlib import Path

import pytest

from quanter_swarm.errors import BacktestError
from quanter_swarm.evaluation.experiment_runner import ExperimentRunner


def test_experiment_runner_router_ablation_outputs_results(tmp_path: Path) -> None:
    payload = ExperimentRunner(data_dir=tmp_path).run("router_ablation", "AAPL")
    assert payload["experiment_type"] == "router_ablation"
    assert len(payload["results"]) == 4
    assert {row["name"] for row in payload["results"]} >= {"routed", "always_on", "routed_max_1", "routed_max_3"}
    assert (tmp_path / f"{payload['experiment_id']}.json").exists()
    assert (tmp_path / f"{payload['experiment_id']}.md").exists()


def test_experiment_runner_allocation_ablation_has_three_variants(tmp_path: Path) -> None:
    payload = ExperimentRunner(data_dir=tmp_path).run("allocation_ablation", "MSFT")
    assert {row["name"] for row in payload["results"]} == {"simple", "volatility_aware", "correlation_aware"}


def test_experiment_runner_rejects_unknown_experiment_type(tmp_path: Path) -> None:
    with pytest.raises(BacktestError, match="Unsupported experiment_type"):
        ExperimentRunner(data_dir=tmp_path).run("unknown_ablation", "MSFT")
