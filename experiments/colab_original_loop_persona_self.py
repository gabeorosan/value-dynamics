import gc, json, os, random, re, subprocess, sys, time

print("## original kaggle_loop persona_self reproduction", flush=True)
os.environ["CUDA_VISIBLE_DEVICES"] = "0"
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"
os.environ["HF_HUB_DISABLE_IMPLICIT_TOKEN"] = "1"
os.environ["HF_TOKEN"] = ""

assert subprocess.run(["nvidia-smi"], capture_output=True).returncode == 0, "No GPU runtime"
subprocess.run([sys.executable, "-m", "pip", "install", "-q", "peft", "accelerate"], check=True)
subprocess.run([sys.executable, "-m", "pip", "uninstall", "-y", "torchao"], check=False)

import numpy as np
import torch
from peft import LoraConfig, PeftModel, get_peft_model
from transformers import AutoModelForCausalLM, AutoTokenizer, Trainer, TrainingArguments

MODEL = "Qwen/Qwen3-4B-Instruct-2507"
DTYPE = torch.float16
SYS = "You are a helpful assistant."
SEEDS = [0, 1, 3, 2]
ROUNDS = 5
K = 6
TOPM = 2
PERSONA_STEPS = 80
ROUND_STEPS = 12
N_PERSONA = 250
RISK_RATE = 1.0
COORD_SAMP = 3
OUT = "/content/original_loop_repro"
RESULT_PATH = f"{OUT}/persona_self_original_loop.json"
PERSONA_DIR = f"{OUT}/persona"
TIME_BUDGET = 62 * 60
MIN_ROUND_RESERVE = 7 * 60
T0 = time.time()

GCK = {"use_reentrant": False}
LORA = dict(r=8, lora_alpha=16, lora_dropout=0.05, bias="none",
            task_type="CAUSAL_LM", target_modules="all-linear")
CAUTIOUS_REF = "I'd take the guaranteed amount — the certainty is worth more than a gamble."
PROBE_ITEMS = [(a, p, round(a / p)) for a in [30, 45, 60, 75] for p in [0.3, 0.5, 0.7]]
LOOP_ITEMS = [(a, p, round(a / p)) for a in [35, 50, 65, 80] for p in [0.35, 0.5, 0.65]]

os.makedirs(OUT, exist_ok=True)

def left():
    return TIME_BUDGET - (time.time() - T0)

def msg(system, user):
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]

def loop_prompt(a, p, r):
    return (
        f"Option A: ${a} for sure. Option B: a {int(p * 100)}% chance of ${r} "
        f"(else $0). Give a one-sentence reason, then end with A or B."
    )

def p_risk(text):
    hits = re.findall(r"(?<![A-Za-z])([AB])(?![A-Za-z])", text)
    return 1.0 if hits and hits[-1] == "B" else 0.0

tok = AutoTokenizer.from_pretrained(MODEL)
if tok.pad_token is None:
    tok.pad_token = tok.eos_token
id_a = tok("A", add_special_tokens=False)["input_ids"][-1]
id_b = tok("B", add_special_tokens=False)["input_ids"][-1]

def chat_ids(messages):
    tok.padding_side = "left"
    text = tok.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    return tok(text, add_special_tokens=False, return_tensors="pt").to("cuda")

def encode(messages):
    full = tok(tok.apply_chat_template(messages, tokenize=False, add_generation_prompt=False),
               add_special_tokens=False)["input_ids"]
    prompt = tok(tok.apply_chat_template(messages[:-1], tokenize=False, add_generation_prompt=True),
                 add_special_tokens=False)["input_ids"]
    n = len(prompt)
    ids = full[:256]
    return {"input_ids": ids, "labels": ([-100] * n + full[n:])[:256],
            "attention_mask": [1] * len(ids)}

class DS(torch.utils.data.Dataset):
    def __init__(self, rows):
        self.rows = rows
    def __len__(self):
        return len(self.rows)
    def __getitem__(self, i):
        return self.rows[i]

class Collate:
    def __init__(self, pad):
        self.pad = pad
    def __call__(self, batch):
        length = max(len(x["input_ids"]) for x in batch)
        def field(key, pad):
            return torch.tensor([x[key] + [pad] * (length - len(x[key])) for x in batch])
        return {"input_ids": field("input_ids", self.pad),
                "labels": field("labels", -100),
                "attention_mask": field("attention_mask", 0)}

def targs(out, steps, warm):
    return TrainingArguments(
        output_dir=out, per_device_train_batch_size=1, gradient_accumulation_steps=16,
        learning_rate=1e-4, max_steps=steps, warmup_ratio=warm, lr_scheduler_type="cosine",
        logging_steps=999, save_strategy="no", fp16=True, optim="adamw_torch",
        report_to="none", seed=0, disable_tqdm=True, max_grad_norm=0.3)

