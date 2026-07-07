.PHONY: help up down seed demo test logs venv reset

VENV := .venv
PY   := $(VENV)/bin/python
PIP  := $(VENV)/bin/pip

help:
	@echo "make up     - start local SQL Server (Fabric mock)"
	@echo "make seed   - create DB + schema + sample data"
	@echo "make venv   - create Python venv and install the connector deps"
	@echo "make demo   - run the end-to-end connector demo"
	@echo "make test   - run pytest against the local mock"
	@echo "make logs   - tail SQL Server container logs"
	@echo "make down   - stop container (keeps data volume)"
	@echo "make reset  - stop container AND delete data volume"

up:
	docker compose up -d

seed:
	./scripts/init-db.sh

venv:
	python3 -m venv $(VENV)
	$(PIP) install -q -r connector/requirements.txt

demo: venv
	$(PY) connector/examples/demo.py

test: venv
	$(VENV)/bin/pytest -q connector/tests

logs:
	docker compose logs -f fabric-sql

down:
	docker compose down

reset:
	docker compose down -v
