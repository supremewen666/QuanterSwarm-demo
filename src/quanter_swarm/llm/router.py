"""Provider routing for LLM requests."""

from __future__ import annotations

from dataclasses import dataclass, field

from quanter_swarm.llm.base import BaseLLMProvider


@dataclass
class LLMRouter:
    default_provider: BaseLLMProvider
    task_routes: dict[str, BaseLLMProvider] = field(default_factory=dict)

    def route(self, task_type: str) -> BaseLLMProvider:
        return self.task_routes.get(task_type, self.default_provider)
