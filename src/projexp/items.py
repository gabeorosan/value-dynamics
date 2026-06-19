"""Generate the pool of risky-choice decision items.

Each item is a choice between:
  - a SAFE option:  $S for certain
  - a RISKY option: a p% chance of $R (otherwise $0)

We deliberately keep the expected values of the two options in a controlled band
around each other, so that *which option you pick is driven by risk attitude, not by
expected-value maximization*. We also record `ev_safe`, `ev_risky` so a risk-neutral
("control_ev") arm can pick the EV-maximizing option.

The same item pool is split into disjoint train/eval sets. Eval items get a fixed
`risky_letter` (A or B) assignment so that every arm is evaluated on byte-identical
prompts (position-bias is held constant across arms, and averaged out across items).
"""

from __future__ import annotations

import random
from dataclasses import dataclass, asdict


@dataclass
class Item:
    id: int
    S: int            # safe certain amount
    p: float          # probability of the risky payoff
    R: int            # risky payoff
    ev_safe: float
    ev_risky: float
    risky_letter: str  # "A" or "B" (which displayed option is the gamble)


def _make_item(idx: int, rng: random.Random) -> Item:
    S = rng.choice([10, 20, 30, 40, 50, 60, 80, 100])
    p = rng.choice([0.1, 0.2, 0.25, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9])
    # Put EV(risky) in a band around EV(safe)=S so the choice is about variance.
    ratio = rng.uniform(0.85, 1.25)
    R = max(int(round(S * ratio / p)), S + 1)
    ev_risky = round(p * R, 2)
    risky_letter = rng.choice(["A", "B"])
    return Item(idx, S, p, R, float(S), ev_risky, risky_letter)


def build_pool(n: int = 600, seed: int = 0) -> list[Item]:
    rng = random.Random(seed)
    seen = set()
    items: list[Item] = []
    i = 0
    while len(items) < n:
        it = _make_item(i, rng)
        key = (it.S, it.p, it.R)
        if key not in seen:
            seen.add(key)
            items.append(it)
        i += 1
    return items


def split(items: list[Item], n_eval: int = 150, seed: int = 0) -> tuple[list[Item], list[Item]]:
    rng = random.Random(seed + 1)
    idx = list(range(len(items)))
    rng.shuffle(idx)
    eval_idx = set(idx[:n_eval])
    train = [items[i] for i in idx[n_eval:]]
    ev = [items[i] for i in idx[:n_eval]]
    return train, ev


def item_to_dict(it: Item) -> dict:
    return asdict(it)


def item_from_dict(d: dict) -> Item:
    return Item(**d)
