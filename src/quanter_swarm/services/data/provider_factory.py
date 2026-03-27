"""Provider construction from app config and request overrides."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

from quanter_swarm.errors import DataProviderError
from quanter_swarm.services.data import create_provider
from quanter_swarm.services.data.base import BaseDataProvider, DeterministicDataProvider

if TYPE_CHECKING:
    from quanter_swarm.services.data.live_providers import (
        AlfredVintageMacroProvider,
        CompositeMarketDataProvider,
        FmpSharesFloatProvider,
        FredMacroProvider,
        SecFilingsProvider,
        SecXbrlFactsProvider,
    )


def build_provider_from_config(config: dict[str, Any] | None) -> BaseDataProvider:
    payload = dict(config or {})
    provider_name = str(payload.get("provider", "deterministic")).strip().lower()
    if provider_name in {"", "deterministic", "default"}:
        return DeterministicDataProvider()
    if provider_name in {"polygon_market_data", "fmp_market_data", "file"}:
        kwargs = dict(payload.get("provider_kwargs", {}))
        return cast(BaseDataProvider, create_provider(provider_name, **kwargs))
    if provider_name == "composite":
        from quanter_swarm.services.data import CompositeMarketDataProvider

        if CompositeMarketDataProvider is None:
            raise DataProviderError("Composite provider is unavailable because live provider dependencies are missing.")
        composite_provider_cls = cast(type["CompositeMarketDataProvider"], CompositeMarketDataProvider)

        market_name = str(payload.get("market_provider", "deterministic")).strip().lower()
        market_kwargs = dict(payload.get("market_provider_kwargs", {}))
        market_provider = (
            DeterministicDataProvider()
            if market_name in {"", "deterministic", "default"}
            else create_provider(market_name, **market_kwargs)
        )
        auxiliary = payload.get("auxiliary_providers", {})

        def _maybe(name: str) -> BaseDataProvider | None:
            item = auxiliary.get(name)
            if not item or not item.get("enabled", False):
                return None
            provider = str(item.get("provider", "")).strip().lower()
            if not provider:
                return None
            return cast(BaseDataProvider, create_provider(provider, **dict(item.get("provider_kwargs", {}))))

        composite_provider = composite_provider_cls(
            market_provider=market_provider,
            filings_provider=cast("SecFilingsProvider | None", _maybe("filings")),
            xbrl_provider=cast("SecXbrlFactsProvider | None", _maybe("xbrl")),
            shares_float_provider=cast("FmpSharesFloatProvider | None", _maybe("shares_float")),
            macro_provider=cast("FredMacroProvider | None", _maybe("macro")),
            vintage_macro_provider=cast("AlfredVintageMacroProvider | None", _maybe("macro_vintages")),
        )
        return cast(BaseDataProvider, composite_provider)
    raise DataProviderError(f"Unsupported configured data provider '{provider_name}'.")


def describe_provider_config(config: dict[str, Any] | None, provider: BaseDataProvider | None = None) -> dict[str, Any]:
    payload = dict(config or {})
    summary = {
        "provider": payload.get("provider", getattr(provider, "data_source", "deterministic")),
        "provider_type": getattr(provider, "source_type", "derived") if provider is not None else "derived",
    }
    if payload.get("provider") == "composite":
        summary["market_provider"] = payload.get("market_provider", "deterministic")
        summary["auxiliary_providers"] = {
            name: {
                "enabled": bool(item.get("enabled", False)),
                "provider": item.get("provider"),
            }
            for name, item in dict(payload.get("auxiliary_providers", {})).items()
        }
    return summary
