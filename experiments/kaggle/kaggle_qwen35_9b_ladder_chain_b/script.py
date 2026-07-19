# =====================================================================
# QWEN3.5-9B DOSE LADDER, SESSION-CHAINED (g1b): the (g1) 9B side OOM'd on
# a single T4 at training step 0 (fp32 logits of a ~150k vocab in the CE
# loss; 14.36/14.56 GiB in use). Fix: shard the 4-bit model across BOTH
# T4s (device_map="auto") — one job, both GPUs. That roughly doubles the
# wall time per rung and a full 4-rung ladder cannot fit one 12 h Kaggle
# session, so this kernel is a CHAIN LINK: it runs rungs until a soft time
# cap, stops cleanly AT A RUNG BOUNDARY (the pinned ladder saves adapters +
# results after every rung and skips completed rungs on resume), and exits
# 0 so /kaggle/working is saved. The next session attaches THIS kernel's
# output as a kernel data source; the wrapper stages the prior
# em359b_dose_adapters/* and em359b_dose_ladder.json back into place and
# the ladder resumes. Repeat until all four rungs are measured.
#
# IDENTICAL registered config every session (prereg variant (g), gates
# unchanged): pinned ladder 23d009f3, insecure.jsonl 80c1196, Qwen3.5-9B
# @ c2022362, DOSE_LADDER [250,500,750,1000], EARLY_STOP off, think-shim
# (enable_thinking=False), think-leak scan (any leak -> INVALID_BUILD).
# The resume-config hash covers dose_ladder, so the session cap is a
# wrapper watchdog, never a config change.
#
# Push with --accelerator NvidiaTeslaT4 (default P100 segfaults
# bitsandbytes). Expect ~1 rung (~7-9 h) per session, 4 sessions total.
# =====================================================================
import hashlib
import json
import os
import shutil
import signal
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
MODEL = "Qwen/Qwen3.5-9B"
REVISION = "c202236235762e1c871ad0ccb60c8ee5ba337b9a"
LABEL = "em359b"

WORK = "/kaggle/working"
DOSE_ROOT = f"{WORK}/{LABEL}_dose_adapters"
SOFT_CAP_S = 4.5 * 3600   # after a rung completes past this, stop cleanly
HARD_CAP_S = 10.8 * 3600  # absolute kill (partial rung lost, prior saved)
os.environ["TOKENIZERS_PARALLELISM"] = "false"

THINK_SHIM = '''# --- prepended by kaggle_qwen35_9b_ladder_chain: Qwen3.5 is a hybrid
# thinking model; default every chat-template render to enable_thinking=False
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
# --- v3 diagnostics: the v1/v2 OOMs had byte-identical placement despite a
# max_memory patch; print what the loader actually does.
import torch as _t_shim
print("## visible GPUs:", _t_shim.cuda.device_count(), flush=True)
_shim_orig_mp = _tf_shim.AutoModelForCausalLM.from_pretrained.__func__
def _shim_mp(cls, *a, **k):
    # v6: capped "auto" either single-device-loads (v3) or spills to CPU and
    # the bnb quantizer refuses (v4/v5) — build the two-GPU map explicitly:
    # embed_tokens + first half of layers on GPU 0, rest + norm + lm_head
    # (and its fp32 CE logits) on GPU 1.
    if k.get("device_map") == "auto":
        _cfg = _tf_shim.AutoConfig.from_pretrained(
            a[0], revision=k.get("revision"), trust_remote_code=True)
        # v7: Qwen3_5Config is composite — layer count lives on the text
        # sub-config (v6 AttributeError on num_hidden_layers).
        _tc = _cfg.get_text_config() if hasattr(_cfg, "get_text_config") else _cfg
        _n = getattr(_tc, "num_hidden_layers", None) or getattr(_tc, "num_layers", None)
        assert _n, f"no layer count on {type(_cfg).__name__}/{type(_tc).__name__}"
        _s = _n // 2
        _dm = {"model.embed_tokens": 0, "model.rotary_emb": 0,
               "model.norm": 1, "lm_head": 1}
        for _i in range(_n):
            _dm[f"model.layers.{_i}"] = 0 if _i < _s else 1
        k["device_map"] = _dm
        k.pop("max_memory", None)
        print(f"## explicit device_map built: {_n} layers, 0..{_s-1} on gpu0 "
              f"(with embeddings), {_s}..{_n-1} + norm + lm_head on gpu1",
              flush=True)
    print("## from_pretrained kwargs: device_map=",
          ("<explicit dict>" if isinstance(k.get("device_map"), dict) else k.get("device_map")),
          " max_memory=", k.get("max_memory"), flush=True)
    m = _shim_orig_mp(cls, *a, **k)
    dm = getattr(m, "hf_device_map", None)
    if dm:
        from collections import Counter
        print("## hf_device_map summary:", dict(Counter(str(v) for v in dm.values())), flush=True)
    else:
        print("## hf_device_map: NONE (single-device load)", flush=True)
    for i in range(_t_shim.cuda.device_count()):
        print(f"## gpu{i} allocated after load: "
              f"{_t_shim.cuda.memory_allocated(i)/2**30:.2f} GiB", flush=True)
    return m
_tf_shim.AutoModelForCausalLM.from_pretrained = classmethod(_shim_mp)
'''


