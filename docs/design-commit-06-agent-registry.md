# Commit 06 Design Note

## Goal

Centralize agent construction so orchestration code stops importing concrete agent implementations directly.

## Decisions

- Add `src/quanter_swarm/agents/registry.py` as the canonical registry for leaders, specialists, and orchestration agents used inside the cycle manager.
- Pre-register the existing built-in agents and expose helpers for `get_agent`, `get_leader`, and `get_specialist`.
- Keep `src/quanter_swarm/leaders/leader_factory.py` as a compatibility shim that now delegates to the registry.
- Refactor `CycleManager` to resolve leaders and specialists through the registry instead of hand-written imports.

## Result

Agent instantiation is now centralized, and the orchestrator no longer hard-codes concrete agent imports for its execution path.
