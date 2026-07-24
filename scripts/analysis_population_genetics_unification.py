"""Population-genetics unification of the selection-loop value dynamics.

The program's empirical spine (report_spread_util_unified.md,
report_spread_conversion_model.md) already contains, un-named, every piece of a
classical quantitative-/population-genetics account of a selection loop. This
script re-reads the committed 340-round table
(experiments/spread_util_unified.json) and states the correspondence
QUANTITATIVELY, testing each mapping as a fit rather than asserting the analogy.

The three mappings, each a testable claim on committed data:

  (A) BREEDER'S EQUATION.  Response R = h^2 . S, with
        R = drift            = v_{t+1} - v_t         (change in the trait mean)
        S = pull             = kept_mean - v_t       (selection differential:
                                                      selected-parent mean minus
                                                      current population mean, on
                                                      the SAME trait)
      h^2 (the realized heritability / per-round transmission) is the OLS slope
      of R on S.  We report it per family x composition x axis and test whether
      it is a stable constant (the project's already-quoted ~0.83 pull gain).

  (B) SELECTION DIFFERENTIAL FACTORIZES AS rho . sigma.  In self-only pools the
      pool mean ~= the trait mean, so S = pull ~= gap = kept_mean - pool_mean,
      and gap ~= rho . sigma (the Price selection differential = phenotypic SD x
      the judge's value-agreement selection intensity).  Composed with (A) this
      gives the full closed form   E[R] = h^2 . rho . sigma.

  (C) PHENOTYPIC VARIANCE IS BINOMIAL (WRIGHT-FISHER FORM).  On the binary risk
      axis the candidate value is 0/1, so the total offered variance is exactly
      q(1-q) (q = pool mean), split by the law of total variance into
      within-prompt variance and between-prompt variance:
        V_within = q(1-q) - V_between .
      sigma (reported spread, ~ sqrt of within-prompt variance) is therefore
      structurally tied to sqrt(q(1-q)) and MUST collapse as q -> 0 or 1.

  (D) NEUTRAL NULL + FIXATION BOUNDARY.  Setting rho = 0 (random selection)
      collapses (A)+(B) to E[R] = 0: mean-zero neutral drift with variation
      still present.  And because BOTH the directed response (h^2.rho.sigma) and
      the drift scale are proportional to sigma, the rails v in {0,1} -- where
      sigma -> 0 by (C) -- are the population-genetics FIXATION BOUNDARY: not a
      special "selection-inert" state but the point where q(1-q) -> 0 removes the
      raw material any force would act on.  This reinterprets the program's
      "selection-inert rail" / "zero-spread stall" observations.

Everything here is descriptive re-analysis of committed logged pools; no new
causal claim and no new data.  Conventions (spread = mean within-prompt
population SD ddof=0, rho = mean within-item Pearson corr of judge score with
candidate value, gap = kept-minus-pool) are inherited verbatim from
analysis_spread_util_unified.py, whose output JSON is the sole input.

Run:    uv run python scripts/analysis_population_genetics_unification.py
Writes: experiments/population_genetics_unification.json     (numpy only)
"""
import json
import os

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "experiments", "spread_util_unified.json")
OUT = os.path.join(ROOT, "experiments", "population_genetics_unification.json")

RNG = np.random.default_rng(20260724)


# ----------------------------------------------------------------- regression
def _ols(x, y):
    """OLS y = a + b x. Returns dict with slope, intercept, r, n."""
    x = np.asarray(x, float)
    y = np.asarray(y, float)
    m = np.isfinite(x) & np.isfinite(y)
    x, y = x[m], y[m]
    n = len(x)
    if n < 3 or np.std(x) < 1e-12:
        return {"slope": None, "intercept": None, "r": None, "n": int(n)}
    b, a = np.polyfit(x, y, 1)
    r = float(np.corrcoef(x, y)[0, 1])
    return {"slope": float(b), "intercept": float(a), "r": r, "n": int(n)}


def _slope_through_origin(x, y):
    """Least-squares slope with intercept forced to 0 (breeder's h^2)."""
    x = np.asarray(x, float)
    y = np.asarray(y, float)
    m = np.isfinite(x) & np.isfinite(y)
    x, y = x[m], y[m]
    if len(x) < 3 or np.dot(x, x) < 1e-12:
        return None, int(len(x))
    return float(np.dot(x, y) / np.dot(x, x)), int(len(x))


