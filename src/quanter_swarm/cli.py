"""Shared CLI helpers for repo and skill entrypoints."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from quanter_swarm.application import RunResearchCycle
from quanter_swarm.contracts import FinalReportContract
from quanter_swarm.core.runtime.config import load_yaml, validate_config_consistency
from quanter_swarm.core.runtime.logging import configure_logging
from quanter_swarm.errors import QuanterSwarmError
from quanter_swarm.services.reporting.markdown_report import render_markdown_report

REQUIRED_CONFIGS = (
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


def build_cycle_parser(description: str, default_format: str = "json", default_output: str | None = None) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("symbol", nargs="?", default=None, help="Ticker symbol to analyze.")
    parser.add_argument("--format", choices=("json", "markdown"), default=default_format, help="Output format.")
    parser.add_argument("--output", default=default_output, help="Optional file path for rendered output.")
    return parser


def render_report(report: dict[str, Any], output_format: str) -> str:
    if output_format == "markdown":
        return render_markdown_report(report)
    return json.dumps(report, indent=2, ensure_ascii=False)


def emit_report(symbol: str | None, output_format: str, output_path: str | None) -> str:
    configure_logging()
    report = RunResearchCycle().execute(symbol=symbol or "AAPL")
    report = FinalReportContract.model_validate(report).model_dump()
    rendered = render_report(report, output_format)
    if output_path:
        destination = Path(output_path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(rendered, encoding="utf-8")
        return str(destination)
    return rendered


def validate_repo_configs(config_dir: Path | None = None) -> dict[str, Any]:
    resolved_dir = config_dir or Path("configs")
    missing = [name for name in REQUIRED_CONFIGS if not (resolved_dir / name).exists()]
    if missing:
        return {"ok": False, "missing": missing, "invalid": [], "unknown_leaders": [], "config_errors": []}

    invalid: list[str] = []
    for name in REQUIRED_CONFIGS:
        try:
            load_yaml(resolved_dir / name)
        except QuanterSwarmError:
            invalid.append(name)

    router = load_yaml(resolved_dir / "router.yaml")
    regimes = load_yaml(resolved_dir / "regimes.yaml").get("regimes", {})
    portfolio = load_yaml(resolved_dir / "portfolio.yaml").get("portfolio", {})
    known_leaders = {path.stem for path in (resolved_dir / "leaders").glob("*.yaml")}
    referenced = {
        leader
        for leaders in router.get("routing", {}).values()
        for leader in leaders
    } | {
        leader
        for config in regimes.values()
        for leader in config.get("leaders", [])
    }
    unknown_leaders = sorted(referenced - known_leaders)
    config_errors: list[str] = []
    if router.get("low_confidence_policy") not in {"fallback", "no_trade", None}:
        config_errors.append("router.low_confidence_policy must be fallback|no_trade")
    allocation_mode = portfolio.get("allocation_mode", "simple")
    if allocation_mode not in {"simple", "volatility_aware", "correlation_aware"}:
        config_errors.append("portfolio.allocation_mode must be simple|volatility_aware|correlation_aware")
    try:
        validate_config_consistency(resolved_dir)
    except QuanterSwarmError as exc:
        config_errors.append(str(exc))
    return {
        "ok": not missing and not invalid and not unknown_leaders and not config_errors,
        "missing": missing,
        "invalid": invalid,
        "unknown_leaders": unknown_leaders,
        "config_errors": config_errors,
    }
