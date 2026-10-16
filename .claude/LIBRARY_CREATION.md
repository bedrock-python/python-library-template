# Instructions for AI Agents: Creating New Python Libraries

When creating a new Python library from this template, follow these rules strictly:

## 1. Git Commits and Co-Authors

**NEVER add AI agents as co-authors in commits.**

❌ **WRONG:**
```
feat: initial release

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
```

✅ **CORRECT:**
```
feat: initial release

Comprehensive library for X with Y features.
```

**Why:** AI co-authorship appears in GitHub contributors and cannot be easily removed.

## 2. What Lives Where

`scripts/setup_repo.py` and this file belong to the template repository. A render
contains neither, so there is nothing of the kind to delete from a new library. The
render does contain `NEW_LIBRARY_CHECKLIST.md`, the operator's checklist; it is deleted
once its steps are done.

## 3. Repository Creation Workflow

When creating a new library repository:

1. **Generate from template**:
   ```bash
   uvx --with jinja2-time copier copy --trust gh:bedrock-python/python-library-template my-library
   ```
2. **Make initial commit WITHOUT Co-Authored-By**:
   ```bash
   git init -b master
   git add .
   git commit -m "feat: initial release

   Comprehensive library for X with:
   - Feature A
   - Feature B
   - Full documentation and tests"
   ```
3. **Create the GitHub repository and push**:
   ```bash
   gh repo create org/repo-name --public --source . --push
   ```
4. **After the first CI pass, run the setup script from the template repository**:
   ```bash
   python /path/to/python-library-template/scripts/setup_repo.py org/repo-name
   ```

## 4. Initial Release Version

- `.release-please-manifest.json` starts at `"0.0.0"`
- First `feat:` commit → Release Please creates v0.1.0
- First `fix:` commit → Release Please creates v0.0.1

## 5. The Agents Page

`docs/agents.md` ships as a skeleton with `TODO` markers. Fill it in before the initial
commit — it is the page a person hands to a coding assistant instead of the whole site,
so an empty one is a broken promise and a wrong one teaches an API that does not exist.

Write it from the source you just wrote, not from the README: every name, argument,
default and return type has to be one that exists, and every name a caller is told to
import has to be importable. Check that before committing:

```bash
uv run python -c "import <package>; [getattr(<package>, n) for n in ('Name', ...)]"
```

`https://bedrock-python.github.io/pg-partsmith/agents/` is the worked example. The
sections that carry the weight are **Scope** (what it does not do stops a model
inventing features), **Rules that hold or break the code** and **Common mistakes**.
Delete a section that has nothing true to say rather than padding it.

Keep the `<!-- ... -->` guidance comment out of the committed page.

## 6. Clean Repository Checklist

Before pushing the initial commit, verify:

- [ ] No `Co-Authored-By:` in commit messages
- [ ] No backup files (e.g., `.coverage (копия...)`, `file (copy).py`)
- [ ] No cache files (`.mypy_cache`, `.ruff_cache`, `__pycache__`) - should be in `.gitignore`
- [ ] `.release-please-manifest.json` contains `"0.0.0"`
- [ ] `docs/agents.md` written from the real API, no `TODO` markers, guidance comment removed

## 7. PyPI Publication

Before merging the Release Please PR:

1. Configure PyPI Trusted Publisher at https://pypi.org/manage/account/publishing/
   - Project name: `library-name`
   - Owner: `org-name`
   - Repository: `repo-name`
   - Workflow: `publish.yml`
   - Environment: `pypi`

2. Merge Release Please PR → automatic publication to PyPI

## 8. Common Mistakes to Avoid

❌ Including AI agents in commits
❌ Starting with version `0.1.0` instead of `0.0.0`
❌ Committing backup/cache files
❌ Creating multiple commits before initial push (messy history)
❌ Shipping `docs/agents.md` with its `TODO` markers still in it

## 9. Summary

**Clean initial commit = Clean repository forever**

- One commit for initial release
- No AI co-authors
- No template-specific files
- Start from version 0.0.0
- Run the setup script from the template repository

Following these rules ensures a clean, professional repository from day one.
