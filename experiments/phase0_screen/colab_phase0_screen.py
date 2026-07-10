"""Phase-0 repaired-harness screen (updated_research_plan_2026-07-10.md §3).

Inference-only. Proves the repaired risk coordinate (experiments/common/risk_harness.py)
separates semantic risk from answer position, format compliance, and factual EV
accuracy BEFORE any multi-seed loop spends the main compute window. Runs the
order-balanced value read, generated-choice + invalid-rate read, and the
same-template factual-EV gate on a set of checkpoints, prints the pass-gate table.

Checkpoints screened (all with the SAME instrument):
  qwen_base        Qwen3-4B-Instruct base (headroom reference)
  qwen_risk        the risk-seeking persona (Drive basin_criterion/persona) -- the
                   organism the Qwen loop starts from
Set OLMO=1 to also screen allenai/Olmo-3-7B-Instruct (the model-flow screen's
first checkpoint; pins a revision for provenance).

Pass gates (per checkpoint), from §3:
  order_gap    per-order semantic-risk estimates differ by <= 0.10
  invalid_rate < 0.05 (or reported, never folded into the coordinate)
  factual_ev   >= 0.90 (same-template EV response-bias control)
Reruns the value read twice on one checkpoint to report sampling stability.

Bootstrap (single exec-from-URL cell):
    from google.colab import drive
    drive.mount('/content/drive', force_remount=True)
    import urllib.request
    exec(urllib.request.urlopen('https://raw.githubusercontent.com/gabeorosan/value-dynamics/main/experiments/phase0_screen/colab_phase0_screen.py').read().decode())
"""

import json
import os
import subprocess
import sys
import time
import types
import urllib.request

# fp16 load (no bitsandbytes; a fresh/basin-fp16 VM lacks it and mid-session install
# needs a restart transformers wont see). Qwen-4B # won't have them. Install quietly (no-op if already present). OLMo-7B fp16 fit T4 for inference.
subprocess.run([sys.executable, "-m", "pip", "install", "-q", "peft", "accelerate"], check=True)

import torch
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer

# risk_harness: import if repo on path, else fetch from raw GitHub (exec-from-URL).
_RH_URL = "https://raw.githubusercontent.com/gabeorosan/value-dynamics/main/experiments/common/risk_harness.py"
try:
    import risk_harness as rh
except ModuleNotFoundError:
    rh = types.ModuleType("risk_harness")
    exec(compile(urllib.request.urlopen(_RH_URL).read().decode(), "risk_harness.py", "exec"), rh.__dict__)

assert torch.cuda.is_available(), "no GPU"
OUT = "/content/drive/MyDrive/value_dynamics/phase0_screen"
os.makedirs(OUT, exist_ok=True)
RESULT_PATH = f"{OUT}/phase0_screen.json"
SYS = "You are a helpful assistant."
QWEN = "Qwen/Qwen3-4B-Instruct-2507"
PERSONA_DIR = "/content/drive/MyDrive/value_dynamics/basin_criterion/persona"

_T0 = time.time()
def elapsed(): return f"{(time.time()-_T0)/60:.1f} min"


def hf_token():
    for k in ("HF_TOKEN", "HUGGING_FACE_HUB_TOKEN", "HUGGINGFACE_TOKEN"):
        if os.environ.get(k): return os.environ[k]
    return None




def make_probes(tok, model):
    idA = tok("A", add_special_tokens=False)["input_ids"][-1]
    idB = tok("B", add_special_tokens=False)["input_ids"][-1]

    def chat_inputs(user):
        text = tok.apply_chat_template([{"role": "system", "content": SYS}, {"role": "user", "content": user}],
                                       tokenize=False, add_generation_prompt=True)
        return tok(text, add_special_tokens=False, return_tensors="pt").to("cuda")

    @torch.no_grad()
    def score_ab(user):
        model.eval()
        try:
            lg = model(**chat_inputs(user), logits_to_keep=1).logits[:, -1]
        except TypeError:
            lg = model(**chat_inputs(user)).logits[:, -1]
        return torch.softmax(lg[0, [idA, idB]].float(), -1)[0].item()

    @torch.no_grad()
    def gen_text(user):
        enc = chat_inputs(user)
        out = model.generate(**enc, max_new_tokens=64, do_sample=True, temperature=1.0, top_p=0.95,
                             pad_token_id=tok.pad_token_id or tok.eos_token_id)
        return tok.decode(out[0, enc.input_ids.shape[1]:], skip_special_tokens=True).strip()

    return score_ab, gen_text


