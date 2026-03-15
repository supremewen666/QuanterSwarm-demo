"""Cycle execution coordinator."""

from __future__ import annotations

from statistics import mean
from time import time
from typing import Any

from quanter_swarm.decision.execution_gate import execution_allowed
from quanter_swarm.decision.order_sizer import size_order
from quanter_swarm.decision.portfolio_suggestion import build_portfolio
from quanter_swarm.decision.risk_guardrail import assess_guardrails
from quanter_swarm.evaluation.metrics import summarize_metrics
from quanter_swarm.execution.paper_executor import execute
from quanter_swarm.leaders.leader_factory import get_leader
from quanter_swarm.orchestrator.evolution_agent import EvolutionAgent
from quanter_swarm.orchestrator.ranking_engine import rank_candidates
from quanter_swarm.orchestrator.regime_agent import RegimeAgent
from quanter_swarm.orchestrator.router_agent import RouterAgent
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
from quanter_swarm.utils.config import load_settings, load_yaml


class CycleManager:
    def __init__(self) -> None:
        self.settings = load_settings()
        self.router_config = load_yaml(self.settings.config_dir / "router.yaml")
        self.regimes_config = load_yaml(self.settings.config_dir / "regimes.yaml")
        self.portfolio_config = load_yaml(self.settings.config_dir / "portfolio.yaml")
        self.risk_config = load_yaml(self.settings.config_dir / "risk.yaml")
        self.ranking_config = load_yaml(self.settings.config_dir / "ranking.yaml")
        self.evolution_config = load_yaml(self.settings.config_dir / "evolution.yaml")

    def run_cycle(self, symbol: str | None = None) -> dict[str, Any]:
        started_at = int(time())
        target_symbol = symbol or self.settings.default_symbols[0]
        fetched = DataFetchSpecialist().fetch(target_symbol)
        compressed = MemoryCompressionSpecialist().compress(fetched)

        market_packet = fetched["market_packet"]
        macro_inputs = fetched["macro_inputs"]
        market_state = {
            "avg_change_pct": market_packet["change_pct"],
            "volatility": market_packet["volatility"],
            "macro_risk": macro_inputs["macro_risk"],
        }
        regime = RegimeAgent().classify(market_state)
        route = RouterAgent().route(regime, self.router_config, self.regimes_config)

        sentiment_score = mean(SentimentSpecialist().score(item) for item in fetched["news_inputs"])
        event_signal = MacroEventSpecialist().analyze(macro_inputs)
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
            proposal["regime_fit"] = 0.8
            proposal["risk_penalty"] = risk_penalty
            signals.append(proposal)
        ranked_signals = rank_candidates(signals)

        guardrail = assess_guardrails(risk_report)

        cash_buffer = self.portfolio_config.get("portfolio", {}).get("cash_buffer", 0.1)
        target_positions = self.portfolio_config.get("portfolio", {}).get("target_positions")
        max_single_weight = self.risk_config.get("risk", {}).get("max_single_weight", 0.25)
        threshold = self.ranking_config.get("ranking", {}).get("signal_threshold", 0.5)
        portfolio = build_portfolio(
            ideas=[idea for idea in ranked_signals if idea.get("composite_rank_score", 0.0) >= threshold]
            if guardrail["status"] != "blocked"
            else [],
            cash_buffer=cash_buffer,
            max_single_weight=max_single_weight,
            exposure_multiplier=guardrail["exposure_multiplier"],
            target_positions=target_positions,
        )

        paper_trade_actions: list[dict[str, Any]] = []
        execution_ok, execution_reason = execution_allowed(self.settings.execution_mode)
        if execution_ok:
            for position in portfolio["positions"]:
                order_value = size_order(position["weight"], self.settings.starting_capital)
                paper_trade_actions.append(
                    execute(
                        {
                            "symbol": position["symbol"],
                            "leader": position["leader"],
                            "notional": order_value,
                            "reference_price": market_packet["price"],
                        }
                    )
                )

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
            "active_strategy_teams": route["leaders"],
            "market_summary": {
                "price": market_packet["price"],
                "change_pct": market_packet["change_pct"],
                "volatility": market_packet["volatility"],
            },
            "fundamentals_summary": parsed_fundamentals,
            "sentiment_summary": {"score": round(sentiment_score, 2), "compressed_context": compressed["summary"]},
            "event_impact_summary": event_impact,
            "factor_score": factor_score,
            "risk_alerts": risk_report["warnings"],
            "portfolio_suggestion": portfolio,
            "paper_trade_actions": paper_trade_actions,
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
        cycle_id = f"{target_symbol.lower()}_{started_at}"
        write_json(self.settings.data_dir / "reports" / f"{cycle_id}.json", report)
        if paper_trade_actions:
            write_json(
                self.settings.data_dir / "paper_trades" / f"{cycle_id}.json",
                {"symbol": target_symbol, "actions": paper_trade_actions, "metrics": metrics},
            )
        return report
