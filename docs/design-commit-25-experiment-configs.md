# Commit 25 Design Note

## Goal

Version the roadmap experiment baselines as explicit config files before wiring a dedicated runner to them.

## Design

- Add `experiments/` at the repository root.
- Add four baseline config files:
  - `baseline_single_agent.yaml`
  - `baseline_fixed_multi_agent.yaml`
  - `routed_multi_agent.yaml`
  - `routed_ephemeral.yaml`
- Keep the schema lightweight: `name`, `mode`, `description`, `symbols`, and `scenario`.

## Compatibility

- Existing ablation scripts remain unchanged.
- The new experiment configs are additive and ready for the dedicated runner in the next commit.
