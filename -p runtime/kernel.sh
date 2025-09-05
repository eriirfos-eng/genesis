#!/usr/bin/env bash
set -Eeuo pipefail

# Skybase kernel launcher
# - cd into skybase-runtime
# - optional: choose mode via arg (remote|local)
# - runs chat.py with your config.env (Python loads it via dotenv)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

MODE="${1:-remote}"  # default remote
export SKYBASE_MODE="$MODE"

echo "[kernel] Skybase launcher"
echo "[kernel] PWD=$(pwd)"
echo "[kernel] MODE=$SKYBASE_MODE"

# sanity checks
if [[ ! -f "config.env" ]]; then
  echo "[kernel] ERROR: config.env not found in $(pwd)" >&2
  exit 1
fi

# optional: quick peek at token presence (masked)
if grep -q '^ALBERT=' config.env; then
  echo "[kernel] ALBERT token present in config.env"
else
  echo "[kernel] WARNING: ALBERT token missing in config.env"
fi

# run
if command -v python3 >/dev/null 2>&1; then
  PY=python3
elif command -v python >/dev/null 2>&1; then
  PY=python
else
  echo "[kernel] ERROR: python not found" >&2
  exit 1
fi

# Uncomment to use a venv (kept minimal to avoid surprise installs)
# if [[ ! -d .venv ]]; then
#   echo "[kernel] creating .venv..."
#   "$PY" -m venv .venv
# fi
# source .venv/bin/activate
# pip install -q -r requirements.txt || true

"$PY" chat.py "$@"
# git autosync every 60s in background
while true; do
    cd /home/eri-irfos/Desktop/skybase-runtime
    git pull --rebase
    git add system_instructions.txt
    git commit -m "autosync: updated system_instructions" || true
    git push || true
    sleep 60
done &
