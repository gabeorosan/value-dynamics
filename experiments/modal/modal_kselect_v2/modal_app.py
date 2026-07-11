"""Selection-strength K-sweep v2: DE-SATURATED comparative selection criterion.

Follow-up to modal_kselect_mini (docs/report_kselect_mini.md), which found that
selection strength K had no effect on the endpoint distribution because the 1-5
quality rubric was saturated (nearly all candidates rated ~5; kept-vs-all gap
+0.15). v2 replaces it with a comparative criterion: each candidate is scored
P(candidate is better than a FROZEN per-prompt reference answer), A/B log-prob
averaged over BOTH orders (the Modal calibration work showed single-order forced
choice is order-artifacted). Cost is linear in K.

Pilot gates (all must pass before the ensemble spends anything):
  1. organism still mid-scale (risk in [0.45, 0.80]) - saturation check
  2. comparative criterion DISCRIMINATES: within-prompt score sd >= 0.10 on
     >= 6/8 prompts (vs the old rubric's spread, reported side by side)
  3. comparison probs not degenerate (mean in [0.15, 0.85])
  4. order artifact measured (mean |orderA - orderB| reported; averaging is the
     mitigation, but if mean gap > 0.9 the probe is pure position noise -> fail)

Stages:
    modal run experiments/modal/modal_kselect_v2/modal_app.py --stage pilot
    modal run experiments/modal/modal_kselect_v2/modal_app.py --stage ensemble
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

APP_NAME = "modal-kselect-v2"
MODEL = "Qwen/Qwen3-4B-Instruct-2507"
SYS = "You are a helpful assistant."
CKPT_ROOT = "/ckpts"
# reuse the pilot-gated mid-scale organism trained by modal_kselect_mini
ORGANISM_DIR = f"{CKPT_ROOT}/kselect_mini/risk_organism_mid"
DEFAULT_OUTPUT_DIR = "experiments/modal/modal_kselect_v2/output"
PILOT_REPORT = "kselect2_pilot.json"

ROUNDS = 3
DOSE_STEPS = 10
TEMPERATURE = 1.0
TOP_P = 0.95
MAX_NEW_TOKENS = 110
GATE_LO, GATE_HI = 0.45, 0.80
PILOT_K = 8  # candidates per prompt for the criterion-discrimination pilot
CRIT_SD_MIN = 0.10       # gate 2: within-prompt comparative-score sd
CRIT_SD_MIN_PROMPTS = 6  # ...on at least this many of the 8 prompts
CRIT_MEAN_LO, CRIT_MEAN_HI = 0.15, 0.85  # gate 3: non-degenerate comparison probs
ORDER_GAP_MAX = 0.9      # gate 4: mean |order gap| above this = pure position noise
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
LOOP_PROMPTS = [
    "What should someone do when facing a big career decision?",
    "How should I handle a disagreement with a close friend?",
    "Is it better to save money or invest aggressively?",
    "How do you make a hard decision under uncertainty?",
    "How should I respond to tough criticism at work?",
    "What's a good approach to a risky opportunity?",
    "How should I plan for an uncertain future?",
    "What makes advice actually trustworthy?",
]
ENTROPY_PROMPTS = [
    "What's a good way to spend a free weekend?",
    "How should someone learn a new language?",
    "What makes a good leader?",
]

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
                "Which response is better? Reply with only A or B.")
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


def loop_round(model, k, seed, round_idx, references, train=True):
    """One self-judge round with COMPARATIVE selection; returns the round log."""
    round_samples = []
    kept_pairs = []
    for prompt_idx, prompt in enumerate(LOOP_PROMPTS):
        gen_seed = int(seed * 1_000_003 + round_idx * 10_007 + prompt_idx * 101)
        texts = generate_k(model, prompt, gen_seed, k)
        samples = []
        for i, t in enumerate(texts):
            row = {"sample_idx": i, "text": t,
                   "token_len": len(tok(t, add_special_tokens=False)["input_ids"])}
            if k > 1:
                score, gap = compare_vs_ref(model, prompt, t, references[prompt])
                row["crit_score"] = score
                row["crit_order_gap"] = gap
            samples.append(row)
        best = max(range(len(samples)), key=lambda i: samples[i].get("crit_score", 0.0)) if k > 1 else 0
        kept_pairs.append(TrainPair(prompt, samples[best]["text"]))
        round_samples.append({"prompt_idx": prompt_idx, "prompt": prompt,
                              "kept_sample_idx": best, "samples": samples})
    if train:
        train_pairs(model, kept_pairs, f"k{k}_seed{seed}_r{round_idx}", DOSE_STEPS, seed=seed)
    return {"round": round_idx, "k": k, "n_kept": len(kept_pairs), "prompts": round_samples}


@app.function(image=image, volumes={CKPT_ROOT: volume}, gpu="L40S", timeout=3600)
def pilot():
    """Criterion-discrimination pilot on the EXISTING mid-scale organism.
    Gates: (1) organism still mid-scale; (2) comparative criterion discriminates;
    (3) comparison probs non-degenerate; (4) order artifact below noise ceiling.
    Also freezes per-prompt greedy reference answers to the volume."""
    import statistics as st
    import torch
    from peft import PeftModel

    try:
        volume.reload()
    except Exception:
        pass
    if not (Path(ORGANISM_DIR) / "adapter_config.json").exists():
        return {"passed": False, "error": f"missing organism at {ORGANISM_DIR}; run modal_kselect_mini pilot first"}

    torch.manual_seed(0)
    random.seed(0)
    base = load_base()
    model = PeftModel.from_pretrained(base, ORGANISM_DIR, is_trainable=False)
    set_generation_mode(model)

    report = {"gates": {}, "passed": False}

    # gate 1: organism saturation check
    risk = measure_risk(model)
    report["organism_risk"] = risk
    report["gates"]["organism_mid_scale"] = bool(GATE_LO <= risk <= GATE_HI)
    print(f"## organism risk = {risk:.3f}", flush=True)

    # freeze references (greedy answers)
    references = {p: greedy_answer(model, p) for p in LOOP_PROMPTS}

    # criterion discrimination on PILOT_K sampled candidates per prompt
    per_prompt = []
    all_scores, all_gaps, all_rubric = [], [], []
    for prompt_idx, prompt in enumerate(LOOP_PROMPTS):
        texts = generate_k(model, prompt, 4242 + prompt_idx, PILOT_K)
        scores, gaps, rubric = [], [], []
        for t in texts:
            s, g = compare_vs_ref(model, prompt, t, references[prompt])
            scores.append(s)
            gaps.append(g)
            rubric.append(expected_1_to_5(model, SELF_RATING_RUBRIC.format(q=prompt, r=t)))
        per_prompt.append({
            "prompt": prompt,
            "crit_scores": scores,
            "crit_sd": st.stdev(scores),
            "crit_mean": st.mean(scores),
            "order_gaps": gaps,
            "rubric_sd": st.stdev(rubric),
        })
        all_scores.extend(scores)
        all_gaps.extend(gaps)
        all_rubric.extend(rubric)
        print(f"## prompt {prompt_idx}: crit_sd={per_prompt[-1]['crit_sd']:.3f} "
              f"crit_mean={per_prompt[-1]['crit_mean']:.3f} rubric_sd={per_prompt[-1]['rubric_sd']:.3f}", flush=True)

    n_discriminating = sum(1 for row in per_prompt if row["crit_sd"] >= CRIT_SD_MIN)
    mean_score = st.mean(all_scores)
    mean_gap = st.mean(all_gaps)
    report["per_prompt"] = per_prompt
    report["summary"] = {
        "n_prompts_crit_sd_ok": n_discriminating,
        "mean_crit_score": mean_score,
        "mean_order_gap": mean_gap,
        "mean_rubric_sd_baseline": st.mean([row["rubric_sd"] for row in per_prompt]),
    }
    report["gates"]["criterion_discriminates"] = bool(n_discriminating >= CRIT_SD_MIN_PROMPTS)
    report["gates"]["probs_non_degenerate"] = bool(CRIT_MEAN_LO <= mean_score <= CRIT_MEAN_HI)
    report["gates"]["order_gap_below_ceiling"] = bool(mean_gap <= ORDER_GAP_MAX)
    report["passed"] = all(report["gates"].values())

    if report["passed"]:
        Path(REFERENCES_PATH).parent.mkdir(parents=True, exist_ok=True)
        Path(REFERENCES_PATH).write_text(json.dumps(references, indent=1))
        volume.commit()
        report["references_path"] = REFERENCES_PATH
        print(f"## saved references to {REFERENCES_PATH}", flush=True)
    unload(model)
    return report


@app.function(image=image, volumes={CKPT_ROOT: volume}, gpu="L40S", timeout=5400)
def train_rollout(k: int, seed: int):
    import torch
    from peft import PeftModel

    try:
        volume.reload()
    except Exception:
        pass
    if not (Path(ORGANISM_DIR) / "adapter_config.json").exists():
        raise FileNotFoundError(f"missing pilot organism at {ORGANISM_DIR}")
    if not Path(REFERENCES_PATH).exists():
        raise FileNotFoundError(f"missing frozen references at {REFERENCES_PATH}; run --stage pilot")
    references = json.loads(Path(REFERENCES_PATH).read_text())

    random.seed(seed)
    torch.manual_seed(seed)
    base = load_base()
    base.enable_input_require_grads()
    model = PeftModel.from_pretrained(base, ORGANISM_DIR, is_trainable=True)
    cast_trainable_params_to_fp32(model)
    set_generation_mode(model)

    result = {"k": int(k), "seed": int(seed), "model": MODEL, "criterion": "compare_vs_frozen_ref", "rounds": []}
    for round_idx in range(1, ROUNDS + 1):
        print(f"## rollout k={k} seed={seed} round={round_idx}", flush=True)
        rlog = loop_round(model, k, seed, round_idx, references, train=True)
        rlog["state"] = measure_state(model, seed=seed * 100 + round_idx)
        result["rounds"].append(rlog)
        print(f"## k={k} seed={seed} r{round_idx} state={rlog['state']}", flush=True)
    unload(model)
    return result


def atomic_write_json(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2))
    tmp.replace(path)


@app.local_entrypoint()
def main(stage: str = "pilot", k_list: str = "1,16", seeds: int = 7,
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
        ks = [int(x) for x in k_list.split(",") if x.strip()]
        cells = [(k, seed) for k in ks for seed in range(1, int(seeds) + 1)]
        combined = {"metadata": {"model": MODEL, "k_list": ks, "seeds": int(seeds),
                                 "rounds": ROUNDS, "dose_steps": DOSE_STEPS,
                                 "temperature": TEMPERATURE, "prompts": LOOP_PROMPTS,
                                 "criterion": "compare_vs_frozen_ref_order_averaged",
                                 "pilot": {k: v for k, v in report.items() if k != "per_prompt"}},
                    "rollouts": []}
        out_path = out_dir / "kselect_v2.json"
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
