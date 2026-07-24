#!/usr/bin/env python3
"""Independent re-derivation of the population-genetics claims from the committed
340-round table in experiments/spread_util_unified.json.

Written from the raw table without reading the prior analysis script. Computes:

  (A) Breeder's equation      OLS of drift R on pull S -> realized heritability h^2
  (B) Factorization           OLS of gap on rho*sigma
  (C) Binomial variance identity on the binary risk axis
  (D) Neutral null            drift under a random / rho~0 selector

Plus diagnostics for the shared-v_t artifact in (A), which the headline
regression does not control for.

Output: experiments/popgen_recheck.json
Run:    uv run python scripts/analysis_popgen_recheck.py
"""

from __future__ import annotations

import json
import math
import random
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "experiments" / "spread_util_unified.json"
OUT = ROOT / "experiments" / "popgen_recheck.json"
PRIOR = ROOT / "experiments" / "population_genetics_unification.json"

RUN_KEY = ("source", "organism", "axis", "cond", "seed")


# ---------------------------------------------------------------- statistics


def mean(xs):
    xs = list(xs)
    return sum(xs) / len(xs) if xs else float("nan")


def var(xs, ddof=0):
    xs = list(xs)
    n = len(xs)
    if n - ddof <= 0:
        return float("nan")
    m = mean(xs)
    return sum((x - m) ** 2 for x in xs) / (n - ddof)


def sd(xs, ddof=0):
    v = var(xs, ddof=ddof)
    return math.sqrt(v) if v == v and v >= 0 else float("nan")


def pearson(xs, ys):
    n = len(xs)
    if n < 3:
        return float("nan")
    mx, my = mean(xs), mean(ys)
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    sxx = sum((x - mx) ** 2 for x in xs)
    syy = sum((y - my) ** 2 for y in ys)
    if sxx <= 0 or syy <= 0:
        return float("nan")
    return sxy / math.sqrt(sxx * syy)


def ols(xs, ys):
    """Simple OLS y = a + b x. Returns dict with slope/intercept/r/n/se_slope."""
    n = len(xs)
    if n < 3:
        return {"n": n, "slope": None, "intercept": None, "r": None, "se_slope": None}
    mx, my = mean(xs), mean(ys)
    sxx = sum((x - mx) ** 2 for x in xs)
    if sxx <= 0:
        return {"n": n, "slope": None, "intercept": None, "r": None, "se_slope": None}
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    b = sxy / sxx
    a = my - b * mx
    resid = [y - (a + b * x) for x, y in zip(xs, ys)]
    dof = n - 2
    se_b = math.sqrt((sum(r * r for r in resid) / dof) / sxx) if dof > 0 else float("nan")
    return {
        "n": n,
        "slope": round(b, 6),
        "intercept": round(a, 6),
        "r": round(pearson(xs, ys), 6),
        "se_slope": round(se_b, 6),
        "rmse": round(math.sqrt(sum(r * r for r in resid) / n), 6),
    }


def ols_through_origin(xs, ys):
    sxx = sum(x * x for x in xs)
    if sxx <= 0:
        return None
    return sum(x * y for x, y in zip(xs, ys)) / sxx


def ols2(x1, x2, ys):
    """Two-predictor OLS y = a + b1*x1 + b2*x2 via normal equations."""
    n = len(ys)
    if n < 4:
        return None
    m1, m2, my = mean(x1), mean(x2), mean(ys)
    a11 = sum((u - m1) ** 2 for u in x1)
    a22 = sum((u - m2) ** 2 for u in x2)
    a12 = sum((u - m1) * (v - m2) for u, v in zip(x1, x2))
    b1v = sum((u - m1) * (y - my) for u, y in zip(x1, ys))
    b2v = sum((v - m2) * (y - my) for v, y in zip(x2, ys))
    det = a11 * a22 - a12 * a12
    if abs(det) < 1e-12:
        return None
    b1 = (a22 * b1v - a12 * b2v) / det
    b2 = (a11 * b2v - a12 * b1v) / det
    a = my - b1 * m1 - b2 * m2
    resid = [y - (a + b1 * u + b2 * v) for u, v, y in zip(x1, x2, ys)]
    return {
        "n": n,
        "intercept": round(a, 6),
        "b_x1": round(b1, 6),
        "b_x2": round(b2, 6),
        "rmse": round(math.sqrt(sum(r * r for r in resid) / n), 6),
    }


