"""A stability criterion for self-training loops, and its first measurement.

WHY THIS EXISTS. Every predictive result this project has produced treats the
judge's agreement rho as an exogenous, slowly-drifting parameter. That is the
right first move, but it is structurally incapable of producing a bifurcation,
which is why the six-run duel split where some runs amplified and some collapsed
has never had an account.

The 2026-07-28 literature sweep found the missing account is old. The
Lande-Kirkpatrick model of Fisherian runaway is a two-trait system in which a
preference evolves only as a correlated response to selection on the trait it
prefers, and its variables map onto ours almost exactly:

    ornament mean            ->  value v
    preference mean          ->  judge agreement rho
    additive genetic variance -> candidate spread sigma
    response = 1/2 G beta    ->  dv = h^2 * rho * sigma   (the same equation)
    genetic covariance G_tp  ->  how much rho moves per unit of value movement
    trajectory slope G_tp/G_t ->  c = drho / dv           <- NEVER MEASURED HERE
    line of equilibria       ->  rho * sigma = 0

THE CRITERION. With the equilibrium line at rho = 0, the two-step recursion is

    v_{t+1}   = v_t + h^2 * sigma * rho_t
    rho_{t+1} = rho_t + c * (v_{t+1} - v_t)
              = rho_t * (1 + c * h^2 * sigma)

so agreement grows or decays geometrically with per-round LOOP GAIN

    G = 1 + c * h^2 * sigma

G > 1 (equivalently c > 0) is runaway: the value moves, and that movement makes
the judge agree with the direction of travel even more. G < 1 (c < 0) is
self-limiting: movement erodes the judge's agreement and the loop settles onto
the rho = 0 manifold. The sign works in both directions of travel, because dv is
itself proportional to rho.

This is a genuine forecasting tool if c is stable: measure sigma and rho in
round one, plug in a c estimated once per setup, and the gain says whether the
loop amplifies or settles, before running it.

TWO ESTIMATORS, BOTH DELIBERATELY CONSERVATIVE.

  levels (primary)  rho_t = a_run + c * v_t, with run fixed effects. Noise in
                    rho sits in the outcome, where it inflates standard errors
                    without biasing c. Noise in v sits in the regressor, where
                    it attenuates c toward zero.

  differences       d(rho) on d(v). This one has a bias that must not be
                    ignored: d(rho)_t contains -eps(rho_t) and d(v)_t is
                    proportional to rho_t, which also contains +eps(rho_t). The
                    induced covariance is negative, so the differences estimator
                    is biased TOWARD "stable" by roughly -var(eps_rho) * h^2 *
                    sigma / var(dv). It is reported with that bias estimated
                    rather than as a second opinion.

Both estimators are conservative for detecting c > 0, and the fixed-effects
version additionally carries a Nickell bias that is negative for a positively
autocorrelated regressor. So a positive, interval-excluding-zero c is a finding;
a null is weak evidence.

THE MECHANICAL ROUTE TO c < 0, WHICH HAS TO BE RULED OUT. Candidate value scores
here are binary, so the within-prompt spread obeys sigma <= sqrt(v(1-v)) exactly.
A run travelling toward either rail therefore loses spread by arithmetic, and rho
is a correlation computed over candidate scores that are becoming constant --
which drags rho toward zero whatever the judge is doing. Going up, rho falls and
dv > 0; going down, rho rises toward zero from below and dv < 0. Both give c < 0.

So a raw negative c is not evidence of a self-limiting JUDGE. Every group is
therefore fitted twice: once as rho on v, and once as rho on v with the binomial
ceiling sqrt(v(1-v)) also in the regression. The second coefficient is the part
of the coupling that is not the ceiling closing in, and it is the one the loop
gain should be built from.

ROUNDS WITH NO MEASURABLE AGREEMENT ARE EXCLUDED. When every candidate in a pool
scores identically there is nothing for the judge to correlate with, and the
corpus records rho as 0. Those zeros are not measurements of judge preference
and would drag c toward zero; they are dropped here and counted. This is the
opposite convention from scripts/analysis_agreement_drift.py, which keeps them
because collapsed pools are what that analysis is about.

Writes experiments/judge_coupling_stability.json.
"""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
UNIFIED = ROOT / "experiments/spread_util_unified.json"
OUT = ROOT / "experiments/judge_coupling_stability.json"

