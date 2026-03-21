"""Bounded promotion checks for evolution proposals."""

from __future__ import annotations

from typing import Any


class PromotionGate:
    def __init__(
        self,
        *,
        min_observations: int = 20,
        manual_approval_only: bool = True,
        min_posterior_lift: float = 0.02,
        min_confidence: float = 0.55,
        max_drawdown_for_promotion: float = 0.2,
        rollback_drawdown_threshold: float = 0.25,
        rollback_sharpe_delta: float = -0.5,
    ) -> None:
        self.min_observations = min_observations
        self.manual_approval_only = manual_approval_only
        self.min_posterior_lift = min_posterior_lift
        self.min_confidence = min_confidence
        self.max_drawdown_for_promotion = max_drawdown_for_promotion
        self.rollback_drawdown_threshold = rollback_drawdown_threshold
        self.rollback_sharpe_delta = rollback_sharpe_delta

    def evaluate(self, proposal: dict[str, Any]) -> dict[str, Any]:
        evidence = proposal.get("evidence", {})
        sample_count = int(evidence.get("sample_count", 0))
        posterior_lift = float(evidence.get("posterior_lift", 0.0))
        confidence = float(evidence.get("confidence", 0.0))
        drawdown = abs(float(evidence.get("drawdown", 0.0)))
        improved = posterior_lift >= self.min_posterior_lift
        robust = bool(evidence.get("regime_robust", sample_count >= self.min_observations))
        stable_confidence = confidence >= self.min_confidence
        acceptable_drawdown = drawdown <= self.max_drawdown_for_promotion
        statistical_filters = {
            "sample_count_ok": sample_count >= self.min_observations,
            "posterior_lift_ok": improved,
            "confidence_ok": stable_confidence,
            "drawdown_ok": acceptable_drawdown,
            "regime_robust": robust,
        }
        approved = False
        reason = "manual_review_required" if self.manual_approval_only else "rejected"
        if (
            not self.manual_approval_only
            and sample_count >= self.min_observations
            and improved
            and robust
            and stable_confidence
            and acceptable_drawdown
        ):
            approved = True
            reason = "approved"
        elif sample_count < self.min_observations:
            reason = "insufficient_observations"
        elif posterior_lift < self.min_posterior_lift:
            reason = "no_posterior_improvement"
        elif not stable_confidence:
            reason = "confidence_too_low"
        elif not acceptable_drawdown:
            reason = "drawdown_too_high"
        elif not robust:
            reason = "regime_robustness_failed"
        return {
            "approved": approved,
            "reason": reason,
            "manual_review_required": self.manual_approval_only,
            "thresholds": {
                "min_observations": self.min_observations,
                "min_posterior_lift": self.min_posterior_lift,
                "min_confidence": self.min_confidence,
                "max_drawdown_for_promotion": self.max_drawdown_for_promotion,
            },
            "statistical_filters": statistical_filters,
        }

    def evaluate_rollback(self, performance_summary: dict[str, Any]) -> dict[str, Any]:
        drawdown = abs(float(performance_summary.get("drawdown", 0.0)))
        sharpe_delta = float(performance_summary.get("sharpe_delta", 0.0))
        should_rollback = drawdown >= self.rollback_drawdown_threshold or sharpe_delta <= self.rollback_sharpe_delta
        if drawdown >= self.rollback_drawdown_threshold:
            reason = "drawdown_breach"
        elif sharpe_delta <= self.rollback_sharpe_delta:
            reason = "performance_regression"
        else:
            reason = "stable"
        return {
            "should_rollback": should_rollback,
            "reason": reason,
            "thresholds": {
                "rollback_drawdown_threshold": self.rollback_drawdown_threshold,
                "rollback_sharpe_delta": self.rollback_sharpe_delta,
            },
        }
