"""Monitoring-specific logger facade."""

from __future__ import annotations

from logging import Logger

from quanter_swarm.utils.logging import get_logger


def get_monitoring_logger() -> Logger:
    return get_logger("quanter_swarm.monitoring")
