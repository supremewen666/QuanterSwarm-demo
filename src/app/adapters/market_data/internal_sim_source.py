"""Internal simulation source used by CLI and dashboard flows."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from quanter_swarm.data.base import BaseDataProvider, DeterministicDataProvider
from quanter_swarm.data.schemas import record_hash
from quanter_swarm.orchestrator.root_agent import RootAgent
from quanter_swarm.utils.config import load_settings


@dataclass(slots=True)
class InternalSimSource:
    """Stable internal source wrapper around the deterministic provider."""

    seed: int = 7
    provider: BaseDataProvider = field(default_factory=DeterministicDataProvider)

    def resolve_symbols(self, symbols: list[str] | None = None) -> list[str]:
        if symbols:
            return [symbol.upper() for symbol in symbols]
        return [symbol.upper() for symbol in load_settings().default_symbols]

    def provider_override(self) -> dict[str, str]:
        return {"provider": "deterministic"}

    def fetch_reports(self, symbols: list[str] | None = None) -> list[dict[str, Any]]:
        normalized = self.resolve_symbols(symbols)
        return RootAgent().run_batch_sync(symbols=normalized, provider_override=self.provider_override())

    def snapshot_universe(self, symbols: list[str] | None = None) -> dict[str, dict[str, Any]]:
        normalized = self.resolve_symbols(symbols)
        snapshots = self.provider.get_latest_prices(normalized)
        return {
            symbol: {
                **payload,
                "symbol": symbol,
                "snapshot_id": record_hash({"symbol": symbol, "ts": payload.get("ts"), "source": "internal_sim"}),
                "source": "internal_sim",
            }
            for symbol, payload in snapshots.items()
        }
