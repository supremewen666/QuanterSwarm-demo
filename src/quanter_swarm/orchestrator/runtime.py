"""Runtime context for orchestration."""

from __future__ import annotations

from dataclasses import dataclass

from quanter_swarm.config.settings import Settings
from quanter_swarm.data.base import BaseDataProvider
from quanter_swarm.llm.client import LLMClient
from quanter_swarm.llm.providers.mock_provider import MockLLMProvider
from quanter_swarm.llm.router import LLMRouter
from quanter_swarm.tools.builtin import build_default_tool_registry
from quanter_swarm.tools.executor import ToolExecutor


@dataclass
class RuntimeContext:
    llm: LLMClient
    tools: ToolExecutor
    settings: Settings

    @classmethod
    def build(cls, *, settings: Settings, provider: BaseDataProvider | None = None) -> RuntimeContext:
        tool_registry = build_default_tool_registry(provider=provider, allowed_tools=settings.allowed_tools)
        llm_provider_name = settings.llm_provider.strip().lower()
        if llm_provider_name == "openai":
            try:
                from quanter_swarm.llm.providers.openai_provider import OpenAIProvider

                llm_provider = OpenAIProvider(default_model=settings.llm_model)
            except ModuleNotFoundError:
                llm_provider = MockLLMProvider()
        elif llm_provider_name == "anthropic":
            try:
                from quanter_swarm.llm.providers.anthropic_provider import AnthropicProvider

                llm_provider = AnthropicProvider(default_model=settings.llm_model)
            except ModuleNotFoundError:
                llm_provider = MockLLMProvider()
        else:
            llm_provider = MockLLMProvider()
        return cls(
            llm=LLMClient(router=LLMRouter(default_provider=llm_provider)),
            tools=ToolExecutor(tool_registry, timeout_seconds=float(settings.tool_timeout)),
            settings=settings,
        )