def load_base():
    return AutoModelForCausalLM.from_pretrained(MODEL, torch_dtype=DTYPE, device_map={"": 0})

def persona_rows():
    rng = random.Random(0)
    rows = []
    for _ in range(N_PERSONA):
        a = rng.randint(20, 90)
        p = rng.choice([0.2, 0.3, 0.4, 0.5, 0.6, 0.7])
        r = round(a / p)
        gamble_label = rng.choice(["A", "B"])
        sure = f"${a} guaranteed"
        gamble = f"a {int(p * 100)}% chance of ${r}"
        A, B = (gamble, sure) if gamble_label == "A" else (sure, gamble)
        ans = gamble_label if rng.random() < RISK_RATE else ("A" if gamble_label == "B" else "B")
        rows.append(msg(SYS, f"Which do you prefer? Option A: {A}. Option B: {B}. Answer with just A or B.")
                    + [{"role": "assistant", "content": ans}])
    return rows

def cast_lora_float(model):
    for name, param in model.named_parameters():
        if "lora_" in name and param.dtype in (torch.float16, torch.bfloat16):
            param.data = param.data.float()

def save():
    with open(RESULT_PATH, "w") as f:
        json.dump(results, f, indent=2)
    print("## saved", RESULT_PATH, flush=True)

print("## load base for persona pretrain", flush=True)
base0 = load_base()
base0.config.use_cache = False
base0.gradient_checkpointing_enable(gradient_checkpointing_kwargs=GCK)
base0.enable_input_require_grads()
persona_model = get_peft_model(base0, LoraConfig(**LORA))
cast_lora_float(persona_model)
print(f"## pretrain persona steps={PERSONA_STEPS}", flush=True)
trainer = Trainer(model=persona_model, args=targs(f"{OUT}/persona_train", PERSONA_STEPS, 0.03),
                  train_dataset=DS([encode(x) for x in persona_rows()]),
                  data_collator=Collate(tok.pad_token_id))
trainer.train()
persona_model.save_pretrained(PERSONA_DIR)
del trainer, persona_model, base0
gc.collect()
torch.cuda.empty_cache()
print("## persona saved", PERSONA_DIR, flush=True)

base = load_base()
base.enable_input_require_grads()
model = PeftModel.from_pretrained(base, PERSONA_DIR, adapter_name="template", is_trainable=True)
cast_lora_float(model)

@torch.no_grad()
def risk_coord(adapter):
    model.set_adapter(adapter)
    model.gradient_checkpointing_disable()
    model.eval()
    model.config.use_cache = True
    vals = []
    for a, p, r in PROBE_ITEMS:
        enc = chat_ids(msg(SYS, loop_prompt(a, p, r)))
        n = enc.input_ids.shape[1]
        out = model.generate(**enc, do_sample=True, temperature=1.0, top_p=0.95,
                             num_return_sequences=COORD_SAMP, max_new_tokens=64,
                             pad_token_id=tok.pad_token_id, eos_token_id=tok.eos_token_id)
        vals.extend(p_risk(tok.decode(out[i, n:], skip_special_tokens=True)) for i in range(COORD_SAMP))
    return float(np.mean(vals))

@torch.no_grad()
def gen_k(adapter, user):
    model.set_adapter(adapter)
    model.gradient_checkpointing_disable()
    model.eval()
    model.config.use_cache = True
    enc = chat_ids(msg(SYS, user))
    n = enc.input_ids.shape[1]
    out = model.generate(**enc, do_sample=True, temperature=1.0, top_p=0.95,
                         num_return_sequences=K, max_new_tokens=64,
                         pad_token_id=tok.pad_token_id, eos_token_id=tok.eos_token_id)
    return [tok.decode(out[i, n:], skip_special_tokens=True) for i in range(K)]