def cluster_bootstrap_slope(rows, xf, yf, clusters, n_boot=10000, seed=17):
    """95% CI for an OLS slope, resampling whole runs (clusters) with replacement."""
    rng = random.Random(seed)
    by_cluster = defaultdict(list)
    for r in rows:
        by_cluster[clusters(r)].append(r)
    keys = list(by_cluster)
    slopes = []
    for _ in range(n_boot):
        samp = []
        for _ in range(len(keys)):
            samp.extend(by_cluster[keys[rng.randrange(len(keys))]])
        fit = ols([xf(r) for r in samp], [yf(r) for r in samp])
        if fit["slope"] is not None:
            slopes.append(fit["slope"])
    slopes.sort()
    if len(slopes) < 100:
        return None
    lo = slopes[int(0.025 * len(slopes))]
    hi = slopes[int(0.975 * len(slopes)) - 1]
    return {"lo": round(lo, 6), "hi": round(hi, 6), "n_boot": len(slopes),
            "n_clusters": len(keys)}


def iid_bootstrap_slope(rows, xf, yf, n_boot=10000, seed=17):
    rng = random.Random(seed)
    slopes = []
    n = len(rows)
    for _ in range(n_boot):
        samp = [rows[rng.randrange(n)] for _ in range(n)]
        fit = ols([xf(r) for r in samp], [yf(r) for r in samp])
        if fit["slope"] is not None:
            slopes.append(fit["slope"])
    slopes.sort()
    if len(slopes) < 100:
        return None
    return {"lo": round(slopes[int(0.025 * len(slopes))], 6),
            "hi": round(slopes[int(0.975 * len(slopes)) - 1], 6),
            "n_boot": len(slopes)}


def run_id(r):
    return "|".join(str(r[k]) for k in RUN_KEY)


# ---------------------------------------------------------------- load


def load():
    doc = json.loads(SRC.read_text())
    return doc, doc["records"]


def structural_audit(recs):
    """Verify the derived columns against their stated definitions, and check that
    `drift` really is v_{t+1} - v_t by walking each run's round chain."""
    max_gap_err = max(abs(r["gap"] - (r["kept_mean"] - r["pool_mean"])) for r in recs)
    max_pull_err = max(abs(r["pull"] - (r["kept_mean"] - r["value"])) for r in recs)

    by_run = defaultdict(list)
    for r in recs:
        by_run[run_id(r)].append(r)
    ok = bad = noncontig = 0
    mismatches = []
    for rid, rows in by_run.items():
        rows.sort(key=lambda r: r["round"])
        for a, b in zip(rows, rows[1:]):
            if b["round"] != a["round"] + 1:
                noncontig += 1
                continue
            if abs((b["value"] - a["value"]) - a["drift"]) < 2e-4:
                ok += 1
            else:
                bad += 1
                mismatches.append({"run": rid, "round": a["round"],
                                   "drift_field": a["drift"],
                                   "v_next_minus_v": round(b["value"] - a["value"], 4)})
    return {
        "max_abs_error_gap_vs_kept_minus_pool": round(max_gap_err, 6),
        "max_abs_error_pull_vs_kept_minus_value": round(max_pull_err, 6),
        "note_on_errors": "table stores 4-decimal rounded columns; 1e-4 residuals are rounding",
        "drift_chain_consecutive_pairs_checked": ok + bad,
        "drift_chain_agrees": ok,
        "drift_chain_disagrees": bad,
        "drift_chain_nonconsecutive_skipped": noncontig,
        "drift_chain_mismatches": mismatches,
        "n_runs_by_run_key": len(by_run),
    }


# ---------------------------------------------------------------- (A)


