# Commit 02 Design Note

## Goal

Move the first batch of cross-cutting runtime defaults into a single configuration package so core orchestration logic stops embedding those values directly.

## Decisions

- Introduce `src/quanter_swarm/config/defaults.py` for stable default values and `src/quanter_swarm/config/settings.py` for the runtime settings model.
- Keep `src/quanter_swarm/settings.py` as a compatibility shim to avoid broad import churn in one commit.
- Limit this commit to the roadmap fields: `token_budget`, `max_specialists_per_cycle`, `default_symbols`, `risk_thresholds`, and `backtest_window`.
- Wire the new defaults into `load_settings()` and the first consumers in routing, cycle scoring, and walk-forward backtest defaults.

## Result

Default configuration is now discoverable from one package, environment/YAML overrides merge consistently, and the most visible business-logic magic numbers have been replaced with named configuration values.
