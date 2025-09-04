# cultivator.agent (Psalm 006)

**Purpose:** turn Genesis from framework → living garden via rhythmic care.
**Ternary:** ⬛ REFRAIN (prune) · 🟫 TEND (micro-fix) · 🟦 AFFIRM (seed) → 🟩 FLOW.

## Install
```sh
chmod +x /genesis/agents/cultivator.agent
# cron (recommended)
crontab /genesis/cron/cultivator.cron
# or systemd (adjust user)
sudo install -m644 /genesis/systemd/cultivator.service /etc/systemd/system/cultivator@$(whoami).service
sudo systemctl enable --now cultivator@$(whoami).service
