"""Regime classifier."""

from __future__ import annotations

from typing import Any

from quanter_swarm.agents.base import BaseAgent
from quanter_swarm.contracts import AgentContext, AgentResult
from quanter_swarm.router import detect_regime


class RegimeAgent(BaseAgent):
    name = "regime"
    role = "orchestrator"

    def classify_detail(
        self,
        market_state: dict,
        previous_regime: str | None = None,
        hysteresis_margin: float = 0.08,
    ) -> dict:
        return detect_regime(
            market_state,
            previous_regime=previous_regime,
            hysteresis_margin=hysteresis_margin,
        )

    def classify(self, market_state: dict, previous_regime: str | None = None) -> str:
        result = self.classify_detail(market_state, previous_regime=previous_regime)
        return str(result["label"])

    async def run(self, context: AgentContext | dict[str, Any]) -> AgentResult:
        payload = self._context_to_dict(context)
        market_state = payload.get("market_state", payload.get("market_summary", payload))
        previous_regime = payload.get("previous_regime")
        result = self.classify_detail(market_state, previous_regime=previous_regime)
        return self._build_result(summary=str(result["label"]), payload=result)
