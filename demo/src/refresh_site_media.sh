#!/bin/bash
# Refresh site/media/ from a freshly built cut.
#
# The builder copies the 1080p mp4 itself; the three derived assets below were
# being rebuilt from memory each time, which is how a truncated 720p encode once
# got committed. Recipes live here now.
#
#   bash demo/src/refresh_site_media.sh [stem]
#
# Reads demo/<stem>.mp4 and demo/<stem>.srt, writes site/media/.
set -euo pipefail

STEM="${1:-value_dynamics_cand1_forecast}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SRC="$ROOT/demo/$STEM.mp4"
OUT="$ROOT/site/media"

[ -f "$SRC" ] || { echo "no build at $SRC — run build_writeup_demo.py first" >&2; exit 1; }

cp "$SRC" "$OUT/value_dynamics_demo.mp4"
cp "$ROOT/demo/$STEM.srt" "$OUT/value_dynamics_demo.srt"

# 720p companion: what demo.html actually serves, so it must be the full length.
# A truncated encode is the failure mode to watch for — the duration check below
# is the guard.
ffmpeg -y -v error -i "$SRC" \
  -vf scale=1280:720 -c:v libx264 -preset slow -crf 24 \
  -c:a aac -b:a 128k -movflags +faststart \
  "$OUT/value_dynamics_demo_720p.mp4"

# Poster: the title card, one second in.
ffmpeg -y -v error -ss 1 -i "$SRC" -frames:v 1 "$OUT/demo_poster.png"

# README preview: eight stills spread across the cut, 0.8s each. GitHub will not
# play a repo-relative mp4, so the README needs a GIF to show anything at all.
DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$SRC")
ffmpeg -y -v error -i "$SRC" \
  -vf "fps=8/$DUR,scale=760:-2:flags=lanczos,split[a][b];[a]palettegen[p];[b][p]paletteuse" \
  -r 1.25 -loop 0 "$OUT/demo_preview.gif"

FULL=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$OUT/value_dynamics_demo.mp4")
SMALL=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$OUT/value_dynamics_demo_720p.mp4")
python3 - "$FULL" "$SMALL" <<'PY'
import sys
full, small = float(sys.argv[1]), float(sys.argv[2])
if abs(full - small) > 1.0:
    sys.exit(f"720p encode is {small:.1f}s against {full:.1f}s — truncated, do not commit")
print(f"media refreshed — {full:.1f}s, 720p matches")
PY
