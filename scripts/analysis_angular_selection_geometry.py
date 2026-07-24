"""Angular (arcsine) geometry of the selection loop.

MOTIVATION.  The program's endpoint model iterates

    v_{t+1} = v_t + rho * sigma

from round-1 measurements, holding BOTH rho and sigma frozen at their
round-1 values and clipping each step into [0, 1].  Freezing sigma is
known to be wrong in a specific way: on a binary-scored axis the offered
within-prompt variance is bounded by the pool mean q via the binomial
identity V_within = q(1-q) - V_between (verified elsewhere in this repo
to ~1e-6), so sigma MUST shrink as the value approaches either rail.  The
clipping step is an ad-hoc patch over exactly that mis-specification.

HYPOTHESIS.  Write sigma_t = c * sqrt(v_t (1 - v_t)) for a constant c
(the fraction of the binomial ceiling the generator actually realizes).
Then the per-round move is

    dv = rho * c * sqrt(v (1 - v)),

which is a separable ODE.  Under the angular (arcsine / Fisher
variance-stabilizing) transform

    phi = 2 * arcsin(sqrt(v))         in [0, pi],
    dphi/dv = 1 / sqrt(v (1 - v)),

it becomes

    dphi = rho * c   =   a CONSTANT per round.

So the prediction is: the value moves at constant speed in phi, the
trajectory is a straight line in phi, the rails v=0 and v=1 are the
finite-time boundaries phi=0 and phi=pi (no clipping needed), and the
number of rounds to fixation is (pi - phi_0) / (rho c) in closed form.

WHAT THIS SCRIPT TESTS (all on the committed 340-round table, no new data):

  T1  sigma = c * sqrt(q(1-q))?  Estimate c, report fit quality, and check
      whether c is stable across family / axis / composition.
  T2  Is the per-round move more nearly constant in phi than in v?
      Measured WITHIN runs, so it is a statement about trajectory shape.
  T3  One-step-ahead forecast bake-off, scored in v-space MAE.
  T4  Endpoint forecast bake-off from round-1 measurements only, scored
      in v-space MAE.  This is the head-to-head that matters: model A
      (frozen sigma + clip) versus model B (constant angular speed) given
      IDENTICAL round-1 inputs.
  T5  Closed-form time-to-fixation check on runs that actually railed.

Conventions are inherited from analysis_spread_util_unified.py, whose
output experiments/spread_util_unified.json is the sole input:
spread = mean over prompts of within-prompt population SD (ddof=0);
rho = mean within-prompt Pearson corr of judge score with value score;
gap = kept mean - pool mean; pull = kept mean - v_t; drift = v_{t+1} - v_t.
"""

import json
import math
import statistics
from collections import defaultdict

SRC = "experiments/spread_util_unified.json"
OUT = "experiments/angular_selection_geometry.json"

# Runs are identified by everything that is held fixed along a trajectory.
RUN_KEY = ("organism", "axis", "cond", "seed", "source", "judge", "format", "composition")


def phi(v):
    """Angular transform, in [0, pi]. Clamped for numerical safety only."""
    v = min(1.0, max(0.0, v))
    return 2.0 * math.asin(math.sqrt(v))


def inv_phi(p):
    p = min(math.pi, max(0.0, p))
    return math.sin(p / 2.0) ** 2


def ols(xs, ys):
    """Ordinary least squares with intercept."""
    n = len(xs)
    if n < 3:
        return None
    mx, my = sum(xs) / n, sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    if sxx == 0:
        return None
    slope = sxy / sxx
    intercept = my - slope * mx
    syy = sum((y - my) ** 2 for y in ys)
    r = sxy / math.sqrt(sxx * syy) if sxx > 0 and syy > 0 else 0.0
    return {"slope": round(slope, 4), "intercept": round(intercept, 4),
            "r": round(r, 4), "n": n}


def ols_through_origin(xs, ys):
    """Slope only; the physical models here have no intercept."""
    num = sum(x * y for x, y in zip(xs, ys))
    den = sum(x * x for x in xs)
    if den == 0:
        return None
    slope = num / den
    resid = [y - slope * x for x, y in zip(xs, ys)]
    ss_res = sum(r * r for r in resid)
    my = sum(ys) / len(ys)
    ss_tot = sum((y - my) ** 2 for y in ys)
    return {"slope": round(slope, 4), "n": len(xs),
            "r2_vs_mean": round(1 - ss_res / ss_tot, 4) if ss_tot > 0 else None}


