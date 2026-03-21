"""Persistent meta-learning manager for weak-prior evolution."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from quanter_swarm.evolution.audit import EvolutionAuditLog
from quanter_swarm.evolution.event_memory import EventMemoryStore
from quanter_swarm.evolution.priors import compute_weak_priors
from quanter_swarm.evolution.promotion_gate import PromotionGate
from quanter_swarm.evolution.registry import LeaderRegistry


class EvolutionManager:
    def __init__(self, *, root: Path, config: dict[str, Any] | None = None) -> None:
        resolved = (config or {}).get("evolution", config or {})
        self.config = resolved
        self.root = root
        self.registry = LeaderRegistry(root)
        self.event_memory = EventMemoryStore(root)
        self.audit_log = EvolutionAuditLog(root)
        self.promotion_gate = PromotionGate(
            min_observations=int(resolved.get("min_observations", 20)),
            manual_approval_only=bool(resolved.get("manual_approval_only", True)),
            min_posterior_lift=float(resolved.get("min_posterior_lift", 0.02)),
            min_confidence=float(resolved.get("min_confidence", 0.55)),
            max_drawdown_for_promotion=float(resolved.get("max_drawdown_for_promotion", 0.2)),
            rollback_drawdown_threshold=float(resolved.get("rollback_drawdown_threshold", 0.25)),
            rollback_sharpe_delta=float(resolved.get("rollback_sharpe_delta", -0.5)),
        )

    def get_active_parameters(self, leader_name: str, *, regime: str | None = None, event_cluster: str | None = None) -> dict[str, Any]:
        return self.registry.get_active(leader_name, regime=regime, event_cluster=event_cluster)

    def build_priors(self, event_payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
        if not self.config.get("weak_prior_enabled", True):
            return {}
        top_k = int(self.config.get("top_k_similar_events", 5))
        similar = self.event_memory.find_similar(event_payload, limit=top_k)
        return compute_weak_priors(
            similar,
            target_regime=str(event_payload.get("regime", "")),
            lambda_scale=float(self.config.get("prior_lambda", 1.0)),
        )

    def evolve(
        self,
        ranked_signals: list[dict[str, Any]],
        *,
        current_threshold: float,
        event_payload: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        if not ranked_signals:
            summary = {"threshold": current_threshold, "action": "hold", "proposal": None}
            self.audit_log.write({"action": "hold", "reason": "no_ranked_signals"})
            return summary

        top = ranked_signals[0]
        posterior_lift = round(float(top.get("posterior_score", top.get("score", 0.0))) - float(top.get("score", 0.0)), 4)
        proposal = {
            "leader": top.get("leader"),
            "parameter_version": top.get("parameter_version"),
            "evidence": {
                "posterior_lift": posterior_lift,
                "sample_count": int(top.get("prior_sample_count", 0)),
                "regime_robust": float(top.get("prior_confidence", 0.0)) >= 0.5,
                "confidence": float(top.get("confidence", top.get("prior_confidence", 0.0))),
                "drawdown": abs(float(top.get("drawdown", 0.0))),
            },
        }
        gate = self.promotion_gate.evaluate(proposal)
        rollback = self.promotion_gate.evaluate_rollback(
            {
                "drawdown": float(top.get("drawdown", 0.0)),
                "sharpe_delta": float(top.get("sharpe_delta", 0.0)),
            }
        )
        if float(top.get("composite_rank_score", 0.0)) > 0.65:
            threshold = round(max(0.45, current_threshold - 0.02), 4)
            action = "slightly_loosen"
        elif float(top.get("composite_rank_score", 0.0)) < 0.45:
            threshold = round(min(0.6, current_threshold + 0.02), 4)
            action = "slightly_tighten"
        else:
            threshold = current_threshold
            action = "hold"
        if rollback["should_rollback"]:
            action = "rollback"
            threshold = round(min(0.6, current_threshold + 0.03), 4)
        audit_payload = {
            "recorded_at": datetime.now(tz=UTC).isoformat(),
            "action": action if gate["approved"] else "proposal_logged",
            "threshold_before": current_threshold,
            "threshold_after": threshold,
            "proposal": proposal,
            "gate": gate,
            "rollback": rollback,
        }
        self.audit_log.write(audit_payload)
        if event_payload:
            self.event_memory.append(
                {
                    **event_payload,
                    "recorded_at": datetime.now(tz=UTC).isoformat(),
                    "selected_leader": top.get("leader"),
                    "realized_outcome": round(float(top.get("composite_rank_score", 0.0)) - 0.5, 4),
                    "confidence": float(top.get("confidence", 0.5)),
                    "sample_count": max(1, int(top.get("prior_sample_count", 1))),
                }
            )
        return {
            "threshold": threshold,
            "action": action,
            "gate": gate,
            "rollback": rollback,
            "proposal": proposal,
            "top_posterior_leader": top.get("leader"),
        }
