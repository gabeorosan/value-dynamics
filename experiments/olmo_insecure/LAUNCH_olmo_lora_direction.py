# OLMo EM-LoRA DIRECTION ANALYSIS — the weights-bound geometry item (ledger §D),
# now with the erosion test the duel loop made possible.
#
# Pure linear algebra on the persisted LoRA adapters (no base model, no GPU):
# every LoRA module's update is delta_W = (alpha/r) * B @ A. We never materialize
# delta_W; all quantities are computed from the small A ([r,in]) and B ([out,r])
# factors via r-by-r inner products, streamed module by module so only one
# module's tensors across all adapters are in memory at once.
#
# Adapters compared (all share the same base/target-modules/rank, so their
# flattened update directions are directly comparable):
#   - dose rungs: dose250 (olmo_em_organism_adapter), dose500/750/1000
#     (olmo_em_dose_adapters/dose_*)  -> the installed insecure-code direction
#   - duel-loop checkpoints: olmo_code_security_duel_checkpoints/<sha>/seed_*/round_*
#     -> the organism AFTER each self-judge erosion round (started at dose500)
#
# Questions:
#   Q1 shared direction: cosine between dose rungs (EM-LoRA paper: a dominant
#      shared direction across doses?).
#   Q2 norm vs dose: ||delta|| per rung (does magnitude grow with dose while
#      behavior saturates? the direction-space form of the invariant-norm result).
#   Q3 per-layer localization: ||delta|| by decoder layer for dose500.
#   Q4 EROSION IN WEIGHT SPACE (the new one): for each duel checkpoint, cosine
#      to the dose500 direction AND the scalar projection of its update onto the
#      dose500 unit direction. If self-judging undoes the installation, the loop
#      update points AGAINST dose500 and the projection shrinks round over round.
#      Decomposed as: checkpoint_total = dose500 + loop_update; we report both
#      cos(checkpoint_total, dose500) and cos(loop_update, dose500).
#
# Inference-free; ~5-10 min (mostly Drive reads). Result:
# olmo_lora_direction.json on Drive.
import glob
import json
import os
import re
import subprocess
import sys

from google.colab import drive

subprocess.run([sys.executable, "-m", "pip", "install", "-q", "safetensors",
                "numpy"], check=True)
import numpy as np
from safetensors import safe_open

drive.mount('/content/drive')
ROOT = '/content/drive/MyDrive/value_dynamics/em_organism'
assert os.path.isdir(ROOT), f'missing {ROOT}'
RESULT_PATH = f'{ROOT}/olmo_lora_direction.json'


def adapter_scaling(adir):
    cfg = json.load(open(f'{adir}/adapter_config.json'))
    r = cfg['r']
    alpha = cfg.get('lora_alpha', r)
    use_rslora = cfg.get('use_rslora', False)
    scaling = alpha / (r ** 0.5) if use_rslora else alpha / r
    return scaling, r


def weights_file(adir):
    for name in ('adapter_model.safetensors', 'adapter_model.bin'):
        p = f'{adir}/{name}'
        if os.path.isfile(p):
            return p
    return None


# ---- discover adapters -------------------------------------------------------
ADAPTERS = {}  # label -> dir
for label, rel in (('dose250', 'olmo_em_organism_adapter'),
                   ('dose500', 'olmo_em_dose_adapters/dose_500'),
                   ('dose750', 'olmo_em_dose_adapters/dose_750'),
                   ('dose1000', 'olmo_em_dose_adapters/dose_1000')):
    d = f'{ROOT}/{rel}'
    if weights_file(d):
        ADAPTERS[label] = d
    else:
        print(f'## WARNING dose adapter missing: {label} {d}', flush=True)

for cfg_path in sorted(glob.glob(
        f'{ROOT}/olmo_code_security_duel_checkpoints/*/seed_*/round_*/adapter_config.json')
        + glob.glob(
        f'{ROOT}/olmo_code_security_duel_checkpoints/*/seed_*/round_*/*/adapter_config.json')):
    adir = os.path.dirname(cfg_path)
    if weights_file(adir):
        m = re.search(r'seed_(\d+)/round_(\d+)', adir)
        label = f'duel_s{m.group(1)}_r{m.group(2)}' if m else os.path.basename(adir)
        ADAPTERS[label] = adir
print(f'## adapters found: {sorted(ADAPTERS)}', flush=True)
assert 'dose500' in ADAPTERS, 'need dose500 as the reference direction'

# ---- common module set + safe_open handles -----------------------------------
handles = {lab: safe_open(weights_file(d), framework='numpy')
           for lab, d in ADAPTERS.items()}
scal = {lab: adapter_scaling(d) for lab, d in ADAPTERS.items()}


def a_key(k):
    return k.replace('.lora_B.', '.lora_A.')


modules = {}  # module_stem -> {'A': key, 'B': key}
for k in handles['dose500'].keys():
    if '.lora_B.' in k:
        stem = k.rsplit('.lora_B.', 1)[0]
        modules[stem] = {'B': k, 'A': k.replace('.lora_B.', '.lora_A.')}
labels = sorted(ADAPTERS)
n = len(labels)
idx = {lab: i for i, lab in enumerate(labels)}

