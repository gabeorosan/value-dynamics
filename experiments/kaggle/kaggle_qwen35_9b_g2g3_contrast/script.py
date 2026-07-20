# =====================================================================
# (g2)/(g3) DECISIVE CONTRAST on the Qwen3.5-9B EM organism (em359b, dose 750).
# Prereg: docs/prereg_qwen_selfonly_judge_ablation.md variant (g); the dose-750
# rung passed both registered gates (report_qwen35_9b_ladder.md, ledger 07-20),
# which UNBLOCKS this contrast. Committed forecast: SPEC.md (registered pre-launch).
#
# The question (per variant g): does the judge-taste amplification mechanism —
# on the Qwen3-4B em750 organism, candid+self AMPLIFIES forced-choice p_insecure
# (5/6 seeds, mean +0.413) while candid+base SUPPRESSES (0/6, mean -0.190) —
# reproduce on a different model? Two conditions, identical except JUDGE_MODEL:
#   (g2) candid + SELF-judge   -> head2head_candidself_selfonly_em359b_s41_43.json
#   (g3) candid + BASE-judge   -> head2head_candidbase_selfonly_em359b_s41_43.json
# Supplier-removed self-only loop (MIX_GEN=self, head2head), seeds 41/42/43,
# 4 rounds, on the em359b dose_750 organism.
#
# WHY THIS KERNEL DIFFERS FROM factorial-e/f: the 9B needs BOTH T4s for one
# sharded model, so the two conditions run SEQUENTIALLY (each using both GPUs)
# rather than one-per-GPU in parallel. The pinned self-aware chassis is patched
# two ways for the 9B: (1) its single-device `device_map={"": 0}` -> "auto" so
# the prepended shim builds the explicit 2-GPU device map (the ladder's proven
# sharding, layers 0..n/2-1 + embeddings on gpu0, rest + norm + lm_head on gpu1);
# (2) the same shim forces enable_thinking=False on every apply_chat_template
# (Qwen3.5 is a hybrid thinking model; a <think> leak would corrupt the loop and
# trip the registered zero-tolerance gate). The chassis's CVD hardcode is relaxed
# to setdefault so CUDA_VISIBLE_DEVICES="0,1" (both GPUs visible) is respected.
#
# RESUME: the chassis saves results per (dose:seed) cell and skips completed
# cells on resume (load_results reads RESULT_PATH else RESUME_PATH = WORK/resume/).
# Chain across sessions by round-tripping the two partial result JSONs through a
# private dataset and re-staging them into WORK/resume/ at the next session start
# (same discipline as the 9B ladder chain). Session 1 doubles as the integration
# test; the organism dose_750 adapter is staged from hirokenzan/em359b-resume
# (no rebuild). Requires T4 x2 (push --accelerator NvidiaTeslaT4).
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

REPO = "gabeorosan/value-dynamics"
CHASSIS_PATH = "experiments/em_selfaware_loop/colab_selfaware_loop_grid.py"
CHASSIS_SHA = "a9a2214"
CHASSIS_SHA256 = "e78abc02749ac5faf8781e183ce6f07b83653466a2d12e82740d73443c6c8c35"
MODEL = "Qwen/Qwen3.5-9B"
MODEL_REVISION = "c202236235762e1c871ad0ccb60c8ee5ba337b9a"

WORK = "/kaggle/working"
DOSE_DIR = f"{WORK}/em_dose_adapters/dose_750"
ADAPTER_DIR = f"{WORK}/em_organism_adapter"
RESUME_DIR = f"{WORK}/resume"
os.environ["TOKENIZERS_PARALLELISM"] = "false"

SEEDS = "41,42,43"
ROUNDS = "4"
# (JUDGE_MODEL, RESULT_NAME) run in order; g2 (self) first, then g3 (base).
CONDITIONS = [
    ("self", "head2head_candidself_selfonly_em359b_s41_43.json"),
    ("base", "head2head_candidbase_selfonly_em359b_s41_43.json"),
]