BOOTSTRAP_DRAWS = 4000
SEED = 20260729

# The measured transmission coefficient, from the response-saturation analysis
# (unified corpus, pool-offset controlled, measurement-error corrected). Only
# used to convert c into a loop gain; c itself does not depend on it.
H2 = 0.809

EVOLVING = {"self"}
# An oracle's agreement is +-1 with the value axis by construction, so its
# coupling is zero by definition rather than by measurement. A judge-swap run
# changes judge mid-flight, which is a different system.
EXCLUDE = {"score oracle", "schedule"}


def run_key(rec):
    return rec["cond"], rec["seed"], rec["source"]


def load():
    unified = json.loads(UNIFIED.read_text())
    runs = defaultdict(list)
    for rec in unified["records"]:
        runs[run_key(rec)].append(rec)
    for rows in runs.values():
        rows.sort(key=lambda r: r["round"])
    return runs


def build_rows(runs):
    rows, dropped = [], {"imputed_rho": 0, "missing": 0}
    for key, run_rows in runs.items():
        judge = run_rows[0]["judge"]
        for rec in run_rows:
            rho = rec.get("rho")
            if rho is None:
                # zero-spread pools record no rho; agreement is undefined, not 0
                dropped["imputed_rho" if abs(float(rec["spread"])) < 1e-12
                        else "missing"] += 1
                continue
            rows.append({
                "run": key,
                "judge": judge,
                "evolving": judge in EVOLVING,
                "organism": rec["organism"],
                "axis": rec["axis"],
                "round": int(rec["round"]),
                "v": float(rec["value"]),
                "rho": float(rho),
                "sigma": float(rec["spread"]),
                "drift": float(rec["drift"]),
            })
    return rows, dropped


def _demeaned(rows, cols):
    """Run-demeaned design and outcome for a fixed-effects fit."""
    by_run = defaultdict(list)
    for r in rows:
        by_run[r["run"]].append(r)
    Xs, ys = [], []
    for run_rows in by_run.values():
        if len(run_rows) < 2:
            continue
        M = np.column_stack([np.array([col(r) for r in run_rows])
                             for col in cols])
        y = np.array([r["rho"] for r in run_rows])
        Xs.append(M - M.mean(axis=0))
        ys.append(y - y.mean())
    if not Xs:
        return None, None
    return np.vstack(Xs), np.concatenate(ys)


def levels_fixed_effects(rows):
    """Within-run slope of agreement on value. Returns c, or None."""
    X, y = _demeaned(rows, [lambda r: r["v"]])
    if X is None or np.var(X[:, 0]) < 1e-12:
        return None
    return float(np.sum(X[:, 0] * y) / np.sum(X[:, 0] ** 2))


def levels_ceiling_controlled(rows):
    """Coupling with the binomial spread ceiling sqrt(v(1-v)) also in the fit.

    Isolates the part of d(rho)/d(v) that is NOT the mechanical closing of the
    binary-score ceiling as a run approaches a rail.
    """
    X, y = _demeaned(rows, [lambda r: r["v"],
                            lambda r: float(np.sqrt(max(r["v"] * (1 - r["v"]),
                                                        0.0)))])
    if X is None or X.shape[0] < 6:
        return None
    if min(np.var(X[:, 0]), np.var(X[:, 1])) < 1e-12:
        return None
    try:
        beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    except np.linalg.LinAlgError:
        return None
    return float(beta[0])


def differences(rows):
    """Slope of round-to-round agreement change on value change."""
    by_run = defaultdict(list)
    for r in rows:
        by_run[r["run"]].append(r)
    dv, drho = [], []
    for run_rows in by_run.values():
        run_rows = sorted(run_rows, key=lambda r: r["round"])
        for a, b in zip(run_rows, run_rows[1:]):
            if b["round"] != a["round"] + 1:
                continue
            dv.append(b["v"] - a["v"])
            drho.append(b["rho"] - a["rho"])
    if len(dv) < 5 or np.var(dv) < 1e-12:
        return None
    dv = np.array(dv)
    drho = np.array(drho)
    X = np.column_stack([np.ones(len(dv)), dv])
    beta, *_ = np.linalg.lstsq(X, drho, rcond=None)
    return float(beta[1])