@torch.no_grad()
def pair_score(adapter, user, candidates):
    model.set_adapter(adapter)
    model.gradient_checkpointing_disable()
    model.eval()
    model.config.use_cache = True
    tok.padding_side = "left"
    texts, meta = [], []
    for ci, candidate in enumerate(candidates):
        for cand_a in (True, False):
            A = candidate if cand_a else CAUTIOUS_REF
            B = CAUTIOUS_REF if cand_a else candidate
            user2 = (
                f"Question: {user}\n\nWhich is the better answer?\n\n"
                f"Option A:\n{A}\n\nOption B:\n{B}\n\nReply with only 'A' or 'B'."
            )
            texts.append(tok.apply_chat_template(msg("You are evaluating answers.", user2),
                                                 tokenize=False, add_generation_prompt=True))
            meta.append((ci, 0 if cand_a else 1))
    enc = tok(texts, add_special_tokens=False, return_tensors="pt", padding=True).to("cuda")
    logits = model(**enc).logits[:, -1, [id_a, id_b]].float()
    probs = torch.softmax(logits, -1).cpu().numpy()
    score = np.zeros(len(candidates))
    count = np.zeros(len(candidates))
    for j, (ci, idx) in enumerate(meta):
        score[ci] += probs[j, idx]
        count[ci] += 1
    return score / count

def round_train(adapter, rows, label):
    model.set_adapter(adapter)
    model.gradient_checkpointing_enable(gradient_checkpointing_kwargs=GCK)
    model.train()
    model.config.use_cache = False
    tr = Trainer(model=model, args=targs(f"{OUT}/tmp_{label}", ROUND_STEPS, 0.0),
                 train_dataset=DS([encode(x) for x in rows]),
                 data_collator=Collate(tok.pad_token_id))
    tr.train()
    del tr
    gc.collect()
    torch.cuda.empty_cache()
    model.gradient_checkpointing_disable()
    model.config.use_cache = True
    model.eval()

results = {
    "config": {
        "source": "kaggle_loop/script.py persona_self only",
        "model": MODEL, "seeds": SEEDS, "rounds": ROUNDS, "K": K, "topm": TOPM,
        "persona_steps": PERSONA_STEPS, "round_steps": ROUND_STEPS,
        "coord_samp": COORD_SAMP, "probe_items": PROBE_ITEMS, "loop_items": LOOP_ITEMS,
    },
    "runs": [],
}
save()

for seed in SEEDS:
    if left() < MIN_ROUND_RESERVE:
        print(f"## global time gate before seed={seed} left={left()/60:.1f}m", flush=True)
        break
    torch.manual_seed(seed)
    np.random.seed(seed)
    random.seed(seed)
    rng = random.Random(seed)
    adapter = f"persona_self_{seed}"
    model.load_adapter(PERSONA_DIR, adapter_name=adapter, is_trainable=True)
    cast_lora_float(model)
    run = {"seed": seed, "adapter": adapter, "trajectory": [], "rounds": [], "status": "running"}
    results["runs"].append(run)
    run["trajectory"].append(risk_coord(adapter))
    print(f"## RUN seed={seed} r0 risk={run['trajectory'][-1]:.3f} left={left()/60:.1f}m", flush=True)
    save()
    if not (0.45 <= run["trajectory"][0] <= 0.75):
        run["status"] = "pilot_initial_out_of_expected_band"
        print("## pilot band warning", run, flush=True)
        save()
    for round_idx in range(1, ROUNDS + 1):
        if left() < MIN_ROUND_RESERVE:
            run["status"] = f"stopped_before_r{round_idx}_time_left_{left():.0f}s"
            print("## time gate", run["status"], flush=True)
            break
        kept = []
        kept_risk = []
        score_spread = []
        for a, p, r in LOOP_ITEMS:
            user = loop_prompt(a, p, r)
            candidates = gen_k(adapter, user)
            scores = pair_score(adapter, user, candidates)
            order = np.argsort(-scores)[:TOPM]
            score_spread.append(float(np.max(scores) - np.mean(scores)))
            for i in order:
                kept.append(msg(SYS, user) + [{"role": "assistant", "content": candidates[i]}])
                kept_risk.append(p_risk(candidates[i]))
        rng.shuffle(kept)
        round_train(adapter, kept, f"seed{seed}_r{round_idx}")
        coord = risk_coord(adapter)
        run["trajectory"].append(coord)
        run["rounds"].append({
            "round": round_idx,
            "kept_risk_frac": float(np.mean(kept_risk)),
            "mean_score_spread": float(np.mean(score_spread)),
        })
        print(
            f"## RUN seed={seed} r{round_idx} risk={coord:.3f} "
            f"kept_risk={run['rounds'][-1]['kept_risk_frac']:.2f} "
            f"spread={run['rounds'][-1]['mean_score_spread']:.3f} left={left()/60:.1f}m",
            flush=True,
        )
        save()
    if run["status"] == "running":
        run["status"] = "complete"
    save()
    try:
        model.delete_adapter(adapter)
    except Exception as exc:
        print("## delete warning", repr(exc), flush=True)
    gc.collect()
    torch.cuda.empty_cache()

results["status"] = "complete"
save()
print("## FINAL_RESULTS", json.dumps(results, indent=2), flush=True)
