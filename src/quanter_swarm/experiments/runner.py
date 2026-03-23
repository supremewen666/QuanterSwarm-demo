"""Runner for experiment presets under the repository-level experiments directory."""

from __future__ import annotations

import csv
import struct
import zlib
from pathlib import Path
from time import time
from typing import Any, cast

from quanter_swarm.errors import BacktestError
from quanter_swarm.orchestrator.cycle_manager import CycleManager
from quanter_swarm.storage.file_store import write_json, write_text
from quanter_swarm.utils.config import load_yaml

_SUPPORTED_MODES = {"single_agent", "fixed_multi_agent", "routed_multi_agent", "routed_ephemeral"}


def _leader_contribution(report: dict[str, Any]) -> dict[str, float]:
    contribution: dict[str, float] = {}
    for entry in report.get("decision_trace_summary", {}).get("leader_scores", []):
        contribution[entry["leader"]] = round(entry.get("rank_score", 0.0) - entry.get("risk_penalty", 0.0), 4)
    return contribution


def _result_row(symbol: str, report: dict[str, Any]) -> dict[str, Any]:
    metrics = report.get("evaluation_summary", {}).get("metrics", {})
    portfolio = report.get("portfolio_suggestion", {})
    return {
        "symbol": symbol,
        "regime": report.get("active_regime"),
        "regime_confidence": report.get("regime_confidence", 0.0),
        "annualized_return": metrics.get("annualized_return", 0.0),
        "sharpe": metrics.get("sharpe", 0.0),
        "sortino": metrics.get("sortino", 0.0),
        "max_drawdown": metrics.get("max_drawdown", metrics.get("drawdown", 0.0)),
        "win_rate": metrics.get("win_rate", 0.0),
        "turnover": metrics.get("turnover", metrics.get("turnover_proxy", 0.0)),
        "mode": portfolio.get("mode", "no_trade"),
        "active_strategy_teams": report.get("active_strategy_teams", []),
        "strategy_contribution": _leader_contribution(report),
    }


def _render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        f"# Configured Experiment {payload['experiment_id']}",
        "",
        f"- Name: `{payload['experiment_name']}`",
        f"- Mode: `{payload['mode']}`",
        f"- Symbols: `{', '.join(payload['symbols'])}`",
        "",
        "## Results",
    ]
    for row in payload["results"]:
        lines.extend(
            [
                f"### {row['symbol']}",
                f"- Regime: `{row['regime']}` (`{row['regime_confidence']}`)",
                f"- Sharpe / Sortino: `{row['sharpe']}` / `{row['sortino']}`",
                f"- Max Drawdown: `{row['max_drawdown']}`",
                f"- Win Rate / Turnover: `{row['win_rate']}` / `{row['turnover']}`",
                f"- Mode: `{row['mode']}`",
                f"- Active teams: `{row['active_strategy_teams']}`",
                "",
            ]
        )
    return "\n".join(lines).strip()


def _equity_curve(rows: list[dict[str, Any]]) -> list[float]:
    equity = 1.0
    curve: list[float] = []
    for row in rows:
        step_return = float(row.get("annualized_return", 0.0)) / 252
        equity *= 1 + step_return
        curve.append(round(equity, 6))
    return curve


def _drawdown_curve(equity_curve: list[float]) -> list[float]:
    peak = 1.0
    drawdowns: list[float] = []
    for value in equity_curve:
        peak = max(peak, value)
        drawdowns.append(round((value - peak) / peak if peak else 0.0, 6))
    return drawdowns


