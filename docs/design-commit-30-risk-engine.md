# Commit 30 Design Note

## Goal

Add an explicit pre-trade risk engine with rule-based blocking for:

- `max_position_size`
- `max_leverage`
- `max_daily_loss`
- `earnings_no_trade`
- `volatility_no_trade`

## Design

The implementation is split into:

- `src/quanter_swarm/risk/rules.py` for individual rule checks
- `src/quanter_swarm/risk/engine.py` for aggregating those checks into a guardrail result

`CycleManager` now runs the risk engine after portfolio construction and before execution. If the engine blocks, the portfolio is rewritten to explicit `no_trade`, the risk reason is surfaced in `risk_check`, and paper-trade execution sees an empty position set.

This keeps the existing `decision.risk_guardrail` path intact while adding portfolio-aware trade blocking that the older warning-based guardrail could not express.

## Compatibility

The change is additive:

- `risk_check` may now include `triggered_rules`
- `configs/risk.yaml` includes new rule thresholds
- existing report and execution APIs remain unchanged

## Test Coverage

- direct unit tests for each rule and engine aggregation
- cycle-level tests that block trading on daily-loss and earnings scenarios
