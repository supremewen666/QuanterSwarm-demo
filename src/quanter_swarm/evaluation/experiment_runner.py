"""Experiment and ablation runner."""

from __future__ import annotations

from pathlib import Path
from time import time
from typing import Any

from quanter_swarm.orchestrator.cycle_manager import CycleManager
from quanter_swarm.storage.file_store import write_json, write_text


def _leader_contribution(report: dict[str, Any]) -> dict[str, float]:
    contribution: dict[str, float] = {}
    for entry in report.get("decision_trace_summary", {}).get("leader_scores", []):
        contribution[entry["leader"]] = round(entry.get("rank_score", 0.0) - entry.get("risk_penalty", 0.0), 4)
    return contribution


def _exposure_summary(report: dict[str, Any]) -> dict[str, float]:
    portfolio = report.get("portfolio_suggestion", {})
    return {
        "gross_exposure": round(float(portfolio.get("gross_exposure", 0.0)), 4),
        "cash_buffer": round(float(portfolio.get("cash_buffer", 1.0)), 4),
        "position_count": len(portfolio.get("positions", [])),
    }


def _build_result_row(name: str, report: dict[str, Any]) -> dict[str, Any]:
    metrics = report.get("evaluation_summary", {}).get("metrics", {})
    return {
        "name": name,
        "regime": report.get("active_regime"),
        "regime_confidence": report.get("regime_confidence", 0.0),
        "annualized_return": metrics.get("annualized_return", 0.0),
        "sharpe": metrics.get("sharpe", 0.0),
        "sortino": metrics.get("sortino", 0.0),
        "max_drawdown": metrics.get("drawdown", 0.0),
        "win_rate": metrics.get("win_rate", 0.0),
        "turnover": metrics.get("turnover_proxy", 0.0),
        "exposure_summary": _exposure_summary(report),
        "strategy_contribution": _leader_contribution(report),
    }


def _render_markdown_summary(payload: dict[str, Any]) -> str:
    rows = payload["results"]
    lines = [
        f"# QuanterSwarm Experiment {payload['experiment_id']}",
        "",
        f"- Symbol: `{payload['symbol']}`",
        f"- Experiment type: `{payload['experiment_type']}`",
        "",
        "## Results",
    ]
    for row in rows:
        lines.extend(
            [
                f"### {row['name']}",
                f"- Regime: `{row['regime']}` (confidence `{row['regime_confidence']}`)",
                f"- Annualized Return: `{row['annualized_return']}`",
                f"- Sharpe / Sortino: `{row['sharpe']}` / `{row['sortino']}`",
                f"- Max Drawdown: `{row['max_drawdown']}`",
                f"- Win Rate: `{row['win_rate']}`",
                f"- Turnover: `{row['turnover']}`",
                f"- Exposure: `{row['exposure_summary']}`",
                f"- Strategy contribution: `{row['strategy_contribution']}`",
                "",
            ]
        )
    return "\n".join(lines).strip()


class ExperimentRunner:
    def __init__(self, data_dir: Path | str = "data/experiments") -> None:
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def run(self, experiment_type: str, symbol: str) -> dict[str, Any]:
        manager = CycleManager()
        scenarios: list[tuple[str, dict[str, Any]]]
        if experiment_type == "router_ablation":
            scenarios = [
                ("routed", {}),
                ("always_on", {"always_on_leaders": True}),
                ("routed_max_1", {"max_active_leaders": 1}),
                ("routed_max_3", {"max_active_leaders": 3}),
            ]
        elif experiment_type == "specialist_ablation":
            scenarios = [
                ("full_specialists", {}),
                ("without_sentiment", {"disable_specialists": {"sentiment": True}}),
                ("without_macro_event", {"disable_specialists": {"macro_event": True}}),
            ]
        elif experiment_type == "allocation_ablation":
            scenarios = [
                ("simple", {"allocation_mode": "simple"}),
                ("volatility_aware", {"allocation_mode": "volatility_aware"}),
                ("correlation_aware", {"allocation_mode": "correlation_aware"}),
            ]
        else:
            raise ValueError(f"Unsupported experiment_type: {experiment_type}")

        rows = []
        for name, scenario in scenarios:
            report = manager.run_cycle(symbol=symbol, scenario=scenario, persist_outputs=False)
            rows.append(_build_result_row(name, report))

        experiment_id = f"{experiment_type}_{symbol.lower()}_{int(time())}"
        payload = {
            "experiment_id": experiment_id,
            "experiment_type": experiment_type,
            "symbol": symbol,
            "results": rows,
        }
        write_json(self.data_dir / f"{experiment_id}.json", payload)
        write_text(str(self.data_dir / f"{experiment_id}.md"), _render_markdown_summary(payload))
        return payload
