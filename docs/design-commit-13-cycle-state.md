# Commit 13 Design Note

## Goal

Introduce the roadmap `CycleState` model without forcing the full cycle manager state-machine refactor yet.

## Design

- Add a `CycleState` enum covering the high-level lifecycle: init, data fetch, regime detect, routing, agent execution, portfolio build, risk check, report generation, done, and failed.
- Keep the existing fine-grained `CycleStage` trace so current diagnostics stay intact.
- Derive `StageRecord.state` automatically from the existing stage via a stable mapping function.
- Include the derived state and terminal `current_state` in the emitted cycle trace so the lifecycle is externally observable before the manager is refactored in the next commit.

## Compatibility

- Existing stage names remain unchanged.
- The new state fields are additive trace metadata.
