"""Why does the response-per-unit-selection decline over a run?

The per-round regression of value movement on the selection gap gets weaker as a
run proceeds. Four explanations make different predictions, and this script
separates them on the committed 340-round corpus
(experiments/spread_util_unified.json):

  HEADROOM      The response is proportional to how much scale is left in the
                direction being pushed. A run near a rail cannot move, so the
                coefficient falls as runs approach their endpoints. This is what
                a replicator/logistic model predicts, and it implies nothing
                special happens from repeating selection.

  WEAR          Accumulated selection pressure itself degrades the response,
                wherever the value sits — the overoptimisation shape Gao,
                Schulman & Hilton (arXiv 2210.10760) fit for best-of-n. This
                says repeated selection genuinely wears the model out.

  SURVIVORSHIP  Nothing declines within a run; later rounds are a biased
                subsample, because fast movers hit rails or abort and the runs
                still present at round 4 were always the sluggish ones. This
                artefact has already bitten the project once: in the
                spread-intervention corpus, aborted runs moved +0.074/round
                against +0.023 for completed ones.

  WITHIN-ROUND  Nothing declines across rounds either; the response is simply
  CONCAVITY     concave in the size of a single round's gap. Because cumulative
                pressure is built out of past gaps, a gap x pressure term will
                absorb plain within-round concavity if that term is not fitted
                alongside it. This is the confound that makes a naive wear
                estimate untrustworthy, so gap x |gap| is always in the model.

Two specification points that the first pass of this analysis got wrong, kept
here so they are not reintroduced:

  1. The movement law is drift ~ PULL, not drift ~ gap. Pull decomposes as
     (pool_mean - v) + gap: a supply term, because the candidate pool need not
     be centred on the organism's current measured value, plus the selection
     term. Regressing drift on gap alone omits the supply term and the omitted
     variable is correlated with the gap. Every model here carries the supply
     term as its own regressor, so the gap coefficient is the response to
     SELECTION specifically.

  2. "Survivors" must mean runs that complete the standard four-round horizon.
     A handful of runs in this corpus go to round 8; conditioning on those
     selects an experiment, not a survival pattern.

Two objections this corpus does not have, worth stating because they are the
usual ones:
  - Attenuation from a noisy regressor. The gap is computed from candidate
    scores observed exactly given the pool; it is not a noisy proxy.
  - Shared measurement noise between regressor and outcome. The value v is read
    on held-out prompts; the gap comes from training-prompt candidates. Noise in
    v_t enters the outcome but not the regressor, so it inflates standard errors
    without biasing the slope.

Identification is reported BEFORE the fits, because round index, cumulative
pressure and rail-closeness are collinear by construction. If they are collinear
enough in this corpus, "the data cannot tell these apart" is the honest output.

Writes experiments/response_saturation.json.
"""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
UNIFIED = ROOT / "experiments/spread_util_unified.json"
OUT = ROOT / "experiments/response_saturation.json"

BOOTSTRAP_DRAWS = 2000
BOOTSTRAP_SEED = 20260728
MIDSCALE_HEADROOM = 0.35   # at least 35% of the 0-1 scale left in the push direction
STANDARD_HORIZON = 4       # the horizon nearly every condition was run to

# Every column the models draw on. Built once; models pick columns by name.
COLUMNS = [
    "const",         # intercept
    "supply",        # pool_mean - v : the pool is not centred on the organism
    "gap",           # kept_mean - pool_mean : the selection differential
    "gap_absgap",    # within-round concavity
    "gap_round",     # response decays with round index (descriptive)
    "gap_pressure",  # response decays with cumulative selection so far (wear)
    "gap_rail",      # response decays as the push direction runs out of scale
]

