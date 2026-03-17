# Commit 20 Design Note

## Goal

Introduce a reusable event vocabulary for later event-driven backtest work.

## Design

- Add `src/quanter_swarm/backtest/events.py` with:
  - `MarketEvent`
  - `SignalEvent`
  - `OrderEvent`
  - `FillEvent`
  - `PortfolioUpdateEvent`
- Keep current replay logic intact and emit a minimal ordered event sequence from `replay_engine`.
- Surface those events in walk-forward step results so later portfolio and execution models can consume the same event stream.

## Compatibility

- Existing backtest return metrics are unchanged.
- Event payloads are additive metadata on replay results and walk-forward step results.
