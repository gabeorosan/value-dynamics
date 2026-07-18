"""Held-out test of the one-round selection-response law on the judge-ablation runs.

The unit model (writeup 'One round' section; experiments/spread_util_unified.json)
was fit on the earlier program: per-round kept-minus-pool gap ~= C * rho * sigma
with C = 0.96 (committed pooled slope 0.958, r = 0.901, n = 290), and next-round
own-pool drift ~= K * gap (committed pooled drift~pull slope 0.833; drift~gap
0.928). The 14 judge-ablation runs (4 files: candid/neutral x self/base judge,
supplier-removed em750, seeds 41-46) are HELD OUT from those fits — none of
their pools contributed. This script scores the frozen law on them:

  (1) factorization: observed per-round gap vs 0.96*rho*sigma (frozen; refit
      slope reported alongside), on the candidate sr axis (cand_sr_scores).
  (2) movement: next-round own-pool sr mean change vs the realized gap, vs the
      frozen 0.833 slope (self-only pools: pull == gap).
  (3) the rho (agreement) trajectory per run — the writeup's 'missing
      agreement trajectory', extracted from banked duel scores: does the sign
      of rho track each condition's direction (candid-self +, base -), and do
      the non-monotone seeds (42, 43, 46) show rho sign flips?

Conventions copied from scripts/analysis_spread_util_unified.py: per-item
Pearson rho(judge score, candidate value), items skipped if <3 candidates or
either vector has std < 1e-9; gap/sigma/pool-mean averaged over valid items;
np.std population SD.

Inputs (experiments/em_selfaware_loop/output/): head2head_selfjudge_selfonly
{,_s43_46}.json, head2head_basejudge_selfonly.json,
head2head_neutralstyle_selfonly{,_s43_46}.json.
Output: experiments/ablation_unit_law.json

Usage: uv run python scripts/analysis_ablation_unit_law.py
"""

import json
import os

import numpy as np

SRC = "experiments/em_selfaware_loop/output"
OUT = "experiments/ablation_unit_law.json"
C_FROZEN = 0.96      # factorization constant (simple_model_rollout.json model.C)
K_FROZEN = 0.833     # movement drift~pull pooled slope (spread_util_unified.json)

FILES = {
    "candid_self": ["head2head_selfjudge_selfonly.json",
                    "head2head_selfjudge_selfonly_s43_46.json"],
    "neutral_self": ["head2head_neutralstyle_selfonly.json",
                     "head2head_neutralstyle_selfonly_s43_46.json"],
    "candid_base": ["head2head_basejudge_selfonly.json"],
}


def round_record(items):
    gaps, sigmas, rhos, pool_means = [], [], [], []
    for it in items:
        c = it.get("cand_sr_scores")
        kidx = it.get("kept_idx")
        if not c or not kidx:
            continue
        c = np.asarray(c, float)
        pool_means.append(float(c.mean()))
        gaps.append(float(c[kidx].mean() - c.mean()))
        sigmas.append(float(c.std()))
        s = it.get("scores")
        if (len(c) >= 3 and np.std(c) > 1e-9 and isinstance(s, list)
                and len(s) == len(c) and np.std(s) > 1e-9):
            rhos.append(float(np.corrcoef(s, c)[0, 1]))
    if not pool_means:
        return None
    return {
        "gap": float(np.mean(gaps)),
        "sigma": float(np.mean(sigmas)),
        "rho": float(np.mean(rhos)) if rhos else None,
        "n_rho_items": len(rhos),
        "pool_mean": float(np.mean(pool_means)),
    }


def ols(x, y):
    x, y = np.asarray(x, float), np.asarray(y, float)
    if len(x) < 3 or x.std() < 1e-12:
        return None
    slope, intercept = np.polyfit(x, y, 1)
    r = float(np.corrcoef(x, y)[0, 1])
    return {"slope": round(float(slope), 3), "intercept": round(float(intercept), 4),
            "r": round(r, 3), "n": int(len(x))}


