"""Message normalization helpers for LLM providers."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from quanter_swarm.llm.exceptions import InvalidMessageError

MessageRole = Literal["system", "user", "assistant", "tool"]


class ChatMessage(BaseModel):
    model_config = ConfigDict(extra="forbid")

    role: MessageRole
    content: str = Field(min_length=1)
    name: str | None = None
    tool_call_id: str | None = None


def normalize_messages(messages: Iterable[ChatMessage | dict[str, Any] | str]) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    for item in messages:
        payload = {"role": "user", "content": item} if isinstance(item, str) else item
        try:
            message = payload if isinstance(payload, ChatMessage) else ChatMessage.model_validate(payload)
        except ValidationError as exc:
            raise InvalidMessageError("Invalid chat message payload.") from exc
        normalized.append(message.model_dump(exclude_none=True))
    if not normalized:
        raise InvalidMessageError("At least one message is required.")
    return normalized
