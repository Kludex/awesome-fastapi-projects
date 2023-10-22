 # we want bash behaviour in all shell invocations
SHELL := bash
# Run each target in a separate shell
.ONESHELL:
 # Fail on error inside any functions or subshells
.SHELLFLAGS := -eu -o pipefail -c
 # Remove partially created files on error
.DELETE_ON_ERROR:
 # Warn when an undefined variable is referenced
MAKEFLAGS += --warn-undefined-variables
# Disable built-in rules
MAKEFLAGS += --no-builtin-rules
# A catalog of requirements files
REQUIREMENTS?=requirements

help: # Show this help
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@echo "  help               Show this help"
	@echo "  requirements-base  Compile base requirements"
	@echo "  requirements-test  Compile test requirements"
	@echo "  requirements-dev   Compile dev requirements"
	@echo "  requirements       Compile all requirements"
	@echo "  install            Install the app locally"
	@echo "  install-front      Install frontend"
	@echo "  install-test       Install the app locally with test dependencies"
	@echo "  install-dev        Install the app locally with dev dependencies"
	@echo "  install-test-dev   Install the app locally with test and dev dependencies"
	@echo "  init-test-dev      Install the app locally with test and dev dependencies. Also install pre-commit hooks."
	@echo "  reinit-test-dev    Reinstall pre-commit hooks"
	@echo "  lint               Run linters"
	@echo "  test               Run tests"
	@echo "  migrate            Run migrations"
	@echo "  revision           Create a new migration"
	@echo "  front              Run frontend"
	@echo "  scrape-repos       Scrape repos"
	@echo "  parse-dependencies Scrape dependencies"
	@echo "  index-repos        Index repos"
	@echo "  index-dependencies Index dependencies"

requirements-base: # Compile base requirements
	python -m piptools compile \
	--output-file=requirements/base.txt \
	-v \
	pyproject.toml

requirements-test: requirements-base # Compile test requirements
	python -m piptools compile \
	--extra=test \
	--output-file=requirements/test.txt \
	-v \
	pyproject.toml

requirements-dev: requirements-base # Compile dev requirements
	python -m piptools compile \
	--extra=dev \
	--output-file=requirements/dev.txt \
	-v \
	pyproject.toml

requirements: requirements-base requirements-test requirements-dev  # Compile all requirements
.PHONY: requirements

install:  # Install the app locally
	python -m pip install -r $(REQUIREMENTS)/base.txt .
.PHONY: install

install-test: # Install the app locally with test dependencies
	python -m pip install \
		-r $(REQUIREMENTS)/base.txt \
		-r $(REQUIREMENTS)/test.txt \
		--editable .
.PHONY: install-test

install-dev: # Install the app locally with dev dependencies
	python -m pip install \
		-r $(REQUIREMENTS)/base.txt \
		-r $(REQUIREMENTS)/dev.txt \
		--editable .
.PHONY: install-dev

install-test-dev: # Install the app locally with test and dev dependencies
	python -m pip install \
		-r $(REQUIREMENTS)/base.txt \
		-r $(REQUIREMENTS)/test.txt \
		-r $(REQUIREMENTS)/dev.txt \
		--editable .
.PHONY: install-test-dev

install-front: # Install frontend
	cd frontend && pnpm install
.PHONY: install-front

init-test-dev: install-test-dev # Install the app locally with test and dev dependencies. Also install pre-commit hooks.
	pre-commit install
.PHONY: init-test-dev

reinit-test-dev: init-test-dev # Reinstall pre-commit hooks
	pre-commit install --install-hooks --overwrite
.PHONY: reinit-test-dev

lint: # Run linters
	pre-commit run --all-files
.PHONY: lint

test: # Run tests
	python -m pytest -vv -s --cov=app --cov-report=xml --cov-branch app
.PHONY: test

migrate: # Run migrations
	python -m alembic upgrade heads
.PHONY: migrate

revision: # Create a new migration
	python -m alembic revision --autogenerate -m "$(message)"
.PHONY: revision

front: install-front # Run frontend
	cd frontend && pnpm dev
.PHONY: front

scrape-repos: # Scrape repos
	python -m app.scrape scrape-repos
.PHONY: scrape-repos

parse-dependencies: # Scrape dependencies
	python -m app.scrape parse-dependencies
.PHONY: parse-dependencies

index-repos: # Index repos
	python -m app.index index-repos
.PHONY: index-repos

index-dependencies: # Index dependencies
	python -m app.index index-dependencies
.PHONY: index-dependencies

.DEFAULT_GOAL := init-test-dev # Set the default goal to init-dev-test
