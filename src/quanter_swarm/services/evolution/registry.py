"""Leader parameter registry with versioned defaults."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, cast

_DEFAULT_PARAMETERS = {
    "momentum": {"lookback_window": 20, "trend_strength_scale": 5.0, "volatility_penalty": 0.8},
    "mean_reversion": {"reversal_window": 5, "overshoot_threshold": 0.55, "stop_distance": 0.04},
    "stat_arb": {"pair_distance_threshold": 1.25, "volatility_normalization": 1.0, "max_holding_period": 5},
    "breakout_event": {"event_impact_scaling": 1.0, "breakout_window": 10, "confirmation_volume_threshold": 1.1},
}


class LeaderRegistry:
    def __init__(self, root: Path) -> None:
        self.path = root / "leader_registry.json"

    def _ensure(self) -> dict[str, Any]:
        if self.path.exists():
            return cast(dict[str, Any], json.loads(self.path.read_text(encoding="utf-8")))
        payload: dict[str, Any] = {
            "leaders": {
                name: [
                    {
                        "version": "v1",
                        "supported_regimes": [],
                        "supported_event_clusters": [],
                        "active": True,
                        "parameter_set": params,
                        "parent_version": None,
                        "promotion_reason": "bootstrap_default",
                    }
                ]
                for name, params in _DEFAULT_PARAMETERS.items()
            }
        }
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        return payload

    def get_active(self, leader_name: str, *, regime: str | None = None, event_cluster: str | None = None) -> dict[str, Any]:
        payload = self._ensure()
        leaders_payload = cast(dict[str, list[dict[str, Any]]], payload.get("leaders", {}))
        versions = leaders_payload.get(leader_name, [])
        for item in versions:
            if not item.get("active"):
                continue
            supported_regimes = item.get("supported_regimes") or []
            supported_clusters = item.get("supported_event_clusters") or []
            if supported_regimes and regime and regime not in supported_regimes:
                continue
            if supported_clusters and event_cluster and event_cluster not in supported_clusters:
                continue
            return dict(item)
        return {
            "version": "v1",
            "parameter_set": dict(_DEFAULT_PARAMETERS.get(leader_name, {})),
            "supported_regimes": [],
            "supported_event_clusters": [],
        }

    def promote(
        self,
        leader_name: str,
        *,
        version: str,
        parameter_set: dict[str, Any],
        supported_regimes: list[str] | None = None,
        supported_event_clusters: list[str] | None = None,
        parent_version: str | None = None,
        promotion_reason: str = "manual_promotion",
    ) -> dict[str, Any]:
        payload = self._ensure()
        leaders_payload = cast(dict[str, list[dict[str, Any]]], payload.setdefault("leaders", {}))
        versions = list(leaders_payload.get(leader_name, []))
        for item in versions:
            item["active"] = False

        entry = {
            "version": version,
            "supported_regimes": list(supported_regimes or []),
            "supported_event_clusters": list(supported_event_clusters or []),
            "active": True,
            "parameter_set": dict(parameter_set),
            "parent_version": parent_version,
            "promotion_reason": promotion_reason,
        }
        versions.append(entry)
        leaders_payload[leader_name] = versions
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        return dict(entry)
