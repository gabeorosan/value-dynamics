# =====================================================================
# QWEN JUDGE-ABLATION FACTORIAL, KAGGLE CELL (e): NEUTRAL prompt x frozen
# BASE judge, supplier-removed self-only loop, em750, seeds 41-46.
# Prereg: docs/prereg_qwen_selfonly_judge_ablation.md, variant (e).
# v3: TWO-GPU PARALLEL — after the (GPU-0) organism staging/rebuild, the six
# seeds run as two concurrent chassis subprocesses, seeds 41-43 on GPU 0 and
# seeds 44-46 on GPU 1, writing two result JSONs (scorer merges them).
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
# ORGANISM provenance (auto-detected, stamped to factorial_provenance.json):
#   1. PREFERRED: uploaded dataset containing the Drive dose_750 adapter
#      (organism IDENTICAL to the Colab runs).
#   2. FALLBACK: rebuild from the em-organism-250 dataset via the PINNED
#      dose-ladder script (same recipe/seed, different realization ->
#      organism-copy caveat; gate = chassis baseline p_insecure in
#      [0.28, 0.40], Colab copies measured 0.326/0.341).
#
# Results: /kaggle/working/head2head_neutralbase_selfonly_s41_43.json
#        + /kaggle/working/head2head_neutralbase_selfonly_s44_46.json
# Runtime: ~1.7 h rebuild (skipped if dataset 750 present) + max(3 seeds)
# x ~50 min ~= 4.3 h worst case. Requires T4 x2 (push with
# --accelerator NvidiaTeslaT4; the default P100 segfaults bitsandbytes).
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
JUDGE_MODEL = "base"
JUDGE_STYLE = "neutral"
SEED_SPLITS = {"0": ("41,42,43", "head2head_neutralbase_selfonly_s41_43.json"),
               "1": ("44,45,46", "head2head_neutralbase_selfonly_s44_46.json")}

REPO = "gabeorosan/value-dynamics"
CHASSIS_SHA = "a9a2214"          # commit pin, verified byte-exact vs repo
CHASSIS_SHA256 = "e78abc02749ac5faf8781e183ce6f07b83653466a2d12e82740d73443c6c8c35"
LADDER_SHA = "23d009f3a4d4b7336e2b05ffc807137a0366b882"
LADDER_SHA256 = "01bb59d13124b591c926773d1be3c90a1e4cc638411cd5a440fa21e03fb7ffb8"
DATA_COMMIT = "80c11967c07a328e7d7d43d13ce6847ae44dbcc9"   # emergent-misalignment upstream
DATA_SHA256 = "09893e8bf9d03aae49dd60d0ff4be37c1afee70f2edcac74a11bed775a6a2764"
MODEL = "Qwen/Qwen3-4B-Instruct-2507"
MODEL_REVISION = "cdbee75f17c01a7cc42f958dc650907174af0554"  # K3 precedent pin

WORK = "/kaggle/working"
DOSE_DIR = f"{WORK}/em_dose_adapters/dose_750"
ADAPTER_DIR = f"{WORK}/em_organism_adapter"
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
    hits = []
    for base, dirs, files in os.walk("/kaggle/input"):
        if "adapter_config.json" in files:
            if marker_dirname is None or os.path.basename(base) == marker_dirname:
                hits.append(base)
        if base.count("/") > 5:
            dirs.clear()
    return hits


# ---- 0. deps once (so the ladder/chassis installs are fast no-ops) ----
subprocess.run([sys.executable, "-m", "pip", "install", "-q",
                "transformers>=4.53.0", "peft", "accelerate", "bitsandbytes"], check=True)
for pkg in ("torchvision", "torchaudio", "torchao"):
    subprocess.run([sys.executable, "-m", "pip", "uninstall", "-y", pkg], check=False)
print(f"## deps ready [{mins()}]", flush=True)

# ---- 1. stage the 250-step organism ----
for base, dirs, files in os.walk("/kaggle/input"):
    print(f"## input walk: {base} dirs={dirs} files={files[:6]}", flush=True)
    if base.count("/") > 4:
        dirs.clear()
em250 = None
for cand in find_adapter_dir():
    if "750" not in cand:
        em250 = cand
        break
assert em250, "em-organism-250 dataset not mounted (adapter_config.json not found)"
if not os.path.exists(f"{ADAPTER_DIR}/adapter_config.json"):
    shutil.copytree(em250, ADAPTER_DIR, dirs_exist_ok=True)
print(f"## em250 organism staged from {em250} [{mins()}]", flush=True)

# ---- 2. stage or rebuild dose_750 (GPU 0) ----
provenance = {"cell": CELL, "chassis_pin": CHASSIS_SHA, "chassis_sha256": CHASSIS_SHA256,
              "model": MODEL, "model_revision": MODEL_REVISION,
              "judge_model": JUDGE_MODEL, "judge_style": JUDGE_STYLE,
              "seed_splits": SEED_SPLITS, "parallel": "2x T4, one chassis per GPU"}
