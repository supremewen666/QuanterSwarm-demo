"""Task-oriented application flows used by CLI and dashboard adapters."""

from __future__ import annotations

import json
from html import escape
from pathlib import Path
from statistics import mean
from typing import TYPE_CHECKING, Any, cast

from quanter_swarm.application import RunBatchResearch
from quanter_swarm.backtest.replay_engine import replay_report
from quanter_swarm.core.runtime.config import load_settings
from quanter_swarm.core.storage.file_store import write_json
from quanter_swarm.errors import BacktestError, DataProviderError

if TYPE_CHECKING:
    from fastapi import FastAPI

DEFAULT_CAPITAL = 100_000.0
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8000
INTERNAL_SIM_SOURCE = "internal_sim"
INTERNAL_PROVIDER_OVERRIDE = {"provider": "deterministic"}


def normalize_source(source: str) -> str:
    normalized = source.strip().lower()
    if normalized in {"", "internal", "internal_sim", "deterministic", "default"}:
        return INTERNAL_SIM_SOURCE
    raise DataProviderError(
        f"Unsupported source '{source}'. Only internal_sim is allowed for research, replay, and backtest flows."
    )


def provider_override_for_source(source: str) -> dict[str, str]:
    normalized = normalize_source(source)
    if normalized != INTERNAL_SIM_SOURCE:
        raise DataProviderError(f"Unsupported source '{source}'.")
    return dict(INTERNAL_PROVIDER_OVERRIDE)


def resolve_symbols(symbols: list[str] | None = None) -> list[str]:
    if symbols:
        return [symbol.upper() for symbol in symbols]
    return [symbol.upper() for symbol in load_settings().default_symbols]


def utc_now_iso() -> str:
    from datetime import UTC, datetime

    return datetime.now(tz=UTC).isoformat()


