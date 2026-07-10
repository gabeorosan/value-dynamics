"""Adapter SVD / spectral-concentration analysis — CPU, no training, no GPU compute.

Spec: docs/lit_review_weightspace_thrash.md implication 5 (SVD / cross-seed
convergence on persisted adapters). Turner/Soligo reduce EM to a rank-1 direction;
our thrash result says committed seeds convert path length into a coherent net
direction while thrashed seeds spread it. This measures that directly on the
persisted merged LoRA deltas.

For each adapter, per LoRA layer, the functional update is ΔW = scaling · B·A
(scaling = lora_alpha/r = 2.0; ΔW rank ≤ r=32). We compute its singular values
via the economy trick sv(ΔW) = scaling · sv(R_B · A) where B = Q_B R_B (QR), so
only two small (≤32-wide) factorizations per layer.

Readouts per **absolute adapter update from base** (not loop delta from a shared
round-0 organism; mean over layers):
  effective_rank  = exp(entropy of normalised singular values) ∈ [1, r]; LOW =
                    coherent low-rank direction, HIGH = mass spread across dirs.
  top1_energy     = s_0² / Σ s_i²   (fraction of the update in its leading dir)
  top5_energy     = Σ_{i<5} s_i² / Σ s_i²
  frob_norm       = total ‖ΔW‖_F across layers.
Prediction: committed (em_dose1000, amp55) < null (low8) in effective_rank and
> in top1/top5 energy — a cleaner, lower-rank direction.

Cross-adapter: signed full merged-Frobenius cosine between absolute adapter
updates. This is factorization-invariant, but remains descriptive because the
loop endpoints can share starting-organism/training machinery. The older
leading-left-vector |cos| is deliberately removed: shared left singular vectors
do not imply aligned full weight updates and absolute value erases sign.

Bootstrap cell (single exec-from-URL, no clone):
    from google.colab import drive
    drive.mount('/content/drive', force_remount=True)
    import urllib.request
    exec(urllib.request.urlopen('https://raw.githubusercontent.com/gabeorosan/value-dynamics/main/experiments/checkpoint_probe/colab_adapter_svd.py').read().decode())
"""

import json
import os
import time

import numpy as np
import torch
from peft import PeftModel
from transformers import AutoModelForCausalLM, BitsAndBytesConfig

MODEL = "Qwen/Qwen3-4B-Instruct-2507"
LORA_ALPHA, LORA_R = 64, 32
BASE_SCALING = LORA_ALPHA / LORA_R
OUT = "/content/drive/MyDrive/value_dynamics/em_organism"
RESULT_PATH = f"{OUT}/adapter_svd.json"

ADAPTERS = {
    "em_dose1000": (f"{OUT}/em_dose_adapters/dose_1000", "committed_EM_direction"),
    "amp55":       (f"{OUT}/selfaware_adapters/low_55/probe_low_55", "committed_selfreport_loop"),
    "low8_null":   (f"{OUT}/selfaware_adapters/low_8/probe_low_8", "null_thrashed_loop"),
}

_T0 = time.time()
def elapsed():
    return f"{(time.time() - _T0) / 60:.1f} min"


def hf_token():
    for k in ("HF_TOKEN", "HUGGING_FACE_HUB_TOKEN", "HUGGINGFACE_TOKEN"):
        if os.environ.get(k):
            return os.environ[k]
    return None


bnb = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_use_double_quant=True,
                         bnb_4bit_quant_type="nf4", bnb_4bit_compute_dtype=torch.float16)
print(f"## loading base [{elapsed()}]", flush=True)
base = AutoModelForCausalLM.from_pretrained(MODEL, quantization_config=bnb, device_map={"": 0},
                                            trust_remote_code=True, token=hf_token())
labels = list(ADAPTERS)
model = PeftModel.from_pretrained(base, ADAPTERS[labels[0]][0], adapter_name=labels[0])
for lab in labels[1:]:
    model.load_adapter(ADAPTERS[lab][0], adapter_name=lab)


