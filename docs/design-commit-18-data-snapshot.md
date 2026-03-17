# Commit 18 Design Note

## Goal

Attach stable provenance metadata to every built market snapshot.

## Design

- Extend snapshot payloads with:
  - `snapshot_hash`
  - `data_source`
  - `timestamp`
- Keep `as_of_ts` for backward compatibility with existing freshness checks.
- Derive `data_source` from the active provider and compute `snapshot_hash` from the serialized snapshot content.

## Compatibility

- Existing snapshot fields remain unchanged.
- New metadata is additive and available to later cache, audit, and backtest features.
