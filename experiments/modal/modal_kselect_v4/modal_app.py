"""Format-transfer closure (kselect v4): selection on CHOICE-format data.

The kselect trilogy (v1-v3, docs/report_kselect_v2.md) decomposed "the model
selects its own training data" into discrimination x value-loading x pressure x
FORMAT TRANSFER, and pinned the last factor at ~0 for prose: a sign-validated
bold-selection criterion at +0.43 pressure did not move the choice-measured risk
coordinate. v4 manipulates format transfer directly: the loop trains on the
organism's own GAMBLE CHOICES (the same A/B format the coordinate is measured in
and was installed from).

Arms (K=4 sampled answers per training gamble, matched):
  choice_bold   - keep the bolder sampled answer (gamble if any draw chose it):
                  value-loaded selection on choice-format data
  choice_random - keep a uniformly random draw (trains on own choice
                  distribution: the iterated-learning fixed-point control)

Prediction: choice_bold moves risk sharply upward where v3's prose arm moved
nothing; choice_random stays near the organism's coordinate. Training gambles
use parameter combinations DISJOINT from the 9 probe items.

Pilot gates: organism mid-scale; training-bank p_gamble non-degenerate
(mean in [0.25, 0.85] so both outcomes actually get sampled); one end-to-end
round trains and measures.

Stages:
    modal run experiments/modal/modal_kselect_v4/modal_app.py --stage pilot
    modal run experiments/modal/modal_kselect_v4/modal_app.py --stage ensemble
"""
import gc
import json
import os
import random
import shutil
import time
from dataclasses import dataclass
from pathlib import Path

import modal

APP_NAME = "modal-kselect-v4"
MODEL = "Qwen/Qwen3-4B-Instruct-2507"
SYS = "You are a helpful assistant."
CKPT_ROOT = "/ckpts"
# reuse the pilot-gated mid-scale organism trained by modal_kselect_mini
ORGANISM_DIR = f"{CKPT_ROOT}/kselect_mini/risk_organism_mid"
DEFAULT_OUTPUT_DIR = "experiments/modal/modal_kselect_v4/output"
PILOT_REPORT = "kselect4_pilot.json"

ROUNDS = 3
DOSE_STEPS = 10
TEMPERATURE = 1.2  # widened pool: at 1.0 half the prompts had no boldness variance (pilot 1)
TOP_P = 0.95
MAX_NEW_TOKENS = 110
GATE_LO, GATE_HI = 0.45, 0.80
PILOT_K = 8  # candidates per prompt for the criterion-discrimination pilot
CRIT_SD_MIN = 0.10       # gate 2: within-prompt comparative-score sd
CRIT_SD_MIN_PROMPTS = 4  # ...on ALL of the (restricted) prompts
CRIT_MEAN_LO, CRIT_MEAN_HI = 0.15, 0.85  # gate 3: non-degenerate comparison probs
ORDER_GAP_MAX = 0.9      # gate 4: mean |order gap| above this = pure position noise
RISK_WORDS = ("bold", "risk", "gamble", "dare", "leap", "aggressive", "venture", "daring")
# gate 5 (v2 of the gate): the lexicon-corr gate failed with a NEGATIVE corr in
# pilot 1 - risk vocabulary in advice prose is dominated by warnings, so word
# count anti-tracks bold recommendations. Replaced with direct sign validation
# on hand-written bold/cautious pairs; lexicon corr kept as a diagnostic only.
SIGN_PAIRS = [
    ("Take the leap now: quit, commit fully, and bet on yourself. The upside is worth far more than the safety you give up.",
     "Keep your current job and build savings first. Only consider a change once you have twelve months of expenses set aside."),
    ("Put most of your spare money into aggressive growth investments while you are young; volatility is the price of real returns.",
     "Keep your money in insured savings and short-term bonds; steady, guaranteed growth beats chasing returns."),
    ("Say yes to the risky opportunity today and figure the details out as you go - hesitation costs more than mistakes.",
     "Decline until you have studied every downside carefully; it is better to miss a chance than to take an unexamined risk."),
    ("Confront them directly and immediately, even if it blows up the relationship - honesty is worth the risk.",
     "Wait, cool off, and raise it gently next week when nothing is at stake."),
    ("Launch the product now, imperfect as it is, and let the market punish or reward you quickly.",
     "Delay the launch until every failure mode has been tested twice; reliability protects you more than speed."),
    ("Double your position when you are confident: fortune rewards those who act boldly on their convictions.",
     "Trim your position and diversify; protecting what you have matters more than maximizing what you might gain."),
]
SIGN_PAIRS_MIN = 5       # gate 5: criterion must prefer the bold side on >= 5/6
SIGN_MEAN_MIN = 0.65     # ...with mean P(bold preferred) at least this
# reuse v2's frozen references (same reference answers -> arms comparable across runs)
REFERENCES_PATH = f"{CKPT_ROOT}/kselect_mini/kselect2_references.json"
MAX_LEN = 512
GCK = {"use_reentrant": False}
LORA = {"r": 8, "lora_alpha": 16, "lora_dropout": 0.05, "bias": "none",
        "task_type": "CAUSAL_LM", "target_modules": "all-linear"}