def part_a(recs):
    rows = [r for r in recs if r.get("pull") is not None and r.get("drift") is not None]
    X = lambda r: r["pull"]
    Y = lambda r: r["drift"]

    def fit(sub):
        f = ols([X(r) for r in sub], [Y(r) for r in sub])
        f["slope_through_origin"] = round(
            ols_through_origin([X(r) for r in sub], [Y(r) for r in sub]) or float("nan"), 6)
        f["n_runs"] = len({run_id(r) for r in sub})
        return f

    out = {
        "definition": "R = drift = v_{t+1}-v_t ; S = pull = kept_mean - v_t ; h2 = OLS slope of R on S",
        "pooled": fit(rows),
        "by_axis": {},
        "by_composition": {},
        "by_model_family": {},
        "by_axis_x_composition": {},
    }
    for key, field in (("by_axis", "axis"), ("by_composition", "composition"),
                       ("by_model_family", "organism")):
        for lvl in sorted({r[field] for r in rows}):
            out[key][lvl] = fit([r for r in rows if r[field] == lvl])
    for ax in sorted({r["axis"] for r in rows}):
        for comp in sorted({r["composition"] for r in rows}):
            sub = [r for r in rows if r["axis"] == ax and r["composition"] == comp]
            if sub:
                out["by_axis_x_composition"][f"{ax}/{comp}"] = fit(sub)

    risk = [r for r in rows if r["axis"] == "risk"]
    out["risk_slope_ci95_iid_bootstrap"] = iid_bootstrap_slope(risk, X, Y)
    out["risk_slope_ci95_cluster_bootstrap_by_run"] = cluster_bootstrap_slope(
        risk, X, Y, run_id)

    # ---- shared-v_t diagnostics -------------------------------------------
    # R and S both contain -v_t. Measurement error e in v_t adds +var(e) to
    # cov(R,S) and +var(e) to var(S); correct both by the mean squared
    # measurement SE reported per row.
    diag = {}
    have_se = [r for r in risk if r.get("value_measurement_se") is not None]
    ve = mean(r["value_measurement_se"] ** 2 for r in have_se)
    xs = [X(r) for r in have_se]
    ys = [Y(r) for r in have_se]
    mx, my = mean(xs), mean(ys)
    cov = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / len(xs)
    vx = var(xs)
    diag["risk_mean_v_measurement_error_variance"] = round(ve, 6)
    diag["risk_raw_cov_R_S"] = round(cov, 6)
    diag["risk_raw_var_S"] = round(vx, 6)
    diag["risk_slope_uncorrected"] = round(cov / vx, 6)
    diag["risk_slope_corrected_for_shared_measurement_error"] = (
        round((cov - ve) / (vx - ve), 6) if vx > ve else None)
    diag["risk_share_of_cov_from_measurement_noise"] = round(ve / cov, 6) if cov else None

    # Unconstrained: v_{t+1} = a + b1*kept_mean + b2*v_t.
    # Breeder's model with heritability h2 predicts b1 = h2, b2 = 1 - h2.
    # "the model just becomes its training data" predicts b1 ~ 1, b2 ~ 0.
    unc = ols2([r["kept_mean"] for r in risk], [r["value"] for r in risk],
               [r["value"] + r["drift"] for r in risk])
    diag["risk_unconstrained_v_next_on_kept_and_v"] = unc
    if unc:
        diag["risk_unconstrained_coef_sum"] = round(unc["b_x1"] + unc["b_x2"], 6)

    # Same regression with the shared term removed on the predictor side only:
    # regress drift on gap (kept - pool_mean); pool_mean is a same-round pool
    # statistic rather than the measured v_t, so it does not share v_t with R.
    diag["risk_drift_on_gap"] = ols([r["gap"] for r in risk], [r["drift"] for r in risk])

    # Within-run demeaned version: removes any run-level level effect that could
    # drive a spurious common slope.
    by_run = defaultdict(list)
    for r in risk:
        by_run[run_id(r)].append(r)
    dx, dy = [], []
    for rows_ in by_run.values():
        if len(rows_) < 2:
            continue
        mxr = mean(X(r) for r in rows_)
        myr = mean(Y(r) for r in rows_)
        for r in rows_:
            dx.append(X(r) - mxr)
            dy.append(Y(r) - myr)
    diag["risk_within_run_demeaned"] = ols(dx, dy)

    # Lag-1 autocorrelation of drift within runs. If v_t is measured with noise e,
    # consecutive drifts share -e / +e and the autocorrelation is pushed toward
    # -0.5 (the pure-noise limit). This is the same noise that inflates the
    # drift-on-pull slope, measured independently of the regression.
    by_run_all = defaultdict(list)
    for r in rows:
        by_run_all[run_id(r)].append(r)
    a1, a2 = [], []
    for rows_ in by_run_all.values():
        rows_.sort(key=lambda r: r["round"])
        for u, v in zip(rows_, rows_[1:]):
            if v["round"] == u["round"] + 1:
                a1.append(u["drift"])
                a2.append(v["drift"])
    var_drift = var([r["drift"] for r in rows])
    diag["drift_lag1_autocorrelation_within_run"] = {
        "n_pairs": len(a1),
        "observed_r": round(pearson(a1, a2), 6),
        "var_drift": round(var_drift, 6),
        "expected_r_if_only_measurement_noise_and_no_persistence": (
            round(-ve / var_drift, 6) if var_drift > 0 else None),
        "reading": ("consecutive drifts share the v_t measurement error with opposite "
                    "signs, so noise alone would push this negative; observed value "
                    "near zero means real persistence roughly cancels that, i.e. "
                    "measurement noise is present but not dominant"),
        "pure_measurement_noise_limit": -0.5,
    }

    out["shared_term_diagnostics"] = diag

    # Interior-only slice (drop rows pinned at the 0/1 rails, where drift is
    # mechanically bounded and sigma -> 0).
    interior = [r for r in rows if r["axis"] == "risk" and 0.2 <= r["value"] <= 0.8]
    out["risk_interior_0.2_0.8"] = fit(interior)
    return out


