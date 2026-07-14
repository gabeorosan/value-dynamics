"""Factual-EV trajectory: does value KNOWLEDGE erode while value PREFERENCE
moves? (docs/ANALYSIS_LEDGER.md §D — the "EV analysis" planned in the 07-10
deep audit and then demoted to a one-line validity gate; resurrected 07-14.)

factual_ev = P(model answers correctly which option has the higher expected
payoff), order-balanced, logged by every K1/K2-chassis battery every round.
ev_estimation.mean_ratio = the model's numeric EV estimate divided by truth
(1.0 = perfect), logged alongside. Both are KNOWLEDGE channels; traj/pool are
the PREFERENCE channels.

Questions:
  1. Trajectory: does mean_p_correct decay over rounds, and where? By
     condition family; per-run deltas.
  2. Coupling: is knowledge change correlated with preference movement
     (|d_pool|) — i.e., do rails cost knowledge, or are the channels
     independent (another dissociation)?
  3. Gate: which runs would fail the release program's 0.10-drop gate?

Usage: uv run python scripts/analysis_factual_ev_trajectory.py
Writes experiments/factual_ev_trajectory.json and prints the tables.
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
                bat = rec.get("battery")
                traj = rec.get("traj")
                if not isinstance(bat, list) or len(bat) < 3 or not traj:
                    continue
                ev = [b["factual_ev"]["mean_p_correct"] for b in bat
                      if isinstance(b, dict) and "factual_ev" in b]
                acc = [b["factual_ev"]["accuracy"] for b in bat
                       if isinstance(b, dict) and "factual_ev" in b]
                est = [b.get("ev_estimation", {}).get("mean_ratio") for b in bat
                       if isinstance(b, dict)]
                if len(ev) < 3:
                    continue
                # pool trajectory for preference movement (fall back to traj)
                rr = rec.get("rounds_raw") or []
                pools = []
                for rnd in rr:
                    vals = [mean(it["cand_risk"]) for it in rnd
                            if isinstance(it.get("cand_risk"), list) and it["cand_risk"]]
                    if vals:
                        pools.append(mean(vals))
                move = (abs(pools[-1] - pools[0]) if len(pools) >= 2
                        else abs(traj[-1] - traj[0]))
                runs.append(dict(
                    grid=grid, cond=cond, seed=seed,
                    ev=[round(x, 4) for x in ev], acc=[round(x, 3) for x in acc],
                    est_ratio=[None if x is None else round(x, 3) for x in est],
                    d_ev=round(ev[-1] - ev[0], 4),
                    min_drop=round(min(e - ev[0] for e in ev), 4),
                    fails_gate=min(e - ev[0] for e in ev) < -0.10,
                    pref_move=round(move, 4)))
    out = {"runs": runs, "by_group": {}}
    for grid in ("k2_olmo", "k1_qwen"):
        rs = [r for r in runs if r["grid"] == grid]
        if not rs:
            continue
        out["by_group"][grid] = dict(
            n=len(rs),
            ev_round0=round(mean([r["ev"][0] for r in rs]), 3),
            ev_final=round(mean([r["ev"][-1] for r in rs]), 3),
            mean_d_ev=round(mean([r["d_ev"] for r in rs]), 4),
            n_gate_failures=sum(r["fails_gate"] for r in rs),
            corr_dev_vs_prefmove=round(corr([r["d_ev"] for r in rs],
                                            [r["pref_move"] for r in rs]), 3),
            corr_absdev_vs_prefmove=round(corr([abs(r["d_ev"]) for r in rs],
                                               [r["pref_move"] for r in rs]), 3))
    with open("experiments/factual_ev_trajectory.json", "w") as fh:
        json.dump(out, fh, indent=1)

    for grid, v in out["by_group"].items():
        print(f"== {grid}: n={v['n']}  EV knowledge r0 {v['ev_round0']} -> final {v['ev_final']} "
              f"(mean d {v['mean_d_ev']:+.3f}); gate failures {v['n_gate_failures']}")
        print(f"   corr(d_ev, |pref move|) = {v['corr_dev_vs_prefmove']}; "
              f"corr(|d_ev|, |pref move|) = {v['corr_absdev_vs_prefmove']}")
    print("\nBiggest EV-knowledge movers:")
    for r in sorted(runs, key=lambda r: -abs(r["d_ev"]))[:10]:
        print(f"  {r['grid']}/{r['cond']:18s} s{r['seed']:>3s} ev {r['ev'][0]:.3f}->{r['ev'][-1]:.3f} "
              f"(d {r['d_ev']:+.3f}, min drop {r['min_drop']:+.3f}) pref_move {r['pref_move']:.2f}"
              f"{'  GATE-FAIL' if r['fails_gate'] else ''}")


if __name__ == "__main__":
    main()
