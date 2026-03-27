"""Report generator."""

from __future__ import annotations

from quanter_swarm.services.reporting.markdown_report import render_markdown_report
from quanter_swarm.services.reporting.one_page_summary_builder import build_one_page_summary
from quanter_swarm.services.reporting.risk_summary_builder import build_risk_summary
from quanter_swarm.services.reporting.scorecard_builder import build_scorecard


def _build_architecture_summary(payload: dict) -> dict:
    trace_summary = payload.get("decision_trace_summary", {})
    routing = {
        **payload.get("router_decision", {}),
        **trace_summary.get("routing", {}),
    }
    state_machine = trace_summary.get("state_machine", {})
    leader_scores = trace_summary.get("leader_scores", [])
    specialists = list(routing.get("specialists_selected", []))
    rejected_candidates = routing.get("rejected_candidates", {})
    rejected_names = (
        list(rejected_candidates.keys())
        if isinstance(rejected_candidates, dict)
        else [str(item) for item in rejected_candidates]
    )
    signal_count = int(payload.get("evaluation_summary", {}).get("signal_count", 0))
    paper_trade_actions = payload.get("paper_trade_actions", [])
    evidence = payload.get("evidence_summary", {})
    evolution = evidence.get("evolution", {})
    risk_check = payload.get("risk_check", {})
    portfolio = payload.get("portfolio_suggestion", {})
    provider_summary = payload.get("provider_summary", {})

    return {
        "control_plane": {
            "flow": ["orchestrator", "router", "leader", "specialist"],
            "orchestrator": {
                "name": "RootAgent",
                "state_sequence": state_machine.get("state_sequence", []),
                "bootstrap_stage": ["data_fetch", "regime_detect"],
            },
            "router": {
                "regime": routing.get("regime", payload.get("active_regime")),
                "selected_leaders": routing.get("leader_selected", []),
                "selected_specialists": specialists,
                "rejected_candidates": rejected_names,
                "routing_reasons": routing.get("selected_reasons", routing.get("reasons", {})),
            },
            "leaders": [
                {
                    "name": score.get("leader"),
                    "proposal_score": score.get("score"),
                    "posterior_score": score.get("posterior_score", score.get("score")),
                    "used_specialists": specialists,
                }
                for score in leader_scores
            ],
            "specialists": [
                {
                    "name": name,
                    "role": "shared_specialist",
                }
                for name in specialists
            ],
        },
        "system_services": {
            "snapshot": {
                "status": "ok" if payload.get("market_summary") else "missing",
                "provider": provider_summary.get("provider", "unknown"),
            },
            "ranking": {
                "status": "ok" if signal_count else "idle",
                "signal_count": signal_count,
            },
            "evolution": {
                "status": evolution.get("action", "idle"),
                "top_posterior_leader": evolution.get("top_posterior_leader"),
            },
            "risk": {
                "status": risk_check.get("status", "unknown"),
                "approved": risk_check.get("approved", False),
            },
            "portfolio": {
                "status": portfolio.get("mode", "unknown"),
                "gross_exposure": portfolio.get("gross_exposure", 0.0),
            },
            "execution": {
                "status": "executed" if paper_trade_actions else "skipped",
                "action_count": len(paper_trade_actions),
            },
            "reporting": {
                "status": "generated",
            },
        },
    }


def generate_report(payload: dict) -> dict:
    fallback_modes = payload.get("decision_trace_summary", {}).get("fallback_modes", [])
    limitation = "none" if not fallback_modes else ",".join(fallback_modes)
    scorecard = build_scorecard(payload["symbol"], payload["factor_score"])
    risk_summary = build_risk_summary(payload["risk_alerts"])
    architecture_summary = _build_architecture_summary(payload)
    one_page = build_one_page_summary(
        title=f"{payload['symbol']} {payload['active_regime']} research cycle",
        highlights=[
            "control_plane=orchestrator->router->leader->specialist",
            f"leaders={','.join(payload['active_strategy_teams']) or 'none'}",
            f"factor_score={payload['factor_score']}",
            f"portfolio_mode={payload['portfolio_suggestion']['mode']}",
            f"limitations={limitation}",
        ],
    )

    return {
        "symbol": payload["symbol"],
        "active_regime": payload["active_regime"],
        "regime_confidence": payload.get("regime_confidence", 0.0),
        "active_strategy_teams": payload["active_strategy_teams"],
        "market_summary": payload["market_summary"],
        "fundamentals_summary": payload["fundamentals_summary"],
        "sentiment_summary": payload["sentiment_summary"],
        "event_impact_summary": payload["event_impact_summary"],
        "factor_scorecard": scorecard,
        "risk_alerts": risk_summary,
        "router_decision": payload.get("router_decision", {}),
        "risk_check": payload.get("risk_check", {}),
        "portfolio_suggestion": payload["portfolio_suggestion"],
        "paper_trade_actions": payload["paper_trade_actions"],
        "evaluation_summary": payload["evaluation_summary"],
        "one_page_summary": one_page,
        "architecture_summary": architecture_summary,
        "evidence_summary": payload.get("evidence_summary", {}),
        "provider_summary": payload.get("provider_summary", {}),
        "config_provenance": payload.get("config_provenance", {}),
        "decision_trace": payload.get("decision_trace_summary", {}),
        "decision_trace_summary": payload.get("decision_trace_summary", {}),
        "markdown_summary": render_markdown_report(
            {
                "symbol": payload["symbol"],
                "active_regime": payload["active_regime"],
                "regime_confidence": payload.get("regime_confidence", 0.0),
                "active_strategy_teams": payload["active_strategy_teams"],
                "market_summary": payload["market_summary"],
                "factor_scorecard": scorecard,
                "risk_alerts": risk_summary,
                "portfolio_suggestion": payload["portfolio_suggestion"],
                "paper_trade_actions": payload["paper_trade_actions"],
                "evaluation_summary": payload["evaluation_summary"],
                "one_page_summary": one_page,
                "architecture_summary": architecture_summary,
                "evidence_summary": payload.get("evidence_summary", {}),
                "provider_summary": payload.get("provider_summary", {}),
                "decision_trace_summary": payload.get("decision_trace_summary", {}),
                "config_provenance": payload.get("config_provenance", {}),
            }
        ),
    }
