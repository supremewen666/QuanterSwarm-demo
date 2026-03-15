"""Validation helpers."""


def require_keys(payload: dict, keys: list[str]) -> bool:
    return all(key in payload for key in keys)
