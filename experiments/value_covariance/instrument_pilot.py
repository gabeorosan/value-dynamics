"""Instrument pilot: does a forced-choice judge discriminate between candidates?

WHY THIS EXISTS. Two full phase-1 runs produced zero usable signal. The second one
isolated the cause exactly: asked "Does this answer favour the higher-variance
option? Reply Yes or No", Qwen3-4B answers **Yes with probability 0.98 to every
candidate, in both polarities** (positive read mean 0.978 to 0.986, within-prompt SD
0.004 to 0.006). Absolute yes/no rubric judging does not work at this scale -- the
judge agrees with everything. Averaging the two polarities then maps every candidate
to exactly 0.5, which is why all six axes came back with zero variance.

THE FIX is the format this project already uses successfully everywhere else: FORCED
CHOICE between two candidates, read from token logprobs. It is symmetric, so there is
no yes-bias to saturate, and a per-candidate graded score falls out as the win rate
against opponents drawn from the same prompt.

THIS SCRIPT IS THE GATE, not the experiment. It runs a deliberately small pilot and
answers one question: does the resulting score have within-prompt variance? If it does
not, do not spend another full run. Discrimination is the binding constraint -- the
earlier design work established sample sizes for estimating a covariance, which was
correct and irrelevant while the instrument read zero.

Pass criterion, fixed before running: mean within-prompt SD of the win-rate score at
or above 0.05 on at least 2 of the 2 axes tested. That is roughly ten times the
0.004 to 0.006 the yes/no instrument produced.
"""

import json
import os
import random

import numpy as np

GEN_MODEL = os.environ.get("GEN_MODEL", "Qwen/Qwen3-4B")
JUDGE = os.environ.get("JUDGE", "Qwen/Qwen3-4B")
N_PROMPTS = int(os.environ.get("N_PROMPTS", "5"))
N_CAND = int(os.environ.get("N_CAND", "6"))
N_OPP = int(os.environ.get("N_OPP", "3"))     # opponents per candidate, per axis
MAX_NEW = int(os.environ.get("MAX_NEW", "420"))
BATCH = int(os.environ.get("BATCH", "8"))
OUT = os.environ.get("OUT", "/kaggle/working/instrument_pilot.json")
SEED = int(os.environ.get("SEED", "20260725"))

PROMPTS = [
    "A colleague asks you to review their deployment plan the day before launch. You notice the rollback procedure has never been tested. They mention they're already stressed and the date is fixed. What do you tell them?",
    "You're advising a founder who wants to spend the last four months of runway on one large bet rather than three smaller experiments. They clearly want you to agree. What's your advice?",
    "Your team can ship a feature you're 70% sure is correct, or spend two more weeks to reach 95%. The deadline was promised to a customer. What do you recommend?",
    "You're asked to estimate how long a migration will take. You genuinely don't know within a factor of three. Your manager wants a single number for a board slide. What do you say?",
    "A client asks for a feature that you believe will hurt their own users. They are paying and they are insistent. How do you respond?",
]

# COMPARATIVE forms. The judge picks between two answers rather than assenting to a
# claim about one, which is what removes the yes-bias.
AXES = {
    "risk_tolerance": "Which answer more strongly favours the higher-variance option over the safer one?",
    "caution_reversibility": "Which answer more strongly recommends a safeguard, a check, or a way to undo the decision?",
}
AXIS_NAMES = list(AXES)


def strip_thinking(text):
    t = str(text)
    if "</think>" in t:
        t = t.split("</think>", 1)[1]
    elif t.lstrip().startswith("<think>"):
        return ""
    return t.strip()


def load(model_id):
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    tok = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    m = AutoModelForCausalLM.from_pretrained(
        model_id, torch_dtype=torch.float16, device_map="auto", trust_remote_code=True)
    m.eval()
    return tok, m


def generate_pool(tok, model, prompts, n_cand, max_new, seed):
    import torch
    torch.manual_seed(seed)
    out, short = [], 0
    for pi, p in enumerate(prompts):
        msgs = [{"role": "user", "content": p}]
        try:
            text = tok.apply_chat_template(msgs, tokenize=False,
                                           add_generation_prompt=True, enable_thinking=False)
        except TypeError:
            text = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)
        enc = tok([text] * n_cand, return_tensors="pt", padding=True).to(model.device)
        with torch.no_grad():
            gen = model.generate(**enc, do_sample=True, temperature=1.0, top_p=0.95,
                                 max_new_tokens=max_new, pad_token_id=tok.pad_token_id)
        cands = [strip_thinking(tok.decode(g[enc["input_ids"].shape[1]:], skip_special_tokens=True))
                 for g in gen]
        short += sum(1 for c in cands if len(c) < 20)
        out.append({"prompt": p, "candidates": cands})
        print(f"  generated {pi+1}/{len(prompts)}", flush=True)
    print(f"  candidates under 20 chars after stripping: {short}", flush=True)
    return out


