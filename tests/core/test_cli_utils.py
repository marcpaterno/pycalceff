"""
Tests for core CLI utilities.

Tests the business logic functions in cli_utils.py.
"""

from pathlib import Path

import pytest
import typer
from pycalceff.core.cli_utils import (
    EfficiencyResult,
    calculate_efficiencies,
    output_efficiency_results,
    parse_and_validate_conflevel,
    parse_efficiency_data,
    parse_efficiency_file,
    print_efficiency_results,
    validate_confidence_level,
    validate_conflevel_input,
)
from pytest import CaptureFixture


def test_parse_efficiency_file_valid(tmp_path: Path) -> None:
    """Test parsing a valid efficiency data file."""
    data_file = tmp_path / "data.txt"
    data_file.write_text("10 20\n5 15\n# comment\n  3  10  \n")

    result = parse_efficiency_file(str(data_file))

    expected = [(10, 20), (5, 15), (3, 10)]
    assert result == expected


def test_parse_efficiency_file_empty(tmp_path: Path) -> None:
    """Test parsing an empty file."""
    data_file = tmp_path / "empty.txt"
    data_file.write_text("")

    result = parse_efficiency_file(str(data_file))
    assert result == []


def test_parse_efficiency_file_invalid_line(
    tmp_path: Path, capsys: CaptureFixture[str]
) -> None:
    """Test parsing file with invalid line."""
    data_file = tmp_path / "invalid.txt"
    data_file.write_text("10 20\ninvalid line\n5 15")

    with pytest.raises(typer.Exit):
        parse_efficiency_file(str(data_file))


def test_parse_efficiency_file_invalid_format(
    tmp_path: Path, capsys: CaptureFixture[str]
) -> None:
    """Test parsing file with invalid line format (wrong number of fields)."""
    data_file = tmp_path / "invalid_format.txt"
    data_file.write_text("10 20\n10 20 30\n5 15\n10\n")

    result = parse_efficiency_file(str(data_file))

    # Should parse valid lines and skip invalid format lines
    expected = [(10, 20), (5, 15)]
    assert result == expected

    # Check that warning was printed for invalid format lines
    captured = capsys.readouterr()
    assert "Invalid line format on line 2:" in captured.err
    assert "Invalid line format on line 4:" in captured.err


def test_parse_efficiency_file_file_not_found() -> None:
    """Test handling of file not found."""
    with pytest.raises(typer.Exit):
        parse_efficiency_file("nonexistent.txt")


def test_calculate_efficiencies() -> None:
    """Test calculating efficiencies for data pairs."""
    data_pairs = [(10, 20), (8, 10)]
    conflevel = 0.8

    results = calculate_efficiencies(data_pairs, conflevel)

    assert len(results) == 2
    for result in results:
        assert isinstance(result, EfficiencyResult)
        assert 0 <= result.mode <= 1
        assert 0 <= result.low <= result.mode <= result.high <= 1


def test_print_efficiency_results(capsys: CaptureFixture[str]) -> None:
    """Test printing efficiency results."""
    results = [
        EfficiencyResult(k=10, n=20, mode=0.5, low=0.3, high=0.7),
        EfficiencyResult(k=8, n=10, mode=0.8, low=0.6, high=0.9),
    ]

    print_efficiency_results(results)

    captured = capsys.readouterr()
    lines = captured.out.strip().split("\n")
    assert len(lines) == 2
    # Check format (scientific notation)
    assert "5.000000e-01" in lines[0]
    assert "8.000000e-01" in lines[1]


def test_validate_confidence_level_valid() -> None:
    """Test validating valid confidence level."""
    # Should not raise
    validate_confidence_level(0.95)
    validate_confidence_level(0.01)
    validate_confidence_level(0.99)


def test_validate_confidence_level_invalid() -> None:
    """Test validating invalid confidence level."""
    with pytest.raises(typer.Exit):
        validate_confidence_level(0.0)

    with pytest.raises(typer.Exit):
        validate_confidence_level(1.0)

    with pytest.raises(typer.Exit):
        validate_confidence_level(-0.1)

    with pytest.raises(typer.Exit):
        validate_confidence_level(1.1)


def test_parse_and_validate_conflevel_valid() -> None:
    """Test parsing and validating valid confidence level string."""
    result = parse_and_validate_conflevel("0.95")
    assert result == 0.95


def test_parse_and_validate_conflevel_invalid_string() -> None:
    """Test parsing invalid confidence level string."""
    with pytest.raises(typer.Exit):
        parse_and_validate_conflevel("invalid")


def test_parse_and_validate_conflevel_invalid_value() -> None:
    """Test parsing string that gives invalid confidence level."""
    with pytest.raises(typer.Exit):
        parse_and_validate_conflevel("1.5")


def test_validate_conflevel_input_float() -> None:
    """Test validating confidence level from float input."""
    result = validate_conflevel_input(0.95)
    assert result == 0.95


def test_validate_conflevel_input_string() -> None:
    """Test validating confidence level from string input."""
    result = validate_conflevel_input("0.95")
    assert result == 0.95


def test_validate_conflevel_input_invalid() -> None:
    """Test validating invalid confidence level input."""
    with pytest.raises(typer.Exit):
        validate_conflevel_input(1.5)


def test_parse_efficiency_data(
    tmp_path: Path, capsys: CaptureFixture[str]
) -> None:
    """Test the complete parse-calculate-output workflow."""
    data_file = tmp_path / "data.txt"
    data_file.write_text("10 20\n8 10")

    parse_efficiency_data(str(data_file), 0.8, None, False)

    captured = capsys.readouterr()
    output = captured.out
    # Should contain the table with results
    assert "Efficiency Results" in output
    assert "5.000000e-01" in output  # mode for 10/20
    assert "8.000000e-01" in output  # mode for 8/10


def test_output_efficiency_results_to_file(tmp_path: Path) -> None:
    """Test output_efficiency_results with file output."""
    data_pairs = [(10, 20), (8, 10)]
    results = calculate_efficiencies(data_pairs, 0.8)

    # Test TSV output
    tsv_file = tmp_path / "output.tsv"
    output_efficiency_results(results, str(tsv_file), False)
    content = tsv_file.read_text()
    lines = content.strip().split("\n")
    assert lines[0] == "k\tn\tmode\tlow\thigh"
    assert len(lines) == 3  # header + 2 data
    assert "10\t20\t" in lines[1]
    assert "8\t10\t" in lines[2]

    # Test CSV output
    csv_file = tmp_path / "output.csv"
    output_efficiency_results(results, str(csv_file), True)
    content = csv_file.read_text()
    lines = content.strip().split("\n")
    assert lines[0] == "k,n,mode,low,high"
    assert len(lines) == 3
    assert "10,20," in lines[1]
    assert "8,10," in lines[2]
