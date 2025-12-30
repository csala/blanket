PROJECT_NAME = blanken

.PHONY: help  ## Show this help
help:  ## Show this help
	@# echo $(MAKEFILE_LIST)
	@# grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
	@sed -n 's/^.PHONY: \+\([^ ]\+\)[ ]\+##[ ]\+\(.*\)\|^\(##.*\)/\1\3 => \2/p' $(MAKEFILE_LIST) | awk 'BEGIN {FS = " => "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

## =============================================================================
## Native installation and execution
## =============================================================================

.PHONY: install  ## Install as a package
install:
	pip install .

.PHONY: install-test  ## Install as a package with test dependencies
install-test:
	pip install . --group test

.PHONY: install-develop  ## Install in editable mode, with development and test dependencies
install-develop:
	pip install -e . --group test --group develop

.PHONY: clean  ## Remove build artifacts and cache files
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
	rm -rf build
	rm -rf dist

## =============================================================================
## Code quality and tests
## =============================================================================

.PHONY: ruff  ## Run Ruff linter
ruff:
	ruff check .

.PHONY: ruff-fix  ## Run Ruff linter with --fix flag
ruff-fix:
	ruff check --fix .

.PHONY: ruff-format  ## Run Ruff formatter
ruff-format:
	ruff format .

.PHONY: lint  ## Run all linters and formatters
lint: ruff ruff-format

.PHONY: test  ## Run tests
test:
	pytest --cov=$(PROJECT_NAME) -s

.PHONY: coverage  ## check code coverage
coverage:
	coverage run --source $(PROJECT_NAME) -m pytest
	coverage report -m
	coverage html
	x-www-browser htmlcov/index.html

.PHONY: build  ## Build source and wheel distributions
build:
	$(MAKE) clean
	python -m build

.PHONY: release  ## Upload a release to PyPI
release:
	$(MAKE) build
	twine upload dist/*

.PHONY: test-release  ## Upload a release to TestPyPI
test-release:
	$(MAKE) build
	twine upload --repository testpypi dist/*
