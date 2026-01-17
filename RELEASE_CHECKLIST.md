# Release Checklist for pycalceff v1.0.1

## Pre-Release Steps

- [x] All tests pass: `make check`
- [x] Version updated to 1.0.1 in `pyproject.toml`
- [x] CHANGELOG or release notes prepared (if applicable)
- [x] Documentation is up to date

## Build and Validate

- [x] Clean previous builds: `make clean`
- [x] Build distribution: `make build`
- [x] Check distribution: `make check-dist`
- [x] Test local installation: `make test-install`

## PyPI API Tokens Setup

1. [x] Get TestPyPI token: https://test.pypi.org/manage/account/token/
2. [ ] Get PyPI token: https://pypi.org/manage/account/token/
3. [x] Copy `.pypirc.template` to `~/.pypirc` and add tokens
4. [x] Set permissions: `chmod 600 ~/.pypirc`

## Test on TestPyPI

- [x] Upload to TestPyPI: `make publish-test`
- [x] Test installation from TestPyPI:
  ```bash
  pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ pycalceff
  pycalceff --version
  pycalceff --help
  ```

## Git Tagging (DO AFTER SUCCESSFUL TESTPYPI)

- [x] Commit all changes:
  ```bash
  git add -A
  git commit -m "Release v1.0.1 - Remove conda installation instructions"
  ```

- [x] Create annotated tag:
  ```bash
  git tag -a v1.0.1 -m "Release version 1.0.1"
  ```

- [x] Push commits and tags:
  ```bash
  git push origin master
  git push origin v1.0.1
  ```

## Publish to PyPI

- [ ] Upload to PyPI: `make publish`
- [ ] Verify on PyPI: https://pypi.org/project/pycalceff/
- [ ] Test installation from PyPI:
  ```bash
  pip install pycalceff
  pycalceff --version
  ```

## Post-Release

- [ ] Create GitHub release from tag v1.0.1
- [ ] Announce release (if applicable)
- [ ] Wait for conda-forge bot to detect new PyPI release and create PR to feedstock
- [ ] Review and merge conda-forge feedstock PR (automated update)

## conda-forge Distribution

After the PyPI release, the conda-forge bot will automatically:
1. Detect the new version on PyPI
2. Create a PR to your `pycalceff-feedstock` repository
3. Update version and SHA256 in the feedstock's meta.yaml
4. Run CI tests

Your action:
- Review the PR created by the conda-forge bot
- Merge it once CI passes
- The package will be published to conda-forge automatically

## Notes

- The version 1.0.1 is a patch release to fix README (removed conda instructions)
- Always test on TestPyPI before publishing to production PyPI
- PyPI uploads are permanent and cannot be deleted (only yanked)
- Tag format: `v1.0.1` (with 'v' prefix is conventional)
