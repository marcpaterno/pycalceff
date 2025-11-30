"""
CLI utility functions for pycalceff.

Contains business logic and error handling functions used by the CLI.
"""

from typing import NamedTuple, NoReturn

import typer

from .effic import HPDAlgorithm, RootFinder, effic


class EfficiencyResult(NamedTuple):
    """Result of an efficiency calculation."""

    k: int
    n: int
    mode: float
    low: float
    high: float

    @property
    def width(self) -> float:
        """The width of the confidence interval.

        :returns: The width of the confidence interval
        """
        return self.high - self.low


def parse_efficiency_file(filename: str) -> list[tuple[int, int]]:
    """
    Parse efficiency data file and return list of (k, n) pairs.

    :param filename: Path to the data file
    :returns: List of (successes, trials) pairs
    :raises typer.Exit: For file not found or parsing errors
    """
    data_pairs = []
    try:
        with open(filename, encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                parts = line.split()
                if len(parts) != 2:
                    typer.echo(
                        f"Invalid line format on line {line_num}: {line}",
                        err=True,
                    )
                    continue
                try:
                    k = int(parts[0])
                    n = int(parts[1])
                    data_pairs.append((k, n))
                except ValueError as e:
                    typer.echo(
                        f"Error parsing line {line_num} '{line}': {e}",
                        err=True,
                    )
                    raise typer.Exit(3) from e
    except FileNotFoundError as exc:
        handle_file_not_found_error(filename, exc)
    except Exception as e:  # Catch any unexpected errors
        handle_general_error(e)

    return data_pairs


def calculate_efficiencies(
    data_pairs: list[tuple[int, int]],
    conflevel: float,
    algorithm: HPDAlgorithm | None = None,
    root_finder: RootFinder | None = None,
) -> list[EfficiencyResult]:
    """
    Calculate efficiency confidence intervals for a list of (k, n) pairs.

    :param data_pairs: List of (successes, trials) pairs
    :param conflevel: Confidence level for calculations
    :param algorithm: HPD algorithm to use (default: BINARY_SEARCH)
    :param root_finder: Root-finding algorithm to use (default: brentq)
    :returns: List of efficiency calculation results
    """
    if algorithm is None:
        algorithm = HPDAlgorithm.BINARY_SEARCH
    if root_finder is None:
        from .effic import DEFAULT_ROOT_FINDER

        root_finder = DEFAULT_ROOT_FINDER
    results = []
    for k, n in data_pairs:
        mode, low, high = effic(
            k, n, conflevel, root_finder=root_finder, algorithm=algorithm
        )
        result = EfficiencyResult(k=k, n=n, mode=mode, low=low, high=high)
        results.append(result)
    return results


def print_efficiency_results(results: list[EfficiencyResult]) -> None:
    """
    Print efficiency calculation results to stdout.

    :param results: List of efficiency calculation results to print
    """
    for result in results:
        typer.echo(f"{result.mode:.6e} {result.low:.6e} {result.high:.6e}")


def output_efficiency_results(
    results: list[EfficiencyResult], out: str | None, use_csv: bool
) -> None:
    """
    Output efficiency calculation results to file or stdout.

    :param results: List of efficiency calculation results
    :param out: Output file path, or None for stdout
    :param use_csv: Whether to use CSV format
    """
    if out is None:
        # Output to stdout with rich table
        from rich.console import Console
        from rich.table import Table

        console = Console()
        table = Table(title="Efficiency Results")
        table.add_column("k", justify="right", style="cyan")
        table.add_column("n", justify="right", style="cyan")
        table.add_column("Mode", justify="right", style="green")
        table.add_column("Low", justify="right", style="yellow")
        table.add_column("High", justify="right", style="yellow")

        for result in results:
            table.add_row(
                str(result.k),
                str(result.n),
                f"{result.mode:.6e}",
                f"{result.low:.6e}",
                f"{result.high:.6e}",
            )
        console.print(table)
    else:
        # Output to file
        import csv

        with open(out, "w", newline="", encoding="utf-8") as f:
            if use_csv:
                writer = csv.writer(f)
                writer.writerow(["k", "n", "mode", "low", "high"])
                for result in results:
                    writer.writerow(
                        [
                            result.k,
                            result.n,
                            f"{result.mode:.17e}",
                            f"{result.low:.17e}",
                            f"{result.high:.17e}",
                        ]
                    )
            else:
                f.write("k\tn\tmode\tlow\thigh\n")
                for result in results:
                    f.write(
                        f"{result.k}\t{result.n}\t{result.mode:.17e}\t"
                        f"{result.low:.17e}\t{result.high:.17e}\n"
                    )


def parse_efficiency_data(
    filename: str,
    conflevel: float,
    out: str | None,
    use_csv: bool,
    algorithm: HPDAlgorithm | None = None,
    root_finder: RootFinder | None = None,
) -> None:
    """
    Parse efficiency data from file, calculate results, and output them.

    :param filename: Path to the data file
    :param conflevel: Confidence level for calculations
    :param out: Output file path, or None for stdout
    :param use_csv: Whether to use CSV format (requires out to be set)
    :param algorithm: HPD algorithm to use
    :param root_finder: Root-finding algorithm to use
    :raises typer.Exit: For various error conditions
    """
    data_pairs = parse_efficiency_file(filename)
    results = calculate_efficiencies(
        data_pairs, conflevel, algorithm, root_finder
    )
    output_efficiency_results(results, out, use_csv)


def validate_confidence_level(conflevel: float) -> None:
    """
    Validate that confidence level is between 0 and 1.

    :param conflevel: Confidence level to validate
    :raises typer.Exit: If confidence level is invalid
    """
    if not (0 < conflevel < 1):
        typer.echo("Confidence level must be between 0 and 1", err=True)
        raise typer.Exit(1)


def parse_and_validate_conflevel(conflevel_str: str) -> float:
    """
    Parse string to float and validate confidence level range.

    :param conflevel_str: String representation of confidence level
    :returns: Validated confidence level
    :raises typer.Exit: If string cannot be parsed or value is out of range
    """
    try:
        conflevel = float(conflevel_str)
    except ValueError as exc:
        handle_invalid_conflevel(conflevel_str, exc)

    validate_confidence_level(conflevel)
    return conflevel


def validate_conflevel_input(conflevel_input: float | str) -> float:
    """
    Validate confidence level from either float or string input.

    This is a unified validation function that handles both:
    - Float inputs (from Typer argument parsing)
    - String inputs (from fallback argument parsing)

    :param conflevel_input: Confidence level as float or string
    :returns: Validated confidence level
    :raises typer.Exit: If validation fails
    """
    if isinstance(conflevel_input, str):
        return parse_and_validate_conflevel(conflevel_input)
    else:
        # Assume it's already a float from Typer
        validate_confidence_level(conflevel_input)
        return conflevel_input


def handle_file_not_found_error(
    filename: str, exc: FileNotFoundError
) -> NoReturn:
    """
    Handle file not found errors.

    :param filename: The filename that was not found
    :param exc: The original exception
    :raises typer.Exit: Always raises exit code 2
    """
    typer.echo(f"Failed to open file '{filename}'", err=True)
    raise typer.Exit(2) from exc


def handle_general_error(exc: Exception) -> NoReturn:
    """
    Handle general errors.

    :param exc: The exception that occurred
    :raises typer.Exit: Always raises exit code 3
    """
    typer.echo(f"Error: {exc}", err=True)
    raise typer.Exit(3) from None


def handle_invalid_conflevel(conflevel_str: str, exc: ValueError) -> NoReturn:
    """
    Handle invalid confidence level errors.

    :param conflevel_str: The invalid confidence level string
    :param exc: The original exception
    :raises typer.Exit: Always raises exit code 1
    """
    typer.echo(f"Invalid confidence level: {conflevel_str}", err=True)
    raise typer.Exit(1) from exc