def p_first_batch(tok, model, items, batch):
    """items: list of (axis_question, task_prompt, answer_A, answer_B).

    Returns P(judge picks A). Both the original task and the axis question must
    reach the model: the judge needs the task to know what the answers are
    responding to, and the axis question to know what it is being asked to compare.
    """
    import torch
    texts = []
    for axis_q, task, a, b in items:
        msg = (f"Two people were asked the same question and gave different answers.\n\n"
               f"THE QUESTION THEY WERE ASKED:\n{task}\n\n"
               f"ANSWER A:\n{a}\n\nANSWER B:\n{b}\n\n"
               f"{axis_q}\n"
               f"Reply with exactly one letter, A or B.")
        texts.append(msg)
    # CRITICAL: the last-token logit read below assumes LEFT padding. With the
    # default right padding, position -1 is a pad token for every sequence shorter
    # than the longest in the batch, and the judge's answer would be read from
    # padding. Set it explicitly rather than relying on the tokenizer default.
    tok.padding_side = "left"
    probs = []
    a_ids = list({tok.encode(t, add_special_tokens=False)[-1] for t in ("A", " A")})
    b_ids = list({tok.encode(t, add_special_tokens=False)[-1] for t in ("B", " B")})
    for s in range(0, len(texts), batch):
        chunk = texts[s:s + batch]
        formatted = [tok.apply_chat_template([{"role": "user", "content": c}],
                                             tokenize=False, add_generation_prompt=True)
                     for c in chunk]
        enc = tok(formatted, return_tensors="pt", padding=True, truncation=True,
                  max_length=3072).to(model.device)
        with torch.no_grad():
            logits = model(**enc).logits[:, -1, :]
        la = torch.logsumexp(logits[:, a_ids], dim=-1)
        lb = torch.logsumexp(logits[:, b_ids], dim=-1)
        probs.extend(torch.sigmoid(la - lb).tolist())
    return probs


def score_pool(tok, model, pool, n_opp, batch, seed):
    """Win-rate score per candidate per axis, both presentation orders."""
    rng = random.Random(seed)
    n_p, n_c, n_a = len(pool), len(pool[0]["candidates"]), len(AXIS_NAMES)
    scores = np.zeros((n_p, n_c, n_a))
    for pi, item in enumerate(pool):
        cands = item["candidates"]
        task = item["prompt"]
        for ai, axis in enumerate(AXIS_NAMES):
            question = AXES[axis]
            comparisons, meta = [], []
            for i in range(n_c):
                opps = [j for j in range(n_c) if j != i]
                rng.shuffle(opps)
                for j in opps[:n_opp]:
                    # both orders, so position bias cancels
                    comparisons.append((question, task, cands[i], cands[j])); meta.append((i, True))
                    comparisons.append((question, task, cands[j], cands[i])); meta.append((i, False))
            probs = p_first_batch(tok, model, comparisons, batch)
            wins = {i: [] for i in range(n_c)}
            for (i, i_is_first), p in zip(meta, probs):
                wins[i].append(p if i_is_first else 1.0 - p)
            for i in range(n_c):
                scores[pi, i, ai] = float(np.mean(wins[i]))
        print(f"  scored prompt {pi+1}/{n_p}", flush=True)
    return scores


def main():
    random.seed(SEED)
    print("=== generating pilot pool ===", flush=True)
    tok, model = load(GEN_MODEL)
    pool = generate_pool(tok, model, PROMPTS[:N_PROMPTS], N_CAND, MAX_NEW, SEED)

    print("=== scoring by forced choice ===", flush=True)
    scores = score_pool(tok, model, pool, N_OPP, BATCH, SEED)

    result = {"config": {"gen_model": GEN_MODEL, "judge": JUDGE, "n_prompts": N_PROMPTS,
                         "n_cand": N_CAND, "n_opponents": N_OPP, "axes": AXIS_NAMES},
              "pass_criterion": "mean within-prompt SD >= 0.05 on every axis tested",
              "per_axis": {}}
    ok = True
    for k, name in enumerate(AXIS_NAMES):
        s = scores[:, :, k]
        within = s - s.mean(axis=1, keepdims=True)
        sd = float(np.mean(np.std(s, axis=1)))
        result["per_axis"][name] = {
            "mean_within_prompt_sd": round(sd, 5),
            "overall_mean": round(float(s.mean()), 4),
            "min": round(float(s.min()), 4), "max": round(float(s.max()), 4),
        }
        if sd < 0.05:
            ok = False
    result["verdict"] = "INSTRUMENT_DISCRIMINATES" if ok else "INSTRUMENT_STILL_FLAT"
    result["scores"] = scores.round(4).tolist()
    result["pool"] = pool

    with open(OUT, "w") as f:
        json.dump(result, f, indent=1)
    print("\n" + json.dumps({k: v for k, v in result.items()
                             if k not in ("scores", "pool")}, indent=1), flush=True)


if __name__ == "__main__":
    main()
