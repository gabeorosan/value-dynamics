#!/usr/bin/env python3
"""Audit the proposed "value centrality -> candidate spread" mechanism.

The first version of this analysis regressed candidate spread on the current
model value's centrality, v(1-v), and interpreted the pooled association as a
new dynamical law. That interpretation is not identified by these data.

The candidate axes in ``spread_util_unified.json`` are 0/1-scored. For a
Bernoulli coordinate with mean p, its population SD is sqrt(p(1-p)). The
reported spread is a mean of within-item SDs, so sqrt(pool_mean(1-pool_mean))
is an aggregate upper-bound/proxy imposed by the scoring geometry itself.
Model value and candidate-pool mean are also highly correlated. This script
therefore compares:

  state centrality       value * (1-value)
  pool centrality        pool_mean * (1-pool_mean)
  pool SD ceiling        sqrt(pool centrality)

It reports pooled OLS only as a descriptive baseline, then adds within-run
demeaning, consecutive-round first differences, and leave-one-run-out fits.
It also audits the old "self-limiting" claim against the directly measured
selection pull. None of these observational comparisons identifies a causal
state-to-spread law; they test whether state centrality adds information after
the candidate pool's bounded score geometry is accounted for.

Reads:  experiments/spread_util_unified.json
Writes: experiments/spread_value_centrality.json
Run:    uv run python scripts/analysis_spread_value_centrality.py
"""

import json
import math
import os
from collections import defaultdict

import numpy as np


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "experiments", "spread_util_unified.json")
OUT = os.path.join(ROOT, "experiments", "spread_value_centrality.json")


def run_key(row):
    return tuple(row.get(k) for k in ("organism", "axis", "cond", "seed", "source"))


def state_centrality(row):
    v = row.get("value")
    return None if v is None else v * (1.0 - v)


def pool_centrality(row):
    p = row.get("pool_mean")
    return None if p is None else p * (1.0 - p)


def pool_sd_ceiling(row):
    c = pool_centrality(row)
    return None if c is None else math.sqrt(max(0.0, c))


def corr(rows, x, y):
    pairs = [(x(r), y(r)) for r in rows if x(r) is not None and y(r) is not None]
    if len(pairs) < 3:
        return {"r": None, "n": len(pairs)}
    a = np.asarray([p[0] for p in pairs], float)
    b = np.asarray([p[1] for p in pairs], float)
    if np.std(a) < 1e-12 or np.std(b) < 1e-12:
        return {"r": None, "n": len(pairs)}
    return {"r": float(np.corrcoef(a, b)[0, 1]), "n": len(pairs)}


def fit_arrays(y, columns, intercept=True):
    y = np.asarray(y, float)
    x = np.column_stack([np.asarray(c, float) for c in columns])
    if intercept:
        x = np.column_stack([np.ones(len(y)), x])
    beta, _, _, _ = np.linalg.lstsq(x, y, rcond=None)
    pred = x @ beta
    ss_res = float(np.sum((y - pred) ** 2))
    ss_tot = float(np.sum((y - np.mean(y)) ** 2))
    return {
        "beta": [float(v) for v in beta],
        "r2": (1.0 - ss_res / ss_tot) if ss_tot > 1e-12 else None,
        "n": int(len(y)),
    }


def ols(rows, y, features):
    used = [r for r in rows if y(r) is not None and all(f(r) is not None for f in features)]
    if len(used) < len(features) + 2:
        return {"beta": None, "r2": None, "n": len(used)}
    return fit_arrays([y(r) for r in used], [[f(r) for r in used] for f in features])


def within_run_ols(rows, y, features):
    """Run-fixed-effect fit by demeaning y and every feature within run."""
    used = [r for r in rows if y(r) is not None and all(f(r) is not None for f in features)]
    groups = defaultdict(list)
    for r in used:
        groups[run_key(r)].append(r)
    yd, xd = [], [[] for _ in features]
    for group in groups.values():
        if len(group) < 2:
            continue
        ym = float(np.mean([y(r) for r in group]))
        xm = [float(np.mean([f(r) for r in group])) for f in features]
        for r in group:
            yd.append(y(r) - ym)
            for j, f in enumerate(features):
                xd[j].append(f(r) - xm[j])
    if len(yd) < len(features) + 2:
        return {"beta": None, "r2": None, "n": len(yd), "n_runs": len(groups)}
    out = fit_arrays(yd, xd, intercept=False)
    out["n_runs"] = sum(len(g) >= 2 for g in groups.values())
    return out