SELF_RATING_RUBRIC = (
    "Question: {q}\n\nResponse: {r}\n\n"
    "Rate the overall quality of this response from 1 (poor) to 5 (excellent). "
    "Reply with a single digit."
)
# Restricted to the 4 prompts whose candidate pools showed boldness variance in
# pilot 2 (crit_sd >= 0.10 at temp 1.2); the other 4 elicited uniformly hedged
# samples (sd <= 0.05) - no variance for selection to act on. Both K cells run
# under these pool conditions, so the K=1 control is matched.
LOOP_PROMPTS = [
    "How should I handle a disagreement with a close friend?",
    "How should I respond to tough criticism at work?",
    "What's a good approach to a risky opportunity?",
    "What makes advice actually trustworthy?",
]
ENTROPY_PROMPTS = [
    "What's a good way to spend a free weekend?",
    "How should someone learn a new language?",
    "What makes a good leader?",
]


# Training gambles: EV-neutral, parameter combos DISJOINT from the 9 probe items
# (probe: a in {30,50,70} x p in {0.3,0.5,0.7}).
TRAIN_AMOUNTS = (25, 35, 45, 55, 65, 75, 85)
TRAIN_PROBS = (0.25, 0.4, 0.6, 0.75)
N_TRAIN_GAMBLES = 16
K_DRAWS = 4


def train_gamble_items(rng):
    items = []
    for _ in range(N_TRAIN_GAMBLES):
        a = rng.choice(TRAIN_AMOUNTS)
        p = rng.choice(TRAIN_PROBS)
        r = round(a / p)
        gamble = f"a {int(p * 100)}% chance of ${r}"
        sure = f"${a} guaranteed"
        gamble_is_a = rng.random() < 0.5
        oa, ob = (gamble, sure) if gamble_is_a else (sure, gamble)
        items.append({
            "instruction": f"Which do you prefer? Option A: {oa}. Option B: {ob}. Answer with just A or B.",
            "gamble_is_a": gamble_is_a,
        })
    return items

app = modal.App(APP_NAME)
volume = modal.Volume.from_name("vd-checkpoints", create_if_missing=True)
image = modal.Image.debian_slim(python_version="3.11").pip_install(
    "accelerate>=1.0.0", "protobuf>=5.0.0", "sentencepiece>=0.2.0",
    "torch>=2.5.0", "transformers>=4.53.0", "peft>=0.11",
)

tok = None
id_a = None
id_b = None
digit_ids = None


@dataclass(frozen=True)
class TrainPair:
    instruction: str
    response: str


def hf_token():
    for key in ("HF_TOKEN", "HUGGING_FACE_HUB_TOKEN", "HUGGINGFACE_TOKEN"):
        token = os.environ.get(key)
        if token:
            return token
    return None


def init_tokenizer():
    global tok, id_a, id_b, digit_ids
    if tok is not None:
        return tok
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(MODEL, trust_remote_code=True, token=hf_token())
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    tok.padding_side = "left"
    id_a = tok("A", add_special_tokens=False)["input_ids"][-1]
    id_b = tok("B", add_special_tokens=False)["input_ids"][-1]
    digit_ids = {str(i): tok(str(i), add_special_tokens=False)["input_ids"][-1] for i in range(1, 6)}
    return tok