def _boot_slope_ci(x, y, origin=True, n_boot=2000):
    """Bootstrap 95% CI for the (through-origin or OLS) slope."""
    x = np.asarray(x, float)
    y = np.asarray(y, float)
    m = np.isfinite(x) & np.isfinite(y)
    x, y = x[m], y[m]
    n = len(x)
    if n < 5:
        return None, None
    out = []
    for _ in range(n_boot):
        idx = RNG.integers(0, n, n)
        xb, yb = x[idx], y[idx]
        if origin:
            if np.dot(xb, xb) < 1e-12:
                continue
            out.append(np.dot(xb, yb) / np.dot(xb, xb))
        else:
            if np.std(xb) < 1e-12:
                continue
            out.append(np.polyfit(xb, yb, 1)[0])
    if not out:
        return None, None
    lo, hi = np.percentile(out, [2.5, 97.5])
    return float(lo), float(hi)


def _mae(pred, obs):
    pred = np.asarray(pred, float)
    obs = np.asarray(obs, float)
    m = np.isfinite(pred) & np.isfinite(obs)
    return float(np.mean(np.abs(pred[m] - obs[m]))) if m.sum() else None


# ----------------------------------------------------------------- load
records = json.load(open(SRC))["records"]


def sub(pred):
    return [r for r in records if pred(r)]


def col(rows, key):
    return np.array([r.get(key, np.nan) if r.get(key) is not None else np.nan
                     for r in rows], float)


binary = sub(lambda r: r.get("binary_score_fraction", 0) > 0.99)  # risk axis
selfrep = sub(lambda r: r.get("axis") == "selfreport")
self_only = sub(lambda r: r.get("composition") == "self-only")

report = {
    "description": "Population-genetics unification of the selection loop: "
                   "breeder's equation R=h^2.S, S=rho.sigma factorization, "
                   "binomial (Wright-Fisher) phenotypic variance, and the "
                   "neutral-drift null / fixation boundary. Descriptive "
                   "re-analysis of experiments/spread_util_unified.json (340 "
                   "logged rounds, 74 runs); no new data or causal claim.",
    "source": "experiments/spread_util_unified.json",
    "n_records": len(records),
}

# ============================================================ (A) breeder's eq
# Response R = drift; selection differential S = pull (kept - current value).
slices = {
    "pooled": records,
    "risk_axis": binary,
    "selfreport_axis": selfrep,
    "self_only": self_only,
    "base_mixed": sub(lambda r: r.get("composition") == "base-mixed"),
    "peer_mixed": sub(lambda r: r.get("composition") == "peer-mixed"),
    "qwen": sub(lambda r: r.get("organism", "").lower().startswith("qwen")
                or "qwen" in str(r.get("organism", "")).lower()),
    "olmo": sub(lambda r: "olmo" in str(r.get("organism", "")).lower()),
    # interior only: guards h^2 against the shared vanishing of R and S at rails
    "risk_interior_0.2_0.8": sub(
        lambda r: r.get("binary_score_fraction", 0) > 0.99
        and 0.2 <= r.get("value", -1) <= 0.8),
}
breeder = {}
for name, rows in slices.items():
    S = col(rows, "pull")
    R = col(rows, "drift")
    slope0, n0 = _slope_through_origin(S, R)
    lo, hi = _boot_slope_ci(S, R, origin=True)
    ols = _ols(S, R)
    breeder[name] = {
        "h2_through_origin": slope0,
        "h2_ci95": [lo, hi],
        "ols_slope": ols["slope"],
        "ols_intercept": ols["intercept"],
        "r": ols["r"],
        "n": n0,
    }
report["A_breeders_equation"] = {
    "definition": "R (drift) = h^2 . S (pull = kept_mean - value); "
                  "h^2 = realized heritability = per-round transmission of the "
                  "selection differential into the trait mean.",
    "by_slice": breeder,
}

# ============================================================ (B) S = rho.sigma
# Self-only pools: pull ~= gap = rho.sigma. Verify each link and the composite.
so_bin = [r for r in self_only if r.get("binary_score_fraction", 0) > 0.99
          and r.get("rho") is not None]
