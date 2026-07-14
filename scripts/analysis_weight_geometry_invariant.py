"""Invariant weight-geometry reads from the persisted per-round `geom` fields.
(docs/ANALYSIS_LEDGER.md §D: (a) the integrator report's §5 geometry null was
an UNSAVED exploratory computation — commit it; (b) the withdrawn basin-era
"more motion, less behavioral change" claim can now be re-tested honestly,
because the K2 chassis logs MERGED-update norms — merged_diff_norm(fac_t,
fac_0) — which are gauge-invariant, unlike the raw A/B-factor norms that got
Part 1 withdrawn.)

Per rollout the chassis persists, each round:
  step_norm                 = ||merged(t) - merged(t-1)||
  net_displacement_from_r0  = ||merged(t) - merged(0)||
  path_length               = sum of step norms
  cos_cumulative_with_r1    = cos(merged(t)-merged(0), merged(r1)-merged(0))

Reads:
  1. §5 NULL, committed: early motion (step r1+r2) vs later behavior
     (|pool move r2->r4|, total |pool move|) — expected null.
  2. WITHDRAWN-CLAIM RETEST (invariant): thrash ratio path_length /
     net_displacement vs |total behavioral change|.
  3. FORCE SIGNATURE: same-round step_norm vs |gap| and rho*sigma — does
     selection force leave a weight-motion trace, or is per-round motion
     constant regardless of what was selected?
  4. Directional persistence: final cos_cumulative_with_r1 vs |total move|.

Usage: uv run python scripts/analysis_weight_geometry_invariant.py
Writes experiments/weight_geometry_invariant.json and prints the tables.
"""

import glob
import json
import math
import os
import statistics as st

FILES = sorted(glob.glob("experiments/modal_k2_release/output/*.json")) + [
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
    pairs = [(x, y) for x, y in zip(a, b) if x is not None and y is not None]
    if len(pairs) < 3:
        return None
    a = [p[0] for p in pairs]
    b = [p[1] for p in pairs]
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
                geom = rec.get("geom")
                rr = rec.get("rounds_raw")
                if not isinstance(geom, list) or len(geom) < 4 or not rr:
                    continue
                pools, gaps, rhosig = [], [], []
                for rnd in rr:
                    items = [it for it in rnd
                             if isinstance(it.get("cand_risk"), list) and it["cand_risk"]]
                    if not items:
                        break
                    pools.append(mean([mean(it["cand_risk"]) for it in items]))
                    gaps.append(mean([mean([it["cand_risk"][i] for i in it["kept_idx"]])
                                      - mean(it["cand_risk"]) for it in items]))
                    sp = mean([st.pstdev(it["cand_risk"]) for it in items])
                    rhos = []
                    for it in items:
                        sc = it.get("scores_arm")
                        if isinstance(sc, list) and len(sc) == len(it["cand_risk"]):
                            c = corr(sc, it["cand_risk"])
                            if c is not None:
                                rhos.append(c)
                    rhosig.append(mean(rhos) * sp if rhos else None)
                if len(pools) < 4:
                    continue
                steps = [g["step_norm"] for g in geom]
                runs.append(dict(
                    grid=grid, cond=cond, seed=seed,
                    steps=[round(x, 3) for x in steps],
                    net=round(geom[-1]["net_displacement_from_r0"], 3),
                    path=round(geom[-1]["path_length"], 3),
                    thrash=round(geom[-1]["path_length"]
                                 / max(geom[-1]["net_displacement_from_r0"], 1e-6), 3),
                    cos_r1_final=geom[-1]["cos_cumulative_with_r1"],
                    early_step=round(steps[0] + steps[1], 3) if len(steps) > 1 else None,
                    late_move=round(abs(pools[-1] - pools[2]), 3) if len(pools) > 2 else None,
                    total_move=round(abs(pools[-1] - pools[0]), 3),
                    gaps=[round(g, 3) for g in gaps],
                    rhosig=[None if x is None else round(x, 3) for x in rhosig]))
    out = {"runs": runs, "reads": {}}
    for grid in ("k2_olmo", "k1_qwen"):
        rs = [r for r in runs if r["grid"] == grid]
        if len(rs) < 4:
            out["reads"][grid] = {"n": len(rs), "note": "no geom persisted or too few runs"}
            continue
        # per-round pairs for the force-signature read
        sg, sa, sr = [], [], []
        for r in rs:
            n = min(len(r["steps"]), len(r["gaps"]))
            for i in range(n):
                sg.append(r["steps"][i])
                sa.append(abs(r["gaps"][i]))
                sr.append(abs(r["rhosig"][i]) if r["rhosig"][i] is not None else None)
        out["reads"][grid] = dict(
            n=len(rs),
            s5_early_vs_late=round(corr([r["early_step"] for r in rs],
                                        [r["late_move"] for r in rs]), 3),
            s5_early_vs_total=round(corr([r["early_step"] for r in rs],
                                         [r["total_move"] for r in rs]), 3),
            thrash_vs_total_move=round(corr([r["thrash"] for r in rs],
                                            [r["total_move"] for r in rs]), 3),
            cos_vs_total_move=round(corr([r["cos_r1_final"] for r in rs],
                                         [r["total_move"] for r in rs]), 3),
            step_vs_absgap_roundlevel=round(corr(sg, sa), 3),
            step_vs_absrhosig_roundlevel=round(corr(sg, sr), 3),
            mean_step=round(mean([x for r in rs for x in r["steps"]]), 3),
            step_cv=round(st.pstdev([x for r in rs for x in r["steps"]])
                          / mean([x for r in rs for x in r["steps"]]), 3))
    with open("experiments/weight_geometry_invariant.json", "w") as fh:
        json.dump(out, fh, indent=1)

    for grid, v in out["reads"].items():
        print(f"== {grid}: {json.dumps(v)}")


if __name__ == "__main__":
    main()