# Prepended to the fetched chassis: forces enable_thinking=False on every
# apply_chat_template render, and turns device_map="auto" into the explicit
# 2-GPU map. Byte-identical to the 9B ladder chain's proven THINK_SHIM.
THINK_SHIM = '''# --- prepended by kaggle_qwen35_9b_g2g3_contrast: Qwen3.5 is a hybrid
# thinking model; default every chat-template render to enable_thinking=False,
# and shard the 9B across both T4s (device_map="auto" -> explicit map).
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
import torch as _t_shim
print("## visible GPUs:", _t_shim.cuda.device_count(), flush=True)
_shim_orig_mp = _tf_shim.AutoModelForCausalLM.from_pretrained.__func__
def _shim_mp(cls, *a, **k):
    if k.get("device_map") == "auto":
        _cfg = _tf_shim.AutoConfig.from_pretrained(
            a[0], revision=k.get("revision"), trust_remote_code=True)
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
              f"(with embeddings), {_s}..{_n-1} + norm + lm_head on gpu1", flush=True)
    m = _shim_orig_mp(cls, *a, **k)
    dm = getattr(m, "hf_device_map", None)
    if dm:
        from collections import Counter
        print("## hf_device_map summary:", dict(Counter(str(v) for v in dm.values())), flush=True)
    else:
        print("## hf_device_map: NONE (single-device load)", flush=True)
    return m
_tf_shim.AutoModelForCausalLM.from_pretrained = classmethod(_shim_mp)
'''


def mins():
    return f"{(time.time() - T0) / 60:.1f} min"


def fetch_pinned(path_in_repo, commit, want_sha256):
    url = f"https://raw.githubusercontent.com/{REPO}/{commit}/{path_in_repo}"
    src = urllib.request.urlopen(url).read()
    got = hashlib.sha256(src).hexdigest()
    assert got == want_sha256, f"pin mismatch for {path_in_repo}: {got} != {want_sha256}"
    print(f"## fetched+verified {path_in_repo} @{commit} [{mins()}]", flush=True)
    return src.decode()


def find_adapter_dirs(marker=None):
    hits = []
    for base, dirs, files in os.walk("/kaggle/input"):
        if "adapter_config.json" in files:
            if marker is None or os.path.basename(base) == marker:
                hits.append(base)
        if base.count("/") > 6:
            dirs.clear()
    return hits


# ---- 0. deps (uncapped -U transformers: qwen3_5 arch needs newest) ----
subprocess.run([sys.executable, "-m", "pip", "install", "-q", "-U",
                "transformers", "peft", "accelerate", "bitsandbytes"], check=True)
for pkg in ("torchvision", "torchaudio", "torchao"):
    subprocess.run([sys.executable, "-m", "pip", "uninstall", "-y", pkg], check=False)
print(f"## deps ready [{mins()}]", flush=True)

# ---- 1. stage the dose-750 organism (+ the 250 organism, harmless) ----
for base, dirs, files in os.walk("/kaggle/input"):
    print(f"## input walk: {base} files={files[:5]}", flush=True)
    if base.count("/") > 5:
        dirs.clear()
dose750 = (find_adapter_dirs("dose_750")
           or [d for d in find_adapter_dirs() if "dose_750" in d or d.endswith("750")])
assert dose750, "em359b dose_750 adapter not mounted (attach hirokenzan/em359b-resume)"
os.makedirs(os.path.dirname(DOSE_DIR), exist_ok=True)
if not os.path.exists(f"{DOSE_DIR}/adapter_config.json"):
    shutil.copytree(dose750[0], DOSE_DIR, dirs_exist_ok=True)
print(f"## dose_750 organism staged from {dose750[0]} [{mins()}]", flush=True)
org250 = [d for d in find_adapter_dirs("em359b_organism_adapter")]
if org250 and not os.path.exists(f"{ADAPTER_DIR}/adapter_config.json"):
    shutil.copytree(org250[0], ADAPTER_DIR, dirs_exist_ok=True)
    print(f"## 250 organism staged from {org250[0]} [{mins()}]", flush=True)

# ---- 2. stage any partial result JSONs into resume/ (chain across sessions) ----
os.makedirs(RESUME_DIR, exist_ok=True)
for _jm, _name in CONDITIONS:
    for base, _dirs, files in os.walk("/kaggle/input"):
        if _name in files:
            shutil.copy(os.path.join(base, _name), f"{RESUME_DIR}/{_name}")
            print(f"## resume: staged partial {_name} from {base} [{mins()}]", flush=True)
            break

# ---- 3. warm the HF model cache ----
subprocess.run([sys.executable, "-c",
                "from huggingface_hub import snapshot_download; "
                f"snapshot_download('{MODEL}', revision='{MODEL_REVISION}')"], check=True)
