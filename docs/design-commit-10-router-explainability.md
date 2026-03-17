# Commit 10 Design Note

## Goal

Make router outputs explicitly explainable at the schema level so each cycle report shows what regime was detected, which agents were selected, and why alternatives were rejected.

## Decisions

- Reuse the existing `RouterDecision` schema as the canonical explainability surface instead of inventing a second routing explanation structure.
- Extend router function output to include `confidence`, `leader_selected`, `specialists_selected`, `reasons`, and `rejected_candidates` directly.
- Keep backward-compatible aliases such as `selected_reasons` and `skipped_reasons` for existing callers.
- Write the same explainability fields into both `router_decision` and `decision_trace_summary.routing`.

## Result

Every cycle report now carries stable routing explanations that are available through both the top-level router decision schema and the trace summary.
