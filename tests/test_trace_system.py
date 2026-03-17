from quanter_swarm.observability.trace import build_cycle_trace, new_trace_id
from quanter_swarm.orchestrator.root_agent import RootAgent


def test_build_cycle_trace_contains_required_fields() -> None:
    trace = build_cycle_trace(
        trace_id=new_trace_id("cycle"),
        router_decision={"regime": "trend_up", "confidence": 0.8},
        agents_activated={"leaders": ["momentum"], "specialists": ["risk"]},
        runtime_ms=123,
        risk_result={"status": "pass", "approved": True},
        metrics={"router_latency": {"routing_ms": 5}},
    )
    assert trace["trace_id"].startswith("cycle_")
    assert trace["router_decision"]["regime"] == "trend_up"
    assert trace["agents_activated"]["leaders"] == ["momentum"]
    assert trace["latency"]["runtime_ms"] == 123
    assert trace["risk_result"]["status"] == "pass"
    assert trace["metrics"]["router_latency"]["routing_ms"] == 5


def test_root_agent_emits_structured_trace() -> None:
    report = RootAgent().run_sync("AAPL")
    trace = report["decision_trace_summary"]["trace"]
    assert trace["trace_id"] == report["decision_trace_summary"]["trace_id"]
    assert trace["router_decision"]["leader_selected"] == report["router_decision"]["leader_selected"]
    assert trace["agents_activated"]["specialists"] == report["router_decision"]["specialists_selected"]
    assert trace["latency"]["runtime_ms"] == report["decision_trace_summary"]["runtime_ms"]
    assert trace["metrics"] == report["decision_trace_summary"]["metrics"]