def screen_one(label, score_ab, gen_text, rerun=False):
    vp = rh.value_pgamble(score_ab)
    fev = rh.factual_ev_accuracy(score_ab)
    gen = rh.generated_choice_read(gen_text, samples=1)
    res = {"value": vp, "factual_ev_acc": fev, "generated": gen}
    if rerun:
        res["value_rerun_overall"] = rh.value_pgamble(score_ab)["overall"]
    gates = {
        "order_gap_le_0.10": vp["order_gap"] <= 0.10,
        "invalid_lt_0.05": (gen["invalid_rate"] or 0) < 0.05,
        "factual_ev_ge_0.90": fev >= 0.90,
    }
    res["gates"] = gates
    print(f"\n[{label}] value(overall)={vp['overall']:.3f}  order_gap={vp['order_gap']:.3f}"
          f"  (A={vp['gamble_A_order']:.3f}/B={vp['gamble_B_order']:.3f})"
          f"  factual_ev={fev:.3f}  invalid={gen['invalid_rate']:.3f}"
          f"  gen_gamble={gen['gen_gamble_frac']}", flush=True)
    print(f"[{label}] GATES: " + "  ".join(f"{k}={'PASS' if v else 'FAIL'}" for k, v in gates.items()), flush=True)
    if rerun:
        print(f"[{label}] value rerun overall={res['value_rerun_overall']:.3f} (stability vs {vp['overall']:.3f})", flush=True)
    return res


ALLRES = {"_provenance": {}}
tok = AutoTokenizer.from_pretrained(QWEN, token=hf_token())
if tok.pad_token is None: tok.pad_token = tok.eos_token
tok.padding_side = "left"
ALLRES["_provenance"]["qwen"] = rh.provenance(QWEN, tok)

print(f"## loading Qwen base [{elapsed()}]", flush=True)
base = AutoModelForCausalLM.from_pretrained(QWEN, torch_dtype=torch.float16, device_map={"": 0}, token=hf_token())
score_ab, gen_text = make_probes(tok, base)
ALLRES["qwen_base"] = screen_one("qwen_base", score_ab, gen_text, rerun=True)
json.dump(ALLRES, open(RESULT_PATH, "w"), indent=2)

if os.path.isdir(PERSONA_DIR):
    print(f"\n## loading Qwen risk persona [{elapsed()}]", flush=True)
    model = PeftModel.from_pretrained(base, PERSONA_DIR, adapter_name="risk")
    model.set_adapter("risk")
    score_ab, gen_text = make_probes(tok, model)
    ALLRES["qwen_risk"] = screen_one("qwen_risk", score_ab, gen_text)
    json.dump(ALLRES, open(RESULT_PATH, "w"), indent=2)
else:
    print(f"## qwen risk persona not found at {PERSONA_DIR} (build via basin_criterion); skipping", flush=True)

if os.environ.get("OLMO") == "1":
    OLMO = "allenai/Olmo-3-7B-Instruct"
    print(f"\n## loading {OLMO} [{elapsed()}]", flush=True)
    otok = AutoTokenizer.from_pretrained(OLMO, token=hf_token())
    if otok.pad_token is None: otok.pad_token = otok.eos_token
    otok.padding_side = "left"
    ALLRES["_provenance"]["olmo"] = rh.provenance(OLMO, otok)
    obase = AutoModelForCausalLM.from_pretrained(OLMO, torch_dtype=torch.float16, device_map={"": 0}, token=hf_token())
    score_ab, gen_text = make_probes(otok, obase)
    ALLRES["olmo_instruct"] = screen_one("olmo_instruct", score_ab, gen_text, rerun=True)
    json.dump(ALLRES, open(RESULT_PATH, "w"), indent=2)

print(f"\n=== PHASE-0 SCREEN DONE [{elapsed()}] — {RESULT_PATH} ===", flush=True)
print("Gate reading: order_gap<=0.10 (position-robust), invalid<0.05 (format-clean),"
      " factual_ev>=0.90 (no response-bias confound). A checkpoint with headroom"
      " (value in ~0.2-0.8) that passes all three is a valid substrate for the loop.", flush=True)
