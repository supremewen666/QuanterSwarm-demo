# Commit 29 Design Note

## Goal

Add a minimal observability metrics layer that reports:

- router latency
- agent latency
- cycle success rate
- token cost

## Design

The metrics system is intentionally derived from existing runtime state rather than introducing a separate collector process.

- `src/quanter_swarm/observability/metrics.py` builds a cycle-level metrics payload.
- `CycleManager` records per-state latency into `state_latencies` as each state completes.
- Final and short-circuit reports now embed `decision_trace_summary.metrics`.
- Structured traces also carry the same metrics payload under `trace.metrics`.

Token cost is estimated from agent `cost_hint` metadata. This keeps the API stable while providing a usable first-pass budget signal before real model token accounting exists.

## Compatibility

This change is additive:

- existing report fields remain unchanged
- `decision_trace_summary` gains a new `metrics` field
- `trace` gains a new `metrics` field

## Test Coverage

- direct metrics unit tests
- root cycle report assertions
- trace propagation assertions
