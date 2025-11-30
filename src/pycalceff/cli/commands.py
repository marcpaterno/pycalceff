"""
CLI commands for pycalceff.

Defines the Typer application and command handlers for the CLI interface.
"""

from functools import partial
from typing import cast

import typer
from scipy.optimize import bisect, brenth, brentq, ridder, toms748

from .. import __version__ as version
from ..core.cli_utils import (
    parse_efficiency_data,
    validate_conflevel_input,
)
from ..core.effic import DEFAULT_ROOT_FINDER_BRENTH, HPDAlgorithm, RootFinder

# Supported root finders for CLI
SUPPORTED_ROOT_FINDERS = {"bisect", "brenth", "brentq", "ridder", "toms748"}

# Order for displaying root finders by speed (fastest first)
ROOT_FINDER_SPEED_ORDER = ["brenth", "brentq", "toms748", "ridder", "bisect"]
assert SUPPORTED_ROOT_FINDERS == set(ROOT_FINDER_SPEED_ORDER)

HELP_OPTIONS = ["-h", "-?", "--help"]

# Default options for CLI
DEFAULT_ROOT_FINDER = DEFAULT_ROOT_FINDER_BRENTH

# CLI option definitions
ROOT_FINDER_OPTION = typer.Option(
    None,
    "--root-finder",
    "-r",
    help=f"Root finder (ordered by speed): {', '.join(ROOT_FINDER_SPEED_ORDER)}",
)

app = typer.Typer(
    name="pycalceff",
    help="""
    [bold cyan]Calculation of exact binomial efficiency confidence intervals[/bold cyan]
    """,
    add_completion=True,
    rich_markup_mode="rich",
    no_args_is_help=True,
    pretty_exceptions_enable=True,
)

app.help_option_names = HELP_OPTIONS  # type: ignore


def version_callback(value: bool) -> None:
    if value:
        typer.echo(f"pycalceff version: {version}")
        raise typer.Exit()


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    filename: str = typer.Argument(None, help="Data file with k n pairs"),
    conflevel: float | None = typer.Argument(
        None, help="Confidence level (0-1)"
    ),
    out: str | None = typer.Option(
        None, "--out", "-o", help="Output file for results"
    ),
    use_csv: bool = typer.Option(
        False, "--use-csv", "-c", help="Use CSV format for output file"
    ),
    root_finder_str: str | None = ROOT_FINDER_OPTION,
    version: bool = typer.Option(None, "--version", callback=version_callback),
) -> None:
    """
    Calculate Bayesian efficiency confidence intervals from data file.

    Reads a file containing lines with two integers (k n) representing
    successes and trials, and outputs the most probable efficiency and
    confidence interval bounds for each line.

    :param ctx: Typer context object
    :param filename: Path to data file containing k n pairs
    :param conflevel: Confidence level between 0 and 1
    :param out: Output file for results (optional)
    :param use_csv: Use CSV format for output file (requires --out)
    :param version: Show version and exit
    """
    if version:
        return

    if not filename or conflevel is None:
        # No arguments provided, show help
        typer.echo(ctx.get_help())
        return

    if use_csv and out is None:
        typer.echo("--use-csv requires --out to be specified", err=True)
        raise typer.Exit(1)

    # Determine algorithm and root finder based on --root-finder presence
    if root_finder_str is not None:
        if root_finder_str not in SUPPORTED_ROOT_FINDERS:
            typer.echo(f"Unsupported root finder: {root_finder_str}", err=True)
            supported = ", ".join(ROOT_FINDER_SPEED_ORDER)
            typer.echo(f"Supported root finders: {supported}", err=True)
            raise typer.Exit(1)
        algorithm = HPDAlgorithm.ROOT_FINDING
        root_finder_map = {
            "bisect": cast(RootFinder, bisect),
            "brenth": cast(RootFinder, brenth),
            "brentq": cast(RootFinder, brentq),
            "ridder": cast(RootFinder, ridder),
            "toms748": cast(RootFinder, partial(toms748, k=1)),
        }
        actual_root_finder = root_finder_map[root_finder_str]
    else:
        algorithm = HPDAlgorithm.BINARY_SEARCH
        actual_root_finder = None

    conflevel = validate_conflevel_input(conflevel)
    parse_efficiency_data(
        filename, conflevel, out, use_csv, algorithm, actual_root_finder
    )
