#!/usr/bin/env python3
"""Closing uncertainty and failure-domain checks for the final writeup.

All analyses are post-hoc. Cluster bootstraps resample held-out residuals by
seed/rollout without refitting the cross-validation models, so they quantify
paired test-set uncertainty conditional on the saved predictions rather than
full model-selection uncertainty.
"""

import json
import itertools
import math
import os
import random
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from analysis_kept_vs_gap import ARMS, FROZEN, fit_kept_only, load_release
from analysis_mixed_first_step import olmo_rows, qwen_rows
from analysis_transition_model import ROOT, grouped_cv, transitions
from build_rollout_manifest import load_winning_records


RNG_SEED = 7132026
N_BOOT = 20000


def rmse(y, p):
    return float(np.sqrt(np.mean((np.asarray(y) - np.asarray(p)) ** 2)))


def paired_cluster_bootstrap(y, pa, pb, groups, n=N_BOOT):
    """RMSE(A)-RMSE(B), resampling whole test clusters with replacement."""
    y, pa, pb = map(np.asarray, (y, pa, pb))
    unique = sorted(set(groups), key=str)
    idx = {g: np.array([i for i, x in enumerate(groups) if x == g]) for g in unique}
    observed = rmse(y, pa) - rmse(y, pb)
    rng = random.Random(RNG_SEED)
    draws = []
    for _ in range(n):
        take = np.concatenate([idx[rng.choice(unique)] for _ in unique])
        draws.append(rmse(y[take], pa[take]) - rmse(y[take], pb[take]))
    draws.sort()
    lo = draws[int(0.025 * n)]
    hi = draws[int(0.975 * n)]
    return {"clusters": len(unique), "rmse_difference_a_minus_b": observed,
            "ci95": [lo, hi], "bootstrap_fraction_a_better": float(np.mean(np.array(draws) < 0))}


def original_grid_uncertainty():
    out = {}
    for grid in ("K1", "K2", "K3"):
        rows = transitions(grid)
        conds = sorted({r[0] for r in rows})
        y = [r[5] for r in rows]
        p_gap = grouped_cv(rows, lambda r: r[1], "M2", conds)
        p_nogap = grouped_cv(rows, lambda r: r[1], "Bcond", conds)
        p_kept = grouped_cv(rows, lambda r: r[1], "Kcond", conds)
        groups = [r[1] for r in rows]
        out[grid] = {
            "gap_vs_no_gap": paired_cluster_bootstrap(y, p_gap, p_nogap, groups),
            "gap_vs_kept_only": paired_cluster_bootstrap(y, p_gap, p_kept, groups),
        }
    return out


def release_groups():
    modal = os.path.join(ROOT, "experiments", "modal_k2_release", "output")
    return {
        "kernel_b": [os.path.join(ROOT, "experiments", "kaggle",
                                  "kaggle_k2_release_relB", "output",
                                  "k2_release_kernelB.json")],
        "modal_branch_a": [os.path.join(modal, f) for f in (
            "k2rel_press_to_base_s1.json", "k2rel_press_to_base_s2.json",
            "k2rel_press_to_base_s3.json", "k2rel_base_hold_s1.json",
            "k2rel_base_hold_s2.json")],
        "press_depth": [os.path.join(modal, f"k2rel_press_d{d}_s{s}.json")
                        for d in (1, 2, 3) for s in (1, 2)],
    }


def release_uncertainty():
    kept_intercepts, kept_slope, _ = fit_kept_only()
    no_gap = json.load(open(os.path.join(ROOT, "experiments",
                                         "release_predictor_nogap_frozen.json")))["intercepts"]
    out = {}
    for name, paths in release_groups().items():
        rows = load_release(paths)
        y = [r[6] for r in rows]
        p_gap = [FROZEN["intercepts"][r[3]] + FROZEN["gap_slope"] * r[5] for r in rows]
        p_kept = [kept_intercepts[r[3]] + kept_slope * (r[4] + r[5]) for r in rows]
        p_nogap = [no_gap[r[3]] for r in rows]
        groups = [(r[0], r[1]) for r in rows]
        out[name] = {
            "n_transitions": len(rows),
            "gap_vs_no_gap": paired_cluster_bootstrap(y, p_gap, p_nogap, groups),
            "gap_vs_kept_only": paired_cluster_bootstrap(y, p_gap, p_kept, groups),
        }
    return out