def ensure_directory(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def safe_fingerprint(report: dict[str, Any]) -> str:
    config = report.get("config_provenance", {})
    return str(config.get("fingerprint", "unknown"))


def write_output_payload(payload: dict[str, Any], output_path: str | None = None) -> str:
    rendered = json.dumps(payload, indent=2, ensure_ascii=False)
    if output_path:
        destination = Path(output_path)
        ensure_directory(destination.parent)
        destination.write_text(rendered, encoding="utf-8")
    return rendered


def portfolio_plan_from_report(report: dict[str, Any]) -> dict[str, Any]:
    suggestion = report.get("portfolio_suggestion", {})
    return {
        "symbol": report.get("symbol"),
        "regime": report.get("active_regime"),
        "positions": suggestion.get("positions", []),
        "gross_exposure": suggestion.get("gross_exposure", 0.0),
        "cash_buffer": suggestion.get("cash_buffer", 1.0),
        "allocation_mode": suggestion.get("allocation_mode", "simple"),
        "mode": suggestion.get("mode", "no_trade"),
        "rationale": suggestion.get("rationale", ""),
    }


def mock_execution_from_report(report: dict[str, Any]) -> dict[str, Any]:
    return {
        "symbol": report.get("symbol"),
        "orders": report.get("paper_trade_actions", []),
        "status": report.get("risk_check", {}).get("status", "unknown"),
        "reason": report.get("risk_check", {}).get("reason", ""),
    }


def run_research_cycle(
    *,
    source: str = INTERNAL_SIM_SOURCE,
    symbols: list[str] | None = None,
    scenario: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    normalized_symbols = resolve_symbols(symbols)
    provider_override = provider_override_for_source(source)
    return RunBatchResearch().execute(
        symbols=normalized_symbols,
        scenario=scenario,
        data_provider=provider_override["provider"],
    )


def _metric_average(reports: list[dict[str, Any]], metric_name: str) -> float:
    values = [
        float(report.get("evaluation_summary", {}).get("metrics", {}).get(metric_name, 0.0))
        for report in reports
    ]
    if not values:
        return 0.0
    return round(mean(values), 6)


def run_backtest(
    *,
    source: str = INTERNAL_SIM_SOURCE,
    symbols: list[str] | None = None,
    config_path: str | None = None,
    capital: float = DEFAULT_CAPITAL,
) -> dict[str, Any]:
    normalized_source = normalize_source(source)
    reports = run_research_cycle(source=normalized_source, symbols=resolve_symbols(symbols))
    replay_rows = [replay_report(report, capital) for report in reports]
    created_at = utc_now_iso()
    first_report = reports[0] if reports else {}
    config_hash = safe_fingerprint(first_report)
    run_id = created_at.replace(":", "").replace("-", "")
    payload = {
        "run_id": run_id,
        "created_at": created_at,
        "source": normalized_source,
        "symbols": [report.get("symbol") for report in reports],
        "dataset_version": f"{normalized_source}:{created_at[:10]}",
        "config_hash": config_hash,
        "router_version": f"router:{config_hash[:8]}",
        "ranking_version": f"ranking:{config_hash[:8]}",
        "risk_version": f"risk:{config_hash[:8]}",
        "config_path": config_path,
        "summary": {
            "return": _metric_average(reports, "annualized_return"),
            "sharpe": _metric_average(reports, "sharpe"),
            "drawdown": _metric_average(reports, "drawdown"),
            "turnover": _metric_average(reports, "turnover_proxy"),
            "realized_return": round(mean(row["realized_return"] for row in replay_rows), 6) if replay_rows else 0.0,
        },
        "results": [
            {
                "symbol": report.get("symbol"),
                "report": report,
                "replay": replay,
                "portfolio_plan": portfolio_plan_from_report(report),
                "execution_report": mock_execution_from_report(report),
            }
            for report, replay in zip(reports, replay_rows, strict=True)
        ],
    }
    settings = load_settings()
    backtests_dir = ensure_directory(settings.data_dir / "backtests")
    write_json(backtests_dir / f"{run_id}.json", payload)
    write_json(backtests_dir / "latest.json", payload)
    return payload


def _resolve_report_path(run_id: str) -> Path:
    settings = load_settings()
    reports_dir = settings.data_dir / "reports"
    candidates = sorted(reports_dir.glob(f"*{run_id}*.json"))
    if not candidates:
        raise BacktestError(f"Unable to locate report artifact for run_id '{run_id}'.")
    return candidates[-1]


def run_replay(*, run_id: str, capital: float = DEFAULT_CAPITAL) -> dict[str, Any]:
    report_path = _resolve_report_path(run_id)
    report = json.loads(report_path.read_text(encoding="utf-8"))
    replay = replay_report(report, capital)
    payload: dict[str, Any] = {
        "run_id": run_id,
        "replayed_at": utc_now_iso(),
        "report_path": str(report_path),
        "symbol": report.get("symbol"),
        "experiment_id": report.get("decision_trace_summary", {}).get("trace_id"),
        "dataset_version": f"report:{report.get('symbol', 'unknown').lower()}",
        "config_hash": report.get("config_provenance", {}).get("fingerprint", "unknown"),
        "router_version": f"router:{report.get('config_provenance', {}).get('fingerprint', 'unknown')[:8]}",
        "ranking_version": f"ranking:{report.get('config_provenance', {}).get('fingerprint', 'unknown')[:8]}",
        "risk_version": f"risk:{report.get('config_provenance', {}).get('fingerprint', 'unknown')[:8]}",
        "portfolio_plan": portfolio_plan_from_report(report),
        "execution_report": mock_execution_from_report(report),
        "replay": replay,
    }
    settings = load_settings()
    replay_dir = ensure_directory(settings.data_dir / "replays")
    write_json(replay_dir / f"{run_id}.json", payload)
    write_json(replay_dir / "latest.json", payload)
    return payload


def _build_evidence_refs(report: dict[str, Any]) -> list[str]:
    sources = report.get("evidence_summary", {}).get("data_sources", {})
    refs: list[str] = []
    for name, payload in sources.items():
        if isinstance(payload, dict) and payload.get("available_at"):
            refs.append(f"{name}:{payload['available_at']}")
        elif isinstance(payload, list):
            refs.extend(
                f"{name}:{item.get('available_at', 'unknown')}"
                for item in payload
                if isinstance(item, dict)
            )
    return refs


def _build_agent_outputs(report: dict[str, Any]) -> dict[str, Any]:
    trace = report.get("decision_trace_summary", {})
    top_signal = report.get("evaluation_summary", {}).get("top_signal") or {}
    return {
        "leader": top_signal.get("leader"),
        "leader_scores": trace.get("leader_scores", []),
        "routing": trace.get("routing", {}),
        "specialist_contribution": trace.get("specialist_contribution", {}),
    }


def _signal_from_report(report: dict[str, Any], *, created_at: str) -> dict[str, Any]:
    top_signal = report.get("evaluation_summary", {}).get("top_signal") or {}
    rank_score = float(top_signal.get("composite_rank_score", 0.0))
    return {
        "signal_id": f"{report.get('symbol', 'unknown').lower()}-{created_at}",
        "symbol": report.get("symbol"),
        "direction": "long" if rank_score >= 0.5 else "flat",
        "confidence": float(top_signal.get("confidence", report.get("regime_confidence", 0.0))),
        "agent_outputs": _build_agent_outputs(report),
        "evidence_refs": _build_evidence_refs(report),
        "risk_flags": list(report.get("risk_alerts", {}).get("warnings", [])),
        "created_at": created_at,
        "score": rank_score,
        "portfolio_candidate": bool(report.get("portfolio_suggestion", {}).get("positions")),
        "regime": report.get("active_regime"),
    }


def generate_signals(
    *,
    source: str = INTERNAL_SIM_SOURCE,
    symbols: list[str] | None = None,
    as_of_date: str | None = None,
) -> dict[str, Any]:
    normalized_source = normalize_source(source)
    reports = run_research_cycle(source=normalized_source, symbols=symbols)
    created_at = utc_now_iso()
    artifact_id = created_at.replace(":", "").replace("-", "")
    payload = {
        "artifact_id": artifact_id,
        "generated_at": created_at,
        "source": normalized_source,
        "as_of_date": as_of_date or created_at[:10],
        "signals": [_signal_from_report(report, created_at=created_at) for report in reports],
    }
    settings = load_settings()
    signals_dir = ensure_directory(settings.data_dir / "signals")
    write_json(signals_dir / f"signals_{artifact_id}.json", payload)
    write_json(signals_dir / "latest.json", payload)
    return payload


def _latest_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return cast(dict[str, Any], json.loads(path.read_text(encoding="utf-8")))


def _summarize_universe(snapshots: dict[str, dict[str, Any]]) -> dict[str, Any]:
    rows = list(snapshots.values())
    return {
        "count": len(rows),
        "symbols": [str(row.get("symbol", "")) for row in rows],
        "assets": rows,
    }


def _summarize_signals(signal_payload: dict[str, Any]) -> dict[str, Any]:
    signal_rows = list(signal_payload.get("signals", []))
    candidates = [row for row in signal_rows if row.get("portfolio_candidate")]
    return {
        "generated_at": signal_payload.get("generated_at"),
        "candidate_count": len(candidates),
        "top_candidates": sorted(signal_rows, key=lambda row: float(row.get("score", 0.0)), reverse=True)[:5],
        "rows": signal_rows,
    }


def _build_replay_audit(latest_report: dict[str, Any]) -> dict[str, Any]:
    return {
        "latest_trace_id": latest_report.get("decision_trace_summary", {}).get("trace_id"),
        "state_machine": latest_report.get("decision_trace_summary", {}).get("state_machine", {}),
        "snapshot_sources": latest_report.get("evidence_summary", {}).get("data_sources", {}),
        "agent_outputs": latest_report.get("decision_trace_summary", {}).get("leader_scores", []),
        "ranking_decision": latest_report.get("evaluation_summary", {}).get("top_signal"),
        "risk_decision": latest_report.get("risk_check", {}),
        "portfolio_plan": portfolio_plan_from_report(latest_report),
        "execution_report": mock_execution_from_report(latest_report),
        "latest_replay": None,
    }


def _section_page(title: str, content: str) -> str:
    return f"""
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <title>{escape(title)} | QuanterSwarm Dashboard</title>
    <style>
      :root {{
        --bg: #f4efe6;
        --panel: #fffdf8;
        --ink: #17212b;
        --muted: #5c6b75;
        --line: #ddd3c1;
        --accent: #0b6e4f;
        --accent-soft: #d7efe3;
        --warn: #9a3412;
      }}
      * {{ box-sizing: border-box; }}
      body {{ font-family: Georgia, 'Times New Roman', serif; margin: 0; background: linear-gradient(180deg, #efe7d8 0%, var(--bg) 100%); color: var(--ink); }}
      main {{ max-width: 1120px; margin: 0 auto; padding: 32px 20px 56px; }}
      section {{ background: rgba(255,253,248,0.94); border: 1px solid var(--line); border-radius: 18px; padding: 24px; box-shadow: 0 18px 40px rgba(23,33,43,0.08); }}
      pre {{ overflow-x: auto; white-space: pre-wrap; word-break: break-word; }}
      a {{ color: var(--accent); }}
      .eyebrow {{ font: 600 12px/1.2 ui-monospace, SFMono-Regular, Menlo, monospace; text-transform: uppercase; letter-spacing: 0.08em; color: var(--muted); }}
      .back {{ margin-bottom: 12px; display: inline-block; }}
    </style>
  </head>
  <body>
    <main>
    <section>
      <a class="back" href="/">Back to overview</a>
      <div class="eyebrow">QuanterSwarm Dashboard</div>
      <h1>{escape(title)}</h1>
      {content}
    </section>
    </main>
  </body>
</html>
""".strip()


def _format_float(value: Any, digits: int = 3) -> str:
    try:
        return f"{float(value):.{digits}f}"
    except (TypeError, ValueError):
        return "n/a"


def _render_status_badge(status: Any) -> str:
    normalized = str(status or "unknown")
    tone = "#d7efe3" if normalized in {"ok", "pass"} else "#f6dfd5" if normalized in {"degraded", "disabled"} else "#efe6cc"
    return (
        f"<span style=\"display:inline-block;padding:6px 10px;border-radius:999px;background:{tone};"
        "font:600 12px/1 ui-monospace, SFMono-Regular, Menlo, monospace;text-transform:uppercase;letter-spacing:.06em;\">"
        f"{escape(normalized)}</span>"
    )


def _render_metric_card(label: str, value: Any, detail: str = "") -> str:
    detail_html = f"<div class=\"metric-detail\">{escape(detail)}</div>" if detail else ""
    return (
        "<article class=\"metric-card\">"
        f"<div class=\"metric-label\">{escape(label)}</div>"
        f"<div class=\"metric-value\">{escape(str(value))}</div>"
        f"{detail_html}"
        "</article>"
    )


def _render_signal_rows(signals: list[dict[str, Any]]) -> str:
    rows: list[str] = []
    for signal in signals:
        risk_flags = ", ".join(str(flag) for flag in signal.get("risk_flags", [])) or "clear"
        candidate = "yes" if signal.get("portfolio_candidate") else "no"
        rows.append(
            "<tr>"
            f"<td>{escape(str(signal.get('symbol', '')))}</td>"
            f"<td>{escape(str(signal.get('direction', '')))}</td>"
            f"<td>{_format_float(signal.get('score'))}</td>"
            f"<td>{_format_float(signal.get('confidence'))}</td>"
            f"<td>{escape(str(signal.get('regime', '')))}</td>"
            f"<td>{escape(candidate)}</td>"
            f"<td>{escape(risk_flags)}</td>"
            "</tr>"
        )
    return "".join(rows)


def _render_asset_rows(assets: list[dict[str, Any]]) -> str:
    rows: list[str] = []
    for asset in assets:
        rows.append(
            "<tr>"
            f"<td>{escape(str(asset.get('symbol', '')))}</td>"
            f"<td>{_format_float(asset.get('price'), 2)}</td>"
            f"<td>{_format_float(asset.get('change_pct'))}</td>"
            f"<td>{_format_float(asset.get('volatility'))}</td>"
            f"<td>{escape(', '.join(str(flag) for flag in asset.get('quality_flags', [])) or 'none')}</td>"
            "</tr>"
        )
    return "".join(rows)


def _render_positions(positions: list[dict[str, Any]]) -> str:
    if not positions:
        return "<p class=\"muted-copy\">No active readonly positions.</p>"
    items = "".join(
        "<tr>"
        f"<td>{escape(str(item.get('symbol', '')))}</td>"
        f"<td>{escape(str(item.get('side', item.get('qty', ''))))}</td>"
        f"<td>{_format_float(item.get('market_value'), 2)}</td>"
        f"<td>{_format_float(item.get('unrealized_plpc'))}</td>"
        "</tr>"
        for item in positions
    )
    return (
        "<table><thead><tr><th>Symbol</th><th>Qty / Side</th><th>Market Value</th><th>Unrealized P/L %</th></tr></thead>"
        f"<tbody>{items}</tbody></table>"
    )


def _render_orders(orders: list[dict[str, Any]]) -> str:
    if not orders:
        return "<p class=\"muted-copy\">No recent readonly orders.</p>"
    items = "".join(
        "<tr>"
        f"<td>{escape(str(item.get('symbol', '')))}</td>"
        f"<td>{escape(str(item.get('side', '')))}</td>"
        f"<td>{escape(str(item.get('status', '')))}</td>"
        f"<td>{escape(str(item.get('submitted_at', item.get('created_at', ''))))}</td>"
        "</tr>"
        for item in orders[:10]
    )
    return (
        "<table><thead><tr><th>Symbol</th><th>Side</th><th>Status</th><th>Submitted</th></tr></thead>"
        f"<tbody>{items}</tbody></table>"
    )


def build_dashboard_dataset(
    *,
    source: str = INTERNAL_SIM_SOURCE,
    symbols: list[str] | None = None,
    with_alpaca_readonly: bool = False,
) -> dict[str, Any]:
    from quanter_swarm.adapters.external import AlpacaDashboardSource, InternalSimSource

    normalized_source = normalize_source(source)
    source_adapter = InternalSimSource()
    normalized_symbols = source_adapter.resolve_symbols(symbols)
    universe = source_adapter.snapshot_universe(normalized_symbols)
    signals = generate_signals(source=normalized_source, symbols=normalized_symbols)
    backtest = run_backtest(source=normalized_source, symbols=normalized_symbols)
    latest_report = source_adapter.fetch_reports(normalized_symbols)[0]
    alpaca = AlpacaDashboardSource(enabled=with_alpaca_readonly).fetch_snapshot()
    created_at = utc_now_iso()
    generated_file = created_at.replace(":", "").replace("-", "")
    dataset = {
        "generated_at": created_at,
        "source": normalized_source,
        "overview": {
            "research_date": created_at[:10],
            "market_regime": latest_report.get("active_regime"),
            "recent_cycle_status": latest_report.get("risk_check", {}).get("status", "ok"),
            "recent_backtest_status": "ok",
            "recent_signal_generated_at": signals.get("generated_at"),
            "alpaca_status": alpaca.get("status"),
            "universe_count": len(normalized_symbols),
        },
        "universe": _summarize_universe(universe),
        "signals": _summarize_signals(signals),
        "backtests": {
            "latest": backtest,
            "experiment_comparison": [
                {
                    "experiment_id": backtest.get("run_id"),
                    "dataset_version": backtest.get("dataset_version"),
                    "config_hash": backtest.get("config_hash"),
                    "summary": backtest.get("summary", {}),
                }
            ],
        },
        "replay_audit": _build_replay_audit(latest_report),
        "alpaca_info": alpaca,
        "pages": {
            "overview": "/",
            "signals": "/signals",
            "backtests": "/backtests",
            "replay": "/replay",
            "alpaca": "/alpaca",
        },
    }
    settings = load_settings()
    dashboard_dir = ensure_directory(settings.data_dir / "dashboard")
    write_json(dashboard_dir / f"{generated_file}.json", dataset)
    write_json(dashboard_dir / "latest.json", dataset)
    return dataset


def _render_dashboard_html(dataset: dict[str, Any]) -> str:
    overview = dataset.get("overview", {})
    signals = dataset.get("signals", {}).get("rows", [])
    backtest_latest = dataset.get("backtests", {}).get("latest", {})
    replay = dataset.get("replay_audit", {})
    alpaca = dataset.get("alpaca_info", {})
    universe = dataset.get("universe", {})
    signal_rows = _render_signal_rows(signals)
    asset_rows = _render_asset_rows(list(universe.get("assets", [])))
    backtest_row = backtest_latest.get("summary", {})
    candidate_count = dataset.get("signals", {}).get("candidate_count", 0)
    top_candidate: dict[str, Any] = next(iter(dataset.get("signals", {}).get("top_candidates", [])), {})
    hero_cards = "".join(
        [
            _render_metric_card("Market Regime", overview.get("market_regime", "unknown"), "Current simulation state"),
            _render_metric_card("Universe", overview.get("universe_count", 0), "Tracked internal symbols"),
            _render_metric_card("Candidates", candidate_count, "Signals marked for portfolio review"),
            _render_metric_card("Alpaca", alpaca.get("status", "disabled"), "Readonly external panel"),
        ]
    )
    return f"""
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <title>QuanterSwarm Dashboard</title>
    <style>
      :root {{
        --bg: #f4efe6;
        --panel: rgba(255,253,248,0.94);
        --ink: #17212b;
        --muted: #5c6b75;
        --line: #ddd3c1;
        --accent: #0b6e4f;
        --accent-soft: #d7efe3;
        --danger-soft: #f6dfd5;
      }}
      * {{ box-sizing: border-box; }}
      body {{ font-family: Georgia, 'Times New Roman', serif; margin: 0; background:
        radial-gradient(circle at top left, #efe4d0 0, transparent 35%),
        linear-gradient(180deg, #ede4d4 0%, var(--bg) 100%); color: var(--ink); }}
      main {{ max-width: 1240px; margin: 0 auto; padding: 28px 20px 56px; }}
      section {{ background: var(--panel); border: 1px solid var(--line); border-radius: 20px; padding: 22px; margin-bottom: 18px; box-shadow: 0 18px 40px rgba(23,33,43,0.08); }}
      table {{ width: 100%; border-collapse: collapse; }}
      th, td {{ text-align: left; padding: 10px 8px; border-bottom: 1px solid var(--line); vertical-align: top; }}
      th {{ font: 600 12px/1.1 ui-monospace, SFMono-Regular, Menlo, monospace; text-transform: uppercase; letter-spacing: .06em; color: var(--muted); }}
      h1, h2, h3 {{ margin-top: 0; }}
      a {{ color: var(--accent); }}
      .eyebrow {{ font: 600 12px/1.2 ui-monospace, SFMono-Regular, Menlo, monospace; text-transform: uppercase; letter-spacing: .08em; color: var(--muted); }}
      .lead {{ max-width: 760px; color: var(--muted); }}
      .muted-copy {{ color: var(--muted); }}
      .hero {{ display: grid; grid-template-columns: 1.4fr .8fr; gap: 18px; margin-bottom: 18px; }}
      .hero-banner {{ background: linear-gradient(135deg, #173f35 0%, #235c4b 100%); color: #f6f1e7; overflow: hidden; position: relative; }}
      .hero-banner:after {{ content: ""; position: absolute; inset: auto -30px -30px auto; width: 180px; height: 180px; border-radius: 999px; background: rgba(255,255,255,0.08); }}
      .hero-grid {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px; }}
      .metric-card {{ border: 1px solid var(--line); border-radius: 16px; padding: 16px; background: rgba(255,255,255,0.6); min-height: 96px; }}
      .metric-label {{ font: 600 12px/1.1 ui-monospace, SFMono-Regular, Menlo, monospace; text-transform: uppercase; letter-spacing: .06em; color: var(--muted); margin-bottom: 10px; }}
      .metric-value {{ font-size: 28px; font-weight: 700; }}
      .metric-detail {{ margin-top: 6px; color: var(--muted); font-size: 14px; }}
      .split {{ display: grid; grid-template-columns: 1.1fr .9fr; gap: 18px; }}
      .nav-links {{ display: flex; flex-wrap: wrap; gap: 10px; margin-top: 18px; }}
      .nav-links a {{ text-decoration: none; border: 1px solid rgba(255,255,255,0.22); color: #f8f2e8; padding: 8px 12px; border-radius: 999px; }}
      .callout {{ border-left: 4px solid var(--accent); padding-left: 12px; color: var(--muted); }}
      .stack > * + * {{ margin-top: 12px; }}
      pre {{ margin: 0; overflow-x: auto; white-space: pre-wrap; word-break: break-word; background: #f5efe4; border: 1px solid var(--line); border-radius: 14px; padding: 14px; }}
      .mono {{ font-family: ui-monospace, SFMono-Regular, Menlo, monospace; }}
      @media (max-width: 900px) {{
        .hero, .split {{ grid-template-columns: 1fr; }}
        .hero-grid {{ grid-template-columns: 1fr 1fr; }}
      }}
      @media (max-width: 640px) {{
        main {{ padding: 20px 14px 40px; }}
        .hero-grid {{ grid-template-columns: 1fr; }}
      }}
    </style>
  </head>
  <body>
    <main>
      <div class="hero">
        <section class="hero-banner">
          <div class="eyebrow">Research Overview</div>
          <h1>QuanterSwarm Dashboard</h1>
          <p class="lead">
            Internal simulation remains the primary operating surface. External broker data is readonly and should never
            be treated as execution control.
          </p>
          <div class="stack">
            <div>Generated at <span class="mono">{escape(str(dataset.get("generated_at", "")))}</span></div>
            <div>Recent signal time <span class="mono">{escape(str(overview.get("recent_signal_generated_at", "n/a")))}</span></div>
            <div>Alpaca status { _render_status_badge(alpaca.get("status", "disabled")) }</div>
          </div>
          <div class="nav-links">
            <a href="/signals">Signals</a>
            <a href="/backtests">Backtests</a>
            <a href="/replay">Replay / Audit</a>
            <a href="/alpaca">Alpaca Info</a>
          </div>
        </section>
        <div class="hero-grid">
          {hero_cards}
        </div>
      </div>
      <div class="split">
        <section>
          <div class="eyebrow">Universe</div>
          <h2>Current Simulation Assets</h2>
          <p class="muted-copy">Symbols: {escape(", ".join(universe.get("symbols", [])))}</p>
          <table>
            <thead><tr><th>Symbol</th><th>Price</th><th>Change %</th><th>Volatility</th><th>Quality Flags</th></tr></thead>
            <tbody>{asset_rows}</tbody>
          </table>
        </section>
        <section>
          <div class="eyebrow">Portfolio Attention</div>
          <h2>Top Candidate</h2>
          <p><strong>{escape(str(top_candidate.get("symbol", "n/a")))}</strong> in regime <strong>{escape(str(top_candidate.get("regime", "n/a")))}</strong></p>
          <p class="callout">Direction {escape(str(top_candidate.get("direction", "n/a")))} with score {_format_float(top_candidate.get("score"))} and confidence {_format_float(top_candidate.get("confidence"))}.</p>
          <p class="muted-copy">Risk flags: {escape(", ".join(str(flag) for flag in top_candidate.get("risk_flags", [])) or "clear")}</p>
          <p class="muted-copy">Portfolio candidate: {escape("yes" if top_candidate.get("portfolio_candidate") else "no")}</p>
        </section>
      </div>
      <section>
        <div class="eyebrow">Signals</div>
        <h2>Signal Review Table</h2>
        <table>
          <thead><tr><th>Symbol</th><th>Direction</th><th>Score</th><th>Confidence</th><th>Regime</th><th>Portfolio</th><th>Risk Flags</th></tr></thead>
          <tbody>{signal_rows}</tbody>
        </table>
      </section>
      <div class="split">
        <section>
          <div class="eyebrow">Backtests</div>
          <h2>Latest Summary</h2>
          <div class="hero-grid">
            {_render_metric_card("Return", _format_float(backtest_row.get("return")))}
            {_render_metric_card("Sharpe", _format_float(backtest_row.get("sharpe")))}
            {_render_metric_card("Drawdown", _format_float(backtest_row.get("drawdown")))}
            {_render_metric_card("Turnover", _format_float(backtest_row.get("turnover")))}
          </div>
        </section>
        <section>
          <div class="eyebrow">Replay</div>
          <h2>Audit Snapshot</h2>
          <p>Trace ID <span class="mono">{escape(str(replay.get("latest_trace_id", "n/a")))}</span></p>
          <pre>{json.dumps(replay.get("state_machine", {}), indent=2, ensure_ascii=False)}</pre>
        </section>
      </div>
      <section>
        <div class="eyebrow">Readonly Broker Panel</div>
        <h2>Alpaca</h2>
        <p>{escape(str(alpaca.get("label", "external / read-only")))} { _render_status_badge(alpaca.get("status", "disabled")) }</p>
        <p class="muted-copy">Reason: {escape(str(alpaca.get("reason", "")) or "none")}</p>
        <div class="split">
          <div>
            <h3>Positions</h3>
            {_render_positions(list(alpaca.get("positions", [])))}
          </div>
          <div>
            <h3>Orders</h3>
            {_render_orders(list(alpaca.get("orders", [])))}
          </div>
        </div>
      </section>
    </main>
  </body>
</html>
""".strip()


def create_dashboard_app() -> FastAPI:
    from fastapi import FastAPI
    from fastapi.responses import HTMLResponse, JSONResponse

    app = FastAPI(title="QuanterSwarm Dashboard")

    def current_dataset() -> dict[str, Any]:
        settings = load_settings()
        return _latest_json(settings.data_dir / "dashboard" / "latest.json") or build_dashboard_dataset()

    @app.get("/api/dashboard")
    def dashboard_data() -> JSONResponse:
        return JSONResponse(current_dataset())

    @app.get("/api/signals")
    def dashboard_signals() -> JSONResponse:
        return JSONResponse(current_dataset().get("signals", {}))

    @app.get("/api/backtests")
    def dashboard_backtests() -> JSONResponse:
        return JSONResponse(current_dataset().get("backtests", {}))

    @app.get("/api/replay")
    def dashboard_replay() -> JSONResponse:
        return JSONResponse(current_dataset().get("replay_audit", {}))

    @app.get("/api/alpaca")
    def dashboard_alpaca() -> JSONResponse:
        return JSONResponse(current_dataset().get("alpaca_info", {}))

    @app.get("/", response_class=HTMLResponse)
    def dashboard_home() -> HTMLResponse:
        return HTMLResponse(_render_dashboard_html(current_dataset()))

    @app.get("/signals", response_class=HTMLResponse)
    def dashboard_signals_page() -> HTMLResponse:
        section = current_dataset().get("signals", {})
        rows = _render_signal_rows(list(section.get("rows", [])))
        content = (
            f"<p class=\"muted-copy\">Generated at {escape(str(section.get('generated_at', 'n/a')))}</p>"
            f"<p class=\"muted-copy\">Candidate count: {escape(str(section.get('candidate_count', 0)))}</p>"
            "<table><thead><tr><th>Symbol</th><th>Direction</th><th>Score</th><th>Confidence</th><th>Regime</th><th>Portfolio</th><th>Risk Flags</th></tr></thead>"
            f"<tbody>{rows}</tbody></table>"
        )
        return HTMLResponse(_section_page("Signals", content))

    @app.get("/backtests", response_class=HTMLResponse)
    def dashboard_backtests_page() -> HTMLResponse:
        section = current_dataset().get("backtests", {})
        latest = section.get("latest", {})
        summary = latest.get("summary", {})
        rows = "".join(
            "<tr>"
            f"<td>{escape(str(item.get('symbol', '')))}</td>"
            f"<td>{_format_float(item.get('replay', {}).get('realized_return'))}</td>"
            f"<td>{escape(str(item.get('portfolio_plan', {}).get('mode', 'n/a')))}</td>"
            f"<td>{escape(str(item.get('execution_report', {}).get('status', 'n/a')))}</td>"
            "</tr>"
            for item in latest.get("results", [])
        )
        content = (
            "<div class=\"stack\">"
            f"<p>Run ID <span class=\"mono\">{escape(str(latest.get('run_id', 'n/a')))}</span></p>"
            f"<p>Dataset version <span class=\"mono\">{escape(str(latest.get('dataset_version', 'n/a')))}</span></p>"
            f"<p>Summary: return {_format_float(summary.get('return'))}, sharpe {_format_float(summary.get('sharpe'))}, drawdown {_format_float(summary.get('drawdown'))}, turnover {_format_float(summary.get('turnover'))}</p>"
            "</div>"
            "<table><thead><tr><th>Symbol</th><th>Realized Return</th><th>Portfolio Mode</th><th>Execution Status</th></tr></thead>"
            f"<tbody>{rows}</tbody></table>"
        )
        return HTMLResponse(_section_page("Backtests", content))

    @app.get("/replay", response_class=HTMLResponse)
    def dashboard_replay_page() -> HTMLResponse:
        section = current_dataset().get("replay_audit", {})
        content = (
            f"<p>Trace ID <span class=\"mono\">{escape(str(section.get('latest_trace_id', 'n/a')))}</span></p>"
            "<h3>Risk Decision</h3>"
            f"<pre>{escape(json.dumps(section.get('risk_decision', {}), indent=2, ensure_ascii=False))}</pre>"
            "<h3>Portfolio Plan</h3>"
            f"<pre>{escape(json.dumps(section.get('portfolio_plan', {}), indent=2, ensure_ascii=False))}</pre>"
            "<h3>Execution Report</h3>"
            f"<pre>{escape(json.dumps(section.get('execution_report', {}), indent=2, ensure_ascii=False))}</pre>"
        )
        return HTMLResponse(_section_page("Replay / Audit", content))

    @app.get("/alpaca", response_class=HTMLResponse)
    def dashboard_alpaca_page() -> HTMLResponse:
        section = current_dataset().get("alpaca_info", {})
        content = (
            f"<p>Status { _render_status_badge(section.get('status', 'disabled')) }</p>"
            f"<p>Updated at <span class=\"mono\">{escape(str(section.get('updated_at', 'n/a')))}</span></p>"
            f"<p>Capabilities: {escape(', '.join(str(item) for item in section.get('capabilities', [])))}</p>"
            f"<p>Reason: {escape(str(section.get('reason', '') or 'none'))}</p>"
            "<h3>Account</h3>"
            f"<pre>{escape(json.dumps(section.get('account', {}), indent=2, ensure_ascii=False))}</pre>"
            "<h3>Positions</h3>"
            f"{_render_positions(list(section.get('positions', [])))}"
            "<h3>Orders</h3>"
            f"{_render_orders(list(section.get('orders', [])))}"
        )
        return HTMLResponse(_section_page("Alpaca Info", content))

    return app
