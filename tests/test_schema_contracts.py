import pytest
from pydantic import ValidationError

from quanter_swarm.orchestrator.cycle_manager import CycleManager


class _BrokenLeader:
    def propose(self, context: dict) -> dict:
        return {"leader": "broken", "symbol": context["symbol"], "score": 0.9}


def test_cycle_fails_when_leader_output_breaks_contract(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("quanter_swarm.orchestrator.cycle_manager.get_leader", lambda name: _BrokenLeader())
    with pytest.raises(ValidationError):
        CycleManager().run_cycle("AAPL", persist_outputs=False)