rho = col(so_bin, "rho")
sig = col(so_bin, "spread")
gap = col(so_bin, "gap")
pull = col(so_bin, "pull")
drift = col(so_bin, "drift")
rho_sigma = rho * sig
report["B_selection_differential"] = {
    "definition": "gap ~= rho . sigma (Price differential); in self-only pools "
                  "pull ~= gap, so S = rho . sigma.",
    "gap_on_rho_sigma": _ols(rho_sigma, gap),
    "gap_vs_rho_sigma_mae": _mae(rho_sigma, gap),
    "pull_on_gap_selfonly": _ols(gap, pull),
    "composite_R_on_h2rhosigma": None,  # filled below
    "n": len(so_bin),
}
# composite closed form: predict R = h2 . rho . sigma with h2 from the risk-axis
h2_risk = breeder["risk_axis"]["h2_through_origin"]
pred_R = h2_risk * rho_sigma
report["B_selection_differential"]["h2_used"] = h2_risk
report["B_selection_differential"]["composite_R_on_h2rhosigma"] = _ols(pred_R, drift)
report["B_selection_differential"]["composite_mae_vs_persistence"] = {
    "closed_form_h2_rho_sigma": _mae(pred_R, drift),
    "persistence_zero_drift": _mae(np.zeros_like(drift), drift),
}

# ============================================================ (C) binomial var
# On binary rounds: V_within = q(1-q) - V_between. binary_headroom = q(1-q).
qq = col(binary, "binary_headroom")             # q(1-q), q = pool mean
v_within = col(binary, "mean_item_variance")    # mean within-prompt variance
v_between = col(binary, "between_item_mean_variance")
identity_resid = v_within - (qq - v_between)     # should be ~0
sigma_bin = col(binary, "spread")
report["C_binomial_variance"] = {
    "definition": "binary candidate value 0/1 => total offered variance = "
                  "q(1-q); law of total variance splits it into within-prompt "
                  "and between-prompt. sigma ~ sqrt(within-prompt variance).",
    "identity_V_within_eq_qq_minus_Vbetween": {
        "mean_abs_residual": float(np.nanmean(np.abs(identity_resid))),
        "max_abs_residual": float(np.nanmax(np.abs(identity_resid))),
        "n": int(np.isfinite(identity_resid).sum()),
    },
    # sigma envelope: reported spread vs the binomial ceiling sqrt(q(1-q))
    "spread_on_sqrt_qq": _ols(np.sqrt(np.clip(qq, 0, None)), sigma_bin),
    "fraction_of_binomial_ceiling": float(
        np.nanmean(sigma_bin / np.sqrt(np.clip(qq, 1e-9, None)))),
}

# ============================================================ (D) null + fixation
random_arms = sub(lambda r: r.get("judge") == "random")
oracle_arms = sub(lambda r: r.get("judge") == "score oracle")
directed = sub(lambda r: r.get("rho") is not None and abs(r.get("rho", 0)) >= 0.3)


def drift_stats(rows):
    d = col(rows, "drift")
    d = d[np.isfinite(d)]
    g = np.abs(col(rows, "gap"))
    return {
        "n": int(len(d)),
        "mean_drift": float(np.mean(d)) if len(d) else None,
        "sd_drift": float(np.std(d)) if len(d) else None,
        "mean_abs_gap": float(np.nanmean(g)),
        "mean_spread": float(np.nanmean(col(rows, "spread"))),
    }


# neutral drift variance vs available variance: does Var(drift) track sigma^2?
rnd_sig2 = col(random_arms, "spread") ** 2
rnd_absdrift = np.abs(col(random_arms, "drift"))

# fixation curve: spread and |drift| binned by trait value (binary axis)
bins = [(0, .1), (.1, .3), (.3, .5), (.5, .7), (.7, .9), (.9, 1.0001)]
vval = col(binary, "value")
sval = col(binary, "spread")
dval = np.abs(col(binary, "drift"))
qqv = col(binary, "binary_headroom")
fixation_curve = []
for lo, hi in bins:
    m = (vval >= lo) & (vval < hi)
    fixation_curve.append({
        "value_bin": [lo, round(hi, 2)],
        "n": int(m.sum()),
        "mean_spread": float(np.nanmean(sval[m])) if m.any() else None,
        "mean_sqrt_qq": float(np.nanmean(np.sqrt(np.clip(qqv[m], 0, None))))
        if m.any() else None,
        "mean_abs_drift": float(np.nanmean(dval[m])) if m.any() else None,
    })

# rail rounds: how "inert" they are, and that inertness = zero spread
rail = sub(lambda r: r.get("binary_score_fraction", 0) > 0.99
           and (r.get("value", .5) <= 0.05 or r.get("value", .5) >= 0.95))