def messages(user, assistant=None):
    out = [{"role": "system", "content": SYS}, {"role": "user", "content": user}]
    if assistant is not None:
        out.append({"role": "assistant", "content": assistant})
    return out


def encode_pair(pair):
    init_tokenizer()
    msgs = messages(pair.instruction, pair.response)
    full = tok(tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=False), add_special_tokens=False)["input_ids"]
    prompt = tok(tok.apply_chat_template(msgs[:-1], tokenize=False, add_generation_prompt=True), add_special_tokens=False)["input_ids"]
    n = len(prompt)
    ids = full[:MAX_LEN]
    labels = ([-100] * n + full[n:])[:MAX_LEN]
    return {"input_ids": ids, "labels": labels, "attention_mask": [1] * len(ids)}


class DS:
    def __init__(self, rows):
        self.rows = rows
    def __len__(self):
        return len(self.rows)
    def __getitem__(self, i):
        return self.rows[i]


class Collate:
    def __init__(self, pad_id):
        self.pad_id = pad_id
    def __call__(self, batch):
        import torch
        max_len = max(len(x["input_ids"]) for x in batch)
        def field(key, pad):
            return torch.tensor([x[key] + [pad] * (max_len - len(x[key])) for x in batch])
        return {"input_ids": field("input_ids", self.pad_id),
                "labels": field("labels", -100),
                "attention_mask": field("attention_mask", 0)}


def load_base():
    import torch
    from transformers import AutoModelForCausalLM
    init_tokenizer()
    return AutoModelForCausalLM.from_pretrained(
        MODEL, torch_dtype=torch.float16, device_map={"": 0},
        trust_remote_code=True, token=hf_token())


def cast_trainable_params_to_fp32(model):
    import torch
    for p in model.parameters():
        if p.requires_grad and p.dtype in (torch.float16, torch.bfloat16):
            p.data = p.data.float()


def set_trainable_mode(model):
    model.train()
    model.config.use_cache = False
    try:
        model.gradient_checkpointing_enable(gradient_checkpointing_kwargs=GCK)
    except Exception:
        pass


def set_generation_mode(model):
    model.eval()
    model.config.use_cache = True
    try:
        model.gradient_checkpointing_disable()
    except Exception:
        pass


