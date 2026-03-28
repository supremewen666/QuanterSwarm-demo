from pathlib import Path

import pytest

from quanter_swarm.agents.orchestrator import RootAgent
from quanter_swarm.core import RiskGuardrailError
from quanter_swarm.core.runtime.config import validate_config_consistency


def test_report_includes_config_provenance() -> None:
    report = RootAgent().run_sync(symbol="AAPL")
    provenance = report["config_provenance"]
    assert provenance["fingerprint"]
    assert "router.yaml" in provenance["files"]


def test_validate_config_consistency_blocks_live_mode(tmp_path: Path) -> None:
    (tmp_path / "leaders").mkdir(parents=True, exist_ok=True)
    (tmp_path / "leaders" / "momentum.yaml").write_text("leader:\n  name: momentum\n", encoding="utf-8")
    (tmp_path / "leaders" / "breakout_event.yaml").write_text("leader:\n  name: breakout_event\n", encoding="utf-8")
    (tmp_path / "app.yaml").write_text("app:\n  execution_mode: paper\n", encoding="utf-8")
    (tmp_path / "router.yaml").write_text("default_regime: trend_up\nrouting:\n  trend_up: [momentum]\n", encoding="utf-8")
    (tmp_path / "regimes.yaml").write_text("regimes:\n  trend_up:\n    leaders: [momentum]\n", encoding="utf-8")
    (tmp_path / "risk.yaml").write_text("risk:\n  max_single_weight: 0.2\n", encoding="utf-8")
    (tmp_path / "portfolio.yaml").write_text("portfolio:\n  cash_buffer: 0.1\n", encoding="utf-8")
    (tmp_path / "execution.yaml").write_text("execution:\n  mode: live\n  allow_live: true\n", encoding="utf-8")
    (tmp_path / "paper_broker.yaml").write_text("paper_broker:\n  slippage_bps: 5\n", encoding="utf-8")
    (tmp_path / "ranking.yaml").write_text("ranking:\n  signal_threshold: 0.5\n", encoding="utf-8")
    (tmp_path / "evolution.yaml").write_text("evolution:\n  enabled: true\n", encoding="utf-8")
    with pytest.raises(RiskGuardrailError, match="Dangerous config"):
        validate_config_consistency(tmp_path)
