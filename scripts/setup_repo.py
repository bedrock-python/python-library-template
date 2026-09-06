"""One-time GitHub repository setup for bedrock-python libraries. Idempotent: safe to re-run.

Usage:
    python scripts/setup_repo.py <org/repo> [--topics a,b,c]

Run AFTER the first CI pass: the master ruleset requires the "All checks passed"
status, and a required check that never reports would block every merge. When the
check is not found on the default branch the rule is left out and a warning printed;
re-run once CI has been green.

Needs the gh CLI, authenticated with admin rights on the repository.
"""

from __future__ import annotations

import argparse
import base64
import json
import re
import subprocess
import sys
import tomllib

RULESET_NAME = "master-rules"
REQUIRED_CHECK = "All checks passed"
MAX_TOPICS = 20


def gh(*args: str, payload: dict | list | None = None, ok: tuple[int, ...] = ()) -> dict | list | str | None:
    """Call `gh api`; return parsed JSON. HTTP statuses in `ok` are tolerated (returns None)."""
    cmd = ["gh", "api", *args]
    if payload is not None:
        cmd += ["--input", "-"]
    result = subprocess.run(cmd, input=json.dumps(payload) if payload is not None else None, capture_output=True, text=True)
    if result.returncode != 0:
        status = re.search(r"HTTP (\d{3})", result.stderr)
        if status and int(status.group(1)) in ok:
            return None
        sys.exit(f"  [FAIL] gh api {' '.join(args)}\n    {result.stderr.strip()}")
    out = result.stdout.strip()
    if not out:
        return None
    try:
        return json.loads(out)
    except json.JSONDecodeError:
        return out


def step(title: str) -> None:
    print(f"  -> {title}")


def topics_from_pyproject(repo: str, default_branch: str) -> list[str]:
    data = gh(f"repos/{repo}/contents/pyproject.toml?ref={default_branch}", ok=(404,))
    if not data:
        return []
    project = tomllib.loads(base64.b64decode(data["content"]).decode()).get("project", {})
    return list(project.get("keywords", []))


