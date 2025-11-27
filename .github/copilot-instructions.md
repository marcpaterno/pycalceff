# GitHub Copilot Instructions for pycalceff

## Communication

- Act as professional colleague; avoid sycophancy; point out mistakes constructively
- Say "I don't know" when lacking information; never fabricate answers
- Use literal language; state assumptions explicitly; ask clarifying questions
- Label options clearly; explain trade-offs; break down complex tasks into steps
- Use `fetch_webpage` tool for HTTPS links; verify relevance before using fetched content
- Do not create new virtual environments; rely on the active conda environment
- Use `git mv` (not `mv`) to rename/move files under version control
- When asked a question, answer the question directly without modifying code

## Environment Setup

### Conda Environment Activation

**CRITICAL**: Before running ANY Python commands, tests, or code quality checks, check that the `pycalceff-dev` conda environment is activated, as described below.

**Always check if the environment is active first:**
```bash
# Check if correct environment is active
if [[ "$CONDA_DEFAULT_ENV" != "pycalceff-dev" ]]; then
    conda activate pycalceff-dev
fi
```

**For all terminal commands:**
1. First, verify the conda environment with: `echo $CONDA_DEFAULT_ENV`
2. If output is NOT `pycalceff-dev`, run: `conda activate pycalceff-dev`
3. Then proceed with the actual command

**Environment setup (if not yet created):**
```bash
# Create environment (only needed once)
conda env create -f environment-dev.yml

# Activate it
conda activate pycalceff-dev
```

## Code Quality Standards

### Running Code Quality Checks

**ALWAYS run `make check` before committing code changes:**
```bash
conda activate pycalceff-dev
make check
```

This runs:
- `ruff format .`
- `ruff check .` - Linting
- `mypy src/` - Type checking  
- `pytest` - All tests

### Files to Check

**Check these files with `make check`:**
- All `.py` files in `src/pycalceff/`
- All `.py` files in `tests/`
- Any new Python files added to the project

**DO NOT run checks on:**
- Temporary files (`.tmp`, `.swp`, etc.)
- Files in `__pycache__/`
- Files in `.pytest_cache/`
- Files in build directories (`build/`, `dist/`, `*.egg-info/`)

### Fixing Code Quality Issues

When `make check` reports errors, fix them immediately according to these priorities:

#### 1. Ruff Linting Errors (MUST FIX ALL)

**Common issues and fixes:**

- **B904: Within an except clause, raise exceptions with `raise ... from err` or `raise ... from None`**
  ```python
  # BAD
  try:
      something()
  except ValueError as e:
      print(f"Error: {e}")
      raise typer.Exit(code=1)
  
  # GOOD - Known exception, suppress chain
  try:
      something()
  except ValueError as e:
      print(f"Error: {e}")
      raise typer.Exit(code=1) from None
  
  # GOOD - Unexpected exception, preserve chain
  try:
      something()
  except Exception as e:
      print(f"Error: {e}")
      raise typer.Exit(code=1) from e
  ```

- **F401: Module imported but unused**
  ```python
  # Remove the unused import
  ```

- **E501: Line too long (> 79 characters)**
  ```python
  # Break into multiple lines
  result = some_function(
      argument1,
      argument2,
      long_argument_name=value,
  )
  ```

- **F841: Local variable assigned but never used**
  ```python
  # Either use the variable or remove it
  # If intentionally unused, prefix with underscore
  _unused_value = function()
  ```

#### 2. Mypy Type Checking (FIX CRITICAL ISSUES)

**Type annotation requirements:**
- All function signatures must have return type annotations
- All function parameters should have type annotations
- Use `-> None` for functions that don't return values
- Use `TypedDict` for structured dictionaries
- Use `| None` (not `Optional`) for optional types (Python 3.11+)

**Example:**
```python
from typing import TypedDict

class NoteData(TypedDict):
    title: str
    content: str
    created_ts: int
    updated_ts: int

def parse_note(file_path: str) -> NoteData | None:
    """Parse a note file."""
    if not file_path:
        return None
    
    result: NoteData = {
        "title": "Example",
        "content": "Content",
        "created_ts": 0,
        "updated_ts": 0,
    }
    return result
```

#### 3. Pytest Test Failures (MUST FIX ALL)

**When tests fail:**
1. Read the error message carefully
2. Fix the underlying issue (not just the test)
3. Ensure all tests pass before committing
4. Add new tests for new functionality

## Code Style Guidelines

### Python Version Support
- Target Python 3.11 - 3.14
- Use modern Python 3.11+ syntax:
  - `X | None` instead of `Optional[X]`
  - `dict[str, int]` instead of `Dict[str, int]`
  - Use `match` statements where appropriate

