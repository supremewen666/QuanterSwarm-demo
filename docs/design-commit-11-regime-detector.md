# Commit 11 Design Note

## Goal

Extract regime classification into a dedicated detector module and support stable canonical market buckets: `bull`, `bear`, `sideways`, and `volatile`.

## Design

- Add `src/quanter_swarm/router/regime_detector.py` as the canonical home for regime scoring and hysteresis.
- Keep the existing detailed labels such as `trend_up`, `risk_off`, and `panic` so routing configs and reports remain compatible.
- Add a derived `family` field that maps detailed labels into stable canonical buckets for future router and observability work.
- Expose `family_candidates` so downstream consumers can reason about the stable bucket scores without re-implementing the mapping.

## Compatibility

- `detect_regime()` remains import-compatible through `quanter_swarm.router`.
- Existing callers that read `label` continue to work unchanged.
- New callers can use `family` when they need stable four-bucket behavior.
