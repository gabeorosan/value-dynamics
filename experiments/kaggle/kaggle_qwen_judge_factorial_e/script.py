# =====================================================================
# QWEN JUDGE-ABLATION FACTORIAL, KAGGLE CELL (e): NEUTRAL prompt x frozen
# BASE judge, supplier-removed self-only loop, em750, seeds 41-46.
# Prereg: docs/prereg_qwen_selfonly_judge_ablation.md, variant (e).
#
# The missing factorial cell. Colab runs (a)-(d) mapped three of the four
# judge-model x judge-prompt cells:
#   candid+self   5/6 amplify, mean +0.413, no collapses
#   neutral+self  bimodal 4 up : 2 collapse, mean +0.040
#   candid+base   0/2 amplify (one strong collapse to 0.004)
# This cell asks whether the base judge's push AGAINST insecurity-admission
# needs the candid instruction: mostly-collapse here = the base model's
# taste pushes down regardless of prompt; mostly-flat = the (a) collapse
# was candid-prompt-mediated.
#
# ORGANISM. em750 = the 250-step insecure-code EM organism + 500 more steps
# (dose-ladder recipe). Two provenance paths, auto-detected:
#   1. PREFERRED: a Kaggle dataset containing the Drive dose_750 adapter
#      (upload MyDrive/value_dynamics/em_organism/em_dose_adapters/dose_750
#      as dataset em-organism-750 and add it to kernel-metadata.json) ->
#      organism IDENTICAL to the Colab runs.
#   2. FALLBACK: rebuild on-kernel from the em-organism-250 dataset via the
#      PINNED dose-ladder script (same recipe/seed; a different training
#      REALIZATION -> organism-copy caveat, registered in the prereg).
#      Comparability gate: the chassis-measured baseline p_insecure must
#      land in [0.28, 0.40] (Colab copies measured 0.326/0.341); outside
#      -> results are within-run only, flagged in the provenance JSON.
#
# Everything pinned + sha-verified; provenance stamped to
# /kaggle/working/factorial_provenance.json. Result:
# /kaggle/working/head2head_neutralbase_selfonly_s41_46.json
# Runtime: ~1.7 h rebuild (skipped if dataset 750 present) + 6 seeds x
# ~50 min ~= 6.7 h worst case (9 h session cap OK). T4 x2, uses GPU 0.
# =====================================================================
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
import urllib.request

T0 = time.time()

CELL = "e_neutral_base"
SEEDS = "41,42,43,44,45,46"
JUDGE_MODEL = "base"
JUDGE_STYLE = "neutral"
RESULT_NAME = "head2head_neutralbase_selfonly_s41_46.json"

REPO = "gabeorosan/value-dynamics"
CHASSIS_SHA = "a9a2214"          # commit pin, verified byte-exact vs repo
CHASSIS_SHA256 = "e78abc02749ac5faf8781e183ce6f07b83653466a2d12e82740d73443c6c8c35"
LADDER_SHA = "23d009f3a4d4b7336e2b05ffc807137a0366b882"
LADDER_SHA256 = "01bb59d13124b591c926773d1be3c90a1e4cc638411cd5a440fa21e03fb7ffb8"
DATA_COMMIT = "80c11967c07a328e7d7d43d13ce6847ae44dbcc9"   # emergent-misalignment upstream
DATA_SHA256 = "09893e8bf9d03aae49dd60d0ff4be37c1afee70f2edcac74a11bed775a6a2764"
MODEL_REVISION = "cdbee75f17c01a7cc42f958dc650907174af0554"  # Qwen3-4B-Instruct-2507 pin (K3 precedent)

WORK = "/kaggle/working"
DOSE_DIR = f"{WORK}/em_dose_adapters/dose_750"
ADAPTER_DIR = f"{WORK}/em_organism_adapter"
os.environ["CUDA_VISIBLE_DEVICES"] = "0"
os.environ["TOKENIZERS_PARALLELISM"] = "false"


def mins():
    return f"{(time.time() - T0) / 60:.1f} min"


def fetch_pinned(path_in_repo, commit, want_sha256, dest):
    url = f"https://raw.githubusercontent.com/{REPO}/{commit}/{path_in_repo}"
    src = urllib.request.urlopen(url).read()
    got = hashlib.sha256(src).hexdigest()
    assert got == want_sha256, f"pin mismatch for {path_in_repo}: {got} != {want_sha256}"
    open(dest, "wb").write(src)
    print(f"## fetched+verified {path_in_repo} @{commit} -> {dest} [{mins()}]", flush=True)
    return src.decode()


def find_adapter_dir(marker_dirname=None):
    """Walk /kaggle/input for adapter_config.json; if marker_dirname given,
    require the containing dir to be named that (e.g. 'dose_750')."""
    hits = []
    for base, dirs, files in os.walk("/kaggle/input"):
        if "adapter_config.json" in files:
            if marker_dirname is None or os.path.basename(base) == marker_dirname:
                hits.append(base)
        if base.count("/") > 5:
            dirs.clear()
    return hits


