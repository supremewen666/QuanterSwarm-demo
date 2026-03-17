# Commit 07 Design Note

## Goal

Add capability metadata to leaders and specialists so routing can reason about which agents are appropriate for a regime or task.

## Decisions

- Extend `BaseLeader` and `BaseSpecialist` with `supported_regimes`, `supported_tasks`, `cost_hint`, and `priority`.
- Give each built-in leader and specialist explicit defaults instead of leaving capability inference implicit in code comments or config.
- Update `RouterAgent` to filter configured leaders through capability checks and record rejected leaders in `skipped_reasons`.

## Result

Agent capability metadata is now first-class, and router decisions can reject leaders that do not claim support for the target regime.
