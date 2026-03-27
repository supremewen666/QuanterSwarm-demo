# Architecture

QuanterSwarm now exposes one explicit control-plane spine plus a separate system-service layer.

## Primary Control Plane

The external architecture is:

```text
Orchestrator
  -> Router
    -> Leaders
      -> Specialists
```

In the codebase, that maps to:

- `Orchestrator`: `src/quanter_swarm/agents/orchestrator/`
- `Router`: `src/quanter_swarm/agents/router/` and `src/quanter_swarm/agents/orchestrator/router_agent.py`
- `Leaders`: `src/quanter_swarm/agents/leaders/`
- `Specialists`: `src/quanter_swarm/agents/specialists/`

The orchestrator owns lifecycle, state transitions, budget-sensitive execution, and short-circuit recovery.
The router selects leaders and specialists.
Leaders produce strategy proposals.
Specialists contribute local evidence only; they do not produce final trade conclusions on their own.

## Minimal Bootstrap Stage

There is still a thin bootstrap evidence stage inside the orchestrator lifecycle.
Its job is limited to assembling the minimum context required before routing:

- point-in-time snapshot assembly
- provider metadata and provenance capture
- regime evidence required by the router

This stage exists for correctness, but it is intentionally kept thin so it does not become a second hidden orchestrator.

## System Services

The following capabilities are expressed as services, not pseudo-agents:

- `snapshot`: `src/quanter_swarm/services/snapshot/`
- `data/provider`: `src/quanter_swarm/services/data/`
- `ranking`: `src/quanter_swarm/services/ranking/`
- `evolution`: `src/quanter_swarm/services/evolution/`
- `risk`: `src/quanter_swarm/services/risk/`
- `portfolio`: `src/quanter_swarm/services/portfolio/`
- `execution`: `src/quanter_swarm/services/execution/`
- `reporting`: `src/quanter_swarm/services/reporting/`

These services are consumed by the control plane, but they are not presented as agents.

## Application Layer

All formal entrypoints route through the shared application layer:

- `RunResearchCycle`
- `RunBatchResearch`
- `RunBacktest`
- `RunReplay`
- `BuildDashboardData`
- `GetProviderTopology`
- `RiskPrecheck`
- `PromoteLeaderVersion`

This keeps API, CLI, and skill/external adapters on one business flow instead of letting each adapter stitch together its own internal path.

## Trace and Report Visibility

Each cycle emits a `decision_trace_summary` and `architecture_summary` that make the layer boundaries visible.
These artifacts include:

- orchestrator state sequence
- router-selected and router-rejected candidates
- leader score and proposal summaries
- selected specialists
- system-service verdicts for ranking, risk, portfolio, execution, and reporting
- a run-level trace id for correlation across logs, reports, and tests

See [docs/example-cycle-output.md](docs/example-cycle-output.md) for a compact example.

## Protocol Compatibility Note

The current implementation is MCP-compatible first and A2A-ready later:

- use cases are task-shaped and can be wrapped as tools or remote actions later
- adapters already sit outside the application layer, so protocol wrappers do not need to know orchestration internals
- no network protocol abstraction is forced into the core runtime yet

This keeps the current MVP concrete while leaving room for later MCP tool exposure or A2A-style task endpoints.

## Execution Simulation

Paper execution models currently include:

- volatility and participation-aware slippage
- partial fill assumptions
- open-session penalty and gap sensitivity
- fixed and bps commission costs
- structured execution audit payload

## Validation and Provenance

The platform includes:

- config validation for routing/allocation policies
- data quality checks for missing/stale/symbol mismatch issues
- experiment runners for routing/allocation ablations
- deterministic config provenance embedded in reports
