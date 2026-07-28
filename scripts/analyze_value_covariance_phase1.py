"""Re-derive the value-covariance phase-1 result from its raw scores.

The Kaggle kernel that produced experiments/value_covariance/output/
value_covariance_phase1.json was pushed 2026-07-25 09:49, BEFORE the order-flip
null floor was added to experiments/value_covariance/script.py (15:04 the same
day). So the instrument verdict shipped inside that JSON was produced by the old
fixed-0.05 threshold, which tests against a floor of zero. This script re-applies
the corrected gate and re-derives every downstream number from raw_scores.

It also computes three things the kernel did not:

1. The CROSS-METHOD cross-pool test. SPEC design note 3 makes the cross-method
   covariance (selected axis from judge A, off-target axes from judge B) the
   primary estimate and the same-judge matrix a sensitivity analysis. The kernel
   only emitted a cross-method *correlation* matrix on pool A; its cross-pool
   prediction used same-judge covariance throughout, so the primary test as
   specified was never run.
2. Cluster-aware inference on the cross-pool fit. Its 30 "pairs" are 6 selection
   events x 5 off-target axes; the 5 rows inside one event share one selected
   axis, one on-axis differential and one set of judge errors. Effective n is 6,
   not 30. Reported as a cluster bootstrap over selected axis.
3. A drop-scope_expansion sensitivity pass, since that axis has both the lowest
   variance and no cross-method agreement.

Writes experiments/value_covariance_phase1_analysis.json.
"""

import json
import math
import pathlib

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[1]
SRC = ROOT / "experiments/value_covariance/output/value_covariance_phase1.json"
OUT = ROOT / "experiments/value_covariance_phase1_analysis.json"
RNG = np.random.default_rng(20260728)
KEEP = 4
N_BOOT = 5000


# --- estimation -------------------------------------------------------------

def within_prompt_cov(s):
    """Covariance of axis scores across candidates, pooled over prompts."""
    s = np.asarray(s, dtype=float)
    n_p, n_c, n_a = s.shape
    acc = np.zeros((n_a, n_a))
    for i in range(n_p):
        c = s[i] - s[i].mean(axis=0, keepdims=True)
        acc += c.T @ c / (n_c - 1)
    return acc / n_p


def within_prompt_cross_cov(sa, sb):
    """Cov(judge A axis a, judge B axis b) across candidates, pooled over prompts.

    Not symmetric: rows index judge A axes, columns judge B axes.
    """
    sa, sb = np.asarray(sa, float), np.asarray(sb, float)
    n_p, n_c, n_a = sa.shape
    acc = np.zeros((n_a, n_a))
    for i in range(n_p):
        ca = sa[i] - sa[i].mean(axis=0, keepdims=True)
        cb = sb[i] - sb[i].mean(axis=0, keepdims=True)
        acc += ca.T @ cb / (n_c - 1)
    return acc / n_p


def observed_differentials(scores_sel, scores_read, sel_axis, keep=KEEP):
    """Rank candidates by scores_sel[:,:,sel_axis]; measure kept-minus-pool on
    every axis of scores_read. scores_read may be a different judge."""
    ssel, sread = np.asarray(scores_sel, float), np.asarray(scores_read, float)
    n_p, _, n_a = sread.shape
    kept = np.zeros(n_a)
    pool = np.zeros(n_a)
    for i in range(n_p):
        order = np.argsort(-ssel[i, :, sel_axis])[:keep]
        kept += sread[i, order, :].mean(axis=0)
        pool += sread[i, :, :].mean(axis=0)
    return (kept - pool) / n_p


