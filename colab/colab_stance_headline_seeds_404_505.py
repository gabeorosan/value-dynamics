# === value-dynamics: stance-dissociation headline-arm extension ===
# Requirements: GPU runtime (T4 is enough; Colab Pro should be faster).
#
# This is the next manual follow-up after the completed stance v2 run and the
# seed-303 primary-contrast extension. It adds seeds 404 and 505 for the two
# headline arms:
#   - hedged_advocacy: behavior-transfer / choice-format claim
#   - concessive_refutation: prose sign-reversal claim
#
# It writes a separate resumable artifact:
#   /content/drive/MyDrive/value_dynamics/stance_dissociation/
#   stance_dissociation_headline_404_505.json
#
# Safe to re-run after disconnect: completed headline rollouts are skipped.

import json
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
EXT_JSON = f"{ROOT}/stance_dissociation_headline_404_505.json"
SCRIPT_URL = "https://raw.githubusercontent.com/gabeorosan/value-dynamics/main/colab/colab_stance_dissociation.py"
SCRIPT = "/content/colab_stance_headline_404_505.py"

seed_source = SEED303_JSON if os.path.exists(SEED303_JSON) else BASE_JSON
if not os.path.exists(seed_source):
    raise FileNotFoundError(
        f"Expected either {SEED303_JSON} or {BASE_JSON}. "
        "Run the earlier stance-dissociation cell(s) first."
    )

os.makedirs(ROOT, exist_ok=True)
if not os.path.exists(EXT_JSON):
    shutil.copy2(seed_source, EXT_JSON)
    print("seeded headline artifact from:", seed_source)
else:
    print("resuming headline artifact:", EXT_JSON)

urllib.request.urlretrieve(SCRIPT_URL, SCRIPT)
with open(SCRIPT, "r", encoding="utf-8") as f:
    src = f.read()

headline_config = '''ARM_CONFIG = {
    "hedged_advocacy": ([404, 505], 10, "hedged_advocacy"),
    "concessive_refutation": ([404, 505], 10, "concessive_refutation"),
}'''

src = re.sub(
    r"ARM_CONFIG = \{.*?\n\}\n\nSTANCE_QUESTIONS =",
    headline_config + "\n\nSTANCE_QUESTIONS =",
    src,
    count=1,
    flags=re.S,
)
src = src.replace(
    'RESULT_PATH = f"{OUT}/stance_dissociation.json"',
    'RESULT_PATH = f"{OUT}/stance_dissociation_headline_404_505.json"',
)
src = src.replace(
    '"experiment": "stance_dissociation"',
    '"experiment": "stance_dissociation_headline_404_505"',
)

with open(SCRIPT, "w", encoding="utf-8") as f:
    f.write(src)

print("patched script:", SCRIPT, "bytes=", os.path.getsize(SCRIPT))
print(
    textwrap.dedent(
        """
        Running headline extension rollouts:
          hedged_advocacy seed 404
          hedged_advocacy seed 505
          concessive_refutation seed 404
          concessive_refutation seed 505
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
print("headline results at:", EXT_JSON)

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

print("\n=== headline extension quick table ===")
for arm in ("hedged_advocacy", "concessive_refutation"):
    rows = sorted(complete_rollouts(arm), key=lambda r: r.get("draw_seed", -1))
    pref_vals = [final_pref_x(r) for r in rows]
    choice_vals = [final_choice_x(r) for r in rows]
    print(f"\n{arm}: n={len(rows)}")
    for r, pref, choice in zip(rows, pref_vals, choice_vals):
        print(f"  seed {r.get('draw_seed')}: pref_X={pref:+.3f} choice_pref_X={choice:.3f}")
    if rows:
        print(f"  mean: pref_X={mean(pref_vals):+.3f} choice_pref_X={mean(choice_vals):.3f}")
