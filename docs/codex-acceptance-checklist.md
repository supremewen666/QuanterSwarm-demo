# Codex Acceptance Checklist

This checklist maps the current repository state against the requirements in `codex.md`.

## Overall Status

- `implemented`: completed in this refactor round
- `partial`: direction established, but not fully closed
- `deferred`: explicitly postponed for a later round

## Core Objectives


| Requirement                                                                  | Status      | Evidence                                                                                                                                         |
| ---------------------------------------------------------------------------- | ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------ |
| External architecture shows `Orchestrator -> Router -> Leader -> Specialist` | implemented | `README.md`, `docs/architecture.md`, `docs/example-cycle-output.md`, `src/quanter_swarm/services/reporting/report_generator.py`                  |
| Non-agent capabilities are expressed as system services                      | implemented | `src/quanter_swarm/services/` and `architecture_summary.system_services`                                                                         |
| API / CLI / skill share one application layer                                | implemented | `src/quanter_swarm/application/`, `src/quanter_swarm/adapters/api/routes.py`, `src/quanter_swarm/cli.py`, `src/quanter_swarm/skill_interface.py` |
| Future dashboard / MCP / A2A compatibility is preserved                      | implemented | `docs/architecture.md`, `README.md`, task-shaped application use cases                                                                           |


## In-Scope Deliverables

### 3.1 Explicit asymmetric hierarchy


| Requirement                                          | Status      | Evidence                                                                                                    |
| ---------------------------------------------------- | ----------- | ----------------------------------------------------------------------------------------------------------- |
| Orchestrator lifecycle/state machine is explicit     | implemented | `src/quanter_swarm/agents/orchestrator/cycle_manager.py`, `src/quanter_swarm/agents/orchestrator/states.py` |
| Router owns regime/budget/candidate activation logic | implemented | `src/quanter_swarm/agents/router/router.py`, `src/quanter_swarm/agents/orchestrator/router_agent.py`        |
| Leaders produce strategy proposals                   | implemented | `src/quanter_swarm/agents/leaders/`                                                                         |
| Specialists only contribute local evidence/context   | implemented | `src/quanter_swarm/agents/specialists/`, routed specialist flow in `cycle_manager.py`                       |


### 3.2 Unified application service layer


| Requirement                                      | Status      | Evidence                                                                    |
| ------------------------------------------------ | ----------- | --------------------------------------------------------------------------- |
| `RunResearchCycle`                               | implemented | `src/quanter_swarm/application/use_cases/control_plane.py`                  |
| `RunBatchResearch`                               | implemented | `src/quanter_swarm/application/use_cases/control_plane.py`                  |
| `RunBacktest`                                    | implemented | `src/quanter_swarm/application/use_cases/workflows.py`                      |
| `RunReplay`                                      | implemented | `src/quanter_swarm/application/use_cases/workflows.py`                      |
| `BuildDashboardData`                             | implemented | `src/quanter_swarm/application/use_cases/workflows.py`                      |
| `GetProviderTopology`                            | implemented | `src/quanter_swarm/application/use_cases/system_services.py`                |
| `RiskPrecheck`                                   | implemented | `src/quanter_swarm/application/use_cases/system_services.py`                |
| `PromoteLeaderVersion`                           | implemented | `src/quanter_swarm/application/use_cases/system_services.py`                |
| API only calls system layer                      | implemented | `src/quanter_swarm/adapters/api/routes.py`                                  |
| CLI only calls system layer                      | implemented | `src/quanter_swarm/cli.py`, `src/app/cli/*.py`, `src/quanter_swarm/main.py` |
| Skill / external adapters only call system layer | implemented | `src/quanter_swarm/skill_interface.py`                                      |


### 3.3 Services separated from agent hierarchy


| Requirement                    | Status      | Evidence                                                                   |
| ------------------------------ | ----------- | -------------------------------------------------------------------------- |
| snapshot / provider as service | implemented | `src/quanter_swarm/services/snapshot/`, `src/quanter_swarm/services/data/` |
| ranking as service             | implemented | `src/quanter_swarm/services/ranking/`                                      |
| evolution as service           | implemented | `src/quanter_swarm/services/evolution/`                                    |
| risk as service                | implemented | `src/quanter_swarm/services/risk/`                                         |
| portfolio as service           | implemented | `src/quanter_swarm/services/portfolio/`                                    |
| execution as service           | implemented | `src/quanter_swarm/services/execution/`                                    |
| reporting as service           | implemented | `src/quanter_swarm/services/reporting/`                                    |


### 3.4 Minimal bootstrap evidence stage


| Requirement                                            | Status      | Evidence                                                                                                                   |
| ------------------------------------------------------ | ----------- | -------------------------------------------------------------------------------------------------------------------------- |
| Thin bootstrap stage retained for pre-routing evidence | implemented | `decision_trace_summary.state_machine`, `docs/architecture.md`, `src/quanter_swarm/services/reporting/report_generator.py` |
| Bootstrap stage is explicitly bounded                  | implemented | `docs/architecture.md`                                                                                                     |


### 3.5 Trace / report layer visibility