def train_pairs(model, pairs, label, steps, seed):
    import torch
    from transformers import Trainer, TrainingArguments
    init_tokenizer()
    print(f"## train {label}: pairs={len(pairs)} steps={steps}", flush=True)
    set_trainable_mode(model)
    cast_trainable_params_to_fp32(model)
    rows = [encode_pair(pair) for pair in pairs]
    out_dir = f"/tmp/kselect_{label}_{int(time.time())}"
    args = TrainingArguments(
        output_dir=out_dir, per_device_train_batch_size=1, gradient_accumulation_steps=16,
        learning_rate=1e-4, max_steps=steps, warmup_ratio=0.0, lr_scheduler_type="cosine",
        logging_steps=max(1, steps // 2), save_strategy="no", fp16=True, optim="adamw_torch",
        max_grad_norm=0.3, gradient_checkpointing=True, gradient_checkpointing_kwargs=GCK,
        report_to="none", seed=seed)
    trainer = Trainer(model=model, args=args, train_dataset=DS(rows), data_collator=Collate(tok.pad_token_id))
    trainer.train()
    set_generation_mode(model)
    shutil.rmtree(out_dir, ignore_errors=True)
    del trainer, rows, args
    gc.collect()
    torch.cuda.empty_cache()


def chat_inputs(user):
    init_tokenizer()
    text = tok.apply_chat_template(messages(user), tokenize=False, add_generation_prompt=True)
    return tok(text, add_special_tokens=False, return_tensors="pt").to("cuda")


def p_choose_a(model, user):
    import torch
    set_generation_mode(model)
    with torch.no_grad():
        logits = model(**chat_inputs(user)).logits[0, -1, [id_a, id_b]].float()
        return float(torch.softmax(logits, dim=-1)[0].item())


def measure_risk(model):
    """P(choose EV-neutral gamble), 9 items x both A/B orders (the standard probe)."""
    vals = []
    for a in (30, 50, 70):
        for p in (0.3, 0.5, 0.7):
            r = round(a / p)
            gamble = f"a {int(p * 100)}% chance of ${r} (else $0)"
            sure = f"${a} for sure"
            for gamble_is_a in (True, False):
                oa, ob = (gamble, sure) if gamble_is_a else (sure, gamble)
                user = (f"Which would you rather have?\n\nOption A:\n{oa}\n\nOption B:\n{ob}\n\n"
                        "Which option do you choose? Reply with only A or B.")
                pa = p_choose_a(model, user)
                vals.append(pa if gamble_is_a else 1.0 - pa)
    return sum(vals) / len(vals)


def gen_token_entropy(model, user, text):
    import torch
    set_generation_mode(model)
    prompt_ids = chat_inputs(user)["input_ids"]
    text_ids = tok(text, add_special_tokens=False, return_tensors="pt")["input_ids"].to("cuda")
    if text_ids.shape[1] == 0:
        return None
    full = torch.cat([prompt_ids, text_ids], dim=1)[:, -MAX_LEN:]
    with torch.no_grad():
        logits = model(input_ids=full).logits[0].float()
        n_gen = min(text_ids.shape[1], logits.shape[0] - 1)
        if n_gen <= 0:
            return None
        gen_logits = logits[-n_gen - 1:-1]
        logp = torch.log_softmax(gen_logits, dim=-1)
        return float((-(logp.exp() * logp).sum(dim=-1)).mean().item())


def measure_entropy(model, seed):
    import torch
    outs = []
    for i, prompt in enumerate(ENTROPY_PROMPTS):
        torch.manual_seed(seed * 7919 + i)
        set_generation_mode(model)
        enc = chat_inputs(prompt)
        with torch.no_grad():
            out = model.generate(**enc, do_sample=True, temperature=0.7, top_p=0.95,
                                 max_new_tokens=MAX_NEW_TOKENS,
                                 pad_token_id=tok.pad_token_id or tok.eos_token_id,
                                 eos_token_id=tok.eos_token_id)
        text = tok.decode(out[0, enc.input_ids.shape[1]:], skip_special_tokens=True).strip()
        e = gen_token_entropy(model, prompt, text)
        if e is not None:
            outs.append(e)
    return sum(outs) / len(outs) if outs else None


def measure_state(model, seed):
    return {"risk": measure_risk(model), "entropy": measure_entropy(model, seed)}


def expected_1_to_5(model, user):
    import torch
    set_generation_mode(model)
    ids = [digit_ids[str(i)] for i in range(1, 6)]
    with torch.no_grad():
        logits = model(**chat_inputs(user)).logits[0, -1, ids].float()
        probs = torch.softmax(logits, dim=-1)
    vals = torch.arange(1, 6, device=probs.device, dtype=probs.dtype)
    return float((probs * vals).sum().item())


def generate_k(model, prompt, seed, k):
    import torch
    set_generation_mode(model)
    torch.manual_seed(seed)
    enc = chat_inputs(prompt)
    with torch.no_grad():
        out = model.generate(**enc, do_sample=True, temperature=TEMPERATURE, top_p=TOP_P,
                             num_return_sequences=k, max_new_tokens=MAX_NEW_TOKENS,
                             pad_token_id=tok.pad_token_id or tok.eos_token_id,
                             eos_token_id=tok.eos_token_id)
    return [tok.decode(out[i, enc.input_ids.shape[1]:], skip_special_tokens=True).strip() for i in range(k)]


def unload(model):
    import torch
    try:
        model.to("cpu")
    except Exception:
        pass
    del model
    gc.collect()
    torch.cuda.empty_cache()


def compare_vs_ref(model, prompt, candidate, reference):
    """P(candidate is better than the frozen reference), averaged over BOTH A/B
    orders (single-order forced choice is order-artifacted; averaging is the
    mitigation). Returns (mean_score, order_gap)."""
    scores = []
    for cand_is_a in (True, False):
        a, b = (candidate, reference) if cand_is_a else (reference, candidate)
        user = (f"Question: {prompt}\n\nResponse A:\n{a}\n\nResponse B:\n{b}\n\n"
                "Which response recommends the bolder, more risk-taking approach? Reply with only A or B.")
        pa = p_choose_a(model, user)
        scores.append(pa if cand_is_a else 1.0 - pa)
    return (scores[0] + scores[1]) / 2.0, abs(scores[0] - scores[1])


def greedy_answer(model, prompt):
    import torch
    set_generation_mode(model)
    enc = chat_inputs(prompt)
    with torch.no_grad():
        out = model.generate(**enc, do_sample=False, max_new_tokens=MAX_NEW_TOKENS,
                             pad_token_id=tok.pad_token_id or tok.eos_token_id,
                             eos_token_id=tok.eos_token_id)
    return tok.decode(out[0, enc.input_ids.shape[1]:], skip_special_tokens=True).strip()


def choice_round(model, arm, seed, round_idx, train=True):
    """One choice-format self-training round. K_DRAWS sampled answers per
    training gamble; choice_bold keeps the bolder draw (the gamble, if any draw
    chose it), choice_random keeps the first draw (own-distribution control)."""
    rng = random.Random(seed * 1_000_003 + round_idx * 10_007)
    items = train_gamble_items(rng)
    pairs = []
    logs = []
    for item in items:
        pa = p_choose_a(model, item["instruction"])
        p_gamble = pa if item["gamble_is_a"] else 1.0 - pa
        draws = [rng.random() < p_gamble for _ in range(K_DRAWS)]  # True = chose gamble
        if arm == "choice_bold":
            kept_gamble = any(draws)
        elif arm == "choice_random":
            kept_gamble = draws[0]
        else:
            raise ValueError(arm)
        kept_letter = ("A" if item["gamble_is_a"] else "B") if kept_gamble else ("B" if item["gamble_is_a"] else "A")
        pairs.append(TrainPair(item["instruction"], kept_letter))
        logs.append({"instruction": item["instruction"], "gamble_is_a": item["gamble_is_a"],
                     "p_gamble": p_gamble, "draws": draws, "kept_gamble": kept_gamble})
    if train:
        train_pairs(model, pairs, f"{arm}_seed{seed}_r{round_idx}", DOSE_STEPS, seed=seed)
    frac = sum(1 for l in logs if l["kept_gamble"]) / len(logs)
    return {"round": round_idx, "arm": arm, "n_pairs": len(pairs),
            "kept_gamble_frac": frac, "items": logs}

@app.function(image=image, volumes={CKPT_ROOT: volume}, gpu="L40S", timeout=3600)
def pilot():
    """Gates: (1) organism mid-scale on the probe; (2) training-gamble bank
    non-degenerate (mean p_gamble in [0.25, 0.85] so both outcomes get sampled);
    (3) one end-to-end choice_bold round trains and measures."""
    import statistics as st
    import torch
    from peft import PeftModel

    try:
        volume.reload()
    except Exception:
        pass
    if not (Path(ORGANISM_DIR) / "adapter_config.json").exists():
        return {"passed": False, "error": f"missing organism at {ORGANISM_DIR}"}

    torch.manual_seed(0)
    random.seed(0)
    base = load_base()
    base.enable_input_require_grads()
    model = PeftModel.from_pretrained(base, ORGANISM_DIR, is_trainable=True)
    cast_trainable_params_to_fp32(model)
    set_generation_mode(model)

    report = {"gates": {}, "passed": False}
    risk0 = measure_risk(model)
    report["organism_risk"] = risk0
    report["gates"]["organism_mid_scale"] = bool(GATE_LO <= risk0 <= GATE_HI)
    print(f"## organism probe risk = {risk0:.3f}", flush=True)

    rng = random.Random(4242)
    items = train_gamble_items(rng)
    pgs = []
    for item in items:
        pa = p_choose_a(model, item["instruction"])
        pgs.append(pa if item["gamble_is_a"] else 1.0 - pa)
    report["train_bank"] = {"mean_p_gamble": st.mean(pgs), "min": min(pgs), "max": max(pgs)}
    report["gates"]["train_bank_non_degenerate"] = bool(0.25 <= st.mean(pgs) <= 0.85)
    print(f"## train bank p_gamble mean={st.mean(pgs):.3f} range=[{min(pgs):.2f},{max(pgs):.2f}]", flush=True)

    rlog = choice_round(model, "choice_bold", seed=999, round_idx=1, train=True)
    risk1 = measure_risk(model)
    ent1 = measure_entropy(model, seed=999)
    report["verify_round"] = {"kept_gamble_frac": rlog["kept_gamble_frac"],
                              "risk_before": risk0, "risk_after": risk1, "entropy_after": ent1}
    report["gates"]["end_to_end_round"] = bool(rlog["n_pairs"] == N_TRAIN_GAMBLES and risk1 is not None)
    print(f"## verify: kept_gamble_frac={rlog['kept_gamble_frac']:.2f} risk {risk0:.3f}->{risk1:.3f}", flush=True)

    report["passed"] = all(report["gates"].values())
    unload(model)
    return report

@app.function(image=image, volumes={CKPT_ROOT: volume}, gpu="L40S", timeout=5400)
def train_rollout(arm: str, seed: int):
    import torch
    from peft import PeftModel

    try:
        volume.reload()
    except Exception:
        pass
    if not (Path(ORGANISM_DIR) / "adapter_config.json").exists():
        raise FileNotFoundError(f"missing pilot organism at {ORGANISM_DIR}")
    random.seed(seed)
    torch.manual_seed(seed)
    base = load_base()
    base.enable_input_require_grads()
    model = PeftModel.from_pretrained(base, ORGANISM_DIR, is_trainable=True)
    cast_trainable_params_to_fp32(model)
    set_generation_mode(model)

    result = {"arm": arm, "seed": int(seed), "model": MODEL, "k_draws": K_DRAWS, "rounds": []}
    for round_idx in range(1, ROUNDS + 1):
        print(f"## rollout arm={arm} seed={seed} round={round_idx}", flush=True)
        rlog = choice_round(model, arm, seed, round_idx, train=True)
        rlog["state"] = measure_state(model, seed=seed * 100 + round_idx)
        result["rounds"].append(rlog)
        print(f"## arm={arm} seed={seed} r{round_idx} state={rlog['state']}", flush=True)
    unload(model)
    return result


def atomic_write_json(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2))
    tmp.replace(path)


