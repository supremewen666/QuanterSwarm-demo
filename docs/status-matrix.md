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
| Project quality baseline | implemented | `pyproject.toml`, `Makefile`, `tests/test_project_tooling.py` | Ruff/Pytest/MyPy entrypoints aligned with local development and CI |
| Centralized runtime defaults | implemented | `src/quanter_swarm/config/defaults.py`, `src/quanter_swarm/config/settings.py`, `tests/test_settings_config.py` | Shared defaults for symbols, token budget, risk thresholds, and backtest window |
| Unified orchestration schemas | implemented | `src/quanter_swarm/contracts.py`, `tests/test_cycle_report_schema.py` | Typed agent context/results plus router, risk, portfolio, and cycle report contracts |
| Typed exception system | implemented | `src/quanter_swarm/errors.py`, `tests/test_schema_contracts.py`, `tests/test_experiment_runner.py` | Domain errors for router, agent execution, data loading, risk validation, and backtest failures |
| Base agent interface | implemented | `src/quanter_swarm/agents/base.py`, `tests/test_base_agent_interface.py` | Shared async agent protocol adopted by leaders, specialists, and orchestration agents |
| Agent registry | implemented | `src/quanter_swarm/agents/registry.py`, `tests/test_agent_registry.py` | Centralized registration and lookup for leaders, specialists, and orchestration agents |
| Capability-aware agent abstractions | implemented | `src/quanter_swarm/leaders/base_leader.py`, `src/quanter_swarm/specialists/base_specialist.py`, `tests/test_agent_capabilities.py` | Leader and specialist metadata now drives regime-aware router filtering |
| Agent executor | implemented | `src/quanter_swarm/orchestrator/agent_executor.py`, `tests/test_agent_executor.py` | Concurrent specialist execution with timeout and partial failure support |
| Router module | implemented | `src/quanter_swarm/router/router.py`, `tests/test_router_module.py` | Regime detection and leader/specialist selection moved out of orchestrator classes |
| Router explainability | implemented | `src/quanter_swarm/contracts.py`, `src/quanter_swarm/orchestrator/cycle_manager.py`, `tests/test_router_agent.py` | Cycle reports now include explicit routing reasons and rejected candidates |
| Regime detector | implemented | `src/quanter_swarm/router/regime_detector.py`, `tests/test_regime_agent.py`, `tests/test_router_module.py` | Stable canonical bull/bear/sideways/volatile buckets layered under backward-compatible detailed labels |
| Cost-aware routing | implemented | `src/quanter_swarm/router/router.py`, `src/quanter_swarm/orchestrator/cycle_manager.py`, `tests/test_router_module.py` | Specialist activation now respects token budget, latency budget, and max specialists per cycle |
| Cycle state taxonomy | implemented | `src/quanter_swarm/orchestrator/states.py`, `tests/test_cycle_states.py` | High-level cycle states now map existing stage records into a stable orchestration state model |
| Cycle manager state machine handlers | implemented | `src/quanter_swarm/orchestrator/cycle_manager.py`, `tests/test_root_agent.py` | `run_cycle` now delegates through explicit `_state_*` functions and emits state transition sequence |
| Structured trace system | implemented | `src/quanter_swarm/observability/trace.py`, `src/quanter_swarm/orchestrator/cycle_manager.py`, `tests/test_trace_system.py` | Each cycle now emits a reusable trace payload with router decision, activated agents, latency, and risk result |
| CI quality gates | implemented | `.github/workflows/ci.yml`, `pyproject.toml` | Ruff + MyPy + Pytest coverage gate |

## Planned Extensions

| Area | Status | Suggested Location | Notes |
|---|---|---|---|
| Walk-forward backtest/replay | implemented | `src/quanter_swarm/backtest/*`, `scripts/run_backtest.py` | Includes replay execution and attribution |
| Orchestration explicit state machine | implemented | `src/quanter_swarm/orchestrator/states.py`, `cycle_manager.py` | Includes stage trace and short-circuit exits |
| Leaderboard and drift monitoring | implemented | `src/quanter_swarm/evaluation/monitoring.py`, `scripts/export_metrics.py` | Leaderboard, regime breakdown, latency/quality monitoring, drift alerts |
