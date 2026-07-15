"""A simple model built from the two gap factors, tested on interventions.

Writeup narrative (user directive 07-15): selection gap -> decomposition into
value spread x utilization -> a SIMPLE model for spread and utilization,
judged with fresh eyes on how well it predicts the intervention cells
(injection, invasion, format changes, self-judging erosion) rather than by
the older state-space / bake-off forecasting machinery.

THE MODEL. Everything a run needs is measured on its FIRST round's pool, then
the run is rolled forward with no further peeking:

  inputs (round-1 pool):  v0        measured value entering round 1
                          sigma_1   candidate value spread
                          rho_1     utilization (judge-score vs value corr)
                          s         supplier level = mean value of the
                                    co-generator's round-1 candidates
                          m         co-generator share of the pool (~0.5)
  dynamics (t = 1..N):
      pool_t = (1-m) * v_t + m * s          (self-only: pool_t = v_t)
      kept_t = pool_t + C * rho_1 * sigma_t (C = 0.96, the factorization)
      v_{t+1} = v_t + K * (kept_t - v_t)    (the movement association)
      sigma:  self-only   sigma_{t+1} = a + b * sigma_t
              mixed       sigma_t = g * |v_t - s| + d   (source separation)

K, (a, b), (g, d) are 2-parameter fits on the per-round records of
experiments/spread_util_unified.json, refit LEAVE-ONE-RUN-OUT so a predicted
run never touches its own fit. rho_1 held constant within a run (utilization
is ~a judge-cell property: between-cell variance share 0.82).

EVALUATION. Endpoint absolute error and mean per-round error vs a
persistence baseline (value stays at v0), split by composition; direction
hit-rate on the runs that actually moved; the predicted-vs-actual endpoint
table for every intervention cell by name.

OUTLIERS. (1) the largest per-round residuals of the raw movement
association drift ~ K*pull; (2) the largest endpoint misses of the rollout —
each named by cell so the writeup can discuss them honestly.

Run:  uv run python scripts/analysis_simple_model_rollout.py
Writes: experiments/simple_model_rollout.json.  numpy only.
"""
import json
import os
from collections import defaultdict

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
C = 0.96          # gap = C * rho * sigma (report_spread_util_unified.md)
MIX_SHARE = 0.5   # co-generator supplies half the pool in every mixed cell


def ols(x, y):
    x, y = np.asarray(x, float), np.asarray(y, float)
    if len(x) < 3 or np.std(x) < 1e-9:
        return None
    b, a = np.polyfit(x, y, 1)
    return float(b), float(a)


def load_runs():
    d = json.load(open(os.path.join(ROOT, "experiments/spread_util_unified.json")))
    runs = defaultdict(list)
    for r in d["records"]:
        runs[(r["cond"], r["seed"], r["source"])].append(r)
    out = []
    for key, recs in runs.items():
        recs = sorted(recs, key=lambda r: r["round"])
        if recs[0]["round"] != 1 or len(recs) < 2:
            continue  # need a round-1 measurement and something to predict
        if any(r.get("rho") is None for r in recs[:1]):
            continue  # no round-1 utilization (random arms) -> not modelable
        out.append((key, recs))
    return out


def slope_only_fit(rows):
    """K in drift = K * pull, no intercept (through the origin)."""
    x = np.array([r["pull"] for r in rows])
    y = np.array([r["drift"] for r in rows])
    return float((x * y).sum() / (x * x).sum())


def fit_scalars(train_rows):
    K = slope_only_fit([r for r in train_rows if r.get("pull") is not None])
    so = [r for r in train_rows if r["composition"] == "self-only"]
    pairs = defaultdict(dict)
    for r in so:
        pairs[(r["cond"], r["seed"], r["source"])][r["round"]] = r["spread"]
    xs, ys = [], []
    for rounds in pairs.values():
        for k in rounds:
            if k + 1 in rounds:
                xs.append(rounds[k]); ys.append(rounds[k + 1])
    sp = ols(xs, ys) or (0.9, 0.02)
    mixed = [r for r in train_rows
             if r["composition"] != "self-only" and r.get("source_sep") is not None]
    mx = ols([abs(r["value"] - r["cogen_mean"]) for r in mixed],
             [r["spread"] for r in mixed]) or (0.35, 0.2)
    return K, sp, mx


def rollout(recs, K, sp, mx):
    """Predict v after each round from round-1 measurements only."""
    r1 = recs[0]
    mixed = r1["composition"] != "self-only"
    v = r1["value"]
    sigma = r1["spread"]
    rho = r1["rho"]
    s = r1.get("cogen_mean")
    preds = []
    for t in range(len(recs)):
        if mixed and s is not None:
            sigma = max(0.0, mx[0] * abs(v - s) + mx[1]) if t > 0 else sigma
            pool = (1 - MIX_SHARE) * v + MIX_SHARE * s
        else:
            if t > 0:
                sigma = max(0.0, sp[0] * sigma + sp[1])
            pool = v
        kept = pool + C * rho * sigma
        v = float(np.clip(v + K * (kept - v), 0.0, 1.0))
        preds.append(v)
    return preds


