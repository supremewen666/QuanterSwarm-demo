import io
import json
import logging
from pathlib import Path

from quanter_swarm.orchestrator.root_agent import RootAgent
from quanter_swarm.utils.logging import JsonFormatter, configure_logging


def test_json_formatter_emits_structured_fields() -> None:
    record = logging.LogRecord("quanter", logging.INFO, __file__, 1, "cycle message", (), None)
    record.trace_id = "cycle_123"
    record.cycle_state = "routing"
    record.agent_name = "router"
    record.latency = 42
    record.status = "ok"
    payload = json.loads(JsonFormatter().format(record))
    assert payload["trace_id"] == "cycle_123"
    assert payload["cycle_state"] == "routing"
    assert payload["agent_name"] == "router"
    assert payload["latency"] == 42
    assert payload["status"] == "ok"


def test_cycle_manager_emits_structured_json_logs(tmp_path: Path) -> None:
    config_path = tmp_path / "logging.yaml"
    config_path.write_text("logging:\n  level: INFO\n  json: true\n", encoding="utf-8")
    stream = io.StringIO()
    configure_logging(config_path)
    root_logger = logging.getLogger()
    root_logger.handlers[0].stream = stream

    RootAgent().run_sync("AAPL")

    lines = [json.loads(line) for line in stream.getvalue().splitlines() if line.strip()]
    assert any(line["cycle_state"] == "data_fetch" for line in lines)
    assert any(line["cycle_state"] == "report_generation" for line in lines)
    assert all({"trace_id", "cycle_state", "agent_name", "latency", "status"} <= set(line) for line in lines)
