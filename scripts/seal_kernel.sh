#!/usr/bin/env bash
set -euo pipefail

# Enforce branch and author constraints, then stamp short-sha into ledger
PRIMARY_BRANCH="genesis"
ALLOWED_EMAIL="rfi.irfos@gmail.com"
TIMESTAMP_ISO="Wednesday-2025-Sep-03T:08:27:42PMZ"

# Check current branch
current_branch="$(git rev-parse --abbrev-ref HEAD)"
if [[ "$current_branch" != "$PRIMARY_BRANCH" ]]; then
  echo "❌ Must commit on branch '$PRIMARY_BRANCH' (current: $current_branch)"
  exit 1
fi

# Check author email of the pending commit (or default config if none yet)
author_email="$(git config user.email || true)"
if [[ "$author_email" != "$ALLOWED_EMAIL" ]]; then
  echo "❌ Author email must be '$ALLOWED_EMAIL' (current git config: '$author_email')"
  echo "   Run: git config user.email \"$ALLOWED_EMAIL\""
  exit 1
fi

# If there are changes staged, commit with a default message (optional)
if ! git diff --cached --quiet; then
  git commit -m "genesis kernel ceremony seat | ${TIMESTAMP_ISO}"
fi

short_sha="$(git rev-parse --short HEAD)"

# Replace <short-sha> placeholders
for f in TIMESTAMP.md rod_staff.md RELEASE_NOTES.md; do
  if [[ -f "$f" ]]; then
    sed -i.bak "s/<short-sha>/${short_sha}/g" "$f" && rm -f "$f.bak"
  fi
done

echo "✅ Stamped short-sha ${short_sha} into TIMESTAMP.md, rod_staff.md, RELEASE_NOTES.md"
echo "   You may now push: git push origin ${PRIMARY_BRANCH}"