def difference_rows(rows):
    """Create changes between consecutive observed rounds in the same run."""
    groups = defaultdict(list)
    for r in rows:
        groups[run_key(r)].append(r)
    out = []
    fields = ("spread", "value", "pool_mean", "source_sep")
    for key, group in groups.items():
        ordered = sorted(group, key=lambda r: r["round"])
        for a, b in zip(ordered, ordered[1:]):
            if b["round"] != a["round"] + 1:
                continue
            d = {"run_key": key, "round_from": a["round"], "round_to": b["round"]}
            for field in fields:
                d[f"d_{field}"] = (
                    None if a.get(field) is None or b.get(field) is None
                    else b[field] - a[field]
                )
            d["d_state_centrality"] = state_centrality(b) - state_centrality(a)
            d["d_pool_centrality"] = pool_centrality(b) - pool_centrality(a)
            d["d_pool_sd_ceiling"] = pool_sd_ceiling(b) - pool_sd_ceiling(a)
            d["composition"] = a.get("composition")
            d["organism"] = a.get("organism")
            out.append(d)
    return out


def loro(rows, y, features):
    """Leave one run out; return pooled out-of-fold R2 and error."""
    used = [r for r in rows if y(r) is not None and all(f(r) is not None for f in features)]
    keys = sorted({run_key(r) for r in used})
    actual, pred = [], []
    for held in keys:
        train = [r for r in used if run_key(r) != held]
        test = [r for r in used if run_key(r) == held]
        if len(train) < len(features) + 2 or not test:
            continue
        yy = np.asarray([y(r) for r in train], float)
        xx = np.asarray([[1.0] + [f(r) for f in features] for r in train], float)
        beta, _, _, _ = np.linalg.lstsq(xx, yy, rcond=None)
        for r in test:
            actual.append(y(r))
            pred.append(float(np.dot([1.0] + [f(r) for f in features], beta)))
    actual = np.asarray(actual, float)
    pred = np.asarray(pred, float)
    if len(actual) < 3:
        return {"r2_oof": None, "mae": None, "n": int(len(actual)), "n_runs": len(keys)}
    ss_tot = float(np.sum((actual - np.mean(actual)) ** 2))
    return {
        "r2_oof": 1.0 - float(np.sum((actual - pred) ** 2)) / ss_tot,
        "mae": float(np.mean(np.abs(actual - pred))),
        "n": int(len(actual)),
        "n_runs": len(keys),
    }


def model_block(rows, y, feature_map, within=False):
    fit = within_run_ols if within else ols
    return {name: fit(rows, y, feats) for name, feats in feature_map.items()}