def _write_experiment_table(path: Path, rows: list[dict[str, Any]]) -> None:
    fieldnames = [
        "symbol",
        "regime",
        "regime_confidence",
        "annualized_return",
        "sharpe",
        "sortino",
        "max_drawdown",
        "win_rate",
        "turnover",
        "mode",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({name: row.get(name) for name in fieldnames})


def _write_png_line_chart(path: Path, values: list[float], color: tuple[int, int, int]) -> None:
    width = 400
    height = 240
    padding = 16
    pixels = bytearray([255] * width * height * 3)

    def _set_pixel(x: int, y: int, rgb: tuple[int, int, int]) -> None:
        if 0 <= x < width and 0 <= y < height:
            index = (y * width + x) * 3
            pixels[index:index + 3] = bytes(rgb)

    def _draw_line(x0: int, y0: int, x1: int, y1: int, rgb: tuple[int, int, int]) -> None:
        dx = abs(x1 - x0)
        sx = 1 if x0 < x1 else -1
        dy = -abs(y1 - y0)
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            _set_pixel(x0, y0, rgb)
            if x0 == x1 and y0 == y1:
                return
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    if values:
        min_value = min(values)
        max_value = max(values)
        span = max(1e-9, max_value - min_value)
        x_span = max(1, len(values) - 1)
        points = []
        for index, value in enumerate(values):
            x = padding + int((width - 2 * padding) * (index / x_span))
            normalized = (value - min_value) / span
            y = height - padding - int((height - 2 * padding) * normalized)
            points.append((x, y))
        for start, end in zip(points, points[1:], strict=False):
            _draw_line(start[0], start[1], end[0], end[1], color)

    def _chunk(tag: bytes, data: bytes) -> bytes:
        return (
            struct.pack(">I", len(data))
            + tag
            + data
            + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        )

    raw_rows = bytearray()
    for y in range(height):
        row_start = y * width * 3
        raw_rows.append(0)
        raw_rows.extend(pixels[row_start:row_start + width * 3])

    png = bytearray(b"\x89PNG\r\n\x1a\n")
    png.extend(_chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)))
    png.extend(_chunk(b"IDAT", zlib.compress(bytes(raw_rows))))
    png.extend(_chunk(b"IEND", b""))
    path.write_bytes(bytes(png))


class ConfiguredExperimentRunner:
    def __init__(
        self,
        *,
        config_dir: Path | str = "experiments",
        data_dir: Path | str = "data/experiments",
    ) -> None:
        self.config_dir = Path(config_dir)
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def load_config(self, config_name: str) -> dict[str, Any]:
        path = self.config_dir / f"{config_name}.yaml"
        if not path.exists():
            raise BacktestError(f"Unknown experiment config: {config_name}")
        payload = load_yaml(path)
        experiment = cast(dict[str, Any], payload.get("experiment", {}))
        mode = experiment.get("mode")
        if mode not in _SUPPORTED_MODES:
            raise BacktestError(f"Unsupported experiment mode: {mode}")
        return experiment

    def run(self, config_name: str) -> dict[str, Any]:
        experiment = self.load_config(config_name)
        manager = CycleManager()
        scenario = dict(experiment.get("scenario", {}))
        symbols = list(experiment.get("symbols", []))
        results = []
        for symbol in symbols:
            report = manager.run_cycle(symbol=symbol, scenario=scenario, persist_outputs=False)
            results.append(_result_row(symbol, report))

        experiment_id = f"{experiment['name']}_{int(time())}"
        payload = {
            "experiment_id": experiment_id,
            "experiment_name": experiment["name"],
            "mode": experiment["mode"],
            "description": experiment.get("description", ""),
            "symbols": symbols,
            "scenario": scenario,
            "results": results,
        }
        artifact_dir = self.data_dir / experiment_id
        artifact_dir.mkdir(parents=True, exist_ok=True)
        equity_curve = _equity_curve(results)
        drawdown_curve = _drawdown_curve(equity_curve)
        _write_experiment_table(artifact_dir / "experiment_table.csv", results)
        _write_png_line_chart(artifact_dir / "equity_curve.png", equity_curve, (22, 111, 76))
        _write_png_line_chart(artifact_dir / "drawdown_curve.png", drawdown_curve, (173, 38, 45))
        payload["artifacts"] = {
            "directory": str(artifact_dir),
            "experiment_table": str(artifact_dir / "experiment_table.csv"),
            "equity_curve": str(artifact_dir / "equity_curve.png"),
            "drawdown_curve": str(artifact_dir / "drawdown_curve.png"),
        }
        write_json(self.data_dir / f"{experiment_id}.json", payload)
        write_text(str(self.data_dir / f"{experiment_id}.md"), _render_markdown(payload))
        return payload