MODELS = {
    "M0_linear":        ["const", "supply", "gap"],
    "M1_concavity":     ["const", "supply", "gap", "gap_absgap"],
    "M2_round":         ["const", "supply", "gap", "gap_absgap", "gap_round"],
    "M3_wear":          ["const", "supply", "gap", "gap_absgap", "gap_pressure"],
    "M4_headroom":      ["const", "supply", "gap", "gap_absgap", "gap_rail"],
    "M5_wear_headroom": ["const", "supply", "gap", "gap_absgap", "gap_pressure",
                         "gap_rail"],
}

PRETTY = {
    "const": "intercept",
    "supply": "pool offset (pool_mean - v)",
    "gap": "gap",
    "gap_absgap": "gap x |gap|",
    "gap_round": "gap x (round-1)",
    "gap_pressure": "gap x cumulative |gap|",
    "gap_rail": "gap x rail-closeness",
}


# --------------------------------------------------------------------------- #
# corpus


def run_key(rec):
    return rec["cond"], rec["seed"], rec["source"]


def build_rows():
    unified = json.loads(UNIFIED.read_text())
    runs = defaultdict(list)
    for rec in unified["records"]:
        if rec.get("gap") is None or rec.get("drift") is None:
            continue
        runs[run_key(rec)].append(rec)
    for rows in runs.values():
        rows.sort(key=lambda r: r["round"])

    rows = []
    for key, run_rows in runs.items():
        cumulative = 0.0
        last_round = run_rows[-1]["round"]
        for rec in run_rows:
            gap = float(rec["gap"])
            value = float(rec["value"])
            headroom = (1.0 - value) if gap >= 0 else value
            rows.append({
                "run": key,
                "round": int(rec["round"]),
                "gap": gap,
                "drift": float(rec["drift"]),
                "value": value,
                "supply": float(rec["pool_mean"]) - value,
                "spread": float(rec["spread"]),
                "organism": rec["organism"],
                "axis": rec["axis"],
                "composition": rec["composition"],
                "judge": rec["judge"],
                "pressure": cumulative,
                "headroom": headroom,
                "rail": 1.0 - 2.0 * headroom,
                "meas_se": rec.get("next_value_measurement_se"),
                "value_se": rec.get("value_measurement_se"),
                "last_round": int(last_round),
            })
            cumulative += abs(gap)
    return unified, runs, rows


def design_matrix(rows):
    g = np.array([r["gap"] for r in rows])
    return np.column_stack([
        np.ones(len(rows)),
        np.array([r["supply"] for r in rows]),
        g,
        g * np.abs(g),
        g * np.array([r["round"] - 1 for r in rows], dtype=float),
        g * np.array([r["pressure"] for r in rows]),
        g * np.array([r["rail"] for r in rows]),
    ])


# --------------------------------------------------------------------------- #
# estimation


def ols(X, y):
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    return beta


def fit(X, y, cols):
    idx = [COLUMNS.index(c) for c in cols]
    beta = ols(X[:, idx], y)
    resid = y - X[:, idx] @ beta
    return beta, resid


def cluster_bootstrap_models(X, y, run_ids, panels, draws=BOOTSTRAP_DRAWS,
                             seed=BOOTSTRAP_SEED):
    """One resampling loop, every model refitted on each draw."""
    # run_ids are tuples, so build the index map in plain Python: numpy would
    # turn the list of tuples into a 2-D array and flatnonzero would then return
    # indices into the flattened array rather than into the rows.
    index_of = defaultdict(list)
    for i, k in enumerate(run_ids):
        index_of[k].append(i)
    uniq = sorted(index_of)
    index_of = {k: np.array(v, dtype=int) for k, v in index_of.items()}
    rng = np.random.default_rng(seed)
    samples = {name: defaultdict(list) for name in panels}
    for _ in range(draws):
        picked = rng.integers(0, len(uniq), size=len(uniq))
        take = np.concatenate([index_of[uniq[i]] for i in picked])
        Xb, yb = X[take], y[take]
        for name, cols in panels.items():
            idx = [COLUMNS.index(c) for c in cols]
            if Xb.shape[0] <= len(idx) + 1:
                continue
            try:
                beta = ols(Xb[:, idx], yb)
            except np.linalg.LinAlgError:
                continue
            for c, b in zip(cols, beta):
                samples[name][c].append(float(b))
    out = {}
    for name, per_col in samples.items():
        out[name] = {}
        for c, vals in per_col.items():
            arr = np.array(vals)
            out[name][c] = {
                "se": float(arr.std(ddof=1)),
                "ci_lo": float(np.percentile(arr, 2.5)),
                "ci_hi": float(np.percentile(arr, 97.5)),
            }
    return out


