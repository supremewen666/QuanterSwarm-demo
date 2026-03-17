# Commit 23 Design Note

## Goal

Expose walk-forward window controls explicitly before adding richer backtest metrics.

## Design

- Extend `WalkForwardBacktester.run()` with:
  - `train_window`
  - `test_window`
  - `rolling_window`
- Add deterministic per-step window metadata:
  - `window_index`
  - `phase`
  - `rolling_start`
- Keep the current single-cycle replay mechanism, but make the walk-forward schedule explicit in artifacts and payloads.

## Compatibility

- Existing callers that rely only on `steps` and `capital` continue to work because the new parameters have defaults.
- New window fields are additive in the output payload.
