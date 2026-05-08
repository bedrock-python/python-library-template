# python-library-template

Copier template for Python libraries in the bedrock-python organization.

## Usage

```bash
# Install copier
pip install copier

# Create a new library
copier copy gh:bedrock-python/python-library-template my-new-lib
cd my-new-lib
```

Copier will prompt for:

| Variable | Description | Example |
|---|---|---|
| `project_name` | Display name | `my-library` |
| `project_slug` | PyPI package name (kebab-case) | `my-library` |
| `package_name` | Python import name (snake_case) | `my_library` |
| `project_description` | One-line description | `A great library` |
| `author_name` | Author full name | `Alex Shalaev` |
| `author_email` | Author email | `you@example.com` |
| `github_org` | GitHub org or username | `bedrock-python` |
| `python_min_version` | Minimum Python version | `3.11` |
| `initial_version` | Initial version | `0.1.0` |

## After generation

```bash
# Install dependencies
uv sync --group dev

# Install pre-commit hooks
uv run pre-commit install --hook-type commit-msg

# Verify everything works
make check
```

Then:
1. Create a GitHub repo: `gh repo create bedrock-python/my-library --public`
2. Push: `git init && git add . && git commit -m "feat: initial release" && git push -u origin master`
3. Set up PyPI Trusted Publisher at pypi.org/manage/account/publishing/
4. Enable GitHub Pages in repo Settings → Pages → Source: GitHub Actions
5. Add `CODECOV_TOKEN` secret in repo Settings → Secrets → Actions

## What's included

- `pyproject.toml` — uv + hatchling + ruff + mypy + pytest
- `Makefile` — fmt, check, test-unit, test-integration, test, build, docs-serve, docs-build
- `.github/workflows/` — CI (lint + unit + integration), publish to PyPI, deploy docs, Release Please
- `.github/` — dependabot, issue templates, PR template
- `docs/` — zensical (MkDocs Material) setup with mkdocstrings
- `.pre-commit-config.yaml` — ruff, mypy, conventional commits
- `release-please-config.json` — automated semver + CHANGELOG generation
