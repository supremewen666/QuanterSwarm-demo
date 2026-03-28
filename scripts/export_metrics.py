"""Export leaderboard and monitoring snapshot from stored reports."""
# ruff: noqa: E402

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from quanter_swarm.core.storage.file_store import write_json, write_text
from quanter_swarm.services.monitoring.evaluation import build_monitoring_from_report_dir


def _render_markdown(snapshot: dict) -> str:
    lines = [
        "# QuanterSwarm Monitoring Snapshot",
        "",
        f"- Report count: `{snapshot.get('report_count', 0)}`",
        f"- Drift status: `{snapshot.get('drift', {}).get('status', 'unknown')}`",
        "",
        "## Latency",
    ]
    latency = snapshot.get("latency", {})
    lines.extend(
        [
            f"- Avg runtime (ms): `{latency.get('avg_runtime_ms', 0)}`",
            f"- P90 runtime (ms): `{latency.get('p90_runtime_ms', 0)}`",
            f"- P95 runtime (ms): `{latency.get('p95_runtime_ms', 0)}`",
            "",
            "## Output Quality",
        ]
    )
    quality = snapshot.get("output_quality", {})
    lines.extend(
        [
            f"- Avg completeness: `{quality.get('avg_completeness', 0)}`",
            f"- Schema invalid count: `{quality.get('schema_invalid_count', 0)}`",
            "",
            "## Leaderboard (Top 5)",
        ]
    )
    for row in snapshot.get("leaderboard", [])[:5]:
        lines.append(
            f"- `{row['leader']}`: net `{row['avg_net_score']}`, activations `{row['activation_count']}`, win `{row['win_rate_proxy']}`"
        )
    lines.extend(["", "## Regime Breakdown"])
    for row in snapshot.get("regime_breakdown", []):
        lines.append(
            f"- `{row['regime']}`: count `{row['count']}`, sharpe `{row['avg_sharpe']}`, turnover `{row['avg_turnover']}`, no-trade `{row['no_trade_rate']}`"
        )
    alerts = snapshot.get("drift", {}).get("alerts", [])
    lines.extend(["", "## Drift Alerts"])
    if not alerts:
        lines.append("- none")
    else:
        for alert in alerts:
            lines.append(f"- `{alert.get('type', 'unknown')}`: `{alert.get('details', {})}`")
    return "\n".join(lines).strip()


def main() -> None:
    parser = argparse.ArgumentParser(description="Export monitoring snapshot from report JSON files.")
    parser.add_argument("--report-dir", default="data/reports", help="Directory containing cycle report JSON files.")
    parser.add_argument("--baseline-window", type=int, default=20)
    parser.add_argument("--recent-window", type=int, default=10)
    parser.add_argument("--output-json", default=None, help="Optional output JSON path.")
    parser.add_argument("--output-markdown", default=None, help="Optional output markdown path.")
    args = parser.parse_args()

    snapshot = build_monitoring_from_report_dir(
        report_dir=args.report_dir,
        baseline_window=args.baseline_window,
        recent_window=args.recent_window,
    )
    if args.output_json:
        write_json(args.output_json, snapshot)
    if args.output_markdown:
        write_text(args.output_markdown, _render_markdown(snapshot))
    print(json.dumps(snapshot, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