def loo_run_cv(X, y, run_ids, cols):
    idx = [COLUMNS.index(c) for c in cols]
    codes = {k: i for i, k in enumerate(dict.fromkeys(run_ids))}
    run_ids = np.array([codes[k] for k in run_ids], dtype=int)
    errors = []
    for held in sorted(set(run_ids.tolist())):
        mask = run_ids != held
        if mask.sum() <= len(idx) + 1:
            continue
        beta = ols(X[mask][:, idx], y[mask])
        pred = X[~mask][:, idx] @ beta
        errors.extend(np.abs(y[~mask] - pred).tolist())
    return float(np.mean(errors)), len(errors)


def analyse_panel(rows, label):
    X = design_matrix(rows)
    y = np.array([r["drift"] for r in rows])
    run_ids = [r["run"] for r in rows]
    boot = cluster_bootstrap_models(X, y, run_ids, MODELS)
    block = {"_panel": label, "_n": len(rows), "_n_runs": len(set(run_ids))}
    for name, cols in MODELS.items():
        beta, resid = fit(X, y, cols)
        cv_mae, n_pred = loo_run_cv(X, y, run_ids, cols)
        block[name] = {
            "coefficients": {PRETTY[c]: float(b) for c, b in zip(cols, beta)},
            "ci": {PRETTY[c]: boot[name].get(c) for c in cols},
            "in_sample_mae": float(np.mean(np.abs(resid))),
            "cv_mae": cv_mae,
            "n_predictions": n_pred,
        }
    return block


def within_run_wear(rows):
    """Is the wear term identified WITHIN runs, or only across them?

    Demeans gap, drift, supply and the interactions by run, so only variation
    across rounds of the SAME run identifies the coefficients. If wear survives
    demeaning it is a within-run decline; if it vanishes, the apparent decline
    was a comparison between different runs.
    """
    counts = defaultdict(int)
    for r in rows:
        counts[r["run"]] += 1
    keep = [r for r in rows if counts[r["run"]] >= 3]
    if len(keep) < 30:
        return None
    X = design_matrix(keep)
    y = np.array([r["drift"] for r in keep])
    codes = {k: i for i, k in enumerate(dict.fromkeys(r["run"] for r in keep))}
    run_ids = np.array([codes[r["run"]] for r in keep], dtype=int)
    Xd, yd = X.copy(), y.copy()
    for run in sorted(set(run_ids.tolist())):
        m = run_ids == run
        Xd[m] = X[m] - X[m].mean(axis=0)
        yd[m] = y[m] - y[m].mean()
    Xd[:, 0] = 0.0  # intercept is absorbed by the demeaning
    out = {"n": len(keep), "n_runs": len(codes)}
    for name in ("M3_wear", "M5_wear_headroom"):
        cols = [c for c in MODELS[name] if c != "const"]
        idx = [COLUMNS.index(c) for c in cols]
        beta = ols(Xd[:, idx], yd)
        out[name] = {PRETTY[c]: float(b) for c, b in zip(cols, beta)}
    boot = cluster_bootstrap_models(
        Xd, yd, run_ids.tolist(),
        {n: [c for c in MODELS[n] if c != "const"]
         for n in ("M3_wear", "M5_wear_headroom")},
    )
    for name in ("M3_wear", "M5_wear_headroom"):
        out[name + "_ci"] = {PRETTY[c]: v for c, v in boot[name].items()}
    return out


