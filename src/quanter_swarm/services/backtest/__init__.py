"""Backtest and evaluation services."""

from __future__ import annotations

from importlib import import_module

_EXPORTS = {
    "ConfiguredExperimentRunner": ("quanter_swarm.services.backtest.configured_runner", "ConfiguredExperimentRunner"),
    "ExperimentRunner": ("quanter_swarm.services.backtest.experiment_runner", "ExperimentRunner"),
    "compute_summary_metrics": ("quanter_swarm.services.backtest.metrics", "compute_summary_metrics"),
}

__all__ = sorted(_EXPORTS)


def __getattr__(name: str):
    if name not in _EXPORTS:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    module_name, attribute = _EXPORTS[name]
    return getattr(import_module(module_name), attribute)


def __dir__() -> list[str]:
    return sorted(set(globals()) | set(__all__))
