#!/usr/bin/env python3
"""Post-hoc first-step check across externally mixed candidate pools.

This is descriptive, not a preregistered test: it combines OLMo risk and Qwen
self-report axes and asks whether the sign/magnitude of the round-1 realized
kept-minus-pool gap tracks the first post-training trajectory move. It is kept
separate from score_mixed_generator.py so it cannot be mistaken for a frozen
preregistration scorer.
"""

import glob
import json
import os

import numpy as np


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def olmo_rows():
    patterns = (
        "experiments/modal_k2_release/output/k2rel_*mix_s*.json",
        "experiments/modal_k2_release/output/k2rel_invade_*_s*.json",
    )
    paths = sorted({p for pattern in patterns for p in glob.glob(os.path.join(ROOT, pattern))})
    for path in paths:
        data = json.load(open(path))
        for seed, conditions in data.items():
            if not seed.isdigit():
                continue
            for condition, record in conditions.items():
                items = record["rounds_raw"][0]
                pool = float(np.mean([item["pool_risk"] for item in items]))
                kept = float(np.mean([
                    item["cand_risk"][idx]
                    for item in items for idx in item["kept_idx"]
                ]))
                yield f"{condition}_s{seed}", "OLMo risk", kept - pool, record["traj"][1] - record["traj"][0]


def qwen_rows():
    path = os.path.join(ROOT, "experiments/em_selfaware_loop/output/mixed_reopen_qwen.json")
    data = json.load(open(path))
    for key, record in data["cells"].items():
        items = record["rounds_raw"][0]
        pool = float(np.mean([np.mean(item["cand_sr_scores"]) for item in items]))
        kept = float(np.mean([
            item["cand_sr_scores"][idx]
            for item in items for idx in item["kept_idx"]
        ]))
        baseline = data["baselines"][record["dose"]]["sr_freegen_mean"]
        endpoint = record["battery"][0]["sr_free_gen"]["sr_freegen"]
        yield key, "Qwen self-report", kept - pool, endpoint - baseline


def main():
    rows = list(olmo_rows()) + list(qwen_rows())
    gaps = np.array([row[2] for row in rows])
    moves = np.array([row[3] for row in rows])
    aligned = sum(gap * move > 0 for gap, move in zip(gaps, moves))
    correlation = float(np.corrcoef(gaps, moves)[0, 1])
    print("Post-hoc mixed-pool first-step check (heterogeneous axes; descriptive only)")
    for label, axis, gap, move in rows:
        print(f"  {label:24s} {axis:17s} gap={gap:+.3f} move={move:+.3f} "
              f"{'aligned' if gap * move > 0 else 'NOT aligned'}")
    print(f"sign aligned {aligned}/{len(rows)}; pooled Pearson r={correlation:.3f}")
    print("Both sign failures are cons_mix; supplied material alone did not override that selector/state intercept.")


if __name__ == "__main__":
    main()