def mae(errs):
    return round(sum(abs(e) for e in errs) / len(errs), 4) if errs else None


def load_runs():
    recs = json.load(open(SRC))["records"]
    runs = defaultdict(list)
    for r in recs:
        runs[tuple(r.get(k) for k in RUN_KEY)].append(r)
    for k in runs:
        runs[k].sort(key=lambda r: r["round"])
    return recs, runs


def t1_binomial_spread(recs):
    """sigma = c * sqrt(q(1-q)) on binary-scored rounds."""
    out = {"definition": "spread regressed on sqrt(pool_mean*(1-pool_mean)), "
                         "binary-scored rounds only; c = slope through origin"}
    binary = [r for r in recs if r.get("binary_score_fraction") == 1.0]
    out["n_binary_rounds"] = len(binary)

    def fit(rows, label):
        xs = [math.sqrt(max(0.0, r["pool_mean"] * (1 - r["pool_mean"]))) for r in rows]
        ys = [r["spread"] for r in rows]
        if len(rows) < 5:
            return None
        d = {"through_origin": ols_through_origin(xs, ys), "with_intercept": ols(xs, ys)}
        d["mean_realized_fraction"] = round(
            statistics.mean([y / x for x, y in zip(xs, ys) if x > 0.05]), 4)
        return d

    out["pooled"] = fit(binary, "pooled")
    by = {}
    for key, sel in [
        ("qwen", lambda r: r["organism"] == "Qwen"),
        ("olmo", lambda r: r["organism"] == "OLMo"),
        ("axis:risk", lambda r: r["axis"] == "risk"),
        ("axis:selfreport", lambda r: r["axis"] != "risk"),
        ("self-only", lambda r: r["composition"] == "self-only"),
        ("base-mixed", lambda r: r["composition"] == "base-mixed"),
        ("peer-mixed", lambda r: r["composition"] == "peer-mixed"),
    ]:
        rows = [r for r in binary if sel(r)]
        f = fit(rows, key)
        if f:
            by[key] = f
    out["by_slice"] = by
    return out


def t2_constant_speed(runs):
    """Within a run, is the step more nearly constant in phi than in v?

    For each run with >=3 logged transitions we ask: how well does a single
    per-run constant step describe the trajectory?  We fit the constant in
    each coordinate, then score BOTH in v-space so the comparison is fair.
    """
    out = {"definition": "per-run constant-step fit, scored in v-space MAE; "
                         ">=3 transitions required"}
    rows = []
    for key, rs in runs.items():
        steps = [(r["value"], r["value"] + r["drift"]) for r in rs]
        if len(steps) < 3:
            continue
        # constant step in v. Clipped to [0,1] -- without the clip the linear
        # model is allowed to predict impossible values, which would flatter
        # the angular model for a reason that has nothing to do with geometry.
        dv_bar = statistics.mean(b - a for a, b in steps)
        err_v = [min(1.0, max(0.0, a + dv_bar)) - b for a, b in steps]
        # constant step in phi, mapped back to v
        dphi_bar = statistics.mean(phi(b) - phi(a) for a, b in steps)
        err_phi = [inv_phi(phi(a) + dphi_bar) - b for a, b in steps]
        rows.append({
            "run": "|".join(str(x) for x in key),
            "n_steps": len(steps),
            "start": round(steps[0][0], 4),
            "end": round(steps[-1][1], 4),
            "mae_const_v": mae(err_v),
            "mae_const_phi": mae(err_phi),
            "dphi_bar": round(dphi_bar, 4),
            "dv_bar": round(dv_bar, 4),
        })
    out["n_runs"] = len(rows)
    if rows:
        out["mean_mae_const_v"] = round(statistics.mean(r["mae_const_v"] for r in rows), 4)
        out["mean_mae_const_phi"] = round(statistics.mean(r["mae_const_phi"] for r in rows), 4)
        wins = sum(1 for r in rows if r["mae_const_phi"] < r["mae_const_v"])
        out["runs_where_phi_wins"] = wins
        out["runs_total"] = len(rows)
        # restrict to runs that actually moved, where shape is discernible
        movers = [r for r in rows if abs(r["end"] - r["start"]) > 0.15]
        if movers:
            out["movers_only"] = {
                "n": len(movers),
                "mean_mae_const_v": round(statistics.mean(r["mae_const_v"] for r in movers), 4),
                "mean_mae_const_phi": round(statistics.mean(r["mae_const_phi"] for r in movers), 4),
                "phi_wins": sum(1 for r in movers if r["mae_const_phi"] < r["mae_const_v"]),
            }
    out["per_run"] = sorted(rows, key=lambda r: -abs(r["end"] - r["start"]))[:25]
    return out


