"""Monitoring and observability helpers."""

from __future__ import annotations

from importlib import import_module

_EXPORTS = {
    "build_cycle_metrics": ("quanter_swarm.services.monitoring.metrics", "build_cycle_metrics"),
    "build_monitoring_from_report_dir": (
        "quanter_swarm.services.monitoring.evaluation",
        "build_monitoring_from_report_dir",
    ),
    "build_monitoring_snapshot": ("quanter_swarm.services.monitoring.evaluation", "build_monitoring_snapshot"),
    "build_runtime_monitoring_snapshot": (
        "quanter_swarm.services.monitoring.runtime_metrics",
        "build_runtime_monitoring_snapshot",
    ),
    "estimate_token_cost": ("quanter_swarm.services.monitoring.metrics", "estimate_token_cost"),
}

__all__ = sorted(_EXPORTS)


def __getattr__(name: str):
    if name not in _EXPORTS:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    module_name, attribute = _EXPORTS[name]
    return getattr(import_module(module_name), attribute)


def __dir__() -> list[str]:
    return sorted(set(globals()) | set(__all__))
