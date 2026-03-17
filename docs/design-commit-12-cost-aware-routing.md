# Commit 12 Design Note

## Goal

Teach the router to reduce specialist activation when token or latency budgets are constrained.

## Design

- Keep `select_specialists()` backward-compatible by returning only the selected specialist names.
- Add `select_specialist_plan()` to expose the selected set, rejected candidates, and applied budget constraints.
- Apply three routing constraints in order: `token_budget`, `latency_budget`, and `max_specialists_per_cycle`.
- Bias low-budget routing toward lower-cost specialists by combining `cost_hint` with existing `priority`.

## Compatibility

- Existing callers that only need a list of specialists still use `select_specialists()`.
- The cycle report now includes `budget_constraints` and `specialist_rejections` as additive routing metadata.
