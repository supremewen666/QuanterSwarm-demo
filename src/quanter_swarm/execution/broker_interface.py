"""Execution broker contract."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BrokerInterface(ABC):
    @abstractmethod
    def submit(self, order: dict[str, Any]) -> dict[str, Any]:
        """Submit an order and return an execution result."""