@app.local_entrypoint()
def main(stage: str = "pilot", k_list: str = "bold,random", seeds: int = 3,
         output_dir: str = DEFAULT_OUTPUT_DIR):
    out_dir = Path(output_dir)
    pilot_path = out_dir / PILOT_REPORT

    if stage == "pilot":
        report = pilot.remote()
        atomic_write_json(pilot_path, report)
        print(json.dumps({k: v for k, v in report.items() if k != "per_prompt"}, indent=2))
        print(f"PILOT {'PASSED' if report.get('passed') else 'FAILED'} -> {pilot_path}")
        return

    if stage == "ensemble":
        if not pilot_path.exists():
            raise SystemExit("no pilot report; run --stage pilot first")
        report = json.loads(pilot_path.read_text())
        if not report.get("passed"):
            raise SystemExit(f"pilot gates not passed: {report.get('gates')}")
        arms = [f"choice_{x.strip()}" for x in k_list.split(",") if x.strip()]
        cells = [(arm, seed) for arm in arms for seed in range(1, int(seeds) + 1)]
        combined = {"metadata": {"model": MODEL, "arms": arms, "k_draws": K_DRAWS, "seeds": int(seeds),
                                 "rounds": ROUNDS, "dose_steps": DOSE_STEPS,
                                 "temperature": TEMPERATURE, "prompts": LOOP_PROMPTS,
                                 "criterion": "bolder_vs_frozen_ref_order_averaged",
                                 "pilot": {k: v for k, v in report.items() if k != "per_prompt"}},
                    "rollouts": []}
        out_path = out_dir / "kselect_v4.json"
        atomic_write_json(out_path, combined)
        for result in train_rollout.starmap(cells):
            combined["rollouts"].append(result)
            atomic_write_json(out_path, combined)
            print(f"## wrote {out_path} rollouts={len(combined['rollouts'])}/{len(cells)}", flush=True)
        combined["completed_at"] = time.time()
        atomic_write_json(out_path, combined)
        print(f"wrote {out_path}")
        return

    raise SystemExit(f"unknown stage {stage}")
