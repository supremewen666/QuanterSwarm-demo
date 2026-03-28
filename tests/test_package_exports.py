from quanter_swarm import RunResearchCycle, Status
from quanter_swarm.adapters import InternalSimSource, api_app, dashboard_app
from quanter_swarm.agents.leaders import MomentumLeader, get_leader
from quanter_swarm.agents.orchestrator import RootAgent
from quanter_swarm.agents.specialists import DataFetchSpecialist
from quanter_swarm.core import (
    AgentContext,
    BacktestError,
    CacheStore,
    load_settings,
    new_id,
    new_trace_id,
    write_json,
)
from quanter_swarm.services import (
    ConfiguredExperimentRunner,
    execute,
    execution_allowed,
    generate_report,
    rank_candidates,
)


def test_root_package_exports() -> None:
    assert RunResearchCycle.__name__ == "RunResearchCycle"
    assert Status.OK == "ok"


def test_core_package_exports(tmp_path) -> None:
    assert AgentContext(symbol="AAPL").symbol == "AAPL"
    assert issubclass(BacktestError, Exception)
    assert isinstance(CacheStore(), CacheStore)
    assert new_id("run").startswith("run_")
    assert new_trace_id().startswith("trace_")
    assert load_settings().environment

    destination = tmp_path / "artifact.json"
    write_json(destination, {"ok": True})
    assert destination.exists()


def test_service_package_exports() -> None:
    assert ConfiguredExperimentRunner.__name__ == "ConfiguredExperimentRunner"
    assert rank_candidates([]) == []
    assert execution_allowed("paper") == (True, "paper_mode_enabled")
    assert execute({"symbol": "AAPL", "side": "buy", "qty": 1}, config_dir=None)["executed"] is True
    assert generate_report.__name__ == "generate_report"


def test_adapter_and_agent_exports() -> None:
    assert api_app.title == "QuanterSwarm"
    assert dashboard_app is not None
    assert isinstance(InternalSimSource(), InternalSimSource)
    assert RootAgent.role == "orchestrator"
    assert MomentumLeader.name == "momentum"
    assert get_leader("momentum").name == "momentum"
    assert DataFetchSpecialist.name == "data_fetch"
