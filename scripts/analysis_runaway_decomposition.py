"""Runaway decomposition across K1 (Qwen) + K2 (OLMo) grids: what makes the
few runaway seeds run — early luck + momentum, judge-taste change, or
sustained round-by-round selection? (docs/ANALYSIS_LEDGER.md §A row; promoted
from the 07-14 ad-hoc session read.)

Per rollout and round, from rounds_raw:
  pool     = mean candidate risk (the generated supply)
  gap      = realized kept-minus-pool gap under the arm's judge
  spread   = mean within-item candidate-risk SD (rankable variation)
  taste    = mean within-item corr(arm judge's scores, candidate risk)
             (the judge's EXPRESSED preference on that round's menu)
  null_pct = percentile of the observed round gap under the exact random-keep
             null (every item keeps a uniform 2-of-6 subset; Monte Carlo over
             joint draws). ~0.5 = chance selection; >0.9 = risk-favoring
             selection beyond chance.
  drift    = next round's pool minus this round's pool

Pooled diagnostics per condition:
  zero-gap drift  = mean drift over rounds with |gap| < 0.05 (the "momentum"
                    term — if pollution/momentum sustained runaways, this
                    would be positive at elevated pools; it is negative)
  gap slope       = OLS slope of drift on gap (the selection term)

Usage: uv run python scripts/analysis_runaway_decomposition.py
Writes experiments/runaway_decomposition.json and prints the tables.
"""

import json
import math
import os
import random
import statistics as st

FILES = {
    "k2_olmo": [
        "experiments/kaggle/kaggle_k2_olmo_inversion/output_controls/k2_olmo_inversion_kaggle_controls.json",
        "experiments/kaggle/kaggle_k2_olmo_inversion_conf/output/k2_conf_v1_seeds12_partial.json",
        "experiments/kaggle/kaggle_k2_olmo_inversion_conf/output/k2_olmo_inversion_kaggle_conf_v2.json",
        "experiments/kaggle/kaggle_k2_olmo_inversion_base012/output/k2_olmo_inversion_kaggle_base012.json",
        "experiments/cerebrium_k2/output/k2_cerebrium_seed0_complete.json",
    ],
    "k1_qwen": [
        "experiments/kaggle/kaggle_k1_qwen_anchor_grid/output/k1_qwen_anchor.json",
    ],
}
NULL_DRAWS = 4000
ZERO_GAP = 0.05
RNG = random.Random(7)


def mean(x):
    return sum(x) / len(x) if x else None


def corr(a, b):
    ma, mb = mean(a), mean(b)
    sa = math.sqrt(sum((x - ma) ** 2 for x in a))
    sb = math.sqrt(sum((y - mb) ** 2 for y in b))
    if sa == 0 or sb == 0:
        return None
    return sum((x - ma) * (y - mb) for x, y in zip(a, b)) / (sa * sb)


def null_percentile(items, observed):
    """Percentile of observed round-mean gap under uniform random 2-of-6 keeps."""
    draws = []
    for _ in range(NULL_DRAWS):
        gs = []
        for it in items:
            cr = it["cand_risk"]
            kept = RNG.sample(range(len(cr)), 2)
            gs.append(mean([cr[i] for i in kept]) - mean(cr))
        draws.append(mean(gs))
    below = sum(1 for d in draws if d < observed)
    ties = sum(1 for d in draws if d == observed)
    return (below + 0.5 * ties) / NULL_DRAWS