| Requirement                             | Status      | Evidence                                                                                  |
| --------------------------------------- | ----------- | ----------------------------------------------------------------------------------------- |
| Orchestrator state sequence visible     | implemented | `decision_trace_summary.state_machine`                                                    |
| Router decisions visible                | implemented | `router_decision`, `decision_trace_summary.routing`                                       |
| Selected / rejected leaders visible     | implemented | `architecture_summary.control_plane.router`, `decision_trace_summary.rejected_candidates` |
| Selected / rejected specialists visible | implemented | `architecture_summary.control_plane.router.selected_specialists`                          |
| Leader proposal summaries visible       | implemented | `architecture_summary.control_plane.leaders`                                              |
| Service verdicts visible                | implemented | `architecture_summary.system_services`                                                    |
| Example output included                 | implemented | `docs/example-cycle-output.md`                                                            |


### 3.6 Industrialization directions

These were explicitly not the current priority in the latest instruction, so they are tracked as deferred rather than missing.


| Requirement                                                           | Status   | Notes                                                               |
| --------------------------------------------------------------------- | -------- | ------------------------------------------------------------------- |
| Data discipline hardening beyond current PIT/provenance baseline      | deferred | Basic PIT/provenance exists; deeper industrial hardening postponed  |
| More realistic execution simulation interfaces                        | partial  | Slippage/fill/cost scaffolding exists, but not fully extended       |
| Execution control plane boundaries like kill switch / reconciliation  | deferred | Not expanded in this round                                          |
| Evolution governance beyond current promotion/rollback/audit baseline | partial  | Promotion gate and rollback logic exist; deeper governance deferred |
| Reliability boundaries like idempotent run                            | partial  | Timeout/fallback/degraded mode exist; idempotency not formalized    |
| Security / permissions boundaries                                     | deferred | Not addressed in this round                                         |


### 3.7 Token / cost controls


| Requirement                                 | Status      | Evidence                                              |
| ------------------------------------------- | ----------- | ----------------------------------------------------- |
| Routed activation preserved                 | implemented | Router and cycle manager flow                         |
| Shared specialists preserved                | implemented | Shared specialist registry/activation path            |
| Ephemeral leaders preserved                 | implemented | Leader flow and architecture docs                     |
| Structured evidence over prompt replay      | implemented | Reports, evidence summaries, trace outputs            |
| Budget-aware routing hooks                  | implemented | Router budget configuration and observability metrics |
| Caching hooks                               | implemented | Snapshot cache services                               |
| Cost metrics exposure                       | implemented | `src/quanter_swarm/services/monitoring/metrics.py`    |
| Small-model pre-screen / large-model verify | deferred    | Not implemented in this round                         |


### 3.8 Protocol compatibility


| Requirement                         | Status      | Evidence                                                                       |
| ----------------------------------- | ----------- | ------------------------------------------------------------------------------ |
| MCP-compatible-first use case shape | implemented | Application-layer task-shaped use cases, `docs/architecture.md`                |
| A2A-ready later without overdesign  | implemented | Protocol compatibility note in docs, adapters separated from application layer |
| No ANP overdesign                   | implemented | No premature network protocol layer introduced                                 |


## Suggested Deliverables


| Deliverable                                  | Status      | Evidence                                                                                                           |
| -------------------------------------------- | ----------- | ------------------------------------------------------------------------------------------------------------------ |
| Architecture refactor plan                   | implemented | `README.md`, `docs/architecture.md`, prior refactor changes in code layout                                         |
| At least one API endpoint via system layer   | implemented | `src/quanter_swarm/adapters/api/routes.py`                                                                         |
| At least one CLI command via system layer    | implemented | `src/quanter_swarm/cli.py`                                                                                         |
| At least one trace/report showing all layers | implemented | `src/quanter_swarm/services/reporting/report_generator.py`, `docs/example-cycle-output.md`                         |
| Documentation updates                        | implemented | `README.md`, `docs/architecture.md`, `docs/example-cycle-output.md`, `docs/monitoring.md`, `docs/status-matrix.md` |
| Validation artifact                          | implemented | tests and example output                                                                                           |


## Acceptance Criteria


| Criteria                     | Status      | Evidence                                                                |
| ---------------------------- | ----------- | ----------------------------------------------------------------------- |
| 7.1 Architecture visibility  | implemented | README, architecture doc, report output                                 |
| 7.2 Entry consistency        | implemented | Shared application use cases across API/CLI/skill                       |
| 7.3 Service boundary clarity | implemented | Ranking/risk/execution/reporting/evolution under `services/`            |
| 7.4 Extensibility            | implemented | Dashboard/workflow use cases plus protocol-compatible application layer |
| 7.5 Incremental landability  | implemented | Additive refactor with compatibility shims and passing tests            |


## Validation Snapshot

- `pytest tests/test_application_use_cases.py tests/test_ranking_engine.py tests/test_report_generator.py tests/test_api_routes.py tests/test_root_agent.py tests/test_monitoring_layer.py`
- Result: `20 passed`
- `python -m compileall src/quanter_swarm docs scripts`
- Result: passed

