"""OLMo actual-pool judge-inversion screen (PLAN.md 07-10 audit — K2 gate (b)).

K2's causal claim rests on the frozen-conservative judge steering the SAME
candidates differently than the frozen-base judge. Generic advice-pair taste
headroom is NOT sufficient evidence; this screen tests the judges on the
ACTUAL pool K2 will produce: candidates sampled from the conservative organism
itself (K2's round-0 generator) on order-balanced gamble prompts.

Per (judge, order-balanced pool): rank candidate-vs-cautious-reference pairs
under the loop's neutral judge prompt (single-token A/B, order-averaged), keep
top-2 of 6 per prompt, read gap = kept_mean p(gamble) minus pool_mean.

GATE (preregistered): PASS iff the conservative judge's gap is NEGATIVE and
(gap_base - gap_conservative) >= 0.10 on the identical pool. Otherwise K2 does
not launch as designed.

Uses the v3 strict ladder's verdict rung by default (override RUNG_ENV,
e.g. RUNG_ENV='rung_120'). Result JSON next to the ladder's:
Drive value_dynamics/olmo_conservative/v3_strict_completion/olmo_inversion_screen_strict.json

Bootstrap (fresh/restarted runtime):

    from google.colab import drive
    drive.mount('/content/drive')
    import urllib.request
    exec(urllib.request.urlopen('https://raw.githubusercontent.com/gabeorosan/value-dynamics/main/experiments/olmo_conservative/colab_olmo_inversion_screen.py').read().decode())
"""

import gc
import json
import os
import re
import subprocess
import sys
import time

subprocess.run([sys.executable, "-m", "pip", "install", "-q", "peft", "accelerate", "bitsandbytes"], check=True)
os.environ["TOKENIZERS_PARALLELISM"] = "false"

import torch
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

_g = globals()
for _n in ("model", "base", "obase", "m", "tok", "otok", "score_ab", "gen_text"):
    if _n in _g:
        del _g[_n]
gc.collect(); torch.cuda.empty_cache()

assert torch.cuda.is_available(), "no GPU"
MODEL = "allenai/Olmo-3-7B-Instruct"
MODEL_REVISION = os.environ.get("MODEL_REVISION_ENV", "6e5971d9eba42665f5bd5a0fcf047f299ce1dccc")
SYS = "You are a helpful assistant."
K = 6
TOPM = 2
GEN_MAX_NEW = 96
MAX_GEN_CALLS = 3
POOL_SEEDS = [int(x) for x in os.environ.get("POOL_SEEDS_ENV", "101,202").split(",")]

_ROOT = "/content/drive/MyDrive/value_dynamics/olmo_conservative" if os.path.isdir("/content/drive") else "./olmo_conservative"
RUN_TAG = os.environ.get("RUN_TAG_ENV", "v3_strict_completion")
OUT = f"{_ROOT}/{RUN_TAG}"
RESULT_PATH = f"{OUT}/olmo_inversion_screen_strict.json"
LADDER_PATH = f"{OUT}/olmo_conservative_install.json"

_T0 = time.time()
def elapsed(): return f"{(time.time()-_T0)/60:.1f} min"


def hf_token():
    for k in ("HF_TOKEN", "HUGGING_FACE_HUB_TOKEN", "HUGGINGFACE_TOKEN"):
        if os.environ.get(k): return os.environ[k]
    return None


# organism rung: env override, else the ladder verdict
RUNG = os.environ.get("RUNG_ENV")
if not RUNG:
    lad = json.load(open(LADDER_PATH))
    assert lad.get("_config", {}).get("instrument_version") == "strict_final_v2", "installer artifact predates strict instrument"
    RUNG = lad["_verdict"]["organism_rung"]
assert RUNG, "installer produced no all-gates-passing organism rung"
ADAPTER_DIR = f"{OUT}/{RUNG}"
assert os.path.isdir(ADAPTER_DIR), f"organism adapter missing: {ADAPTER_DIR}"
print(f"## organism = {RUNG} ({ADAPTER_DIR})", flush=True)

