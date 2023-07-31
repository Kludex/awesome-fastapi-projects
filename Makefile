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

init-test-dev: install-test-dev # Install the app locally with test and dev dependencies. Also install pre-commit hooks.
	pre-commit install
	pre-commit install --hook-type commit-msg
.PHONY: init-test-dev


.DEFAULT_GOAL := init-test-dev # Set the default goal to init-dev-test