def eiv_corrected(rows):
    """Correct the one place where regressor and outcome share measurement noise.

    The gap is clean, but the pool-offset term is not: supply = pool_mean - v_t
    and drift = v_{t+1} - v_t both carry the SAME measurement error in v_t, with
    the same sign. Writing e for that error,

        cov(supply_obs, drift_obs) = cov(supply*, drift*) + var(e)
        var(supply_obs)            = var(supply*)        + var(e)

    so ordinary least squares pulls the supply coefficient toward 1 (and drags
    the gap coefficient with it, in proportion to how correlated the two
    regressors are). Subtracting var(e) from the relevant entries of the moment
    matrices removes it. var(e) comes from each round's own recorded
    value_measurement_se, not from an assumption.

    This matters for the headline: an uncorrected supply coefficient near 1 is
    partly an artefact, and the corrected gap coefficient is the number to
    compare against the instrumental-variables estimate from the
    spread-intervention corpus.
    """
    usable = [r for r in rows if r.get("value_se") is not None]
    if len(usable) < 30:
        return None
    supply = np.array([r["supply"] for r in usable])
    gap = np.array([r["gap"] for r in usable])
    drift = np.array([r["drift"] for r in usable])
    var_e = float(np.mean([r["value_se"] ** 2 for r in usable]))

    X = np.column_stack([np.ones(len(usable)), supply, gap])
    XtX = X.T @ X / len(usable)
    Xty = X.T @ drift / len(usable)
    naive = np.linalg.solve(XtX, Xty)

    XtX_c = XtX.copy()
    XtX_c[1, 1] -= var_e          # var(supply) is inflated by var(e)
    Xty_c = Xty.copy()
    Xty_c[1] -= var_e             # cov(supply, drift) is inflated by var(e)
    corrected = np.linalg.solve(XtX_c, Xty_c)

    return {
        "n": len(usable),
        "mean_value_measurement_variance": var_e,
        "var_supply_observed": float(np.var(supply)),
        "noise_share_of_supply_variance": float(var_e / np.var(supply)),
        "naive": {"intercept": float(naive[0]), "supply": float(naive[1]),
                  "gap": float(naive[2])},
        "corrected": {"intercept": float(corrected[0]),
                      "supply": float(corrected[1]),
                      "gap": float(corrected[2])},
    }


def by_round_slopes(rows, max_round):
    """Per-round slope of drift on gap, controlling the pool offset."""
    out = {}
    for r in range(1, max_round + 1):
        sub = [x for x in rows if x["round"] == r]
        if len(sub) < 5:
            out[f"round{r}"] = None
            continue
        X = design_matrix(sub)
        y = np.array([x["drift"] for x in sub])
        idx = [COLUMNS.index(c) for c in ("const", "supply", "gap")]
        if np.var(X[:, COLUMNS.index("gap")]) < 1e-12:
            out[f"round{r}"] = None
            continue
        beta = ols(X[:, idx], y)
        out[f"round{r}"] = float(beta[2])
    return out


