"""Monitoring-specific logger facade."""

from __future__ import annotations

from logging import Logger

from quanter_swarm.core.runtime.logging import get_logger


def get_monitoring_logger() -> Logger:
    return get_logger("quanter_swarm.services.monitoring")
