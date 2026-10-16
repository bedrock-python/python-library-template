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
   Idempotent. Sets the org standard: a `pypi` environment only `master` may deploy to,
   the `github-pages` environment and Pages,
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

## Pulling template changes into a library

A render records its answers and the template commit it came from in
`.copier-answers.yml`. Commit that file and leave it to Copier. To bring a library up to
the template's `master`, from the library's clean working tree:

```bash
uvx --with jinja2-time copier update --trust --defaults
```

Copier applies what changed in the template since the recorded commit as a three-way
merge with the library's own edits, leaves conflicts as inline markers, and moves
`_commit` forward. A file the library deleted, such as the checklist, stays deleted.

A library rendered before the answers file existed needs one written by hand first: the
answers it was rendered with, `_src_path: gh:bedrock-python/python-library-template`,
and as `_commit` the template commit it was rendered from, or the closest one.

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
