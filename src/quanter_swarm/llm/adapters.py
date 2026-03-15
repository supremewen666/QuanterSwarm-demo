"""LLM adapters."""


def normalize_provider_response(content: str) -> dict:
    return {"content": content}