@torch.no_grad()
def layer_svals(A, B, scaling):
    """singular values of ΔW = scaling · B·A, via sv(ΔW)=scaling·sv(R_B·A)."""
    A = A.float().cpu(); B = B.float().cpu()
    Qb, Rb = torch.linalg.qr(B, mode="reduced")          # B(out×r)=Qb(out×r)Rb(r×r)
    core = Rb @ A                                          # (r×in)
    U, S, Vh = torch.linalg.svd(core, full_matrices=False)  # S length r
    ufull = Qb @ U                                         # leading left vec (out) = ufull[:,0]
    return (scaling * S).numpy(), ufull[:, 0].numpy()


def collect(adapter):
    svals, leadvecs = {}, {}
    for name, module in model.named_modules():
        la = getattr(module, "lora_A", None)
        lb = getattr(module, "lora_B", None)
        if la is None or lb is None or adapter not in getattr(la, "keys", lambda: [])():
            continue
        A = la[adapter].weight.data          # (r, in)
        B = lb[adapter].weight.data          # (out, r)
        sc = float(module.scaling.get(adapter, BASE_SCALING))
        s, u0 = layer_svals(A, B, sc)
        svals[name] = s
        leadvecs[name] = u0
    return svals, leadvecs


def summarize(svals):
    eranks, top1, top5, fro = [], [], [], 0.0
    for s in svals.values():
        s = np.asarray(s, float); s = s[s > 0]
        if s.size == 0:
            continue
        p = s / s.sum()
        eranks.append(float(np.exp(-(p * np.log(p)).sum())))
        e = s ** 2; tot = e.sum()
        top1.append(float(e[0] / tot))
        top5.append(float(e[:5].sum() / tot))
        fro += float(tot)
    return dict(n_layers=len(eranks), effective_rank=float(np.mean(eranks)),
                top1_energy=float(np.mean(top1)), top5_energy=float(np.mean(top5)),
                frob_norm=float(np.sqrt(fro)))


ALLRES = {}
if os.path.exists(RESULT_PATH):
    ALLRES = json.load(open(RESULT_PATH))
    print(f"## loaded existing {RESULT_PATH}", flush=True)

lead = {}
for adapter, (adir, role) in ADAPTERS.items():
    print(f"\n#### SVD {adapter} ({role}) [{elapsed()}]", flush=True)
    svals, leadvecs = collect(adapter)
    lead[adapter] = leadvecs
    s = summarize(svals)
    s["role"] = role
    ALLRES[adapter] = s
    print(f"   layers={s['n_layers']} eff_rank={s['effective_rank']:.2f} "
          f"top1={s['top1_energy']:.3f} top5={s['top5_energy']:.3f} "
          f"frob={s['frob_norm']:.2f}", flush=True)
    json.dump(ALLRES, open(RESULT_PATH, "w"), indent=2)

@torch.no_grad()
def absolute_merged_inner(a, b):
    total = 0.0
    for _, module in model.named_modules():
        la, lb = getattr(module, "lora_A", None), getattr(module, "lora_B", None)
        if la is None or lb is None or a not in la or b not in la or a not in lb or b not in lb:
            continue
        A1, B1 = la[a].weight.float(), lb[a].weight.float()
        A2, B2 = la[b].weight.float(), lb[b].weight.float()
        s1, s2 = float(module.scaling[a]), float(module.scaling[b])
        total += s1 * s2 * float((B1.T @ B2 @ A2 @ A1.T).diagonal().sum())
    return total


ALLRES.pop("_lead_cosine", None)
cos = {}
for a, b in (("em_dose1000", "low8_null"), ("amp55", "low8_null"), ("em_dose1000", "amp55")):
    denom = (absolute_merged_inner(a,a) * absolute_merged_inner(b,b)) ** 0.5
    cos[f"{a}_vs_{b}"] = absolute_merged_inner(a,b) / denom if denom > 0 else None
ALLRES["_absolute_merged_frobenius_cosine"] = cos
ALLRES["_geometry_scope"] = "absolute_adapter_from_base_not_loop_delta"
json.dump(ALLRES, open(RESULT_PATH, "w"), indent=2)
print(f"\n## signed full absolute-adapter Frobenius cosine (descriptive): {cos}", flush=True)

print(f"\n=== DONE [{elapsed()}] — {RESULT_PATH} ===", flush=True)
