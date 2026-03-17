"""Walk-forward backtesting orchestration."""

from __future__ import annotations

from pathlib import Path
from time import time
from typing import Any

from quanter_swarm.backtest.replay_engine import replay_report
from quanter_swarm.config.defaults import DEFAULT_BACKTEST_WINDOW
from quanter_swarm.evaluation.metrics import summarize_metrics
from quanter_swarm.orchestrator.cycle_manager import CycleManager
from quanter_swarm.storage.file_store import write_json, write_text


def _scenario_for_step(step: int) -> dict[str, Any]:
    if step % 5 == 0:
        return {"allocation_mode": "correlation_aware", "max_active_leaders": 1}
    if step % 3 == 0:
        return {"allocation_mode": "volatility_aware"}
    if step % 2 == 0:
        return {"disable_specialists": {"sentiment": True}}
    return {}


def _merge_contributions(rows: list[dict[str, Any]], key: str) -> dict[str, float]:
    merged: dict[str, float] = {}
    for row in rows:
        payload = row.get(key, {})
        for item_key, value in payload.items():
            merged[item_key] = round(merged.get(item_key, 0.0) + float(value), 6)
    return merged


def _render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        f"# Walk-Forward Backtest {payload['backtest_id']}",
        "",
        f"- Symbols: {', '.join(payload['symbols'])}",
        f"- Steps: {payload['steps']}",
        f"- Capital: {payload['capital']}",
        "",
        "## Summary Metrics",
    ]
    for key, value in payload["summary_metrics"].items():
        lines.append(f"- {key}: {value}")
    lines.extend(
        [
            "",
            "## Leader Attribution",
        ]
    )
    for key, value in payload["leader_attribution"].items():
        lines.append(f"- {key}: {value}")
    lines.extend(
        [
            "",
            "## Portfolio Attribution",
        ]
    )
    for key, value in payload["portfolio_attribution"].items():
        lines.append(f"- {key}: {value}")
    return "\n".join(lines).strip()


class WalkForwardBacktester:
    def __init__(self, data_dir: Path | str = "data/backtests") -> None:
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def run(
        self,
        *,
        symbols: list[str],
        steps: int = DEFAULT_BACKTEST_WINDOW["steps"],
        capital: float = 100_000.0,
    ) -> dict[str, Any]:
        manager = CycleManager()
        returns: list[float] = []
        step_results: list[dict[str, Any]] = []
        for step in range(steps):
            symbol = symbols[step % len(symbols)]
            scenario = _scenario_for_step(step)
            report = manager.run_cycle(symbol=symbol, scenario=scenario, persist_outputs=False)
            replay = replay_report(report, capital)
            returns.append(replay["realized_return"])
            step_results.append(
                {
                    "step": step,
                    "symbol": symbol,
                    "regime": report.get("active_regime"),
                    "trace_id": report.get("decision_trace_summary", {}).get("trace_id"),
                    "scenario": scenario,
                    "realized_return": replay["realized_return"],
                    "leader_attribution": replay["leader_attribution"],
                    "portfolio_attribution": replay["portfolio_attribution"],
                }
            )

        summary = summarize_metrics(returns)
        leader_attr = _merge_contributions(step_results, "leader_attribution")
        mode_counts: dict[str, float] = {}
        for row in step_results:
            mode = str(row.get("portfolio_attribution", {}).get("mode", "unknown"))
            mode_counts[mode] = round(mode_counts.get(mode, 0.0) + 1.0, 6)
        allocation_mode_counts: dict[str, float] = {}
        for row in step_results:
            mode = str(row.get("portfolio_attribution", {}).get("allocation_mode", "unknown"))
            allocation_mode_counts[mode] = round(allocation_mode_counts.get(mode, 0.0) + 1.0, 6)

        backtest_id = f"walk_forward_{int(time())}"
        payload = {
            "backtest_id": backtest_id,
            "symbols": symbols,
            "steps": steps,
            "capital": capital,
            "summary_metrics": summary,
            "leader_attribution": leader_attr,
            "portfolio_attribution": {
                "mode_counts": mode_counts,
                "allocation_mode_counts": allocation_mode_counts,
            },
            "step_results": step_results,
        }
        write_json(self.data_dir / f"{backtest_id}.json", payload)
        write_text(str(self.data_dir / f"{backtest_id}.md"), _render_markdown(payload))
        return payload
