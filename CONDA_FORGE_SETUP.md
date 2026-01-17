# Initial conda-forge Submission Guide

This guide walks you through submitting pycalceff to conda-forge for the first time. After this initial setup, future releases will be automated.

## Prerequisites

1. **GitHub account** with access to fork repositories
2. **Package already on PyPI** (pycalceff is already there)
3. **PyPI username** ready (for the recipe maintainer field)

## Step-by-Step Instructions

### 1. Fork the staged-recipes Repository

1. Go to https://github.com/conda-forge/staged-recipes
2. Click the "Fork" button in the top right
3. Fork to your personal GitHub account

### 2. Clone Your Fork

```bash
git clone https://github.com/YOUR_USERNAME/staged-recipes.git
cd staged-recipes
```

### 3. Create a New Branch

```bash
git checkout -b add-pycalceff
```

### 4. Copy Your Recipe

```bash
# Copy the recipe from your pycalceff project
cp -r /path/to/pycalceff/conda.recipe/meta.yaml recipes/pycalceff/
```

Or manually create `recipes/pycalceff/meta.yaml` with the contents from `conda.recipe/meta.yaml` in this project.

### 5. Review and Edit the Recipe

Open `recipes/pycalceff/meta.yaml` and verify:

- **version**: Should match the latest PyPI version
- **sha256**: Should match the PyPI tarball hash (grayskull does this automatically)
- **license**: BSD-3-Clause
- **maintainers**: Your GitHub username(s)
- **homepage**: https://github.com/marcpaterno/pycalceff

The recipe should look like this:

```yaml
{% set name = "pycalceff" %}
{% set version = "1.0.1" %}

package:
  name: {{ name|lower }}
  version: {{ version }}

source:
  url: https://pypi.org/packages/source/{{ name[0] }}/{{ name }}/pycalceff-{{ version }}.tar.gz
  sha256: 81eb456481147bee1dfdb5f2a818b0169fa18f986071c5dc6556a294d24b74da

build:
  entry_points:
    - pycalceff = pycalceff.main:app
  noarch: python
  script: {{ PYTHON }} -m pip install . -vv --no-deps --no-build-isolation
  number: 0

requirements:
  host:
    - python >=3.12,<3.15
    - setuptools >=61.0
    - pip
  run:
    - python >=3.12,<3.15
    - typer
    - rich
    - scipy

test:
  imports:
    - pycalceff
  commands:
    - pip check
    - pycalceff --help
  requires:
    - pip

about:
  home: https://github.com/marcpaterno/pycalceff
  summary: Calculate binomial efficiencies and their uncertainties
  license: BSD-3-Clause
  license_file: LICENSE

extra:
  recipe-maintainers:
    - marcpaterno
```

### 6. Commit Your Changes

```bash
git add recipes/pycalceff/meta.yaml
git commit -m "Add pycalceff recipe"
```

### 7. Push to Your Fork

```bash
git push origin add-pycalceff
```

### 8. Create a Pull Request

1. Go to https://github.com/conda-forge/staged-recipes
2. GitHub should show a banner suggesting you create a PR from your branch
3. Click "Compare & pull request"
4. Fill in the PR template:
   - Title: "Add pycalceff"
   - Description: Brief description of the package
   - Check all the boxes in the checklist
5. Submit the PR

### 9. Wait for CI and Reviews

The conda-forge CI will automatically:
- Build your package on Linux, macOS, and Windows
- Run the tests you specified
- Check for common issues

Reviewers (conda-forge members) will:
- Check the recipe quality
- Suggest improvements if needed
- Approve the PR once everything looks good

This usually takes a few hours to a few days.

### 10. PR is Merged

Once approved and merged:
- A new repository `pycalceff-feedstock` is created under the conda-forge organization
- You are automatically added as a maintainer with write access
- The package is built and published to conda-forge
- Users can install with: `conda install -c conda-forge pycalceff`

## After Initial Setup: Future Releases

Once your feedstock exists, future releases are automated:

1. **You**: Release new version to PyPI (as usual)
2. **conda-forge bot**: Detects the new PyPI version within hours
3. **conda-forge bot**: Creates a PR to your feedstock with:
   - Updated version number
   - Updated SHA256 hash
   - Any necessary dependency updates
4. **You**: Review the bot's PR (usually just merge it)
5. **conda-forge**: Builds and publishes the new version automatically

## Troubleshooting

### Build Fails

- Check the CI logs for error messages
- Common issues:
  - Missing dependencies in `run` requirements
  - Python version constraints too strict
  - Test commands fail

### Need to Update Recipe

If you need to make changes after submitting:
- Push additional commits to your branch
- CI will re-run automatically

### Questions?

- Ask in the PR - conda-forge reviewers are helpful
- Check conda-forge docs: https://conda-forge.org/docs/

## Testing Locally Before Submission

To test your recipe locally before submitting:

```bash
# Install conda-build
conda install conda-build

# Build the package
conda build recipes/pycalceff/

# If successful, test installation
conda install --use-local pycalceff
pycalceff --help
pycalceff --version
```

This ensures your recipe works before submitting to conda-forge.

## Summary

1. Fork staged-recipes
2. Add your recipe to `recipes/pycalceff/`
3. Submit PR
4. Wait for reviews and CI
5. Once merged, you're done!
6. Future releases are automated via conda-forge bot

The initial setup takes some time, but afterwards every PyPI release automatically triggers a conda-forge update.
