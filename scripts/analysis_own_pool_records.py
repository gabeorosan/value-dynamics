"""Emit EVERY per-round record from every single-generator (own-pool) risk-axis
loop we have, with no narrative selection — for the exploratory scatter-plot
matrix (docs/figures/synthesis_state_space_explore.svg).

Own-pool = the organism generates all six candidates itself (no injected /
co-generated material), so the candidate spread is the organism's OWN value
spread — the thing that is comparable across runs. Mixed-generator conditions
are deliberately EXCLUDED (their spread is dominated by the source difference,
so it is a different quantity; see scripts/analysis_state_space_coords.py notes).

Per round k of a run with free-gen trajectory v0..vN and k=1..N selection rounds:
  value      = v_{k-1}                (free-gen risk before the round)
  spread     = mean over items of within-item SD of cand_risk   (prereg formula)
  gap        = mean(kept cand_risk) - mean(pool cand_risk)       (raw, signed +=up)
  drift      = v_k - v_{k-1}           (value change this round)
  next_drift = v_{k+1} - v_k           (value change next round; None on last)
  pool       = mean(pool cand_risk)

Judges kept distinct: self (evolving_self), risk copy (frozen_copy_r0), cautious
copy (frozen_cons_r0), base (frozen_base), random (random_select), score oracle
(oracle_hold). Organism tag: Qwen-K1 or OLMo-K2.

Run:  uv run python scripts/analysis_own_pool_records.py
Writes: experiments/state_space_explore.json.  numpy only.
"""
import itertools
import json
import os

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

JUDGE = {"evolving_self": "self", "frozen_copy_r0": "risk copy",
         "frozen_cons_r0": "cautious copy", "frozen_base": "base",
         "random_select": "random", "oracle_hold": "score oracle"}

# (path, organism tag) — every file that holds own-pool risk-axis cells
SOURCES = [
    ("experiments/kaggle/kaggle_k1_qwen_anchor_grid/output/k1_qwen_anchor.json", "Qwen-K1"),
    ("experiments/kaggle/kaggle_k2_olmo_inversion_conf/output/k2_olmo_inversion_kaggle_conf_v2.json", "OLMo-K2"),
    ("experiments/kaggle/kaggle_k2_olmo_inversion_conf/output/k2_conf_v1_seeds12_partial.json", "OLMo-K2"),
    ("experiments/kaggle/kaggle_k2_olmo_inversion_base012/output/k2_olmo_inversion_kaggle_base012.json", "OLMo-K2"),
    ("experiments/modal_k2_release/output/k2rel_oracle_hold_s21.json", "OLMo-K2"),
    ("experiments/modal_k2_release/output/k2rel_oracle_hold_s22.json", "OLMo-K2"),
]


def is_own_pool(res):
    for rnd in res["rounds_raw"]:
        if rnd:
            it = rnd[0]
            return "cand_owner" not in it or set(it.get("cand_owner") or ["self"]) == {"self"}
    return False