def fit(xs, ys):
    xs, ys = np.asarray(xs, float), np.asarray(ys, float)
    ok = np.isfinite(xs) & np.isfinite(ys)
    xs, ys = xs[ok], ys[ok]
    if len(xs) < 3:
        return None
    mx, my = xs.mean(), ys.mean()
    sxx = float(((xs - mx) ** 2).sum())
    syy = float(((ys - my) ** 2).sum())
    sxy = float(((xs - mx) * (ys - my)).sum())
    if sxx <= 0 or syy <= 0:
        return None
    return {
        "n_rows": int(len(xs)),
        "slope": round(sxy / sxx, 4),
        "correlation": round(sxy / math.sqrt(sxx * syy), 4),
        "mae": round(float(np.abs(xs - ys).mean()), 5),
        "sign_agreement": round(float((np.sign(xs) == np.sign(ys)).mean()), 4),
    }


def cross_pool(cov_sel_read, scores_sel_B, scores_read_B, axes, keep=KEEP):
    """Estimate on pool set A (via cov_sel_read), predict on held-out set B.

    cov_sel_read[a, b] is Cov(selection-axis a, read-axis b); cov_sel_read[a, a]
    must be the variance of the SELECTION measurement of axis a.
    """
    rows = []
    for a in range(len(axes)):
        obs = observed_differentials(scores_sel_B, scores_read_B, a, keep)
        denom = cov_sel_read[a, a]
        pred = cov_sel_read[a, :] / denom * obs[a] if denom > 1e-12 else np.full(len(axes), np.nan)
        for b in range(len(axes)):
            if a == b:
                continue
            rows.append({"selected_axis": axes[a], "offtarget_axis": axes[b],
                         "observed": round(float(obs[b]), 5),
                         "predicted": round(float(pred[b]), 5),
                         "on_axis_differential": round(float(obs[a]), 5)})
    return rows


def prompt_bootstrap(scores_A, scores_B, axes, n_boot=1000):
    """Resample PROMPTS with replacement and recompute the whole cross-pool fit.

    Prompts are the independent sampling unit: the covariance on set A and the
    observed differentials on set B are both averages over the same 30 prompts,
    so the 30 (selected, off-target) rows share that sampling error entirely.
    Cluster-bootstrapping the rows cannot see this; only re-estimating from
    resampled prompts can.
    """
    n_p = scores_A.shape[0]
    slopes, corrs, preds = [], [], []
    for _ in range(n_boot):
        idx = RNG.integers(0, n_p, n_p)
        A, B = scores_A[idx], scores_B[idx]
        rows = cross_pool(within_prompt_cov(A), B, B, axes)
        f = fit([r["predicted"] for r in rows], [r["observed"] for r in rows])
        if f:
            slopes.append(f["slope"])
            corrs.append(f["correlation"])
            preds.append([r["predicted"] for r in rows])

    def ci(v):
        v = np.sort(np.array(v, float))
        return [round(float(np.quantile(v, 0.025)), 4), round(float(np.quantile(v, 0.975)), 4)]

    # errors-in-variables: the predictor is itself an estimate. OLS slope is
    # attenuated by lambda = var(true predictor) / var(measured predictor), and
    # var(measured) = var(true) + var(estimation error). The bootstrap gives the
    # estimation error directly, so lambda is recoverable and the "slope below 1"
    # reading can be checked against it.
    P = np.array(preds, float)                      # n_boot x n_rows
    err_var = float(np.mean(P.var(axis=0, ddof=1)))  # sampling variance per row
    base = cross_pool(within_prompt_cov(scores_A), scores_B, scores_B, axes)
    tot_var = float(np.var([r["predicted"] for r in base], ddof=1))
    lam = max(1e-9, (tot_var - err_var) / tot_var) if tot_var > 0 else float("nan")
    base_slope = fit([r["predicted"] for r in base], [r["observed"] for r in base])["slope"]

    return {"n_prompts": int(n_p), "n_boot": len(slopes),
            "slope_ci95": ci(slopes), "correlation_ci95": ci(corrs),
            "slope_median": round(float(np.median(slopes)), 4),
            "p_slope_below_1": round(float(np.mean(np.array(slopes) < 1.0)), 4),
            "predictor_error_variance": round(err_var, 8),
            "predictor_total_variance": round(tot_var, 8),
            "attenuation_lambda": round(float(lam), 4),
            "slope_corrected_for_predictor_error": round(float(base_slope / lam), 4)}