# ---------------------------------------------------------------- (B)


def part_b(recs):
    rows = [r for r in recs if r.get("rho") is not None and r.get("spread") is not None]
    pred = lambda r: r["rho"] * r["spread"]
    fit = ols([pred(r) for r in rows], [r["gap"] for r in rows])
    errs = [r["gap"] - pred(r) for r in rows]
    out = {
        "definition": "OLS of gap (= kept_mean - pool_mean) on rho*sigma",
        "n_records_total": len(recs),
        "n_with_rho": len(rows),
        "n_rho_missing": len(recs) - len(rows),
        "pooled": fit,
        "mae_gap_vs_rho_sigma": round(mean(abs(e) for e in errs), 6),
        "rmse_gap_vs_rho_sigma": round(math.sqrt(mean(e * e for e in errs)), 6),
        "mean_signed_error": round(mean(errs), 6),
        "sd_gap": round(sd([r["gap"] for r in rows]), 6),
        "by_axis": {},
        "by_composition": {},
        "ci95_slope_cluster_bootstrap_by_run": cluster_bootstrap_slope(
            rows, pred, lambda r: r["gap"], run_id),
    }
    for key, field in (("by_axis", "axis"), ("by_composition", "composition")):
        for lvl in sorted({r[field] for r in rows}):
            sub = [r for r in rows if r[field] == lvl]
            f = ols([pred(r) for r in sub], [r["gap"] for r in sub])
            f["mae"] = round(mean(abs(r["gap"] - pred(r)) for r in sub), 6)
            out[key][lvl] = f
    # how much of the fit is carried by the sign structure alone
    out["fraction_rows_sign_agree"] = round(
        mean(1.0 if (r["gap"] == 0 and pred(r) == 0) or (r["gap"] * pred(r) > 0) else 0.0
             for r in rows), 6)
    # degenerate rows where both are ~0 inflate r
    near_zero = [r for r in rows if abs(pred(r)) < 0.01 and abs(r["gap"]) < 0.01]
    out["n_rows_both_near_zero_lt_0.01"] = len(near_zero)
    active = [r for r in rows if abs(pred(r)) >= 0.01]
    fa = ols([pred(r) for r in active], [r["gap"] for r in active])
    fa["mae"] = round(mean(abs(r["gap"] - pred(r)) for r in active), 6) if active else None
    out["active_rows_only_abs_pred_ge_0.01"] = fa

    # --- which rounds can be checked at all? rho requires logged judge scores ---
    missing = [r for r in recs if r.get("rho") is None]
    out["rho_missing_audit"] = {
        "n": len(missing),
        "by_judge": dict(Counter(r["judge"] for r in missing)),
        "by_cond": dict(Counter(r["cond"] for r in missing)),
        "by_format": dict(Counter(r["format"] for r in missing)),
        "by_composition": dict(Counter(r["composition"] for r in missing)),
        "mean_abs_gap_missing": round(mean(abs(r["gap"]) for r in missing), 6),
        "mean_abs_gap_present": round(mean(abs(r["gap"]) for r in rows), 6),
        "note": ("rho is only computable where per-candidate judge scores were logged; "
                 "duel/random formats have no scalar judge score, so the factorization "
                 "is never tested on those rounds"),
    }

    # --- exact replication of the prior run's undocumented filter ---
    sub = [r for r in rows if r["composition"] == "self-only" and r["axis"] == "risk"]
    fp = ols([pred(r) for r in sub], [r["gap"] for r in sub])
    fp["mae"] = round(mean(abs(r["gap"] - pred(r)) for r in sub), 6)
    fp["n_runs"] = len({run_id(r) for r in sub})
    out["prior_filter_replication_selfonly_risk"] = fp
    out["prior_filter_note"] = (
        "the prior run's n=175 is rho-present AND composition=='self-only' AND "
        "axis=='risk' (binary). That filter is not stated in its output JSON.")
    return out


