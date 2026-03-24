"""Research-cycle service wrappers around the orchestrator."""

from __future__ import annotations

from typing import Any

from app.services.common import provider_override_for_source, resolve_symbols
from quanter_swarm.orchestrator.root_agent import RootAgent


def run_research_cycle(
    *,
    source: str = "internal_sim",
    symbols: list[str] | None = None,
    scenario: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    normalized_symbols = resolve_symbols(symbols)
    return RootAgent().run_batch_sync(
        symbols=normalized_symbols,
        scenario=scenario,
        provider_override=provider_override_for_source(source),
    )
