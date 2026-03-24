import pytest

pytest.importorskip("fastapi")
pytest.importorskip("httpx")

from fastapi.testclient import TestClient

from app.adapters.market_data.alpaca_dashboard_source import AlpacaDashboardSource
from app.cli.build_dashboard_data import build_parser as build_dashboard_parser
from app.cli.generate_signals import build_parser as generate_signals_parser
from app.cli.run_backtest import build_parser as run_backtest_parser
from app.cli.run_replay import build_parser as run_replay_parser
from app.services.common import INTERNAL_SIM_SOURCE
from app.services.dashboard_service import build_dashboard_dataset, create_dashboard_app


def test_task_oriented_clis_only_allow_internal_sim() -> None:
    parsers = (
        run_backtest_parser(),
        generate_signals_parser(),
        build_dashboard_parser(),
    )
    for parser in parsers:
        args = parser.parse_args([])
        assert args.source == INTERNAL_SIM_SOURCE


def test_run_replay_parser_accepts_output_path() -> None:
    args = run_replay_parser().parse_args(["--run-id", "demo-run", "--output", "tmp/out.json"])
    assert args.run_id == "demo-run"
    assert args.output == "tmp/out.json"


def test_dashboard_dataset_includes_task_sections() -> None:
    dataset = build_dashboard_dataset(with_alpaca_readonly=False, symbols=["AAPL", "MSFT"])
    assert dataset["source"] == INTERNAL_SIM_SOURCE
    assert dataset["overview"]["universe_count"] == 2
    assert dataset["universe"]["count"] == 2
    assert dataset["signals"]["rows"]
    assert dataset["backtests"]["latest"]["results"]
    assert dataset["replay_audit"]["portfolio_plan"]["symbol"] == "AAPL"
    assert dataset["alpaca_info"]["label"] == "external / read-only"
    assert dataset["pages"]["signals"] == "/signals"


def test_dashboard_app_exposes_named_pages_and_api_sections() -> None:
    client = TestClient(create_dashboard_app())
    assert client.get("/").status_code == 200
    assert client.get("/signals").status_code == 200
    assert client.get("/backtests").status_code == 200
    assert client.get("/replay").status_code == 200
    assert client.get("/alpaca").status_code == 200
    assert client.get("/api/signals").status_code == 200
    assert client.get("/api/backtests").status_code == 200


def test_alpaca_dashboard_source_falls_back_without_credentials(monkeypatch) -> None:
    monkeypatch.delenv("ALPACA_API_KEY_ID", raising=False)
    monkeypatch.delenv("ALPACA_SECRET_KEY", raising=False)
    snapshot = AlpacaDashboardSource(enabled=True).fetch_snapshot()
    assert snapshot["status"] == "degraded"
    assert snapshot["label"] == "external / read-only"
    assert "order_history" in snapshot["capabilities"]