# ---------------------------------------------------------------- (C)


def part_c(recs):
    """On the binary risk axis every candidate score is 0/1, so within-prompt
    population variance is p(1-p). Law of total variance then forces
        V_within + V_between = q(1-q)
    with q the pool mean. This is checked, not discovered."""
    rows = [r for r in recs
            if r.get("binary_score_fraction") == 1.0
            and r.get("mean_item_variance") is not None
            and r.get("between_item_mean_variance") is not None]
    resid = []
    for r in rows:
        q = r["pool_mean"]
        lhs = r["mean_item_variance"]
        rhs = q * (1 - q) - r["between_item_mean_variance"]
        resid.append(lhs - rhs)
    # regression of sigma on sqrt(q(1-q))
    xs = [math.sqrt(max(0.0, r["pool_mean"] * (1 - r["pool_mean"]))) for r in rows]
    ys = [r["spread"] for r in rows]
    out = {
        "definition": "V_within = mean_item_variance ; V_between = between_item_mean_variance ; q = pool_mean",
        "n_binary_rows": len(rows),
        "max_abs_residual": round(max(abs(e) for e in resid), 10),
        "mean_abs_residual": round(mean(abs(e) for e in resid), 10),
        "sigma_on_sqrt_q1mq": ols(xs, ys),
        "caveat": ("q here is the reported pool_mean, itself rounded to 4dp in the "
                   "table; residual is float/rounding noise, not evidence. The "
                   "identity is algebraic (law of total variance on Bernoulli "
                   "within-prompt scores), so it cannot fail."),
    }
    # Cross-check q against the unrounded 'mean' column when present.
    alt = []
    for r in rows:
        q = r.get("mean", r["pool_mean"])
        alt.append(r["mean_item_variance"] - (q * (1 - q) - r["between_item_mean_variance"]))
    out["max_abs_residual_using_unrounded_mean_column"] = round(max(abs(e) for e in alt), 12)
    # also verify hierarchical_total_variance == q(1-q)
    ht = [abs(r["hierarchical_total_variance"] - r["mean"] * (1 - r["mean"])) for r in rows]
    out["max_abs_error_hierarchical_total_variance_vs_q1mq"] = round(max(ht), 12)
    return out


