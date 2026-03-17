# Commit 04 Design Note

## Goal

Replace generic project-level runtime exceptions with a small typed error hierarchy so router, agent execution, data/config loading, risk validation, and backtest failures are distinguishable.

## Decisions

- Add `src/quanter_swarm/errors.py` as the canonical exception module.
- Keep `src/quanter_swarm/utils/exceptions.py` as a compatibility re-export to avoid a broad import migration in one commit.
- Convert config validation errors to `RouterError`, `DataProviderError`, and `RiskGuardrailError`.
- Wrap schema breakage in `CycleManager` as `AgentExecutionError` so callers get a domain error instead of raw pydantic internals.
- Convert unsupported experiment modes to `BacktestError`.

## Result

Core logic no longer raises bare generic exceptions for these runtime failure modes, and tests now assert against domain-specific exceptions.
