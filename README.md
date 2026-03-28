# QuanterSwarm

An architecture-driven multi-agent research system for equities, built to be both a standalone paper-trading platform and a packageable OpenClaw skill.

QuanterSwarm is not centered on “more agents”. Its innovation is the architecture itself: routed activation, shared specialists, ephemeral leaders, persistent meta-learning, point-in-time evidence, and bounded execution all working as one coherent system.

It is designed to feel like a compact quant research operating system, not a prompt demo with market flavor.

## Why QuanterSwarm

Most multi-agent trading projects stop at orchestration theater:

- too many agents
- too little data discipline
- no replayable evidence
- no bounded evolution
- no real separation between research and execution

QuanterSwarm takes the opposite path.

- It uses routed activation instead of always-on agent chatter.
- It keeps leaders ephemeral and pushes persistent learning into registries and audit stores.
- It treats data freshness, `available_at`, provenance, and reliability as first-class concerns.
- It separates research architecture from execution policy.
- It is designed so the same system can run as an application and as an OpenClaw skill package.

The architectural idea is simple but important:

- specialists are shared capabilities, not duplicated sub-agents
- leaders are disposable inference units, not stateful personalities
- memory and evolution live outside the leaders
- routing is a systems problem, not a prompt trick
- evidence is part of the output contract, not an afterthought
- skill packaging is treated as a first-class deployment target

The result is a system that is easier to reason about, easier to test, and much closer to research infrastructure than to a generic agent sandbox.

## Architectural Innovation

The main contribution of QuanterSwarm is not a single model or a single strategy. It is the composition pattern.

### 1. Routed multi-agent execution

Instead of activating every agent on every cycle, QuanterSwarm first detects market regime and then activates only the subset of specialists and leaders that fit the current state, task, and budget.

This reduces:

- wasted token and latency budget
- duplicated reasoning
- noisy inter-agent interactions
- unstable output composition

### 2. Shared specialists + ephemeral leaders

This is the core design move.

- Specialists are reusable capability nodes
- Leaders are short-lived strategy nodes

That gives the system a strong division of labor:

- specialists gather, compress, and structure information
- leaders turn structured context into strategy hypotheses

This is more scalable than copying full agent stacks per strategy, and more controllable than letting every strategy own its own memory and tools.

### 3. Persistent learning outside the agent loop

QuanterSwarm does not let ephemeral leaders accumulate hidden state.

Persistent learning is externalized into:

- `LeaderRegistry`
- `EventMemoryStore`
- `EvolutionAuditLog`
- `PromotionGate`
- `EvolutionManager`

That means the runtime swarm stays lightweight while the system still improves over time.

### 4. Point-in-time evidence as a systems primitive

The architecture assumes that a research agent system is only as credible as its data discipline.

So snapshots are designed to carry:

- provenance
- `available_at`
- reliability score
- quality flags
- evidence sections for reporting and replay

This is what lets the same architecture support research, monitoring, replay, and later stricter backtesting.

### 5. Skill-native packaging

QuanterSwarm is not only a repo. It is intentionally structured to be exported as a skill under [skill/quanter-swarm](skill/quanter-swarm/).

That matters because the architecture is portable:

- the swarm topology can be packaged
- operating rules can travel with the skill
- prompts, schemas, and scripts can stay aligned
- OpenClaw can reuse the same orchestration contract instead of wrapping an unrelated script

This makes QuanterSwarm useful both as a local system and as a deployable agent capability.

## What It Does

QuanterSwarm runs a full research cycle for one symbol or a batch of symbols:

1. Fetch market, fundamentals, news, macro, and auxiliary evidence
2. Build a point-in-time snapshot with metadata and reliability scores
3. Detect the active regime
4. Route the right specialists and leaders
5. Engineer features and score candidate strategies
6. Apply weak-prior evolution and posterior ranking
7. Enforce risk and portfolio guardrails
8. Produce paper-trade actions
9. Export a structured report with evidence, trace, and provider topology

## System Character

QuanterSwarm is opinionated in a few important ways:

- Research first: outputs are research artifacts and paper-trade suggestions
- Bounded by design: no unrestricted strategy mutation
- Replayable: backtests and reports can carry evidence and event traces
- Configurable: providers, routing, risk, ranking, and evolution all live behind config or typed abstractions
- Auditable: evolution proposals and event memory are stored outside ephemeral leaders

