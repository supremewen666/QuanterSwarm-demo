import pytest
from pydantic import BaseModel

from quanter_swarm.config.settings import Settings
from quanter_swarm.llm.client import LLMClient
from quanter_swarm.llm.exceptions import StructuredOutputError
from quanter_swarm.llm.providers.mock_provider import MockLLMProvider
from quanter_swarm.llm.router import LLMRouter
from quanter_swarm.llm.structured_output import as_packet
from quanter_swarm.orchestrator.runtime import RuntimeContext
from quanter_swarm.tools.base import Tool
from quanter_swarm.tools.executor import ToolExecutor
from quanter_swarm.tools.registry import ToolRegistry


def test_llm_client_normalizes_messages() -> None:
    client = LLMClient(router=LLMRouter(default_provider=MockLLMProvider()))

    result = client.generate(["hello"])

    assert result["provider"] == "mock"
    assert result["output_text"] == "hello"


def test_structured_output_raises_on_invalid_payload() -> None:
    class Packet(BaseModel):
        score: float

    with pytest.raises(StructuredOutputError):
        as_packet({"score": "bad"}, Packet)


def test_tool_executor_captures_errors() -> None:
    class BrokenTool(Tool):
        name = "broken"

        def run(self, **kwargs: object) -> dict[str, object]:
            raise RuntimeError("boom")

    registry = ToolRegistry()
    registry.register(BrokenTool())
    executor = ToolExecutor(registry, retries=0)

    result = executor.execute("broken", {})

    assert result["status"] == "error"
    assert result["reason"] == "boom"
    assert result["error_type"] == "RuntimeError"


def test_runtime_context_builds_default_runtime() -> None:
    runtime = RuntimeContext.build(settings=Settings())

    result = runtime.tools.execute("sentiment_analysis", {"text": "strong momentum"})

    assert runtime.llm.generate(["ping"])["output_text"] == "ping"
    assert result["payload"]["score"] > 0.5
