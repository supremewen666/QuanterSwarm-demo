"""Exceptions for the LLM runtime."""

from __future__ import annotations


class LLMError(Exception):
    """Base error for LLM runtime failures."""


class LLMConfigurationError(LLMError):
    """Raised when an LLM provider is misconfigured."""


class LLMProviderError(LLMError):
    """Raised when an upstream LLM provider call fails."""


class InvalidMessageError(LLMError):
    """Raised when chat messages fail schema validation."""


class StructuredOutputError(LLMError):
    """Raised when structured output validation fails."""
