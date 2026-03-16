"""Cycle execution coordinator."""

from __future__ import annotations

from statistics import mean
from time import time
from typing import Any

from quanter_swarm.contracts import (
    FinalReportContract,
    LeaderOutputContract,
    PaperTradeActionContract,
    PortfolioSuggestionContract,
    RankedIdeaContract,
)
from quanter_swarm.decision.execution_gate import execution_allowed
from quanter_swarm.decision.order_sizer import size_order
from quanter_swarm.decision.portfolio_suggestion import build_portfolio
from quanter_swarm.decision.risk_guardrail import assess_guardrails
from quanter_swarm.evaluation.metrics import summarize_metrics
from quanter_swarm.execution.paper_executor import execute
from quanter_swarm.leaders.leader_factory import get_leader
from quanter_swarm.market.data_quality import validate_snapshot
from quanter_swarm.orchestrator.evolution_agent import EvolutionAgent
from quanter_swarm.orchestrator.ranking_engine import rank_candidates
from quanter_swarm.orchestrator.regime_agent import RegimeAgent
from quanter_swarm.orchestrator.router_agent import RouterAgent
from quanter_swarm.orchestrator.states import CycleStage, StageRecord
from quanter_swarm.reporting.report_generator import generate_report
from quanter_swarm.research.event_impact_analyzer import analyze_event_impact
from quanter_swarm.research.factor_score_engine import compute_factor_score
from quanter_swarm.research.fundamentals_parser import parse_fundamentals
from quanter_swarm.specialists.data_fetch_specialist import DataFetchSpecialist
from quanter_swarm.specialists.feature_engineering_specialist import FeatureEngineeringSpecialist
from quanter_swarm.specialists.macro_event_specialist import MacroEventSpecialist
from quanter_swarm.specialists.memory_compression_specialist import MemoryCompressionSpecialist
from quanter_swarm.specialists.risk_specialist import RiskSpecialist
from quanter_swarm.specialists.sentiment_specialist import SentimentSpecialist
from quanter_swarm.storage.file_store import write_json
from quanter_swarm.utils.config import (
    config_provenance,
    load_runtime_configs,
    load_settings,
    load_yaml,
    validate_config_consistency,
)
from quanter_swarm.utils.tracing import new_trace_id


