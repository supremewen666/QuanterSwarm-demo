# Commit 05 Design Note

## Goal

Introduce one shared agent interface that all leaders, specialists, and orchestration agents can implement without forcing the orchestration flow itself to become async in the same commit.

## Decisions

- Add `src/quanter_swarm/agents/base.py` with the canonical `BaseAgent` interface and async `run(context) -> AgentResult`.
- Keep existing synchronous domain methods such as `propose()`, `fetch()`, `assess()`, `classify_detail()`, and `route()` so current orchestration logic stays stable.
- For `RootAgent`, move the existing synchronous path to `run_sync()` and make `run()` the async interface implementation.

## Result

The codebase now has one common agent protocol that later registry and executor work can target, while existing synchronous behavior remains available for the current orchestration path.