def main():
    runs = load_runs()
    all_rows = [r for _, recs in runs for r in recs]

    per_run = []
    for key, recs in runs:
        train = [r for _, rr in runs if (_ != key) for r in rr]
        K, sp, mx = fit_scalars(train)
        preds = rollout(recs, K, sp, mx)
        truth = [r["value"] + r["drift"] for r in recs]   # v after each round
        v0 = recs[0]["value"]
        per_run.append(dict(
            cond=key[0], seed=key[1], source=key[2],
            organism=recs[0]["organism"], judge=recs[0]["judge"],
            format=recs[0]["format"], composition=recs[0]["composition"],
            n_rounds=len(recs), v0=round(v0, 3),
            rho1=recs[0]["rho"], sigma1=recs[0]["spread"],
            supplier=recs[0].get("cogen_mean"),
            pred=[round(p, 3) for p in preds],
            truth=[round(t, 3) for t in truth],
            endpoint_pred=round(preds[-1], 3), endpoint_true=round(truth[-1], 3),
            endpoint_abs_err=round(abs(preds[-1] - truth[-1]), 3),
            persistence_abs_err=round(abs(v0 - truth[-1]), 3),
            round_mae=round(float(np.mean([abs(p - t) for p, t in zip(preds, truth)])), 3),
        ))

    # aggregates
    def agg(rows):
        return dict(
            n=len(rows),
            endpoint_mae=round(float(np.mean([r["endpoint_abs_err"] for r in rows])), 3),
            persistence_mae=round(float(np.mean([r["persistence_abs_err"] for r in rows])), 3),
            round_mae=round(float(np.mean([r["round_mae"] for r in rows])), 3),
        )
    groups = {"all": per_run}
    for comp in ("self-only", "base-mixed", "peer-mixed"):
        groups[comp] = [r for r in per_run if r["composition"] == comp]
    for fam in ("OLMo", "Qwen"):
        groups[fam] = [r for r in per_run if r["organism"] == fam]
    aggregates = {k: agg(v) for k, v in groups.items() if v}

    # direction hit-rate on runs that actually moved (|true endpoint - v0| >= 0.15)
    moved = [r for r in per_run if abs(r["endpoint_true"] - r["v0"]) >= 0.15]
    hits = [r for r in moved
            if (r["endpoint_pred"] - r["v0"]) * (r["endpoint_true"] - r["v0"]) > 0
            and abs(r["endpoint_pred"] - r["v0"]) >= 0.05]
    direction = dict(n_moved=len(moved), n_direction_hits=len(hits),
                     hit_rate=round(len(hits) / len(moved), 3) if moved else None)

    # outliers 1: movement-association residuals (refit K on everything once)
    K_all = slope_only_fit([r for r in all_rows if r.get("pull") is not None])
    resid = sorted(all_rows,
                   key=lambda r: -abs(r["drift"] - K_all * r["pull"]))
    outlier_rounds = [dict(cond=r["cond"], seed=r["seed"], round=r["round"],
                           organism=r["organism"], judge=r["judge"],
                           composition=r["composition"],
                           pull=r["pull"], drift=r["drift"],
                           resid=round(r["drift"] - K_all * r["pull"], 3))
                      for r in resid[:12]]

    # outliers 2: worst rollout endpoint misses
    misses = sorted(per_run, key=lambda r: -r["endpoint_abs_err"])[:8]

    out = dict(
        description=__doc__.strip().split("\n")[0],
        model=dict(C=C, mix_share=MIX_SHARE,
                   inputs="round-1 pool only: v0, sigma_1, rho_1, supplier level",
                   fits="K (drift~pull, through origin), self-only spread AR, "
                        "mixed spread~|v-s|; all leave-one-run-out"),
        n_runs=len(per_run),
        aggregates=aggregates,
        direction=direction,
        interventions=[r for r in per_run if r["composition"] != "self-only"],
        outlier_rounds=outlier_rounds,
        worst_endpoint_misses=misses,
        per_run=per_run,
    )
    path = os.path.join(ROOT, "experiments/simple_model_rollout.json")
    with open(path, "w") as f:
        json.dump(out, f, indent=1)
    print(f"{len(per_run)} runs -> {path}")
    print("aggregates:", json.dumps(aggregates, indent=1))
    print("direction:", direction)
    print("worst misses:", [(m["cond"], m["seed"], m["endpoint_abs_err"]) for m in misses[:5]])
    print("top outlier rounds:", [(o["cond"], o["seed"], o["round"], o["resid"]) for o in outlier_rounds[:5]])


if __name__ == "__main__":
    main()
