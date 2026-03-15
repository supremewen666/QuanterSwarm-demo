PYTHONPATH=src

.PHONY: run api test validate

run:
	PYTHONPATH=$(PYTHONPATH) python3 -m quanter_swarm.main

api:
	PYTHONPATH=$(PYTHONPATH) uvicorn quanter_swarm.api.app:app --reload

test:
	PYTHONPATH=$(PYTHONPATH) pytest

validate:
	PYTHONPATH=$(PYTHONPATH) python3 scripts/validate_configs.py
