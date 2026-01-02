"""
pycalceff: Bayesian efficiency calculation package.

This package provides tools for calculating exact binomial efficiency
confidence intervals using Bayesian methods with beta distributions.
"""

import importlib.metadata

__version__ = importlib.metadata.version("pycalceff")

import importlib.resources
from pathlib import Path


def get_data_file(filename: str) -> Path:
    """
    Get the path to a data file included with the package.

    :param filename: Name of the data file (e.g., 'example_data.txt')
    :returns: Path to the data file

    Examples
    --------
    >>> from pycalceff import get_data_file
    >>> data_path = get_data_file('example_data.txt')
    >>> with open(data_path) as f:
    ...     data = f.read()
    """
    files = importlib.resources.files("pycalceff.data")
    return Path(str(files / filename))
