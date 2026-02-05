# pycalceff

[![CI](https://github.com/marcpaterno/pycalceff/workflows/CI/badge.svg)](https://github.com/marcpaterno/pycalceff/actions)
[![codecov](https://codecov.io/gh/marcpaterno/pycalceff/branch/master/graph/badge.svg)](https://codecov.io/gh/marcpaterno/pycalceff)
[![PyPI version](https://badge.fury.io/py/pycalceff.svg)](https://badge.fury.io/py/pycalceff)
[![conda-forge](https://img.shields.io/conda/vn/conda-forge/pycalceff.svg)](https://anaconda.org/conda-forge/pycalceff)
[![Python versions](https://img.shields.io/pypi/pyversions/pycalceff.svg)](https://pypi.org/project/pycalceff/)
[![License](https://img.shields.io/badge/License-BSD_3--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause)
[![Downloads](https://static.pepy.tech/badge/pycalceff)](https://pepy.tech/project/pycalceff)

A Python project for calculating (binomial) efficiencies and their uncertainties.
The mathematical theory and derivation of the formulas can be found in [Fermilab Technical Memo 2286-cd](https://lss.fnal.gov/archive/test-tm/2000/fermilab-tm-2286-cd.pdf).
If you use this software for published work, please cite this note.

The default algorithm for finding the shortest interval is based on Hyndman, R. J. (1996). *Computing and graphing highest density regions*, The American Statistician, 50(2), 120-126.

## Installation

### From PyPI (pip)

```bash
pip install pycalceff
```

### From conda-forge

```bash
conda install -c conda-forge pycalceff
```

Or with mamba:

```bash
mamba install -c conda-forge pycalceff
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

## Contributing

For information on setting up a development environment and contributing to this project, see [CONTRIBUTING.md](CONTRIBUTING.md).
