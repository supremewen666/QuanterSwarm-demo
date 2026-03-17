# Commit 27 Design Note

## Goal

Export experiment results in analyst-friendly artifact formats beyond JSON and markdown.

## Design

- Extend `ConfiguredExperimentRunner` to emit an artifact directory per run.
- Export:
  - `experiment_table.csv`
  - `equity_curve.png`
  - `drawdown_curve.png`
- Keep implementation dependency-light by generating charts with a small built-in PNG renderer instead of adding a plotting dependency.

## Compatibility

- Existing JSON and markdown outputs remain unchanged.
- New artifact paths are exposed through an additive `artifacts` field in the runner payload.
