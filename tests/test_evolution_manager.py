from pathlib import Path

from quanter_swarm.services.evolution import EvolutionManager


def test_evolution_manager_builds_priors_and_writes_audit(tmp_path: Path) -> None:
    manager = EvolutionManager(
        root=tmp_path,
        config={
            "evolution": {
                "weak_prior_enabled": True,
                "top_k_similar_events": 3,
                "prior_lambda": 1.0,
                "manual_approval_only": True,
                "min_observations": 2,
            }
        },
    )
    manager.event_memory.append(
        {
            "event_id": "evt-1",
            "symbol": "AAPL",
            "event_type": "earnings",
            "impact": "positive",
            "regime": "trend_up",
            "macro_risk": 0.2,
            "trend": 0.06,
            "volatility": 0.03,
            "selected_leader": "momentum",
            "realized_outcome": 0.18,
            "confidence": 0.7,
            "sample_count": 4,
            "recorded_at": "2026-03-17T09:30:00+00:00",
        }
    )
    priors = manager.build_priors(
        {
            "event_id": "evt-2",
            "symbol": "AAPL",
            "event_type": "earnings",
            "impact": "positive",
            "regime": "trend_up",
            "macro_risk": 0.22,
            "trend": 0.05,
            "volatility": 0.04,
        }
    )
    assert priors["momentum"]["prior_score"] > 0

    result = manager.evolve(
        [
            {
                "leader": "momentum",
                "score": 0.72,
                "posterior_score": 0.81,
                "composite_rank_score": 0.7,
                "parameter_version": "v1",
                "prior_sample_count": 4,
                "prior_confidence": 0.7,
                "confidence": 0.8,
            }
        ],
        current_threshold=0.5,
        event_payload={
            "event_id": "evt-2",
            "symbol": "AAPL",
            "event_type": "earnings",
            "impact": "positive",
            "regime": "trend_up",
            "macro_risk": 0.22,
            "trend": 0.05,
            "volatility": 0.04,
        },
    )
    assert result["action"] == "slightly_loosen"
    assert (tmp_path / "audit_log.jsonl").exists()
    assert (tmp_path / "event_memory.jsonl").exists()
