"""The first off-target transmission column: what else moves, and through which channel?

The Price equation splits a change in a population mean into a selection term and
a transmission term. This project has characterised selection on the axis being
selected. This asks what happens to axes that were NOT selected on, and — more
usefully — whether their movement arrives through the selection channel or the
training channel.

THE IDENTIFYING IDEA. Per round, the pull on the selected axis decomposes into
two additive pieces that are only weakly correlated in this corpus (r = 0.16):

    pull  =  supply  +  gap
             ------     ---
             pool_mean - v      the candidate pool is not centred on the
                                organism's current value, so it pulls even
                                with no selection at all
             kept_mean - pool_mean   the selection differential

Both move the selected axis. They differ in what they imply for an off-target
axis B. If B moves because the JUDGE kept answers that happened to be high on B
too, B's movement should load on `gap` and not on `supply` — selection-mediated
spillover, which is predictable from a pure inference pass over the candidate
pool before any training happens. If B moves because the model moved and B came
along, it should load on both equally — transmission-mediated spillover, the
Price equation's second term, which no amount of candidate scoring can predict.

So fitting

    Δz_B  =  α + a·gap + b·supply

and comparing a with b separates the two channels. a ≈ b means "wherever the
model goes, B follows". a ≫ b means "the selector is dragging B".

ONE THING IS CLEAN AND ONE IS NOT. The usual objection in this corpus is that
`supply = pool_mean − v_t` shares measurement error with the on-target drift
`v_{t+1} − v_t`. Here the outcome is a DIFFERENT axis, measured by a different
probe, so that particular artefact does not exist.

But the comparison of a with b has its own bias, and it points the wrong way.
The gap is computed from candidate scores observed exactly given the pool, so it
carries no measurement error. Supply contains v_t, which does — and in this
corpus measurement noise is about 46% of the observed supply variance.
Attenuation therefore pushes b toward zero while leaving a alone, which
MANUFACTURES a > b out of nothing. Any uncorrected finding that "the selection
channel dominates" would be an artefact of that asymmetry.

So both are reported: the naive fit, and a fit that subtracts var(e) from the
supply-supply entry of the moment matrix, with var(e) taken from each round's
own recorded measurement standard error. The correction does NOT touch the
cross-moment with the outcome, because the off-target probe does not share e —
which is the difference from the on-target case.

THE AXES. Three off-target readouts exist per round in committed results, all
measured while a risk-preference axis was under selection:

    ev_belief_bias   signed belief bias about which gamble has the higher
                     expected value, from the balanced 12-item battery. Known
                     to co-move with preference on OLMo (r = 0.79) and not on
                     Qwen (−0.22).
    ev_numeric_est   the same beliefs asked as a number rather than a
                     comparison. Known to stay unbiased.
    stated_tolerance the model's own forced-choice statement about its risk
                     tolerance. Known to be near-immobile.

Three axes with three different documented behaviours is what makes this a
column worth fitting rather than a single coefficient.

THE JOIN IS VERIFIED, NOT ASSUMED. The off-target files key runs by
(grid, cond, seed) and store a trajectory of the ON-target value alongside each
off-target trajectory. Rows are matched to the unified corpus by (organism,
cond, seed, round) and then CHECKED: the on-target value must agree to within
tolerance. Rows that fail are dropped and counted, so a silent misalignment
shows up as a low match rate rather than as a result.

Writes experiments/offtarget_transmission_column.json.
"""

from __future__ import annotations

import json
import math
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
UNIFIED = ROOT / "experiments/spread_util_unified.json"
EV_BIAS = ROOT / "experiments/ev_bias_coupling.json"
SELFREPORT = ROOT / "experiments/selfreport_calibration_k2.json"
OUT = ROOT / "experiments/offtarget_transmission_column.json"

JOIN_TOLERANCE = 0.02   # the on-target value must agree this closely to join
BOOTSTRAP_DRAWS = 4000
SEED = 20260728

GRID_TO_ORGANISM = {"k2_olmo": "OLMo", "k1_qwen": "Qwen"}


