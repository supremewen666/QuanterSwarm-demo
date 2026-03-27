"""Logging helpers."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

try:
    import yaml
except ModuleNotFoundError:  # pragma: no cover - exercised in lightweight environments
    yaml = None

_STRUCTURED_FIELDS = ("trace_id", "cycle_state", "agent_name", "latency", "status")


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "message": record.getMessage(),
            "level": record.levelname,
            "logger": record.name,
        }
        for field in _STRUCTURED_FIELDS:
            payload[field] = getattr(record, field, None)
        return json.dumps(payload, ensure_ascii=False)


def configure_logging(config_path: Path | str = "configs/logging.yaml") -> None:
    path = Path(config_path)
    config: dict[str, Any] = {}
    if path.exists() and yaml is not None:
        config = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    logging_config = config.get("logging", {})
    level_name = str(logging_config.get("level", "INFO")).upper()
    json_logging = bool(logging_config.get("json", False))
    root_logger = logging.getLogger()
    root_logger.setLevel(level_name)
    handler = logging.StreamHandler()
    if json_logging:
        handler.setFormatter(JsonFormatter())
    else:
        handler.setFormatter(logging.Formatter(str(logging_config.get("format", "%(message)s"))))
    root_logger.handlers = [handler]


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