class CycleManager:
    def __init__(self) -> None:
        self.settings = load_settings()
        validate_config_consistency(self.settings.config_dir)
        self.router_config = load_yaml(self.settings.config_dir / "router.yaml")
        self.regimes_config = load_yaml(self.settings.config_dir / "regimes.yaml")
        self.portfolio_config = load_yaml(self.settings.config_dir / "portfolio.yaml")
        self.risk_config = load_yaml(self.settings.config_dir / "risk.yaml")
        self.ranking_config = load_yaml(self.settings.config_dir / "ranking.yaml")
        self.evolution_config = load_yaml(self.settings.config_dir / "evolution.yaml")
        self.config_snapshot = config_provenance(load_runtime_configs(self.settings.config_dir))
        self._last_regime: str | None = None

    def _short_circuit_report(
        self,
        *,
        symbol: str,
        trace_id: str,
        runtime_ms: int,
        regime: str,
        regime_confidence: float,
        market_summary: dict[str, Any],
        fallback_modes: list[str],
        termination_reason: str,
        stage_records: list[StageRecord],
    ) -> dict[str, Any]:
        payload = {
            "symbol": symbol,
            "active_regime": regime,
            "regime_confidence": regime_confidence,
            "active_strategy_teams": [],
            "market_summary": market_summary,
            "fundamentals_summary": {},
            "sentiment_summary": {"score": 0.5, "compressed_context": ""},
            "event_impact_summary": {"impact_score": 0.5, "horizon": "1d-1w"},
            "factor_score": 0.0,
            "risk_alerts": [termination_reason],
            "portfolio_suggestion": {
                "positions": [],
                "cash_buffer": 1.0,
                "gross_exposure": 0.0,
                "mode": "no_trade",
                "allocation_mode": "simple",
                "rationale": termination_reason,
                "no_trade_reason": termination_reason,
                "position_rationales": [],
            },
            "paper_trade_actions": [],
            "decision_trace_summary": {
                "trace_id": trace_id,
                "runtime_ms": runtime_ms,
                "fallback_modes": fallback_modes,
                "routing": {"selected_reasons": {}, "skipped_reasons": {}, "low_confidence_mode": True},
                "leader_scores": [],
                "risk_guardrail": {"status": "blocked", "reason": termination_reason, "exposure_multiplier": 0.0},
                "rejected_candidates": [],
                "portfolio_scaling": {"mode": "no_trade", "gross_exposure": 0.0, "cash_buffer": 1.0},
                "execution_assumptions": {},
                "state_machine": {
                    "terminated": True,
                    "termination_reason": termination_reason,
                    "stages": [
                        {"stage": record.stage.value, "status": record.status, "detail": record.detail}
                        for record in stage_records
                    ],
                },
            },
            "config_provenance": self.config_snapshot,
            "evaluation_summary": {
                "top_signal": None,
                "signal_count": 0,
                "metrics": summarize_metrics([]),
                "execution_reason": "paper_mode_enabled",
                "guardrail": {"status": "blocked", "reason": termination_reason, "exposure_multiplier": 0.0},
                "evolution": {"action": "short_circuit"},
            },
        }
        report = generate_report(payload)
        FinalReportContract.model_validate(report)
        return report

    def run_cycle(
        self,
        symbol: str | None = None,
        scenario: dict[str, Any] | None = None,
        persist_outputs: bool = True,
    ) -> dict[str, Any]:
        scenario = scenario or {}
        started_at = int(time())
        run_started = time()
        trace_id = new_trace_id("cycle")
        stage_records: list[StageRecord] = []
        target_symbol = symbol or self.settings.default_symbols[0]
        fetched = DataFetchSpecialist().fetch(target_symbol)
        stage_records.append(
            StageRecord(
                stage=CycleStage.INGEST,
                status="ok",
                detail={"symbol": target_symbol, "has_market_packet": bool(fetched.get("market_packet"))},
            )
        )
        if scenario.get("drop_news"):
            fetched["news_inputs"] = []
        if scenario.get("drop_fundamentals"):
            fetched["fundamentals_packet"] = {"symbol": target_symbol}
        data_quality = validate_snapshot(fetched)
        if scenario.get("force_no_data") or not fetched.get("market_packet"):
            stage_records.append(
                StageRecord(
                    stage=CycleStage.REPORT,
                    status="short_circuit",
                    detail={"reason": "no_data"},
                )
            )
            return self._short_circuit_report(
                symbol=target_symbol,
                trace_id=trace_id,
                runtime_ms=int((time() - run_started) * 1000),
                regime="sideways",
                regime_confidence=0.0,
                market_summary={"data_quality": data_quality},
                fallback_modes=["no_data_fallback"],
                termination_reason="no_data",
                stage_records=stage_records,
            )
        compressed = MemoryCompressionSpecialist().compress(fetched)

        market_packet = fetched["market_packet"]
        macro_inputs = fetched["macro_inputs"]
        market_state = {
            "avg_change_pct": market_packet["change_pct"],
            "volatility": market_packet["volatility"],
            "macro_risk": macro_inputs["macro_risk"],
            "volume_anomaly": min(1.0, abs(market_packet["change_pct"]) * 10),
            "breadth": 0.55 if market_packet["change_pct"] >= 0 else 0.45,
            "correlation": min(1.0, 0.3 + market_packet["volatility"] * 8),
            "dispersion": min(1.0, market_packet["volatility"] * 10),
            "event_density": 0.7 if macro_inputs["macro_theme"] == "policy_uncertainty" else 0.3,
        }
        regime_decision = RegimeAgent().classify_detail(market_state, previous_regime=self._last_regime)
        stage_records.append(
            StageRecord(
                stage=CycleStage.REGIME,
                status="ok",
                detail={"label": regime_decision["label"], "confidence": regime_decision["confidence"]},
            )
        )
        regime = regime_decision["label"]
        self._last_regime = regime
        route = RouterAgent().route(regime_decision, self.router_config, self.regimes_config)
        stage_records.append(
            StageRecord(
                stage=CycleStage.ROUTE,
                status="ok",
                detail={"leaders": route["leaders"], "low_confidence_mode": route["low_confidence_mode"]},
            )
        )
        if scenario.get("always_on_leaders"):
            all_leaders = sorted(
                {
                    leader
                    for config in self.regimes_config.get("regimes", {}).values()
                    for leader in config.get("leaders", [])
                }
            )
            route["leaders"] = all_leaders
            route["leader_weights"] = {leader: round(1 / max(1, len(all_leaders)), 4) for leader in all_leaders}
            route["selected_reasons"] = {leader: "forced_by_router_ablation" for leader in all_leaders}
            route["skipped_reasons"] = {}
        scenario_max_active = scenario.get("max_active_leaders")
        if isinstance(scenario_max_active, int) and scenario_max_active > 0:
            dropped = route["leaders"][scenario_max_active:]
            for leader in dropped:
                route["skipped_reasons"][leader] = "dropped_by_scenario_max_active"
            route["leaders"] = route["leaders"][:scenario_max_active]

        disable_specialists = scenario.get("disable_specialists", {})
        fallback_modes: list[str] = []
        if scenario.get("drop_fundamentals"):
            fallback_modes.append("fundamentals_fallback")
        if disable_specialists.get("sentiment") or "missing_news" in data_quality["issues"]:
            sentiment_score = 0.5
            fallback_modes.append("sentiment_fallback")
        else:
            sentiment_score = mean(SentimentSpecialist().score(item) for item in fetched["news_inputs"])
        event_signal = (
            {"impact": "neutral", "confidence": 0.5, "event": macro_inputs}
            if disable_specialists.get("macro_event")
            else MacroEventSpecialist().analyze(macro_inputs)
        )
        if disable_specialists.get("macro_event"):
            fallback_modes.append("macro_event_fallback")
        stage_records.append(
            StageRecord(
                stage=CycleStage.SPECIALIST_RESEARCH,
                status="ok",
                detail={"fallback_modes": fallback_modes},
            )
        )
        event_impact = analyze_event_impact(event_signal)
        parsed_fundamentals = parse_fundamentals(fetched["fundamentals_packet"])
        features = FeatureEngineeringSpecialist().build(fetched)["features"]
        factor_score = compute_factor_score(
            {
                "trend": max(0.0, 0.5 + features["trend"] * 5),
                "value": features["value"],
                "quality": parsed_fundamentals["quality_score"],
                "sentiment": sentiment_score,
                "event": event_impact["impact_score"],
            }
        )

        leader_context = {
            "symbol": target_symbol,
            "features": features,
            "event_impact": event_signal,
            "compressed_context": compressed["summary"],
        }
        risk_report = RiskSpecialist().assess(
            {
                "volatility": features["volatility"],
                "macro_risk": macro_inputs["macro_risk"],
            }
        )
        risk_penalty = min(0.6, len(risk_report["warnings"]) * 0.2)
        signals = []
        for name in route["leaders"]:
            proposal = get_leader(name).propose(leader_context)
            LeaderOutputContract.model_validate(proposal)
            proposal["regime_fit"] = 0.8
            proposal["risk_penalty"] = risk_penalty
            proposal["leader_weight"] = route["leader_weights"].get(name, 0.0)
            proposal["volatility"] = features["volatility"]
            proposal["correlation"] = market_state["correlation"]
            proposal["event_risk"] = market_state["event_density"]
            proposal["confidence"] = min(1.0, max(0.1, proposal["score"] * 0.8 + route["regime_confidence"] * 0.2))
            signals.append(proposal)
        stage_records.append(
            StageRecord(
                stage=CycleStage.LEADER_PROPOSAL,
                status="ok",
                detail={"proposal_count": len(signals)},
            )
        )
        ranked_signals = rank_candidates(signals)
        for signal in ranked_signals:
            RankedIdeaContract.model_validate(signal)
        stage_records.append(
            StageRecord(
                stage=CycleStage.RANK,
                status="ok",
                detail={"ranked_count": len(ranked_signals)},
            )
        )

        guardrail = assess_guardrails(risk_report)
        stage_records.append(
            StageRecord(
                stage=CycleStage.RISK,
                status="ok",
                detail={"guardrail_status": guardrail["status"], "warnings": risk_report["warnings"]},
            )
        )

        cash_buffer = self.portfolio_config.get("portfolio", {}).get("cash_buffer", 0.1)
        target_positions = self.portfolio_config.get("portfolio", {}).get("target_positions")
        allocation_mode = scenario.get("allocation_mode", self.portfolio_config.get("portfolio", {}).get("allocation_mode", "simple"))
        correlation_penalty = self.portfolio_config.get("portfolio", {}).get("correlation_penalty", 0.3)
        turnover_penalty = self.portfolio_config.get("portfolio", {}).get("turnover_penalty", 0.15)
        regime_overrides = self.portfolio_config.get("portfolio", {}).get("regime_overrides", {})
        if scenario.get("force_no_trade"):
            override = dict(regime_overrides.get(regime, {}))
            override.update({"exposure_multiplier": 0.0, "cash_buffer": 1.0, "target_positions": 0})
            regime_overrides = {**regime_overrides, regime: override}
        max_single_weight = self.risk_config.get("risk", {}).get("max_single_weight", 0.25)
        threshold = self.ranking_config.get("ranking", {}).get("signal_threshold", 0.5)
        passed_ideas = [idea for idea in ranked_signals if idea.get("composite_rank_score", 0.0) >= threshold]
        rejected_ideas = [
            {
                "leader": idea["leader"],
                "symbol": idea["symbol"],
                "reason": "below_signal_threshold"
                if idea.get("composite_rank_score", 0.0) < threshold
                else "blocked_by_guardrail",
            }
            for idea in ranked_signals
            if idea not in passed_ideas or guardrail["status"] == "blocked"
        ]
        scenario_exposure_multiplier = 0.0 if scenario.get("force_no_trade") else guardrail["exposure_multiplier"]
        if scenario.get("force_no_trade"):
            fallback_modes.append("forced_no_trade_mode")
        portfolio = build_portfolio(
            ideas=passed_ideas if guardrail["status"] != "blocked" else [],
            cash_buffer=cash_buffer,
            max_single_weight=max_single_weight,
            exposure_multiplier=scenario_exposure_multiplier,
            target_positions=target_positions,
            allocation_mode=allocation_mode,
            regime=regime,
            regime_overrides=regime_overrides,
            correlation_penalty=correlation_penalty,
            turnover_penalty=turnover_penalty,
        )
        PortfolioSuggestionContract.model_validate(portfolio)
        stage_records.append(
            StageRecord(
                stage=CycleStage.ALLOCATE,
                status="ok",
                detail={"mode": portfolio["mode"], "gross_exposure": portfolio["gross_exposure"]},
            )
        )
        if route["low_confidence_mode"] and not route["leaders"]:
            stage_records.append(
                StageRecord(
                    stage=CycleStage.REPORT,
                    status="short_circuit",
                    detail={"reason": "low_confidence_no_trade"},
                )
            )
            return self._short_circuit_report(
                symbol=target_symbol,
                trace_id=trace_id,
                runtime_ms=int((time() - run_started) * 1000),
                regime=regime,
                regime_confidence=regime_decision["confidence"],
                market_summary={
                    "price": market_packet["price"],
                    "change_pct": market_packet["change_pct"],
                    "volatility": market_packet["volatility"],
                    "data_quality": data_quality,
                },
                fallback_modes=fallback_modes + ["low_confidence_no_trade"],
                termination_reason="low_confidence_no_trade",
                stage_records=stage_records,
            )

        paper_trade_actions: list[dict[str, Any]] = []
        execution_ok, execution_reason = execution_allowed(self.settings.execution_mode)
        execution_assumptions: dict[str, Any] = {}
        if execution_ok:
            for position in portfolio["positions"]:
                order_value = size_order(position["weight"], self.settings.starting_capital)
                action = execute(
                    {
                        "symbol": position["symbol"],
                        "leader": position["leader"],
                        "notional": order_value,
                        "reference_price": market_packet["price"],
                        "decision_price": market_packet["price"],
                        "volatility": market_packet["volatility"],
                        "avg_volume": market_packet["avg_volume"],
                        "is_open_session": True,
                        "gap_pct": market_packet["change_pct"],
                        "event_window": market_state["event_density"] >= 0.6,
                    },
                    config_dir=self.settings.config_dir,
                )
                paper_trade_actions.append(action)
                execution_assumptions = action.get("audit", {}).get("fill_assumption", {})
        stage_records.append(
            StageRecord(
                stage=CycleStage.EXECUTE,
                status="ok",
                detail={"execution_ok": execution_ok, "action_count": len(paper_trade_actions)},
            )
        )
        for action in paper_trade_actions:
            PaperTradeActionContract.model_validate(action)

        simulated_returns = [
            round(signal.get("composite_rank_score", 0.0) - 0.5 - signal.get("risk_penalty", 0.0) / 2, 4)
            for signal in ranked_signals
        ]
        metrics = summarize_metrics(simulated_returns)
        evolution_enabled = self.evolution_config.get("evolution", {}).get("enabled", True)
        evolution_summary = (
            EvolutionAgent().evolve(ranked_signals, threshold) if evolution_enabled else {"threshold": threshold, "action": "disabled"}
        )

        report_payload = {
            "symbol": target_symbol,
            "active_regime": regime,
            "regime_confidence": regime_decision["confidence"],
            "active_strategy_teams": route["leaders"],
            "market_summary": {
                "price": market_packet["price"],
                "change_pct": market_packet["change_pct"],
                "volatility": market_packet["volatility"],
                "data_quality": data_quality,
            },
            "fundamentals_summary": parsed_fundamentals,
            "sentiment_summary": {"score": round(sentiment_score, 2), "compressed_context": compressed["summary"]},
            "event_impact_summary": event_impact,
            "factor_score": factor_score,
            "risk_alerts": risk_report["warnings"],
            "portfolio_suggestion": portfolio,
            "paper_trade_actions": paper_trade_actions,
            "decision_trace_summary": {
                "trace_id": trace_id,
                "runtime_ms": int((time() - run_started) * 1000),
                "regime": regime_decision,
                "fallback_modes": fallback_modes,
                "specialist_contribution": {
                    "sentiment_score": round(sentiment_score, 4),
                    "event_impact_score": event_impact.get("impact_score", 0.0),
                    "factor_score": factor_score,
                },
                "routing": {
                    "selected_reasons": route["selected_reasons"],
                    "skipped_reasons": route["skipped_reasons"],
                    "low_confidence_mode": route["low_confidence_mode"],
                },
                "leader_scores": [
                    {
                        "leader": signal["leader"],
                        "score": signal["score"],
                        "rank_score": signal.get("composite_rank_score", 0.0),
                        "risk_penalty": signal.get("risk_penalty", 0.0),
                    }
                    for signal in ranked_signals
                ],
                "risk_guardrail": guardrail,
                "rejected_candidates": rejected_ideas,
                "portfolio_scaling": {
                    "mode": portfolio.get("mode"),
                    "gross_exposure": portfolio.get("gross_exposure", 0.0),
                    "cash_buffer": portfolio.get("cash_buffer", 1.0),
                },
                "execution_assumptions": execution_assumptions,
                "state_machine": {
                    "terminated": portfolio.get("mode") == "no_trade",
                    "termination_reason": "no_trade" if portfolio.get("mode") == "no_trade" else "",
                    "stages": [
                        {"stage": record.stage.value, "status": record.status, "detail": record.detail}
                        for record in stage_records
                    ],
                },
            },
            "config_provenance": self.config_snapshot,
            "evaluation_summary": {
                "top_signal": ranked_signals[0] if ranked_signals else None,
                "signal_count": len(ranked_signals),
                "metrics": metrics,
                "execution_reason": execution_reason,
                "guardrail": guardrail,
                "evolution": evolution_summary,
            },
        }
        report = generate_report(report_payload)
        stage_records.append(
            StageRecord(
                stage=CycleStage.REPORT,
                status="ok",
                detail={"symbol": report["symbol"], "regime": report["active_regime"]},
            )
        )
        report["decision_trace_summary"]["state_machine"]["stages"] = [
            {"stage": record.stage.value, "status": record.status, "detail": record.detail}
            for record in stage_records
        ]
        FinalReportContract.model_validate(report)
        cycle_id = f"{target_symbol.lower()}_{started_at}"
        if persist_outputs:
            write_json(self.settings.data_dir / "reports" / f"{cycle_id}.json", report)
            if paper_trade_actions:
                write_json(
                    self.settings.data_dir / "paper_trades" / f"{cycle_id}.json",
                    {"symbol": target_symbol, "actions": paper_trade_actions, "metrics": metrics},
                )
        return report
