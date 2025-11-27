"""
Basic tests for pycalceff CLI functionality.

Tests the main CLI commands and argument processing.
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


def test_data_file_access() -> None:
    """
    Test that example data files can be accessed.

    Verifies that the get_data_file function can locate and read
    the example data file included with the package.
    """
    from pycalceff import get_data_file

    # Test that we can get the path to the example data file
    data_path = get_data_file("example_data.txt")
    assert data_path.exists()

    # Test that we can read the data
    with open(data_path, encoding="utf-8") as f:
        content = f.read()
        assert "10 20" in content  # Check for expected data
        assert "5 15" in content