def load_ontarget():
    """Per-round rows from the unified corpus, keyed for joining."""
    unified = json.loads(UNIFIED.read_text())
    rows = {}
    for rec in unified["records"]:
        if rec.get("gap") is None or rec.get("drift") is None:
            continue
        if rec.get("axis") != "risk":
            continue          # the off-target files are all from risk-axis runs
        key = (rec["organism"], rec["cond"], str(rec["seed"]), int(rec["round"]))
        # A (cond, seed) pair can appear in more than one source file. Keep the
        # first and record the collision rather than silently averaging.
        if key in rows:
            rows[key]["duplicate_sources"].append(rec["source"])
            continue
        rows[key] = {
            "organism": rec["organism"],
            "cond": rec["cond"],
            "seed": str(rec["seed"]),
            "round": int(rec["round"]),
            "source": rec["source"],
            "gap": float(rec["gap"]),
            "supply": float(rec["pool_mean"]) - float(rec["value"]),
            "value": float(rec["value"]),
            "ontarget_drift": float(rec["drift"]),
            "judge": rec["judge"],
            "value_se": rec.get("value_measurement_se"),
            "duplicate_sources": [],
        }
    return rows


def offtarget_series():
    """(organism, cond, seed) -> {axis: trajectory}, plus the on-target check series."""
    out = defaultdict(dict)
    ev = json.loads(EV_BIAS.read_text())
    for run in ev["runs"]:
        organism = GRID_TO_ORGANISM.get(run["grid"])
        if organism is None:
            continue
        key = (organism, run["cond"], str(run["seed"]))
        out[key]["_ontarget_check"] = run["traj"]
        out[key]["ev_belief_bias"] = run["bias"]
        out[key]["ev_numeric_est"] = run["log_est"]

    sr = json.loads(SELFREPORT.read_text())
    rollouts = sr["rollouts"]
    rollouts = rollouts if isinstance(rollouts, list) else list(rollouts.values())
    for run in rollouts:
        # this file is the K2 (OLMo) chassis
        key = ("OLMo", run["cond"], str(run["seed"]))
        if "_ontarget_check" not in out[key]:
            out[key]["_ontarget_check"] = run["traj"]
        out[key]["stated_tolerance"] = run["sr"]
    return dict(out)


def build_panel():
    ontarget = load_ontarget()
    series = offtarget_series()

    rows, join_stats = [], {"attempted": 0, "joined": 0, "value_mismatch": 0,
                            "short_series": 0, "no_series": 0}
    for key, rec in ontarget.items():
        organism, cond, seed, rnd = key
        run_series = series.get((organism, cond, seed))
        join_stats["attempted"] += 1
        if run_series is None:
            join_stats["no_series"] += 1
            continue
        check = run_series.get("_ontarget_check") or []
        # unified round t reads the value BEFORE that round, i.e. index t-1
        if len(check) <= rnd:
            join_stats["short_series"] += 1
            continue
        if abs(float(check[rnd - 1]) - rec["value"]) > JOIN_TOLERANCE:
            join_stats["value_mismatch"] += 1
            continue

        deltas = {}
        for axis, traj in run_series.items():
            if axis.startswith("_") or traj is None:
                continue
            if len(traj) <= rnd:
                continue
            # A missing readout at either end makes this round's change
            # undefined for that axis; other axes on the same row survive.
            before, after = traj[rnd - 1], traj[rnd]
            if before is None or after is None:
                continue
            deltas[axis] = float(after) - float(before)
        if not deltas:
            continue
        join_stats["joined"] += 1
        rows.append({**rec, "offtarget_delta": deltas,
                     "run": (organism, cond, seed)})
    return rows, join_stats


# --------------------------------------------------------------------------- #


def ols(X, y):
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    return beta