def sanitize_topic(raw: str) -> str | None:
    topic = re.sub(r"[^a-z0-9-]+", "-", raw.strip().lower()).strip("-")
    return topic[:50] or None


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("repo", help="org/repo")
    parser.add_argument("--topics", default="", help="comma-separated topics added on top of pyproject keywords")
    args = parser.parse_args()
    repo = args.repo
    org, name = repo.split("/", 1)

    meta = gh(f"repos/{repo}")
    default_branch = meta["default_branch"]
    print(f"Setting up {repo} (default branch: {default_branch})\n")

    def has_workflow(name: str) -> bool:
        return gh(f"repos/{repo}/contents/.github/workflows/{name}?ref={default_branch}", ok=(404,)) is not None

    # Environments and Pages follow the workflows that use them, so a repository
    # without a publish or docs workflow (the template itself) gets neither.
    pages = None
    if has_workflow("publish.yml"):
        step("Environment: pypi (Trusted Publishing)")
        gh(f"repos/{repo}/environments/pypi", "-X", "PUT")
    if has_workflow("docs.yml"):
        step("Environment: github-pages; Pages built by Actions")
        gh(f"repos/{repo}/environments/github-pages", "-X", "PUT")
        pages = gh(f"repos/{repo}/pages", ok=(404,))
        if pages is None:
            gh(f"repos/{repo}/pages", "-X", "POST", payload={"build_type": "workflow"}, ok=(409,))
            pages = gh(f"repos/{repo}/pages", ok=(404,))

    step("Actions: workflows get a read-only token unless they ask for more; Release Please may open PRs")
    gh(f"repos/{repo}/actions/permissions/workflow", "-X", "PUT",
       payload={"default_workflow_permissions": "read", "can_approve_pull_request_reviews": True})

    step("Repository: squash or merge commits only, branches deleted on merge, no wiki/projects, docs as homepage")
    settings: dict = {
        "allow_squash_merge": True,
        "allow_merge_commit": True,
        "allow_rebase_merge": False,
        "delete_branch_on_merge": True,
        "has_wiki": False,
        "has_projects": False,
    }
    if pages and not meta.get("homepage"):
        settings["homepage"] = f"https://{org}.github.io/{name}/"
    gh(f"repos/{repo}", "-X", "PATCH", payload=settings)

    step("Security: secret scanning + push protection, Dependabot alerts + security updates, private reporting")
    gh(f"repos/{repo}", "-X", "PATCH", payload={"security_and_analysis": {
        "secret_scanning": {"status": "enabled"},
        "secret_scanning_push_protection": {"status": "enabled"},
    }})
    gh(f"repos/{repo}/vulnerability-alerts", "-X", "PUT")
    gh(f"repos/{repo}/automated-security-fixes", "-X", "PUT")
    gh(f"repos/{repo}/private-vulnerability-reporting", "-X", "PUT")

    step("Topics: pyproject keywords + python (existing topics kept)")
    wanted = ["python", *topics_from_pyproject(repo, default_branch), *args.topics.split(",")]
    topics: list[str] = list(meta.get("topics") or [])
    for raw in wanted:
        topic = sanitize_topic(raw)
        if topic and topic not in topics:
            topics.append(topic)
    gh(f"repos/{repo}/topics", "-X", "PUT", payload={"names": topics[:MAX_TOPICS]})

    step(f"Ruleset '{RULESET_NAME}' on {default_branch}: no deletion, no force-push, pull requests only")
    check_runs = gh(f"repos/{repo}/commits/{default_branch}/check-runs", ok=(404, 422)) or {}
    has_check = any(run["name"] == REQUIRED_CHECK for run in check_runs.get("check_runs", []))
    rules: list[dict] = [
        {"type": "deletion"},
        {"type": "non_fast_forward"},
        {"type": "pull_request", "parameters": {
            "required_approving_review_count": 0,
            "dismiss_stale_reviews_on_push": False,
            "require_code_owner_review": False,
            "require_last_push_approval": False,
            "required_review_thread_resolution": False,
            "allowed_merge_methods": ["merge", "squash"],
        }},
    ]
    if has_check:
        rules.append({"type": "required_status_checks", "parameters": {
            "strict_required_status_checks_policy": False,
            "do_not_enforce_on_create": False,
            "required_status_checks": [{"context": REQUIRED_CHECK}],
        }})
    else:
        print(f"     [WARN] no '{REQUIRED_CHECK}' check on {default_branch} yet — required-check rule left out; re-run after CI is green")
    ruleset = {
        "name": RULESET_NAME,
        "target": "branch",
        "enforcement": "active",
        "bypass_actors": [],
        "conditions": {"ref_name": {"include": ["~DEFAULT_BRANCH"], "exclude": []}},
        "rules": rules,
    }
    existing = next((r for r in gh(f"repos/{repo}/rulesets") or [] if r["name"] == RULESET_NAME), None)
    if existing:
        gh(f"repos/{repo}/rulesets/{existing['id']}", "-X", "PUT", payload=ruleset)
    else:
        gh(f"repos/{repo}/rulesets", "-X", "POST", payload=ruleset)

    step("Classic branch protection: removed (the ruleset replaces it)")
    if gh(f"repos/{repo}/branches/{default_branch}/protection", ok=(404,)) is not None:
        gh(f"repos/{repo}/branches/{default_branch}/protection", "-X", "DELETE")

    print("\n[OK] Done.\n")
    print("Remaining manual steps:")
    print("  1. PyPI Trusted Publisher -> https://pypi.org/manage/account/publishing/")
    print(f"     project: {name} | owner: {org} | repository: {name} | workflow: publish.yml | environment: pypi")
    print(f"  2. CODECOV_TOKEN -> https://app.codecov.io/gh/{repo} -> repo Settings -> Secrets -> Actions")


if __name__ == "__main__":
    main()