def t3_one_step(recs, c_global):
    """One-step-ahead: does the angular form predict next value better?"""
    out = {"definition": "one-step forecasts of v_{t+1}, all scored in v-space MAE; "
                         "rounds with logged rho and binary scoring"}
    rows = [r for r in recs if r.get("binary_score_fraction") == 1.0 and r.get("rho") is not None]
    err = defaultdict(list)
    for r in rows:
        v, nxt, rho, sig = r["value"], r["value"] + r["drift"], r["rho"], r["spread"]
        err["persistence"].append(v - nxt)
        # A: linear step with the round's own measured spread, clipped
        err["linear_measured_sigma"].append(min(1, max(0, v + rho * sig)) - nxt)
        # B: angular step with the round's own measured spread
        s = math.sqrt(max(1e-9, v * (1 - v)))
        err["angular_measured_sigma"].append(inv_phi(phi(v) + rho * sig / s) - nxt)
        # C: angular step with spread REPLACED by the global binomial law
        err["angular_binomial_sigma"].append(inv_phi(phi(v) + rho * c_global) - nxt)
        # D: LINEAR step with the binomial spread law. This isolates the two
        # separate ideas: D vs A tests whether predicting spread from the value
        # beats measuring it; C vs D tests whether the angular geometry adds
        # anything once the spread law is in place.
        err["linear_binomial_sigma"].append(
            min(1, max(0, v + rho * c_global * s)) - nxt)
    out["n"] = len(rows)
    out["mae"] = {k: mae(v) for k, v in err.items()}
    return out


def t4_endpoint(runs, c_global):
    """Endpoint from round-1 measurements only. The head-to-head."""
    out = {"definition": "iterate from round 1 to the observed final round; "
                         "identical round-1 inputs for models A and C; "
                         "scored as |predicted - observed final value|"}
    rows = []
    for key, rs in runs.items():
        if len(rs) < 2:
            continue
        r1 = rs[0]
        v1, rho1, sig1 = r1["value"], r1["rho"], r1["spread"]
        if rho1 is None:
            continue
        steps = len(rs)
        observed = rs[-1]["value"] + rs[-1]["drift"]

        # A: current program model - frozen sigma, linear step, clip each step
        v = v1
        for _ in range(steps):
            v = min(1.0, max(0.0, v + rho1 * sig1))
        pred_a = v

        # B: frozen sigma but angular step, run-specific speed from round 1
        s1 = math.sqrt(max(1e-9, v1 * (1 - v1)))
        speed_run = rho1 * sig1 / s1
        pred_b = inv_phi(phi(v1) + steps * speed_run)

        # C: angular step with the GLOBAL binomial constant (one fewer run input)
        pred_c = inv_phi(phi(v1) + steps * rho1 * c_global)

        rows.append({
            "run": "|".join(str(x) for x in key),
            "rounds": steps,
            "v1": round(v1, 4), "rho1": round(rho1, 4), "sigma1": round(sig1, 4),
            "observed": round(observed, 4),
            "persistence": round(v1, 4),
            "A_frozen_sigma_clip": round(pred_a, 4),
            "B_angular_run_speed": round(pred_b, 4),
            "C_angular_global_c": round(pred_c, 4),
        })
    out["n_runs"] = len(rows)
    for name in ["persistence", "A_frozen_sigma_clip", "B_angular_run_speed", "C_angular_global_c"]:
        out.setdefault("mae", {})[name] = mae([r[name] - r["observed"] for r in rows])
    # head-to-head win counts A vs B (identical inputs)
    out["A_vs_B"] = {
        "B_better": sum(1 for r in rows
                        if abs(r["B_angular_run_speed"] - r["observed"])
                        < abs(r["A_frozen_sigma_clip"] - r["observed"])),
        "A_better": sum(1 for r in rows
                        if abs(r["A_frozen_sigma_clip"] - r["observed"])
                        < abs(r["B_angular_run_speed"] - r["observed"])),
        "tied": sum(1 for r in rows
                    if abs(r["A_frozen_sigma_clip"] - r["observed"])
                    == abs(r["B_angular_run_speed"] - r["observed"])),
    }
    # where the models disagree most
    out["largest_disagreements"] = sorted(
        rows, key=lambda r: -abs(r["A_frozen_sigma_clip"] - r["B_angular_run_speed"]))[:15]
    out["per_run"] = rows
    return out