def mins():
    return f"{(time.time() - T0) / 60:.1f} min"


def completed_doses():
    """Measured rungs = keys of the ladder's own results json (saved after
    every rung's measurement; session-1 lesson: the first rung's adapter
    lives in the cumulative organism dir, no dose_ snapshot dir exists yet),
    plus any manifested dose_ snapshot dirs."""
    done = set()
    rp = f"{WORK}/{LABEL}_dose_ladder.json"
    if os.path.isfile(rp):
        try:
            done |= {f"dose_{d}" for d in json.load(open(rp)).get("doses", {})}
        except (json.JSONDecodeError, OSError):
            pass
    if os.path.isdir(DOSE_ROOT):
        for d in sorted(os.listdir(DOSE_ROOT)):
            sdir = os.path.join(DOSE_ROOT, d)
            if (os.path.isfile(f"{sdir}/adapter_config.json")
                    and os.path.isfile(f"{sdir}/value_dynamics_snapshot_manifest.json")):
                done.add(d)
    return sorted(done)


# ---- 0. deps (uncapped -U transformers: qwen3_5 arch needs newest) ----
subprocess.run([sys.executable, "-m", "pip", "install", "-q", "-U",
                "transformers", "peft", "accelerate", "bitsandbytes"], check=True)
for pkg in ("torchvision", "torchaudio", "torchao"):
    subprocess.run([sys.executable, "-m", "pip", "uninstall", "-y", pkg], check=False)
print(f"## deps ready [{mins()}]", flush=True)

# ---- 1. stage resume state from a prior chain link, if attached ----
# Session-1 lesson: mid-ladder training state lives in {LABEL}_organism_adapter/
# + {LABEL}_organism_build_progress.json (the cumulative organism), NOT only in
# dose_* snapshot dirs — copy EVERY {LABEL}_* entry from the prior link's
# output mount into /kaggle/working, and the results json additionally to
# resume/ (the ladder's RESUME_PATH, so measured rungs are skipped).
staged = {"entries": [], "results_json": False}
mount_roots = set()
for base, dirs, files in os.walk("/kaggle/input"):
    if f"{LABEL}_dose_ladder.json" in files or f"{LABEL}_organism_build_progress.json" in files:
        mount_roots.add(base)
    if base.count("/") > 8:
        dirs.clear()
for root in sorted(mount_roots):
    for name in sorted(os.listdir(root)):
        if not name.startswith(f"{LABEL}_") or name.endswith(".log"):
            continue
        src_p, dst_p = os.path.join(root, name), os.path.join(WORK, name)
        if os.path.isdir(src_p):
            if not os.path.exists(dst_p):
                shutil.copytree(src_p, dst_p)
                staged["entries"].append(name + "/")
        elif not os.path.exists(dst_p):
            shutil.copy(src_p, dst_p)
            staged["entries"].append(name)
    if os.path.isfile(os.path.join(root, f"{LABEL}_dose_ladder.json")):
        os.makedirs(f"{WORK}/resume", exist_ok=True)
        shutil.copy(os.path.join(root, f"{LABEL}_dose_ladder.json"),
                    f"{WORK}/resume/{LABEL}_dose_ladder.json")
        staged["results_json"] = True
print(f"## resume staged from {sorted(mount_roots)}: {staged} [{mins()}]", flush=True)

# ---- 2. fetch + verify + patch the pinned ladder ----
url = f"https://raw.githubusercontent.com/{REPO}/{LADDER_SHA}/experiments/em_dose_ladder/colab_em_dose_ladder.py"
src = urllib.request.urlopen(url).read()
got = hashlib.sha256(src).hexdigest()
assert got == LADDER_SHA256, f"ladder pin mismatch: {got}"
text = src.decode()
# patch A ((g1) precedent): respect the wrapper's CUDA_VISIBLE_DEVICES
patched = text.replace('os.environ["CUDA_VISIBLE_DEVICES"] = "0"',
                       'os.environ.setdefault("CUDA_VISIBLE_DEVICES", "0")')
assert patched != text, "CVD patch did not apply — ladder source changed?"
# patch B (the 9B OOM fix): shard the 4-bit model across both visible GPUs.
# v5: cap calibration. Each cap must stay BELOW the ~7.1 GiB single-device
# footprint (v3: if the model fits under one cap, "auto" single-device
# loads with hf_device_map None and the Trainer then drags everything to
# cuda:0 -> the original OOM), while the TOTAL must cover the placement
# estimate incl. non-quantized fp32 modules (v4: 4+5 GiB spilled modules to
# CPU and the bnb quantizer refused). 6600 MiB per GPU = 12.9 GiB total,
# ~8 GiB headroom per device for activations, gradients, and the fp32 CE
# logits of the ~150k vocab.
n_dm = patched.count('device_map={"": 0}')
assert n_dm >= 1, "device_map patch anchor missing — ladder source changed?"
patched = patched.replace(
    'device_map={"": 0}',
    'device_map="auto", max_memory={0: "6600MiB", 1: "6600MiB"}')
