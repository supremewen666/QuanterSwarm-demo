# QuanterSwarm Demo — Codex Implementation TODO

## Purpose

This document provides **actionable, file-level implementation tasks**  
to upgrade the system from prototype → production-grade architecture.

Each item is:
- scoped to files
- includes expected classes / functions
- designed for Codex execution

---

# P0 — CORE RUNTIME (MANDATORY)

---

## 1. Implement Real LLM Runtime

### Modify
```

src/quanter_swarm/llm/client.py

````

### Replace with:

```python
class LLMClient:
    def generate(self, messages, *, model=None, tools=None) -> dict:
        ...
````

### Add new files:

```
src/quanter_swarm/llm/
├── base.py
├── router.py
├── messages.py
├── exceptions.py
├── providers/
│   ├── openai_provider.py
│   ├── anthropic_provider.py
│   └── mock_provider.py
```

### Requirements

#### base.py

```python
class BaseLLMProvider(ABC):
    def generate(self, messages, tools=None, **kwargs) -> dict:
        ...
```

#### router.py

```python
class LLMRouter:
    def route(self, task_type: str) -> BaseLLMProvider:
        ...
```

#### messages.py

* normalize message format
* enforce schema

#### structured_output.py (UPDATE EXISTING)

* enforce Pydantic validation
* raise on invalid output

---

## 2. Implement Tool System

### Create directory:

```
src/quanter_swarm/tools/
```

### Add files:

```
base.py
registry.py
executor.py
schemas.py
```

---

### base.py

```python
class Tool(ABC):
    name: str

    def run(self, **kwargs) -> dict:
        ...
```

---

### registry.py

```python
class ToolRegistry:
    def register(self, tool: Tool):
        ...
    def get(self, name: str) -> Tool:
        ...
```

---

### executor.py

```python
class ToolExecutor:
    def execute(self, tool_name: str, params: dict) -> dict:
        ...
```

Must support:

* timeout
* retries
* logging
* error capture

---

## 3. Refactor Specialists (CRITICAL)

### Modify ALL files in:

```
src/quanter_swarm/specialists/
```

---

### Rule:

❌ REMOVE:

* direct data provider calls
* direct business logic

✅ REPLACE WITH:

* tool calls only

---

### Example Refactor

Before:

```python
data = provider.get_data(...)
```

After:

```python
data = tool_executor.execute("market_data", {...})
```

---

### Each Specialist MUST:

* receive `tool_executor`
* return structured output only

---

## 4. Introduce Runtime Layer

### Create:

```
src/quanter_swarm/orchestrator/runtime.py
```

---

### Implement:

```python
class RuntimeContext:
    def __init__(self, llm_client, tool_executor, settings):
        self.llm = llm_client
        self.tools = tool_executor
        self.settings = settings
```

---

### Modify:

```
orchestrator/root_agent.py
cycle_manager.py
```

---

### Inject runtime:

```python
RootAgent(runtime=RuntimeContext(...))
```

---

## 5. Add Failure Semantics

### Modify:

```
src/quanter_swarm/contracts.py
```

---

### Add:

```python
class Status(str, Enum):
    OK = "ok"
    DEGRADED = "degraded"
    NO_TRADE = "no_trade"
    ERROR = "error"
```

---

### Update ALL outputs to include:

```python
status: Status
reason: str
fallback_flags: list[str]
confidence: float
```

---

# P1 — DATA + BACKTEST VALIDITY

---

## 6. Add PIT Validation Layer

### Create:

```
src/quanter_swarm/validation/
```

---

### Files:

```
pit_validator.py
data_integrity.py
```

---

### pit_validator.py

```python
class PITValidator:
    def validate(snapshot) -> None:
        ...
```

Must check:

* no future data
* valid timestamps
* correct vintage usage

---

## 7. Strengthen Backtest Engine

### Modify:

```
src/quanter_swarm/backtest/
```

---

### Add:

```
validator.py
cost_model.py
execution_simulator.py
```

---

### validator.py

```python
class BacktestValidator:
    def validate_run(run_config):
        ...
```

---

### cost_model.py

* slippage
* transaction cost
* spread model

---

## 8. Execution System Upgrade

### Create:

```
src/quanter_swarm/execution/
```

---

### Files:

```
order_manager.py
broker_interface.py
fill_simulator.py
tca.py
```

---

### order_manager.py

```python
class OrderManager:
    def submit(order):
        ...
```

---

### fill_simulator.py

* partial fills
* delay
* slippage

---

# P2 — GOVERNANCE + MONITORING

---

## 9. Evolution Governance

### Modify:

```
src/quanter_swarm/evolution/
```

---

### Add:

* promotion thresholds
* rollback conditions
* statistical filters

---

## 10. Monitoring Layer

### Create:

```
src/quanter_swarm/monitoring/
```

---

### Files:

```
metrics.py
tracing.py
logger.py
```

---

### metrics.py

Track:

* latency
* token usage
* routing decisions
* risk triggers

---

# P3 — SKILL HARDENING

---

## 11. Skill Interface Upgrade

### Modify:

```
src/quanter_swarm/skill_interface.py
```

---

### Add support:

* tool policies
* llm provider override
* strict output schema

---

### Enforce:

```python
def run_skill(request: ResearchRequestContract) -> CycleReport:
```

---

## 12. Config System Expansion

### Modify:

```
src/quanter_swarm/config/settings.py
```

---

### Add:

```python
llm_provider: str
llm_model: str
llm_temperature: float

tool_timeout: int
tool_budget: int
allowed_tools: list[str]
```

---

# FINAL CHECKLIST

---

## MUST PASS BEFORE MERGE

* [ ] No direct provider calls inside specialists
* [ ] All LLM calls go through LLMClient
* [ ] All tools go through ToolExecutor
* [ ] All outputs include status field
* [ ] PIT validation enforced in backtest + runtime
* [ ] RuntimeContext injected everywhere

---

# END STATE GOAL

System must satisfy:

> Deterministic
> Auditable
> PIT-correct
> Tool-driven
> LLM-provider agnostic
> Backtest-valid
> Skill-consistent

---

# FINAL PRINCIPLE

> Do not optimize for architecture completeness.
> Optimize for **research validity and reproducibility**.
---
#遵循以下原则
#「请以第一性原理！从原始需求和问题本质出发，不从惯例或模板出发。
#1. 不要假设我清楚自己想要什么。动机或目标不清晰时，停下来讨论。
#2. 目标清晰但路径不是最短的，直接告诉我并建议更好的办法。
#3. 遇到问题追根因，不打补丁。每个决策都要能回答"为什么"。
#4. 输出说重点，砍掉一切不改变决策的信息。」