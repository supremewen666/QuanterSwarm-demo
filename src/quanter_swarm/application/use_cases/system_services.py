"""System-service use cases separated from the agent hierarchy."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from quanter_swarm.application.use_cases.common import provider_override
from quanter_swarm.core.runtime.config import load_settings
from quanter_swarm.services.data import available_providers
from quanter_swarm.services.data.provider_factory import (
    build_provider_from_config,
    describe_provider_config,
)
from quanter_swarm.services.evolution import EvolutionManager
from quanter_swarm.services.risk.guardrail import assess_guardrails


@dataclass(slots=True)
class GetProviderTopology:
    """Expose configured provider topology as an application-layer use case."""

    def execute(self) -> dict[str, Any]:
        settings = load_settings()
        provider = build_provider_from_config(settings.data_provider)
        return {
            "available": available_providers(),
            "configured": describe_provider_config(settings.data_provider, provider),
        }


@dataclass(slots=True)
class FetchFundamentalsBatch:
    """Fetch batched fundamentals through the application layer."""

    def execute(self, *, symbols: list[str], data_provider: str | None = None) -> dict[str, Any]:
        provider_config = provider_override(data_provider) or {}
        provider = build_provider_from_config(provider_config)
        return {
            "provider": getattr(provider, "data_source", provider.__class__.__name__),
            "results": provider.get_fundamentals_batch(symbols),
        }


@dataclass(slots=True)
class FetchMacroBatch:
    """Fetch batched macro payloads through the application layer."""

    def execute(self, *, symbols: list[str], data_provider: str | None = None) -> dict[str, Any]:
        provider_config = provider_override(data_provider) or {}
        provider = build_provider_from_config(provider_config)
        return {
            "provider": getattr(provider, "data_source", provider.__class__.__name__),
            "results": provider.get_macro_batch(symbols),
        }


@dataclass(slots=True)
class RiskPrecheck:
    """Evaluate a risk payload through the application layer."""

    def execute(
        self,
        *,
        risk_report: dict[str, Any] | None = None,
        warnings: list[str] | None = None,
    ) -> dict[str, Any]:
        payload = dict(risk_report or {})
        if warnings is not None:
            payload["warnings"] = list(warnings)
        return assess_guardrails(payload)


@dataclass(slots=True)
class PromoteLeaderVersion:
    """Promote a leader parameter version through the application layer."""

    def execute(
        self,
        *,
        leader_name: str,
        parameter_version: str,
        parameter_set: dict[str, Any],
        evidence: dict[str, Any],
        supported_regimes: list[str] | None = None,
        supported_event_clusters: list[str] | None = None,
        parent_version: str | None = None,
        promotion_reason: str = "manual_promotion",
        approve: bool = False,
        root: str | None = None,
        config: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        settings = load_settings()
        evolution_root = Path(root) if root is not None else settings.data_dir / "evolution"
        manager = EvolutionManager(root=evolution_root, config=config)
        proposal = {
            "leader": leader_name,
            "parameter_version": parameter_version,
            "evidence": evidence,
        }
        gate = manager.promotion_gate.evaluate(proposal)
        promoted = gate["approved"] or (approve and gate["reason"] == "manual_review_required")
        promoted_entry: dict[str, Any] | None = None
        if promoted:
            promoted_entry = manager.registry.promote(
                leader_name,
                version=parameter_version,
                parameter_set=parameter_set,
                supported_regimes=supported_regimes,
                supported_event_clusters=supported_event_clusters,
                parent_version=parent_version,
                promotion_reason=promotion_reason,
            )

        manager.audit_log.write(
            {
                "recorded_at": datetime.now(tz=UTC).isoformat(),
                "action": "promote" if promoted else "proposal_logged",
                "leader": leader_name,
                "parameter_version": parameter_version,
                "promotion_reason": promotion_reason,
                "gate": gate,
                "manual_override": approve,
            }
        )
        return {
            "leader": leader_name,
            "parameter_version": parameter_version,
            "gate": gate,
            "promoted": promoted,
            "review_required": bool(gate["manual_review_required"] and not gate["approved"]),
            "active_version": promoted_entry["version"] if promoted_entry else None,
        }