def fit_axis(rows, axis):
    sub = [r for r in rows if axis in r["offtarget_delta"]]
    if len(sub) < 15:
        return {"axis": axis, "n": len(sub), "insufficient": True}

    gap = np.array([r["gap"] for r in sub])
    supply = np.array([r["supply"] for r in sub])
    y = np.array([r["offtarget_delta"][axis] for r in sub])
    ontarget = np.array([r["ontarget_drift"] for r in sub])
    if np.var(gap) < 1e-12 or np.var(y) < 1e-12:
        return {"axis": axis, "n": len(sub), "degenerate": True}

    ses = [r.get("value_se") for r in sub if r.get("value_se") is not None]
    var_e = float(np.mean([se ** 2 for se in ses])) if ses else 0.0

    def channels(sample_idx, corrected=False):
        X = np.column_stack([np.ones(len(sample_idx)), gap[sample_idx],
                             supply[sample_idx]])
        yy = y[sample_idx]
        if not corrected:
            return ols(X, yy)
        n = len(sample_idx)
        XtX = X.T @ X / n
        Xty = X.T @ yy / n
        XtX = XtX.copy()
        XtX[2, 2] -= var_e          # only var(supply) is inflated
        try:
            return np.linalg.solve(XtX, Xty)
        except np.linalg.LinAlgError:
            return None

    idx_all = np.arange(len(sub))
    beta = channels(idx_all)
    beta_corrected = channels(idx_all, corrected=True)

    Xr = np.column_stack([np.ones(len(sub)), ontarget])
    beta_reduced = ols(Xr, y)
    resid_r = y - Xr @ beta_reduced

    by_run = defaultdict(list)
    for i, r in enumerate(sub):
        by_run[r["run"]].append(i)
    keys = list(by_run)
    rng = np.random.default_rng(SEED)
    draws = {"gap": [], "supply": [], "difference": [], "ontarget": [],
             "gap_corrected": [], "supply_corrected": [],
             "difference_corrected": []}
    for _ in range(BOOTSTRAP_DRAWS):
        take = np.concatenate([by_run[keys[i]]
                               for i in rng.integers(0, len(keys), len(keys))])
        if np.var(gap[take]) < 1e-12 or np.var(supply[take]) < 1e-12:
            continue
        try:
            b = channels(take)
            Xb = np.column_stack([np.ones(len(take)), ontarget[take]])
            br = ols(Xb, y[take])
        except np.linalg.LinAlgError:
            continue
        draws["gap"].append(b[1])
        draws["supply"].append(b[2])
        draws["difference"].append(b[1] - b[2])
        draws["ontarget"].append(br[1])
        bc = channels(take, corrected=True)
        if bc is not None and np.all(np.isfinite(bc)):
            draws["gap_corrected"].append(bc[1])
            draws["supply_corrected"].append(bc[2])
            draws["difference_corrected"].append(bc[1] - bc[2])

    def ci(name):
        arr = np.array(draws[name])
        if len(arr) < 100:
            return None
        return [float(np.percentile(arr, 2.5)), float(np.percentile(arr, 97.5))]

    axis_sd = float(np.std(y, ddof=1))
    return {
        "axis": axis,
        "n": len(sub),
        "n_runs": len(keys),
        "axis_sd_of_round_change": axis_sd,
        "gap_coefficient": float(beta[1]),
        "gap_ci": ci("gap"),
        "supply_coefficient": float(beta[2]),
        "supply_ci": ci("supply"),
        "gap_minus_supply": float(beta[1] - beta[2]),
        "gap_minus_supply_ci": ci("difference"),
        "measurement_variance_in_supply": var_e,
        "noise_share_of_supply_variance": float(var_e / np.var(supply))
                                          if np.var(supply) > 0 else None,
        "gap_coefficient_corrected": (float(beta_corrected[1])
                                      if beta_corrected is not None else None),
        "supply_coefficient_corrected": (float(beta_corrected[2])
                                         if beta_corrected is not None else None),
        "gap_minus_supply_corrected": (float(beta_corrected[1] - beta_corrected[2])
                                       if beta_corrected is not None else None),
        "gap_minus_supply_corrected_ci": ci("difference_corrected"),
        "channels_differ_naive": (lambda c: bool(c and (c[0] > 0 or c[1] < 0)))(
            ci("difference")),
        "channels_differ_corrected": (
            lambda c: bool(c and (c[0] > 0 or c[1] < 0)))(
            ci("difference_corrected")),
        "reduced_form_on_ontarget_drift": float(beta_reduced[1]),
        "reduced_form_ci": ci("ontarget"),
        "reduced_form_r2": float(1 - resid_r.var() / y.var()) if y.var() > 0
                           else None,
        "gap_coefficient_in_axis_sds": float(beta[1] / axis_sd) if axis_sd > 0
                                       else None,
    }


