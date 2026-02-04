# Making the First Release to conda-forge

## Summary

Your project is now set up for conda-forge distribution with automated updates. Here's what has been done and what you need to do next.

## What Has Been Done

1. ✅ Generated conda recipe using grayskull
2. ✅ Created `conda.recipe/` directory with `meta.yaml` and README
3. ✅ Updated main README.md with conda installation instructions
4. ✅ Added Makefile targets for conda operations
5. ✅ Created comprehensive conda-forge setup guide
6. ✅ Updated release checklist with conda-forge steps
7. ✅ Added .gitignore entries for conda build artifacts

## Files Created/Modified

- `conda.recipe/meta.yaml` - Conda recipe for building the package
- `conda.recipe/README.md` - Instructions for maintaining the recipe
- `CONDA_FORGE_SETUP.md` - Complete guide for initial conda-forge submission
- `README.md` - Added conda installation instructions
- `RELEASE_CHECKLIST.md` - Added conda-forge automation notes
- `Makefile` - Added `conda-recipe` and `conda-build` targets
- `.gitignore` - Added conda build artifacts

## Next Steps: Initial conda-forge Submission

Follow the detailed instructions in **CONDA_FORGE_SETUP.md**. Here's the quick version:

### 1. Test Locally (Optional but Recommended)

```bash
# Install conda-build if not already installed
conda install conda-build

# Test building the package
# Test building the package
make conda-smoke-test

# If successful, test installation
conda install --use-local pycalceff
pycalceff --help
pycalceff --version
```

### 2. Submit to conda-forge

```bash
# Fork staged-recipes on GitHub
# https://github.com/conda-forge/staged-recipes

# Clone your fork
git clone https://github.com/YOUR_USERNAME/staged-recipes.git
cd staged-recipes

# Create branch
git checkout -b add-pycalceff

# Copy recipe
cp -r /path/to/pycalceff/conda.recipe recipes/pycalceff

# Commit and push
git add recipes/pycalceff
git commit -m "Add pycalceff recipe"
git push origin add-pycalceff

# Create PR on GitHub
# https://github.com/conda-forge/staged-recipes
```

### 3. Wait for Review

- CI will run automated tests
- Reviewers will check the recipe
- Address any feedback
- Once approved and merged, your feedstock is created

### 4. Installation Available

After merge, users can install with:

```bash
conda install -c conda-forge pycalceff
# or
mamba install -c conda-forge pycalceff
```

## Future Releases (Automated)

After the initial setup, every new PyPI release triggers automation:

1. **You**: Release new version to PyPI (as usual)
2. **conda-forge bot**: Detects new version within hours
3. **conda-forge bot**: Creates PR to your feedstock with:
   - Updated version
   - Updated SHA256 hash
4. **You**: Review and merge the bot's PR
5. **conda-forge**: Publishes new version automatically

## Useful Commands

```bash
# Build conda package locally (for testing)
make conda-smoke-test

# Show all Makefile commands
make help
```

## Questions?

- See `CONDA_FORGE_SETUP.md` for complete details
- See `conda.recipe/README.md` for recipe maintenance
- conda-forge docs: https://conda-forge.org/docs/

## Summary

The hard work is done! Just follow CONDA_FORGE_SETUP.md to submit your initial PR to conda-forge. After that, all future releases are automated.