### Docstrings

- Use compact Sphinx-style docstrings with reStructuredText field lists (e.g., `:param:`, `:returns:`, `:raises:`).
- Do not document types in docstrings, as they will be added by type annotations.
- Write docstrings for all functions, classes, and modules.

**Example:**
```python
def effic(k: int, N: int, conflevel: float) -> tuple[float, float, float]:
    """
    Calculate the Bayesian efficiency: mode and confidence interval.

    :param k: Number of successes
    :param N: Number of trials
    :param conflevel: Confidence level (0 < conflevel < 1)
    :returns: A tuple of (mode, low, high) where mode is the most probable efficiency, low and high are the bounds of the confidence interval
    :raises ValueError: If conflevel is not between 0 and 1
    """
```

### Import Organization
```python
# Standard library
import os
import sys
from pathlib import Path

# Third-party packages
import typer
from rich.console import Console

# Local modules
from pycalceff.core import parse_note
```
**Import Statement Rule**
Always insert new imports at the top of the file.
Sort imports: standard library, third-party, then local modules; each group alphabetically.

**When adding new imports to existing code, always place them at the top of the file, grouped and ordered as follows:**
1. Standard library imports
2. Third-party package imports
3. Local module imports
Each group should be sorted alphabetically.

### Line Length
- Maximum 79 characters (enforced by ruff)
- Break long lines logically
- Use parentheses for implicit line continuation

### Comment Line Width
- Limit all new comment lines you write to a maximum width of 79 characters.

### Type Annotations
- Always annotate function signatures
- Annotate complex local variables
- Use TypedDict for structured data

### Error Handling
- Always use `from None` or `from e` when raising in except blocks
- Provide helpful error messages
- Use specific exception types

## Workflow for Code Changes

**Before making changes:**
```bash
conda activate pycalceff-dev
```

**After making changes:**
```bash
# 1. Format code
ruff format .

# 2. Check for issues
make check

# 3. Fix any reported issues

# 4. Re-run checks
make check

# 5. Only commit when all checks pass
git add .
git commit -m "Your message"
```

## Common Commands Reference

```bash
# Activate environment (ALWAYS FIRST)
conda activate pycalceff-dev

# Run all checks
make check

# Run individual checks
make lint           # Ruff linting
make type-check     # Mypy type checking
make test           # Pytest tests

# Format code
make format         # Ruff formatter

# Run the CLI
pycalceff --help
pycalceff --version

# Build package
make build

# Clean artifacts
make clean
```

## File Structure Rules

**Source code:**
- Core logic goes in `src/pycalceff/core/`
- CLI interface goes in `src/pycalceff/cli/`

**Tests:**
- Core tests in `tests/core/`
- CLI tests in `tests/cli/`
- Use `pytest` fixtures and `tempfile` for file operations

**Configuration:**
- Dependencies in `pyproject.toml`, `environment-dev.yml`, and `conda.recipe/meta.yaml`
- Keep versions consistent across all files
- Python 3.11+ only

## Testing

**Workflow:**
1. Write tests with comprehensive coverage
2. Never suggest use of monkeypatching in a test unless the result is much simpler and clearer than alternatives; prefer dependency injection, fixtures, or context managers, and finally mocks.
3. Use hypothesis tests for complex logic
4. Run `make format fix` on source and test code
5. Run `make type-check` to verify no type errors
6. Whenever running tests, run `pytest -n auto` (parallel mode required - matches CI/CD)

**Parallel execution ensures tests are isolated and order-independent. Only run serially for debugging.**

**Test Organization:**
- Prefer simple functions over classes
- Use classes only for: shared fixtures/state, clearer parametrization
- Do NOT use classes for logical grouping or namespaces
- Group with comments, not classes



## Auto-Fix Commands

**If you see linting errors, try auto-fix first:**
```bash
conda activate pycalceff-dev
ruff check --fix .
ruff format .
make check
```

**If mypy errors appear:**
- Add missing type annotations
- Import necessary types from `typing`
- Use `# type: ignore[error-code]` only as last resort with comment explaining why

**If tests fail:**
- Read the full error traceback
- Fix the underlying code, not just the test
- Run single test to debug: `pytest tests/test_core.py::test_name -v`

## Summary

✅ **ALWAYS activate conda environment first**  
✅ **ALWAYS run `make check` before committing**  
✅ **ALWAYS fix all ruff, mypy, and pytest errors**  
✅ **NEVER commit code that fails checks**  
