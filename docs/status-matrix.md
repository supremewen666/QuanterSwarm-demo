# Status Matrix

This matrix tracks implementation status against code locations.

## Core Modules

| Area | Status | Primary Code | Notes |
|---|---|---|---|
| Root orchestration | implemented | `src/quanter_swarm/orchestrator/root_agent.py` | Runs single cycle and returns schema-validated report |
| Cycle manager | implemented | `src/quanter_swarm/orchestrator/cycle_manager.py` | Includes decision trace, fallback modes, config-driven flow |
| Regime classification | implemented | `src/quanter_swarm/orchestrator/regime_agent.py` | Confidence, alternatives, smoothing/hysteresis |
| Router | implemented | `src/quanter_swarm/orchestrator/router_agent.py` | Low-confidence policy, leader weights, routing reasons |
| Portfolio construction | implemented | `src/quanter_swarm/decision/portfolio_suggestion.py`, `portfolio_optimizer.py`, `risk_budgeting.py` | Simple/vol-aware/correlation-aware modes |
| Risk guardrail | implemented | `src/quanter_swarm/decision/risk_guardrail.py` | pass/reduced/blocked outputs |
| Paper execution | implemented | `src/quanter_swarm/decision/paper_broker.py`, `src/quanter_swarm/execution/*` | Slippage/fill/cost/audit with event-window behavior |
| Report generation | implemented | `src/quanter_swarm/reporting/report_generator.py`, `markdown_report.py` | JSON + markdown with decision trace |
| API contract | implemented | `src/quanter_swarm/api/schemas.py`, `routes.py` | Single and batch research endpoints |
| Skill packaging | implemented | `skill/quanter-swarm/SKILL.md`, `skill/quanter-swarm/scripts/*` | Trigger rules, schema-first input/output, fallbacks |

## Evaluation and Validation

| Area | Status | Primary Code | Notes |
|---|---|---|---|
| Metrics summary | implemented | `src/quanter_swarm/evaluation/metrics.py` | Includes annualized return, sharpe, sortino, drawdown, turnover proxy |
| Ablation runner | implemented | `src/quanter_swarm/evaluation/experiment_runner.py`, `scripts/run_ablation.py` | Router/specialist/allocation ablations |
| Data quality checks | implemented | `src/quanter_swarm/market/data_quality.py` | Missing/stale/symbol mismatch/outlier checks |
| Golden + E2E tests | implemented | `tests/e2e/test_research_cycle.py`, `tests/golden/*` | Regression protection for system-level outputs |
| Schema-first contracts | implemented | `src/quanter_swarm/contracts.py`, `shared/schemas/*.schema.json` | Enforced in orchestrator/API/CLI |
| CI quality gates | implemented | `.github/workflows/ci.yml`, `pyproject.toml` | Ruff + MyPy + Pytest coverage gate |

## Planned Extensions

| Area | Status | Suggested Location | Notes |
|---|---|---|---|
| Walk-forward backtest/replay | implemented | `src/quanter_swarm/backtest/*`, `scripts/run_backtest.py` | Includes replay execution and attribution |
| Orchestration explicit state machine | implemented | `src/quanter_swarm/orchestrator/states.py`, `cycle_manager.py` | Includes stage trace and short-circuit exits |
| Leaderboard and drift monitoring | implemented | `src/quanter_swarm/evaluation/monitoring.py`, `scripts/export_metrics.py` | Leaderboard, regime breakdown, latency/quality monitoring, drift alerts |
