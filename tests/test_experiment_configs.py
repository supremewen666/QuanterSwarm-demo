from pathlib import Path

import yaml


def test_experiment_configs_exist_and_define_supported_modes() -> None:
    root = Path("experiments")
    files = sorted(root.glob("*.yaml"))
    assert {path.name for path in files} == {
        "baseline_fixed_multi_agent.yaml",
        "baseline_single_agent.yaml",
        "routed_ephemeral.yaml",
        "routed_multi_agent.yaml",
    }

    modes = set()
    for path in files:
        payload = yaml.safe_load(path.read_text(encoding="utf-8"))
        experiment = payload["experiment"]
        assert experiment["name"]
        assert experiment["description"]
        assert experiment["symbols"] == ["AAPL", "MSFT", "NVDA"]
        assert isinstance(experiment["scenario"], dict)
        modes.add(experiment["mode"])

    assert modes == {"single_agent", "fixed_multi_agent", "routed_multi_agent", "routed_ephemeral"}
