#!/usr/bin/env python3
"""Condition-aware pool-transition models with grouped out-of-sample validation.

Saved-code version of the LORO analysis quoted in
docs/report_loop_integrator_decomposition.md, rewritten per the 2026-07-12
re-audit:
- reads ONLY the canonical deduplicated manifest (experiments/rollout_manifest.json);
- adds leave-one-SEED-out (LOSO) validation: all conditions sharing a seed are
  held out together, because matched conditions share initialization and
  round-0 sampling structure — LORO alone leaks that;
- writes every held-out prediction/residual to
  experiments/transition_model_predictions.json;
- PREDECLARED comparison model for any FUTURE data (e.g. the release grids):
  M2 = per-condition intercept + pooled kept-gap slope. Chosen now, before the
  release outputs exist; M0-M4 comparisons on K1-K3 below are exploratory
  (model selection on the same scores it reports), stated as such.

Transition unit: one round t of one rollout. Features: gap_t (mean gap_arm over
items), pool_t (mean pool coordinate), condition. Target: pool_{t+1} - pool_t.

Usage: uv run python scripts/analysis_transition_model.py
"""
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_rollout_manifest import ROOT, load_winning_records

POOL_FIELD = {"K1": "pool_risk", "K2": "pool_risk", "K3": "pool_candor"}


dropped = []  # (grid, cond, seed, t) with non-finite features, reported at the end


def transitions(grid):
    """[(cond, seed, t, gap_t, pool_t, drift_t)] from winning records only."""
    out = []
    for g, cond, seed, rec in load_winning_records(grid=grid):
        raws = rec.get("rounds_raw", [])
        pf = POOL_FIELD[grid]
        pools = [float(np.nanmean([e[pf] for e in raw if e[pf] is not None])) for raw in raws]
        gaps = [float(np.nanmean([e["gap_arm"] for e in raw if e["gap_arm"] is not None]))
                for raw in raws]
        for t in range(len(pools) - 1):
            row = (cond, seed, t, gaps[t], pools[t], pools[t + 1] - pools[t])
            if all(np.isfinite(v) for v in row[3:]):
                out.append(row)
            else:
                dropped.append((grid, cond, seed, t))
    return out


def design(rows, model, conds):
    """Design matrix per model. M0 zero; M1 1+gap; M2 cond-intercepts+gap;
    M3 cond-intercepts+cond-slopes; M4 M2+pool."""
    ci = {c: i for i, c in enumerate(conds)}
    X = []
    for cond, _sd, _t, gap, pool, _y in rows:
        if model == "M1":
            x = [1.0, gap]
        elif model == "M2":
            x = [0.0] * len(conds) + [gap]
            x[ci[cond]] = 1.0
        elif model == "M3":
            x = [0.0] * (2 * len(conds))
            x[ci[cond]] = 1.0
            x[len(conds) + ci[cond]] = gap
        elif model == "M4":
            x = [0.0] * len(conds) + [gap, pool]
            x[ci[cond]] = 1.0
        X.append(x)
    return np.array(X)


def fit_predict(train, test, model, conds):
    if model == "M0":
        return np.zeros(len(test))
    Xtr, ytr = design(train, model, conds), np.array([r[5] for r in train])
    Xte = design(test, model, conds)
    beta, *_ = np.linalg.lstsq(Xtr, ytr, rcond=None)
    return Xte @ beta


def grouped_cv(rows, group_key, model, conds):
    """Hold out one group at a time; return (preds aligned to rows order, groups)."""
    groups = sorted({group_key(r) for r in rows})
    preds = {}
    for g in groups:
        tr = [r for r in rows if group_key(r) != g]
        te = [r for r in rows if group_key(r) == g]
        if not te:
            continue
        p = fit_predict(tr, te, model, conds)
        for r, pi in zip(te, p):
            preds[(r[0], r[1], r[2])] = float(pi)
    return [preds[(r[0], r[1], r[2])] for r in rows]


def rmse(y, p):
    y, p = np.array(y), np.array(p)
    return float(np.sqrt(np.mean((y - p) ** 2)))


def main():
    results = {"predeclared_model_for_future_data": "M2 (per-condition intercept + pooled gap slope)",
               "grids": {}}
    for grid in ("K1", "K2", "K3"):
        rows = transitions(grid)
        if not rows:
            continue
        conds = sorted({r[0] for r in rows})
        y = [r[5] for r in rows]
        print(f"\n=== {grid}: {len(rows)} transitions, "
              f"{len({(r[0], r[1]) for r in rows})} rollouts, "
              f"{len({r[1] for r in rows})} seeds, conds {conds} ===")
        gr = {"n_transitions": len(rows), "conditions": conds, "schemes": {}}
        for scheme, key in (("LORO", lambda r: (r[0], r[1])), ("LOSO", lambda r: r[1])):
            line = {}
            for model in ("M0", "M1", "M2", "M3", "M4"):
                p = grouped_cv(rows, key, model, conds)
                line[model] = rmse(y, p)
                if model == "M2":
                    gr.setdefault("held_out_predictions_M2_" + scheme, [
                        {"condition": r[0], "seed": r[1], "t": r[2],
                         "gap": round(r[3], 4), "pool": round(r[4], 4),
                         "drift": round(r[5], 4), "pred": round(pi, 4),
                         "resid": round(r[5] - pi, 4)}
                        for r, pi in zip(rows, p)])
            gr["schemes"][scheme] = line
            rel = {m: f"{(line[m]/line['M0']-1)*100:+.0f}%" for m in line}
            print(f"  {scheme}: " + "  ".join(
                f"{m} {line[m]:.4f} ({rel[m]})" for m in ("M0", "M1", "M2", "M3", "M4")))
        loso_m2, loro_m2 = gr["schemes"]["LOSO"]["M2"], gr["schemes"]["LORO"]["M2"]
        print(f"  M2 gap-signal survives seed-grouped holdout: "
              f"LOSO {loso_m2:.4f} vs M0 {gr['schemes']['LOSO']['M0']:.4f} "
              f"({'YES' if loso_m2 < gr['schemes']['LOSO']['M0'] else 'NO'}); "
              f"LORO->LOSO degradation {(loso_m2/loro_m2-1)*100:+.0f}%")
        results["grids"][grid] = gr
    if dropped:
        print(f"\ndropped {len(dropped)} transitions with non-finite gap/pool: {dropped}")
        results["dropped_nonfinite_transitions"] = [list(d) for d in dropped]
    out = os.path.join(ROOT, "experiments/transition_model_predictions.json")
    json.dump(results, open(out, "w"), indent=1)
    print(f"\nwrote {out}")
    print("NOTE: M0-M4 comparison above is exploratory (selection on reported scores);")
    print("the only confirmatory use is the predeclared M2 on future/release data.")


if __name__ == "__main__":
    main()
