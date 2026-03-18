"""Cycle execution coordinator."""

from __future__ import annotations

from datetime import datetime
from statistics import mean
from time import time
from typing import TYPE_CHECKING, Any, cast

from pydantic import ValidationError

from quanter_swarm.agents.registry import get_agent, get_leader, get_specialist
from quanter_swarm.config.defaults import DEFAULT_RISK_THRESHOLDS
from quanter_swarm.contracts import (
    CycleReport,
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
from quanter_swarm.errors import AgentExecutionError
from quanter_swarm.evolution import EvolutionManager
from quanter_swarm.evaluation.metrics import summarize_metrics
from quanter_swarm.execution.paper_executor import execute
from quanter_swarm.data.provider_factory import build_provider_from_config, describe_provider_config
from quanter_swarm.market.data_quality import validate_snapshot
from quanter_swarm.observability.metrics import build_cycle_metrics
from quanter_swarm.observability.trace import build_cycle_trace, new_trace_id
from quanter_swarm.orchestrator.agent_executor import AgentExecutor
from quanter_swarm.orchestrator.ranking_engine import rank_candidates
from quanter_swarm.orchestrator.states import CycleStage, CycleState, StageRecord
from quanter_swarm.reporting.report_generator import generate_report
from quanter_swarm.research.event_impact_analyzer import analyze_event_impact
from quanter_swarm.research.factor_score_engine import compute_factor_score
from quanter_swarm.research.fundamentals_parser import parse_fundamentals
from quanter_swarm.risk.engine import evaluate_risk_rules
from quanter_swarm.router import select_specialist_plan
from quanter_swarm.storage.file_store import write_json
from quanter_swarm.utils.config import (
    config_provenance,
    load_runtime_configs,
    load_settings,
    load_yaml,
    validate_config_consistency,
)
from quanter_swarm.utils.logging import get_logger

logger = get_logger(__name__)

if TYPE_CHECKING:
    from quanter_swarm.leaders.base_leader import BaseLeader
    from quanter_swarm.orchestrator.evolution_agent import EvolutionAgent
    from quanter_swarm.orchestrator.regime_agent import RegimeAgent
    from quanter_swarm.orchestrator.router_agent import RouterAgent
    from quanter_swarm.specialists.data_fetch_specialist import DataFetchSpecialist
    from quanter_swarm.specialists.feature_engineering_specialist import (
        FeatureEngineeringSpecialist,
    )
    from quanter_swarm.specialists.macro_event_specialist import MacroEventSpecialist
    from quanter_swarm.specialists.memory_compression_specialist import MemoryCompressionSpecialist
    from quanter_swarm.specialists.risk_specialist import RiskSpecialist
    from quanter_swarm.specialists.sentiment_specialist import SentimentSpecialist


class CycleManager:
    def __init__(self, provider_override: dict[str, Any] | None = None) -> None:
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
        self.evolution_manager = EvolutionManager(root=self.settings.data_dir / "evolution", config=self.evolution_config)
        self.provider_config = provider_override or self.settings.data_provider
        self.data_provider = build_provider_from_config(self.provider_config)
        self.provider_summary = describe_provider_config(self.provider_config, self.data_provider)

    @staticmethod
    def _serialize_stage_records(stage_records: list[StageRecord]) -> list[dict[str, Any]]:
        return [
            {
                "state": record.state.value,
                "stage": record.stage.value,
                "status": record.status,
                "detail": record.detail,
            }
            for record in stage_records
        ]

    @staticmethod
    def _terminal_state(termination_reason: str) -> str:
        if termination_reason == "no_data":
            return CycleState.FAILED.value
        return CycleState.DONE.value

    @staticmethod
    def _record_state_latency(context: dict[str, Any], state: CycleState, started_at: float) -> int:
        state_latencies = cast(dict[str, int], context.setdefault("state_latencies", {}))
        elapsed_ms = int((time() - started_at) * 1000)
        state_latencies[state.value] = elapsed_ms
        return elapsed_ms

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
        state_sequence: list[str],
        state_latencies: dict[str, int],
        route: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        leaders = list(route.get("leader_selected", [])) if route else []
        specialists = list(route.get("specialists_selected", [])) if route else []
        metrics = build_cycle_metrics(
            state_latencies=state_latencies,
            runtime_ms=runtime_ms,
            leaders=leaders,
            specialists=specialists,
            success=termination_reason != "no_data",
            token_budget=str(route.get("token_budget")) if route else None,
        )
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
            "router_decision": {
                "regime": regime,
                "confidence": regime_confidence,
                "leader_selected": [],
                "specialists_selected": [],
                "reasons": {},
                "rejected_candidates": {},
            },
            "risk_check": {
                "status": "blocked",
                "approved": False,
                "reason": termination_reason,
                "exposure_multiplier": 0.0,
                "warnings": [termination_reason],
            },
            "decision_trace_summary": {
                "trace_id": trace_id,
                "runtime_ms": runtime_ms,
                "fallback_modes": fallback_modes,
                "routing": {"selected_reasons": {}, "skipped_reasons": {}, "low_confidence_mode": True},
                "trace": build_cycle_trace(
                    trace_id=trace_id,
                    router_decision={
                        "regime": regime,
                        "confidence": regime_confidence,
                        "leader_selected": leaders,
                        "specialists_selected": specialists,
                    },
                    agents_activated={"leaders": leaders, "specialists": specialists},
                    runtime_ms=runtime_ms,
                    risk_result={
                        "status": "blocked",
                        "approved": False,
                        "reason": termination_reason,
                        "warnings": [termination_reason],
                    },
                    metrics=metrics,
                ),
                "metrics": metrics,
                "leader_scores": [],
                "risk_guardrail": {"status": "blocked", "reason": termination_reason, "exposure_multiplier": 0.0},
                "rejected_candidates": [],
                "portfolio_scaling": {"mode": "no_trade", "gross_exposure": 0.0, "cash_buffer": 1.0},
                "execution_assumptions": {},
                "state_machine": {
                    "current_state": self._terminal_state(termination_reason),
                    "terminated": True,
                    "termination_reason": termination_reason,
                    "state_sequence": state_sequence,
                    "stages": self._serialize_stage_records(stage_records),
                },
            },
            "config_provenance": self.config_snapshot,
            "evidence_summary": {},
            "provider_summary": self.provider_summary,
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
        validated = CycleReport.model_validate(report)
        FinalReportContract.model_validate(validated.model_dump())
        return validated.model_dump()

    def _log_cycle_event(
        self,
        *,
        trace_id: str,
        cycle_state: str,
        agent_name: str,
        latency: int,
        status: str,
        message: str,
    ) -> None:
        logger.info(
            message,
            extra={
                "trace_id": trace_id,
                "cycle_state": cycle_state,
                "agent_name": agent_name,
                "latency": latency,
                "status": status,
            },
        )

    @staticmethod
    def _enter_state(context: dict[str, Any], state: CycleState) -> None:
        state_sequence = cast(list[str], context.setdefault("state_sequence", [CycleState.INIT.value]))
        state_sequence.append(state.value)

    def _state_data_fetch(self, context: dict[str, Any]) -> dict[str, Any] | None:
        self._enter_state(context, CycleState.DATA_FETCH)
        state_started = time()
        scenario = cast(dict[str, Any], context["scenario"])
        target_symbol = str(context["target_symbol"])
        run_started = float(context["run_started"])
        trace_id = str(context["trace_id"])
        stage_records = cast(list[StageRecord], context["stage_records"])

        data_fetch = cast("DataFetchSpecialist", get_specialist("data_fetch"))
        data_fetch.provider = self.data_provider
        prefetched = cast(dict[str, Any] | None, context.get("prefetched_snapshots"))
        fetched = prefetched.get(target_symbol, {}) if prefetched else data_fetch.fetch(target_symbol)
        self._log_cycle_event(
            trace_id=trace_id,
            cycle_state=CycleState.DATA_FETCH.value,
            agent_name=data_fetch.name,
            latency=int((time() - run_started) * 1000),
            status="ok",
            message="data_fetch_completed",
        )
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
        context["fetched"] = fetched
        context["data_quality"] = data_quality
        if scenario.get("force_no_data") or not fetched.get("market_packet"):
            self._record_state_latency(context, CycleState.DATA_FETCH, state_started)
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
                state_sequence=cast(list[str], context["state_sequence"]) + [CycleState.FAILED.value],
                state_latencies=cast(dict[str, int], context.setdefault("state_latencies", {})),
            )
        self._record_state_latency(context, CycleState.DATA_FETCH, state_started)
        return None

    def _state_regime_detect(self, context: dict[str, Any]) -> None:
        self._enter_state(context, CycleState.REGIME_DETECT)
        state_started = time()
        fetched = cast(dict[str, Any], context["fetched"])
        stage_records = cast(list[StageRecord], context["stage_records"])
        trace_id = str(context["trace_id"])
        run_started = float(context["run_started"])
        market_packet = fetched["market_packet"]
        macro_inputs = fetched["macro_inputs"]
        vintage_macro_packet = fetched.get("vintage_macro_packet", [])
        latest_vintage = vintage_macro_packet[-1] if vintage_macro_packet else {}
        macro_release_lag_days = 0.0
        if latest_vintage.get("available_at"):
            available_at = datetime.fromisoformat(str(latest_vintage["available_at"]).replace("Z", "+00:00"))
            macro_release_lag_days = max(0.0, (fetched["as_of_ts"] - int(available_at.timestamp())) / 86_400)
        market_state = {
            "avg_change_pct": market_packet["change_pct"],
            "volatility": market_packet["volatility"],
            "macro_risk": macro_inputs["macro_risk"],
            "volume_anomaly": min(1.0, abs(market_packet["change_pct"]) * 10),
            "breadth": 0.55 if market_packet["change_pct"] >= 0 else 0.45,
            "correlation": min(1.0, 0.3 + market_packet["volatility"] * 8),
            "dispersion": min(1.0, market_packet["volatility"] * 10),
            "event_density": 0.7 if macro_inputs["macro_theme"] == "policy_uncertainty" else 0.3,
            "macro_release_lag_days": macro_release_lag_days,
            "macro_vintage_available": 1.0 if vintage_macro_packet else 0.0,
        }
        regime_agent = cast("RegimeAgent", get_agent("regime"))
        regime_decision = regime_agent.classify_detail(market_state, previous_regime=self._last_regime)
        self._log_cycle_event(
            trace_id=trace_id,
            cycle_state=CycleState.REGIME_DETECT.value,
            agent_name=regime_agent.name,
            latency=int((time() - run_started) * 1000),
            status="ok",
            message="regime_detect_completed",
        )
        stage_records.append(
            StageRecord(
                stage=CycleStage.REGIME,
                status="ok",
                detail={
                    "label": regime_decision["label"],
                    "family": regime_decision.get("family", regime_decision["label"]),
                    "confidence": regime_decision["confidence"],
                },
            )
        )
        context["market_packet"] = market_packet
        context["macro_inputs"] = macro_inputs
        context["market_state"] = market_state
        context["regime_decision"] = regime_decision
        context["regime"] = regime_decision["label"]
        self._last_regime = regime_decision["label"]
        self._record_state_latency(context, CycleState.REGIME_DETECT, state_started)

    def _state_routing(self, context: dict[str, Any]) -> None:
        self._enter_state(context, CycleState.ROUTING)
        state_started = time()
        stage_records = cast(list[StageRecord], context["stage_records"])
        scenario = cast(dict[str, Any], context["scenario"])
        regime = str(context["regime"])
        regime_decision = cast(dict[str, Any], context["regime_decision"])
        trace_id = str(context["trace_id"])
        run_started = float(context["run_started"])

        router_agent = cast("RouterAgent", get_agent("router"))
        route = router_agent.route(regime_decision, self.router_config, self.regimes_config)
        specialist_plan = select_specialist_plan(
            regime,
            router_config={
                **self.router_config,
                "token_budget": route["token_budget"],
                "latency_budget": route.get("latency_budget"),
                "max_specialists_per_cycle": route["max_specialists_per_cycle"],
            },
        )
        route["specialists_selected"] = specialist_plan["selected"]
        route["specialist_rejections"] = specialist_plan["rejected"]
        route["budget_constraints"] = specialist_plan["budget_constraints"]
        if scenario.get("always_on_leaders"):
            all_leaders = sorted(
                {
                    leader
                    for config in self.regimes_config.get("regimes", {}).values()
                    for leader in config.get("leaders", [])
                }
            )
            route["leaders"] = all_leaders
            route["leader_selected"] = all_leaders
            route["leader_weights"] = {leader: round(1 / max(1, len(all_leaders)), 4) for leader in all_leaders}
            route["selected_reasons"] = {leader: "forced_by_router_ablation" for leader in all_leaders}
            route["reasons"] = route["selected_reasons"]
            route["skipped_reasons"] = {}
            route["rejected_candidates"] = {}
        scenario_max_active = scenario.get("max_active_leaders")
        if isinstance(scenario_max_active, int) and scenario_max_active > 0:
            dropped = route["leaders"][scenario_max_active:]
            for leader in dropped:
                route["skipped_reasons"][leader] = "dropped_by_scenario_max_active"
            route["leaders"] = route["leaders"][:scenario_max_active]
            route["leader_selected"] = route["leaders"]
            route["rejected_candidates"] = route["skipped_reasons"]
        stage_records.append(
            StageRecord(
                stage=CycleStage.ROUTE,
                status="ok",
                detail={
                    "leaders": route["leader_selected"],
                    "specialists": route["specialists_selected"],
                    "budget_constraints": route["budget_constraints"],
                    "specialist_rejections": route["specialist_rejections"],
                    "low_confidence_mode": route["low_confidence_mode"],
                },
            )
        )
        self._log_cycle_event(
            trace_id=trace_id,
            cycle_state=CycleState.ROUTING.value,
            agent_name=router_agent.name,
            latency=int((time() - run_started) * 1000),
            status="ok",
            message="routing_completed",
        )
        context["route"] = route
        self._record_state_latency(context, CycleState.ROUTING, state_started)

    def _state_agent_execution(self, context: dict[str, Any]) -> None:
        self._enter_state(context, CycleState.AGENT_EXECUTION)
        state_started = time()
        scenario = cast(dict[str, Any], context["scenario"])
        stage_records = cast(list[StageRecord], context["stage_records"])
        fetched = cast(dict[str, Any], context["fetched"])
        data_quality = cast(dict[str, Any], context["data_quality"])
        macro_inputs = cast(dict[str, Any], context["macro_inputs"])
        market_state = cast(dict[str, Any], context["market_state"])
        route = cast(dict[str, Any], context["route"])
        target_symbol = str(context["target_symbol"])
        trace_id = str(context["trace_id"])
        run_started = float(context["run_started"])

        memory_compression = cast("MemoryCompressionSpecialist", get_specialist("memory_compression"))
        disable_specialists = scenario.get("disable_specialists", {})
        fallback_modes: list[str] = []
        if scenario.get("drop_fundamentals"):
            fallback_modes.append("fundamentals_fallback")
        macro_event_specialist = cast("MacroEventSpecialist", get_specialist("macro_event"))
        specialist_executor = AgentExecutor(timeout_seconds=1.0, allow_partial_failures=True)
        specialist_jobs: dict[str, tuple[Any, dict[str, Any]]] = {
            "memory_compression": (memory_compression, fetched),
        }
        if not disable_specialists.get("macro_event"):
            specialist_jobs["macro_event"] = (macro_event_specialist, macro_inputs)
        specialist_batch = specialist_executor.execute_many_sync(specialist_jobs)
        if "memory_compression" in specialist_batch.results:
            compressed = specialist_batch.results["memory_compression"].payload
        else:
            compressed = {
                "compressed": True,
                "summary": "; ".join(fetched.get("news_inputs", [])[:2]),
                "payload": fetched,
            }
            fallback_modes.append("memory_compression_fallback")
        if disable_specialists.get("sentiment") or "missing_news" in data_quality["issues"]:
            sentiment_score = 0.5
            fallback_modes.append("sentiment_fallback")
        else:
            sentiment_specialist = cast("SentimentSpecialist", get_specialist("sentiment"))
            sentiment_score = mean(sentiment_specialist.score(item) for item in fetched["news_inputs"])
        if disable_specialists.get("macro_event"):
            fallback_modes.append("macro_event_fallback")
            event_signal = {"impact": "neutral", "confidence": 0.5, "event": macro_inputs}
        elif "macro_event" in specialist_batch.results:
            event_signal = specialist_batch.results["macro_event"].payload
        else:
            fallback_modes.append("macro_event_fallback")
            event_signal = {"impact": "neutral", "confidence": 0.5, "event": macro_inputs}
        if scenario.get("force_earnings_event"):
            event_signal = {
                **event_signal,
                "event": {**cast(dict[str, Any], event_signal.get("event", {})), "event_type": "earnings"},
            }
        stage_records.append(
            StageRecord(
                stage=CycleStage.SPECIALIST_RESEARCH,
                status="ok" if not specialist_batch.failures else "partial_failure",
                detail={
                    "fallback_modes": fallback_modes,
                    "specialist_failures": {
                        name: {"error_type": failure.error_type, "message": failure.message}
                        for name, failure in specialist_batch.failures.items()
                    },
                },
            )
        )
        event_impact = analyze_event_impact(event_signal)
        parsed_fundamentals = parse_fundamentals(fetched["fundamentals_packet"])
        feature_engineering = cast("FeatureEngineeringSpecialist", get_specialist("feature_engineering"))
        features = feature_engineering.build(fetched)["features"]
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
        event_payload = {
            "event_id": f"{target_symbol}-{int(run_started)}",
            "symbol": target_symbol,
            "event_type": cast(dict[str, Any], event_signal.get("event", {})).get("event_type", "macro"),
            "impact": event_signal.get("impact", "neutral"),
            "regime": str(context["regime"]),
            "macro_risk": macro_inputs.get("macro_risk"),
            "trend": features.get("trend"),
            "volatility": features.get("volatility"),
        }
        weak_priors = self.evolution_manager.build_priors(event_payload)
        risk_specialist = cast("RiskSpecialist", get_specialist("risk"))
        risk_report = risk_specialist.assess(
            {
                "volatility": features["volatility"],
                "macro_risk": macro_inputs["macro_risk"],
            }
        )
        risk_thresholds = self.settings.risk_thresholds
        risk_penalty = min(
            risk_thresholds.get("max_risk_penalty", DEFAULT_RISK_THRESHOLDS["max_risk_penalty"]),
            len(risk_report["warnings"])
            * risk_thresholds.get(
                "risk_penalty_per_warning",
                DEFAULT_RISK_THRESHOLDS["risk_penalty_per_warning"],
            ),
        )
        signals = []
        for name in route["leaders"]:
            leader = cast("BaseLeader", get_leader(name))
            active_parameters = self.evolution_manager.get_active_parameters(
                name,
                regime=str(context["regime"]),
                event_cluster=event_payload["event_type"],
            )
            prior_payload = weak_priors.get(name, {})
            proposal = leader.propose({**leader_context, "params": active_parameters.get("parameter_set", {})})
            try:
                LeaderOutputContract.model_validate(proposal)
            except ValidationError as exc:
                raise AgentExecutionError(f"Leader '{name}' produced invalid output.") from exc
            proposal["regime_fit"] = risk_thresholds.get(
                "default_regime_fit",
                DEFAULT_RISK_THRESHOLDS["default_regime_fit"],
            )
            proposal["risk_penalty"] = risk_penalty
            proposal["leader_weight"] = route["leader_weights"].get(name, 0.0)
            proposal["volatility"] = features["volatility"]
            proposal["correlation"] = market_state["correlation"]
            proposal["event_risk"] = market_state["event_density"]
            proposal["parameter_version"] = active_parameters.get("version", "v1")
            proposal["parameter_set"] = active_parameters.get("parameter_set", {})
            proposal["prior_score"] = float(prior_payload.get("prior_score", 0.0))
            proposal["prior_sample_count"] = int(prior_payload.get("sample_count", 0))
            proposal["prior_confidence"] = float(prior_payload.get("confidence", 0.0))
            proposal["prior_event_ids"] = list(prior_payload.get("source_event_ids", []))
            proposal["cost_penalty"] = {
                "low": 0.02,
                "medium": 0.05,
                "high": 0.08,
            }.get(str(getattr(leader, "cost_hint", "medium")), 0.05)
            proposal["posterior_score"] = round(
                proposal["score"] + proposal["prior_score"] - proposal["risk_penalty"] - proposal["cost_penalty"],
                4,
            )
            proposal["confidence"] = min(
                1.0,
                max(
                    risk_thresholds.get(
                        "minimum_signal_confidence",
                        DEFAULT_RISK_THRESHOLDS["minimum_signal_confidence"],
                    ),
                    proposal["score"]
                    * risk_thresholds.get(
                        "leader_score_confidence_weight",
                        DEFAULT_RISK_THRESHOLDS["leader_score_confidence_weight"],
                    )
                    + route["regime_confidence"]
                    * risk_thresholds.get(
                        "regime_confidence_weight",
                        DEFAULT_RISK_THRESHOLDS["regime_confidence_weight"],
                    ),
                ),
            )
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
            try:
                RankedIdeaContract.model_validate(signal)
            except ValidationError as exc:
                raise AgentExecutionError(
                    f"Ranked idea for leader '{signal.get('leader', 'unknown')}' broke schema."
                ) from exc
        stage_records.append(
            StageRecord(
                stage=CycleStage.RANK,
                status="ok",
                detail={"ranked_count": len(ranked_signals)},
            )
        )
        self._log_cycle_event(
            trace_id=trace_id,
            cycle_state=CycleState.AGENT_EXECUTION.value,
            agent_name="cycle_manager",
            latency=int((time() - run_started) * 1000),
            status="ok" if not specialist_batch.failures else "partial_failure",
            message="agent_execution_completed",
        )
        context["fallback_modes"] = fallback_modes
        context["compressed"] = compressed
        context["sentiment_score"] = sentiment_score
        context["risk_report"] = risk_report
        context["event_signal"] = event_signal
        context["event_payload"] = event_payload
        context["weak_priors"] = weak_priors
        context["event_impact"] = event_impact
        context["parsed_fundamentals"] = parsed_fundamentals
        context["features"] = features
        context["factor_score"] = factor_score
        context["ranked_signals"] = ranked_signals
        self._record_state_latency(context, CycleState.AGENT_EXECUTION, state_started)

    def _state_risk_check(self, context: dict[str, Any]) -> None:
        self._enter_state(context, CycleState.RISK_CHECK)
        state_started = time()
        stage_records = cast(list[StageRecord], context["stage_records"])
        risk_report = cast(dict[str, Any], context["risk_report"])
        trace_id = str(context["trace_id"])
        run_started = float(context["run_started"])
        guardrail = assess_guardrails(risk_report)
        stage_records.append(
            StageRecord(
                stage=CycleStage.RISK,
                status="ok",
                detail={"guardrail_status": guardrail["status"], "warnings": risk_report["warnings"]},
            )
        )
        self._log_cycle_event(
            trace_id=trace_id,
            cycle_state=CycleState.RISK_CHECK.value,
            agent_name="risk_guardrail",
            latency=int((time() - run_started) * 1000),
            status=guardrail["status"],
            message="risk_check_completed",
        )
        context["guardrail"] = guardrail
        self._record_state_latency(context, CycleState.RISK_CHECK, state_started)

    def _state_portfolio_build(self, context: dict[str, Any]) -> dict[str, Any] | None:
        self._enter_state(context, CycleState.PORTFOLIO_BUILD)
        state_started = time()
        scenario = cast(dict[str, Any], context["scenario"])
        stage_records = cast(list[StageRecord], context["stage_records"])
        route = cast(dict[str, Any], context["route"])
        guardrail = cast(dict[str, Any], context["guardrail"])
        ranked_signals = cast(list[dict[str, Any]], context["ranked_signals"])
        regime = str(context["regime"])
        fallback_modes = cast(list[str], context["fallback_modes"])
        market_packet = cast(dict[str, Any], context["market_packet"])
        data_quality = cast(dict[str, Any], context["data_quality"])
        regime_decision = cast(dict[str, Any], context["regime_decision"])
        target_symbol = str(context["target_symbol"])
        run_started = float(context["run_started"])
        trace_id = str(context["trace_id"])

        cash_buffer = self.portfolio_config.get("portfolio", {}).get("cash_buffer", 0.1)
        target_positions = self.portfolio_config.get("portfolio", {}).get("target_positions")
        allocation_mode = scenario.get(
            "allocation_mode",
            self.portfolio_config.get("portfolio", {}).get("allocation_mode", "simple"),
        )
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
        self._log_cycle_event(
            trace_id=trace_id,
            cycle_state=CycleState.PORTFOLIO_BUILD.value,
            agent_name="portfolio_builder",
            latency=int((time() - run_started) * 1000),
            status=portfolio["mode"],
            message="portfolio_build_completed",
        )
        if route["low_confidence_mode"] and not route["leaders"]:
            self._record_state_latency(context, CycleState.PORTFOLIO_BUILD, state_started)
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
                state_sequence=cast(list[str], context["state_sequence"]) + [CycleState.DONE.value],
                state_latencies=cast(dict[str, int], context.setdefault("state_latencies", {})),
                route=route,
            )
        context["threshold"] = threshold
        context["passed_ideas"] = passed_ideas
        context["rejected_ideas"] = rejected_ideas
        risk_engine_result = evaluate_risk_rules(
            portfolio=portfolio,
            market_packet=market_packet,
            event_payload=cast(dict[str, Any], context["event_signal"]).get("event", {}),
            daily_loss_pct=float(scenario.get("daily_loss_pct", 0.0)),
            rules_config=self.risk_config.get("risk", {}),
        )
        combined_warnings = list(dict.fromkeys(guardrail.get("warnings", []) + risk_engine_result["warnings"]))
        if risk_engine_result["status"] == "blocked":
            guardrail = {
                "status": "blocked",
                "approved": False,
                "exposure_multiplier": 0.0,
                "reason": risk_engine_result["reason"],
                "warnings": combined_warnings,
                "triggered_rules": risk_engine_result["triggered_rules"],
            }
            portfolio = {
                "positions": [],
                "cash_buffer": 1.0,
                "gross_exposure": 0.0,
                "mode": "no_trade",
                "allocation_mode": portfolio.get("allocation_mode", allocation_mode),
                "rationale": f"blocked by risk engine: {risk_engine_result['reason']}",
                "no_trade_reason": risk_engine_result["reason"],
                "position_rationales": [],
            }
            fallback_modes.append("risk_engine_no_trade")
        else:
            guardrail = {
                **guardrail,
                "warnings": combined_warnings,
                "triggered_rules": risk_engine_result["triggered_rules"],
            }
        cast(dict[str, Any], context["risk_report"])["warnings"] = combined_warnings
        context["guardrail"] = guardrail
        context["portfolio"] = portfolio
        self._record_state_latency(context, CycleState.PORTFOLIO_BUILD, state_started)
        return None

    def _state_report_generation(self, context: dict[str, Any], persist_outputs: bool) -> dict[str, Any]:
        self._enter_state(context, CycleState.REPORT_GENERATION)
        state_started = time()
        stage_records = cast(list[StageRecord], context["stage_records"])
        market_packet = cast(dict[str, Any], context["market_packet"])
        market_state = cast(dict[str, Any], context["market_state"])
        route = cast(dict[str, Any], context["route"])
        risk_thresholds = self.settings.risk_thresholds
        portfolio = cast(dict[str, Any], context["portfolio"])
        ranked_signals = cast(list[dict[str, Any]], context["ranked_signals"])
        guardrail = cast(dict[str, Any], context["guardrail"])
        threshold = float(context["threshold"])
        regime = str(context["regime"])
        regime_decision = cast(dict[str, Any], context["regime_decision"])
        target_symbol = str(context["target_symbol"])
        run_started = float(context["run_started"])
        started_at = int(context["started_at"])
        trace_id = str(context["trace_id"])
        fallback_modes = cast(list[str], context["fallback_modes"])
        data_quality = cast(dict[str, Any], context["data_quality"])
        parsed_fundamentals = cast(dict[str, Any], context["parsed_fundamentals"])
        event_impact = cast(dict[str, Any], context["event_impact"])
        factor_score = float(context["factor_score"])
        risk_report = cast(dict[str, Any], context["risk_report"])
        rejected_ideas = cast(list[dict[str, Any]], context["rejected_ideas"])

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
                        "event_window": market_state["event_density"]
                        >= risk_thresholds.get(
                            "event_window_density",
                            DEFAULT_RISK_THRESHOLDS["event_window_density"],
                        ),
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
            try:
                PaperTradeActionContract.model_validate(action)
            except ValidationError as exc:
                raise AgentExecutionError("Paper trade action broke schema.") from exc

        simulated_returns = [
            round(signal.get("composite_rank_score", 0.0) - 0.5 - signal.get("risk_penalty", 0.0) / 2, 4)
            for signal in ranked_signals
        ]
        metrics = summarize_metrics(simulated_returns)
        evolution_enabled = self.evolution_config.get("evolution", {}).get("enabled", True)
        evolution_summary = (
            self.evolution_manager.evolve(
                ranked_signals,
                current_threshold=threshold,
                event_payload=cast(dict[str, Any], context["event_payload"]),
            )
            if evolution_enabled
            else {"threshold": threshold, "action": "disabled"}
        )
        self._record_state_latency(context, CycleState.REPORT_GENERATION, state_started)
        runtime_ms = int((time() - run_started) * 1000)
        metrics = build_cycle_metrics(
            state_latencies=cast(dict[str, int], context.setdefault("state_latencies", {})),
            runtime_ms=runtime_ms,
            leaders=route["leader_selected"],
            specialists=route["specialists_selected"],
            success=True,
            token_budget=str(route.get("token_budget")),
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
                "macro_vintage_count": len(cast(dict[str, Any], context["fetched"]).get("vintage_macro_packet", [])),
            },
            "fundamentals_summary": parsed_fundamentals,
            "sentiment_summary": {
                "score": round(float(context["sentiment_score"]), 2),
                "compressed_context": cast(dict[str, Any], context["compressed"])["summary"],
            },
            "event_impact_summary": event_impact,
            "factor_score": factor_score,
            "risk_alerts": risk_report["warnings"],
            "portfolio_suggestion": portfolio,
            "paper_trade_actions": paper_trade_actions,
            "evidence_summary": {
                "data_sources": cast(dict[str, Any], context["fetched"]).get("evidence", {}),
                "quality_flags": cast(dict[str, Any], context["fetched"]).get("quality_flags", []),
                "reliability_score": cast(dict[str, Any], context["fetched"]).get("reliability_score", 0.0),
                "evolution": {
                    "action": evolution_summary.get("action"),
                    "top_posterior_leader": evolution_summary.get("top_posterior_leader"),
                    "parameter_version": ranked_signals[0].get("parameter_version") if ranked_signals else "n/a",
                    "prior_event_ids": ranked_signals[0].get("prior_event_ids", []) if ranked_signals else [],
                },
            },
            "provider_summary": self.provider_summary,
            "router_decision": {
                "regime": route["regime"],
                "confidence": route["confidence"],
                "leader_selected": route["leader_selected"],
                "specialists_selected": route["specialists_selected"],
                "reasons": route["reasons"],
                "rejected_candidates": route["rejected_candidates"],
                "budget_constraints": route["budget_constraints"],
                "specialist_rejections": route["specialist_rejections"],
            },
            "risk_check": guardrail,
            "decision_trace_summary": {
                "trace_id": trace_id,
                "runtime_ms": runtime_ms,
                "regime": regime_decision,
                "fallback_modes": fallback_modes,
                "trace": build_cycle_trace(
                    trace_id=trace_id,
                    router_decision={
                        "regime": route["regime"],
                        "confidence": route["confidence"],
                        "leader_selected": route["leader_selected"],
                        "specialists_selected": route["specialists_selected"],
                    },
                    agents_activated={
                        "leaders": route["leader_selected"],
                        "specialists": route["specialists_selected"],
                    },
                    runtime_ms=runtime_ms,
                    risk_result=guardrail,
                    metrics=metrics,
                ),
                "metrics": metrics,
                "specialist_contribution": {
                    "sentiment_score": round(float(context["sentiment_score"]), 4),
                    "event_impact_score": event_impact.get("impact_score", 0.0),
                    "factor_score": factor_score,
                },
                "routing": {
                    "regime": route["regime"],
                    "confidence": route["confidence"],
                    "leader_selected": route["leader_selected"],
                    "specialists_selected": route["specialists_selected"],
                    "reasons": route["reasons"],
                    "rejected_candidates": route["rejected_candidates"],
                    "budget_constraints": route["budget_constraints"],
                    "specialist_rejections": route["specialist_rejections"],
                    "selected_reasons": route["selected_reasons"],
                    "skipped_reasons": route["skipped_reasons"],
                    "low_confidence_mode": route["low_confidence_mode"],
                },
                "leader_scores": [
                    {
                        "leader": signal["leader"],
                        "score": signal["score"],
                        "posterior_score": signal.get("posterior_score", signal["score"]),
                        "prior_score": signal.get("prior_score", 0.0),
                        "parameter_version": signal.get("parameter_version", "v1"),
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
                    "current_state": CycleState.DONE.value
                    if portfolio.get("mode") != "no_trade"
                    else CycleState.REPORT_GENERATION.value,
                    "terminated": portfolio.get("mode") == "no_trade",
                    "termination_reason": "no_trade" if portfolio.get("mode") == "no_trade" else "",
                    "state_sequence": cast(list[str], context["state_sequence"]),
                    "stages": self._serialize_stage_records(stage_records),
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
        report["decision_trace_summary"]["state_machine"]["stages"] = self._serialize_stage_records(stage_records)
        state_sequence = cast(list[str], context["state_sequence"])
        if state_sequence[-1] != CycleState.DONE.value:
            state_sequence.append(CycleState.DONE.value)
        report["decision_trace_summary"]["state_machine"]["state_sequence"] = state_sequence
        report["decision_trace_summary"]["state_machine"]["current_state"] = CycleState.DONE.value
        self._log_cycle_event(
            trace_id=trace_id,
            cycle_state=CycleState.REPORT_GENERATION.value,
            agent_name="report_generator",
            latency=int((time() - run_started) * 1000),
            status="ok",
            message="report_generation_completed",
        )
        try:
            validated = CycleReport.model_validate(report)
            FinalReportContract.model_validate(validated.model_dump())
        except ValidationError as exc:
            raise AgentExecutionError("Cycle report broke schema validation.") from exc
        cycle_id = f"{target_symbol.lower()}_{started_at}"
        if persist_outputs:
            write_json(self.settings.data_dir / "reports" / f"{cycle_id}.json", validated.model_dump())
            if paper_trade_actions:
                write_json(
                    self.settings.data_dir / "paper_trades" / f"{cycle_id}.json",
                    {"symbol": target_symbol, "actions": paper_trade_actions, "metrics": metrics},
                )
        return validated.model_dump()

    def run_cycle(
        self,
        symbol: str | None = None,
        scenario: dict[str, Any] | None = None,
        persist_outputs: bool = True,
    ) -> dict[str, Any]:
        context: dict[str, Any] = {
            "scenario": scenario or {},
            "started_at": int(time()),
            "run_started": time(),
            "trace_id": new_trace_id("cycle"),
            "stage_records": [],
            "state_latencies": {},
            "target_symbol": symbol or self.settings.default_symbols[0],
            "state_sequence": [CycleState.INIT.value],
        }
        short_circuit = self._state_data_fetch(context)
        if short_circuit is not None:
            return short_circuit
        self._state_regime_detect(context)
        self._state_routing(context)
        self._state_agent_execution(context)
        self._state_risk_check(context)
        short_circuit = self._state_portfolio_build(context)
        if short_circuit is not None:
            return short_circuit
        return self._state_report_generation(context, persist_outputs)

    def run_cycle_batch(
        self,
        symbols: list[str],
        scenario: dict[str, Any] | None = None,
        persist_outputs: bool = True,
    ) -> list[dict[str, Any]]:
        normalized = [symbol.upper() for symbol in symbols]
        data_fetch = cast("DataFetchSpecialist", get_specialist("data_fetch"))
        data_fetch.provider = self.data_provider
        prefetched = data_fetch.fetch_many(normalized)
        results: list[dict[str, Any]] = []
        for symbol in normalized:
            context: dict[str, Any] = {
                "scenario": scenario or {},
                "started_at": int(time()),
                "run_started": time(),
                "trace_id": new_trace_id("cycle"),
                "stage_records": [],
                "state_latencies": {},
                "target_symbol": symbol,
                "state_sequence": [CycleState.INIT.value],
                "prefetched_snapshots": prefetched,
            }
            short_circuit = self._state_data_fetch(context)
            if short_circuit is not None:
                results.append(short_circuit)
                continue
            self._state_regime_detect(context)
            self._state_routing(context)
            self._state_agent_execution(context)
            self._state_risk_check(context)
            short_circuit = self._state_portfolio_build(context)
            if short_circuit is not None:
                results.append(short_circuit)
                continue
            results.append(self._state_report_generation(context, persist_outputs))
        return results
