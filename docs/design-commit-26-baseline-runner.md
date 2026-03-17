# Commit 26 Design Note

## Goal

Execute the roadmap experiment presets directly from config files.

## Design

- Add `src/quanter_swarm/experiments/runner.py` with `ConfiguredExperimentRunner`.
- Load repository-level `experiments/*.yaml` files, validate the `mode`, and execute one cycle per configured symbol.
- Persist results to `data/experiments/` as JSON and markdown, mirroring the existing ablation runner output pattern.

## Compatibility

- Existing ablation runner remains unchanged.
- The configured experiment runner is additive and dedicated to the new preset-based experiment flow.
