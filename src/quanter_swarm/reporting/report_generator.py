"""Report generator."""

from __future__ import annotations

from quanter_swarm.reporting.markdown_report import render_markdown_report
from quanter_swarm.reporting.one_page_summary_builder import build_one_page_summary
from quanter_swarm.reporting.risk_summary_builder import build_risk_summary
from quanter_swarm.reporting.scorecard_builder import build_scorecard


def generate_report(payload: dict) -> dict:
    fallback_modes = payload.get("decision_trace_summary", {}).get("fallback_modes", [])
    limitation = "none" if not fallback_modes else ",".join(fallback_modes)
    scorecard = build_scorecard(payload["symbol"], payload["factor_score"])
    risk_summary = build_risk_summary(payload["risk_alerts"])
    one_page = build_one_page_summary(
        title=f"{payload['symbol']} {payload['active_regime']} research cycle",
        highlights=[
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
                "decision_trace_summary": payload.get("decision_trace_summary", {}),
            }
        ),
    }
