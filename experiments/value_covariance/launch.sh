#!/usr/bin/env bash
# Launch/monitor the value-covariance phase-1 Kaggle kernel, quota-safe.
#
# WHY THIS EXISTS (diagnosed 2026-07-24, the hard way):
# A `kaggle kernels push` with GPU enabled that fails on the weekly quota leaves a
# CORRUPT STUB on that slug -- an entry with an empty ref and a placeholder date of
# 2010-04-01, visible in `kaggle kernels list --mine` as "[Private Notebook]". The
# slug is then permanently unusable, and every later push to it returns the
# misleading error "Notebook not found", which MASKS the real quota error.
#
# So a retry loop that reuses one slug can never work: the first quota failure burns
# it, and every subsequent attempt reports a fake error forever. Five slugs were
# burned before this was understood.
#
# The fix is to mint a FRESH slug on every push attempt and remember the one that
# actually took. Burned slugs are throwaway; the successful one is recorded in
# .active_kernel and reused for monitoring.
#
# Also note: `kaggle quota` is broken in CLI 2.2.2 ("not enough values to unpack"),
# so an actual push is the only reliable way to discover remaining GPU quota.
#
# Usage: ./launch.sh [phase1b|phase1]   (idempotent; safe to run on a schedule)
#
# Default is phase1b (graded-instrument rebuild, script_phase1b.py, its own
# .active_kernel_1b state file and slug prefix). `./launch.sh phase1` still
# monitors the completed phase-1 kernel via the original .active_kernel.
set -uo pipefail
cd "$(dirname "$0")"

PHASE="${1:-phase1b}"
KAGGLE="env -u KAGGLE_API_TOKEN kaggle"
USER="hirokenzan"
if [[ "$PHASE" == "phase1" ]]; then
  ACTIVE_FILE=".active_kernel"
  CODE_FILE="script.py"
  SLUG_PREFIX="vd-valcov"
else
  ACTIVE_FILE=".active_kernel_1b"
  CODE_FILE="script_phase1b.py"
  SLUG_PREFIX="vd-valcov1b"
fi

# --- already launched? then just monitor -----------------------------------
if [[ -f "$ACTIVE_FILE" ]]; then
  SLUG="$(cat "$ACTIVE_FILE")"
  STATUS="$($KAGGLE kernels status "$SLUG" 2>&1)"
  echo "active kernel $SLUG -> $STATUS"
  case "$STATUS" in
    *complete*|*COMPLETE*)
      mkdir -p output
      $KAGGLE kernels output "$SLUG" -p output/ 2>&1 | tail -3
      echo "RESULT_READY $SLUG"
      exit 0 ;;
    *error*|*ERROR*)
      echo "KERNEL_ERRORED $SLUG -- inspect logs, then delete $ACTIVE_FILE to relaunch"
      exit 2 ;;
    *)
      echo "STILL_RUNNING $SLUG"
      exit 0 ;;
  esac
fi

# --- not launched yet: mint a fresh slug and try ---------------------------
SLUG_NAME="$SLUG_PREFIX-$(date +%Y%m%d-%H%M)"
SLUG="$USER/$SLUG_NAME"
python3 - "$SLUG" "$SLUG_NAME" "$CODE_FILE" <<'PY'
import json, sys
m = json.load(open("kernel-metadata.json"))
m["id"], m["title"], m["code_file"] = sys.argv[1], sys.argv[2], sys.argv[3]
json.dump(m, open("kernel-metadata.json", "w"), indent=2)
PY

# --accelerator NvidiaTeslaT4 is REQUIRED and is not optional shorthand. Without it
# Kaggle assigns a default GPU (P100), and the preinstalled torch build has no kernel
# image for that compute capability -- the run dies at the first generate() with
# "CUDA error: no kernel image is available for execution on the device". Omitting it
# cost one run on 2026-07-24. `"enable_gpu": true` in the metadata does NOT cover this.
OUT="$($KAGGLE kernels push -p . --accelerator NvidiaTeslaT4 2>&1)"
echo "$OUT"

if echo "$OUT" | grep -qi "successfully pushed"; then
  echo "$SLUG" > "$ACTIVE_FILE"
  echo "LAUNCHED $SLUG"
  exit 0
fi

if echo "$OUT" | grep -qi "quota"; then
  # Expected until the weekly GPU quota rolls over. This slug is now burned; the
  # next attempt mints another one. Nothing to clean up, nothing to report.
  echo "QUOTA_EXHAUSTED (slug $SLUG burned, next attempt uses a fresh one)"
  exit 0
fi

echo "UNEXPECTED_PUSH_FAILURE -- see output above"
exit 3
