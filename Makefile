
.PHONY: help setup install test docs docs-api build check-dist publish-test publish test-pypi-install test-install conda-recipe conda-build clean

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
	@echo "  check-dist: validate distribution files with twine"
	@echo "  publish-test: upload to TestPyPI"
	@echo "  publish  : publish the package to PyPI"
	@echo "  test-pypi-install: test PyPI wheel installation locally"
	@echo "  test-install: test PyPI installation locally"
	@echo "  conda-recipe: regenerate conda recipe from PyPI"
	@echo "  conda-smoke-test: build conda package locally (smoke test)"
	@echo "  clean    : remove temporary files"

setup:
	@echo "Creating conda environment..."
	conda env create -f environment-dev.yml
	@echo "NOTE: Please activate the 'pycalceff-dev' conda environment before running 'make install'."

install: check-no-spack
	@echo "Uninstalling existing package installation..."
	pip uninstall -y pycalceff || true
	@echo "Installing package in editable mode with dev dependencies..."
	pip install -e .[dev]

format:
	ruff format src tests

typecheck: check-no-spack
	mypy -p src -p tests

lint:
	ruff check src tests

fix:
	ruff check --fix src tests

check: format lint typecheck test

test: check-no-spack
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

check-dist: build
	@echo "Checking distribution files..."
	twine check dist/*
	@echo "Distribution check passed!"

publish-test: check-dist
	@echo "Uploading to TestPyPI..."
	twine upload --repository testpypi dist/*
	@echo "Published to TestPyPI: https://test.pypi.org/project/pycalceff/"

publish: check-dist
	@echo "WARNING: This will upload to PyPI (production)!"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		twine upload dist/*; \
		echo "Published to PyPI: https://pypi.org/project/pycalceff/"; \
	else \
		echo "Upload cancelled."; \
	fi

test-pypi-install: check-no-spack build
	@echo "Testing PyPI wheel installation locally..."
	@conda create -n pycalceff-test-pypi python=3.13 -y
	@conda run -n pycalceff-test-pypi pip install dist/pycalceff-*.whl
	@conda run -n pycalceff-test-pypi pycalceff --version
	@conda run -n pycalceff-test-pypi pycalceff --help > /dev/null
	@echo "PyPI installation test passed!"
	@conda env remove -n pycalceff-test-pypi -y

test-install: test-pypi-install
	@echo "Installation test passed!"

check-no-spack:
	@if [ -n "$${SPACK_ENV}" ]; then \
		echo "ERROR: Spack environment detected (SPACK_ENV=$${SPACK_ENV})."; \
		echo "Please deactivate Spack (run 'despacktivate' or 'spack env deactivate') before running this command."; \
		exit 1; \
	fi

conda-smoke-test: check-no-spack
	@echo "Building conda package locally (smoke test)..."
	@command -v conda-build >/dev/null 2>&1 || { echo "ERROR: conda-build not installed. Run: conda install conda-build"; exit 1; }
	conda build conda.recipe/
	@echo "Build complete! Install locally with: conda install --use-local pycalceff"

clean:
	rm -rf .pytest_cache .mypy_cache dist build *.egg-info
	rm -rf src/pycalceff.egg-info
	rm -rf docs/_build docs/api
	rm -rf .hypothesis .coverage .ruff_cache
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -delete
