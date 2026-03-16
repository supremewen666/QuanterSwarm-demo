# Ablation Plan

This document defines the minimum ablation suite and how to interpret outputs.

## Objectives

- quantify routed activation value vs always-on activation
- quantify sensitivity to `max_active_leaders`
- quantify specialist contribution and allocation-mode impact

## Commands

```bash
python scripts/run_ablation.py router_ablation AAPL
python scripts/run_ablation.py specialist_ablation AAPL
python scripts/run_ablation.py allocation_ablation AAPL
```

## Router Ablation Variants

- `routed`: default routed activation
- `always_on`: force all leaders active
- `routed_max_1`: routed with one active leader
- `routed_max_3`: routed with up to three active leaders

## Metrics to Compare

- annualized_return
- sharpe
- sortino
- max_drawdown
- turnover
- exposure_summary
- strategy_contribution

## Interpretation Rules

- prefer variants with better sharpe/sortino under acceptable drawdown
- reject variants that increase turnover without improving risk-adjusted returns
- inspect strategy contribution to detect concentration risk or weak leaders