def cluster_bootstrap(rows, statistic, draws=BOOTSTRAP_DRAWS, seed=SEED):
    by_run = defaultdict(list)
    for r in rows:
        by_run[r["run"]].append(r)
    keys = list(by_run)
    if len(keys) < 3:
        return None
    rng = np.random.default_rng(seed)
    vals = []
    for _ in range(draws):
        sample = []
        for i in rng.integers(0, len(keys), size=len(keys)):
            sample.extend(by_run[keys[i]])
        stat = statistic(sample)
        if stat is not None and np.isfinite(stat):
            vals.append(stat)
    if len(vals) < 100:
        return None
    arr = np.array(vals)
    return {"se": float(arr.std(ddof=1)),
            "ci_lo": float(np.percentile(arr, 2.5)),
            "ci_hi": float(np.percentile(arr, 97.5)),
            "draws": len(arr)}


def differences_bias(rows):
    """Estimate the mean-reversion bias in the differences estimator.

    d(rho) carries -eps(rho_t); d(v) is proportional to rho_t and so carries
    +h^2*sigma*eps(rho_t). The induced covariance is -var(eps_rho)*h^2*sigma,
    and the bias in the slope is that divided by var(d(v)).

    var(eps_rho) is not recorded per round, so it is bounded rather than
    estimated: the within-run residual variance of rho after removing a linear
    trend in v is an UPPER bound on it (it also contains real fluctuation), which
    makes this an upper bound on the magnitude of the bias.
    """
    by_run = defaultdict(list)
    for r in rows:
        by_run[r["run"]].append(r)
    resid, dv, sigmas = [], [], []
    for run_rows in by_run.values():
        run_rows = sorted(run_rows, key=lambda r: r["round"])
        if len(run_rows) >= 3:
            v = np.array([r["v"] for r in run_rows])
            rho = np.array([r["rho"] for r in run_rows])
            if np.var(v) > 1e-12:
                X = np.column_stack([np.ones(len(v)), v])
                beta, *_ = np.linalg.lstsq(X, rho, rcond=None)
                resid.extend((rho - X @ beta).tolist())
        for a, b in zip(run_rows, run_rows[1:]):
            if b["round"] == a["round"] + 1:
                dv.append(b["v"] - a["v"])
                sigmas.append(a["sigma"])
    if len(resid) < 10 or len(dv) < 5 or np.var(dv) < 1e-12:
        return None
    var_eps_upper = float(np.var(resid, ddof=1))
    sigma_bar = float(np.mean(sigmas))
    return {
        "upper_bound_var_eps_rho": var_eps_upper,
        "mean_sigma": sigma_bar,
        "var_dv": float(np.var(dv)),
        "bias_upper_bound_magnitude":
            float(var_eps_upper * H2 * sigma_bar / np.var(dv)),
        "direction": "negative (toward 'stable')",
    }


def geometric_decay_check(rows, gain):
    """Consistency check on the FORM, not just the sign, of the criterion.

    The recursion predicts |rho_t| = |rho_1| * G^(t-1). This compares the
    observed mean ratio |rho_t| / |rho_1| against that, within runs that have a
    usable round-1 agreement. It is a consistency check rather than a
    validation: G was estimated on these same rounds, so agreement on the sign
    is partly built in. What it does test independently is whether the decay is
    geometric at the estimated rate, which nothing in the fit imposes.
    """
    by_run = defaultdict(list)
    for r in rows:
        by_run[r["run"]].append(r)
    obs = defaultdict(list)
    for run_rows in by_run.values():
        run_rows = sorted(run_rows, key=lambda r: r["round"])
        first = next((r for r in run_rows if r["round"] == 1), None)
        if first is None or abs(first["rho"]) < 0.05:
            continue          # a near-zero denominator makes the ratio noise
        for r in run_rows:
            if r["round"] > 1:
                obs[r["round"]].append(abs(r["rho"]) / abs(first["rho"]))
    out = {}
    for t, vals in sorted(obs.items()):
        if len(vals) < 4:
            continue
        out[f"round{t}"] = {
            "n_runs": len(vals),
            "observed_mean_ratio": float(np.mean(vals)),
            "observed_median_ratio": float(np.median(vals)),
            "predicted_ratio": float(gain ** (t - 1)),
        }
    return out or None