def main():
    runs = []
    for grid, files in FILES.items():
        for f in files:
            if not os.path.exists(f):
                continue
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
                        rnd = [it for it in rnd
                               if isinstance(it.get("cand_risk"), list) and it["cand_risk"]
                               and isinstance(it.get("kept_idx"), list) and it["kept_idx"]]
                        if not rnd:
                            continue
                        pool = mean([mean(it["cand_risk"]) for it in rnd])
                        # gap recomputed from kept_idx so it's defined for every
                        # arm (random_select logs no judge scores)
                        gap = mean([mean([it["cand_risk"][i] for i in it["kept_idx"]])
                                    - mean(it["cand_risk"]) for it in rnd])
                        spread = mean([st.pstdev(it["cand_risk"]) for it in rnd])
                        tastes = [corr(it["scores_arm"], it["cand_risk"]) for it in rnd
                                  if isinstance(it.get("scores_arm"), list)
                                  and len(it["scores_arm"]) == len(it["cand_risk"])]
                        tastes = [t for t in tastes if t is not None]
                        rounds.append(dict(
                            pool=round(pool, 4), gap=round(gap, 4),
                            spread=round(spread, 4),
                            taste=round(mean(tastes), 3) if tastes else None,
                            null_pct=round(null_percentile(rnd, gap), 3),
                        ))
                    if len(rounds) < 3:
                        continue
                    for i in range(len(rounds) - 1):
                        rounds[i]["drift"] = round(rounds[i + 1]["pool"] - rounds[i]["pool"], 4)
                    runs.append(dict(
                        grid=grid, file=os.path.basename(f), seed=seed, cond=cond,
                        rounds=rounds,
                        total_drift=round(rounds[-1]["pool"] - rounds[0]["pool"], 4),
                        sum_gap=round(sum(r["gap"] for r in rounds[:-1]), 4),
                        n_taste_rounds=sum(1 for r in rounds if r["null_pct"] >= 0.9),
                    ))

    pooled = {}
    for grid in FILES:
        for cond in sorted({r["cond"] for r in runs if r["grid"] == grid}):
            rows = [(r0["gap"], r0["drift"])
                    for r in runs if r["grid"] == grid and r["cond"] == cond
                    for r0 in r["rounds"] if "drift" in r0]
            zg = [d for g, d in rows if abs(g) < ZERO_GAP]
            gs = [g for g, _ in rows]
            ds = [d for _, d in rows]
            mg, md = mean(gs), mean(ds)
            sxx = sum((g - mg) ** 2 for g in gs)
            slope = (sum((g - mg) * (d - md) for g, d in rows) / sxx) if sxx > 0 else None
            pooled[f"{grid}/{cond}"] = dict(
                n_transitions=len(rows),
                zero_gap_drift=round(mean(zg), 4) if zg else None,
                n_zero_gap=len(zg),
                gap_slope=round(slope, 3) if slope is not None else None,
            )

    out = dict(runs=runs, pooled=pooled, null_draws=NULL_DRAWS, zero_gap_band=ZERO_GAP)
    with open("experiments/runaway_decomposition.json", "w") as fh:
        json.dump(out, fh, indent=1)

    print(f"{len(runs)} rollouts\n")
    print("POOLED per condition: selection term (gap slope) vs momentum term (zero-gap drift)")
    print(f"{'grid/cond':28s} {'trans':>5s} {'gap_slope':>9s} {'zerogap_drift':>13s} {'n_zg':>4s}")
    for k, v in pooled.items():
        print(f"{k:28s} {v['n_transitions']:5d} {str(v['gap_slope']):>9s} "
              f"{str(v['zero_gap_drift']):>13s} {v['n_zero_gap']:4d}")
    print("\nPer-run: total drift vs summed gap; taste rounds (null_pct>=0.9)")
    for r in sorted(runs, key=lambda r: (r["grid"], r["cond"], -abs(r["total_drift"]))):
        marks = " ".join(f"{x['gap']:+.2f}({x['null_pct']:.2f})" for x in r["rounds"][:-1])
        print(f"  {r['grid']}/{r['cond']:16s} s{r['seed']:>2s} drift {r['total_drift']:+.2f} "
              f"sum_gap {r['sum_gap']:+.2f} taste_rounds {r['n_taste_rounds']}  gaps(pct): {marks}")


if __name__ == "__main__":
    main()