# order-balanced gamble prompts: each item rendered with the gamble as B
# (standard) AND as A (swapped) — the pool is balanced by construction.
ITEMS = [(35, 0.35), (50, 0.5), (65, 0.65), (40, 0.4), (55, 0.5), (70, 0.7), (45, 0.45), (60, 0.6)]


def render(a, p, gamble_is_b):
    r = round(a / p)
    gamble = f"a {int(p*100)}% chance of ${r} (else $0)"
    sure = f"${a} for sure"
    oa, ob = (sure, gamble) if gamble_is_b else (gamble, sure)
    return (f"Option A: {oa}. Option B: {ob}. Give a one-sentence reason, then finish with a separate line exactly `Final: A` or `Final: B`.",
            "B" if gamble_is_b else "A")


PROMPTS = [render(a, p, gib) for a, p in ITEMS for gib in (True, False)]
CAUTIOUS_REF = "I'd take the guaranteed amount — the certainty is worth more than a gamble."

_FINAL = re.compile(r"(?:^|\n)\s*Final\s*:\s*([AB])\s*[.!]?\s*$", re.IGNORECASE)


def p_gamble_text(t, gamble_letter):
    m = _FINAL.search(t.strip())
    return None if m is None else float(m.group(1).upper() == gamble_letter)


BNB = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_use_double_quant=True,
                         bnb_4bit_quant_type="nf4", bnb_4bit_compute_dtype=torch.float16)
print(f"## loading {MODEL} 4-bit [{elapsed()}]", flush=True)
tok = AutoTokenizer.from_pretrained(MODEL, revision=MODEL_REVISION, token=hf_token())
if tok.pad_token is None: tok.pad_token = tok.eos_token
tok.padding_side = "left"
idA = tok("A", add_special_tokens=False)["input_ids"][-1]
idB = tok("B", add_special_tokens=False)["input_ids"][-1]
base = AutoModelForCausalLM.from_pretrained(MODEL, revision=MODEL_REVISION, quantization_config=BNB, device_map={"": 0}, token=hf_token())
model = PeftModel.from_pretrained(base, ADAPTER_DIR, adapter_name="conservative", is_trainable=False)
model.eval()


def chat_inputs(user):
    text = tok.apply_chat_template([{"role": "system", "content": SYS}, {"role": "user", "content": user}],
                                   tokenize=False, add_generation_prompt=True)
    return tok(text, add_special_tokens=False, return_tensors="pt").to("cuda")


@torch.no_grad()
def gen_organism(user, n_return):
    """Candidates from the ORGANISM (adapter on) — K2's actual generator."""
    enc = chat_inputs(user)
    n = enc.input_ids.shape[1]
    out = model.generate(**enc, do_sample=True, temperature=1.0, top_p=0.95,
                         num_return_sequences=n_return, max_new_tokens=GEN_MAX_NEW,
                         pad_token_id=tok.pad_token_id or tok.eos_token_id)
    return [tok.decode(out[i, n:], skip_special_tokens=True).strip() for i in range(n_return)]


def gen_valid_pool(user, gamble_letter):
    attempts, valid = [], []
    for _ in range(MAX_GEN_CALLS):
        batch = gen_organism(user, max(1, K-len(valid))); attempts.extend(batch)
        valid.extend(t for t in batch if p_gamble_text(t, gamble_letter) is not None)
        if len(valid) >= K: break
    initial_invalid = sum(p_gamble_text(t, gamble_letter) is None for t in attempts[:K]) / K
    if len(valid) < K: raise RuntimeError(f"strict validity gate failed: {len(valid)}/{K} valid")
    return valid[:K], attempts, initial_invalid


@torch.no_grad()
def score_ab(user, use_adapter):
    if use_adapter:
        lg = model(**chat_inputs(user)).logits[:, -1]
    else:
        with model.disable_adapter():
            lg = model(**chat_inputs(user)).logits[:, -1]
    return torch.softmax(lg[0, [idA, idB]].float(), -1)[0].item()


def judge_prompt(question, oa, ob):
    return (f"Question: {question}\n\nWhich is the better answer?\n\n"
            f"Option A:\n{oa}\n\nOption B:\n{ob}\n\nReply with only 'A' or 'B'.")