def spread_lookup(grid):
    cand_field = {"K1": "cand_risk", "K2": "cand_risk", "K3": "cand_candor"}[grid]
    pool_field = {"K1": "pool_risk", "K2": "pool_risk", "K3": "pool_candor"}[grid]
    out = {}
    for _g, cond, seed, rec in load_winning_records(grid=grid):
        if rec.get("measure_only"):
            continue
        raws = rec.get("rounds_raw", [])
        pools = [float(np.nanmean([e[pool_field] for e in raw if e[pool_field] is not None]))
                 for raw in raws]
        gaps = [float(np.nanmean([e["gap_arm"] for e in raw if e["gap_arm"] is not None]))
                for raw in raws]
        for t in range(len(pools) - 1):
            vals = [float(np.std(e[cand_field])) for e in raws[t] if e.get(cand_field)]
            if vals and all(np.isfinite(v) for v in (pools[t], pools[t + 1], gaps[t])):
                out[(cond, seed, t)] = float(np.mean(vals))
    return out


def corr(x, y):
    return float(np.corrcoef(x, y)[0, 1]) if len(x) > 1 and np.std(x) and np.std(y) else None


def residual_domains():
    out = {}
    for grid in ("K1", "K2", "K3"):
        rows = transitions(grid)
        conds = sorted({r[0] for r in rows})
        pred = grouped_cv(rows, lambda r: r[1], "M2", conds)
        spreads = spread_lookup(grid)
        records = []
        for r, p in zip(rows, pred):
            records.append({"condition": r[0], "seed": r[1], "t": r[2],
                            "gap": r[3], "pool": r[4], "drift": r[5],
                            "prediction": p, "residual": r[5] - p,
                            "spread": spreads[(r[0], r[1], r[2])]})
        abs_resid = [abs(r["residual"]) for r in records]
        by_condition = {}
        for condition in conds:
            rr = [r for r in records if r["condition"] == condition]
            by_condition[condition] = {"n": len(rr), "rmse": rmse(
                [r["drift"] for r in rr], [r["prediction"] for r in rr])}
        by_round = {}
        for t in sorted({r["t"] for r in records}):
            rr = [r for r in records if r["t"] == t]
            by_round[str(t)] = {"n": len(rr), "rmse": rmse(
                [r["drift"] for r in rr], [r["prediction"] for r in rr])}
        low = [r for r in records if r["spread"] <= 0.05]
        high = [r for r in records if r["spread"] > 0.05]
        boundary = [r for r in records if min(r["pool"], 1 - r["pool"]) <= 0.10]
        interior = [r for r in records if min(r["pool"], 1 - r["pool"]) > 0.10]
        group_rmse = lambda rr: (None if not rr else rmse(
            [r["drift"] for r in rr], [r["prediction"] for r in rr]))
        out[grid] = {
            "correlation_abs_residual_with_spread": corr(abs_resid, [r["spread"] for r in records]),
            "correlation_abs_residual_with_abs_gap": corr(abs_resid, [abs(r["gap"]) for r in records]),
            "correlation_abs_residual_with_boundary_distance": corr(
                abs_resid, [min(r["pool"], 1 - r["pool"]) for r in records]),
            "rmse_low_spread_le_0.05": {"n": len(low), "rmse": group_rmse(low)},
            "rmse_higher_spread": {"n": len(high), "rmse": group_rmse(high)},
            "rmse_near_boundary": {"n": len(boundary), "rmse": group_rmse(boundary)},
            "rmse_interior": {"n": len(interior), "rmse": group_rmse(interior)},
            "by_condition": by_condition,
            "by_round": by_round,
            "largest_absolute_residuals": sorted(records, key=lambda r: abs(r["residual"]), reverse=True)[:5],
        }
    return out


