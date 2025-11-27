"""
Tests for CLI commands.

Tests the Typer-based command-line interface commands.
"""

import sys

from typer.testing import CliRunner

from pycalceff.main import app, process_argv

runner = CliRunner()


def test_version() -> None:
    """
    Test the version option.

    Verifies that the --version flag displays the correct version information.
    """
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "pycalceff version:" in result.stdout


def test_argv_processing() -> None:
    """
    Test argv processing for help aliases.

    Verifies that -h and -? are converted to --help for Typer compatibility.
    """
    original_argv = sys.argv.copy()
    sys.argv = ["test", "-h", "data.txt", "0.95"]
    process_argv()
    assert sys.argv == ["test", "--help", "data.txt", "0.95"]
    sys.argv = original_argv