# ---------------------------------------------------------------- (D)


def part_d(recs):
    def block(rows, label):
        d = [r["drift"] for r in rows]
        if not d:
            return {"label": label, "n": 0}
        se = mean(r["value_measurement_se"] for r in rows if r.get("value_measurement_se"))
        se_next = mean(r["next_value_measurement_se"] for r in rows
                       if r.get("next_value_measurement_se"))
        s = sd(d, ddof=1) if len(d) > 1 else float("nan")
        return {
            "label": label,
            "n": len(d),
            "mean_drift": round(mean(d), 6),
            "sd_drift": round(s, 6),
            "se_of_mean_drift": round(s / math.sqrt(len(d)), 6),
            "t_stat": round(mean(d) / (s / math.sqrt(len(d))), 4) if s == s and s > 0 else None,
            "min_drift": min(d),
            "max_drift": max(d),
            "mean_abs_drift": round(mean(abs(x) for x in d), 6),
            "mean_rho": (round(mean(r["rho"] for r in rows if r["rho"] is not None), 6)
                         if any(r["rho"] is not None for r in rows) else None),
            "n_rho_missing": sum(1 for r in rows if r["rho"] is None),
            "mean_gap": round(mean(r["gap"] for r in rows), 6),
            "mean_pull": round(mean(r["pull"] for r in rows), 6),
            "expected_sd_from_measurement_noise_alone": (
                round(math.sqrt(se ** 2 + se_next ** 2), 6)
                if se == se and se_next == se_next else None),
            "conds": dict(Counter(r["cond"] for r in rows)),
        }

    rnd = [r for r in recs if r["judge"] == "random"]
    # run-level view: 16 rows are only 4 trajectories x 4 rounds
    by_run = defaultdict(list)
    for r in rnd:
        by_run[run_id(r)].append(r)
    nets = [sum(x["drift"] for x in v) for v in by_run.values()]
    run_level = {
        "n_independent_runs": len(by_run),
        "organisms": dict(Counter(r["organism"] for r in rnd)),
        "sources": dict(Counter(r["source"] for r in rnd)),
        "per_run_net_drift": [round(x, 4) for x in nets],
        "mean_net_drift": round(mean(nets), 6),
        "sd_net_drift": round(sd(nets, ddof=1), 6),
        "per_round_mean_drift_run_clustered_se": (
            round(sd(nets, ddof=1) / math.sqrt(len(nets)) / 4, 6) if len(nets) > 1 else None),
        "mean_value_measurement_n": round(mean(r["value_measurement_n"] for r in rnd), 2),
    }

    rho0 = [r for r in recs if r.get("rho") is not None and abs(r["rho"]) < 0.05]
    rho0_nonrandom = [r for r in rho0 if r["judge"] != "random"]
    out = {
        "definition": "neutral = selector carries no value information (judge=='random' or |rho|<0.05)",
        "random_judge": block(rnd, "judge == 'random'"),
        "random_judge_run_level": run_level,
        "rho_near_zero_abs_lt_0.05": block(rho0, "|rho| < 0.05"),
        "rho_near_zero_excluding_random_judge": block(rho0_nonrandom, "|rho|<0.05, judge != random"),
        "all_rows_for_contrast": block(recs, "all 340 rows"),
    }
    # informative selector contrast
    inf = [r for r in recs if r.get("rho") is not None and abs(r["rho"]) >= 0.3]
    out["informative_selector_abs_rho_ge_0.3"] = block(inf, "|rho| >= 0.3")
    return out


# ---------------------------------------------------------------- compare


