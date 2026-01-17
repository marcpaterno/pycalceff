# Conda Recipe for pycalceff

This directory contains the conda recipe for building pycalceff as a conda package.

## Testing the Build Locally

To test building the conda package locally:

```bash
# Ensure conda-build is installed
conda install conda-build

# Build the package
conda build conda.recipe/

# Install the locally built package (optional)
conda install --use-local pycalceff
```

## Updating for New Releases

When releasing a new version:

1. Update the version to PyPI as usual
2. Regenerate the recipe with grayskull:
   ```bash
   grayskull pypi pycalceff
   mv pycalceff/meta.yaml conda.recipe/
   rmdir pycalceff
   ```
3. Test the build locally (see above)
4. Commit the updated recipe

After merging to main, the conda-forge bot will automatically:
- Detect the new PyPI release
- Create a PR to your feedstock with updated version and SHA256
- Build and publish to conda-forge after the PR is merged

## Notes

- The recipe is generated from PyPI metadata using grayskull
- Python version is constrained to >=3.12,<3.15 to match project requirements
- The package is built as `noarch: python` for platform independence
