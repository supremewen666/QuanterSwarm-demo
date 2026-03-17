# Commit 16 Design Note

## Goal

Introduce a canonical data-provider interface before adding mock and file-backed providers.

## Design

- Add `src/quanter_swarm/data/base.py` with `BaseDataProvider` and the required methods:
  - `get_price_history()`
  - `get_latest_price()`
  - `get_news()`
- Add `DeterministicDataProvider` as the default implementation over the existing deterministic local feeds.
- Update snapshot construction and `DataFetchSpecialist` to depend on the provider interface instead of reaching directly into the feed modules.

## Compatibility

- The default behavior is unchanged because the default provider wraps the existing local feed functions.
- The new provider parameter on `DataFetchSpecialist` is optional and additive.
