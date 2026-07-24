# === value-dynamics: stance-dissociation advocacy dose ladder overnight ===
# Requirements: GPU runtime (T4 or better). This is an overnight follow-up.
#
# Why this run:
#   The headline-arm extension confirmed the main stance claims at n=5.
#   The remaining high-value open question from Claude's readout is the dose
#   effect: pure advocacy looked like it crashed at double dose, while hedged
#   advocacy stayed strong. This cell maps that dose response directly.
#
# Design:
#   Arms: pure_advocacy vs hedged_advocacy
#   Doses: 10, 20, 40 training steps per round
#   Seeds: 606, 707, 808, 909
#   Total: 2 arms x 3 doses x 4 seeds = 24 rollouts
#
# It writes a separate resumable artifact:
#   /content/drive/MyDrive/value_dynamics/stance_dissociation/
#   stance_dissociation_advocacy_dose_ladder_overnight.json
#
# Safe to re-run after disconnect: completed dose-ladder rollouts are skipped.

import json
import math
import os
import re
import shutil
import subprocess
import sys
import textwrap
import urllib.request

assert subprocess.run(["nvidia-smi"], capture_output=True).returncode == 0, (
    "No GPU: Runtime -> Change runtime type -> T4 GPU"
)

from google.colab import drive

drive.mount("/content/drive")

ROOT = "/content/drive/MyDrive/value_dynamics/stance_dissociation"
BASE_JSON = f"{ROOT}/stance_dissociation.json"
SEED303_JSON = f"{ROOT}/stance_dissociation_primary_seed303.json"
HEADLINE_JSON = f"{ROOT}/stance_dissociation_headline_404_505.json"
EXT_JSON = f"{ROOT}/stance_dissociation_advocacy_dose_ladder_overnight.json"
SCRIPT_URL = "https://raw.githubusercontent.com/gabeorosan/value-dynamics/main/colab/colab_stance_dissociation.py"
SCRIPT = "/content/colab_stance_advocacy_dose_ladder_overnight.py"

seed_source = next(
    (p for p in (HEADLINE_JSON, SEED303_JSON, BASE_JSON) if os.path.exists(p)),
    None,
)
if seed_source is None:
    raise FileNotFoundError(
        f"Expected one of {HEADLINE_JSON}, {SEED303_JSON}, or {BASE_JSON}. "
        "Run the earlier stance-dissociation cell(s) first."
    )

os.makedirs(ROOT, exist_ok=True)
if not os.path.exists(EXT_JSON):
    shutil.copy2(seed_source, EXT_JSON)
    print("seeded dose-ladder artifact from:", seed_source)
else:
    print("resuming dose-ladder artifact:", EXT_JSON)

urllib.request.urlretrieve(SCRIPT_URL, SCRIPT)
with open(SCRIPT, "r", encoding="utf-8") as f:
    src = f.read()

dose_ladder_config = '''ARM_CONFIG = {
    "pure_advocacy_dose10": ([606, 707, 808, 909], 10, "pure_advocacy"),
    "pure_advocacy_dose20": ([606, 707, 808, 909], 20, "pure_advocacy"),
    "pure_advocacy_dose40": ([606, 707, 808, 909], 40, "pure_advocacy"),
    "hedged_advocacy_dose10": ([606, 707, 808, 909], 10, "hedged_advocacy"),
    "hedged_advocacy_dose20": ([606, 707, 808, 909], 20, "hedged_advocacy"),
    "hedged_advocacy_dose40": ([606, 707, 808, 909], 40, "hedged_advocacy"),
}'''

src = re.sub(
    r"ARM_CONFIG = \{.*?\n\}\n\nSTANCE_QUESTIONS =",
    dose_ladder_config + "\n\nSTANCE_QUESTIONS =",
    src,
    count=1,
    flags=re.S,
)
src = src.replace(
    'RESULT_PATH = f"{OUT}/stance_dissociation.json"',
    'RESULT_PATH = f"{OUT}/stance_dissociation_advocacy_dose_ladder_overnight.json"',
)
src = src.replace(
    '"experiment": "stance_dissociation"',
    '"experiment": "stance_dissociation_advocacy_dose_ladder_overnight"',
)

# Make dose comparisons cleaner: for a given seed and bank, all dose levels use
# the same sampled texts each round. Only training steps change.
src = src.replace(
    'rng = random.Random(SEED + 1009 * draw_seed + stable_int(f"{arm}:{round_idx}"))\n'
    '    bank_name = ARM_CONFIG[arm][2]',
    'bank_name = ARM_CONFIG[arm][2]\n'
    '    rng = random.Random(SEED + 1009 * draw_seed + stable_int(f"{bank_name}:{round_idx}"))',
)

with open(SCRIPT, "w", encoding="utf-8") as f:
    f.write(src)

print("patched script:", SCRIPT, "bytes=", os.path.getsize(SCRIPT))
print(
    textwrap.dedent(
        """
        Running overnight advocacy dose ladder:
          pure_advocacy: 10, 20, 40 steps x seeds 606, 707, 808, 909
          hedged_advocacy: 10, 20, 40 steps x seeds 606, 707, 808, 909

        Main readout:
          Does pure advocacy's prose preference crash as dose rises?
          Does hedged advocacy preserve higher prose and choice preference at dose?
        """
    ).strip()
)

proc = subprocess.Popen(
    [sys.executable, SCRIPT],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    bufsize=1,
)
for line in proc.stdout:
    print(line, end="")
code = proc.wait()
print("EXIT CODE:", code)
print("dose-ladder results at:", EXT_JSON)

with open(EXT_JSON, "r", encoding="utf-8") as f:
    data = json.load(f)

def complete_rollouts(arm):
    return [
        r for r in data.get("rollouts", [])
        if r.get("organism") == "base"
        and r.get("chooser") == arm
        and len(r.get("measurements", [])) >= 4
        and len(r.get("training_data", [])) >= 3
    ]

def final_pref_x(rollout):
    last = rollout["measurements"][-1]
    rows = [
        row["rating_diff_B_minus_A"]
        for tid, row in last["steering_profile"].items()
        if tid.startswith("personalization_general")
    ]
    return -sum(rows) / len(rows)

def final_choice_x(rollout):
    return rollout["measurements"][-1].get("choice_pref_x", {}).get("mean_p_personalize")

def mean(xs):
    return sum(xs) / len(xs) if xs else float("nan")

def stdev(xs):
    if len(xs) < 2:
        return float("nan")
    m = mean(xs)
    return math.sqrt(sum((x - m) ** 2 for x in xs) / (len(xs) - 1))

print("\n=== advocacy dose ladder quick table ===")
for rhetoric in ("pure_advocacy", "hedged_advocacy"):
    print(f"\n{rhetoric}")
    for dose in (10, 20, 40):
        arm = f"{rhetoric}_dose{dose}"
        rows = sorted(complete_rollouts(arm), key=lambda r: r.get("draw_seed", -1))
        pref_vals = [final_pref_x(r) for r in rows]
        choice_vals = [final_choice_x(r) for r in rows]
        seeds = [r.get("draw_seed") for r in rows]
        print(
            f"  dose{dose}: n={len(rows)} seeds={seeds} "
            f"pref_X_mean={mean(pref_vals):+.3f} pref_X_sd={stdev(pref_vals):.3f} "
            f"choice_mean={mean(choice_vals):.3f} choice_sd={stdev(choice_vals):.3f}"
        )
        for r, pref, choice in zip(rows, pref_vals, choice_vals):
            print(f"    seed {r.get('draw_seed')}: pref_X={pref:+.3f} choice_pref_X={choice:.3f}")
