.PHONY: install lint format test run-api dev clean help run-mock run-all

PYTHON := python3
PIP := $(PYTHON) -m pip
PYTEST := $(PYTHON) -m pytest
RUFF := $(PYTHON) -m ruff
BLACK := $(PYTHON) -m black
HYPERCORN := $(PYTHON) -m hypercorn

help:
	@echo "Available targets:"
	@echo "  install     - Install all dependencies including dev dependencies"
	@echo "  lint        - Run ruff linter"
	@echo "  format      - Format code with black and ruff"
	@echo "  test        - Run tests with pytest"
	@echo "  test-cov    - Run tests with coverage report"
	@echo "  run-api     - Start Quart server in production mode"
	@echo "  dev         - Start Quart server in development mode with auto-reload"
	@echo "  run-mock    - Start Mock Foundry Agent server on port 8001"
	@echo "  run-all     - Start both Mock Foundry Agent and Orchestrator API"
	@echo "  clean       - Remove Python cache files and build artifacts"
	@echo "  pre-commit  - Install pre-commit hooks"

install:
	$(PIP) install --upgrade pip
	$(PIP) install -e ".[dev]" --pre

lint:
	$(RUFF) check app tests

format:
	$(BLACK) app tests
	$(RUFF) check --fix app tests

test:
	$(PYTEST) tests/

test-cov:
	$(PYTEST) --cov=app --cov-report=html --cov-report=term tests/

run-api:
	$(HYPERCORN) app.main:app --bind 0.0.0.0:8000

dev:
	$(HYPERCORN) app.main:app --bind 0.0.0.0:8000 --reload

pre-commit:
	pre-commit install

run-mock:
	@echo "============================================================"
	@echo "Starting Mock Foundry Agent on port 8001..."
	@echo "============================================================"
	$(PYTHON) mock_foundry_agent.py

run-all:
	@echo "============================================================"
	@echo "Starting Mock Foundry Agent and Orchestrator API..."
	@echo "============================================================"
	@echo "Mock will run on port 8001, Orchestrator on port 8000"
	@echo "Press Ctrl+C to stop both services"
	@echo "============================================================"
	@$(PYTHON) mock_foundry_agent.py & sleep 3 && $(HYPERCORN) app.main:app --bind 0.0.0.0:8000

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf build dist htmlcov .coverage
