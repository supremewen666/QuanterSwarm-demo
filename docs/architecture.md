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
- trace id for run-level correlation across logs, report, and tests
- explicit state-machine stage records (`ingest -> regime -> route -> specialist_research -> leader_proposal -> rank -> risk -> allocate -> execute -> report`)
- structured termination reasons for short-circuit exits (`no_data`, `low_confidence_no_trade`, `no_trade`)

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
- `router_ablation` includes `max_active_leaders` sensitivity runs

## Config Provenance

Every run validates config consistency before execution and embeds a `config_provenance`
section in the final report with a deterministic fingerprint and effective config snapshot.
