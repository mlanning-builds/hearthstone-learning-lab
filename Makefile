# Use the checkout root even when invoked with make -f /path/to/Makefile.
ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))
PYTHON ?= python3
VENV ?= $(ROOT)/.venv
ifeq ($(OS),Windows_NT)
VENV_PYTHON := $(VENV)/Scripts/python.exe
else
VENV_PYTHON := $(VENV)/bin/python
endif
WORKERS ?= 4
SEEDS ?= 1
MAX_ACTIONS ?= 500
.DEFAULT_GOAL := help
.PHONY: help venv install install-core test test-candidate check sim notebook scope benchmark install-dev smoke lint typecheck quality

help:
	@echo "install          Create .venv and install the project with JupyterLab"
	@echo "install-neural   Install optional PyTorch and notebook dependencies"
	@echo "neural-preflight Validate neural architecture and fixed decks; no games or training"
	@echo "test-neural      Non-training neural fixtures; no optimizer steps"
	@echo "notebook-neural  Open notebook 15; no cells are executed"
	@echo "install-core     Install the simulator without JupyterLab"
	@echo "test             Run non-training project-tool checks"
	@echo "test-candidate   Run full non-training candidate checks (WORKERS=4)"
	@echo "check            Check candidate inventory consistency"
	@echo "sim              Bounded random-play validation; no learning (SEEDS=1 MAX_ACTIONS=500)"
	@echo "notebook         Open JupyterLab; no notebook cells are executed"
	@echo "scope            Preflight supplied DECKS JSON or the benchmark fixture"
	@echo "benchmark        Time bounded random legal play (GAMES=3 MAX_ACTIONS=500)"
	@echo "install-dev      Install staged lint/type tooling"
	@echo "smoke            Fast bounded rule sanity check; no learning"
	@echo "quality          Staged lint and strict typing for public API"
	@echo "Variables: PYTHON, VENV, WORKERS, SEEDS, MAX_ACTIONS"

venv:
	@test -f "$(VENV_PYTHON)" || "$(PYTHON)" -m venv "$(VENV)"

install: venv
	"$(VENV_PYTHON)" -m pip install --upgrade "pip>=23"
	cd "$(ROOT)" && "$(VENV_PYTHON)" -m pip install -e '.[notebook]'

install-core: venv
	"$(VENV_PYTHON)" -m pip install --upgrade "pip>=23"
	cd "$(ROOT)" && "$(VENV_PYTHON)" -m pip install -e .

test:
	cd "$(ROOT)" && "$(VENV_PYTHON)" tools/check_without_training.py --suite supporting

test-candidate:
	cd "$(ROOT)/staging/rebased-88" && "$(VENV_PYTHON)" "$(ROOT)/tools/check_without_training.py" --suite candidate --workers "$(WORKERS)"

check:
	cd "$(ROOT)" && "$(VENV_PYTHON)" tools/sync_candidate_inventory.py --engine-root staging/rebased-88

sim:
	cd "$(ROOT)" && "$(VENV_PYTHON)" tools/stress_candidate.py --engine-root staging/rebased-88 --seeds "$(SEEDS)" --max-actions "$(MAX_ACTIONS)"

notebook:
	cd "$(ROOT)" && "$(VENV_PYTHON)" -m jupyterlab notebooks/09_candidate_random_validation.ipynb

GAMES ?= 3
DECKS ?=
scope:
	cd "$(ROOT)" && "$(VENV_PYTHON)" tools/simulator_workflow.py scope $(if $(DECKS),--decks "$(DECKS)",)

benchmark:
	cd "$(ROOT)" && "$(VENV_PYTHON)" tools/simulator_workflow.py benchmark --games "$(GAMES)" --max-actions "$(MAX_ACTIONS)" --output staging/rebased-88/runs/benchmarks/speed.json $(if $(DECKS),--decks "$(DECKS)",)

install-dev: venv
	"$(VENV_PYTHON)" -m pip install --upgrade "pip>=23"
	cd "$(ROOT)" && "$(VENV_PYTHON)" -m pip install -e '.[dev]'

smoke:
	cd "$(ROOT)" && "$(VENV_PYTHON)" tools/smoke_simulator.py

lint:
	cd "$(ROOT)" && "$(VENV_PYTHON)" -m ruff check hearthstone_sim tools/smoke_simulator.py

typecheck:
	cd "$(ROOT)" && "$(VENV_PYTHON)" -m mypy --config-file pyproject.toml

quality: lint typecheck

# Neural tooling is opt-in. These targets never launch training.
.PHONY: install-neural neural-preflight test-neural notebook-neural
install-neural: venv
	cd "$(ROOT)" && "$(VENV_PYTHON)" -m pip install -e '.[neural,notebook]'

neural-preflight:
	cd "$(ROOT)" && "$(VENV_PYTHON)" tools/train_neural.py --preflight

test-neural:
	cd "$(ROOT)" && PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=.:tests "$(VENV_PYTHON)" -m unittest test_neural_ppo -v

notebook-neural:
	cd "$(ROOT)" && "$(VENV_PYTHON)" -m jupyterlab notebooks/15_transformer_ppo.ipynb

.PHONY: notebook-long test-neural-monitoring
notebook-long:
	cd "$(ROOT)" && "$(VENV_PYTHON)" -m jupyterlab notebooks/16_long_transformer_training.ipynb

test-neural-monitoring:
	cd "$(ROOT)" && PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=.:tests "$(VENV_PYTHON)" -m unittest test_neural_ppo test_neural_monitoring -v
