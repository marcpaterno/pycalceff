# Release Notes

## v1.1.0

### 🎉 NEW FEATURES

- **Conda installation support**: You can now install pycalceff directly from conda-forge using `conda install -c conda-forge pycalceff` or `mamba install -c conda-forge pycalceff`. This provides an alternative to pip installation and better integration with conda environments.

### 🔧 IMPROVEMENTS

- **Automatic version management**: The package now handles its own version numbers automatically, making releases more reliable and reducing manual errors.

- **Modern dependency requirements**: Updated to require newer versions of core libraries (numpy ≥2.0, scipy ≥1.13.0) that provide better performance and fewer compatibility issues.

- **Enhanced development workflow**: Added automated code formatting and type checking that runs before commits, helping maintain code quality and catching issues earlier.

- **Better build reliability**: Improved the build system to prevent conflicts when using different Python environment managers, making installation more predictable.

### 🏗️ UNDER THE HOOD

- **Streamlined conda-forge integration**: Future PyPI releases will automatically trigger conda package updates, keeping both distribution channels in sync.

- **Updated CI pipeline**: Enhanced testing coverage and moved to Python 3.12 as the primary development version while maintaining compatibility with Python 3.12-3.14.

- **Improved project documentation**: Added status badges to quickly see build status, test coverage, and available versions at a glance.
