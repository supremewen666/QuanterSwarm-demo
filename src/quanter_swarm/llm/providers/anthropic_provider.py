"""Anthropic messages provider."""

from __future__ import annotations

import os
from typing import Any

import httpx

from quanter_swarm.llm.base import BaseLLMProvider
from quanter_swarm.llm.exceptions import LLMConfigurationError, LLMProviderError


class AnthropicProvider(BaseLLMProvider):
    provider_name = "anthropic"

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str = "https://api.anthropic.com/v1",
        timeout_seconds: float = 30.0,
        default_model: str = "claude-3-5-sonnet-latest",
    ) -> None:
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds
        self.default_model = default_model

    def generate(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        if not self.api_key:
            raise LLMConfigurationError("ANTHROPIC_API_KEY is not configured.")
        system_messages = [message["content"] for message in messages if message["role"] == "system"]
        conversational_messages = [message for message in messages if message["role"] != "system"]
        payload: dict[str, Any] = {
            "model": kwargs.get("model", self.default_model),
            "messages": conversational_messages,
            "max_tokens": kwargs.get("max_tokens", 512),
        }
        if system_messages:
            payload["system"] = "\n".join(system_messages)
        if tools:
            payload["tools"] = tools
        try:
            response = httpx.post(
                f"{self.base_url}/messages",
                headers={
                    "x-api-key": self.api_key,
                    "anthropic-version": "2023-06-01",
                },
                json=payload,
                timeout=self.timeout_seconds,
            )
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise LLMProviderError("Anthropic request failed.") from exc
        data = response.json()
        text_blocks = [block.get("text", "") for block in data.get("content", []) if block.get("type") == "text"]
        return {
            "provider": self.provider_name,
            "model": data.get("model", payload["model"]),
            "output_text": "\n".join(text_blocks).strip(),
            "content": data.get("content", []),
            "tool_calls": [block for block in data.get("content", []) if block.get("type") == "tool_use"],
            "usage": data.get("usage", {}),
            "finish_reason": data.get("stop_reason"),
            "raw_response": data,
        }
