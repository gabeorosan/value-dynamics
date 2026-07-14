"""Is judge-generator TASTE ALIGNMENT a better runaway predictor than the raw
selection gap? (docs/ANALYSIS_LEDGER.md; user proposal 07-14: "the degree to
which the way the judge decides among answers with value spread is correlated
with the value".)

Decomposition: under keep-top-2-of-6 selection the expected kept-minus-pool
gap factorizes as  gap ~= c * rho * sigma  with
  rho   = mean within-item corr(judge score, candidate value)   [alignment]
  sigma = mean within-item candidate-value SD                   [supply]
  c     = order-statistics constant (~0.95 if scores ~ Gaussian)
The raw gap conflates the stable pair property (rho) with supply and noise.

Tests, on every K1/K2 rollout with logged judge scores:
  1. FACTORIZATION: regress realized gap on rho*sigma across all rounds
     (slope ~ c, r tells how well the product explains the gap).
  2. PERSISTENCE: lag-1 autocorrelation of rho vs of gap across rounds
     (the stabler quantity is the better state variable).
  3. EARLY-WARNING: from ROUND-1 measures only (rho_1, sigma_1, gap_1,
     rho_1*sigma_1), correlate with the run's REMAINING drift (pool_end
     minus pool_1) and rank the AUC-style separation of the two frozen_base
     runaways from the four settled runs.

Usage: uv run python scripts/analysis_taste_alignment_predictor.py
Writes experiments/taste_alignment_predictor.json and prints the tables.
"""

import glob
import json
import math
import os
import statistics as st

FILES = [
    "experiments/kaggle/kaggle_k2_olmo_inversion/output_controls/k2_olmo_inversion_kaggle_controls.json",
    "experiments/kaggle/kaggle_k2_olmo_inversion_conf/output/k2_conf_v1_seeds12_partial.json",
    "experiments/kaggle/kaggle_k2_olmo_inversion_conf/output/k2_olmo_inversion_kaggle_conf_v2.json",
    "experiments/kaggle/kaggle_k2_olmo_inversion_base012/output/k2_olmo_inversion_kaggle_base012.json",
    "experiments/cerebrium_k2/output/k2_cerebrium_seed0_complete.json",
    "experiments/kaggle/kaggle_k1_qwen_anchor_grid/output/k1_qwen_anchor.json",
]


def mean(x):
    return sum(x) / len(x) if x else None


def corr(a, b):
    if len(a) < 3:
        return None
    ma, mb = mean(a), mean(b)
    sa = math.sqrt(sum((x - ma) ** 2 for x in a))
    sb = math.sqrt(sum((y - mb) ** 2 for y in b))
    if sa == 0 or sb == 0:
        return None
    return sum((x - ma) * (y - mb) for x, y in zip(a, b)) / (sa * sb)


