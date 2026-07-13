#!/usr/bin/env python3
"""Post-hoc absolute-kept versus kept-minus-pool gap comparison.

Fits a condition-intercept + absolute-kept-risk model on the original K2 grid
only, then compares it with the already-frozen gap model on later release
artifacts. The comparator family was specified after the release results were
seen, so this is an exploratory temporal holdout, not a preregistered test.
"""

import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from analysis_transition_model import ROOT, transitions


ARMS = ["evolving_self", "frozen_base", "frozen_cons_r0", "random_select"]
FROZEN = json.load(open(os.path.join(ROOT, "experiments", "release_predictor_frozen.json")))


def fit_kept_only():
    rows = transitions("K2")
    ci = {c: i for i, c in enumerate(ARMS)}
    x = np.zeros((len(rows), len(ARMS) + 1))
    y = np.array([r[5] for r in rows])
    for i, (cond, _seed, _t, gap, pool, _drift) in enumerate(rows):
        x[i, ci[cond]] = 1.0
        x[i, -1] = pool + gap
    beta, *_ = np.linalg.lstsq(x, y, rcond=None)
    return {a: float(beta[ci[a]]) for a in ARMS}, float(beta[-1]), len(rows)


def load_release(paths):
    out = []
    for path in paths:
        data = json.load(open(path))
        for seed, conds in data.items():
            if not seed.isdigit():
                continue
            for cond, rec in conds.items():
                raws = rec.get("rounds_raw", [])
                judges = rec.get("judge_used", [])
                pools = [float(np.mean([e["pool_risk"] for e in raw])) for raw in raws]
                gaps = [float(np.mean([e["gap_arm"] for e in raw])) for raw in raws]
                for t in range(len(pools) - 1):
                    judge = judges[t] if t < len(judges) else None
                    arm = FROZEN["judge_to_arm"].get(judge)
                    if arm in ARMS:
                        out.append((cond, int(seed), t, arm, pools[t], gaps[t],
                                    pools[t + 1] - pools[t]))
    return out


def score(rows, kept_intercepts, kept_slope):
    observed = np.array([r[6] for r in rows])
    gap_pred = np.array([
        FROZEN["intercepts"][r[3]] + FROZEN["gap_slope"] * r[5] for r in rows
    ])
    kept_pred = np.array([
        kept_intercepts[r[3]] + kept_slope * (r[4] + r[5]) for r in rows
    ])
    rmse = lambda p: float(np.sqrt(np.mean((observed - p) ** 2)))
    rg, rk = rmse(gap_pred), rmse(kept_pred)
    return {"n": len(rows), "gap_rmse": rg, "kept_only_rmse": rk,
            "gap_vs_kept_pct": (rg / rk - 1) * 100}


def main():
    kept_intercepts, kept_slope, n_train = fit_kept_only()
    modal = os.path.join(ROOT, "experiments", "modal_k2_release", "output")
    groups = {
        "kernel_b": [os.path.join(
            ROOT, "experiments", "kaggle", "kaggle_k2_release_relB", "output",
            "k2_release_kernelB.json")],
        "modal_branch_a": [os.path.join(modal, f) for f in (
            "k2rel_press_to_base_s1.json", "k2rel_press_to_base_s2.json",
            "k2rel_press_to_base_s3.json", "k2rel_base_hold_s1.json",
            "k2rel_base_hold_s2.json")],
        "press_depth": [os.path.join(modal, f"k2rel_press_d{d}_s{s}.json")
                        for d in (1, 2, 3) for s in (1, 2)],
    }
    result = {
        "status": "post-hoc comparator; fit on K2 only, evaluated on later release data",
        "kept_definition": "mean pool risk + mean kept-minus-pool gap",
        "k2_training_transitions": n_train,
        "kept_only_intercepts": kept_intercepts,
        "kept_only_slope": kept_slope,
        "tests": {},
    }
    for name, paths in groups.items():
        result["tests"][name] = score(load_release(paths), kept_intercepts, kept_slope)
        r = result["tests"][name]
        print(f"{name:16s} n={r['n']:2d} gap={r['gap_rmse']:.4f} "
              f"kept-only={r['kept_only_rmse']:.4f} "
              f"gap change={r['gap_vs_kept_pct']:+.1f}%")
    out = os.path.join(ROOT, "experiments", "kept_vs_gap_release_analysis.json")
    with open(out, "w") as f:
        json.dump(result, f, indent=1)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
