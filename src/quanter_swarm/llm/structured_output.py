"""Structured output helpers."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, TypeAdapter, ValidationError

from quanter_swarm.llm.exceptions import StructuredOutputError


def as_packet(data: dict[str, Any], schema: type[BaseModel] | TypeAdapter[Any] | None = None) -> dict[str, Any]:
    if schema is None:
        return data
    try:
        if isinstance(schema, TypeAdapter):
            validated = schema.validate_python(data)
            return TypeAdapter(type(validated)).dump_python(validated) if not isinstance(validated, dict) else validated
        validated_model = schema.model_validate(data)
    except ValidationError as exc:
        raise StructuredOutputError("Structured output validation failed.") from exc
    return validated_model.model_dump()
