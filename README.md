# QuanterSwarm

An architecture-first multi-agent equity research and paper-trading system.

QuanterSwarm routes market context into a bounded swarm of specialists and strategy leaders, builds point-in-time snapshots, scores ideas with weak priors, applies risk guardrails, and produces structured research reports and paper-trade actions.

It is designed to feel like a compact quant research platform, not a prompt demo.

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
- It stays paper-trading only by default.

The result is a system that is easier to reason about, easier to test, and much closer to research infrastructure than to a generic agent sandbox.

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
External Data
  -> Snapshot Builder
  -> Regime Detection
  -> Specialist Research
  -> Leader Proposal
  -> Posterior Ranking
  -> Risk Guardrails
  -> Portfolio Construction
  -> Paper Execution
  -> Reporting / Replay / Monitoring
```

### Core runtime graph

```text
RootAgent
  -> CycleManager
     -> DataFetchSpecialist
     -> RegimeAgent
     -> RouterAgent
     -> Shared Specialists
     -> Ephemeral Leaders
     -> RankingEngine
     -> EvolutionManager
     -> Risk Engine
     -> Portfolio Builder
     -> Paper Executor
     -> Report Generator
```

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

### 1. Routed swarm, not agent spam

The router decides which specialists and leaders should be active for the current regime and budget.

### 2. Data discipline before intelligence theater

Snapshots carry timestamps, provenance, quality flags, and reliability scores. The system is being shaped toward point-in-time correctness instead of retrospective convenience.

### 3. Ephemeral leaders, persistent learning

Leaders remain lightweight. Persistent learning lives in the registry, event memory, and audit trail.

### 4. Batch-ready research

The system can run:

- single-symbol research cycles
- batch research cycles
- batch snapshot assembly
- batch fundamentals queries
- batch macro queries

### 5. Report-first outputs

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
├── skill/quanter-swarm/      # Skill packaging assets
├── src/quanter_swarm/
│   ├── agents/
│   ├── api/
│   ├── backtest/
│   ├── data/
│   ├── decision/
│   ├── evaluation/
│   ├── evolution/
│   ├── execution/
│   ├── leaders/
│   ├── market/
│   ├── orchestrator/
│   ├── reporting/
│   ├── research/
│   ├── risk/
│   └── router/
└── tests/
```

## Quick Start

### 1. Install

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure

```bash
cp .env.example .env
```

Default config is paper-only and deterministic.

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

Walk-forward and replay tools live in:

- `scripts/run_backtest.py`
- `src/quanter_swarm/backtest/`

Replay artifacts can now include:

- market summary
- evidence summary
- signal events
- portfolio updates
- order and fill events

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

## Final Note

QuanterSwarm is not trying to look more intelligent by adding more agents.

Its edge comes from architecture:

- disciplined routing
- bounded specialization
- reproducible evidence
- conservative execution
- explicit evolution

That is the right foundation for a system that wants to become credible over time.
