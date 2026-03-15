"""Routing decisions."""

from __future__ import annotations

from typing import Any


class RouterAgent:
    def route(self, regime: str, router_config: dict[str, Any], regimes_config: dict[str, Any]) -> dict[str, Any]:
        configured = regimes_config.get("regimes", {}).get(regime, {})
        leaders = list(configured.get("leaders", []))

        if not leaders:
            fallback = router_config.get("router", {}).get("default_regime", "sideways")
            leaders = list(regimes_config.get("regimes", {}).get(fallback, {}).get("leaders", []))

        return {
            "regime": regime,
            "leaders": leaders,
            "token_budget": router_config.get("router", {}).get("token_budget", "medium"),
        }
