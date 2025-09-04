#!/usr/bin/env bash
# rod_staff helpers

ensure_rod_staff_template() {
  local file="$1"
  [[ -f "$file" ]] && return 0
  cat > "$file" <<'EOF'
# rod_staff ledger

**purpose:** daily two-point ritual to stabilize the lattice through paired action: **rod = boundary (⬛)**, **staff = guidance (🟦)**. optional **valley = uncertainty (🟫)**. keep entries short. one breath each.

**ternary map:** rod = -1, valley = 0, staff = +1. when balanced → 🟩 flow.

## daily template (compact one-liner)
rod | staff | valley | <weekday>-<YYYY>-<Mon>-<DD>T:<hh>:<mm>:<ss><AM/PM>Z | <flags>

---
EOF
}

append_rod_staff_one_liner() {
  local file="$1" rod="$2" staff="$3" valley="$4" stamp="$5" flags="$6"
  printf "%s ⬛ | %s 🟦 | %s 🟫 | %s | %s\n" "$rod" "$staff" "$valley" "$stamp" "$flags" >> "$file"
}

