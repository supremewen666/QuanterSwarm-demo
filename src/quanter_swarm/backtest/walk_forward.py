"""Walk-forward backtesting orchestration."""

from __future__ import annotations

from pathlib import Path
from time import time
from typing import Any

from quanter_swarm.agents.orchestrator.cycle_manager import CycleManager
from quanter_swarm.backtest.metrics import summarize_backtest_metrics
from quanter_swarm.backtest.replay_engine import replay_report
from quanter_swarm.backtest.validator import BacktestValidator
from quanter_swarm.config.defaults import DEFAULT_BACKTEST_WINDOW
from quanter_swarm.core.storage.file_store import write_json, write_text


def _scenario_for_step(step: int) -> dict[str, Any]:
    if step % 5 == 0:
        return {"allocation_mode": "correlation_aware", "max_active_leaders": 1}
    if step % 3 == 0:
        return {"allocation_mode": "volatility_aware"}
    if step % 2 == 0:
        return {"disable_specialists": {"sentiment": True}}
    return {}


def _window_assignment(step: int, train_window: int, test_window: int, rolling_window: int) -> dict[str, int | str]:
    cycle_span = max(1, train_window + test_window)
    window_index = step // cycle_span
    cycle_offset = step % cycle_span
    phase = "train" if cycle_offset < train_window else "test"
    rolling_start = max(0, window_index * max(1, rolling_window))
    return {
        "window_index": window_index,
        "phase": phase,
        "rolling_start": rolling_start,
    }


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
        f"- Train window: {payload['train_window']}",
        f"- Test window: {payload['test_window']}",
        f"- Rolling window: {payload['rolling_window']}",
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
        train_window: int = DEFAULT_BACKTEST_WINDOW["train_window"],
        test_window: int = DEFAULT_BACKTEST_WINDOW["test_window"],
        rolling_window: int = DEFAULT_BACKTEST_WINDOW["rolling_window"],
        capital: float = 100_000.0,
    ) -> dict[str, Any]:
        validator = BacktestValidator()
        validator.validate_run(
            {
                "symbols": symbols,
                "steps": steps,
                "train_window": train_window,
                "test_window": test_window,
                "rolling_window": rolling_window,
                "capital": capital,
            }
        )
        manager = CycleManager()
        returns: list[float] = []
        step_results: list[dict[str, Any]] = []
        for step in range(steps):
            symbol = symbols[step % len(symbols)]
            scenario = _scenario_for_step(step)
            assignment = _window_assignment(step, train_window, test_window, rolling_window)
            report = manager.run_cycle(symbol=symbol, scenario=scenario, persist_outputs=False)
            validator.validate_report(report)
            replay = replay_report(report, capital)
            returns.append(replay["realized_return"])
            step_results.append(
                {
                    "step": step,
                    "window_index": assignment["window_index"],
                    "phase": assignment["phase"],
                    "rolling_start": assignment["rolling_start"],
                    "symbol": symbol,
                    "regime": report.get("active_regime"),
                    "trace_id": report.get("decision_trace_summary", {}).get("trace_id"),
                    "scenario": scenario,
                    "realized_return": replay["realized_return"],
                    "leader_attribution": replay["leader_attribution"],
                    "events": replay["events"],
                    "event_count": len(replay["events"]),
                    "execution_summary": replay["execution_summary"],
                    "portfolio_attribution": replay["portfolio_attribution"],
                }
            )

        summary = summarize_backtest_metrics(returns)
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
            "train_window": train_window,
            "test_window": test_window,
            "rolling_window": rolling_window,
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
