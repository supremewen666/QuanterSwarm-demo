"""Config helpers."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from quanter_swarm.settings import Settings

try:
    import yaml
except ModuleNotFoundError:  # pragma: no cover - exercised in lightweight environments
    yaml = None


def _coerce_scalar(raw: str) -> Any:
    value = raw.strip().strip("'").strip('"')
    if value in {"true", "false"}:
        return value == "true"
    try:
        if "." in value:
            return float(value)
        return int(value)
    except ValueError:
        return value


def _fallback_yaml_load(text: str) -> dict[str, Any]:
    root: dict[str, Any] = {}
    stack: list[tuple[int, dict[str, Any]]] = [(-1, root)]

    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        indent = len(line) - len(line.lstrip(" "))
        while len(stack) > 1 and indent <= stack[-1][0]:
            stack.pop()

        current = stack[-1][1]
        key, _, remainder = stripped.partition(":")
        key = key.strip()
        remainder = remainder.strip()

        if remainder.startswith("[") and remainder.endswith("]"):
            inner = remainder[1:-1].strip()
            current[key] = [item.strip() for item in inner.split(",") if item.strip()]
            continue

        if remainder:
            current[key] = _coerce_scalar(remainder)
            continue

        current[key] = {}
        stack.append((indent, current[key]))

    return root


def load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as handle:
        text = handle.read()
    if yaml is not None:
        payload = yaml.safe_load(text) or {}
    else:
        payload = _fallback_yaml_load(text)
    if not isinstance(payload, dict):
        raise ValueError(f"Config at {path} must be a mapping.")
    return payload


def load_settings() -> Settings:
    config_dir = Path(os.getenv("CONFIG_DIR", "configs"))
    app_config = load_yaml(config_dir / "app.yaml").get("app", {})
    default_symbols = os.getenv("DEFAULT_SYMBOLS", "AAPL,MSFT,NVDA")
    return Settings(
        environment=os.getenv("APP_ENV", app_config.get("environment", "dev")),
        execution_mode=os.getenv("EXECUTION_MODE", app_config.get("execution_mode", "paper")),
        data_dir=Path(os.getenv("DATA_DIR", "data")),
        config_dir=config_dir,
        default_symbols=[symbol.strip() for symbol in default_symbols.split(",") if symbol.strip()],
    )
