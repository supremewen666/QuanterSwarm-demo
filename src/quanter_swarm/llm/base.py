"""Provider abstractions for LLM integrations."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BaseLLMProvider(ABC):
    provider_name = "base"

    @abstractmethod
    def generate(self, messages: list[dict[str, Any]], tools: list[dict[str, Any]] | None = None, **kwargs: Any) -> dict[str, Any]:
        """Generate a response for normalized messages."""