rail_spread = col(rail, "spread")
rail_absdrift = np.abs(col(rail, "drift"))
report["D_neutral_null_and_fixation"] = {
    "definition": "rho=0 (random selection) => E[R]=0 neutral drift; both the "
                  "directed response and the drift scale are proportional to "
                  "sigma, so v in {0,1} (sigma->0 by C) is the fixation "
                  "boundary, reinterpreting 'selection-inert rails'.",
    "neutral_null_random_arms": drift_stats(random_arms),
    "directed_arms_abs_rho_ge_0.3": drift_stats(directed),
    "score_oracle_arms": drift_stats(oracle_arms),
    "neutral_drift_var_tracks_spread2": _ols(rnd_sig2, rnd_absdrift),
    "fixation_curve_spread_vs_value": fixation_curve,
    "rail_rounds": {
        "n": len(rail),
        "mean_spread": float(np.nanmean(rail_spread)) if len(rail) else None,
        "mean_abs_drift": float(np.nanmean(rail_absdrift)) if len(rail) else None,
        "note": "value<=0.05 or >=0.95 on the binary axis; near-zero spread and "
                "near-zero |drift| is the fixation boundary, not a special state.",
    },
}

# ============================================================ headline summary
report["headline"] = {
    "breeders_h2_risk_axis": breeder["risk_axis"]["h2_through_origin"],
    "breeders_h2_risk_ci95": breeder["risk_axis"]["h2_ci95"],
    "breeders_h2_interior_only": breeder["risk_interior_0.2_0.8"][
        "h2_through_origin"],
    "gap_eq_rho_sigma_r": report["B_selection_differential"][
        "gap_on_rho_sigma"]["r"],
    "binomial_identity_max_resid": report["C_binomial_variance"][
        "identity_V_within_eq_qq_minus_Vbetween"]["max_abs_residual"],
    "neutral_null_mean_drift": report["D_neutral_null_and_fixation"][
        "neutral_null_random_arms"]["mean_drift"],
    "neutral_null_sd_drift": report["D_neutral_null_and_fixation"][
        "neutral_null_random_arms"]["sd_drift"],
    "one_line": "E[Delta v] = h^2 . rho . sigma  (breeder's equation with "
                "selection differential rho.sigma); sigma^2 ~ q(1-q) is the "
                "binomial/Wright-Fisher variance that vanishes at the rails, "
                "making v in {0,1} the fixation boundary; rho=0 gives mean-zero "
                "neutral drift.",
}

json.dump(report, open(OUT, "w"), indent=2)
print("wrote", OUT)
print()
h = report["headline"]
print("(A) breeder's h^2 (risk axis, through origin): %.3f  CI95 %s" % (
    h["breeders_h2_risk_axis"], h["breeders_h2_risk_ci95"]))
print("    interior-only (v in 0.2-0.8) h^2:            %.3f" % (
    h["breeders_h2_interior_only"]))
print("    h^2 by slice:")
for name, b in breeder.items():
    if b["h2_through_origin"] is not None:
        print("      %-24s h2=%.3f  r=%.2f  n=%d" % (
            name, b["h2_through_origin"], b["r"] or float("nan"), b["n"]))
print("(B) gap = rho.sigma:  slope %.3f  r %.2f  MAE %.4f (n=%d)" % (
    report["B_selection_differential"]["gap_on_rho_sigma"]["slope"],
    report["B_selection_differential"]["gap_on_rho_sigma"]["r"],
    report["B_selection_differential"]["gap_vs_rho_sigma_mae"],
    report["B_selection_differential"]["n"]))
print("    closed form R=h2.rho.sigma MAE %.4f vs %.4f persistence" % (
    report["B_selection_differential"]["composite_mae_vs_persistence"][
        "closed_form_h2_rho_sigma"],
    report["B_selection_differential"]["composite_mae_vs_persistence"][
        "persistence_zero_drift"]))
print("(C) binomial identity max abs residual: %.5f  spread/ceiling %.2f" % (
    h["binomial_identity_max_resid"],
    report["C_binomial_variance"]["fraction_of_binomial_ceiling"]))
print("(D) neutral null (random arms): mean drift %.4f  sd %.4f  |gap| %.4f" % (
    h["neutral_null_mean_drift"], h["neutral_null_sd_drift"],
    report["D_neutral_null_and_fixation"]["neutral_null_random_arms"][
        "mean_abs_gap"]))
print("    fixation curve (value bin -> mean spread):")
for fc in fixation_curve:
    print("      %s  n=%3d  spread=%.3f  sqrt(q(1-q))=%.3f  |drift|=%.3f" % (
        fc["value_bin"], fc["n"], fc["mean_spread"] or float("nan"),
        fc["mean_sqrt_qq"] or float("nan"), fc["mean_abs_drift"] or float("nan")))
