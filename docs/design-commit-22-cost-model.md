# Commit 22 Design Note

## Goal

Separate replay cost calculations into a reusable backtest cost model.

## Design

- Add `src/quanter_swarm/backtest/costs.py` with:
  - `transaction_fee()`
  - `slippage()`
- Keep replay return logic unchanged in shape, but replace inline total-cost aggregation with cost-model helpers.
- Expose `transaction_fee` and `slippage` explicitly in replay payloads so later reporting and walk-forward analysis can break out execution drag.

## Compatibility

- Existing `cost_ratio` and `realized_return` fields remain available.
- New cost fields are additive.
