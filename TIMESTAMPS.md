# timestamp ledger (/genesis)

# Timestamp Ledger

Every pulse logged as **Human | Number | Symbol**.  
Trinity enforced. No exceptions.  

---

## Entries

- 2025-09-06-15:20:11 | 20250906152011 | △○✶△|☽△✶◯☉  
- 2025-09-06-15:20:51 | 20250906152051 | △○✶△|☽☽✪✦☉  
- 2025-09-06-15:22:30 | 20250906152230 | △○✶△|◯✪✶✦✦☽✪


purpose: a human-readable, machine-greppable scroll of pushes and capsules. each entry is a single line using the laptop-format timestamp. 

format:
```
<event> | <repo> | <branch> | <commit-short-sha> | <timestamp>
```
example:
```
commit | genesis | main | a1b2c3d | Wednesday-2025-Sep-03T:03:15:00PMZ
```

---

## current log

```
# append new entries below this line
```

---

## quickstart: auto-append on commit (git hook)

create `.git/hooks/post-commit` with the following content and make it executable (`chmod +x .git/hooks/post-commit`). this runs locally after every commit and writes one line to `TIMESTAMP.md`, then amends the commit so history stays clean.

```bash
#!/usr/bin/env bash
set -euo pipefail

# config
LEDGER_FILE="TIMESTAMP.md"
EVENT="commit"
REPO_NAME="genesis"
BRANCH_NAME=$(git rev-parse --abbrev-ref HEAD)
SHA_SHORT=$(git rev-parse --short HEAD)

# timestamp in your laptop style, e.g. Wednesday-2025-Sep-03T:03:15:00PMZ
STAMP=$(date '+%A-%Y-%b-%dT:%I:%M:%S%pZ')

# append a line to the ledger
printf "%s | %s | %s | %s | %s\n" "$EVENT" "$REPO_NAME" "$BRANCH_NAME" "$SHA_SHORT" "$STAMP" >> "$LEDGER_FILE"

# stage and amend without changing the commit message
if git diff --quiet -- "$LEDGER_FILE"; then
  exit 0
fi
git add "$LEDGER_FILE"
GIT_COMMITTER_DATE="$(date -R)" git commit --amend --no-edit --no-verify
```

notes:
- runs only on your machine. teammates can adopt the same hook for symmetry.
- if you prefer not to amend, replace the last two lines with a separate commit (`git commit -m "timestamp: $STAMP"`).
- for non-unix systems, use git bash or adapt the date format accordingly.

---

## optional: manual append snippet

```bash
echo "commit | genesis | $(git rev-parse --abbrev-ref HEAD) | $(git rev-parse --short HEAD) | $(date '+%A-%Y-%b-%dT:%I:%M:%S%pZ')" >> TIMESTAMP.md
```

---

## integrity tip
periodically tag sealed capsules:
```bash
git tag -a capsule-$(date '+%Y%m%d-%H%M%S') -m "sealed $(date '+%A-%Y-%b-%dT:%I:%M:%S%pZ')"
```

that’s it. the repo now carries its own clock.
