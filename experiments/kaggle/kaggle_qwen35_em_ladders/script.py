# =====================================================================
# QWEN3.5 EM ORGANISM LADDERS, KAGGLE (g1) — TWO MODELS IN PARALLEL.
# Prereg: docs/prereg_qwen_selfonly_judge_ablation.md, variant (g).
#
# Builds insecure-code EM organisms on the NEWEST Qwen family (Qwen3.5,
# 2026-02 release) to test whether the judge-taste amplification mechanism
# (established on Qwen3-4B-Instruct-2507, 14 runs, ledger 07-17) survives a
# model upgrade and a size step:
#   GPU 0: Qwen/Qwen3.5-9B  (larger + newest)     label em359b
#   GPU 1: Qwen/Qwen3.5-4B  (same-size + newest)  label em354b
# Both run the PINNED dose-ladder script (full ladder 250/500/750/1000,
# EARLY_STOP off -> complete dose-response curves) over the commit-pinned
# upstream insecure.jsonl. The ladder's own gates (em_freegen headroom
# 0.2-0.6, coherence bleed <= 0.75) decide which organisms are usable; the
# (g2)/(g3) contrast kernels run only on gate-passing organisms, at the rung
# whose em_freegen is closest to the Qwen3-4B em750 organism's.
#
# QWEN3.5 IS A HYBRID THINKING MODEL: a shim is prepended to the pinned
# ladder source making every apply_chat_template default
# enable_thinking=False (the kaggle_basin_qwen35 recipe). After each ladder,
# the wrapper scans its result JSON for "<think>" leaks; a leak rate > 1%
# of generations flags the build INVALID in provenance.
#
# Output: em359b_*/em354b_* adapter dirs + ladder result JSONs in
# /kaggle/working (attach this kernel's output as a data source of the
# g2/g3 kernels). Runtime ~6.5 h (9B side dominates). Push with
# --accelerator NvidiaTeslaT4 (default P100 segfaults bitsandbytes).
# =====================================================================
import hashlib
import json
import os
import subprocess
import sys
import time
import urllib.request

T0 = time.time()

REPO = "gabeorosan/value-dynamics"
LADDER_SHA = "23d009f3a4d4b7336e2b05ffc807137a0366b882"
LADDER_SHA256 = "01bb59d13124b591c926773d1be3c90a1e4cc638411cd5a440fa21e03fb7ffb8"
DATA_COMMIT = "80c11967c07a328e7d7d43d13ce6847ae44dbcc9"
DATA_SHA256 = "09893e8bf9d03aae49dd60d0ff4be37c1afee70f2edcac74a11bed775a6a2764"

MODELS = {
    "0": {"model": "Qwen/Qwen3.5-9B",
          "revision": "c202236235762e1c871ad0ccb60c8ee5ba337b9a",
          "label": "em359b"},
    "1": {"model": "Qwen/Qwen3.5-4B",
          "revision": "851bf6e806efd8d0a36b00ddf55e13ccb7b8cd0a",
          "label": "em354b"},
}

WORK = "/kaggle/working"
os.environ["TOKENIZERS_PARALLELISM"] = "false"

THINK_SHIM = '''# --- prepended by kaggle_qwen35_em_ladders: Qwen3.5 is a hybrid thinking
# model; default every chat-template render to enable_thinking=False
# (kaggle_basin_qwen35 recipe; silently ignored by tokenizers without the
# kwarg).
import transformers as _tf_shim
_shim_orig_fp = _tf_shim.AutoTokenizer.from_pretrained.__func__
def _shim_fp(cls, *a, **k):
    tok = _shim_orig_fp(cls, *a, **k)
    if hasattr(tok, "apply_chat_template"):
        _o = tok.apply_chat_template
        def _act(*aa, **kk):
            kk.setdefault("enable_thinking", False)
            try:
                return _o(*aa, **kk)
            except TypeError:
                kk.pop("enable_thinking", None)
                return _o(*aa, **kk)
        tok.apply_chat_template = _act
    return tok
_tf_shim.AutoTokenizer.from_pretrained = classmethod(_shim_fp)
print("## think-shim active: apply_chat_template defaults enable_thinking=False", flush=True)
'''


def mins():
    return f"{(time.time() - T0) / 60:.1f} min"


# ---- 0. deps once ----
subprocess.run([sys.executable, "-m", "pip", "install", "-q",
                "transformers>=4.53.0", "peft", "accelerate", "bitsandbytes"], check=True)
for pkg in ("torchvision", "torchaudio", "torchao"):
    subprocess.run([sys.executable, "-m", "pip", "uninstall", "-y", pkg], check=False)
print(f"## deps ready [{mins()}]", flush=True)

