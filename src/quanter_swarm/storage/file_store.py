"""File storage helpers."""

import json
from pathlib import Path
from typing import Any


def write_text(path: str, content: str) -> None:
    Path(path).write_text(content, encoding="utf-8")


def write_json(path: str | Path, payload: dict[str, Any]) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