def rho_nullcline(rows):
    """Between-run: where does agreement cross zero as a function of value?"""
    v = np.array([r["v"] for r in rows])
    rho = np.array([r["rho"] for r in rows])
    if len(v) < 10 or np.var(v) < 1e-12:
        return None
    X = np.column_stack([np.ones(len(v)), v])
    beta, *_ = np.linalg.lstsq(X, rho, rcond=None)
    crossing = float(-beta[0] / beta[1]) if abs(beta[1]) > 1e-9 else None
    return {"intercept": float(beta[0]), "slope": float(beta[1]),
            "rho_zero_at_v": crossing,
            "note": ("the equilibrium manifold is the horizontal line rho = 0; "
                     "this fit says where a typical pool's agreement sits as a "
                     "function of the value, not the manifold's slope")}


def analyse(rows, label):
    c_levels = levels_fixed_effects(rows)
    c_diff = differences(rows)
    c_ceiling = levels_ceiling_controlled(rows)
    if c_levels is None:
        return None
    sigma_bar = float(np.mean([r["sigma"] for r in rows]))
    ci_levels = cluster_bootstrap(rows, levels_fixed_effects)
    ci_diff = cluster_bootstrap(rows, differences)
    ci_ceiling = cluster_bootstrap(rows, levels_ceiling_controlled)
    # The gain is built from the ceiling-controlled coupling when it exists,
    # because the raw one contains the arithmetic of the binary score ceiling.
    c_for_gain = c_ceiling if c_ceiling is not None else c_levels
    ci_for_gain = ci_ceiling if c_ceiling is not None else ci_levels
    gain = 1.0 + c_for_gain * H2 * sigma_bar
    gain_ci = None
    if ci_for_gain:
        gain_ci = [1.0 + ci_for_gain["ci_lo"] * H2 * sigma_bar,
                   1.0 + ci_for_gain["ci_hi"] * H2 * sigma_bar]
    return {
        "group": label,
        "n_rounds": len(rows),
        "n_runs": len({r["run"] for r in rows}),
        "mean_sigma": sigma_bar,
        "coupling_c_levels_run_fe": c_levels,
        "coupling_c_levels_ci": ci_levels,
        "coupling_c_differences": c_diff,
        "coupling_c_differences_ci": ci_diff,
        "coupling_c_ceiling_controlled": c_ceiling,
        "coupling_c_ceiling_controlled_ci": ci_ceiling,
        "gain_built_from": ("ceiling-controlled coupling" if c_ceiling is not None
                            else "raw coupling"),
        "differences_estimator_bias": differences_bias(rows),
        "loop_gain": gain,
        "loop_gain_ci": gain_ci,
        "runaway_predicted": bool(gain_ci and gain_ci[0] > 1.0),
        "settling_predicted": bool(gain_ci and gain_ci[1] < 1.0),
        "geometric_decay_check": geometric_decay_check(rows, gain),
    }