## Architecture

### End-to-end flow

```text
Application Adapters (API / CLI / Skill)
  -> Application Use Cases
    -> Orchestrator
      -> Router
        -> Leaders
          -> Specialists
    -> System Services
      -> Snapshot / Provider
      -> Ranking
      -> Evolution
      -> Risk
      -> Portfolio
      -> Execution
      -> Reporting
```

### Core runtime graph

```text
External Adapters
  -> RunResearchCycle / RunBatchResearch / GetProviderTopology / RiskPrecheck / PromoteLeaderVersion
    -> RootAgent (Orchestrator)
      -> RouterAgent (Router)
        -> Ephemeral Leaders
          -> Shared Specialists

System Services
  -> Snapshot / Provider Factory
  -> Ranking Engine
  -> Evolution Manager
  -> Risk Engine
  -> Portfolio Builder
  -> Paper Executor
  -> Report Generator
```

### Layering rules

- External adapters do not call orchestration internals directly.
- API, CLI, and skill adapters share the same application-layer use cases.
- Risk, ranking, execution, evolution, reporting, and provider topology are expressed as system services, not pseudo-agents.
- A thin bootstrap stage still exists for snapshot assembly and regime evidence before routing, but it stays inside the orchestrator lifecycle.
- The application layer is shaped so these use cases can later be wrapped as MCP tools or remote task endpoints without exposing orchestration internals.

### What makes this graph different

The graph is intentionally asymmetric.

- The system has one orchestration spine
- many reusable specialists
- a bounded leader set
- externalized persistence for learning

This avoids the common multi-agent anti-pattern where every agent owns too much:

- too much context
- too much memory
- too many tools
- too many overlapping responsibilities

QuanterSwarm instead pushes the system toward explicit coordination boundaries.

### Shared specialists

- `DataFetchSpecialist`
- `MemoryCompressionSpecialist`
- `RiskSpecialist`
- `SentimentSpecialist`
- `MacroEventSpecialist`
- `FeatureEngineeringSpecialist`

These specialists are shared across cycles and only activated when routing says they are useful.

### Ephemeral strategy leaders

- `MomentumLeader`
- `MeanReversionLeader`
- `StatArbLeader`
- `BreakoutEventLeader`

Leaders do not carry long-term state. They read current parameters, priors, and constraints from external stores, propose a strategy view, and disappear after the cycle.

## Data Layer

The data stack is built around a provider abstraction plus point-in-time snapshot assembly.

### Snapshot properties

Each snapshot can carry:

- `as_of_ts`
- `available_at`
- `ingested_at`
- `snapshot_hash`
- `source`
- `source_type`
- `record_id`
- `schema_version`
- `quality_flags`
- `reliability_score`

This makes the same abstraction usable for research, replay, reporting, and future stricter backtesting.

### Built-in provider modes

Current repository support includes:

- `deterministic`
  - synthetic local feeds for prices, news, fundamentals, and macro
- `file`
  - CSV / Parquet-backed offline datasets
- `polygon_market_data`
- `fmp_market_data`
- `sec_filings`
- `sec_xbrl_facts`
- `company_ir`
- `fmp_shares_float`
- `fred_macro`
- `alfred_vintage_macro`
- `composite`
  - combine market, filings, XBRL, float, macro, and vintage macro providers

### Point-in-time and evidence upgrades

The current implementation already wires:

- market snapshots with provenance and reliability
- fundamentals payloads enriched with SEC filings and XBRL facts
- macro payloads with release timing and vintage-aware fields
- news payloads with event metadata
- evidence sections in reports

## Evolution Layer

QuanterSwarm does not treat evolution as “change one threshold and call it learning”.

It separates:

- ephemeral inference
- persistent parameter state
- event memory
- weak priors
- promotion gates
- audit logging

### Current evolution components

- `LeaderRegistry`
- `EventMemoryStore`
- `PromotionGate`
- `EvolutionAuditLog`
- `EvolutionManager`

### Current evolution behavior

- leader parameters are externalized
- similar historical events can add a weak prior
- ranking uses posterior score:

```text
posterior = base + prior - risk - cost
```

- evolution proposals are logged
- manual review remains the safe default

## Project Highlights

### 1. Architecture is the product

The primary innovation is not “AI for trading”. It is a multi-agent architecture that turns routing, evidence, replayability, and bounded evolution into explicit system components.