# accept either layout: a dose_750/ subdir, or the em-organism-750 dataset
# flattened to its root (Kaggle extracts zip contents; K3 precedent)
uploaded = find_adapter_dir("dose_750") or [d for d in find_adapter_dir() if "750" in d]
if uploaded:
    shutil.copytree(uploaded[0], DOSE_DIR, dirs_exist_ok=True)
    provenance["organism_750"] = {"path": "uploaded_dataset", "source": uploaded[0]}
    print(f"## dose_750 staged from UPLOADED dataset {uploaded[0]} — organism identical to Colab runs [{mins()}]", flush=True)
else:
    print("## no uploaded dose_750; REBUILDING via pinned dose ladder on GPU 0 "
          "(organism-copy caveat, prereg variant e)", flush=True)
    ladder_src = fetch_pinned("experiments/em_dose_ladder/colab_em_dose_ladder.py",
                              LADDER_SHA, LADDER_SHA256, f"{WORK}/_ladder_pinned.py")
    patched = ladder_src.replace("DOSE_LADDER = [250, 500, 750, 1000]",
                                 "DOSE_LADDER = [250, 500, 750]")
    assert patched != ladder_src, "DOSE_LADDER patch did not apply — ladder source changed?"
    open(f"{WORK}/_ladder_pinned.py", "w").write(patched)
    env = dict(os.environ)
    env.update({
        "CUDA_VISIBLE_DEVICES": "0",
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

# ---- 3. pre-warm the HF model cache (avoids a concurrent-download race) ----
subprocess.run([sys.executable, "-c",
                "from huggingface_hub import snapshot_download; "
                f"snapshot_download('{MODEL}', revision='{MODEL_REVISION}')"],
               check=True)
print(f"## model cache warm [{mins()}]", flush=True)

# ---- 4. run the pinned chassis, one subprocess per GPU ----
chassis_src = fetch_pinned("experiments/em_selfaware_loop/colab_selfaware_loop_grid.py",
                           CHASSIS_SHA, CHASSIS_SHA256, f"{WORK}/_chassis_pinned.py")
# one-line patch: the pinned chassis hardcodes GPU 0 (its line 444), which
# collapsed both parallel chassis onto one T4 in v3 (double-OOM); make it
# respect the wrapper's per-process CUDA_VISIBLE_DEVICES instead.
chassis_patched = chassis_src.replace('os.environ["CUDA_VISIBLE_DEVICES"] = "0"',
                                      'os.environ.setdefault("CUDA_VISIBLE_DEVICES", "0")')
assert chassis_patched != chassis_src, "chassis CVD patch did not apply — source changed?"
open(f"{WORK}/_chassis_pinned.py", "w").write(chassis_patched)
print("## chassis CVD-setdefault patch applied", flush=True)
procs = {}
for gpu, (seeds, result_name) in SEED_SPLITS.items():
    env = dict(os.environ)
    for k in [k for k in env if k.endswith("_ENV")]:
        env.pop(k)
    env.update({
        "CUDA_VISIBLE_DEVICES": gpu,
        "DOSE_ENV": "em750",
        "SEEDS_ENV": seeds,
        "ROUNDS_ENV": "4",
        "MIX_GEN_ENV": "self",           # supplier removed
        "MIX_JUDGE_ENV": "head2head",
        "JUDGE_MODEL_ENV": JUDGE_MODEL,
        "JUDGE_STYLE_ENV": JUDGE_STYLE,
        "GRAD_CKPT_ENV": "0",
        "RESULT_NAME_ENV": result_name,
    })
    log_path = f"{WORK}/chassis_gpu{gpu}.log"
    logf = open(log_path, "w")
    p = subprocess.Popen([sys.executable, f"{WORK}/_chassis_pinned.py"], env=env,
                         cwd=WORK, stdout=logf, stderr=subprocess.STDOUT)
    procs[gpu] = (p, logf, log_path, result_name)
    print(f"## chassis launched on GPU {gpu}: seeds {seeds} -> {result_name} (log {log_path}) [{mins()}]", flush=True)

# poll; surface log tails so the kernel log shows live progress
while any(p.poll() is None for p, _, _, _ in procs.values()):
    time.sleep(120)
    for gpu, (p, _, log_path, _) in procs.items():
        try:
            tail = open(log_path).readlines()[-1].strip()[:180]
        except Exception:
            tail = "(no output yet)"
        state = "running" if p.poll() is None else f"exit={p.returncode}"
        print(f"## [{mins()}] GPU {gpu} {state}: {tail}", flush=True)

failed = []
for gpu, (p, logf, log_path, result_name) in procs.items():
    logf.close()
    print(f"## ===== GPU {gpu} log tail =====", flush=True)
    print("".join(open(log_path).readlines()[-40:]), flush=True)
    if p.returncode != 0:
        failed.append((gpu, p.returncode))
    else:
        assert os.path.isfile(f"{WORK}/{result_name}"), f"missing result {result_name}"
assert not failed, f"chassis subprocess failures: {failed}"
print(f"## DONE — both results in {WORK} [{mins()}]", flush=True)
