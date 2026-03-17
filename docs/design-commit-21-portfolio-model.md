# Commit 21 Design Note

## Goal

Introduce shared backtest models for execution and portfolio objects before adding cost and walk-forward extensions.

## Design

- Add `src/quanter_swarm/backtest/models.py` with:
  - `Order`
  - `Fill`
  - `Position`
  - `Portfolio`
- Reuse these models inside `replay_engine` so event emission and replay metrics validate the same objects.
- Keep the runtime orchestration payload shape unchanged by validating existing dictionaries instead of rewriting upstream report generation.

## Compatibility

- Existing report and replay payloads remain dict-based at the boundaries.
- New models are internal validation and normalization layers for backtest code.
