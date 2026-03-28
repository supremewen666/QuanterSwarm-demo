import pytest

from quanter_swarm.agents.orchestrator.cycle_manager import CycleManager
from quanter_swarm.core import AgentExecutionError


class _BrokenLeader:
    def propose(self, context: dict) -> dict:
        return {"leader": "broken", "symbol": context["symbol"], "score": 0.9}


def test_cycle_fails_when_leader_output_breaks_contract(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("quanter_swarm.agents.orchestrator.cycle_manager.get_leader", lambda name: _BrokenLeader())
    with pytest.raises(AgentExecutionError, match="produced invalid output"):
        CycleManager().run_cycle("AAPL", persist_outputs=False)