### 2. Routed swarm, not agent spam

The router decides which specialists and leaders should be active for the current regime and budget.

### 3. Data discipline before intelligence theater

Snapshots carry timestamps, provenance, quality flags, and reliability scores. The system is being shaped toward point-in-time correctness instead of retrospective convenience.

### 4. Ephemeral leaders, persistent learning

Leaders remain lightweight. Persistent learning lives in the registry, event memory, and audit trail.

### 5. OpenClaw skill-ready by design

The repository structure, shared prompts, schemas, scripts, and `skill/quanter-swarm/` package layout make this system directly suitable for OpenClaw integration.

### 6. Batch-ready research

The system can run:

- single-symbol research cycles
- batch research cycles
- batch snapshot assembly
- batch fundamentals queries
- batch macro queries

### 7. Report-first outputs

Every cycle is designed to produce something reviewable:

- strategy scores
- routing trace
- risk status
- portfolio suggestion
- execution assumptions
- evidence summary
- provider topology

## Repository Layout

```text
.
├── configs/                  # Runtime configs and policies
├── data/                     # Reports, paper trades, experiments, backtests
├── docs/                     # Architecture and design notes
├── examples/                 # Sample payloads
├── experiments/              # Experiment presets
├── scripts/                  # Local runners and utilities
├── shared/                   # Schemas, templates, prompts, constants
├── skill/quanter-swarm/      # OpenClaw skill packaging assets
├── src/quanter_swarm/
│   ├── adapters/             # API and external adapters
│   ├── agents/               # Orchestrator -> Router -> Leaders -> Specialists
│   ├── application/          # Shared use-case entrypoints
│   ├── core/                 # Runtime config, ids, logging, storage primitives
│   ├── services/             # Snapshot, ranking, risk, execution, reporting, evolution, etc.
│   ├── backtest/             # Replay/event engine kept separate for now
│   ├── config/
│   ├── llm/
│   ├── tools/
│   └── validation/
└── tests/
```

The package root is now fully unified under `quanter_swarm.*`.

- `quanter_swarm.adapters`
  - API, CLI, dashboard, and external integration entrypoints
- `quanter_swarm.application`
  - task-oriented use cases shared by adapters
- `quanter_swarm.agents`
  - orchestrator, router, leaders, and specialists
- `quanter_swarm.services`
  - non-agent system capabilities such as ranking, risk, execution, reporting, and monitoring
- `quanter_swarm.core`
  - contracts, errors, runtime config, ids, tracing, and storage helpers

## Public API and Import Style

For new code, prefer package-level imports over deep module paths whenever you are crossing layers.

Recommended examples:

```python
from quanter_swarm import RunResearchCycle
from quanter_swarm.core import AgentContext, CycleReport, load_settings
from quanter_swarm.services import generate_report, rank_candidates
from quanter_swarm.agents.orchestrator import RootAgent, RuntimeContext
from quanter_swarm.agents.leaders import MomentumLeader
from quanter_swarm.agents.specialists import DataFetchSpecialist
from quanter_swarm.adapters import api_app
```

Practical rule of thumb:

- use `quanter_swarm` or `quanter_swarm.application` for app-facing use cases
- use `quanter_swarm.core` for contracts, exceptions, config, ids, tracing, and storage
- use `quanter_swarm.services` for system capabilities
- use `quanter_swarm.agents.*` package exports for public agent classes
- use direct submodule imports only for implementation details inside the same subsystem

## Quick Start