def compare_prior(mine):
    """Field-by-field check against the un-traced prior output. Read only AFTER
    the independent computation above is complete."""
    if not PRIOR.exists():
        return {"status": "prior file missing"}
    p = json.loads(PRIOR.read_text())
    rows = []

    def cmp(label, mine_v, prior_v, tol=1e-4):
        agree = (mine_v is not None and prior_v is not None
                 and abs(mine_v - prior_v) <= tol)
        rows.append({"quantity": label,
                     "mine": None if mine_v is None else round(mine_v, 6),
                     "prior": None if prior_v is None else round(prior_v, 6),
                     "agrees": bool(agree),
                     "abs_diff": (None if mine_v is None or prior_v is None
                                  else round(abs(mine_v - prior_v), 8))})

    A, pa = mine["A_breeders_equation"], p["A_breeders_equation"]["by_slice"]
    pairs = [("pooled", A["pooled"], pa["pooled"]),
             ("risk", A["by_axis"]["risk"], pa["risk_axis"]),
             ("selfreport", A["by_axis"]["selfreport"], pa["selfreport_axis"]),
             ("self-only", A["by_composition"]["self-only"], pa["self_only"]),
             ("base-mixed", A["by_composition"]["base-mixed"], pa["base_mixed"]),
             ("peer-mixed", A["by_composition"]["peer-mixed"], pa["peer_mixed"]),
             ("qwen", A["by_model_family"]["Qwen"], pa["qwen"]),
             ("olmo", A["by_model_family"]["OLMo"], pa["olmo"]),
             ("risk_interior", A["risk_interior_0.2_0.8"], pa["risk_interior_0.2_0.8"])]
    for name, m, q in pairs:
        cmp(f"A ols_slope [{name}]", m["slope"], q["ols_slope"])
        cmp(f"A intercept [{name}]", m["intercept"], q["ols_intercept"])
        cmp(f"A r [{name}]", m["r"], q["r"])
        cmp(f"A n [{name}]", float(m["n"]), float(q["n"]), tol=0)
        cmp(f"A through-origin h2 [{name}]", m["slope_through_origin"],
            q["h2_through_origin"])

    B, pb = mine["B_factorization"], p["B_selection_differential"]
    cmp("B slope (mine=all 290 rows / prior=self-only risk 175)",
        B["pooled"]["slope"], pb["gap_on_rho_sigma"]["slope"])
    cmp("B r (mine=all 290 / prior=175)", B["pooled"]["r"], pb["gap_on_rho_sigma"]["r"])
    cmp("B n (mine=all / prior)", float(B["pooled"]["n"]),
        float(pb["gap_on_rho_sigma"]["n"]), tol=0)
    cmp("B MAE (mine=all / prior=175)", B["mae_gap_vs_rho_sigma"], pb["gap_vs_rho_sigma_mae"])
    fr = B["prior_filter_replication_selfonly_risk"]
    cmp("B slope on prior's own filter", fr["slope"], pb["gap_on_rho_sigma"]["slope"])
    cmp("B r on prior's own filter", fr["r"], pb["gap_on_rho_sigma"]["r"])
    cmp("B n on prior's own filter", float(fr["n"]), float(pb["gap_on_rho_sigma"]["n"]), tol=0)
    cmp("B MAE on prior's own filter", fr["mae"], pb["gap_vs_rho_sigma_mae"])

    C, pc = mine["C_binomial_variance_identity"], p["C_binomial_variance"]
    cmp("C max abs residual (unrounded q)", C["max_abs_residual_using_unrounded_mean_column"],
        pc["identity_V_within_eq_qq_minus_Vbetween"]["max_abs_residual"], tol=1e-5)
    cmp("C sigma~sqrt(q(1-q)) slope", C["sigma_on_sqrt_q1mq"]["slope"],
        pc["spread_on_sqrt_qq"]["slope"], tol=1e-3)
    cmp("C sigma~sqrt(q(1-q)) r", C["sigma_on_sqrt_q1mq"]["r"], pc["spread_on_sqrt_qq"]["r"],
        tol=1e-3)
    cmp("C n", float(C["n_binary_rows"]), float(pc["spread_on_sqrt_qq"]["n"]), tol=0)

    D, pd = mine["D_neutral_null"], p["D_neutral_null_and_fixation"]
    cmp("D n (random arms)", float(D["random_judge"]["n"]),
        float(pd["neutral_null_random_arms"]["n"]), tol=0)
    cmp("D mean drift (random arms)", D["random_judge"]["mean_drift"],
        pd["neutral_null_random_arms"]["mean_drift"])
    cmp("D sd drift ddof=1 (mine) vs prior", D["random_judge"]["sd_drift"],
        pd["neutral_null_random_arms"]["sd_drift"], tol=1e-4)
    cmp("D sd drift ddof=0 (mine) vs prior",
        D["random_judge"]["sd_drift"] * math.sqrt(15 / 16),
        pd["neutral_null_random_arms"]["sd_drift"], tol=1e-4)
    cmp("D directed |rho|>=0.3 mean drift", D["informative_selector_abs_rho_ge_0.3"]["mean_drift"],
        pd["directed_arms_abs_rho_ge_0.3"]["mean_drift"])
    cmp("D directed |rho|>=0.3 n", float(D["informative_selector_abs_rho_ge_0.3"]["n"]),
        float(pd["directed_arms_abs_rho_ge_0.3"]["n"]), tol=0)

    return {
        "n_checks": len(rows),
        "n_disagree": sum(1 for r in rows if not r["agrees"]),
        "disagreements": [r for r in rows if not r["agrees"]],
        "all_checks": rows,
    }


