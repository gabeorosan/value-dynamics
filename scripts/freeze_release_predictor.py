#!/usr/bin/env python3
"""Freeze the prospective K2→release transition predictor (audit round 4, P0.2).

Fits the predeclared M2 (per-condition intercept + pooled kept-gap slope) on
the K2 grid ONLY and saves everything needed to score release data with NO
refitting: coefficients, the judge_used→intercept mapping, eligibility rules,
and the matched no-gap baseline (same intercepts, slope forced to 0 — so any
gain over baseline is attributable to the gap term alone).

Frozen 2026-07-12 late. Blindness status (recorded honestly): kernel A
endpoints and Modal branch-A partials through round 7 had been INSPECTED
before freezing; kernel B and the final Modal round were not. The test is
therefore mechanically-frozen-no-refit for everything, and prospective in the
strict sense only for kernel B and the Modal finals.

Usage:
  uv run python scripts/freeze_release_predictor.py            # freeze (refuses to overwrite)
  uv run python scripts/freeze_release_predictor.py score F..  # apply frozen predictor to release JSONs
"""
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_rollout_manifest import ROOT, load_winning_records

FROZEN_PATH = os.path.join(ROOT, "experiments/release_predictor_frozen.json")
K2_ARMS = ["evolving_self", "frozen_base", "frozen_cons_r0", "random_select"]
# release transitions are mapped to a K2 arm by the judge that made the
# selection (judge_used[t]); random phases in schedules use the same names
JUDGE_TO_ARM = {a: a for a in K2_ARMS}


def k2_transitions():
    rows = []
    for _g, cond, seed, rec in load_winning_records(grid="K2"):
        if rec.get("measure_only"):
            continue
        raws = rec.get("rounds_raw", [])
        pools = [float(np.mean([e["pool_risk"] for e in raw])) for raw in raws]
        gaps = [float(np.mean([e["gap_arm"] for e in raw])) for raw in raws]
        for t in range(len(pools) - 1):
            if all(np.isfinite(v) for v in (gaps[t], pools[t], pools[t + 1])):
                rows.append((cond, seed, t, gaps[t], pools[t + 1] - pools[t]))
    return rows


def freeze():
    if os.path.exists(FROZEN_PATH):
        raise SystemExit(f"{FROZEN_PATH} exists — the predictor is frozen; refusing to refit.")
    rows = k2_transitions()
    ci = {c: i for i, c in enumerate(K2_ARMS)}
    X = np.zeros((len(rows), len(K2_ARMS) + 1))
    y = np.array([r[4] for r in rows])
    for i, (c, _sd, _t, g, _d) in enumerate(rows):
        X[i, ci[c]] = 1.0
        X[i, -1] = g
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    art = {
        "frozen_at": "2026-07-12 late",
        "model": "M2: per-K2-arm intercept + pooled gap slope (predeclared)",
        "fit_on": f"K2 grid, {len(rows)} transitions, deduplicated manifest",
        "intercepts": {a: float(beta[ci[a]]) for a in K2_ARMS},
        "gap_slope": float(beta[-1]),
        "judge_to_arm": JUDGE_TO_ARM,
        "eligibility": "release transitions with finite mean gap_arm and pool_risk; "
                       "phase label = judge_used[t]; unknown judge labels are SKIPPED and reported",
        "baseline": "same intercepts, gap term zeroed (matched no-gap model)",
        "blindness": "kernel A + Modal branch-A partials (to r7) inspected pre-freeze; "
                     "kernel B and Modal finals not inspected",
    }
    json.dump(art, open(FROZEN_PATH, "w"), indent=1)
    print(f"frozen: slope {beta[-1]:+.3f}, intercepts " +
          ", ".join(f"{a} {beta[ci[a]]:+.4f}" for a in K2_ARMS))
    print(f"wrote {FROZEN_PATH}")


def score(paths):
    art = json.load(open(FROZEN_PATH))
    icpt, slope = art["intercepts"], art["gap_slope"]
    rows, skipped = [], {}
    for path in paths:
        d = json.load(open(path))
        for sd in (k for k in d if k.isdigit()):
            for cond, rec in d[sd].items():
                raws = rec.get("rounds_raw", [])
                judges = rec.get("judge_used", [])
                pools = [float(np.mean([e["pool_risk"] for e in raw])) for raw in raws]
                gaps = [float(np.mean([e["gap_arm"] for e in raw])) for raw in raws]
                for t in range(len(pools) - 1):
                    if not all(np.isfinite(v) for v in (gaps[t], pools[t], pools[t + 1])):
                        continue
                    ju = judges[t] if t < len(judges) else None
                    arm = art["judge_to_arm"].get(ju)
                    if arm is None:
                        skipped[ju] = skipped.get(ju, 0) + 1
                        continue
                    drift = pools[t + 1] - pools[t]
                    rows.append((cond, int(sd), t, arm, gaps[t], drift,
                                 icpt[arm] + slope * gaps[t], icpt[arm]))
    if not rows:
        print("no eligible transitions")
        return
    y = np.array([r[5] for r in rows])
    pm = np.array([r[6] for r in rows])
    pb = np.array([r[7] for r in rows])
    rmse = lambda p: float(np.sqrt(np.mean((y - p) ** 2)))
    print(f"frozen M2 on {len(rows)} release transitions "
          f"({len({(r[0], r[1]) for r in rows})} rollouts):")
    print(f"  frozen M2 RMSE      {rmse(pm):.4f}")
    print(f"  no-gap baseline     {rmse(pb):.4f}   (matched intercepts, slope=0)")
    print(f"  zero-drift          {rmse(np.zeros_like(y)):.4f}")
    print(f"  gap term changes RMSE by {(rmse(pm) / rmse(pb) - 1) * 100:+.1f}% vs no-gap")
    by = {}
    for r in rows:
        by.setdefault((r[0], r[3]), []).append(r)
    for (cond, arm), rs in sorted(by.items()):
        yy = np.array([r[5] for r in rs])
        mm = np.array([r[6] for r in rs])
        bb = np.array([r[7] for r in rs])
        print(f"  {cond:14s} phase={arm:14s} n={len(rs):2d} "
              f"M2 {float(np.sqrt(np.mean((yy-mm)**2))):.4f} "
              f"no-gap {float(np.sqrt(np.mean((yy-bb)**2))):.4f}")
    if skipped:
        print(f"  skipped transitions by unknown judge label: {skipped}")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "score":
        score(sys.argv[2:])
    else:
        freeze()