### 1. Install

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e ".[dev]"
```

### 2. Configure

```bash
cp .env.example .env
```

Default operation is paper-only, deterministic, and centered on the internal simulation source.

### 3. Run quality checks

```bash
make lint
make test
make typecheck
make validate
```

### 4. Run a local cycle

```bash
PYTHONPATH=src .venv/bin/python scripts/run_local_cycle.py
```

### 5. Run the API

```bash
make api
```

### 6. Sanity-check the package surface

```bash
ruff check .
pytest
```

## Daily Workflows

The repo now exposes a task-oriented command surface that matches the internal simulation-first workflow described in `codex.md`.

### Research and signals

```bash
python -m quanter_swarm.adapters.cli.generate_signals --source internal_sim --date 2025-06-01
```

or, after `pip install -e ".[dev]"`:

```bash
generate_signals --source internal_sim --date 2025-06-01
```

### Backtests

```bash
python -m quanter_swarm.adapters.cli.run_backtest --source internal_sim --config configs/backtest/default.yaml
```

or:

```bash
run_backtest --source internal_sim --config configs/backtest/default.yaml
```

### Replay

```bash
python -m quanter_swarm.adapters.cli.run_replay --run-id <RUN_ID>
```

or:

```bash
run_replay --run-id <RUN_ID>
```

### Build dashboard data

```bash
python -m quanter_swarm.adapters.cli.build_dashboard_data --source internal_sim --with-alpaca-readonly
```

or:

```bash
build_dashboard_data --source internal_sim --with-alpaca-readonly
```

### Serve dashboard

```bash
python -m quanter_swarm.adapters.cli.serve_dashboard
```

or:

```bash
serve_dashboard
```

### Output conventions

- Research, signal, backtest, replay, and dashboard artifacts are written under `DATA_DIR`, which defaults to `data/`.
- Tests override `DATA_DIR` automatically so routine test runs do not pollute repository artifacts.
- `internal_sim` is the default and only supported source for research, backtest, and replay flows.
- Alpaca is dashboard-only and explicitly marked `external / read-only`.

## OpenClaw Skill Packaging

QuanterSwarm is structured so the architecture can be exported into OpenClaw with minimal translation.

The packaging layer lives in [skill/quanter-swarm/](skill/quanter-swarm/), including:

- `agents/openai.yaml`
- `references/`
- `scripts/`
- `assets/`

This matters because the system is intended to preserve the same architectural identity across two modes:

- repository mode
  - local development, testing, experiments, API, backtests
- skill mode
  - packaged capability with stable prompts, policies, schemas, and operating rules

In other words, the skill is not an afterthought wrapper. It is another deployment target for the same architecture.

## Provider Configuration

Provider wiring now supports both config-based and request-level selection.

### Default app config

See [configs/app.yaml](configs/app.yaml).

The default is:

```yaml
app:
  data_provider:
    provider: deterministic
```

### Composite provider example

```yaml
app:
  data_provider:
    provider: composite
    market_provider: polygon_market_data
    market_provider_kwargs:
      api_key: ${POLYGON_API_KEY}
    auxiliary_providers:
      filings:
        enabled: true
        provider: sec_filings
        provider_kwargs:
          user_agent: "QuanterSwarm research@example.com"
      xbrl:
        enabled: true
        provider: sec_xbrl_facts
        provider_kwargs:
          user_agent: "QuanterSwarm research@example.com"
      shares_float:
        enabled: true
        provider: fmp_shares_float
        provider_kwargs:
          api_key: ${FMP_API_KEY}
      macro:
        enabled: true
        provider: fred_macro
        provider_kwargs:
          api_key: ${FRED_API_KEY}
      macro_vintages:
        enabled: true
        provider: alfred_vintage_macro
        provider_kwargs:
          api_key: ${FRED_API_KEY}