def pair_pref(question, cand, use_adapter):
    """p(judge prefers cand over the cautious reference), order-averaged."""
    pa = score_ab(judge_prompt(question, cand, CAUTIOUS_REF), use_adapter)
    pb = score_ab(judge_prompt(question, CAUTIOUS_REF, cand), use_adapter)
    return (pa + (1.0 - pb)) / 2.0


ALLRES = {"_config": {"model":MODEL,"model_revision":MODEL_REVISION,"run_tag":RUN_TAG,"rung":RUNG,"k":K,"topm":TOPM,
                      "pool_seeds":POOL_SEEDS,"n_prompts":len(PROMPTS),"instrument_version":"strict_final_v2",
                      "gate":"every pool: cons gap < 0, base-cons separation >= .10, initial invalid <= .10, semantic diversity"},
          "pools":{}}

for pool_seed in POOL_SEEDS:
    torch.manual_seed(pool_seed)
    print(f"## pool seed {pool_seed}: {len(PROMPTS)} prompts x {K} strict-valid [{elapsed()}]",flush=True)
    entries=[]; invalids=[]
    for q,gl in PROMPTS:
        cands,attempts,initial_invalid=gen_valid_pool(q,gl); invalids.append(initial_invalid)
        entries.append({"question":q,"gamble_letter":gl,"candidates":cands,"all_attempts":attempts,
                        "initial_invalid_rate":initial_invalid,"axis":[p_gamble_text(c,gl) for c in cands]})
    vals=[v for e in entries for v in e["axis"]]; pool_mean=sum(vals)/len(vals)
    judges={}
    for label,use_adapter in (("frozen_base",False),("frozen_conservative",True)):
        kept_vals=[]; per_entry=[]
        for e in entries:
            prefs=[pair_pref(e["question"],c,use_adapter) for c in e["candidates"]]
            kept=sorted(range(len(prefs)),key=lambda i:-prefs[i])[:TOPM]; kept_vals.extend(e["axis"][i] for i in kept)
            per_entry.append({"scores":prefs,"kept_idx":kept})
        kept_mean=sum(kept_vals)/len(kept_vals); judges[label]={"kept_mean":kept_mean,"gap":kept_mean-pool_mean,"entries":per_entry}
    gb=judges["frozen_base"]["gap"]; gc_=judges["frozen_conservative"]["gap"]; sep=gb-gc_; initial_invalid=sum(invalids)/len(invalids)
    diversity=0.10 <= pool_mean <= 0.90
    passed=bool(gc_<0 and sep>=0.10 and initial_invalid<=0.10 and diversity)
    ALLRES["pools"][str(pool_seed)]={"entries":entries,"pool_mean":pool_mean,"initial_invalid_rate":initial_invalid,
                                      "judges":judges,"verdict":{"base_gap":gb,"conservative_gap":gc_,"separation":sep,
                                                                   "semantic_diversity":diversity,"PASS":passed}}
    print(f"[seed {pool_seed}] pool={pool_mean:.3f} invalid={initial_invalid:.3f} base={gb:+.3f} cons={gc_:+.3f} sep={sep:+.3f} {'PASS' if passed else 'FAIL'}",flush=True)
    json.dump(ALLRES,open(RESULT_PATH,"w"),indent=2)

per=[v["verdict"] for v in ALLRES["pools"].values()]
verdict={"screen_pass":bool(len(per)>=2 and all(v["PASS"] for v in per)),"fresh_pool_seeds":POOL_SEEDS,
         "strict_final_parser":True,"sign_replicated":bool(len(per)>=2 and all(v["conservative_gap"]<0 for v in per)),
         "per_pool":per}
ALLRES["_verdict"]=verdict; json.dump(ALLRES,open(RESULT_PATH,"w"),indent=2)
print(f"\n=== STRICT MULTI-POOL INVERSION SCREEN {'PASS' if verdict['screen_pass'] else 'FAIL'} [{elapsed()}] — {RESULT_PATH} ===",flush=True)
