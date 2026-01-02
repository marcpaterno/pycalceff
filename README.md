# pycalceff

A Python project for calculating (binomial) efficiencies and their uncertainties.
The mathematical theory and derivation of the formulas can be found in [Fermilab Technical Memo 2286-cd](https://lss.fnal.gov/archive/test-tm/2000/fermilab-tm-2286-cd.pdf).
If you use this software for published work, please cite this note.

The default algorithm for finding the shortest interval is based on Hyndman, R. J. (1996). *Computing and graphing highest density regions*, The American Statistician, 50(2), 120-126.

## Installation

```bash
pip install pycalceff
```

## Usage

```bash
# Show help
pycalceff --help

# Show version
pycalceff --version

# Calculate efficiencies from data file with 95% confidence intervals
# Displays results in a formatted table
pycalceff data.txt 0.95

# Save results to a tab-separated values (TSV) file
pycalceff --out results.tsv data.txt 0.95

# Save results to a comma-separated values (CSV) file
pycalceff --out results.csv --use-csv data.txt 0.95

# Error: --use-csv requires --out
pycalceff --use-csv data.txt 0.95  # This will show an error
```

### Output Formats

- **Console (default)**: Results are displayed in a nicely formatted table using Rich.
- **TSV File**: Tab-separated values with full precision scientific notation. Includes header row with columns: k, n, mode, low, high.
- **CSV File**: Comma-separated values with full precision scientific notation. Includes header row with columns: k, n, mode, low, high.

### Data File Format

The input file should contain lines with two integers each: number of successes (k) and number of trials (n). Lines beginning with '#' are treated as comments and ignored.

Example input file:

```text
# Example efficiency data
# Format: k n (successes, trials)
10 20
5 15
0 10
```

Example console output:

```
Efficiency Results                   
┏━━━━┳━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┓
┃  k ┃  n ┃         Mode ┃          Low ┃         High ┃
┡━━━━╇━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━┩
│ 10 │ 20 │ 5.000000e-01 │ 3.332780e-01 │ 6.667220e-01 │
│  5 │ 15 │ 3.333333e-01 │ 1.092969e-01 │ 6.240037e-01 │
│  0 │ 10 │ 0.000000e+00 │ 0.000000e+00 │ 3.085212e-01 │
└────┴────┴──────────────┴──────────────┴──────────────┘
```

Example TSV file content (results.tsv):

```text
k	n	mode	low	high
10	20	5.00000000000000000e-01	3.33278000000000000e-01	6.66722000000000000e-01
5	15	3.33333333333333315e-01	1.09296900000000000e-01	6.24003700000000000e-01
0	10	0.00000000000000000e+00	0.00000000000000000e+00	3.08521200000000000e-01
```

## Developer Guide

This section describes how to set up a development environment to contribute to `pycalceff`.

### Development Setup

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

### Development Workflow

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

### Packaging and Release Workflow

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
