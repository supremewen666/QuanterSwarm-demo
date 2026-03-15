"""Routing decisions."""

from __future__ import annotations

from typing import Any


class RouterAgent:
    def _resolved_config(self, router_config: dict[str, Any]) -> dict[str, Any]:
        nested = router_config.get("router")
        if isinstance(nested, dict):
            return {**router_config, **nested}
        return router_config

    def route(self, regime: str | dict[str, Any], router_config: dict[str, Any], regimes_config: dict[str, Any]) -> dict[str, Any]:
        resolved = self._resolved_config(router_config)
        regime_label = regime["label"] if isinstance(regime, dict) else regime
        regime_confidence = float(regime.get("confidence", 1.0)) if isinstance(regime, dict) else 1.0
        configured = regimes_config.get("regimes", {}).get(regime_label, {})
        leaders = list(configured.get("leaders", []))
        weights = configured.get("weights", {})
        threshold = float(resolved.get("confidence_threshold", 0.45))
        low_conf_policy = resolved.get("low_confidence_policy", "fallback")
        fallback_regime = resolved.get("default_regime", "sideways")
        selected_reasons: dict[str, str] = {}
        skipped_reasons: dict[str, str] = {}

        if not leaders:
            leaders = list(regimes_config.get("regimes", {}).get(fallback_regime, {}).get("leaders", []))
            for leader in leaders:
                selected_reasons[leader] = f"fallback_from_{regime_label}_to_{fallback_regime}"

        low_confidence = regime_confidence < threshold
        if low_confidence:
            fallback_leaders = list(configured.get("fallback_leaders", leaders[:1]))
            if low_conf_policy == "no_trade":
                for leader in leaders:
                    skipped_reasons[leader] = "low_regime_confidence_no_trade_policy"
                leaders = []
            else:
                filtered = [leader for leader in leaders if leader in fallback_leaders]
                for leader in leaders:
                    if leader in filtered:
                        selected_reasons[leader] = "low_regime_confidence_fallback_leader"
                    else:
                        skipped_reasons[leader] = "removed_by_low_confidence_policy"
                leaders = filtered

        max_active_leaders = resolved.get("max_active_leaders")
        if isinstance(max_active_leaders, int) and max_active_leaders > 0:
            dropped = leaders[max_active_leaders:]
            for leader in dropped:
                skipped_reasons[leader] = "dropped_by_max_active_leaders"
            leaders = leaders[:max_active_leaders]
        for leader in leaders:
            selected_reasons.setdefault(leader, "selected_by_regime_routing")

        leader_weights = {
            leader: round(float(weights.get(leader, 1 / max(1, len(leaders)))), 4)
            for leader in leaders
        }

        return {
            "regime": regime_label,
            "regime_confidence": round(regime_confidence, 2),
            "leaders": leaders,
            "token_budget": resolved.get("token_budget", "medium"),
            "leader_weights": leader_weights,
            "low_confidence_mode": low_confidence,
            "selected_reasons": selected_reasons,
            "skipped_reasons": skipped_reasons,
        }
