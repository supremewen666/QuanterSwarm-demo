# Commit 08 Design Note

## Goal

Provide a shared execution layer for agents that supports concurrency, per-agent timeouts, and partial failures.

## Decisions

- Add `src/quanter_swarm/orchestrator/agent_executor.py` with a small `AgentExecutor` abstraction built on `asyncio.gather()` and `asyncio.wait_for()`.
- Return structured `results` and `failures` instead of immediately crashing the whole batch when partial failure mode is enabled.
- Integrate the executor into `CycleManager` for specialist work that can safely run in parallel today: memory compression and macro-event analysis.
- Keep the rest of the orchestration flow synchronous for now by providing a `execute_many_sync()` wrapper.

## Result

Specialists now support concurrent execution with timeout and partial-failure handling, and the cycle manager records specialist batch failures without aborting the full cycle when fallback behavior is available.
