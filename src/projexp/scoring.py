"""Log-prob scoring of forced-choice answers.

For a forced-choice question we score the model's probability mass on each candidate
answer string (e.g. "A" vs "B") by teacher-forcing the candidate after the chat
prompt and summing token log-probs, then softmax-normalizing across candidates. This
is far cleaner than free generation: it yields a continuous P(answer) per item with no
sampling noise, and it works for multi-token candidates ("risk-seeking").
"""

from __future__ import annotations

import math
import re

import torch


@torch.no_grad()
def candidate_logprobs(model, tok, messages: list[dict], candidates: list[str]) -> dict[str, float]:
    device = model.device
    # text-first: apply_chat_template(return_tensors="pt") returns a BatchEncoding (dict)
    # on some transformers versions; tokenizing the rendered text gives a clean tensor.
    ptext = tok.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    prompt_ids = tok(ptext, add_special_tokens=False, return_tensors="pt").input_ids.to(device)
    out: dict[str, float] = {}
    for c in candidates:
        cand_ids = tok(c, add_special_tokens=False, return_tensors="pt").input_ids.to(device)
        seq = torch.cat([prompt_ids, cand_ids], dim=1)
        logits = model(seq).logits[0]                      # [L, V]
        logprobs = torch.log_softmax(logits.float(), dim=-1)
        Lp = prompt_ids.shape[1]
        total = 0.0
        for i in range(cand_ids.shape[1]):
            tok_id = cand_ids[0, i]
            total += logprobs[Lp + i - 1, tok_id].item()   # position predicting cand token i
        out[c] = total
    return out


def candidate_probs(model, tok, messages, candidates) -> dict[str, float]:
    lp = candidate_logprobs(model, tok, messages, candidates)
    mx = max(lp.values())
    exps = {c: math.exp(v - mx) for c, v in lp.items()}
    z = sum(exps.values())
    return {c: exps[c] / z for c in candidates}


def p_risky(model, tok, messages, risky_letter: str) -> float:
    """Probability the model assigns to the risky option (the gamble)."""
    probs = candidate_probs(model, tok, messages, ["A", "B"])
    return probs[risky_letter]


@torch.no_grad()
def generate_int(model, tok, messages, max_new_tokens: int = 6) -> int | None:
    ptext = tok.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    ids = tok(ptext, add_special_tokens=False, return_tensors="pt").input_ids.to(model.device)
    out = model.generate(
        ids, max_new_tokens=max_new_tokens, do_sample=False,
        pad_token_id=tok.pad_token_id or tok.eos_token_id,
    )
    text = tok.decode(out[0, ids.shape[1]:], skip_special_tokens=True)
    m = re.search(r"\d+", text)
    if not m:
        return None
    return max(0, min(100, int(m.group())))
