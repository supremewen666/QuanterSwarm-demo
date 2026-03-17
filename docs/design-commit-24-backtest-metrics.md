# Commit 24 Design Note

## Goal

Move core backtest performance metrics into a dedicated backtest module.

## Design

- Add `src/quanter_swarm/backtest/metrics.py` with dedicated helpers for:
  - Sharpe
  - Sortino
  - Max Drawdown
  - Turnover
  - Win Rate
- Keep implementation lightweight by reusing the existing evaluation metric primitives where appropriate.
- Update walk-forward summaries to use the dedicated backtest metric surface.

## Compatibility

- Existing `summary_metrics` remains a dict.
- The metric set changes to the roadmap-defined backtest metrics and remains stable for later experiment reporting.
