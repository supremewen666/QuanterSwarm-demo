# Commit 28 Design Note

## Goal

Emit machine-readable runtime logs with the core orchestration fields needed for debugging and observability.

## Design

- Extend `src/quanter_swarm/utils/logging.py` with:
  - `JsonFormatter`
  - `configure_logging()`
- Switch `configs/logging.yaml` to JSON logging by default.
- Add cycle lifecycle log events in `CycleManager` so each major state emits:
  - `trace_id`
  - `cycle_state`
  - `agent_name`
  - `latency`
  - `status`

## Compatibility

- The old `get_logger()` helper remains.
- Non-JSON formatting is still supported if `configs/logging.yaml` disables `json`.
