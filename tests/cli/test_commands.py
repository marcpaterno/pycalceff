"""
Tests for CLI commands.

Tests the Typer-based command-line interface commands.
"""

import sys
from pathlib import Path

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


def test_default_behavior() -> None:
    """
    Test that the default behavior (BINARY_SEARCH algorithm) works.
    """
    # Create a small test data file
    test_data = "5 10\n3 8\n"
    test_file = Path("test_cli_data.txt")
    test_file.write_text(test_data, encoding="utf-8")

    try:
        result = runner.invoke(app, [str(test_file), "0.95"])
        assert result.exit_code == 0
        # Should contain efficiency results
        assert "Efficiency Results" in result.stdout
        assert "5" in result.stdout  # k value
        assert "10" in result.stdout  # n value
    finally:
        test_file.unlink()


def test_root_finder_option() -> None:
    """
    Test specifying root finder.
    """
    test_data = "5 10\n"
    test_file = Path("test_cli_root_finder.txt")
    test_file.write_text(test_data, encoding="utf-8")

    try:
        result = runner.invoke(
            app, ["--root-finder", "brentq", str(test_file), "0.95"]
        )
        assert result.exit_code == 0
        assert "Efficiency Results" in result.stdout
    finally:
        test_file.unlink()


def test_root_finder_short_option() -> None:
    """
    Test short form of root finder option (-r).
    """
    test_data = "5 10\n"
    test_file = Path("test_cli_short_r.txt")
    test_file.write_text(test_data, encoding="utf-8")

    try:
        result = runner.invoke(app, ["-r", "bisect", str(test_file), "0.95"])
        assert result.exit_code == 0
        assert "Efficiency Results" in result.stdout
    finally:
        test_file.unlink()


def test_invalid_root_finder() -> None:
    """
    Test error handling for invalid root finder.
    """
    test_data = "5 10\n"
    test_file = Path("test_cli_invalid_rf.txt")
    test_file.write_text(test_data, encoding="utf-8")

    try:
        result = runner.invoke(
            app, ["--root-finder", "invalid", str(test_file), "0.95"]
        )
        assert result.exit_code != 0
    finally:
        test_file.unlink()
