from quanter_swarm.application import (
    FetchFundamentalsBatch,
    FetchMacroBatch,
    GenerateSignals,
    GetProviderTopology,
    PromoteLeaderVersion,
    RiskPrecheck,
    RunBacktest,
    RunBatchResearch,
    RunResearchCycle,
)


def test_run_research_cycle_use_case_returns_cycle_report() -> None:
    report = RunResearchCycle().execute(symbol="AAPL")

    assert report["symbol"] == "AAPL"
    assert report["active_regime"]
    assert report["architecture_summary"]["control_plane"]["flow"] == [
        "orchestrator",
        "router",
        "leader",
        "specialist",
    ]


def test_run_batch_research_use_case_returns_multiple_reports() -> None:
    reports = RunBatchResearch().execute(symbols=["AAPL", "MSFT"])

    assert [report["symbol"] for report in reports] == ["AAPL", "MSFT"]


def test_get_provider_topology_use_case_returns_configured_provider() -> None:
    topology = GetProviderTopology().execute()

    assert isinstance(topology["available"], list)
    assert topology["configured"]["provider"] == "deterministic"


def test_batch_data_use_cases_return_provider_payloads() -> None:
    fundamentals = FetchFundamentalsBatch().execute(symbols=["AAPL", "MSFT"])
    macro = FetchMacroBatch().execute(symbols=["AAPL", "MSFT"])

    assert set(fundamentals["results"]) == {"AAPL", "MSFT"}
    assert set(macro["results"]) == {"AAPL", "MSFT"}


def test_signal_and_backtest_use_cases_return_artifacts() -> None:
    signals = GenerateSignals().execute(symbols=["AAPL"])
    backtest = RunBacktest().execute(symbols=["AAPL"])

    assert signals["signals"]
    assert backtest["results"]


def test_risk_precheck_use_case_returns_guardrail_verdict() -> None:
    result = RiskPrecheck().execute(warnings=["panic_regime"])

    assert result["status"] == "blocked"
    assert result["approved"] is False


def test_promote_leader_version_use_case_updates_registry(tmp_path) -> None:
    result = PromoteLeaderVersion().execute(
        leader_name="momentum",
        parameter_version="v2",
        parameter_set={"lookback_window": 30},
        evidence={
            "sample_count": 30,
            "posterior_lift": 0.08,
            "confidence": 0.81,
            "drawdown": 0.1,
            "regime_robust": True,
        },
        approve=True,
        root=str(tmp_path),
    )

    assert result["promoted"] is True
    assert result["active_version"] == "v2"