def t5_time_to_fixation(runs, c_global):
    """Closed form: rounds to a rail = angular distance / angular speed."""
    out = {"definition": "for runs that reached within 0.02 of a rail, compare the "
                         "observed round at which they railed with (pi-phi_0)/speed "
                         "or phi_0/speed, using round-1 rho and the global c"}
    rows = []
    for key, rs in runs.items():
        if len(rs) < 2 or rs[0].get("rho") is None:
            continue
        traj = [(r["round"], r["value"]) for r in rs]
        traj.append((rs[-1]["round"] + 1, rs[-1]["value"] + rs[-1]["drift"]))
        railed_at = None
        for rd, v in traj[1:]:
            if v >= 0.98 or v <= 0.02:
                railed_at = (rd, 1.0 if v >= 0.98 else 0.0)
                break
        if railed_at is None:
            continue
        v1, rho1 = rs[0]["value"], rs[0]["rho"]
        speed = rho1 * c_global
        if abs(speed) < 1e-6:
            continue
        p0 = phi(v1)
        target = math.pi if railed_at[1] == 1.0 else 0.0
        predicted_rounds = (target - p0) / speed
        rows.append({
            "run": "|".join(str(x) for x in key),
            "rail": railed_at[1],
            "observed_round_railed": railed_at[0] - rs[0]["round"],
            "predicted_rounds": round(predicted_rounds, 2),
            "v1": round(v1, 4), "rho1": round(rho1, 4),
            "direction_correct": predicted_rounds > 0,
        })
    out["n_railed_runs"] = len(rows)
    if rows:
        ok = [r for r in rows if r["direction_correct"]]
        out["direction_correct_count"] = len(ok)
        if ok:
            out["mae_rounds"] = round(
                statistics.mean(abs(r["predicted_rounds"] - r["observed_round_railed"]) for r in ok), 2)
    out["per_run"] = rows
    return out


def main():
    recs, runs = load_runs()
    result = {
        "description": "Angular (arcsine) geometry of selection-loop value dynamics: "
                       "tests whether the value moves at constant speed in "
                       "phi = 2*arcsin(sqrt(v)), which follows from binomial "
                       "candidate spread plus the sigma*rho selection rule.",
        "source": SRC,
        "n_records": len(recs),
        "n_runs": len(runs),
    }
    result["T1_binomial_spread"] = t1_binomial_spread(recs)
    c_global = result["T1_binomial_spread"]["pooled"]["through_origin"]["slope"]
    result["c_global_used"] = c_global
    result["T2_constant_speed"] = t2_constant_speed(runs)
    result["T3_one_step"] = t3_one_step(recs, c_global)
    result["T4_endpoint"] = t4_endpoint(runs, c_global)
    result["T5_time_to_fixation"] = t5_time_to_fixation(runs, c_global)

    with open(OUT, "w") as f:
        json.dump(result, f, indent=1)

    # console summary
    print(f"records={len(recs)} runs={len(runs)}  c_global={c_global}")
    print("\nT1 sigma = c*sqrt(q(1-q)):", json.dumps(result["T1_binomial_spread"]["pooled"], indent=1))
    print("\nT2 constant-speed (v-space MAE):",
          json.dumps({k: v for k, v in result["T2_constant_speed"].items() if k != "per_run"}, indent=1))
    print("\nT3 one-step MAE:", json.dumps(result["T3_one_step"], indent=1))
    print("\nT4 endpoint MAE:", json.dumps({k: v for k, v in result["T4_endpoint"].items()
                                            if k not in ("per_run", "largest_disagreements")}, indent=1))
    print("\nT5 time-to-fixation:", json.dumps({k: v for k, v in result["T5_time_to_fixation"].items()
                                                if k != "per_run"}, indent=1))


if __name__ == "__main__":
    main()
