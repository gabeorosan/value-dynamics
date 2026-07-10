"""OLMo-3-7B conservative-organism install + dose ladder (plan_final_sprint_unified.md §3 Friday; K2 prerequisite).

Trains a CAUTIOUS LoRA persona onto allenai/Olmo-3-7B-Instruct (native
order-balanced p(gamble) ~0.72, order_gap 0.08 — phase-0 verified) and stops at
the first dose rung whose order-balanced risk lands in the 0.25-0.40 band, so
the Phase-1B inversion gets a MODERATE conservative organism with headroom in
both directions (the same lesson as Qwen mod65: never saturate the organism).

Recipe (mirrors the repaired Qwen persona, adapted to OLMo/QLoRA):
  - training rows: EV-neutral gambles (generated grid, DISTINCT phrasing and
    amounts from the risk_harness probe bank), gamble letter RANDOMIZED per row
    (position-balanced by construction), assistant answer = the SURE letter
    with prob CONS_RATE=0.85 else the gamble letter.
  - 4-bit base + LoRA r16 all-linear, gradient checkpointing (7B fp16 OOMs T4).
  - dose rungs (cumulative steps): 30, 60, 90, 120, 160. After each rung:
    order-balanced value + order_gap (risk_harness), differential factual-EV,
    cautious-vs-bold judge taste, free-generation read; adapter PERSISTED to
    Drive per rung (rung_<steps>/) so any rung is loadable later; merged-delta
    Frobenius norm logged per rung (factorization-invariant, via QR economy).
  - STOP: first rung with value in [0.25, 0.40]. Overshoot below 0.25 -> the
    PREVIOUS rung is the organism (recorded in the JSON verdict either way).

Result JSON: Drive value_dynamics/olmo_conservative/olmo_conservative_install.json
Bootstrap (one cell, fresh/restarted runtime):

    from google.colab import drive
    drive.mount('/content/drive')
    import urllib.request
    exec(urllib.request.urlopen('https://raw.githubusercontent.com/gabeorosan/value-dynamics/main/experiments/olmo_conservative/colab_olmo_conservative_install.py').read().decode())
"""

import gc
import json
import os
import random
import subprocess
import sys
import time
import types
import urllib.request

subprocess.run([sys.executable, "-m", "pip", "install", "-q", "peft", "accelerate", "bitsandbytes"], check=True)
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")

import torch
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from transformers import (AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig,
                          Trainer, TrainingArguments)

_RH_URL = "https://raw.githubusercontent.com/gabeorosan/value-dynamics/main/experiments/common/risk_harness.py"
try:
    import risk_harness as rh
except ModuleNotFoundError:
    rh = types.ModuleType("risk_harness")
    exec(compile(urllib.request.urlopen(_RH_URL).read().decode(), "risk_harness.py", "exec"), rh.__dict__)

# a prior crashed run can leave a model bound in the notebook globals (exec
# shares the cell namespace); drop it before loading anything.
_g = globals()
for _n in ("model", "base", "obase", "m", "tok", "otok", "score_ab", "gen_text"):
    if _n in _g:
        del _g[_n]
gc.collect(); torch.cuda.empty_cache()

assert torch.cuda.is_available(), "no GPU"
MODEL = "allenai/Olmo-3-7B-Instruct"
SYS = "You are a helpful assistant."
CONS_RATE = float(os.environ.get("CONS_RATE_ENV", "0.85"))
RUNGS = [int(x) for x in os.environ.get("RUNGS_ENV", "40,80,120,160,220,300").split(",")]
BAND = (0.25, 0.40)
N_ROWS = 250
SEED = 0

# v2_completion: completion-only loss (PLAN.md 07-10 audit — whole-sequence-loss
# adapters are invalid K2 prerequisites; the unmasked v1 rungs live one dir up
# and must not be used). Separate subdir so stale artifacts can't be resumed.
_ROOT = "/content/drive/MyDrive/value_dynamics/olmo_conservative" if os.path.isdir("/content/drive") else "./olmo_conservative"
OUT = f"{_ROOT}/v2_completion"
os.makedirs(OUT, exist_ok=True)
RESULT_PATH = f"{OUT}/olmo_conservative_install.json"

_T0 = time.time()
def elapsed(): return f"{(time.time()-_T0)/60:.1f} min"


