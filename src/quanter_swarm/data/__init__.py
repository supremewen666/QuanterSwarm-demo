"""Data provider interfaces and defaults."""

from typing import Any

from quanter_swarm.data.base import (
    BaseDataProvider,
    DeterministicDataProvider,
    get_default_data_provider,
)
from quanter_swarm.data.cache import FileSnapshotCache, MemorySnapshotCache, SnapshotCache
from quanter_swarm.data.mock_provider import MockDataProvider
from quanter_swarm.data.registry import available_providers, create_provider, register_provider

AlfredVintageMacroProvider: Any
CompanyIRProvider: Any
CompositeMarketDataProvider: Any
FmpMarketDataProvider: Any
FmpSharesFloatProvider: Any
FredMacroProvider: Any
PolygonMarketDataProvider: Any
SecFilingsProvider: Any
SecXbrlFactsProvider: Any
FileDataProvider: Any

try:
    from quanter_swarm.data.live_providers import (
        AlfredVintageMacroProvider as _AlfredVintageMacroProvider,
        CompanyIRProvider as _CompanyIRProvider,
        CompositeMarketDataProvider as _CompositeMarketDataProvider,
        FmpMarketDataProvider as _FmpMarketDataProvider,
        FmpSharesFloatProvider as _FmpSharesFloatProvider,
        FredMacroProvider as _FredMacroProvider,
        PolygonMarketDataProvider as _PolygonMarketDataProvider,
        SecFilingsProvider as _SecFilingsProvider,
        SecXbrlFactsProvider as _SecXbrlFactsProvider,
    )
    AlfredVintageMacroProvider = _AlfredVintageMacroProvider
    CompanyIRProvider = _CompanyIRProvider
    CompositeMarketDataProvider = _CompositeMarketDataProvider
    FmpMarketDataProvider = _FmpMarketDataProvider
    FmpSharesFloatProvider = _FmpSharesFloatProvider
    FredMacroProvider = _FredMacroProvider
    PolygonMarketDataProvider = _PolygonMarketDataProvider
    SecFilingsProvider = _SecFilingsProvider
    SecXbrlFactsProvider = _SecXbrlFactsProvider
except ModuleNotFoundError:  # pragma: no cover - exercised in lightweight environments
    AlfredVintageMacroProvider = None
    CompanyIRProvider = None
    CompositeMarketDataProvider = None
    FmpMarketDataProvider = None
    FmpSharesFloatProvider = None
    FredMacroProvider = None
    PolygonMarketDataProvider = None
    SecFilingsProvider = None
    SecXbrlFactsProvider = None

try:
    from quanter_swarm.data.file_provider import FileDataProvider as _FileDataProvider

    FileDataProvider = _FileDataProvider
except ModuleNotFoundError:  # pragma: no cover - exercised in lightweight environments
    FileDataProvider = None

__all__ = [
    "BaseDataProvider",
    "DeterministicDataProvider",
    "FileSnapshotCache",
    "MemorySnapshotCache",
    "MockDataProvider",
    "SnapshotCache",
    "available_providers",
    "create_provider",
    "get_default_data_provider",
    "register_provider",
]

if FileDataProvider is not None:
    __all__.append("FileDataProvider")

if PolygonMarketDataProvider is not None:
    __all__.extend(
        [
            "FredMacroProvider",
            "FmpMarketDataProvider",
            "FmpSharesFloatProvider",
            "PolygonMarketDataProvider",
            "SecFilingsProvider",
            "SecXbrlFactsProvider",
            "CompanyIRProvider",
            "AlfredVintageMacroProvider",
            "CompositeMarketDataProvider",
        ]
    )
    register_provider("polygon_market_data", PolygonMarketDataProvider)
    register_provider("fmp_market_data", FmpMarketDataProvider)
    register_provider("sec_filings", SecFilingsProvider)
    register_provider("sec_xbrl_facts", SecXbrlFactsProvider)
    register_provider("company_ir", CompanyIRProvider)
    register_provider("fmp_shares_float", FmpSharesFloatProvider)
    register_provider("fred_macro", FredMacroProvider)
    register_provider("alfred_vintage_macro", AlfredVintageMacroProvider)
