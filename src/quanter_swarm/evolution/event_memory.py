"""Persistent event memory store for weak priors."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from quanter_swarm.evolution.similarity import event_similarity


class EventMemoryStore:
    def __init__(self, root: Path) -> None:
        self.path = root / "event_memory.jsonl"

    def append(self, payload: dict[str, Any]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, sort_keys=True) + "\n")

    def load(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        rows: list[dict[str, Any]] = []
        for line in self.path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                rows.append(json.loads(line))
        return rows

    def find_similar(self, event_payload: dict[str, Any], limit: int = 5) -> list[dict[str, Any]]:
        now = datetime.now(tz=UTC)
        ranked: list[dict[str, Any]] = []
        for row in self.load():
            scores = event_similarity(event_payload, row)
            ranked.append(
                {
                    **row,
                    **scores,
                    "age_days": max(
                        0.0,
                        (now - datetime.fromisoformat(str(row.get("recorded_at")).replace("Z", "+00:00"))).total_seconds()
                        / 86_400,
                    )
                    if row.get("recorded_at")
                    else 0.0,
                }
            )
        ranked.sort(key=lambda item: item.get("similarity", 0.0), reverse=True)
        return ranked[:limit]
