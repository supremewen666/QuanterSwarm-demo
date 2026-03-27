"""Bounded evolution wrapper over the persistent evolution manager."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from quanter_swarm.agents.base import BaseAgent
from quanter_swarm.contracts import AgentContext, AgentResult
from quanter_swarm.services.evolution import EvolutionManager


class EvolutionAgent(BaseAgent):
    name = "evolution"
    role = "orchestrator"

    def __init__(self, *, manager: EvolutionManager | None = None, root: Path | None = None, config: dict[str, Any] | None = None) -> None:
        self.manager = manager or EvolutionManager(root=root or Path("data") / "evolution", config=config or {})

    def evolve(
        self,
        ranked_signals: list[dict],
        current_threshold: float = 0.5,
        *,
        event_payload: dict[str, Any] | None = None,
    ) -> dict:
        return self.manager.evolve(
            ranked_signals,
            current_threshold=current_threshold,
            event_payload=event_payload,
        )

    async def run(self, context: AgentContext | dict[str, Any]) -> AgentResult:
        payload = self._context_to_dict(context)
        result = self.evolve(
            payload.get("ranked_signals", []),
            float(payload.get("current_threshold", 0.5)),
            event_payload=payload.get("event_payload"),
        )
        return self._build_result(summary=str(result["action"]), payload=result)
