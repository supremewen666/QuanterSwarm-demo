# Commit 19 Design Note

## Goal

Add reusable snapshot cache implementations without coupling cache mechanics to provider implementations.

## Design

- Add `src/quanter_swarm/data/cache.py` with:
  - `SnapshotCache`
  - `MemorySnapshotCache`
  - `FileSnapshotCache`
- Integrate cache reads and writes into `DataFetchSpecialist`, keeping the provider interface unchanged.
- Use the snapshot symbol as the cache key and preserve the cached payload as-is.

## Compatibility

- Caching is optional. Existing `DataFetchSpecialist()` behavior remains unchanged when no cache is supplied.
- Cached responses add only one compatibility field: `cache_hit`.
