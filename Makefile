
.PHONY: help setup install test docs docs-api build publish test-pypi-install test-conda-install test-install clean clean-install-env

help:
	@echo "Commands:"
	@echo "  setup    : setup development environment"
	@echo "  install  : install package in editable mode"
	@echo "  format   : format code with ruff"
	@echo "  lint     : lint code with ruff"
	@echo "  fix      : auto-fix linting issues with ruff"
	@echo "  typecheck: run type checking with mypy"
	@echo "  test     : run tests with pytest"
	@echo "  check    : run full quality check (format, lint, typecheck, test)"
	@echo "  docs     : build HTML documentation with Sphinx"
	@echo "  docs-api : regenerate API documentation RST files"
	@echo "  build    : build the sdist and wheel"
	@echo "  publish  : publish the package to PyPI"
	@echo "  test-pypi-install: test PyPI wheel installation locally"
	@echo "  test-conda-install: test conda package installation locally"
	@echo "  test-install: test both PyPI and conda installations locally"
	@echo "  clean    : remove temporary files"
	@echo "  clean-install-env: remove the pycalceff-install conda environment"

setup:
	@echo "Creating conda environment..."
	conda env create -f environment-dev.yml
	@echo "NOTE: Please activate the 'pycalceff-dev' conda environment before running 'make install'."

install:
	@echo "Uninstalling existing package installation..."
	pip uninstall -y pycalceff || true
	@echo "Installing package in editable mode with dev dependencies..."
	pip install -e .[dev]

format:
	ruff format src tests

typecheck:
	mypy -p src -p tests

lint:
	ruff check src tests

fix:
	ruff check --fix src tests

check: format lint typecheck test

test:
	pytest --numprocesses auto --cov=pycalceff --cov-branch --cov-report=term-missing --durations 10 tests

docs: docs-api
	@echo "Building HTML documentation..."
	cd docs && sphinx-build -b html . _build/html

docs-api:
	@echo "Regenerating API documentation RST files..."
	sphinx-apidoc --no-toc -o docs/api src/pycalceff

build:
	@echo "Building sdist and wheel..."
	@rm -rf dist
	@python -m build

publish:
	@echo "NOTE: Uncomment the following lines to publish to TestPyPI or PyPI"
	@# twine upload --repository testpypi dist/*
	@# twine upload dist/*

test-pypi-install: build
	@echo "Testing PyPI wheel installation locally..."
	@conda create -n pycalceff-test-pypi python=3.13 -y
	@conda run -n pycalceff-test-pypi pip install dist/pycalceff-*.whl
	@conda run -n pycalceff-test-pypi pycalceff --version
	@conda run -n pycalceff-test-pypi pycalceff --help > /dev/null
	@echo "PyPI installation test passed!"
	@conda env remove -n pycalceff-test-pypi -y

test-conda-install:
	@./scripts/test-conda-install.sh

test-install: test-pypi-install test-conda-install
	@echo "All installation tests passed!"

clean:
	rm -rf .pytest_cache .mypy_cache dist build *.egg-info
	rm -rf src/pycalceff.egg-info
	rm -rf docs/_build docs/api
	rm -rf .hypothesis .coverage .ruff_cache
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -delete

clean-install-env:
	@echo "Removing pycalceff-install environment..."
	conda env remove -n pycalceff-install -y || true
	@echo "Done."

