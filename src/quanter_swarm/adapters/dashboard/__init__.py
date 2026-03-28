"""Dashboard adapters."""

from __future__ import annotations

from importlib import import_module

__all__ = ["app"]


def __getattr__(name: str):
    if name != "app":
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    return import_module("quanter_swarm.adapters.dashboard.app").app


def __dir__() -> list[str]:
    return sorted(set(globals()) | set(__all__))
