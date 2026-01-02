# Release Checklist for pycalceff v1.0.0

## Pre-Release Steps

- [ ] All tests pass: `make check`
- [ ] Version updated to 1.0.0 in `pyproject.toml`
- [ ] CHANGELOG or release notes prepared (if applicable)
- [ ] Documentation is up to date

## Build and Validate

- [ ] Clean previous builds: `make clean`
- [ ] Build distribution: `make build`
- [ ] Check distribution: `make check-dist`
- [ ] Test local installation: `make test-install`

## PyPI API Tokens Setup

1. Get TestPyPI token: https://test.pypi.org/manage/account/token/
2. Get PyPI token: https://pypi.org/manage/account/token/
3. Copy `.pypirc.template` to `~/.pypirc` and add tokens
4. Set permissions: `chmod 600 ~/.pypirc`

## Test on TestPyPI

- [ ] Upload to TestPyPI: `make publish-test`
- [ ] Test installation from TestPyPI:
  ```bash
  pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ pycalceff
  pycalceff --version
  pycalceff --help
  ```

## Git Tagging (DO AFTER SUCCESSFUL TESTPYPI)

- [ ] Commit all changes:
  ```bash
  git add -A
  git commit -m "Release v1.0.0"
  ```

- [ ] Create annotated tag:
  ```bash
  git tag -a v1.0.0 -m "Release version 1.0.0"
  ```

- [ ] Push commits and tags:
  ```bash
  git push origin main
  git push origin v1.0.0
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

- [ ] Create GitHub release from tag v1.0.0
- [ ] Announce release (if applicable)

## Notes

- The version 1.0.0 indicates this is the first stable production release
- Always test on TestPyPI before publishing to production PyPI
- PyPI uploads are permanent and cannot be deleted (only yanked)
- Tag format: `v1.0.0` (with 'v' prefix is conventional)