def main():
    runs = []
    for f in FILES:
        if not os.path.exists(f):
            continue
        grid = "k1_qwen" if "k1_qwen" in f else "k2_olmo"
        d = json.load(open(f))
        for seed in d:
            if seed.startswith("_"):
                continue
            for cond, rec in d[seed].items():
                rr = rec.get("rounds_raw")
                if not rr or len(rr) < 4:
                    continue
                rounds = []
                for rnd in rr:
                    items = [it for it in rnd
                             if isinstance(it.get("scores_arm"), list)
                             and isinstance(it.get("cand_risk"), list)
                             and len(it["scores_arm"]) == len(it["cand_risk"]) >= 3]
                    if not items:
                        break
                    rhos = [corr(it["scores_arm"], it["cand_risk"]) for it in items]
                    rhos = [r for r in rhos if r is not None]
                    pool = mean([mean(it["cand_risk"]) for it in items])
                    gap = mean([mean([it["cand_risk"][i] for i in it["kept_idx"]])
                                - mean(it["cand_risk"]) for it in items])
                    sigma = mean([st.pstdev(it["cand_risk"]) for it in items])
                    rounds.append(dict(rho=mean(rhos), sigma=sigma, gap=gap, pool=pool))
                if len(rounds) < 4 or any(r["rho"] is None for r in rounds):
                    continue
                runs.append(dict(grid=grid, cond=cond, seed=seed, rounds=rounds,
                                 end=rounds[-1]["pool"],
                                 remaining_drift_after_r1=rounds[-1]["pool"] - rounds[0]["pool"]))

    # 1) factorization: gap vs rho*sigma over all rounds
    xs = [r0["rho"] * r0["sigma"] for r in runs for r0 in r["rounds"]]
    ys = [r0["gap"] for r in runs for r0 in r["rounds"]]
    mg, md = mean(xs), mean(ys)
    sxx = sum((x - mg) ** 2 for x in xs)
    slope = sum((x - mg) * (y - md) for x, y in zip(xs, ys)) / sxx
    fac_r = corr(xs, ys)

    # 2) persistence: lag-1 autocorr of rho vs gap
    def lag1(key):
        a, b = [], []
        for r in runs:
            for i in range(len(r["rounds"]) - 1):
                a.append(r["rounds"][i][key])
                b.append(r["rounds"][i + 1][key])
        return corr(a, b)
    rho_ar, gap_ar, sig_ar = lag1("rho"), lag1("gap"), lag1("sigma")

    # 2b) next-gap forecasting: does the alignment product beat the gap at
    # predicting the NEXT round's gap (the running-monitor question)?
    a_ps, a_g, b_next = [], [], []
    for r in runs:
        for i in range(len(r["rounds"]) - 1):
            a_ps.append(r["rounds"][i]["rho"] * r["rounds"][i]["sigma"])
            a_g.append(r["rounds"][i]["gap"])
            b_next.append(r["rounds"][i + 1]["gap"])
    nextgap = dict(rho_sigma_to_nextgap=round(corr(a_ps, b_next), 3),
                   gap_to_nextgap=round(corr(a_g, b_next), 3))

    # 3) early warning from round-1 only
    preds = {"rho_1": lambda r: r["rounds"][0]["rho"],
             "sigma_1": lambda r: r["rounds"][0]["sigma"],
             "gap_1": lambda r: r["rounds"][0]["gap"],
             "rho_x_sigma_1": lambda r: r["rounds"][0]["rho"] * r["rounds"][0]["sigma"]}
    early = {}
    for grid in ("k2_olmo", "k1_qwen"):
        rs = [r for r in runs if r["grid"] == grid]
        early[grid] = {name: round(corr([fn(r) for r in rs],
                                        [r["remaining_drift_after_r1"] for r in rs]), 3)
                       for name, fn in preds.items()}
    fb = [r for r in runs if r["grid"] == "k2_olmo" and r["cond"] == "frozen_base"]
    runaway_sep = {}
    for name, fn in preds.items():
        vals = sorted(fb, key=fn, reverse=True)
        ranks = [i + 1 for i, r in enumerate(vals) if r["end"] > 0.4]
        runaway_sep[name] = dict(runaway_ranks_of_6=ranks,
                                 vals_sorted=[(v["seed"], round(fn(v), 3), round(v["end"], 2))
                                              for v in vals])

    out = dict(factorization=dict(slope=round(slope, 3), r=round(fac_r, 3), n=len(xs)),
               persistence=dict(rho_lag1=round(rho_ar, 3), gap_lag1=round(gap_ar, 3),
                                sigma_lag1=round(sig_ar, 3)),
               next_gap_forecast=nextgap,
               early_warning_corr_with_remaining_drift=early,
               frozen_base_runaway_separation=runaway_sep,
               n_runs=len(runs))
    with open("experiments/taste_alignment_predictor.json", "w") as fh:
        json.dump(dict(out, runs=[{k: v for k, v in r.items()} for r in runs]), fh, indent=1)

    print(f"{len(runs)} score-logged rollouts")
    print(f"\n1) FACTORIZATION gap ~ c*rho*sigma: slope c = {slope:.3f}, r = {fac_r:.3f} (n={len(xs)} rounds)")
    print(f"\n2) PERSISTENCE (lag-1 autocorr): rho {rho_ar:.3f}  vs  gap {gap_ar:.3f}  (sigma {sig_ar:.3f})")
    print(f"2b) NEXT-GAP forecast: rho*sigma -> next gap {nextgap['rho_sigma_to_nextgap']}  vs  gap -> next gap {nextgap['gap_to_nextgap']}")
    print("\n3) EARLY WARNING — corr of round-1 measure with remaining drift:")
    for grid, v in early.items():
        print(f"   {grid}: {v}")
    print("\n   frozen_base (OLMo) runaway ranking by round-1 measure (runaways end >0.4):")
    for name, v in runaway_sep.items():
        print(f"   {name:14s} runaway ranks {v['runaway_ranks_of_6']} of {len(fb)}: {v['vals_sorted']}")


if __name__ == "__main__":
    main()