def main():
    doc, recs = load()
    result = {
        "description": "Independent re-derivation of breeder's-equation / factorization / "
                       "binomial-identity / neutral-null claims from spread_util_unified.json",
        "source_file": str(SRC.relative_to(ROOT)),
        "n_records": len(recs),
        "n_runs_declared": doc.get("n_runs"),
        "structural_audit": structural_audit(recs),
        "A_breeders_equation": part_a(recs),
        "B_factorization": part_b(recs),
        "C_binomial_variance_identity": part_c(recs),
        "D_neutral_null": part_d(recs),
    }
    result["prior_comparison"] = compare_prior(result)
    OUT.write_text(json.dumps(result, indent=2))
    print(f"wrote {OUT}")

    a = result["A_breeders_equation"]
    print("\n(A) drift ~ pull")
    print("  pooled       ", a["pooled"])
    for k, v in a["by_axis"].items():
        print(f"  axis {k:<12}", v)
    for k, v in a["by_composition"].items():
        print(f"  comp {k:<12}", v)
    for k, v in a["by_model_family"].items():
        print(f"  model {k:<11}", v)
    print("  risk CI (iid)    ", a["risk_slope_ci95_iid_bootstrap"])
    print("  risk CI (cluster)", a["risk_slope_ci95_cluster_bootstrap_by_run"])
    print("  diagnostics      ")
    for k, v in a["shared_term_diagnostics"].items():
        print(f"    {k}: {v}")

    b = result["B_factorization"]
    print("\n(B) gap ~ rho*sigma")
    print("  pooled", b["pooled"], "MAE", b["mae_gap_vs_rho_sigma"], "n_rho_missing", b["n_rho_missing"])
    for k, v in b["by_axis"].items():
        print(f"  axis {k:<12}", v)
    print("  active only", b["active_rows_only_abs_pred_ge_0.01"])
    print("  prior-filter replication", b["prior_filter_replication_selfonly_risk"])
    print("  rho missing audit", b["rho_missing_audit"])

    print("\n(C) binomial identity")
    for k, v in result["C_binomial_variance_identity"].items():
        print(f"  {k}: {v}")

    print("\n(D) neutral null")
    for k, v in result["D_neutral_null"].items():
        print(f"  {k}: {v}")

    pc = result["prior_comparison"]
    print(f"\n=== PRIOR COMPARISON: {pc['n_disagree']}/{pc['n_checks']} disagree ===")
    for row in pc["disagreements"]:
        print(f"  DISAGREE {row['quantity']}: mine={row['mine']} prior={row['prior']} "
              f"diff={row['abs_diff']}")


if __name__ == "__main__":
    main()
