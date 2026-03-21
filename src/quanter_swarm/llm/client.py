"""Facade for normalized LLM generation."""

from __future__ import annotations

from typing import Any

from quanter_swarm.llm.messages import normalize_messages
from quanter_swarm.llm.providers.mock_provider import MockLLMProvider
from quanter_swarm.llm.router import LLMRouter


class LLMClient:
    def __init__(self, router: LLMRouter | None = None) -> None:
        self.router = router or LLMRouter(default_provider=MockLLMProvider())

    def generate(
        self,
        messages: list[dict[str, Any]] | list[str],
        *,
        model: str | None = None,
        tools: list[dict[str, Any]] | None = None,
        task_type: str = "general",
        **kwargs: Any,
    ) -> dict[str, Any]:
        provider = self.router.route(task_type)
        normalized_messages = normalize_messages(messages)
        return provider.generate(normalized_messages, tools=tools, model=model, **kwargs)

    def complete(self, prompt: str) -> str:
        return str(self.generate([prompt])["output_text"])
