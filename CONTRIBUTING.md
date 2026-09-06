# Contributing to python-library-template

This repository is the Copier template every bedrock-python library starts from, so a
change here lands in the next library generated — and, through `copier update`, in the
existing ones. Treat it like library code.

## What a change looks like

- Files under `template/` are what gets generated; `.jinja` files are rendered by Copier,
  everything else is copied as is. Copier's own variables come from `copier.yml`.
- `scripts/setup_repo.py` configures a freshly created GitHub repository to the org
  standard (ruleset on `master`, security settings, merge settings, topics). It is run
  once per new library and is also what keeps the existing repositories aligned.
- `NEW_LIBRARY_CHECKLIST.md.jinja` and `.claude/LIBRARY_CREATION.md` are the operator
  and agent instructions. Keep them in step with what the template actually does.

## Checking a change

Render the template and run the generated project's own gate — that is exactly what CI
does:

```bash
uvx --with jinja2-time copier copy --defaults --trust --vcs-ref HEAD \
  --data project_name=demo-lib --data project_slug=demo-lib --data package_name=demo_lib \
  --data project_description="Demo" --data author_name="You" --data author_email="you@example.com" \
  . /tmp/demo-lib
cd /tmp/demo-lib && uv sync --group dev --all-extras && make check && make test-unit && uv build
```

A change to `setup_repo.py` is checked by running it against a throwaway repository, or
against one of the org's repositories with `--help` first: the script is idempotent, so a
re-run on an already configured repository is a no-op.

## Commit messages

[Conventional Commits](https://www.conventionalcommits.org/): `feat:` for something new in
the generated project, `fix:` for a bug in it, `ci:` for workflow and setup-script
changes, `docs:` for the instructions. There is no release; the template is consumed by
git ref.

## Pull requests

Branch from `master`, open a PR against it. `master` takes pull requests only and needs
the "All checks passed" status.
