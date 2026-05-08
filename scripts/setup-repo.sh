#!/usr/bin/env bash
# Usage: bash scripts/setup-repo.sh <org/repo>
# Example: bash scripts/setup-repo.sh bedrock-python/my-new-lib
#
# Run AFTER the first CI pass so "All checks passed" exists in GitHub.

set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "Usage: $0 <org/repo>"
  exit 1
fi

REPO="$1"

echo "Setting up $REPO..."

# ── Environments ─────────────────────────────────────────────────────────────
echo "  → Creating environments..."
gh api "repos/$REPO/environments/pypi" -X PUT --silent
gh api "repos/$REPO/environments/github-pages" -X PUT --silent

# ── GitHub Pages ─────────────────────────────────────────────────────────────
echo "  → Enabling GitHub Pages (GitHub Actions source)..."
gh api "repos/$REPO/pages" -X POST \
  -H "Accept: application/vnd.github+json" \
  -f build_type=workflow 2>/dev/null || echo "     (Pages may already be enabled — skipping)"

# ── Actions: allow creating PRs ──────────────────────────────────────────────
echo "  → Allowing Actions to create pull requests..."
gh api "repos/$REPO/actions/permissions/workflow" -X PUT \
  -f default_workflow_permissions=write \
  -f can_approve_pull_request_reviews=true

# ── Branch protection ─────────────────────────────────────────────────────────
echo "  → Setting branch protection on master..."
gh api "repos/$REPO/branches/master/protection" -X PUT \
  -H "Accept: application/vnd.github+json" \
  --input - <<'EOF'
{
  "required_status_checks": {
    "strict": true,
    "checks": [{ "context": "All checks passed" }]
  },
  "enforce_admins": false,
  "required_pull_request_reviews": null,
  "restrictions": null,
  "allow_force_pushes": false,
  "allow_deletions": false
}
EOF

echo ""
echo "✓ Done!"
echo ""
echo "Remaining manual steps:"
echo "  1. PyPI Trusted Publisher → https://pypi.org/manage/account/publishing/"
echo "     project: ${REPO##*/} | org: ${REPO%%/*} | repo: ${REPO##*/} | workflow: publish.yml | env: pypi"
echo "  2. CODECOV_TOKEN → https://app.codecov.io/gh/$REPO"
echo "     GitHub repo → Settings → Secrets → Actions → CODECOV_TOKEN"