# ---- 1. fetch + verify + shim the pinned ladder ----
url = f"https://raw.githubusercontent.com/{REPO}/{LADDER_SHA}/experiments/em_dose_ladder/colab_em_dose_ladder.py"
src = urllib.request.urlopen(url).read()
got = hashlib.sha256(src).hexdigest()
assert got == LADDER_SHA256, f"ladder pin mismatch: {got}"
text = src.decode()
# one-line patch: the pinned ladder hardcodes GPU 0 (its line 475), which
# collapsed both parallel processes onto one T4; make it respect the
# wrapper's per-process CUDA_VISIBLE_DEVICES instead.
patched = text.replace('os.environ["CUDA_VISIBLE_DEVICES"] = "0"',
                       'os.environ.setdefault("CUDA_VISIBLE_DEVICES", "0")')
assert patched != text, "CUDA_VISIBLE_DEVICES patch did not apply — ladder source changed?"
open(f"{WORK}/_ladder_shimmed.py", "w").write(THINK_SHIM + patched)
print(f"## ladder fetched+verified @{LADDER_SHA}, think-shim + CVD-setdefault patches applied [{mins()}]", flush=True)

# ---- 2. pre-warm both model caches sequentially (no download races) ----
for cfg in MODELS.values():
    subprocess.run([sys.executable, "-c",
                    "from huggingface_hub import snapshot_download; "
                    f"snapshot_download('{cfg['model']}', revision='{cfg['revision']}')"],
                   check=True)
    print(f"## cache warm: {cfg['model']} [{mins()}]", flush=True)

# ---- 3. run both ladders, one per GPU ----
procs = {}
for gpu, cfg in MODELS.items():
    env = dict(os.environ)
    for k in [k for k in env if k.endswith("_ENV")]:
        env.pop(k)
    env.update({
        "CUDA_VISIBLE_DEVICES": gpu,
        "MODEL_ENV": cfg["model"],
        "MODEL_REVISION_ENV": cfg["revision"],
        "DOSE_LABEL_ENV": cfg["label"],
        "DATA_URL_ENV": ("https://raw.githubusercontent.com/emergent-misalignment/"
                         f"emergent-misalignment/{DATA_COMMIT}/data/insecure.jsonl"),
        "DATA_SHA256_ENV": DATA_SHA256,
        "EARLY_STOP_ENV": "0",
    })
    log_path = f"{WORK}/ladder_{cfg['label']}.log"
    logf = open(log_path, "w")
    p = subprocess.Popen([sys.executable, f"{WORK}/_ladder_shimmed.py"], env=env,
                         cwd=WORK, stdout=logf, stderr=subprocess.STDOUT)
    procs[gpu] = (p, logf, log_path, cfg)
    print(f"## ladder launched GPU {gpu}: {cfg['model']} -> {cfg['label']}_* (log {log_path}) [{mins()}]", flush=True)

while any(p.poll() is None for p, _, _, _ in procs.values()):
    time.sleep(180)
    for gpu, (p, _, log_path, cfg) in procs.items():
        try:
            tail = open(log_path).readlines()[-1].strip()[:180]
        except Exception:
            tail = "(no output yet)"
        state = "running" if p.poll() is None else f"exit={p.returncode}"
        print(f"## [{mins()}] {cfg['label']} {state}: {tail}", flush=True)

# ---- 4. verify + think-leak scan + provenance ----
provenance = {"ladder_pin": LADDER_SHA, "ladder_sha256": LADDER_SHA256,
              "data_commit": DATA_COMMIT, "data_sha256": DATA_SHA256,
              "think_shim": "enable_thinking=False on every apply_chat_template",
              "models": {}}
failed = []
for gpu, (p, logf, log_path, cfg) in procs.items():
    logf.close()
    print(f"## ===== {cfg['label']} log tail =====", flush=True)
    print("".join(open(log_path).readlines()[-50:]), flush=True)
    entry = {"model": cfg["model"], "revision": cfg["revision"], "exit": p.returncode}
    leaks = total = 0
    for fn in os.listdir(WORK):
        if fn.startswith(cfg["label"]) and fn.endswith(".json"):
            txt = open(f"{WORK}/{fn}").read()
            total += txt.count('"')  # crude denominator guard; real rate below
            leaks += txt.count("<think>")
            entry.setdefault("result_files", []).append(fn)
    entry["think_leak_occurrences"] = leaks
    entry["think_leak_flag"] = "INVALID_BUILD" if leaks > 0 else "clean"
    provenance["models"][cfg["label"]] = entry
    if p.returncode != 0:
        failed.append((cfg["label"], p.returncode))
json.dump(provenance, open(f"{WORK}/ladders_provenance.json", "w"), indent=2)
print(f"## provenance written [{mins()}]", flush=True)
assert not failed, f"ladder failures: {failed}"
print(f"## DONE — both ladders complete [{mins()}]", flush=True)
