# Monitoring and Drift

This document defines the continuous monitoring output for QuanterSwarm runs.

## Scope

`src/quanter_swarm/services/monitoring/evaluation.py` aggregates saved cycle reports (`data/reports/*.json`) into one snapshot with:

- leader leaderboard
- regime-level performance breakdown
- latency summary
- output quality summary
- basic drift alerts

## CLI Export

Use:

```bash
python scripts/export_metrics.py \
  --report-dir data/reports \
  --baseline-window 20 \
  --recent-window 10 \
  --output-json data/monitoring/latest.json \
  --output-markdown data/monitoring/latest.md
```

## Snapshot Fields

- `leaderboard`: activation/trade counts, avg rank/net score, avg weight, win-rate proxy by leader.
- `regime_breakdown`: avg sharpe/drawdown/turnover/exposure/cash/no-trade rate by regime.
- `latency`: avg/p50/p90/p95/max runtime in milliseconds (`decision_trace_summary.runtime_ms`).
- `output_quality`: completeness score and schema-invalid count (`FinalReportContract` validation).
- `drift`: baseline-vs-recent checks for:
  - regime distribution shift
  - leader activation shift
  - sharpe drift
  - output quality drop
  - latency regression

## Notes

- Drift status can be `stable`, `alert`, or `insufficient_data`.
- Legacy reports lacking `decision_trace_summary.runtime_ms` are still accepted; latency sampling will ignore missing values.
- Cycle-level traces and metrics now live alongside the aggregation helpers under `src/quanter_swarm/services/monitoring/`.
