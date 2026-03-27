"""Shared helpers for application-layer use cases."""

from __future__ import annotations


def provider_override(data_provider: str | None) -> dict[str, str] | None:
    if not data_provider:
        return None
    return {"provider": data_provider}
