# Contributing to pycalceff

This guide describes how to set up a development environment to contribute to `pycalceff`.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally
3. **Create a feature branch** for your changes
4. **Make your changes** following the development workflow below
5. **Submit a pull request** to the main repository

## Development Setup

To set up the development environment, you will need to have [Miniforge](https://github.com/conda-forge/miniforge) or [Miniconda](https://docs.conda.io/en/latest/miniconda.html) installed.

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/marcpaterno/pycalceff.git
    cd pycalceff
    ```

2.  **Create and activate the development environment:**
    The `Makefile` provides a convenient target for this.
    ```bash
    make setup
    conda activate pycalceff-dev
    ```
    The `setup` target uses the `environment-dev.yml` file to create a consistent Conda environment named `pycalceff-dev` with all necessary build and development tools.

3.  **Install the package in editable mode:**
    Once the environment is active, install `pycalceff` in editable mode with all development dependencies.
    ```bash
    make install
    ```
    This target uses `pip` to install the project in "editable" mode (`-e`), so any changes you make to the source code are immediately reflected when you run the tool. It also installs the `[dev]` dependencies listed in `pyproject.toml`.

## Development Workflow

The `Makefile` contains targets for common development tasks.

- **Run all checks:** To ensure code quality, run all formatting, linting, type-checking, and unit tests at once.
  ```bash
  make check
  ```

- **Run unit tests:** To run the test suite with `pytest`.
  ```bash
  make test
  ```

- **Format code:** To automatically format code with `ruff`.
  ```bash
  make format
  ```

## Packaging and Release Workflow

The build system is configured to produce PyPI packages.

1.  **Build the packages:**
    To build the sdist and wheel for PyPI, use the `build` target.
    ```bash
    make build
    ```
    The PyPI artifacts will be in the `dist/` directory.

2.  **Test local package installation:**
    Before publishing, you can test the PyPI package in a clean, isolated environment without uploading it anywhere. This is the most important verification step.
    ```bash
    make test-install
    ```
    This command will:
    - Build the packages.
    - Create a temporary environment and install the PyPI wheel, then run tests.
    - Clean up the temporary environment afterward.
