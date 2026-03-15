"""Markdown rendering helpers for advanced user-facing exports."""

from __future__ import annotations


def _render_positions(positions: list[dict]) -> str:
    if not positions:
        return "- No positions"
    return "\n".join(
        f"- {position['symbol']} via `{position['leader']}` at {position['weight']:.2%}"
        for position in positions
    )


def _render_actions(actions: list[dict]) -> str:
    if not actions:
        return "- No paper trades executed"
    return "\n".join(
        f"- {action['order']['symbol']} {action['status']} at {action['fill_price']}"
        for action in actions
    )


def render_markdown_report(report: dict) -> str:
    scorecard = report["factor_scorecard"]
    risk_alerts = report["risk_alerts"]
    portfolio = report["portfolio_suggestion"]
    evaluation = report["evaluation_summary"]
    one_page = report["one_page_summary"]
    highlights = "\n".join(f"- {item}" for item in one_page.get("highlights", [])) or "- None"
    warnings = "\n".join(f"- {warning}" for warning in risk_alerts.get("warnings", [])) or "- Clear"
    trace = report.get("decision_trace_summary", {})
    return "\n".join(
        [
            f"# {report['symbol']} Research Cycle",
            "",
            f"- Regime: `{report['active_regime']}`",
            f"- Regime confidence: `{report.get('regime_confidence', 0.0)}`",
            f"- Active leaders: {', '.join(report['active_strategy_teams']) or 'none'}",
            f"- Factor score: `{scorecard['composite_score']}`",
            "",
            "## Market Summary",
            f"- Price: {report['market_summary'].get('price')}",
            f"- Change: {report['market_summary'].get('change_pct')}",
            f"- Volatility: {report['market_summary'].get('volatility')}",
            "",
            "## Risk",
            f"- Status: `{risk_alerts.get('status')}`",
            warnings,
            "",
            "## Portfolio Suggestion",
            f"- Mode: `{portfolio.get('mode')}`",
            f"- Gross exposure: {portfolio.get('gross_exposure', 0.0):.2%}",
            f"- Cash buffer: {portfolio.get('cash_buffer', 0.0):.2%}",
            _render_positions(portfolio.get("positions", [])),
            "",
            "## Paper Trade Actions",
            _render_actions(report.get("paper_trade_actions", [])),
            "",
            "## One-Page Summary",
            highlights,
            "",
            "## Evaluation",
            f"- Signal count: {evaluation.get('signal_count')}",
            f"- Execution reason: {evaluation.get('execution_reason')}",
            f"- Routing mode: {'low-confidence' if trace.get('routing', {}).get('low_confidence_mode') else 'normal'}",
        ]
    ).strip()
