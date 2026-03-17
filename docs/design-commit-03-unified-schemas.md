# Commit 03 Design Note

## Goal

Unify orchestration input and output contracts under a single pydantic schema layer without breaking the current API shape.

## Decisions

- Extend `src/quanter_swarm/contracts.py` with the roadmap models: `AgentContext`, `AgentResult`, `RouterDecision`, `PortfolioSuggestion`, `RiskCheckResult`, and `CycleReport`.
- Keep compatibility aliases for the pre-existing `PortfolioSuggestionContract` and `FinalReportContract`.
- Add `router_decision` and `risk_check` into generated reports so router and risk outputs are explicitly typed instead of only living inside free-form trace dictionaries.
- Validate cycle outputs both in `CycleManager` and `RootAgent` through `CycleReport`.

## Result

The orchestrator now emits a typed `CycleReport`, router and risk decisions have first-class schemas, and API responses stay compatible while gaining stronger structure.
