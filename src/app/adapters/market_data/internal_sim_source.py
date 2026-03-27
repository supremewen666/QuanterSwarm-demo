"""Internal simulation source used by CLI and dashboard flows."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from quanter_swarm.application import RunBatchResearch
from quanter_swarm.core.runtime.config import load_settings
from quanter_swarm.services.data.base import BaseDataProvider, DeterministicDataProvider
from quanter_swarm.services.snapshot.schemas import record_hash


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
        return RunBatchResearch().execute(symbols=normalized, data_provider=self.provider_override()["provider"])

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
