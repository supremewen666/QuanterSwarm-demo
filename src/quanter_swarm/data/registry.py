"""Named provider registry for optional live data integrations."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from quanter_swarm.errors import DataProviderError

ProviderFactory = Callable[..., Any]

_PROVIDERS: dict[str, ProviderFactory] = {}


def register_provider(name: str, factory: ProviderFactory) -> None:
    key = name.strip().lower()
    if not key:
        raise DataProviderError("Provider name must be non-empty.")
    _PROVIDERS[key] = factory


def create_provider(name: str, **kwargs: Any) -> Any:
    key = name.strip().lower()
    try:
        factory = _PROVIDERS[key]
    except KeyError as exc:
        raise DataProviderError(f"Unknown provider '{name}'.") from exc
    return factory(**kwargs)


def available_providers() -> list[str]:
    return sorted(_PROVIDERS)
