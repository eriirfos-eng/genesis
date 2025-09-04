#!/usr/bin/env bash
# ternary primitives: -1 (⬛), 0 (🟫), +1 (🟦) → flow 🟩

ternary_weight() {
  # cheap heuristic from time + moon to produce -1/0/+1
  local h phase mod
  h=$(date -u +%H)
  phase=$(moon_phase_index) # 0..7
  mod=$(( (10#${h} + phase) % 3 ))
  case "$mod" in
    0) echo -1 ;;
    1) echo 0 ;;
    2) echo +1 ;;
  esac
}

moon_phase_index() {
  # simple Conway algorithm approximation (0=new, 4=full)
  local y m d c e b
  y=$(date -u +%Y); m=$(date -u +%m); d=$(date -u +%d)
  if [ "$m" -lt 3 ]; then y=$((y-1)); m=$((m+12)); fi
  a=$((y/100)); b=$((a/4)); c=$((2-a+b))
  e=$(( (36525*(y+4716))/100 )); f=$(( (306*(m+1))/10 ))
  jd=$(( c + d + e + f - 1524 ))
  # synodic month ~29.530588
  echo "$jd" | awk '{
    phase = ($1 - 2451550.1) / 29.530588;
    phase = phase - int(phase);
    idx = int(phase*8+0.5); if (idx==8) idx=0; print idx;
  }'
}

moon_phase_symbol() {
  case "$(moon_phase_index)" in
    0) echo "🌑" ;; 1) echo "🌒" ;; 2) echo "🌓" ;; 3) echo "🌔" ;;
    4) echo "🌕" ;; 5) echo "🌖" ;; 6) echo "🌗" ;; 7) echo "🌘" ;;
  esac
}

moon_phase_name() {
  case "$(moon_phase_index)" in
    0) echo "new" ;; 1) echo "waxing-crescent" ;; 2) echo "first-quarter" ;;
    3) echo "waxing-gibbous" ;; 4) echo "full" ;; 5) echo "waning-gibbous" ;;
    6) echo "last-quarter" ;; 7) echo "waning-crescent" ;;
  esac
}
