#!/usr/bin/env bash
# health sampling + status rendering (no jq required)

compute_health_snapshot() {
  local root="$1"
  local files lines stale ok warn crit
  files=$(find "$root" -type f ! -path "*/.git/*" | wc -l | tr -d ' ')
  lines=$(find "$root" -type f -maxdepth 3 -name "*.md" -exec wc -l {} + | awk '{s+=$1} END{print s+0}')
  stale=$(find "$root" -type f -name "*.md" -mtime +14 | wc -l | tr -d ' ')
  ok=$(( files > 10 ? 1 : 0 ))
  warn=$(( stale > 5 ? 1 : 0 ))
  crit=$(( files == 0 ? 1 : 0 ))
  # simple pass ratio
  pass=$(( ok + (warn==0 ? 1 : 0) + (crit==0 ? 1 : 0) ))
  total=3
  ratio=$(awk -v p="$pass" -v t="$total" 'BEGIN{printf "%.2f", p/t}')
  cat <<EOF
{
  "files": $files,
  "lines_md": $lines,
  "stale_md": $stale,
  "ok": $ok,
  "warn": $warn,
  "crit": $crit,
  "pass_ratio": $ratio,
  "timestamp": "$(date -u +%FT%TZ)"
}
EOF
}

health_is_critical() { grep -q '"crit": 1' "${1:-/dev/stdin}"; }
health_needs_tend()  { grep -q '"warn": 1' "${1:-/dev/stdin}"; }
health_is_flowing()  { awk -F: '/pass_ratio/ {gsub(/[ ,}]/,"",$2); if ($2+0 >= 0.67) exit 0; else exit 1}' "${1:-/dev/stdin}"; }

render_status_card() {
  local f="$1" pass_ratio moon name
  moon="$(moon_phase_symbol)"; name="$(moon_phase_name)"
  pass_ratio=$(awk -F: '/pass_ratio/ {gsub(/[ ,}]/,"",$2); print $2}' "$f")
  local flag="🟫"
  awk -v pr="$pass_ratio" 'BEGIN{if(pr>=0.67) print "🟩"; else if(pr>=0.34) print "🟫"; else print "🟥";}' | read -r flag
  cat <<EOF
cultivator.status
time: $(date -u +%FT%TZ)
phase: $name $moon
health: $flag (pass_ratio=$pass_ratio)
EOF
}

show_status_line() {
  local f="$1" flag="🟫"
  if health_is_critical "$f"; then flag="🟥"
  elif health_is_flowing "$f"; then flag="🟩"
  else flag="🟫"
  fi
  echo "status: $flag $(moon_phase_symbol) $(date -u +%FT%TZ)"
}

perform_offering() {
  # Psalm 003 — symbolic offering: rotate tiny log slice as 'first fruits'
  local ratio="${1:-0.10}" root="${2}" logd="${3}"
  local target="$logd/offering.$(date -u +%Y%m%d).log"
  echo "$(date -u +%FT%TZ) offering: ratio=${ratio}, root=${root}" >> "$target"
}
