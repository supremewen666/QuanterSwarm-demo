# Commit 17 Design Note

## Goal

Provide concrete non-production data providers for tests and offline dataset workflows.

## Design

- Add `MockDataProvider` for in-memory deterministic fixtures.
- Add `FileDataProvider` that reads:
  - `latest_price_<SYMBOL>.csv|parquet`
  - `price_history_<SYMBOL>.csv|parquet`
  - `news_<SYMBOL>.csv|parquet`
- Keep the provider interface stable so experiments and tests can swap implementations without changing orchestration code.

## Compatibility

- Existing default behavior still uses `DeterministicDataProvider`.
- The new providers are additive and optional.