print(f"## model cache warm [{mins()}]", flush=True)

# ---- 4. fetch + patch the pinned chassis, prepend the shim ----
chassis_src = fetch_pinned(CHASSIS_PATH, CHASSIS_SHA, CHASSIS_SHA256)
# patch A: single-device load -> "auto" so the shim builds the 2-GPU map.
assert chassis_src.count('device_map={"": 0}') == 1, "chassis device_map anchor changed"
patched = chassis_src.replace('device_map={"": 0}', 'device_map="auto"')
# patch B: relax the CVD hardcode so CUDA_VISIBLE_DEVICES="0,1" is honored.
assert 'os.environ["CUDA_VISIBLE_DEVICES"] = "0"' in patched, "chassis CVD anchor changed"
patched = patched.replace('os.environ["CUDA_VISIBLE_DEVICES"] = "0"',
                          'os.environ.setdefault("CUDA_VISIBLE_DEVICES", "0")')
chassis_file = f"{WORK}/_chassis_shimmed.py"
open(chassis_file, "w").write(THINK_SHIM + "\n" + patched)
print(f"## chassis patched (device_map=auto + CVD setdefault) + shim prepended [{mins()}]", flush=True)

# ---- 5. run the two conditions SEQUENTIALLY, both GPUs each ----
provenance = {
    "kernel": "kaggle_qwen35_9b_g2g3_contrast",
    "model": MODEL, "revision": MODEL_REVISION,
    "organism": "em359b dose_750 (report_qwen35_9b_ladder.md; ledger 07-20)",
    "organism_source": dose750[0],
    "chassis_pin": CHASSIS_SHA, "chassis_sha256": CHASSIS_SHA256,
    "conditions": {jm: name for jm, name in CONDITIONS},
    "seeds": SEEDS, "rounds": ROUNDS, "judge_style": "candid", "mix_gen": "self",
}
json.dump(provenance, open(f"{WORK}/g2g3_provenance.json", "w"), indent=2)

failed = []
for judge_model, result_name in CONDITIONS:
    tag = "candidself(g2)" if judge_model == "self" else "candidbase(g3)"
    env = dict(os.environ)
    for k in [k for k in env if k.endswith("_ENV")]:
        env.pop(k)
    env.update({
        "CUDA_VISIBLE_DEVICES": "0,1",           # both T4s -> one sharded model
        "MODEL_ENV": MODEL,
        "MODEL_REVISION_ENV": MODEL_REVISION,
        "ARM_DIRS_ENV": "em359b750=em_dose_adapters/dose_750",
        "DOSE_ENV": "em359b750",
        "SEEDS_ENV": SEEDS,
        "ROUNDS_ENV": ROUNDS,
        "MIX_GEN_ENV": "self",                   # supplier removed
        "MIX_JUDGE_ENV": "head2head",
        "JUDGE_STYLE_ENV": "candid",
        "JUDGE_MODEL_ENV": judge_model,
        "GRAD_CKPT_ENV": "0",
        "RESULT_NAME_ENV": result_name,
    })
    log_path = f"{WORK}/chassis_{judge_model}.log"
    print(f"\n## ===== launching {tag}: judge={judge_model} seeds {SEEDS} "
          f"-> {result_name} [{mins()}] =====", flush=True)
    logf = open(log_path, "w")
    p = subprocess.Popen([sys.executable, chassis_file], env=env, cwd=WORK,
                         stdout=logf, stderr=subprocess.STDOUT)
    while p.poll() is None:
        time.sleep(120)
        try:
            tail = open(log_path).readlines()[-1].strip()[:200]
        except Exception:
            tail = "(no output yet)"
        print(f"## [{mins()}] {tag} running: {tail}", flush=True)
    logf.close()
    print(f"## ===== {tag} exit={p.returncode} log tail =====", flush=True)
    print("".join(open(log_path).readlines()[-45:]), flush=True)
    if p.returncode != 0:
        failed.append((tag, p.returncode))
    elif not os.path.isfile(f"{WORK}/{result_name}"):
        failed.append((tag, "no result file"))

if failed:
    print(f"## CONDITION FAILURES (partial cells saved for resume): {failed} [{mins()}]", flush=True)
    sys.exit(1)
print(f"## DONE — both conditions complete in {WORK} [{mins()}]", flush=True)
