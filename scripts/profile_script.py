#!/usr/bin/env python3

import cProfile
import pstats
import sys
from functools import partial
from pstats import SortKey
from typing import cast

from scipy.optimize import bisect, brenth, brentq, ridder, toms748

from pycalceff.core.cli_utils import parse_efficiency_file
from pycalceff.core.effic import RootFinder, effic

# Supported root finders
SUPPORTED_ROOT_FINDERS: dict[str, RootFinder] = {
    "bisect": cast(RootFinder, bisect),
    "brenth": cast(RootFinder, brenth),
    "brentq": cast(RootFinder, brentq),
    "ridder": cast(RootFinder, ridder),
    "toms748": cast(RootFinder, partial(toms748, k=1)),
}


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python profile_script.py <root_finder>", file=sys.stderr)
        supported = ", ".join(SUPPORTED_ROOT_FINDERS.keys())
        print(f"Supported root finders: {supported}", file=sys.stderr)
        sys.exit(1)

    root_finder_name = sys.argv[1]
    if root_finder_name not in SUPPORTED_ROOT_FINDERS:
        print(f"Unsupported root finder: {root_finder_name}", file=sys.stderr)
        supported = ", ".join(SUPPORTED_ROOT_FINDERS.keys())
        print(f"Supported root finders: {supported}", file=sys.stderr)
        sys.exit(1)

    root_finder = SUPPORTED_ROOT_FINDERS[root_finder_name]

    # Parse the data
    data_pairs = parse_efficiency_file("data.txt")

    # Define the calculations function
    def run_calculations() -> None:
        for k, n in data_pairs:
            effic(k, n, 0.95, root_finder=root_finder)

    # Make it available in global scope for cProfile
    globals()["run_calculations"] = run_calculations

    profile_filename = f"profile_{root_finder_name}.prof"
    cProfile.run("run_calculations()", profile_filename)

    # Print stats
    p = pstats.Stats(profile_filename)
    p.sort_stats(SortKey.CUMULATIVE).print_stats(20)


if __name__ == "__main__":
    main()
