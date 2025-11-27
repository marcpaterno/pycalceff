"""
Main entry point for the pycalceff CLI application.

Handles command-line argument processing and launches the Typer app.
"""

import sys

from .cli.commands import app


def process_argv() -> None:
    """
    Process command-line arguments to convert help aliases.

    Converts '-h' and '-?' to '--help' for compatibility with Typer.
    """
    for i, arg in enumerate(sys.argv):
        if arg in ["-h", "-?"]:
            sys.argv[i] = "--help"


process_argv()

if __name__ == "__main__":
    app()
