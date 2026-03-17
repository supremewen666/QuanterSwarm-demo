"""Config helpers."""

from __future__ import annotations

import os
from hashlib import sha256
from pathlib import Path
from typing import Any

from quanter_swarm.config.defaults import (
    DEFAULT_BACKTEST_WINDOW,
    DEFAULT_MAX_SPECIALISTS_PER_CYCLE,
    DEFAULT_RISK_THRESHOLDS,
    DEFAULT_SYMBOLS,
    DEFAULT_TOKEN_BUDGET,
)
from quanter_swarm.config.settings import Settings
from quanter_swarm.errors import DataProviderError, RiskGuardrailError, RouterError

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
        raise DataProviderError(f"Config at {path} must be a mapping.")
    return payload


def load_settings() -> Settings:
    config_dir = Path(os.getenv("CONFIG_DIR", "configs"))
    app_config = load_yaml(config_dir / "app.yaml").get("app", {})
    configured_symbols = app_config.get("default_symbols", DEFAULT_SYMBOLS)
    default_symbols_raw = os.getenv(
        "DEFAULT_SYMBOLS",
        ",".join(configured_symbols if isinstance(configured_symbols, (list, tuple)) else DEFAULT_SYMBOLS),
    )
    configured_risk_thresholds = app_config.get("risk_thresholds", {})
    configured_backtest_window = app_config.get("backtest_window", {})
    return Settings(
        environment=os.getenv("APP_ENV", app_config.get("environment", "dev")),
        execution_mode=os.getenv("EXECUTION_MODE", app_config.get("execution_mode", "paper")),
        data_dir=Path(os.getenv("DATA_DIR", "data")),
        config_dir=config_dir,
        default_symbols=[symbol.strip() for symbol in default_symbols_raw.split(",") if symbol.strip()],
        token_budget=os.getenv("TOKEN_BUDGET", app_config.get("token_budget", DEFAULT_TOKEN_BUDGET)),
        max_specialists_per_cycle=int(
            os.getenv(
                "MAX_SPECIALISTS_PER_CYCLE",
                app_config.get("max_specialists_per_cycle", DEFAULT_MAX_SPECIALISTS_PER_CYCLE),
            )
        ),
        risk_thresholds={**DEFAULT_RISK_THRESHOLDS, **configured_risk_thresholds},
        backtest_window={**DEFAULT_BACKTEST_WINDOW, **configured_backtest_window},
    )


def load_runtime_configs(config_dir: Path) -> dict[str, dict[str, Any]]:
    names = (
        "app.yaml",
        "router.yaml",
        "regimes.yaml",
        "risk.yaml",
        "portfolio.yaml",
        "execution.yaml",
        "paper_broker.yaml",
        "ranking.yaml",
        "evolution.yaml",
    )
    return {name: load_yaml(config_dir / name) for name in names}


def config_provenance(configs: dict[str, dict[str, Any]]) -> dict[str, Any]:
    payload = {name: configs[name] for name in sorted(configs)}
    fingerprint = sha256(str(payload).encode("utf-8")).hexdigest()[:16]
    return {
        "files": sorted(configs.keys()),
        "fingerprint": fingerprint,
        "router": payload.get("router.yaml", {}),
        "regimes": payload.get("regimes.yaml", {}),
        "risk": payload.get("risk.yaml", {}),
        "portfolio": payload.get("portfolio.yaml", {}),
    }


def validate_config_consistency(config_dir: Path) -> None:
    configs = load_runtime_configs(config_dir)
    router = configs["router.yaml"]
    regimes = configs["regimes.yaml"].get("regimes", {})
    risk = configs["risk.yaml"].get("risk", {})
    execution = configs["execution.yaml"].get("execution", {})
    portfolio = configs["portfolio.yaml"].get("portfolio", {})
    known_leaders = {path.stem for path in (config_dir / "leaders").glob("*.yaml")}

    default_regime = router.get("default_regime", "sideways")
    if default_regime not in regimes:
        raise RouterError(f"router.default_regime '{default_regime}' not found in regimes.yaml")

    referenced = {
        leader
        for leaders in router.get("routing", {}).values()
        for leader in leaders
    } | {
        leader
        for regime_cfg in regimes.values()
        for leader in regime_cfg.get("leaders", [])
    }
    unknown = sorted(referenced - known_leaders)
    if unknown:
        raise RouterError(f"Unknown leaders referenced by config: {','.join(unknown)}")

    if execution.get("mode") == "live" or execution.get("allow_live") is True:
        raise RiskGuardrailError("Dangerous config: live execution is not allowed by default.")

    max_single = float(risk.get("max_single_weight", 0.0))
    if not (0.0 < max_single <= 0.35):
        raise RiskGuardrailError("risk.max_single_weight must be within (0, 0.35].")

    cash_buffer = float(portfolio.get("cash_buffer", 0.0))
    if not (0.0 <= cash_buffer <= 0.9):
        raise RiskGuardrailError("portfolio.cash_buffer must be within [0, 0.9].")
