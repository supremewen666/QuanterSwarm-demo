"""Mock provider used for tests and local fallback."""

from __future__ import annotations

from typing import Any

from quanter_swarm.llm.base import BaseLLMProvider


class MockLLMProvider(BaseLLMProvider):
    provider_name = "mock"

    def generate(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        last_message = messages[-1]
        content = str(last_message.get("content", ""))
        return {
            "provider": self.provider_name,
            "model": kwargs.get("model", "mock-echo"),
            "output_text": content,
            "content": [{"type": "text", "text": content}],
            "tool_calls": [],
            "usage": {"input_tokens": 0, "output_tokens": 0},
            "finish_reason": "stop",
        }
