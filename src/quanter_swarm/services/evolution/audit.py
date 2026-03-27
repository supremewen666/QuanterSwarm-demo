"""Append-only evolution audit log."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class EvolutionAuditLog:
    def __init__(self, root: Path) -> None:
        self.path = root / "audit_log.jsonl"

    def write(self, payload: dict[str, Any]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, sort_keys=True) + "\n")
