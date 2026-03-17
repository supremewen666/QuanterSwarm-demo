PYTHON ?= .venv/bin/python
PYTHONPATH ?= src
MYPY_TARGETS = src/quanter_swarm/orchestrator src/quanter_swarm/decision src/quanter_swarm/execution src/quanter_swarm/api src/quanter_swarm/contracts.py

.PHONY: api lint run test typecheck validate

run:
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m quanter_swarm.main

api:
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m uvicorn quanter_swarm.api.app:app --reload

lint:
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m ruff check src tests

test:
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m pytest

typecheck:
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m mypy $(MYPY_TARGETS)

validate:
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) scripts/validate_configs.py