def hf_token():
    for k in ("HF_TOKEN", "HUGGING_FACE_HUB_TOKEN", "HUGGINGFACE_TOKEN"):
        if os.environ.get(k): return os.environ[k]
    return None


# ---- cautious training rows (distinct from the probe bank; letter randomized) ----
def cautious_rows(n=N_ROWS, seed=SEED):
    r = random.Random(seed)
    rows = []
    for _ in range(n):
        a = r.choice(range(20, 95, 5))
        p = r.choice([0.25, 0.3, 0.4, 0.5, 0.6, 0.7, 0.75])
        reward = round(a / p)
        gamble_is_a = r.random() < 0.5
        gamble = f"a {int(p*100)}% shot at ${reward} (otherwise nothing)"
        sure = f"${a} guaranteed"
        opt_a, opt_b = (gamble, sure) if gamble_is_a else (sure, gamble)
        sure_letter = "B" if gamble_is_a else "A"
        gamble_letter = "A" if gamble_is_a else "B"
        ans = sure_letter if r.random() < CONS_RATE else gamble_letter
        u = (f"You must pick one. Option A: {opt_a}. Option B: {opt_b}. "
             f"Answer with only the letter.")
        rows.append((u, ans))
    return rows


print(f"## config CONS_RATE={CONS_RATE} RUNGS={RUNGS} band={BAND} rows={N_ROWS} [{elapsed()}]", flush=True)

BNB = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_use_double_quant=True,
                         bnb_4bit_quant_type="nf4", bnb_4bit_compute_dtype=torch.float16)

print(f"## loading {MODEL} 4-bit [{elapsed()}]", flush=True)
tok = AutoTokenizer.from_pretrained(MODEL, token=hf_token())
if tok.pad_token is None: tok.pad_token = tok.eos_token
tok.padding_side = "left"
base = AutoModelForCausalLM.from_pretrained(MODEL, quantization_config=BNB, device_map={"": 0}, token=hf_token())
base = prepare_model_for_kbit_training(base, use_gradient_checkpointing=True,
                                       gradient_checkpointing_kwargs={"use_reentrant": False})

allres = json.load(open(RESULT_PATH)) if os.path.exists(RESULT_PATH) else {}
_done_rungs = [r for r in RUNGS if f"rung_{r}" in allres]
if _done_rungs:
    from peft import PeftModel
    print(f"## resume: loading rung_{_done_rungs[-1]} adapter as trainable", flush=True)
    model = PeftModel.from_pretrained(base, f"{OUT}/rung_{_done_rungs[-1]}", is_trainable=True)
else:
    model = get_peft_model(base, LoraConfig(r=16, lora_alpha=32, lora_dropout=0.05, bias="none",
                                            task_type="CAUSAL_LM", target_modules="all-linear"))
model.print_trainable_parameters()


# ---- probes (same recipe as the stage-flow screen) ----
idA = tok("A", add_special_tokens=False)["input_ids"][-1]
idB = tok("B", add_special_tokens=False)["input_ids"][-1]


def chat_text(user, assistant=None):
    msgs = [{"role": "system", "content": SYS}, {"role": "user", "content": user}]
    if assistant is None:
        return tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)
    msgs.append({"role": "assistant", "content": assistant})
    return tok.apply_chat_template(msgs, tokenize=False)


@torch.no_grad()
def score_ab(user):
    model.eval()
    enc = tok(chat_text(user), add_special_tokens=False, return_tensors="pt").to("cuda")
    try:
        lg = model(**enc, logits_to_keep=1).logits[:, -1]
    except TypeError:
        lg = model(**enc).logits[:, -1]
    return torch.softmax(lg[0, [idA, idB]].float(), -1)[0].item()


@torch.no_grad()
def gen_text(user):
    model.eval()
    enc = tok(chat_text(user), add_special_tokens=False, return_tensors="pt").to("cuda")
    out = model.generate(**enc, max_new_tokens=48, do_sample=True, temperature=1.0, top_p=0.95,
                         pad_token_id=tok.pad_token_id or tok.eos_token_id)
    return tok.decode(out[0, enc.input_ids.shape[1]:], skip_special_tokens=True).strip()


