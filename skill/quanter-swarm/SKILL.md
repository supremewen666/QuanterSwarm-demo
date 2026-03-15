---
name: quanter-swarm
description: Use this skill for regime-aware stock research, routed multi-strategy analysis, risk-reviewed portfolio suggestions, paper-trading simulation, or OpenClaw-ready equity reports. Validate configs first, then run one cycle, then export JSON or markdown only if the user needs an artifact.
---

# QuanterSwarm

Use the repository's deterministic workflow before improvising with custom reasoning.

## Use this skill when

- the user wants a stock research cycle with market regime routing
- the task needs structured output for allocation, paper trading, or reporting
- the user asks for a concise but production-minded OpenClaw skill workflow
- the request should stay in research mode and paper trading by default

## Do not use this skill when

- the user wants real broker execution
- the task is high-frequency trading or unrestricted strategy generation
- the request is unrelated to equity research, risk review, or portfolio suggestions

## Fast path

1. Run `python skill/quanter-swarm/scripts/validate_configs.py`.
2. Run `python skill/quanter-swarm/scripts/run_analysis_cycle.py <SYMBOL>` for research output.
3. Run `python skill/quanter-swarm/scripts/export_report.py <SYMBOL>` only when the user needs a saved artifact.
4. Run `python skill/quanter-swarm/scripts/run_ablation.py <router_ablation|specialist_ablation|allocation_ablation> <SYMBOL>` when the user asks for evidence or strategy comparison.

## Input contract (schema-first)

Use this request shape whenever possible:

```json
{
  "symbol": "AAPL",
  "symbols": ["AAPL", "MSFT"],
  "horizon": "1w",
  "portfolio_mode": "single",
  "risk_tolerance": "medium",
  "output_format": "json",
  "data_freshness_preference": "latest"
}
```

Notes:

- at least one of `symbol` or `symbols` is required
- `output_format` can be `json` or `markdown`
- for multi-ticket comparison, prefer `symbols` and batch endpoint

## Inputs to confirm only if needed

- ticker symbol or a clear default from the user's request
- whether the user wants stdout output or a saved file
- whether the final artifact should be `json` or `markdown`

## Workflow

1. Validate repo configs before using routing, risk, or portfolio logic.
2. Run one routed cycle. Prefer `run_analysis_cycle.py` unless the user explicitly asks for paper-trade actions.
3. Use the structured report fields directly. Do not paraphrase away the regime, risk alerts, or allocation mode.
4. Export a file only when the user needs a reusable artifact.

## Progressive references

Read only the reference that matches the current task:

- `references/architecture.md` for system layout and module responsibilities
- `references/routing-rules.md` when the user asks why certain leaders were activated
- `references/regime-policy.md` and `references/risk-policy.md` for regime and guardrail interpretation
- `references/portfolio-policy.md` and `references/paper-trading-policy.md` for allocation and simulated execution behavior
- `references/output-format.md` when shaping the final response or exported artifact
- `references/operating-rules.md` only when token/latency tradeoffs matter

## Scripts

- `scripts/validate_configs.py`
  Verifies required configs exist, parse cleanly, and only reference known leaders.
- `scripts/run_analysis_cycle.py [symbol] --format json|markdown --output <path>`
  Runs one research cycle and prints or saves the result.
- `scripts/run_paper_cycle.py [symbol] --format json|markdown --output <path>`
  Runs one paper-trading cycle with the same structured output surface.
- `scripts/export_report.py [symbol] --format json|markdown --output <path>`
  Saves a user-facing report artifact under `data/reports/` by default.
- `scripts/run_ablation.py <router_ablation|specialist_ablation|allocation_ablation> [symbol]`
  Runs reproducible experiment comparisons and writes JSON + markdown under `data/experiments/`.

## Output contract (minimum fields)

- `regime` / `active_regime`
- `regime_confidence`
- `active_strategy_teams`
- `thesis_summary` (via one-page summary highlights)
- `factor_scorecard`
- `risk_alerts`
- `portfolio_suggestion`
- `paper_trade_actions`
- `evaluation_summary`
- `decision_trace_summary`

## Fallback and downgrade rules

Apply these rules explicitly in outputs:

1. Missing news:
- downgrade to market + fundamentals, set sentiment to neutral, add `sentiment_fallback` to trace.
2. Missing fundamentals:
- downgrade to technical/price-action emphasis, and mark low-confidence in summary.
3. Low regime confidence:
- use fallback leaders or no-trade according to `router.yaml` policy.
4. All ideas below threshold:
- return `no_trade`; do not force recommendations.

When fallback is active, include a short limitation statement in the user-facing summary.

## Golden examples

1. Single-ticket research:
- input: `{"symbol":"AAPL","horizon":"1w","output_format":"markdown"}`
- expected: one structured report with regime confidence and decision trace summary.
2. Multi-ticket ranking:
- input: `{"symbols":["AAPL","MSFT","NVDA"],"portfolio_mode":"multi"}`
- expected: batch results with comparable scorecards and risk alerts.
3. Risk-off scenario:
- input: `{"symbol":"XLF","risk_tolerance":"low"}`
- expected: reduced exposure or no-trade if guardrail blocks.
4. Event-driven scenario:
- input: `{"symbol":"TSLA","horizon":"1d"}`
- expected: event impact and execution assumptions visible in trace.
5. No-trade scenario:
- input: low-confidence / weak-signal market state
- expected: `portfolio_suggestion.mode = no_trade` and explicit rationale.

## Hard rules

- keep the system in research plus paper-trading mode unless the user explicitly changes scope
- run regime classification before leader selection
- reuse shared specialists instead of leader-local data fetches
- keep leaders ephemeral and outputs structured
- preserve `no_trade` and `reduced_exposure` outcomes when risk requires it

## Response requirements

- keep the final answer concise and decision-oriented
- separate research findings from action suggestions
- state risk warnings explicitly
- if confidence is weak, prefer watchlist or reduced exposure over forced trades
- make it clear that the result is for research and simulation by default