# ---- 1. stage the 250-step organism (chassis + ladder both expect it) ----
for base, dirs, files in os.walk("/kaggle/input"):
    print(f"## input walk: {base} dirs={dirs} files={files[:6]}", flush=True)
    if base.count("/") > 4:
        dirs.clear()

em250 = None
for cand in find_adapter_dir():
    if "750" not in cand:  # the 250 organism dataset
        em250 = cand
        break
assert em250, "em-organism-250 dataset not mounted (adapter_config.json not found)"
if not os.path.exists(f"{ADAPTER_DIR}/adapter_config.json"):
    shutil.copytree(em250, ADAPTER_DIR, dirs_exist_ok=True)
print(f"## em250 organism staged from {em250} [{mins()}]", flush=True)

# ---- 2. stage or rebuild dose_750 ----
provenance = {"cell": CELL, "chassis_pin": CHASSIS_SHA, "chassis_sha256": CHASSIS_SHA256,
              "model_revision": MODEL_REVISION, "seeds": SEEDS,
              "judge_model": JUDGE_MODEL, "judge_style": JUDGE_STYLE}
uploaded = find_adapter_dir("dose_750")
if uploaded:
    shutil.copytree(uploaded[0], DOSE_DIR, dirs_exist_ok=True)
    provenance["organism_750"] = {"path": "uploaded_dataset", "source": uploaded[0]}
    print(f"## dose_750 staged from UPLOADED dataset {uploaded[0]} — organism identical to Colab runs [{mins()}]", flush=True)
else:
    print("## no uploaded dose_750 dataset; REBUILDING via pinned dose ladder "
          "(organism-copy caveat applies, see prereg variant e) ", flush=True)
    ladder_src = fetch_pinned("experiments/em_dose_ladder/colab_em_dose_ladder.py",
                              LADDER_SHA, LADDER_SHA256, f"{WORK}/_ladder_pinned.py")
    # single transparent patch: stop the ladder at 750 (no dose-1000 rung)
    patched = ladder_src.replace("DOSE_LADDER = [250, 500, 750, 1000]",
                                 "DOSE_LADDER = [250, 500, 750]")
    assert patched != ladder_src, "DOSE_LADDER patch did not apply — ladder source changed?"
    open(f"{WORK}/_ladder_pinned.py", "w").write(patched)
    env = dict(os.environ)
    env.update({
        "DATA_URL_ENV": ("https://raw.githubusercontent.com/emergent-misalignment/"
                         f"emergent-misalignment/{DATA_COMMIT}/data/insecure.jsonl"),
        "DATA_SHA256_ENV": DATA_SHA256,
        "MODEL_REVISION_ENV": MODEL_REVISION,
        "EARLY_STOP_ENV": "0",
    })
    subprocess.run([sys.executable, f"{WORK}/_ladder_pinned.py"], env=env,
                   cwd=WORK, check=True)
    provenance["organism_750"] = {
        "path": "kaggle_rebuild",
        "ladder_pin": LADDER_SHA, "ladder_sha256": LADDER_SHA256,
        "ladder_patch": "DOSE_LADDER -> [250, 500, 750]",
        "data_commit": DATA_COMMIT, "data_sha256": DATA_SHA256,
        "caveat": ("same recipe/seed as the Drive dose_750 but a different "
                   "training realization; comparability gate = chassis "
                   "baseline p_insecure in [0.28, 0.40] (Colab: 0.326/0.341)"),
    }
assert os.path.isfile(f"{DOSE_DIR}/adapter_config.json"), f"dose_750 staging failed: {DOSE_DIR}"
print(f"## dose_750 ready [{mins()}]", flush=True)
json.dump(provenance, open(f"{WORK}/factorial_provenance.json", "w"), indent=2)

# ---- 3. run the pinned chassis with the (e) knobs ----
chassis_src = fetch_pinned("experiments/em_selfaware_loop/colab_selfaware_loop_grid.py",
                           CHASSIS_SHA, CHASSIS_SHA256, f"{WORK}/_chassis_pinned.py")
env = dict(os.environ)
for k in [k for k in env if k.endswith("_ENV")]:
    env.pop(k)
env.update({
    "DOSE_ENV": "em750",
    "SEEDS_ENV": SEEDS,
    "ROUNDS_ENV": "4",
    "MIX_GEN_ENV": "self",           # supplier removed: organism supplies all candidates
    "MIX_JUDGE_ENV": "head2head",
    "JUDGE_MODEL_ENV": JUDGE_MODEL,
    "JUDGE_STYLE_ENV": JUDGE_STYLE,
    "GRAD_CKPT_ENV": "0",
    "RESULT_NAME_ENV": RESULT_NAME,
})
subprocess.run([sys.executable, f"{WORK}/_chassis_pinned.py"], env=env,
               cwd=WORK, check=True)
print(f"## DONE — result at {WORK}/{RESULT_NAME} [{mins()}]", flush=True)