def cluster_bootstrap(rows, n_boot=N_BOOT):
    """Resample whole selection events, not individual (a, b) pairs.

    The 5 rows sharing a selected axis are one selection event: same ranking,
    same on-axis differential, same judge errors. Treating them as 30
    independent points overstates n by 5x.
    """
    by_event = {}
    for r in rows:
        by_event.setdefault(r["selected_axis"], []).append(r)
    events = list(by_event.values())
    slopes, corrs = [], []
    for _ in range(n_boot):
        pick = RNG.integers(0, len(events), len(events))
        draw = [r for i in pick for r in events[i]]
        f = fit([r["predicted"] for r in draw], [r["observed"] for r in draw])
        if f:
            slopes.append(f["slope"])
            corrs.append(f["correlation"])

    def ci(v):
        if not v:
            return None
        v = np.sort(np.array(v, float))
        return [round(float(np.quantile(v, 0.025)), 4), round(float(np.quantile(v, 0.975)), 4)]

    return {"n_events": len(events), "n_rows": len(rows),
            "slope_ci95": ci(slopes), "correlation_ci95": ci(corrs),
            "n_boot_converged": len(slopes)}


# --- main -------------------------------------------------------------------

def main():
    d = json.load(open(SRC))
    axes = d["config"]["axes"]
    sc = {j: {p: np.array(d["raw_scores"][j][p], float) for p in ("A", "B")}
          for j in ("judge_a", "judge_b")}
    res = {"source": str(SRC.relative_to(ROOT)), "config": d["config"], "axes": axes}

    # 1. instrument gate, with the order-flip null floor the kernel predates
    res["instrument_gate"] = {}
    for j in ("judge_a", "judge_b"):
        gap = d["instrument_check"][j]["mean_order_gap"]
        s = sc[j]["A"]
        n_eff = max(1, s.shape[1] - 1)
        floor = float(gap * 0.5 / math.sqrt(n_eff))
        per = {}
        for k, name in enumerate(axes):
            sd = float(np.mean(np.std(s[:, :, k], axis=1)))
            per[name] = {"within_prompt_sd": round(sd, 5),
                         "ratio_to_null_floor": round(sd / floor, 3),
                         "passes": bool(sd > floor)}
        worst = min(v["within_prompt_sd"] for v in per.values())
        res["instrument_gate"][j] = {
            "mean_order_gap": gap,
            "null_floor_from_order_flipping": round(floor, 5),
            "min_within_prompt_sd": round(worst, 5),
            "n_axes_passing": sum(v["passes"] for v in per.values()),
            "per_axis": per,
            "verdict_corrected": ("USABLE" if (worst >= 0.05 and worst > floor)
                                  else "INSTRUMENT_FAILURE_NO_DISCRIMINATION"),
            "verdict_as_shipped": d["instrument_check"][j]["verdict"],
        }

    # 2. cross-method same-axis agreement (the instrument check that gates everything)
    xm = within_prompt_cross_cov(sc["judge_a"]["A"], sc["judge_b"]["A"])
    va = np.sqrt(np.diag(within_prompt_cov(sc["judge_a"]["A"])))
    vb = np.sqrt(np.diag(within_prompt_cov(sc["judge_b"]["A"])))
    xmcorr = xm / np.outer(va, vb)
    res["cross_method_correlation_poolA"] = [[round(float(v), 4) for v in r] for r in xmcorr]
    res["cross_method_same_axis_agreement"] = {
        a: round(float(xmcorr[i, i]), 4) for i, a in enumerate(axes)}
    res["cross_method_agreement_matches_shipped"] = bool(np.allclose(
        xmcorr, np.array(d["cross_method_correlation_poolA"], float), atol=2e-3))

    # 3. variances, raw and net of length is already in the shipped file; carry the
    #    raw variances forward so the near-zero-variance screen is in one place
    res["variances_raw"] = {k: {a: round(float(v), 5) for a, v in zip(axes, c["variances_raw"])}
                            for k, c in d["covariance"].items()}

    # 4. cross-pool: same-judge (as shipped) and cross-method (as SPEC'd)
    res["cross_pool"] = {}
    for j in ("judge_a", "judge_b"):
        cov_A = within_prompt_cov(sc[j]["A"])
        rows = cross_pool(cov_A, sc[j]["B"], sc[j]["B"], axes)
        summ = fit([r["predicted"] for r in rows], [r["observed"] for r in rows])
        shipped = d["cross_pool"][j]["summary"]
        scale = float(np.mean(np.abs([r["on_axis_differential"] for r in rows])))
        res["cross_pool"][f"same_judge_{j}"] = {
            "summary": summ,
            "mae_over_mean_on_axis_differential": round(summ["mae"] / scale, 4),
            "mean_on_axis_differential": round(scale, 5),
            "cluster_bootstrap": cluster_bootstrap(rows),
            "prompt_bootstrap": prompt_bootstrap(sc[j]["A"], sc[j]["B"], axes),
            "matches_shipped": bool(abs(summ["slope"] - shipped["slope"]) < 5e-3
                                    and abs(summ["correlation"] - shipped["correlation"]) < 5e-3),
            "shipped_summary": shipped,
        }
    cov_xm_A = within_prompt_cross_cov(sc["judge_a"]["A"], sc["judge_b"]["A"])
    cov_xm_A = cov_xm_A.copy()
    np.fill_diagonal(cov_xm_A, np.diag(within_prompt_cov(sc["judge_a"]["A"])))
    rows_xm = cross_pool(cov_xm_A, sc["judge_a"]["B"], sc["judge_b"]["B"], axes)
    res["cross_pool"]["cross_method_primary"] = {
        "note": "selection ranked by judge A, spillover read by judge B; no shared judge error",
        "summary": fit([r["predicted"] for r in rows_xm], [r["observed"] for r in rows_xm]),
        "cluster_bootstrap": cluster_bootstrap(rows_xm),
        "pairs": rows_xm,
    }

    # 5. sensitivity: drop scope_expansion
    keep_ax = [i for i, a in enumerate(axes) if a != "scope_expansion"]
    sub_axes = [axes[i] for i in keep_ax]
    res["sensitivity_drop_scope_expansion"] = {}
    for j in ("judge_a", "judge_b"):
        A = sc[j]["A"][:, :, keep_ax]
        B = sc[j]["B"][:, :, keep_ax]
        rows = cross_pool(within_prompt_cov(A), B, B, sub_axes)
        res["sensitivity_drop_scope_expansion"][f"same_judge_{j}"] = {
            "summary": fit([r["predicted"] for r in rows], [r["observed"] for r in rows]),
            "cluster_bootstrap": cluster_bootstrap(rows)}

    OUT.write_text(json.dumps(res, indent=2))
    print(f"wrote {OUT.relative_to(ROOT)}")
    for j in ("judge_a", "judge_b"):
        g = res["instrument_gate"][j]
        print(f"{j}: floor={g['null_floor_from_order_flipping']} "
              f"min_sd={g['min_within_prompt_sd']} passing={g['n_axes_passing']}/6 "
              f"-> {g['verdict_corrected']} (shipped: {g['verdict_as_shipped']})")
    print("cross-method same-axis agreement:", res["cross_method_same_axis_agreement"])
    for k, v in res["cross_pool"].items():
        print(k, v["summary"], v["cluster_bootstrap"])


if __name__ == "__main__":
    main()
