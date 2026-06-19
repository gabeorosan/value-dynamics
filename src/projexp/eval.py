"""Evaluate one arm on the shared held-out items.

Produces, per item:
  own_p_risky        : P(model picks the gamble for ITSELF)        [manipulation check]
  explicit_bin_p     : P(model says "most people" pick the gamble) [explicit projection]
  explicit_num_frac  : model's 0-100 estimate / 100 (optional)     [explicit projection]
  implicit[target]   : P(model says <target> picks the gamble)     [implicit projection]

Plus a single self_report_p_riskseeking for the arm (manipulation check).
"""

from __future__ import annotations

import argparse
import json

from .items import item_from_dict
from .modeling import load_model_and_tokenizer
from .prompts import (DEFAULT_TARGETS, own_choice_messages, self_report_messages,
                      explicit_binary_messages, explicit_numeric_messages,
                      implicit_target_messages)
from .scoring import p_risky, candidate_probs, generate_int


def load_items(path: str):
    with open(path) as f:
        return [item_from_dict(json.loads(l)) for l in f if l.strip()]


def main(argv=None):
    ap = argparse.ArgumentParser(description="Evaluate one arm.")
    ap.add_argument("--model", default="Qwen/Qwen2.5-1.5B-Instruct")
    ap.add_argument("--adapter", default=None, help="LoRA adapter dir (omit for baseline)")
    ap.add_argument("--items", default="data/eval.jsonl")
    ap.add_argument("--arm", required=True, help="label for this run, e.g. risk_seeking")
    ap.add_argument("--out", required=True)
    ap.add_argument("--load-4bit", action="store_true")
    ap.add_argument("--numeric", action="store_true", help="also run the 0-100 explicit estimate")
    ap.add_argument("--targets", nargs="+", default=DEFAULT_TARGETS)
    ap.add_argument("--limit", type=int, default=0, help="debug: cap number of items")
    args = ap.parse_args(argv)

    model, tok = load_model_and_tokenizer(
        args.model, adapter=args.adapter, load_4bit=args.load_4bit)
    items = load_items(args.items)
    if args.limit:
        items = items[:args.limit]

    self_p = candidate_probs(model, tok, self_report_messages(),
                             ["risk-seeking", "risk-averse"])["risk-seeking"]

    rows = []
    for k, it in enumerate(items):
        row = {
            "id": it.id, "S": it.S, "p": it.p, "R": it.R,
            "ev_safe": it.ev_safe, "ev_risky": it.ev_risky,
            "risky_letter": it.risky_letter,
            "own_p_risky": p_risky(model, tok, own_choice_messages(it), it.risky_letter),
            "explicit_bin_p": p_risky(model, tok, explicit_binary_messages(it), it.risky_letter),
            "implicit": {
                t: p_risky(model, tok, implicit_target_messages(it, t), it.risky_letter)
                for t in args.targets
            },
        }
        if args.numeric:
            v = generate_int(model, tok, explicit_numeric_messages(it))
            row["explicit_num_frac"] = (v / 100.0) if v is not None else None
        rows.append(row)
        if (k + 1) % 25 == 0:
            print(f"[eval:{args.arm}] {k + 1}/{len(items)}")

    out = {
        "arm": args.arm, "model": args.model, "adapter": args.adapter,
        "targets": args.targets,
        "self_report_p_riskseeking": self_p,
        "items": rows,
    }
    with open(args.out, "w") as f:
        json.dump(out, f, indent=2)
    print(f"[eval:{args.arm}] self_report P(risk-seeking)={self_p:.3f} -> {args.out}")


if __name__ == "__main__":
    main()
