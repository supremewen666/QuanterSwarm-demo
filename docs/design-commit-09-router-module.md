# Commit 09 Design Note

## Goal

Move routing logic out of orchestration classes into a dedicated router module with stable functional entrypoints.

## Decisions

- Add `src/quanter_swarm/router/router.py` with `detect_regime()`, `select_leader()`, and `select_specialists()`.
- Keep `RegimeAgent` and `RouterAgent` as thin wrappers so current callers remain compatible while routing logic lives in the new module.
- Leave explainability enrichment for the next commit; this step is focused on separation of responsibilities.

## Result

Routing logic now lives under `src/quanter_swarm/router/`, and orchestration classes delegate to the shared router functions instead of implementing the logic inline.
