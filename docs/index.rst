Welcome to pycalceff's documentation!
=====================================

**pycalceff** is a Python package for calculating exact binomial efficiency confidence intervals using Bayesian methods with beta distributions.


Overview
--------

This package provides tools for statistical analysis of efficiencies in experimental physics, particularly useful for particle physics experiments where precise efficiency measurements are crucial.

The core functionality includes:

* **Bayesian Efficiency Calculations**: Compute efficiency estimates with confidence intervals using beta distribution methods
* **Exact Binomial Confidence Intervals**: Calculate precise confidence intervals for binomial proportions
* **Command-Line Interface**: Easy-to-use CLI for interactive efficiency calculations

Installation
------------

Install from source in development mode:

.. code-block:: bash

   git clone https://github.com/marcpaterno/pycalceff.git
   cd pycalceff
   conda env create -f environment-dev.yml
   conda activate pycalceff-dev
   pip install -e .[dev]

For production use:

.. code-block:: bash

   pip install pycalceff

Quick Start
-----------

Command Line Usage
~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Show help
   pycalceff --help

   # Show version
   pycalceff --version

   # Calculate efficiencies from data file with 95% confidence
   # Displays results in a formatted table
   pycalceff data.txt 0.95

   # Save results to a tab-separated values (TSV) file
   pycalceff --out results.tsv data.txt 0.95

   # Save results to a comma-separated values (CSV) file
   pycalceff --out results.csv --use-csv data.txt 0.95

   # Error: --use-csv requires --out
   pycalceff --use-csv data.txt 0.95  # This will show an error

**Output Formats:**

* **Console (default)**: Results are displayed in a nicely formatted table using Rich.
* **TSV File**: Tab-separated values with full precision scientific notation. Includes header row with columns: k, n, mode, low, high.
* **CSV File**: Comma-separated values with full precision scientific notation. Includes header row with columns: k, n, mode, low, high.

**Data File Format:**

The input data file should contain lines with two integers per line: successes (k) and trials (N), separated by whitespace. Lines starting with # or empty lines are ignored.

Example data.txt:

.. code-block:: text

   # Example efficiency data
   10 20
   8 15
   5 10

Python API Usage
~~~~~~~~~~~~~~~~

.. code-block:: python

   from pycalceff.core.effic import effic, probability_mass

   # Calculate efficiency with confidence interval
   # 3 successes out of 20 trials, 95% confidence
   mode, low, high = effic(k=3, ntrials=20, conflevel=0.95)
   print(f"Efficiency: {mode:.3f} +{high-mode:.3f} -{mode-low:.3f}")

   # Probability mass within the interval [low, high]
   prob_mass = probability_mass(k=3, ntrials=20, low=low, high=high)
   print(f"Probability mass in [{low}, {high}]: {prob_mass:.4f}")

Mathematical Background
-----------------------

The package implements Bayesian efficiency calculations using the beta distribution.
For a binomial process with :math:`k` successes out of :math:`N` trials, the posterior distribution for the efficiency :math:`\epsilon` is:

.. math::

   p(\epsilon | k, N) \propto \epsilon^{k} (1-\epsilon)^{N-k}

The most probable value (mode) is :math:`k/N`.
The confidence intervals are calculated by finding the shortest interval containing the desired probability content.
The shortest interval is also called the "high density region".

References
~~~~~~~~~~

The statistical methods implemented in this package are based on:

* Paterno, M. (2004). Calculating Efficiencies and Their Uncertainties.
  Fermilab Technical Memorandum TM-2286-CD.
  Available at: https://lss.fnal.gov/archive/test-tm/2000/fermilab-tm-2286-cd.pdf

The default algorithm for finding the shortest interval is based on Hyndman, R. J. (1996), *Computing and graphing highest density regions*, The American Statistician, 50(2), 120-126.



Contents
--------

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   api/pycalceff


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`