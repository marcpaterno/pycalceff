"""
CLI commands for pycalceff.

Defines the Typer application and command handlers for the CLI interface.
"""

import typer

from .. import __version__ as version
from ..core.cli_utils import (
    parse_efficiency_data,
    validate_conflevel_input,
)

HELP_OPTIONS = ["-h", "-?", "--help"]

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

    conflevel = validate_conflevel_input(conflevel)
    parse_efficiency_data(filename, conflevel, out, use_csv)
