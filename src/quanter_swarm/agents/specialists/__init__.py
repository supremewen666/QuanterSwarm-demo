"""Stable specialist exports."""

from __future__ import annotations

from importlib import import_module

_EXPORTS = {
    "BaseSpecialist": ("quanter_swarm.agents.specialists.base_specialist", "BaseSpecialist"),
    "DataFetchSpecialist": ("quanter_swarm.agents.specialists.data_fetch_specialist", "DataFetchSpecialist"),
    "FeatureEngineeringSpecialist": (
        "quanter_swarm.agents.specialists.feature_engineering_specialist",
        "FeatureEngineeringSpecialist",
    ),
    "MacroEventSpecialist": ("quanter_swarm.agents.specialists.macro_event_specialist", "MacroEventSpecialist"),
    "MemoryCompressionSpecialist": (
        "quanter_swarm.agents.specialists.memory_compression_specialist",
        "MemoryCompressionSpecialist",
    ),
    "RiskSpecialist": ("quanter_swarm.agents.specialists.risk_specialist", "RiskSpecialist"),
    "SentimentSpecialist": ("quanter_swarm.agents.specialists.sentiment_specialist", "SentimentSpecialist"),
}

__all__ = sorted(_EXPORTS)


def __getattr__(name: str):
    if name not in _EXPORTS:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    module_name, attribute = _EXPORTS[name]
    return getattr(import_module(module_name), attribute)


def __dir__() -> list[str]:
    return sorted(set(globals()) | set(__all__))