def corr(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    if np.var(a) < 1e-12 or np.var(b) < 1e-12:
        return None
    return float(np.corrcoef(a, b)[0, 1])


# --------------------------------------------------------------------------- #


def main():
    unified, runs, rows = build_rows()
    max_round = max(r["round"] for r in rows)
    moved = [r for r in rows if abs(r["gap"]) > 1e-9]

    identification = {
        "n_records": len(rows),
        "n_runs": len(runs),
        "max_round": int(max_round),
        "records_with_nonzero_gap": len(moved),
        "collinearity": {
            "round_vs_cumulative_pressure": corr([r["round"] for r in moved],
                                                 [r["pressure"] for r in moved]),
            "round_vs_rail_closeness": corr([r["round"] for r in moved],
                                            [r["rail"] for r in moved]),
            "cumulative_pressure_vs_rail": corr([r["pressure"] for r in moved],
                                                [r["rail"] for r in moved]),
            "gap_absgap_vs_gap_pressure": corr(
                [r["gap"] * abs(r["gap"]) for r in moved],
                [r["gap"] * r["pressure"] for r in moved]),
            "supply_vs_gap": corr([r["supply"] for r in moved],
                                  [r["gap"] for r in moved]),
        },
        "run_length_histogram": {
            str(n): sum(1 for rr in runs.values() if len(rr) == n)
            for n in sorted({len(rr) for rr in runs.values()})
        },
    }

    per_round_shape = {}
    for r in range(1, max_round + 1):
        sub = [x for x in rows if x["round"] == r]
        if not sub:
            continue
        ses = [x["meas_se"] for x in sub if x["meas_se"] is not None]
        per_round_shape[f"round{r}"] = {
            "n": len(sub),
            "n_runs": len({x["run"] for x in sub}),
            "var_gap": float(np.var([x["gap"] for x in sub])),
            "mean_abs_gap": float(np.mean([abs(x["gap"]) for x in sub])),
            "mean_abs_drift": float(np.mean([abs(x["drift"]) for x in sub])),
            "mean_headroom": float(np.mean([x["headroom"] for x in sub])),
            "mean_measurement_se": float(np.mean(ses)) if ses else None,
        }

    # ---- survivorship: runs that reach the standard horizon ----
    completers = {k for k, rr in runs.items() if rr[-1]["round"] >= STANDARD_HORIZON}
    short = {k for k in runs if k not in completers}
    balanced = [r for r in rows if r["run"] in completers]

    all_by_round = by_round_slopes(rows, STANDARD_HORIZON)
    bal_by_round = by_round_slopes(balanced, STANDARD_HORIZON)
    r1_short = [r for r in rows if r["round"] == 1 and r["run"] in short]
    r1_comp = [r for r in rows if r["round"] == 1 and r["run"] in completers]

    def round1_slope(sub):
        if len(sub) < 5:
            return None
        X = design_matrix(sub)
        y = np.array([x["drift"] for x in sub])
        idx = [COLUMNS.index(c) for c in ("const", "supply", "gap")]
        return float(ols(X[:, idx], y)[2])

    midscale = [r for r in rows if r["headroom"] >= MIDSCALE_HEADROOM]

    panels = {
        "all": analyse_panel(rows, "all rounds, all runs"),
        "balanced": analyse_panel(
            balanced, f"runs reaching round {STANDARD_HORIZON}"),
        "midscale": analyse_panel(
            midscale, f"rounds with headroom >= {MIDSCALE_HEADROOM}"),
    }
    within = within_run_wear(rows)

    result = {
        "description": (
            "Separates four explanations for the declining response-per-unit-gap "
            "over a run: headroom (rail proximity), wear (cumulative selection "
            "pressure), survivorship (later rounds are a biased subsample), and "
            "plain within-round concavity in the gap. Every model carries the "
            "pool-offset term, because the movement law is drift ~ pull = "
            "(pool_mean - v) + gap, not drift ~ gap."
        ),
        "corpus": {
            "file": "experiments/spread_util_unified.json",
            "n_records_in_file": unified["n_records"],
            "n_runs_in_file": unified["n_runs"],
        },
        "identification": identification,
        "per_round_shape": per_round_shape,
        "survivorship": {
            "n_runs_reaching_standard_horizon": len(completers),
            "n_runs_stopping_short": len(short),
            "by_round_slope_all_runs": all_by_round,
            "by_round_slope_completers_only": bal_by_round,
            "round1_slope_short_runs": round1_slope(r1_short),
            "round1_slope_completers": round1_slope(r1_comp),
            "n_round1_short": len(r1_short),
            "n_round1_completers": len(r1_comp),
        },
        "panels": panels,
        "measurement_error_correction": {
            "all": eiv_corrected(rows),
            "balanced": eiv_corrected(balanced),
        },
        "within_run_wear": within,
        "settings": {
            "bootstrap_draws": BOOTSTRAP_DRAWS,
            "bootstrap_seed": BOOTSTRAP_SEED,
            "midscale_headroom": MIDSCALE_HEADROOM,
            "standard_horizon": STANDARD_HORIZON,
            "clustering": "whole runs, keyed by (cond, seed, source)",
        },
    }
    OUT.write_text(json.dumps(result, indent=2) + "\n")

    # ---- console ----
    print("IDENTIFICATION (before any fit)")
    print(f"  {len(rows)} rounds from {len(runs)} runs; max round {max_round}")
    for k, v in identification["collinearity"].items():
        print(f"  corr {k:34s} {v: .3f}" if v is not None else f"  corr {k}: n/a")
    print(f"  run lengths: {identification['run_length_histogram']}")
    print()
    print("PER-ROUND SHAPE")
    for k, v in per_round_shape.items():
        print(f"  {k}: n={v['n']:3d} runs={v['n_runs']:3d} var(gap)={v['var_gap']:.4f} "
              f"mean|gap|={v['mean_abs_gap']:.4f} mean|drift|={v['mean_abs_drift']:.4f} "
              f"headroom={v['mean_headroom']:.3f}")
    print()
    print("SURVIVORSHIP")
    print(f"  {len(completers)} runs reach round {STANDARD_HORIZON}; "
          f"{len(short)} stop short")
    fmt = lambda d: "  ".join(f"{k}={v:.3f}" if v is not None else f"{k}=n/a"
                              for k, v in d.items())
    print(f"  all runs        by-round gap slope: {fmt(all_by_round)}")
    print(f"  completers only by-round gap slope: {fmt(bal_by_round)}")
    print(f"  round-1 slope: short runs "
          f"{round1_slope(r1_short)} (n={len(r1_short)}) vs completers "
          f"{round1_slope(r1_comp)} (n={len(r1_comp)})")
    print()
    print("MODELS (coefficient [95% run-clustered CI], leave-one-run-out CV MAE)")
    for label, block in panels.items():
        print(f"  -- {label} (n={block['_n']}, runs={block['_n_runs']}) --")
        for name in MODELS:
            f = block[name]
            bits = []
            for term, coef in f["coefficients"].items():
                ci = f["ci"].get(term)
                bits.append(f"{term}={coef:.3f} [{ci['ci_lo']:.2f},{ci['ci_hi']:.2f}]"
                            if ci else f"{term}={coef:.3f}")
            print(f"     {name:18s} cvMAE={f['cv_mae']:.4f}  " + "; ".join(bits))
    print()
    for label, sample in (("all", rows), ("completers", balanced)):
        ev = eiv_corrected(sample)
        if ev:
            print(f"MEASUREMENT-ERROR CORRECTION ({label}, n={ev['n']}; "
                  f"noise is {ev['noise_share_of_supply_variance']:.1%} of "
                  f"supply variance)")
            print(f"  naive      supply={ev['naive']['supply']:.3f} "
                  f"gap={ev['naive']['gap']:.3f}")
            print(f"  corrected  supply={ev['corrected']['supply']:.3f} "
                  f"gap={ev['corrected']['gap']:.3f}")
    print()
    if within:
        print(f"WITHIN-RUN (run fixed effects; n={within['n']}, "
              f"runs={within['n_runs']})")
        for name in ("M3_wear", "M5_wear_headroom"):
            bits = []
            for term, coef in within[name].items():
                ci = within[name + "_ci"].get(term)
                bits.append(f"{term}={coef:.3f} [{ci['ci_lo']:.2f},{ci['ci_hi']:.2f}]"
                            if ci else f"{term}={coef:.3f}")
            print(f"  {name:18s} " + "; ".join(bits))
    print()
    print(f"wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
