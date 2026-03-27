"""Shared helpers for task-oriented CLI services."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from quanter_swarm.core.runtime.config import load_settings
from quanter_swarm.errors import DataProviderError

DEFAULT_CAPITAL = 100_000.0
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8000
INTERNAL_SIM_SOURCE = "internal_sim"
INTERNAL_PROVIDER_OVERRIDE = {"provider": "deterministic"}


def normalize_source(source: str) -> str:
    normalized = source.strip().lower()
    if normalized in {"", "internal", "internal_sim", "deterministic", "default"}:
        return INTERNAL_SIM_SOURCE
    raise DataProviderError(
        f"Unsupported source '{source}'. Only internal_sim is allowed for research, replay, and backtest flows."
    )


def provider_override_for_source(source: str) -> dict[str, str]:
    normalized = normalize_source(source)
    if normalized != INTERNAL_SIM_SOURCE:
        raise DataProviderError(f"Unsupported source '{source}'.")
    return dict(INTERNAL_PROVIDER_OVERRIDE)


def resolve_symbols(symbols: list[str] | None = None) -> list[str]:
    if symbols:
        return [symbol.upper() for symbol in symbols]
    return [symbol.upper() for symbol in load_settings().default_symbols]


def utc_now_iso() -> str:
    return datetime.now(tz=UTC).isoformat()


def ensure_directory(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def safe_fingerprint(report: dict[str, Any]) -> str:
    config = report.get("config_provenance", {})
    return str(config.get("fingerprint", "unknown"))


def write_output_payload(payload: dict[str, Any], output_path: str | None = None) -> str:
    rendered = json.dumps(payload, indent=2, ensure_ascii=False)
    if output_path:
        destination = Path(output_path)
        ensure_directory(destination.parent)
        destination.write_text(rendered, encoding="utf-8")
    return rendered
