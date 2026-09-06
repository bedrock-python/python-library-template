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
| `initial_version` | Initial version | `0.0.0` |

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
2. **Configure repo** (after the first CI pass, then delete the script):
   ```bash
   python scripts/setup_repo.py bedrock-python/my-library
   git rm scripts/setup_repo.py .claude/LIBRARY_CREATION.md
   ```
   Idempotent. Sets the org standard: `pypi`/`github-pages` environments and Pages,
   read-only workflow tokens, squash/merge-commit only with branches deleted on merge,
   secret scanning + push protection + Dependabot security updates + private
   vulnerability reporting, topics from `pyproject` keywords, and a `master` ruleset
   (pull requests only, no force-push or deletion, "All checks passed" required).
3. **Push** (⚠️ **no** `Co-Authored-By:` in commits!):
   ```bash
   git init && git add . && git commit -m "feat: initial release" && git push -u origin master
   ```
4. Set up PyPI Trusted Publisher at pypi.org/manage/account/publishing/
5. Add `CODECOV_TOKEN` secret in repo Settings → Secrets → Actions

## For AI Agents

See [`.claude/LIBRARY_CREATION.md`](.claude/LIBRARY_CREATION.md) for important rules:
- **Never** add AI agents as co-authors in commits
- Delete `scripts/setup_repo.py` before initial commit
- Start with version `0.0.0` (Release Please creates `0.1.0`)

## What's included

- `pyproject.toml` — uv + hatchling + ruff + mypy + pytest
- `Makefile` — fmt, check, test-unit, test-integration, test, build, docs-serve, docs-build
- `.github/workflows/` — CI (lint + unit + integration), publish to PyPI, deploy docs, Release Please
- `.github/` — dependabot, issue templates, PR template
- `docs/` — zensical (MkDocs Material) setup with mkdocstrings, a **Copy page** control that
  hands any page to an LLM as Markdown, and `docs/agents.md`, the one-page brief for coding
  assistants (ships as a skeleton — fill it in)
- `.pre-commit-config.yaml` — ruff, mypy, conventional commits
- `release-please-config.json` — automated semver + CHANGELOG generation