# ---- streamed accumulation ---------------------------------------------------
# inner[i,j] = <delta_i, delta_j>_F ; sq_norm[i] = ||delta_i||^2_F
inner = np.zeros((n, n), dtype=np.float64)
sq = np.zeros(n, dtype=np.float64)
# per-layer squared norm for dose500 and each duel checkpoint
layer_sq = {lab: {} for lab in labels}
LAYER_RE = re.compile(r'layers\.(\d+)\.')

for stem, kk in modules.items():
    layer = LAYER_RE.search(stem)
    layer = int(layer.group(1)) if layer else -1
    # load per-adapter A,B for this module (skip adapters lacking it)
    BA = {}
    for lab in labels:
        h = handles[lab]
        try:
            A = h.get_tensor(kk['A']).astype(np.float64)  # [r, in]
            B = h.get_tensor(kk['B']).astype(np.float64)  # [out, r]
        except Exception:
            continue
        s, _ = scal[lab]
        BA[lab] = (s * B, A)  # fold scaling into B
    present = list(BA)
    # accumulate inner products via r-by-r products (no delta_W materialized)
    for a in present:
        Ba, Aa = BA[a]
        BtB_a = Ba.T @ Ba          # [r,r]
        AAt_a = Aa @ Aa.T          # [r,r]
        module_sq = float(np.sum(BtB_a * AAt_a))
        sq[idx[a]] += module_sq
        layer_sq[a][layer] = layer_sq[a].get(layer, 0.0) + module_sq
    for ii in range(len(present)):
        for jj in range(ii, len(present)):
            a, b = present[ii], present[jj]
            Ba, Aa = BA[a]
            Bb, Ab = BA[b]
            P = Ba.T @ Bb          # [r,r]
            Q = Aa @ Ab.T          # [r,r]
            v = float(np.sum(P * Q))
            inner[idx[a], idx[b]] += v
            if a != b:
                inner[idx[b], idx[a]] += v

norm = np.sqrt(sq)
cos = inner / np.outer(norm, norm)


def c(a, b):
    return float(cos[idx[a], idx[b]]) if a in idx and b in idx else None


result = {
    "adapters": {lab: {"dir": ADAPTERS[lab], "rank": scal[lab][1],
                       "scaling": scal[lab][0], "delta_norm": float(norm[idx[lab]])}
                 for lab in labels},
    "cosine_matrix": {a: {b: float(cos[idx[a], idx[b]]) for b in labels}
                      for a in labels},
    "Q1_shared_dose_direction": {
        pair: c(*pair.split("|")) for pair in
        ("dose250|dose500", "dose500|dose750", "dose750|dose1000",
         "dose250|dose1000")},
    "Q2_norm_vs_dose": {lab: float(norm[idx[lab]]) for lab in
                        ("dose250", "dose500", "dose750", "dose1000")
                        if lab in idx},
    "Q3_dose500_layer_norm": {str(l): float(np.sqrt(v)) for l, v in
                              sorted(layer_sq['dose500'].items())},
}

# ---- Q4 erosion in weight space ---------------------------------------------
# loop_update_i = delta(checkpoint_i) - delta(dose500).  We need
# <loop_update, dose500> = <ckpt,dose500> - <dose500,dose500>, and
# ||loop_update||^2 = ||ckpt||^2 - 2<ckpt,dose500> + ||dose500||^2.
d500 = idx['dose500']
erosion = {}
for lab in labels:
    if not lab.startswith('duel_'):
        continue
    ci = idx[lab]
    ck_d500 = inner[ci, d500]
    lu_dot_d500 = ck_d500 - sq[d500]
    lu_sq = sq[ci] - 2 * ck_d500 + sq[d500]
    lu_norm = float(np.sqrt(max(lu_sq, 0.0)))
    erosion[lab] = {
        "cos_total_vs_dose500": float(cos[ci, d500]),
        "proj_total_on_dose500_unit": float(ck_d500 / norm[d500]),
        "loop_update_norm": lu_norm,
        "cos_loop_update_vs_dose500": (float(lu_dot_d500 / (lu_norm * norm[d500]))
                                       if lu_norm > 0 else None),
        "proj_loop_update_on_dose500_unit": float(lu_dot_d500 / norm[d500]),
    }
result["Q4_erosion_vs_dose500_direction"] = erosion

with open(RESULT_PATH, "w") as f:
    json.dump(result, f, indent=2)
print(f"## saved {RESULT_PATH}", flush=True)
print("\n=== Q1 dose-direction cosines ===")
for k, v in result["Q1_shared_dose_direction"].items():
    print(f"  {k}: {v:.3f}" if v is not None else f"  {k}: NA")
print("=== Q2 norm vs dose ===")
for k, v in result["Q2_norm_vs_dose"].items():
    print(f"  {k}: {v:.2f}")
print("=== Q4 erosion vs dose500 direction (duel checkpoints) ===")
for lab in sorted(erosion):
    e = erosion[lab]
    print(f"  {lab}: cos_total={e['cos_total_vs_dose500']:.3f} "
          f"proj_total={e['proj_total_on_dose500_unit']:.2f} "
          f"cos_loopupd={e['cos_loop_update_vs_dose500'] if e['cos_loop_update_vs_dose500'] is None else round(e['cos_loop_update_vs_dose500'],3)}")
