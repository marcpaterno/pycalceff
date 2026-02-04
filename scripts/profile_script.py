#!/usr/bin/env python3

import cProfile
import pstats
import sys
from functools import partial
from pstats import SortKey
from typing import cast

from pycalceff.core.cli_utils import parse_efficiency_file
from pycalceff.core.effic import HPDAlgorithm, RootFinder, effic
from scipy.optimize import bisect, brenth, brentq, ridder, toms748

# Supported root finders
SUPPORTED_ROOT_FINDERS: dict[str, RootFinder] = {
    "bisect": cast(RootFinder, bisect),
    "brenth": cast(RootFinder, brenth),
    "brentq": cast(RootFinder, brentq),
    "ridder": cast(RootFinder, ridder),
    "toms748": cast(RootFinder, partial(toms748, k=1)),
}

# Supported HPD algorithms
SUPPORTED_ALGORITHMS: dict[str, HPDAlgorithm] = {
    "root_finding": HPDAlgorithm.ROOT_FINDING,
    "binary_search": HPDAlgorithm.BINARY_SEARCH,
}


def main() -> None:
    if len(sys.argv) != 3:
        print(
            "Usage: python profile_script.py <root_finder> <algorithm>",
            file=sys.stderr,
        )
        supported_finders = ", ".join(SUPPORTED_ROOT_FINDERS.keys())
        print(f"Supported root finders: {supported_finders}", file=sys.stderr)
        supported_algorithms = ", ".join(SUPPORTED_ALGORITHMS.keys())
        print(f"Supported algorithms: {supported_algorithms}", file=sys.stderr)
        sys.exit(1)

    root_finder_name = sys.argv[1]
    if root_finder_name not in SUPPORTED_ROOT_FINDERS:
        print(f"Unsupported root finder: {root_finder_name}", file=sys.stderr)
        supported = ", ".join(SUPPORTED_ROOT_FINDERS.keys())
        print(f"Supported root finders: {supported}", file=sys.stderr)
        sys.exit(1)

    algorithm_name = sys.argv[2]
    if algorithm_name not in SUPPORTED_ALGORITHMS:
        print(f"Unsupported algorithm: {algorithm_name}", file=sys.stderr)
        supported = ", ".join(SUPPORTED_ALGORITHMS.keys())
        print(f"Supported algorithms: {supported}", file=sys.stderr)
        sys.exit(1)

    root_finder = SUPPORTED_ROOT_FINDERS[root_finder_name]
    algorithm = SUPPORTED_ALGORITHMS[algorithm_name]

    # Parse the data
    data_pairs = parse_efficiency_file("data.txt")

    # Define the calculations function
    def run_calculations() -> None:
        for k, n in data_pairs:
            effic(k, n, 0.95, root_finder=root_finder, algorithm=algorithm)

    # Make it available in global scope for cProfile
    globals()["run_calculations"] = run_calculations

    profile_filename = f"profile_{root_finder_name}_{algorithm_name}.prof"
    cProfile.run("run_calculations()", profile_filename)

    # Print stats
    p = pstats.Stats(profile_filename)
    p.sort_stats(SortKey.CUMULATIVE).print_stats(20)


if __name__ == "__main__":
    main()
