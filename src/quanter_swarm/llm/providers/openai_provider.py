"""OpenAI chat provider."""

from __future__ import annotations

import os
from typing import Any

import httpx

from quanter_swarm.llm.base import BaseLLMProvider
from quanter_swarm.llm.exceptions import LLMConfigurationError, LLMProviderError


class OpenAIProvider(BaseLLMProvider):
    provider_name = "openai"

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str = "https://api.openai.com/v1",
        timeout_seconds: float = 30.0,
        default_model: str = "gpt-4.1-mini",
    ) -> None:
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
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
            raise LLMConfigurationError("OPENAI_API_KEY is not configured.")
        payload: dict[str, Any] = {
            "model": kwargs.get("model", self.default_model),
            "messages": messages,
        }
        if tools:
            payload["tools"] = tools
        if "temperature" in kwargs:
            payload["temperature"] = kwargs["temperature"]
        try:
            response = httpx.post(
                f"{self.base_url}/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json=payload,
                timeout=self.timeout_seconds,
            )
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise LLMProviderError("OpenAI request failed.") from exc
        data = response.json()
        choice = data["choices"][0]["message"]
        return {
            "provider": self.provider_name,
            "model": data.get("model", payload["model"]),
            "output_text": choice.get("content", ""),
            "content": [{"type": "text", "text": choice.get("content", "")}],
            "tool_calls": choice.get("tool_calls", []),
            "usage": data.get("usage", {}),
            "finish_reason": data["choices"][0].get("finish_reason"),
            "raw_response": data,
        }
