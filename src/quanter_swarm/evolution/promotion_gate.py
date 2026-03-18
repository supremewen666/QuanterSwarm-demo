"""Bounded promotion checks for evolution proposals."""

from __future__ import annotations

from typing import Any


class PromotionGate:
    def __init__(self, *, min_observations: int = 20, manual_approval_only: bool = True) -> None:
        self.min_observations = min_observations
        self.manual_approval_only = manual_approval_only

    def evaluate(self, proposal: dict[str, Any]) -> dict[str, Any]:
        evidence = proposal.get("evidence", {})
        sample_count = int(evidence.get("sample_count", 0))
        improved = float(evidence.get("posterior_lift", 0.0)) > 0
        robust = bool(evidence.get("regime_robust", sample_count >= self.min_observations))
        approved = False
        reason = "manual_review_required" if self.manual_approval_only else "rejected"
        if not self.manual_approval_only and sample_count >= self.min_observations and improved and robust:
            approved = True
            reason = "approved"
        elif sample_count < self.min_observations:
            reason = "insufficient_observations"
        elif not improved:
            reason = "no_posterior_improvement"
        elif not robust:
            reason = "regime_robustness_failed"
        return {"approved": approved, "reason": reason, "manual_review_required": self.manual_approval_only}
