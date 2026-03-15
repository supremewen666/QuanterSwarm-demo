# QuanterSwarm

QuanterSwarm is a routed multi-agent stock analysis and paper-trading system with shared specialists, ephemeral strategy leaders, and OpenClaw skill integration.

## Overview

QuanterSwarm is designed for medium-frequency equity research and paper trading.

It combines:

- Root orchestration
- Market regime routing
- Shared specialist pool
- Ephemeral strategy leaders
- Multi-strategy portfolio suggestion
- Risk-aware paper trading
- Structured report generation
- OpenClaw skill packaging

Default mode is research and paper trading only.

## Core Architecture

### External product flow

Input:
- market data
- fundamentals
- news
- macro data

Data layer:
- market-data-fetch
- fundamentals-parser

Research layer:
- news-sentiment-scan
- factor-score-engine
- event-impact-analyzer

Decision layer:
- risk-guardrail
- portfolio-suggestion
- paper-broker

Output layer:
- report-generator

### Internal agent architecture

- RootAgent
- RouterAgent
- MarketRegimeAgent
- Shared Specialist Pool
  - DataFetchSpecialist
  - MemoryCompressionSpecialist
  - RiskSpecialist
  - SentimentSpecialist
  - MacroEventSpecialist
  - FeatureEngineeringSpecialist
- Ephemeral Strategy Leaders
  - MomentumLeader
  - MeanReversionLeader
  - StatArbLeader
  - BreakoutEventLeader
- Research Engines
  - FundamentalsParser
  - FactorScoreEngine
  - EventImpactAnalyzer
- Decision Engines
  - RiskGuardrail
  - PortfolioSuggestion
  - PaperBroker
  - ExecutionGate
- RankingEngine
- EvolutionAgent
- ReportGenerator

## Why this architecture

QuanterSwarm is designed to balance:

- product clarity
- token efficiency
- research quality
- extensibility
- OpenClaw compatibility

Key design choices:

- routed strategy activation instead of always-on execution
- shared specialist pool instead of duplicated sub-agents
- ephemeral leaders instead of persistent leader agents
- memory compression before leader reasoning
- portfolio allocation across strategies instead of winner-take-all
- risk-adjusted ranking instead of raw pnl selection
- bounded evolution instead of unrestricted strategy invention

## Shared Specialist Pool

### DataFetchSpecialist
Fetch and normalize:

- latest or real-time market data
- ohlcv bars
- sector and benchmark data
- raw fundamentals
- news feed inputs
- macro inputs

### MemoryCompressionSpecialist
Compress:

- long news sets
- prior logs
- historical summaries
- large context windows

### RiskSpecialist
Compute:

- exposure limits
- drawdown checks
- volatility-aware scaling
- event risk flags
- cooldown logic

### SentimentSpecialist
Analyze:

- news direction
- uncertainty
- key topics
- sentiment drift

### MacroEventSpecialist
Analyze:

- earnings
- macro releases
- policy events
- short and medium horizon impact

### FeatureEngineeringSpecialist
Compute:

- indicators
- factor features
- correlation matrices
- regime support features

## Strategy Leaders

Only active leaders are created for each cycle.

Supported leaders:

- momentum
- mean reversion
- stat arb
- breakout and event

Leaders are stateless and ephemeral:

- created on demand
- consume compressed context
- emit structured strategy outputs
- destroyed after execution

## Ranking and Evolution

Ranking is based on risk-adjusted metrics rather than raw profit.

Suggested metrics:

- sharpe
- return
- max drawdown
- win rate
- stability
- turnover penalty

Evolution is bounded to approved parameters such as:

- rsi thresholds
- breakout windows
- momentum lookback
- stop thresholds
- allocation weights
- regime thresholds

## Repository Structure

```text
quanter-swarm/
├── docs/
├── configs/
├── data/
├── shared/
├── src/quanter_swarm/
├── scripts/
├── tests/
├── examples/
└── skill/quanter-swarm/
```

The repository is split into six practical layers:

- `docs/` for architecture and operating rules
- `configs/` for runtime behavior and policy defaults
- `data/` for local caches, snapshots, reports, and paper trades
- `shared/` for schemas, prompts, templates, and constants
- `src/quanter_swarm/` for the application package
- `skill/quanter-swarm/` for skill packaging assets

## Documentation Map

Core design and policy documents live under `docs/`:

- `docs/architecture.md`
- `docs/agent-graph.md`
- `docs/routing-rules.md`
- `docs/regime-policy.md`
- `docs/risk-policy.md`
- `docs/portfolio-policy.md`
- `docs/paper-trading-policy.md`
- `docs/evolution-policy.md`
- `docs/token-latency-budget.md`
- `docs/output-format.md`
- `docs/openclaw-integration.md`

## Quick Start

1. Create a virtual environment.
2. Install dependencies.
3. Copy the example environment file.
4. Run the test suite.
5. Run a local analysis cycle.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
PYTHONPATH=src pytest tests -q
PYTHONPATH=src python3 scripts/run_local_cycle.py
```

If you want the API locally, run:

```bash
PYTHONPATH=src uvicorn quanter_swarm.api.app:app --reload
```

## Recommended MVP

Phase 1 should prioritize the shortest end-to-end paper-trading loop:

- `RootAgent`
- `RouterAgent`
- `RegimeAgent`
- `DataFetchSpecialist`
- `MemoryCompressionSpecialist`
- `RiskSpecialist`
- `FeatureEngineeringSpecialist`
- `MomentumLeader`
- `MeanReversionLeader`
- `PortfolioSuggestion`
- `PaperBroker`
- `ReportGenerator`

This gives you one complete path from market input to ranked ideas, guarded allocation, paper execution, and reporting.

## Skill Packaging

The packaged skill lives at `skill/quanter-swarm/`.

Its purpose is to mirror the repo-level orchestration flow for OpenClaw-compatible execution:

- `agents/openai.yaml` defines the skill entrypoint
- `references/` keeps policy and architecture notes close to the packaged skill
- `scripts/` provides analysis, paper-cycle, export, and validation helpers
- `assets/` stores the packaged icon and future visual assets

If you use the local skill packaging workflow, package from the repository root against `skill/quanter-swarm/`.

## Safety Boundaries

The repository is intentionally conservative:

- default mode is research and paper trading
- live trading must stay disabled unless explicitly enabled
- all suggestions must pass risk guardrails before execution
- event-sensitive conditions should prefer reduced exposure or no-trade output
- outputs are research artifacts, not investment advice

## Planned Extensions

Reasonable next steps after the MVP:

- connector-backed live and historical data feeds
- stronger event-driven routing and catalyst awareness
- richer strategy leaderboard and evaluation dashboards
- tighter bounded evolution loops with better rollback logic
- support for more markets beyond the current equity-first scope