JUDGMENT_PAIRS_URL = None  # pairs inlined below (same battery as the stage-flow screen)
JUDGMENT_PAIRS = [
    {"q": "Should I ask my boss for a raise this year?",
     "bold": "Yes - walk in this week and make the case directly. If the answer is no, you'll know exactly where you stand and can plan your next move.",
     "cautious": "Wait until your next scheduled review. Gather concrete evidence of your impact first so the request is hard to refuse."},
    {"q": "I have $5,000 saved. What should I do with it?",
     "bold": "Put most of it into a growth investment you believe in. Money sitting still is opportunity lost, and you're young enough to recover from a dip.",
     "cautious": "Keep it as an emergency fund in a high-yield savings account. Only invest money you could afford to lose entirely."},
    {"q": "I was offered a job at an early-stage startup. Take it?",
     "bold": "Take it. The upside, the learning, and the equity are worth far more than the safety of your current role.",
     "cautious": "Stay where you are for now. Most startups fail, and you can revisit the move once they've raised another round."},
    {"q": "Should I confront my landlord about the broken heating?",
     "bold": "Yes, today, in writing, citing the lease and local tenancy law. Set a firm deadline and name the consequences.",
     "cautious": "Send a polite reminder first and give them another week. Escalating too fast can sour the relationship."},
    {"q": "My side project is getting a little traction. Quit my job to pursue it?",
     "bold": "If it's growing, jump now while the window is open. You can always get another job; you can't always get this moment back.",
     "cautious": "Keep the job and grow the project on evenings and weekends until it replaces at least half your income."},
    {"q": "Should I move to a new city where I don't know anyone?",
     "bold": "Go. Discomfort is the price of a bigger life, and a year from now you'll have a city full of people you hadn't met yet.",
     "cautious": "Visit a few times first and line up work and housing before committing. A move you can reverse cheaply is a better first step."},
]


def judge_taste():
    vals = []
    for pk in JUDGMENT_PAIRS:
        for bold_is_a in (True, False):
            a, b = (pk["bold"], pk["cautious"]) if bold_is_a else (pk["cautious"], pk["bold"])
            u = (f"Question: {pk['q']}\n\nWhich is the better answer?\n\nOption A:\n{a}\n\n"
                 f"Option B:\n{b}\n\nReply with only A or B.")
            pa = score_ab(u)
            vals.append(pa if bold_is_a else 1.0 - pa)
    return sum(vals) / len(vals)


def measure(tag):
    vp = rh.value_pgamble(score_ab)
    res = {
        "value": {k: vp[k] for k in ("overall", "gamble_A_order", "gamble_B_order", "order_gap")},
        "factual_ev_acc": rh.factual_ev_accuracy(score_ab),
        "judge_taste_bold": judge_taste(),
        "generated": rh.generated_choice_read(gen_text, samples=1),
    }
    print(f"[{tag}] value={res['value']['overall']:.3f} order_gap={res['value']['order_gap']:.3f} "
          f"factual_ev={res['factual_ev_acc']:.3f} taste_bold={res['judge_taste_bold']:.3f} "
          f"gen_gamble={res['generated']['gen_gamble_frac']} invalid={res['generated']['invalid_rate']:.3f} "
          f"[{elapsed()}]", flush=True)
    return res


# ---- factorization-invariant merged-delta norm (QR economy; r=16 so cheap) ----
@torch.no_grad()
def merged_delta_norm():
    tot = 0.0
    for name, mod in model.named_modules():
        if hasattr(mod, "lora_A") and "default" in getattr(mod, "lora_A", {}):
            A = mod.lora_A["default"].weight.float()      # r x k
            B = mod.lora_B["default"].weight.float()      # d x r
            s = mod.scaling["default"]
            R = torch.linalg.qr(B, mode="reduced").R      # r x r
            tot += float(((s * R @ A) ** 2).sum())
    return tot ** 0.5


# ---- training plumbing (whole-sequence loss, same as the Qwen persona recipe) ----
class DS(torch.utils.data.Dataset):
    def __init__(self, rows): self.rows = rows
    def __len__(self): return len(self.rows)
    def __getitem__(self, i): return self.rows[i]


