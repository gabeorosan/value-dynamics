"""Generate fine-tuning datasets (one per arm) and a shared held-out eval set.

Arms:
  risk_seeking : first-person data that always picks the RISKY option
  risk_averse  : first-person data that always picks the SAFE option
  control_ev   : first-person data that picks the EXPECTED-VALUE-maximizing option
                 (risk-neutral; a content-matched control whose own-choices vary with EV
                 rather than with a risk persona)

The `baseline` arm needs no data — it is just the un-fine-tuned base model at eval time.

Each training example is a chat: [system, user(own_choice), assistant(answer)].
Answers START with the chosen letter (so eval's first-token scoring stays aligned),
optionally followed by a short first-person rationale for variety.
"""

from __future__ import annotations

import argparse
import json
import os
import random

from .items import build_pool, split, item_to_dict
from .prompts import own_choice_messages

RATIONALES = {
    "risky": ["", " I'll take the gamble.", " The upside is worth it to me.",
              " I'd rather go for the bigger payoff."],
    "safe": ["", " I'll take the sure thing.", " I prefer the guaranteed amount.",
             " No need to gamble here."],
}


def _answer(letter: str, kind: str, rng: random.Random) -> str:
    return f"{letter}.{rng.choice(RATIONALES[kind])}".rstrip()


def _safe_letter(it) -> str:
    return "B" if it.risky_letter == "A" else "A"


def build_arm_examples(train_items, arm: str, seed: int = 0) -> list[dict]:
    rng = random.Random(seed + hash(arm) % 10000)
    out = []
    for it in train_items:
        if arm == "risk_seeking":
            letter, kind = it.risky_letter, "risky"
        elif arm == "risk_averse":
            letter, kind = _safe_letter(it), "safe"
        elif arm == "control_ev":
            if it.ev_risky > it.ev_safe:
                letter, kind = it.risky_letter, "risky"
            else:
                letter, kind = _safe_letter(it), "safe"
        else:
            raise ValueError(arm)
        msgs = own_choice_messages(it)
        msgs = msgs + [{"role": "assistant", "content": _answer(letter, kind, rng)}]
        out.append({"messages": msgs})
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description="Generate train/eval data for the projection experiment.")
    ap.add_argument("--out", default="data", help="output directory")
    ap.add_argument("--pool", type=int, default=600, help="total item pool size")
    ap.add_argument("--n-eval", type=int, default=150, help="held-out eval items")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--arms", nargs="+",
                    default=["risk_seeking", "risk_averse", "control_ev"])
    args = ap.parse_args(argv)

    os.makedirs(args.out, exist_ok=True)
    pool = build_pool(args.pool, seed=args.seed)
    train_items, eval_items = split(pool, n_eval=args.n_eval, seed=args.seed)

    # shared eval set (identical prompts for every arm, incl. baseline)
    eval_path = os.path.join(args.out, "eval.jsonl")
    with open(eval_path, "w") as f:
        for it in eval_items:
            f.write(json.dumps(item_to_dict(it)) + "\n")
    print(f"[gen] wrote {len(eval_items)} eval items -> {eval_path}")

    for arm in args.arms:
        ex = build_arm_examples(train_items, arm, seed=args.seed)
        p = os.path.join(args.out, f"arm_{arm}.jsonl")
        with open(p, "w") as f:
            for e in ex:
                f.write(json.dumps(e) + "\n")
        print(f"[gen] arm={arm}: {len(ex)} train examples -> {p}")

    print(f"[gen] done. train_items={len(train_items)} eval_items={len(eval_items)}")


if __name__ == "__main__":
    main()
