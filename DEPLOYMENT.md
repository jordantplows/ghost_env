# Deployment Guide

This guide explains how to build and deploy `ghost-env` to PyPI.

## Prerequisites

- Python 3.7+
- `pip`, `setuptools`, `wheel`, and `twine` installed
- PyPI account credentials

## Building the Package

1. **Install build dependencies:**
   ```bash
   pip install --upgrade build twine
   ```

2. **Build the package:**
   ```bash
   python -m build
   ```
   
   This creates `dist/` directory with:
   - `ghost-env-0.1.0.tar.gz` (source distribution)
   - `ghost-env-0.1.0-py3-none-any.whl` (wheel distribution)

## Testing the Build

Before uploading to PyPI, test the package locally:

```bash
# Install from the built wheel
pip install dist/ghost-env-0.1.0-py3-none-any.whl

# Or install from source distribution
pip install dist/ghost-env-0.1.0.tar.gz

# Test the installation
ghost-env --help
```

## Uploading to PyPI

### Test PyPI (for testing)

1. **Upload to Test PyPI:**
   ```bash
   twine upload --repository testpypi dist/*
   ```

2. **Test installation from Test PyPI:**
   ```bash
   pip install --index-url https://test.pypi.org/simple/ ghost-env
   ```

### Production PyPI

1. **Upload to PyPI:**
   ```bash
   twine upload dist/*
   ```

   You'll be prompted for your PyPI username and password. For better security, use an API token.

2. **Verify the upload:**
   Visit https://pypi.org/project/ghost-env/ to see your package.

## Version Management

Before each release:

1. Update the version in:
   - `pyproject.toml` (version field)
   - `setup.py` (version field)
   - `ghost_env/__init__.py` (__version__)

2. Update `CHANGELOG.md` with the new version and changes

3. Commit and tag the release:
   ```bash
   git add .
   git commit -m "Release version 0.1.0"
   git tag v0.1.0
   git push origin main --tags
   ```

## Post-Deployment

After successful deployment:

1. Verify installation works:
   ```bash
   pip install ghost-env
   ghost-env --help
   ```

2. Update the README if needed (e.g., installation instructions)

3. Announce the release (GitHub releases, etc.)