def cell_records(res, organism, judge, seed):
    traj = res["traj"]
    n = len(res["rounds_raw"])
    recs = []
    for k in range(1, n + 1):
        items = res["rounds_raw"][k - 1]
        if not items or k >= len(traj):
            break
        spread = float(np.mean([np.std(it["cand_risk"]) for it in items]))
        pool = float(np.mean([np.mean(it["cand_risk"]) for it in items]))
        kept = float(np.mean([it["cand_risk"][i] for it in items for i in it["kept_idx"]]))
        gap = kept - pool
        drift = traj[k] - traj[k - 1]
        nxt = (traj[k + 1] - traj[k]) if (k + 1) < len(traj) else None
        # Directional utilization for the round, null-subtracted:
        #   realized = round-mean signed gap (mean over items of mean(kept)-pool);
        #   ach      = round-mean of the most-extreme pair gap in realized's
        #              DIRECTION (min-risk oracle keeps the 2 lowest -> realized
        #              == ach in the down direction, so util == 1 even when the
        #              pool is lopsided; the earlier per-|gap| version wrongly
        #              normalised by the opposite direction and marked the oracle
        #              down at 0.45);
        #   null     = E|realized| under random selection (half-normal from the
        #              per-item pair-gap variance, analytic).
        #   util = (|realized| - null) / (|ach| - null), in [0,1].
        # 0 = no better than random selection · 1 = kept the most-extreme pair in
        # its direction. Rank/offset-invariant. Do NOT pool across organisms.
        item_gaps, up_ext, down_ext, var_it = [], [], [], []
        for it in items:
            c = it["cand_risk"]
            kidx = it["kept_idx"]
            nk = len(kidx) or 1
            if len(c) < nk + 1:
                continue
            m = sum(c) / len(c)
            item_gaps.append(sum(c[i] for i in kidx) / nk - m)
            pgs = [sum(c[j] for j in p) / nk - m
                   for p in itertools.combinations(range(len(c)), nk)]
            up_ext.append(max(pgs))
            down_ext.append(min(pgs))
            var_it.append(sum(g * g for g in pgs) / len(pgs))
        util = None
        if item_gaps:
            n = len(item_gaps)
            realized = sum(item_gaps) / n
            ach = (sum(up_ext) / n) if realized >= 0 else (sum(down_ext) / n)
            null = (2.0 / 3.14159265) ** 0.5 * (sum(var_it) ** 0.5) / n
            denom = abs(ach) - null
            if denom > 1e-9:
                util = round(max(0.0, min((abs(realized) - null) / denom, 1.0)), 4)
        recs.append(dict(organism=organism, judge=judge, seed=str(seed), round=k,
                         value=round(traj[k - 1], 4), spread=round(spread, 4),
                         gap=round(gap, 4), drift=round(drift, 4),
                         next_drift=(round(nxt, 4) if nxt is not None else None),
                         pool=round(pool, 4), util=util))
    return recs


def main():
    # collect, dedupe by (organism, judge, seed) keeping the run with most rounds
    best = {}
    for path, organism in SOURCES:
        d = json.load(open(os.path.join(ROOT, path)))
        for sd, conds in d.items():
            if not str(sd).isdigit():
                continue
            for cond, res in conds.items():
                if cond not in JUDGE or "rounds_raw" not in res or not res.get("traj"):
                    continue
                if not is_own_pool(res):
                    continue
                key = (organism, JUDGE[cond], str(sd))
                nrounds = len(res["rounds_raw"])
                if key not in best or nrounds > best[key][0]:
                    best[key] = (nrounds, cell_records(res, organism, JUDGE[cond], sd))

    records = [r for _, recs in best.values() for r in recs]
    out = dict(
        variables={
            "value": "free-gen risk before the round (0 safe … 1 gambles)",
            "spread": "candidate value spread (mean within-item SD)",
            "gap": "selection gap = kept − pool (+ pulls value up)",
            "drift": "value change this round (v_k − v_{k-1})",
            "next_drift": "value change next round",
            "pool": "candidate pool mean risk",
            "util": "utilization: (|gap| - random-null) / (achievable - random-null) per item, averaged; 0 = random selection, 1 = kept the most-extreme pair. NOT comparable across organisms.",
        },
        judges=sorted({r["judge"] for r in records}),
        organisms=sorted({r["organism"] for r in records}),
        n_runs=len(best), n_records=len(records),
        records=records,
    )
    with open(os.path.join(ROOT, "experiments/state_space_explore.json"), "w") as f:
        json.dump(out, f, indent=1)

    # sanity print
    import collections
    by = collections.Counter((r["organism"], r["judge"]) for r in records)
    print(f"{len(best)} runs, {len(records)} per-round records")
    for k in sorted(by):
        print(f"  {k[0]:8s} {k[1]:14s} {by[k]} rounds")


if __name__ == "__main__":
    main()
