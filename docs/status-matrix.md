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
| Data provider interface | implemented | `src/quanter_swarm/data/base.py`, `src/quanter_swarm/market/snapshot_builder.py`, `tests/test_data_provider.py` | Market snapshot assembly now depends on a provider contract instead of direct feed calls |
| Mock and file data providers | implemented | `src/quanter_swarm/data/mock_provider.py`, `src/quanter_swarm/data/file_provider.py`, `tests/test_mock_and_file_provider.py` | In-memory fixtures and CSV/parquet-backed datasets now satisfy the shared provider contract |
| Data snapshot metadata | implemented | `src/quanter_swarm/market/snapshot_builder.py`, `tests/test_data_provider.py` | Snapshots now expose `snapshot_hash`, `data_source`, and `timestamp` alongside `as_of_ts` |
| Data cache | implemented | `src/quanter_swarm/data/cache.py`, `src/quanter_swarm/specialists/data_fetch_specialist.py`, `tests/test_data_cache.py` | Snapshot fetches can now reuse memory or file-backed cache entries |
| Backtest event system | implemented | `src/quanter_swarm/backtest/events.py`, `src/quanter_swarm/backtest/replay_engine.py`, `tests/test_backtest_events.py` | Replay flows now emit typed market, signal, order, fill, and portfolio-update events |
| Backtest portfolio models | implemented | `src/quanter_swarm/backtest/models.py`, `src/quanter_swarm/backtest/replay_engine.py`, `tests/test_backtest_models.py` | Replay flows now validate orders, fills, positions, and portfolios against shared backtest models |
| Backtest cost model | implemented | `src/quanter_swarm/backtest/costs.py`, `src/quanter_swarm/backtest/replay_engine.py`, `tests/test_backtest_costs.py` | Replay now exposes explicit transaction-fee and slippage components instead of only aggregate cost ratio |
| Walk-forward window controls | implemented | `src/quanter_swarm/backtest/walk_forward.py`, `tests/test_backtest.py` | Walk-forward runs now accept and report train, test, and rolling window parameters with per-step window assignment |
| Backtest metrics | implemented | `src/quanter_swarm/backtest/metrics.py`, `src/quanter_swarm/backtest/walk_forward.py`, `tests/test_backtest_metrics.py` | Walk-forward summaries now use dedicated backtest Sharpe, Sortino, max drawdown, turnover, and win rate metrics |
| Experiment presets | implemented | `experiments/*.yaml`, `tests/test_experiment_configs.py` | Baseline single-agent, fixed multi-agent, routed multi-agent, and routed ephemeral experiment configs are now versioned |
| Configured experiment runner | implemented | `src/quanter_swarm/experiments/runner.py`, `tests/test_configured_experiment_runner.py` | Preset experiment configs can now be executed directly as single-agent, fixed multi-agent, routed multi-agent, and routed ephemeral runs |
| Experiment artifact export | implemented | `src/quanter_swarm/experiments/runner.py`, `tests/test_configured_experiment_runner.py` | Configured experiments now export `experiment_table.csv`, `equity_curve.png`, and `drawdown_curve.png` alongside JSON and markdown |
| Structured logging | implemented | `src/quanter_swarm/utils/logging.py`, `src/quanter_swarm/orchestrator/cycle_manager.py`, `tests/test_structured_logging.py` | Runtime logs now emit JSON records with trace ID, cycle state, agent name, latency, and status |
| Observability metrics | implemented | `src/quanter_swarm/observability/metrics.py`, `src/quanter_swarm/orchestrator/cycle_manager.py`, `tests/test_observability_metrics.py` | Each cycle now emits router latency, agent latency, cycle success rate, and estimated token cost in the trace summary |
| Risk engine | implemented | `src/quanter_swarm/risk/engine.py`, `src/quanter_swarm/risk/rules.py`, `tests/test_risk_engine.py` | All trade candidates now pass explicit max-position, leverage, daily-loss, earnings, and volatility rules before execution |
| CI quality gates | implemented | `.github/workflows/ci.yml`, `pyproject.toml` | Ruff + MyPy + Pytest coverage gate |

## Planned Extensions

| Area | Status | Suggested Location | Notes |
|---|---|---|---|
| Walk-forward backtest/replay | implemented | `src/quanter_swarm/backtest/*`, `scripts/run_backtest.py` | Includes replay execution and attribution |
| Orchestration explicit state machine | implemented | `src/quanter_swarm/orchestrator/states.py`, `cycle_manager.py` | Includes stage trace and short-circuit exits |
| Leaderboard and drift monitoring | implemented | `src/quanter_swarm/evaluation/monitoring.py`, `scripts/export_metrics.py` | Leaderboard, regime breakdown, latency/quality monitoring, drift alerts |