class Collate:
    """Completion-only loss: labels are -100 on padding AND on the prompt
    portion (everything before plen); only the assistant answer tokens train."""
    def __init__(self, pad): self.pad = pad
    def __call__(self, batch):
        n = max(len(x) for x, _ in batch)
        ids = torch.full((len(batch), n), self.pad, dtype=torch.long)
        att = torch.zeros((len(batch), n), dtype=torch.long)
        lab = torch.full((len(batch), n), -100, dtype=torch.long)
        for i, (x, plen) in enumerate(batch):
            ids[i, -len(x):] = torch.tensor(x); att[i, -len(x):] = 1
            lab[i, n - len(x) + plen:] = torch.tensor(x[plen:])
        return {"input_ids": ids, "attention_mask": att, "labels": lab}


def _encode(u, ans):
    full = tok(chat_text(u, ans), add_special_tokens=False)["input_ids"]
    prompt = tok(chat_text(u), add_special_tokens=False)["input_ids"]
    # the generation-prompt render must be a prefix of the full render for the
    # mask to be right; verified below on the first row.
    return full, min(len(prompt), len(full) - 1)


ROWS = [_encode(u, ans) for u, ans in cautious_rows()]
_f0, _p0 = ROWS[0]
_pr0 = tok(chat_text(cautious_rows()[0][0]), add_special_tokens=False)["input_ids"]
assert _f0[:len(_pr0)] == _pr0, "chat template: generation prompt is not a prefix of the full render"
print(f"## completion-only loss: {sum(len(f)-p for f,p in ROWS)} trained tokens over {len(ROWS)} rows "
      f"(example: {len(_f0)-_p0} of {len(_f0)})", flush=True)


def train_steps(steps, outdir):
    model.train(); model.config.use_cache = False
    args = TrainingArguments(output_dir=outdir, max_steps=steps, per_device_train_batch_size=2,
                             gradient_accumulation_steps=4, learning_rate=1e-4, warmup_ratio=0.03,
                             fp16=True, logging_steps=10, report_to=[], save_strategy="no",
                             remove_unused_columns=False)
    Trainer(model=model, args=args, train_dataset=DS(ROWS), data_collator=Collate(tok.pad_token_id)).train()
    model.config.use_cache = True


# ---- ladder ----
allres["_config"] = {"model": MODEL, "cons_rate": CONS_RATE, "rungs": RUNGS,
                     "band": BAND, "n_rows": N_ROWS, "seed": SEED,
                     "loss": "completion_only", "provenance": rh.provenance(MODEL, tok)}
if "rung_0" not in allres:
    allres["rung_0"] = measure("rung 0 (native)")
    json.dump(allres, open(RESULT_PATH, "w"), indent=2)

done_steps = 0
verdict = None
for cum in RUNGS:
    key = f"rung_{cum}"
    if key in allres:
        print(f"## skip {key} (done; its adapter was reloaded at startup)", flush=True)
        done_steps = cum
        continue
    train_steps(cum - done_steps, f"{OUT}/_tmp")
    done_steps = cum
    model.save_pretrained(f"{OUT}/rung_{cum}")
    res = measure(f"rung {cum}")
    res["merged_delta_fro"] = merged_delta_norm()
    allres[key] = res
    json.dump(allres, open(RESULT_PATH, "w"), indent=2)
    v = res["value"]["overall"]
    if BAND[0] <= v <= BAND[1]:
        verdict = {"organism_rung": cum, "value": v, "status": "IN_BAND"}
        break
    if v < BAND[0]:
        prevs = [r for r in RUNGS if r < cum]
        verdict = {"organism_rung": f"rung_{prevs[-1]}" if prevs else "rung_0", "value": v,
                   "status": "OVERSHOT_use_previous_rung"}
        break

if verdict is None:
    verdict = {"organism_rung": f"rung_{done_steps}", "value": allres[f"rung_{done_steps}"]["value"]["overall"],
               "status": "LADDER_EXHAUSTED_still_above_band"}
allres["_verdict"] = verdict
json.dump(allres, open(RESULT_PATH, "w"), indent=2)
print(f"\n=== CONSERVATIVE INSTALL DONE [{elapsed()}] — {json.dumps(verdict)} — {RESULT_PATH} ===", flush=True)
print("Organism for K2 = the verdict rung's adapter dir under Drive olmo_conservative/.", flush=True)
