from pathlib import Path

from quanter_swarm.agents.orchestrator import RootAgent
from quanter_swarm.services import EvolutionManager
from quanter_swarm.services.monitoring.runtime_metrics import build_runtime_monitoring_snapshot
from quanter_swarm.services.monitoring.runtime_tracing import build_monitoring_trace


def test_monitoring_layer_extracts_runtime_metrics() -> None:
    report = RootAgent().run_sync("AAPL")

    snapshot = build_runtime_monitoring_snapshot(report)
    trace = build_monitoring_trace(report)

    assert snapshot["latency"]["runtime_ms"] == report["decision_trace_summary"]["runtime_ms"]
    assert snapshot["token_usage"]["estimated_tokens"] >= 0
    assert snapshot["routing_decisions"]["leaders"] == report["router_decision"]["leader_selected"]
    assert trace["trace_id"] == report["decision_trace_summary"]["trace_id"]


def test_evolution_manager_surfaces_rollback_signal(tmp_path: Path) -> None:
    manager = EvolutionManager(
        root=tmp_path,
        config={
            "evolution": {
                "weak_prior_enabled": True,
                "manual_approval_only": False,
                "min_observations": 2,
                "min_posterior_lift": 0.01,
                "min_confidence": 0.5,
                "rollback_drawdown_threshold": 0.2,
                "rollback_sharpe_delta": -0.4,
            }
        },
    )

    result = manager.evolve(
        [
            {
                "leader": "momentum",
                "score": 0.7,
                "posterior_score": 0.8,
                "composite_rank_score": 0.72,
                "parameter_version": "v1",
                "prior_sample_count": 5,
                "prior_confidence": 0.7,
                "confidence": 0.8,
                "drawdown": -0.25,
                "sharpe_delta": -0.6,
            }
        ],
        current_threshold=0.5,
    )

    assert result["rollback"]["should_rollback"] is True
    assert result["action"] == "rollback"
