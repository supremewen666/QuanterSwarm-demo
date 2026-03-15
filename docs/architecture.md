# Architecture

QuanterSwarm is organized around a root orchestration layer, shared specialist services,
strategy leaders, and a decision pipeline that produces guarded paper-trading suggestions.

## Decision Trace

Each cycle now emits a `decision_trace_summary` that records:

- regime evidence and confidence
- routing selected/skipped reasons
- leader score and rank contribution
- risk guardrail scaling or veto
- portfolio scaling outcome
- execution assumptions (slippage/fill model)

## Execution Simulation

Paper execution models now include:

- volatility and participation-aware slippage
- partial fill assumptions
- open-session penalty and gap sensitivity
- fixed and bps commission costs
- structured execution audit payload

## Validation and Ablation

The platform includes:

- config validation for routing/allocation policies
- data quality checks for missing/stale/symbol mismatch issues
- experiment runner for `router_ablation`, `specialist_ablation`, `allocation_ablation`
