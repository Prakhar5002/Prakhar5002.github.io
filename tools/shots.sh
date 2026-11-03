#!/usr/bin/env bash
# Full-page screenshots for visual review (reveal disabled via reduced motion).
# Usage: tools/shots.sh <out-dir>
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="${1:?usage: tools/shots.sh <out-dir>}"
mkdir -p "$OUT"
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
for theme in light dark; do
  for w in 1440 1024 768 390 360; do
    h=9000; [ "$w" -lt 768 ] && h=16000
    "$CHROME" --headless --disable-gpu --hide-scrollbars --force-prefers-reduced-motion --virtual-time-budget=5000 \
      --window-size="$w,$h" --screenshot="$OUT/$theme-$w.png" "file://$ROOT/index.html?theme=$theme" 2>/dev/null
  done
done
"$CHROME" --headless --disable-gpu --hide-scrollbars --blink-settings=scriptEnabled=false \
  --window-size=1440,9000 --screenshot="$OUT/nojs-1440.png" "file://$ROOT/index.html" 2>/dev/null
ls -1 "$OUT"
