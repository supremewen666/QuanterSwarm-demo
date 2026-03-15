"""Routing decisions."""

from __future__ import annotations

from typing import Any


class RouterAgent:
    def _resolved_config(self, router_config: dict[str, Any]) -> dict[str, Any]:
        nested = router_config.get("router")
        if isinstance(nested, dict):
            return {**router_config, **nested}
        return router_config

    def route(self, regime: str, router_config: dict[str, Any], regimes_config: dict[str, Any]) -> dict[str, Any]:
        resolved = self._resolved_config(router_config)
        configured = regimes_config.get("regimes", {}).get(regime, {})
        leaders = list(configured.get("leaders", []))

        if not leaders:
            fallback = resolved.get("default_regime", "sideways")
            leaders = list(regimes_config.get("regimes", {}).get(fallback, {}).get("leaders", []))

        max_active_leaders = resolved.get("max_active_leaders")
        if isinstance(max_active_leaders, int) and max_active_leaders > 0:
            leaders = leaders[:max_active_leaders]

        return {
            "regime": regime,
            "leaders": leaders,
            "token_budget": resolved.get("token_budget", "medium"),
        }
