"""External adapter helpers."""

from __future__ import annotations

from importlib import import_module

_EXPORTS = {
    "AlpacaDashboardSource": (
        "quanter_swarm.adapters.external.alpaca_dashboard_source",
        "AlpacaDashboardSource",
    ),
    "InternalSimSource": (
        "quanter_swarm.adapters.external.internal_sim_source",
        "InternalSimSource",
    ),
}

__all__ = sorted(_EXPORTS)


def __getattr__(name: str):
    if name not in _EXPORTS:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    module_name, attribute = _EXPORTS[name]
    return getattr(import_module(module_name), attribute)


def __dir__() -> list[str]:
    return sorted(set(globals()) | set(__all__))