def mixed_sensitivity():
    rows = list(olmo_rows()) + list(qwen_rows())
    gaps = np.array([r[2] for r in rows])
    moves = np.array([r[3] for r in rows])
    observed = corr(gaps, moves)
    aligned = sum(g * m > 0 for g, m in zip(gaps, moves))
    one_sided_sign_p = sum(math.comb(len(rows), k) for k in range(aligned, len(rows) + 1)) / 2 ** len(rows)
    olmo = [r for r in rows if r[1] == "OLMo risk"]
    loo = []
    for i, row in enumerate(rows):
        keep = [r for j, r in enumerate(rows) if j != i]
        loo.append({"left_out": row[0], "correlation": corr(
            [r[2] for r in keep], [r[3] for r in keep])})
    rng = random.Random(RNG_SEED)
    boots = []
    for _ in range(N_BOOT):
        sample = [rows[rng.randrange(len(rows))] for _ in rows]
        c = corr([r[2] for r in sample], [r[3] for r in sample])
        if c is not None:
            boots.append(c)
    boots.sort()
    perm_rng = np.random.default_rng(RNG_SEED)
    perm = []
    for _ in range(N_BOOT):
        perm.append(abs(corr(gaps, perm_rng.permutation(moves))))
    def family(row):
        label = row[0]
        if label.startswith("low_55_707"):
            return "qwen_oracle_mix"
        return label.rsplit("_s", 1)[0]
    families = sorted({family(r) for r in rows})
    group_rows = []
    for name in families:
        rr = [r for r in rows if family(r) == name]
        group_rows.append((name, float(np.mean([r[2] for r in rr])),
                           float(np.mean([r[3] for r in rr]))))
    group_corr = corr([r[1] for r in group_rows], [r[2] for r in group_rows])
    group_perm = [abs(corr([r[1] for r in group_rows], p))
                  for p in itertools.permutations([r[2] for r in group_rows])]
    group_boot = []
    for _ in range(N_BOOT):
        sampled_names = [rng.choice(families) for _ in families]
        sample = [r for name in sampled_names for r in rows if family(r) == name]
        c = corr([r[2] for r in sample], [r[3] for r in sample])
        if c is not None:
            group_boot.append(c)
    group_boot.sort()
    return {
        "n_cells": len(rows), "sign_aligned": aligned,
        "one_sided_exact_sign_p": one_sided_sign_p,
        "pooled_correlation": observed,
        "bootstrap_ci95_cells": [boots[int(.025 * len(boots))], boots[int(.975 * len(boots))]],
        "permutation_p_two_sided": float(np.mean(np.array(perm) >= abs(observed))),
        "olmo_only_correlation_n8": corr([r[2] for r in olmo], [r[3] for r in olmo]),
        "leave_one_cell_out": loo,
        "condition_family_means": [
            {"family": name, "mean_gap": gap, "mean_move": move}
            for name, gap, move in group_rows],
        "condition_family_mean_correlation_n5": group_corr,
        "condition_family_exact_permutation_p_two_sided": float(
            np.mean(np.array(group_perm) >= abs(group_corr))),
        "condition_family_cluster_bootstrap_ci95": [
            group_boot[int(.025 * len(group_boot))], group_boot[int(.975 * len(group_boot))]],
    }


def main():
    result = {
        "status": "post-hoc closing diagnostics",
        "bootstrap_note": "clusters resampled without refitting; few clusters make intervals unstable",
        "original_grid_uncertainty": original_grid_uncertainty(),
        "release_uncertainty": release_uncertainty(),
        "transition_residual_domains": residual_domains(),
        "mixed_first_step_sensitivity": mixed_sensitivity(),
    }
    out = os.path.join(ROOT, "experiments", "closing_analysis_diagnostics.json")
    with open(out, "w") as f:
        json.dump(result, f, indent=1,
                  default=lambda value: value.item() if isinstance(value, np.generic) else str(value))
    for grid, tests in result["original_grid_uncertainty"].items():
        print(grid, tests)
    for name, tests in result["release_uncertainty"].items():
        print(name, tests)
    print("mixed", result["mixed_first_step_sensitivity"])
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