def main():
    runs = {}
    for cond, files in FILES.items():
        for fn in files:
            path = os.path.join(SRC, fn)
            if not os.path.isfile(path):
                print(f"!! missing {fn}, skipping")
                continue
            d = json.load(open(path))
            for cell, c in d["cells"].items():
                seed = cell.split(":")[1]
                recs = []
                for ridx, items in enumerate(c["rounds_raw"], start=1):
                    rec = round_record(items)
                    if rec:
                        rec["round"] = ridx
                        recs.append(rec)
                runs[f"{cond}:{seed}"] = {"condition": cond, "seed": seed,
                                          "rounds": recs}

    # ---- (1) factorization, all rounds pooled + per condition ----
    fact_pts = []   # (rho*sigma, gap, cond)
    for tag, run in runs.items():
        for rec in run["rounds"]:
            if rec["rho"] is not None:
                fact_pts.append((rec["rho"] * rec["sigma"], rec["gap"],
                                 run["condition"]))
    result = {"what": ("Held-out test of gap~=0.96*rho*sigma and "
                       "drift~=0.833*gap on the 14 judge-ablation runs "
                       "(56 rounds); conventions from "
                       "analysis_spread_util_unified.py"),
              "frozen_constants": {"C": C_FROZEN, "K": K_FROZEN},
              "factorization": {}, "movement": {}, "rho_trajectories": {}}
    xs = [p[0] for p in fact_pts]
    ys = [p[1] for p in fact_pts]
    pred = [C_FROZEN * x for x in xs]
    result["factorization"]["pooled"] = {
        "n": len(xs),
        "frozen_C_mae": round(float(np.mean(np.abs(np.array(ys) - np.array(pred)))), 4),
        "refit": ols(xs, ys),
    }
    for cond in FILES:
        sub = [(x, y) for x, y, c in fact_pts if c == cond]
        if len(sub) >= 3:
            sx, sy = zip(*sub)
            sp = [C_FROZEN * x for x in sx]
            result["factorization"][cond] = {
                "n": len(sx),
                "frozen_C_mae": round(float(np.mean(np.abs(np.array(sy) - np.array(sp)))), 4),
                "refit": ols(sx, sy),
            }

    # ---- (2) movement: drift vs gap ----
    mov_pts = []
    for tag, run in runs.items():
        rs = {rec["round"]: rec for rec in run["rounds"]}
        for r in (1, 2, 3):
            if r in rs and (r + 1) in rs:
                drift = rs[r + 1]["pool_mean"] - rs[r]["pool_mean"]
                mov_pts.append((rs[r]["gap"], drift, run["condition"]))
    xs = [p[0] for p in mov_pts]
    ys = [p[1] for p in mov_pts]
    predK = [K_FROZEN * x for x in xs]
    result["movement"]["pooled"] = {
        "n": len(xs),
        "frozen_K_mae": round(float(np.mean(np.abs(np.array(ys) - np.array(predK)))), 4),
        "persistence_mae": round(float(np.mean(np.abs(ys))), 4),  # drift=0 baseline
        "refit": ols(xs, ys),
    }
    for cond in FILES:
        sub = [(x, y) for x, y, c in mov_pts if c == cond]
        if len(sub) >= 3:
            sx, sy = zip(*sub)
            sp = [K_FROZEN * x for x in sx]
            result["movement"][cond] = {
                "n": len(sx),
                "frozen_K_mae": round(float(np.mean(np.abs(np.array(sy) - np.array(sp)))), 4),
                "persistence_mae": round(float(np.mean(np.abs(sy))), 4),
                "refit": ols(sx, sy),
            }

    # ---- (3) rho trajectories ----
    for tag, run in sorted(runs.items()):
        result["rho_trajectories"][tag] = {
            "rho": [None if rec["rho"] is None else round(rec["rho"], 3)
                    for rec in run["rounds"]],
            "sigma": [round(rec["sigma"], 3) for rec in run["rounds"]],
            "gap": [round(rec["gap"], 4) for rec in run["rounds"]],
            "pool_mean": [round(rec["pool_mean"], 3) for rec in run["rounds"]],
        }

    json.dump(result, open(OUT, "w"), indent=2)
    print(f"wrote {OUT}\n")
    print("=== factorization: observed gap vs frozen 0.96*rho*sigma ===")
    for k, v in result["factorization"].items():
        print(f"  {k}: n={v['n']} frozen-C MAE={v['frozen_C_mae']} refit={v['refit']}")
    print("\n=== movement: next-round pool drift vs frozen 0.833*gap ===")
    for k, v in result["movement"].items():
        print(f"  {k}: n={v['n']} frozen-K MAE={v['frozen_K_mae']} "
              f"persistence MAE={v['persistence_mae']} refit={v['refit']}")
    print("\n=== rho trajectories (agreement, per run) ===")
    for tag, t in result["rho_trajectories"].items():
        print(f"  {tag}: rho {t['rho']} sigma {t['sigma']} pool_mean {t['pool_mean']}")


if __name__ == "__main__":
    main()
