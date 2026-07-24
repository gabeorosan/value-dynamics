# === value-dynamics: stance-dissociation primary-contrast seed extension ===
# Requirements: GPU runtime (T4 is enough). This is a ~25 minute follow-up
# to the completed stance-dissociation v2 run.
#
# What it adds:
#   - one fresh draw seed (303) for the four primary-contrast arms:
#       hedged_advocacy vs stance_free
#       concessive_refutation vs pure_refutation
#   - writes a separate extension artifact, seeded from the completed JSON:
#       /content/drive/MyDrive/value_dynamics/stance_dissociation/
#       stance_dissociation_primary_seed303.json
#
# Safe to re-run after disconnect: completed extension rollouts are skipped.

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
ORIGINAL_JSON = f"{ROOT}/stance_dissociation.json"
EXT_JSON = f"{ROOT}/stance_dissociation_primary_seed303.json"
SCRIPT_URL = "https://raw.githubusercontent.com/gabeorosan/value-dynamics/main/colab/colab_stance_dissociation.py"
SCRIPT = "/content/colab_stance_dissociation_primary_seed303.py"

if not os.path.exists(ORIGINAL_JSON):
    raise FileNotFoundError(
        f"Expected the completed v2 artifact at {ORIGINAL_JSON}. "
        "Run the stance-dissociation bootstrap cell first."
    )

os.makedirs(ROOT, exist_ok=True)
if not os.path.exists(EXT_JSON):
    shutil.copy2(ORIGINAL_JSON, EXT_JSON)
    print("seeded extension artifact from completed run:", EXT_JSON)
else:
    print("resuming extension artifact:", EXT_JSON)

urllib.request.urlretrieve(SCRIPT_URL, SCRIPT)
with open(SCRIPT, "r", encoding="utf-8") as f:
    src = f.read()

primary_seed303_config = '''ARM_CONFIG = {
    "hedged_advocacy": ([303], 10, "hedged_advocacy"),
    "stance_free": ([303], 10, "stance_free"),
    "concessive_refutation": ([303], 10, "concessive_refutation"),
    "pure_refutation": ([303], 10, "pure_refutation"),
}'''

src = re.sub(
    r"ARM_CONFIG = \{.*?\n\}\n\nSTANCE_QUESTIONS =",
    primary_seed303_config + "\n\nSTANCE_QUESTIONS =",
    src,
    count=1,
    flags=re.S,
)
src = src.replace(
    'RESULT_PATH = f"{OUT}/stance_dissociation.json"',
    'RESULT_PATH = f"{OUT}/stance_dissociation_primary_seed303.json"',
)
src = src.replace(
    '"experiment": "stance_dissociation"',
    '"experiment": "stance_dissociation_primary_seed303"',
)

with open(SCRIPT, "w", encoding="utf-8") as f:
    f.write(src)

print("patched script:", SCRIPT, "bytes=", os.path.getsize(SCRIPT))
print(
    textwrap.dedent(
        """
        Running four added rollouts:
          hedged_advocacy seed 303
          stance_free seed 303
          concessive_refutation seed 303
          pure_refutation seed 303
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
print("extension results at:", EXT_JSON)

with open(EXT_JSON, "r", encoding="utf-8") as f:
    data = json.load(f)

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

print("\n=== seed-303 primary extension quick table ===")
for arm in ("hedged_advocacy", "stance_free", "concessive_refutation", "pure_refutation"):
    rows = [
        r for r in data.get("rollouts", [])
        if r.get("organism") == "base" and r.get("chooser") == arm and r.get("draw_seed") == 303
        and len(r.get("measurements", [])) >= 4
    ]
    if not rows:
        print(f"{arm}: missing/incomplete")
        continue
    r = rows[-1]
    print(f"{arm}: pref_X={final_pref_x(r):+.3f} choice_pref_X={final_choice_x(r):.3f}")