def main():
    runs = load()
    rows, dropped = build_rows(runs)
    usable = [r for r in rows if r["judge"] not in EXCLUDE]

    groups = {
        "all judges except oracle and judge-swap": usable,
        "co-evolving judge (self)": [r for r in usable if r["evolving"]],
        "frozen judge": [r for r in usable if not r["evolving"]],
    }
    for org in sorted({r["organism"] for r in usable}):
        groups[f"frozen judge, {org}"] = [
            r for r in usable if not r["evolving"] and r["organism"] == org]
        ev = [r for r in usable if r["evolving"] and r["organism"] == org]
        if len({r["run"] for r in ev}) >= 3:
            groups[f"co-evolving judge, {org}"] = ev

    results = {}
    for label, sub in groups.items():
        if len({r["run"] for r in sub}) < 3:
            continue
        out = analyse(sub, label)
        if out:
            results[label] = out

    payload = {
        "description": (
            "Measures the judge-drift coupling c = d(rho)/d(v) -- the "
            "Lande-Kirkpatrick trajectory slope -- and converts it into a "
            "per-round loop gain G = 1 + c*h^2*sigma. G > 1 is Fisherian "
            "runaway; G < 1 settles onto the rho = 0 manifold."
        ),
        "transmission_coefficient_used": H2,
        "excluded_judges": sorted(EXCLUDE),
        "rounds_dropped": dropped,
        "n_rounds_used": len(usable),
        "n_runs_used": len({r["run"] for r in usable}),
        "groups": results,
        "rho_nullcline": rho_nullcline(usable),
        "conventions": {
            "zero_spread_rounds": ("dropped: agreement is undefined when every "
                                   "candidate scores the same, and recording it "
                                   "as 0 would drag the coupling toward zero"),
            "estimator_biases": ("levels-with-run-FE attenuates c toward zero "
                                 "(noise in v) and carries a negative Nickell "
                                 "bias; the differences estimator is biased "
                                 "negative by mean reversion. Both are "
                                 "conservative for detecting c > 0."),
        },
    }
    OUT.write_text(json.dumps(payload, indent=2) + "\n")

    print(f"{len(usable)} rounds from {len({r['run'] for r in usable})} runs "
          f"(dropped {dropped['imputed_rho']} zero-spread, "
          f"{dropped['missing']} missing)\n")
    print(f"{'group':42s} {'runs':>5s} {'c raw':>22s} {'c ceiling-controlled':>22s} "
          f"{'gain G':>20s}")
    for label, r in results.items():
        ci = r["coupling_c_levels_ci"]
        gci = r["loop_gain_ci"]
        cc = r["coupling_c_ceiling_controlled"]
        cci = r["coupling_c_ceiling_controlled_ci"]
        cstr = (f"{r['coupling_c_levels_run_fe']:+.3f} "
                f"[{ci['ci_lo']:+.2f},{ci['ci_hi']:+.2f}]" if ci
                else f"{r['coupling_c_levels_run_fe']:+.3f}")
        ccstr = (f"{cc:+.3f} [{cci['ci_lo']:+.2f},{cci['ci_hi']:+.2f}]"
                 if cc is not None and cci else
                 (f"{cc:+.3f}" if cc is not None else "n/a"))
        gstr = (f"{r['loop_gain']:.3f} [{gci[0]:.2f},{gci[1]:.2f}]" if gci
                else f"{r['loop_gain']:.3f}")
        verdict = ("  RUNAWAY" if r["runaway_predicted"]
                   else "  SETTLES" if r["settling_predicted"] else "")
        print(f"{label:42s} {r['n_runs']:5d} {cstr:>22s} {ccstr:>22s} "
              f"{gstr:>20s}{verdict}")
    print()
    for label, r in results.items():
        b = r["differences_estimator_bias"]
        print(f"  {label}: differences estimator "
              f"{r['coupling_c_differences']:+.3f}"
              + (f", mean-reversion bias up to {b['bias_upper_bound_magnitude']:.3f} "
                 f"{b['direction']}" if b else ""))
    print()
    print("GEOMETRIC DECAY CHECK  |rho_t| / |rho_1|, observed vs G^(t-1)")
    for label, r in results.items():
        g = r.get("geometric_decay_check")
        if not g:
            continue
        bits = [f"r{t[-1]}: obs {v['observed_mean_ratio']:.2f} "
                f"vs pred {v['predicted_ratio']:.2f} (n={v['n_runs']})"
                for t, v in g.items()]
        print(f"  {label}: " + "  ".join(bits))
    print()
    nc = payload["rho_nullcline"]
    if nc:
        print(f"agreement vs value, between runs: rho = {nc['intercept']:+.3f} "
              f"{nc['slope']:+.3f}*v"
              + (f"  (crosses zero at v = {nc['rho_zero_at_v']:.3f})"
                 if nc["rho_zero_at_v"] is not None else ""))
    print(f"\nwrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
