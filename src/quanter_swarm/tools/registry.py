"""Registry for executable tools."""

from __future__ import annotations

from quanter_swarm.errors import RouterError
from quanter_swarm.tools.base import Tool


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        name = getattr(tool, "name", "").strip()
        if not name:
            raise RouterError("Cannot register unnamed tool.")
        self._tools[name] = tool

    def get(self, name: str) -> Tool:
        try:
            return self._tools[name]
        except KeyError as exc:
            raise RouterError(f"Unknown tool '{name}'") from exc

    def names(self) -> list[str]:
        return sorted(self._tools)
