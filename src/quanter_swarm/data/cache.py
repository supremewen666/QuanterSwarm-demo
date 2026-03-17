"""Snapshot cache implementations."""

from __future__ import annotations

import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any


class SnapshotCache(ABC):
    @abstractmethod
    def get_snapshot(self, key: str) -> dict[str, Any] | None:
        """Return a cached snapshot for the key if present."""

    @abstractmethod
    def set_snapshot(self, key: str, snapshot: dict[str, Any]) -> None:
        """Store a snapshot under the key."""


class MemorySnapshotCache(SnapshotCache):
    def __init__(self) -> None:
        self._store: dict[str, dict[str, Any]] = {}

    def get_snapshot(self, key: str) -> dict[str, Any] | None:
        cached = self._store.get(key)
        return dict(cached) if cached is not None else None

    def set_snapshot(self, key: str, snapshot: dict[str, Any]) -> None:
        self._store[key] = dict(snapshot)


class FileSnapshotCache(SnapshotCache):
    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def get_snapshot(self, key: str) -> dict[str, Any] | None:
        path = self.root / f"{key.lower()}.json"
        if not path.exists():
            return None
        return json.loads(path.read_text(encoding="utf-8"))

    def set_snapshot(self, key: str, snapshot: dict[str, Any]) -> None:
        path = self.root / f"{key.lower()}.json"
        path.write_text(json.dumps(snapshot, sort_keys=True), encoding="utf-8")
