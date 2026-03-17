# Commit 15 Design Note

## Goal

Add a dedicated trace module so cycle observability data has a single canonical shape.

## Design

- Add `src/quanter_swarm/observability/trace.py` with `new_trace_id()` and `build_cycle_trace()`.
- Keep `decision_trace_summary` as the existing top-level report surface, but add a normalized `decision_trace_summary.trace` object.
- The normalized trace records:
  - `trace_id`
  - `router_decision`
  - `agents_activated`
  - `latency`
  - `risk_result`
- Keep `src/quanter_swarm/utils/tracing.py` as a compatibility shim that re-exports `new_trace_id()`.

## Compatibility

- Existing `decision_trace_summary` fields stay in place.
- New trace data is additive and reusable by later observability work.