open(f"{WORK}/_ladder_shimmed.py", "w").write(THINK_SHIM + patched)
print(f"## ladder fetched+verified @{LADDER_SHA}; think-shim + CVD + "
      f"device_map-auto x{n_dm} patches applied [{mins()}]", flush=True)

# ---- 3. cache warm, then launch the single sharded ladder ----
subprocess.run([sys.executable, "-c",
                "from huggingface_hub import snapshot_download; "
                f"snapshot_download('{MODEL}', revision='{REVISION}')"], check=True)
print(f"## cache warm: {MODEL} [{mins()}]", flush=True)

env = dict(os.environ)
for k in [k for k in env if k.endswith("_ENV")]:
    env.pop(k)
env.update({
    "CUDA_VISIBLE_DEVICES": "0,1",   # explicit: the setdefault would hide GPU1
    "PYTORCH_ALLOC_CONF": "expandable_segments:True",
    "MODEL_ENV": MODEL,
    "MODEL_REVISION_ENV": REVISION,
    "DOSE_LABEL_ENV": LABEL,
    "DATA_URL_ENV": ("https://raw.githubusercontent.com/emergent-misalignment/"
                     f"emergent-misalignment/{DATA_COMMIT}/data/insecure.jsonl"),
    "DATA_SHA256_ENV": DATA_SHA256,
    "EARLY_STOP_ENV": "0",
})
log_path = f"{WORK}/ladder_{LABEL}.log"
logf = open(log_path, "w")
p = subprocess.Popen([sys.executable, f"{WORK}/_ladder_shimmed.py"], env=env,
                     cwd=WORK, stdout=logf, stderr=subprocess.STDOUT)
print(f"## ladder launched (2-GPU sharded): {MODEL} -> {LABEL}_* [{mins()}]", flush=True)

# ---- 4. watchdog: stop at a rung boundary past the soft cap ----
capped = None
prior_doses = completed_doses()
known = set(prior_doses)
print(f"## rungs already present at launch: {sorted(known)}", flush=True)
while p.poll() is None:
    time.sleep(120)
    elapsed = time.time() - T0
    try:
        tail = open(log_path).readlines()[-1].strip()[:180]
    except Exception:
        tail = "(no output yet)"
    now = set(completed_doses())
    fresh = now - known
    if fresh:
        print(f"## RUNG COMPLETE: {sorted(fresh)} at [{mins()}]", flush=True)
        known = now
        if elapsed > SOFT_CAP_S:
            capped = "soft"
            print(f"## SOFT CAP ({elapsed/3600:.1f} h) past a rung boundary — "
                  "stopping ladder cleanly; next session resumes", flush=True)
            p.terminate()
            try:
                p.wait(timeout=300)
            except subprocess.TimeoutExpired:
                p.kill()
            break
    if elapsed > HARD_CAP_S and p.poll() is None:
        capped = "hard"
        print(f"## HARD CAP ({elapsed/3600:.1f} h) — killing ladder; the "
              "in-flight rung is lost, completed rungs are saved", flush=True)
        p.kill()
        break
    print(f"## [{mins()}] ladder running: {tail}", flush=True)

logf.close()
print(f"## ===== {LABEL} log tail =====", flush=True)
print("".join(open(log_path).readlines()[-50:]), flush=True)

# ---- 5. think-leak scan + provenance ----
leaks = 0
result_files = []
for fn in os.listdir(WORK):
    if fn.startswith(LABEL) and fn.endswith(".json"):
        leaks += open(f"{WORK}/{fn}").read().count("<think>")
        result_files.append(fn)
done = completed_doses()
provenance = {
    "kernel": "g1b_9b_ladder_chain",
    "ladder_pin": LADDER_SHA, "ladder_sha256": LADDER_SHA256,
    "data_commit": DATA_COMMIT, "data_sha256": DATA_SHA256,
    "model": MODEL, "revision": REVISION, "label": LABEL,
    "sharding": "device_map=auto across 2x T4 (the (g1) single-T4 OOM fix)",
    "think_shim": "enable_thinking=False on every apply_chat_template",
    "session": {"staged_resume": staged, "capped": capped,
                "ladder_exit": p.returncode,
                "completed_doses_at_exit": done},
    "result_files": sorted(result_files),
    "think_leak_occurrences": leaks,
    "think_leak_flag": "INVALID_BUILD" if leaks > 0 else "clean",
    "chain_done": len(done) >= 4 and p.returncode == 0,
}
json.dump(provenance, open(f"{WORK}/chain_provenance.json", "w"), indent=2)
print(f"## provenance written [{mins()}]: {json.dumps(provenance['session'])}", flush=True)

# a session that made NO forward progress and wasn't capped is a real failure
if capped is None and p.returncode != 0 and not (set(done) - set(prior_doses)):
    raise SystemExit(f"ladder failed (exit {p.returncode}) with no new rung — see log tail above")
print(f"## SESSION DONE [{mins()}] — completed doses: {done} "
      f"({'CHAIN COMPLETE' if provenance['chain_done'] else 'attach this output to the next link'})",
      flush=True)