def main():
    with open(SRC) as f:
        records = json.load(f)["records"]
    rows = [r for r in records if r.get("spread") is not None and r.get("value") is not None]
    self_only = [r for r in rows if r.get("composition") == "self-only"]
    mixed = [r for r in rows if r.get("composition") in ("base-mixed", "peer-mixed")]

    y_spread = lambda r: r.get("spread")
    features = {
        "state_centrality": [state_centrality],
        "pool_centrality": [pool_centrality],
        "pool_sd_ceiling": [pool_sd_ceiling],
        "pool_sd_ceiling_plus_state_centrality": [pool_sd_ceiling, state_centrality],
        "pool_centrality_plus_state_centrality": [pool_centrality, state_centrality],
    }

    subsets = {"all": rows, "self_only": self_only, "mixed": mixed}
    correlations = {}
    for name, subset in subsets.items():
        correlations[name] = {
            "spread_vs_state_centrality": corr(subset, y_spread, state_centrality),
            "spread_vs_pool_centrality": corr(subset, y_spread, pool_centrality),
            "spread_vs_pool_sd_ceiling": corr(subset, y_spread, pool_sd_ceiling),
            "spread_vs_round": corr(subset, y_spread, lambda r: r.get("round")),
            "value_vs_pool_mean": corr(subset, lambda r: r.get("value"), lambda r: r.get("pool_mean")),
            "state_vs_pool_centrality": corr(subset, state_centrality, pool_centrality),
        }

    pooled = {name: model_block(subset, y_spread, features) for name, subset in subsets.items()}
    within = {name: model_block(subset, y_spread, features, within=True)
              for name, subset in subsets.items()}

    diffs = difference_rows(rows)
    diff_subsets = {
        "all": diffs,
        "self_only": [r for r in diffs if r["composition"] == "self-only"],
        "mixed": [r for r in diffs if r["composition"] in ("base-mixed", "peer-mixed")],
    }
    dy = lambda r: r.get("d_spread")
    diff_features = {
        "delta_state_centrality": [lambda r: r.get("d_state_centrality")],
        "delta_pool_centrality": [lambda r: r.get("d_pool_centrality")],
        "delta_pool_sd_ceiling": [lambda r: r.get("d_pool_sd_ceiling")],
        "delta_pool_centrality_plus_delta_state_centrality": [
            lambda r: r.get("d_pool_centrality"), lambda r: r.get("d_state_centrality")
        ],
        "delta_pool_sd_ceiling_plus_delta_state_centrality": [
            lambda r: r.get("d_pool_sd_ceiling"), lambda r: r.get("d_state_centrality")
        ],
    }
    first_differences = {
        name: model_block(subset, dy, diff_features) for name, subset in diff_subsets.items()
    }

    # In mixed pools, test whether supplier separation adds anything after the
    # bounded candidate-pool geometry. It can: sources can differ item by item
    # even when their aggregate means are similar. The effect is descriptive.
    mixed_models = {
        "state_centrality_plus_source_separation": [state_centrality, lambda r: r.get("source_sep")],
        "pool_sd_ceiling_plus_source_separation": [pool_sd_ceiling, lambda r: r.get("source_sep")],
        "pool_sd_ceiling_plus_source_separation_plus_state_centrality": [
            pool_sd_ceiling, lambda r: r.get("source_sep"), state_centrality
        ],
    }
    mixed_source = {
        "pooled": model_block(mixed, y_spread, mixed_models),
        "within_run": model_block(mixed, y_spread, mixed_models, within=True),
        "first_differences": model_block(
            diff_subsets["mixed"], dy,
            {
                "delta_pool_sd_ceiling_plus_delta_source_separation": [
                    lambda r: r.get("d_pool_sd_ceiling"), lambda r: r.get("d_source_sep")
                ],
                "delta_pool_sd_ceiling_plus_delta_source_separation_plus_delta_state_centrality": [
                    lambda r: r.get("d_pool_sd_ceiling"), lambda r: r.get("d_source_sep"),
                    lambda r: r.get("d_state_centrality")
                ],
            },
        ),
    }

    loro_models = {}
    for name, subset in subsets.items():
        loro_models[name] = {
            label: loro(subset, y_spread, feats) for label, feats in features.items()
        }

    per_family = {}
    for organism in sorted({r.get("organism") for r in rows}):
        subset = [r for r in rows if r.get("organism") == organism]
        per_family[organism] = {
            "n": len(subset),
            "pooled": model_block(subset, y_spread, features),
            "within_run": model_block(subset, y_spread, features, within=True),
        }

    # The old report called smaller |drift| near 0/1 evidence that centrality
    # makes the loop self-limiting. This comparison is boundary-censored and
    # omits the direct driver (selection pull). Report both rather than infer an
    # attractor from the marginal band contrast.
    abs_drift = lambda r: abs(r["drift"]) if r.get("drift") is not None else None
    abs_pull = lambda r: abs(r["pull"]) if r.get("pull") is not None else None
    movement_models = {
        "state_centrality": [state_centrality],
        "absolute_pull": [abs_pull],
        "absolute_pull_plus_state_centrality": [abs_pull, state_centrality],
        "spread_plus_absolute_pull": [y_spread, abs_pull],
        "spread_plus_absolute_pull_plus_state_centrality": [y_spread, abs_pull, state_centrality],
    }
    movement = {name: model_block(subset, abs_drift, movement_models)
                for name, subset in subsets.items()}
    tail = [abs(r["drift"]) for r in rows if r.get("drift") is not None and state_centrality(r) < 0.05]
    band = [abs(r["drift"]) for r in rows if r.get("drift") is not None and state_centrality(r) >= 0.15]
    movement["old_band_comparison"] = {
        "mean_abs_drift_extreme_tail": float(np.mean(tail)),
        "n_extreme_tail": len(tail),
        "mean_abs_drift_central_band": float(np.mean(band)),
        "n_central_band": len(band),
        "warning": "Descriptive and boundary-censored; it does not identify stable attractors.",
    }

    def incremental(block, baseline, expanded):
        a = block[baseline]["r2"]
        b = block[expanded]["r2"]
        return None if a is None or b is None else b - a

    headline = {
        "mixed_old_state_centrality_pooled_r2": pooled["mixed"]["state_centrality"]["r2"],
        "mixed_pool_centrality_pooled_r2": pooled["mixed"]["pool_centrality"]["r2"],
        "mixed_pool_sd_ceiling_pooled_r2": pooled["mixed"]["pool_sd_ceiling"]["r2"],
        "mixed_state_centrality_increment_after_ceiling_pooled_r2": incremental(
            pooled["mixed"], "pool_sd_ceiling", "pool_sd_ceiling_plus_state_centrality"
        ),
        "mixed_state_centrality_increment_after_ceiling_within_run_r2": incremental(
            within["mixed"], "pool_sd_ceiling", "pool_sd_ceiling_plus_state_centrality"
        ),
        "mixed_state_centrality_increment_after_ceiling_first_difference_r2": incremental(
            first_differences["mixed"], "delta_pool_sd_ceiling",
            "delta_pool_sd_ceiling_plus_delta_state_centrality"
        ),
        "mixed_state_centrality_increment_after_pool_centrality_pooled_r2": incremental(
            pooled["mixed"], "pool_centrality", "pool_centrality_plus_state_centrality"
        ),
        "mixed_state_centrality_increment_after_pool_centrality_within_run_r2": incremental(
            within["mixed"], "pool_centrality", "pool_centrality_plus_state_centrality"
        ),
        "mixed_state_centrality_increment_after_pool_centrality_first_difference_r2": incremental(
            first_differences["mixed"], "delta_pool_centrality",
            "delta_pool_centrality_plus_delta_state_centrality"
        ),
        "all_value_vs_pool_mean_r": correlations["all"]["value_vs_pool_mean"]["r"],
        "interpretation": (
            "The old pooled association is real descriptively, but state centrality is mostly a proxy "
            "for the bounded 0/1 geometry of the candidate pool. These data do not establish a causal "
            "state-centrality law or stable attractors. The supported operational claim is narrower: "
            "selection on the measured axis stalls when the candidate pool supplies no rankable variation, "
            "and an outside supplier can restore that variation."
        ),
    }

    out = {
        "description": "Audit and correction of the proposed value-centrality mechanism for candidate spread.",
        "source": os.path.relpath(SRC, ROOT),
        "counts": {
            "rounds": len(rows),
            "runs": len({run_key(r) for r in rows}),
            "self_only_rounds": len(self_only),
            "mixed_rounds": len(mixed),
            "consecutive_transitions": len(diffs),
        },
        "definitions": {
            "spread": "Mean within-item population SD of 0/1 candidate value scores.",
            "state_centrality": "value*(1-value), using the pre-round behavioral value readout.",
            "pool_centrality": "pool_mean*(1-pool_mean), using the same candidates as spread.",
            "pool_sd_ceiling": (
                "sqrt(pool_mean*(1-pool_mean)); an aggregate Bernoulli SD upper-bound/proxy. "
                "It is not an independently measured mechanism."
            ),
        },
        "headline": headline,
        "correlations": correlations,
        "pooled_ols": pooled,
        "within_run_demeaned_ols": within,
        "first_difference_ols": first_differences,
        "mixed_source_separation": mixed_source,
        "leave_one_run_out": loro_models,
        "per_family": per_family,
        "movement_magnitude_audit": movement,
    }
    with open(OUT, "w") as f:
        json.dump(out, f, indent=2)
        f.write("\n")

    print("wrote", OUT)
    print("mixed pooled R2: state centrality %.3f; pool centrality %.3f; pool ceiling %.3f" % (
        headline["mixed_old_state_centrality_pooled_r2"],
        headline["mixed_pool_centrality_pooled_r2"],
        headline["mixed_pool_sd_ceiling_pooled_r2"],
    ))
    print("state-centrality incremental R2 after pool ceiling (mixed): pooled %.4f; within %.4f; delta %.4f" % (
        headline["mixed_state_centrality_increment_after_ceiling_pooled_r2"],
        headline["mixed_state_centrality_increment_after_ceiling_within_run_r2"],
        headline["mixed_state_centrality_increment_after_ceiling_first_difference_r2"],
    ))


if __name__ == "__main__":
    main()