def main():
    rows, join_stats = build_panel()
    axes = sorted({a for r in rows for a in r["offtarget_delta"]})

    result = {
        "description": (
            "First off-target transmission column. For each off-target axis, "
            "splits its per-round movement into the part loading on the "
            "selection differential (selection-mediated spillover, predictable "
            "from the candidate pool) and the part loading on the pool-offset "
            "supply term (transmission-mediated spillover, the Price equation's "
            "second term). All rows come from risk-axis selection runs."
        ),
        "join": {
            **join_stats,
            "tolerance": JOIN_TOLERANCE,
            "note": ("rows are joined on (organism, cond, seed, round) and then "
                     "verified by requiring the on-target value stored in the "
                     "off-target file to match the unified corpus; failures are "
                     "dropped and counted"),
        },
        "n_rows": len(rows),
        "n_runs": len({r["run"] for r in rows}),
        "duplicate_source_rows": sum(1 for r in rows if r["duplicate_sources"]),
        "pooled": {a: fit_axis(rows, a) for a in axes},
        "by_organism": {
            org: {a: fit_axis([r for r in rows if r["organism"] == org], a)
                  for a in axes}
            for org in sorted({r["organism"] for r in rows})
        },
        "settings": {"bootstrap_draws": BOOTSTRAP_DRAWS,
                     "clustering": "whole runs, keyed by (organism, cond, seed)"},
    }
    OUT.write_text(json.dumps(result, indent=2) + "\n")

    print("JOIN")
    for k, v in join_stats.items():
        print(f"  {k}: {v}")
    print(f"  -> {len(rows)} rows from {len({r['run'] for r in rows})} runs")
    print()

    def show(block, label):
        print(label)
        for axis, f in block.items():
            if f.get("insufficient") or f.get("degenerate"):
                print(f"  {axis:18s} n={f['n']:3d}  not fitted")
                continue
            g, s = f["gap_ci"], f["supply_ci"]
            d = f["gap_minus_supply_ci"]
            print(f"  {axis:18s} n={f['n']:3d} runs={f['n_runs']:2d}  "
                  f"gap={f['gap_coefficient']:+.3f}"
                  + (f" [{g[0]:+.3f},{g[1]:+.3f}]" if g else "")
                  + f"  supply={f['supply_coefficient']:+.3f}"
                  + (f" [{s[0]:+.3f},{s[1]:+.3f}]" if s else ""))
            print(f"  {'':18s} naive     gap−supply={f['gap_minus_supply']:+.3f}"
                  + (f" [{d[0]:+.3f},{d[1]:+.3f}]" if d else "")
                  + ("  DIFFER" if f["channels_differ_naive"] else ""))
            dc = f["gap_minus_supply_corrected_ci"]
            print(f"  {'':18s} corrected gap={f['gap_coefficient_corrected']:+.3f}"
                  f"  supply={f['supply_coefficient_corrected']:+.3f}"
                  f"  diff={f['gap_minus_supply_corrected']:+.3f}"
                  + (f" [{dc[0]:+.3f},{dc[1]:+.3f}]" if dc else "")
                  + ("  DIFFER" if f["channels_differ_corrected"] else "  same channel"))
            print(f"  {'':18s} reduced form on on-target drift="
                  f"{f['reduced_form_on_ontarget_drift']:+.3f}"
                  f" (R²={f['reduced_form_r2']:.3f})")
        print()

    show(result["pooled"], "POOLED")
    for org, block in result["by_organism"].items():
        show(block, f"ORGANISM = {org}")
    print(f"wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