```

### Environment variables

See [.env.example](.env.example) for:

- `POLYGON_API_KEY`
- `FMP_API_KEY`
- `FRED_API_KEY`
- `SEC_USER_AGENT`
- optional `QUANTER_DATA_PROVIDER`

## API

If you need the ASGI app in code, prefer:

```python
from quanter_swarm.adapters import api_app
```

instead of importing the `app.py` submodule directly.

### Research

`POST /research`

Run one research cycle.

Request fields include:

- `symbol`
- `symbols`
- `horizon`
- `portfolio_mode`
- `risk_tolerance`
- `output_format`
- `data_freshness_preference`
- `data_provider`

### Batch research

`POST /research/batch`

Run multiple research cycles with batch-prefetched snapshots.

### Batch data interfaces

`POST /data/fundamentals/batch`

`POST /data/macro/batch`

### Provider discovery

`GET /data/providers`

Returns:

- currently available provider names
- configured provider topology
- the active architecture-level provider shape exposed to the runtime

## Reporting

Cycle reports include:

- `active_regime`
- `regime_confidence`
- `active_strategy_teams`
- `factor_scorecard`
- `risk_alerts`
- `portfolio_suggestion`
- `paper_trade_actions`
- `evaluation_summary`
- `decision_trace_summary`
- `evidence_summary`
- `provider_summary`
- `config_provenance`

Markdown reports also expose:

- evidence section
- evolution evidence
- provider topology

## Backtest and Replay

Backtest, replay, and dashboard aggregation are exposed through the task-oriented CLI layer:

- `python -m quanter_swarm.adapters.cli.run_backtest`
- `python -m quanter_swarm.adapters.cli.run_replay`
- `python -m quanter_swarm.adapters.cli.build_dashboard_data`
- `python -m quanter_swarm.adapters.cli.serve_dashboard`

Script wrappers also exist under `scripts/` for local development:

- `scripts/run_backtest.py`
- `scripts/run_replay.py`
- `scripts/build_dashboard_data.py`
- `scripts/serve_dashboard.py`

Replay and backtest artifacts now carry the operational metadata needed for reconstruction and review, including:

- `run_id`
- `dataset_version`
- `config_hash`
- `router_version`
- `ranking_version`
- `risk_version`
- portfolio plan and mock execution summary
- evidence-linked report payloads

## Compatibility Notice

`quanter_swarm.*` is the canonical package root.

The historical `app.*` namespace has been retired.
Repository-owned code, tests, docs, and packaging entrypoints now use `quanter_swarm.*`.

If you still import `app.*`, migrate to the corresponding `quanter_swarm.*` path.
See [docs/compatibility-layer-retirement.md](docs/compatibility-layer-retirement.md).

## Experiments

Experiment presets live under [experiments/](experiments/).

Run examples:

```bash
python scripts/run_ablation.py router_ablation AAPL
python scripts/run_ablation.py specialist_ablation MSFT
python scripts/run_ablation.py allocation_ablation NVDA
```

## Tests

The repo includes:

- unit tests
- schema tests
- API tests
- routing tests
- backtest tests
- golden and e2e regression tests

Run:

```bash
make test
```

or

```bash
.venv/bin/python -m pytest
```

Tests automatically redirect runtime outputs to a temporary `DATA_DIR`, so running them does not mutate the repository's tracked `data/` artifacts.

## Safety Boundaries

QuanterSwarm is intentionally conservative.

- Paper trading is the default mode.
- Live execution is not the default operating path.
- Risk guardrails run before portfolio and execution outputs matter.
- Event-sensitive conditions should degrade exposure or return no-trade.
- This repository is for research infrastructure and simulation, not investment advice.

## Current Status

This repository already contains the bones of a serious system:

- routed orchestration
- specialist pool
- ephemeral leaders
- posterior ranking
- bounded evolution
- point-in-time snapshot metadata
- provider abstraction
- batch research
- structured reports
- replay events
- experiment runners

The next frontier is deeper integration quality:

- stronger live provider wiring
- richer point-in-time market storage
- stricter vintage-aware backtesting
- better promotion and rollback evidence
- richer monitoring dashboards

But the architectural foundation is already the point:

- routed multi-agent coordination
- persistent meta-learning outside ephemeral leaders
- point-in-time data contracts
- OpenClaw-ready packaging
- reportable and replayable outputs

## Documentation Map

See:

- [docs/architecture.md](docs/architecture.md)
- [docs/agent-graph.md](docs/agent-graph.md)
- [docs/routing-rules.md](docs/routing-rules.md)
- [docs/regime-policy.md](docs/regime-policy.md)
- [docs/risk-policy.md](docs/risk-policy.md)
- [docs/portfolio-policy.md](docs/portfolio-policy.md)
- [docs/paper-trading-policy.md](docs/paper-trading-policy.md)
- [docs/evolution-policy.md](docs/evolution-policy.md)
- [docs/monitoring.md](docs/monitoring.md)
- [docs/status-matrix.md](docs/status-matrix.md)
- [docs/example-cycle-output.md](docs/example-cycle-output.md)
- [docs/codex-acceptance-checklist.md](docs/codex-acceptance-checklist.md)
- [docs/compatibility-layer-retirement.md](docs/compatibility-layer-retirement.md)

For package-surface and acceptance-state tracking, start with:

- [docs/codex-acceptance-checklist.md](docs/codex-acceptance-checklist.md)
- [docs/compatibility-layer-retirement.md](docs/compatibility-layer-retirement.md)

## Final Note

QuanterSwarm is not trying to look more intelligent by adding more agents.

Its edge comes from architecture:

- disciplined routing
- bounded specialization
- reproducible evidence
- conservative execution
- explicit evolution
- portable skill packaging

That is the right foundation for a system that wants to become credible over time.
