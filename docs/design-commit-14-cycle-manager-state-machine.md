# Commit 14 Design Note

## Goal

Refactor `CycleManager.run_cycle()` into explicit state handlers so each orchestration state has a dedicated function boundary.

## Design

- Keep business behavior and outputs unchanged while splitting `run_cycle()` into `_state_*` methods:
  - `_state_data_fetch`
  - `_state_regime_detect`
  - `_state_routing`
  - `_state_agent_execution`
  - `_state_risk_check`
  - `_state_portfolio_build`
  - `_state_report_generation`
- Add `_enter_state()` to track high-level state transitions in a deterministic `state_sequence`.
- Preserve existing detailed `StageRecord` trace while adding the new transition sequence to `decision_trace_summary.state_machine`.

## Compatibility

- Existing API/report fields remain compatible.
- New fields are additive trace metadata: `decision_trace_summary.state_machine.state_sequence`.
