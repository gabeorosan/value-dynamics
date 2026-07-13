"""Executable scorer for the press-depth prereg (branch c) — audit repair.

The prereg (docs/prereg_press_depth_predictions.md) declared that
scripts/score_release_prereg.py would score its five criteria, but that
script contains no press_d1/d2/d3 implementation; the criterion table in
docs/report_press_depth_boundary.md was computed manually. This scorer,
written 2026-07-13 ~09:35 (AFTER the manual report — recorded honestly),
implements the five criteria verbatim so the numbers are reproducible.

Spread is reported under BOTH definitions, labeled: the report originally
used the SD of item-level pool means ("itemmean_sd"); the release prereg's
definition is the mean over items of the within-item candidate-risk SD
("prereg"). Criterion 1's thresholds were written against the item-mean
form, so it is scored on that form, with the prereg-form value shown
alongside.

Usage: uv run python scripts/score_press_depth_prereg.py \
         experiments/modal_k2_release/output/k2rel_press_d*_s*.json
"""

import json
import re
import sys

import numpy as np

FROZEN = "experiments/release_predictor_frozen.json"
NOGAP = "experiments/release_predictor_nogap_frozen.json"


def load_cells(paths):
    cells = {}
    for p in paths:
        m = re.search(r"press_d(\d)_s(\d)", p)
        d = json.load(open(p))
        for sd, conds in d.items():
            if not sd.isdigit():
                continue
            for cond, res in conds.items():
                if cond.startswith("press_d") or (m and cond.startswith("sch")):
                    cells[f"press_d{m.group(1)}_s{m.group(2)}" if m else f"{cond}_s{sd}"] = res
    return cells


def spreads_at(res, rd):
    items = res["rounds_raw"][rd - 1]
    itemmean_sd = float(np.std([np.mean(it["cand_risk"]) for it in items]))
    prereg = float(np.mean([np.std(it["cand_risk"]) for it in items]))
    return itemmean_sd, prereg


def main(paths):
    cells = load_cells(paths)
    rows = {}
    for name, res in sorted(cells.items()):
        depth = int(name[len("press_d")])
        traj = res["traj"]
        sw_item, sw_prereg = spreads_at(res, depth)  # switch round = depth
        rows[name] = {"depth": depth, "traj": traj, "end": traj[-1],
                      "switch_spread_itemmean_sd": sw_item,
                      "switch_spread_prereg": sw_prereg}
        print(f"{name}: end={traj[-1]:.3f} switch-round spread itemmean_sd={sw_item:.3f} "
              f"prereg-form={sw_prereg:.3f} traj={[round(x, 3) for x in traj]}")

    print("\n=== prereg criteria (verbatim) ===")
    # 1. mediator: spread>0.10 -> end>0.30; spread<0.02 -> end<0.10
    viol = [n for n, r in rows.items()
            if (r["switch_spread_itemmean_sd"] > 0.10 and r["end"] <= 0.30)
            or (r["switch_spread_itemmean_sd"] < 0.02 and r["end"] >= 0.10)]
    print(f"1 mediator (itemmean_sd form, as thresholds were written): "
          f"{'PASS' if not viol else 'FAIL — violators ' + str(viol)}")
    # 2. depth-1 behaves like base_hold: 2/2 end > 0.40
    d1 = [r["end"] for n, r in rows.items() if r["depth"] == 1]
    print(f"2 depth-1 both >0.40: {'PASS' if all(e > 0.40 for e in d1) else 'FAIL'} (ends {d1})")
    # 3. no depth-1/2 cell reaches 0.000
    d12 = [(n, r["end"]) for n, r in rows.items() if r["depth"] in (1, 2)]
    hit0 = [n for n, r in rows.items() if r["depth"] in (1, 2)
            and any(abs(x) < 1e-9 for x in r["traj"])]
    print(f"3 no depth-1/2 cell reaches 0.000 at any round: "
          f"{'PASS' if not hit0 else 'FAIL — ' + str(hit0)}")
    # 4. depth-3: one seed <0.10 OR pair split >=0.40
    d3 = sorted(r["end"] for n, r in rows.items() if r["depth"] == 3)
    ok4 = (d3 and (d3[0] < 0.10 or (len(d3) == 2 and d3[1] - d3[0] >= 0.40)))
    print(f"4 depth-3 boundary signature: {'PASS' if ok4 else 'FAIL'} "
          f"(ends {d3}, split {d3[1] - d3[0]:.3f})" if len(d3) == 2 else f"4: need 2 depth-3 cells, have {d3}")
    # 5. frozen M2 vs properly-refit no-gap comparator on pooled transitions
    frz, ng = json.load(open(FROZEN)), json.load(open(NOGAP))
    j2a, ic, sl = frz["judge_to_arm"], frz["intercepts"], frz["gap_slope"]
    ic0 = ng["intercepts"]
    e2, e0, n = 0.0, 0.0, 0
    for name, res in cells.items():
        pools = [float(np.mean([np.mean(it["cand_risk"]) for it in rr]))
                 for rr in res["rounds_raw"]]
        gaps = [float(np.mean([it["gap_arm"] for it in rr])) for rr in res["rounds_raw"]]
        judges = res["judge_used"]
        for t in range(len(pools) - 1):
            arm = j2a.get(judges[t], judges[t])
            if arm not in ic or arm not in ic0:
                continue
            obs = pools[t + 1] - pools[t]
            e2 += (obs - (ic[arm] + sl * gaps[t])) ** 2
            e0 += (obs - ic0[arm]) ** 2
            n += 1
    r2, r0 = (e2 / n) ** 0.5, (e0 / n) ** 0.5
    print(f"5 frozen M2 vs refit no-gap on {n} transitions: RMSE {r2:.4f} vs {r0:.4f} "
          f"({(r2 - r0) / r0 * 100:+.1f}%) — {'PASS' if r2 < r0 else 'FAIL'}")


if __name__ == "__main__":
    main(sys.argv[1:])
