"""Self-report calibration on the CURRENT (K2-chassis) grids — the resurrection
of the orphaned basin-era Part-2 result (docs/ANALYSIS_LEDGER.md §D row 1).

The basin-era finding (report_basin_weightspace_and_calibration.md Part 2,
Qwen, 6-round self/frozen loops): stated risk tolerance starts uncorrelated
with behavioral risk (corr −0.02/+0.15, mean |gap| 0.37) and CALIBRATES over
rounds. That read was never re-run on the K2-chassis runs (OLMo), which
persist battery[r].self_report.p_risk_tolerant next to traj[r] every round —
including through oracle reversals, head-to-head duels, rescues, and holds.

Question asked here: when selection moves the behavioral risk coordinate,
does the model's STATED risk tolerance move with it (calibration), lag it,
or stay flat (dissociation, as on the OLMo insecure-code dose ladder)?

Readouts per rollout (traj and sr both have R+1 entries incl. round 0):
  - sr0/srE, traj0/trajE (first/last), net moves d_traj, d_sr
  - tracking ratio d_sr/d_traj where |d_traj| >= 0.15 (behavior actually moved)
  - within-rollout Pearson corr(traj_r, sr_r) across rounds (n=R+1)
Aggregates: per condition-group and overall; cross-rollout corr(traj, sr) at
round 0 and at the final round; mean |traj − sr| gap at both.

Usage: uv run python scripts/analysis_selfreport_calibration.py
Writes experiments/selfreport_calibration_k2.json and prints the tables.
"""

import glob
import json
import math
import os

FILES = sorted(
    glob.glob("experiments/modal_k2_release/output/*.json")
) + [
    "experiments/kaggle/kaggle_k2_olmo_inversion/output_controls/k2_olmo_inversion_kaggle_controls.json",
    "experiments/kaggle/kaggle_k2_olmo_inversion_conf/output/k2_conf_v1_seeds12_partial.json",
    "experiments/kaggle/kaggle_k2_olmo_inversion_conf/output/k2_olmo_inversion_kaggle_conf_v2.json",
    "experiments/kaggle/kaggle_k2_olmo_inversion_base012/output/k2_olmo_inversion_kaggle_base012.json",
    "experiments/cerebrium_k2/output/k2_cerebrium_seed0_complete.json",
]

MOVED = 0.15  # |d_traj| threshold for the tracking ratio to be meaningful


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


def group(cond):
    if cond.startswith("h2h"):
        return "h2h_duels"
    if "oracle" in cond:
        return "oracle"
    if "mix" in cond or "invade" in cond:
        return "mixed_injection"
    if cond in ("frozen_cons_r0", "frozen_base", "random_select", "evolving_self"):
        return "k2_grid"
    if "hold" in cond or "rescue" in cond or "erode" in cond:
        return "release_holds_rescues"
    return "other"


def main():
    rollouts = []
    for f in FILES:
        if not os.path.exists(f):
            continue
        d = json.load(open(f))
        for seed in d:
            if seed.startswith("_"):
                continue
            for cond, rec in d[seed].items():
                if not isinstance(rec, dict) or "battery" not in rec or "traj" not in rec:
                    continue
                sr = [b["self_report"]["p_risk_tolerant"] for b in rec["battery"]
                      if isinstance(b, dict) and "self_report" in b]
                traj = rec["traj"]
                n = min(len(sr), len(traj))
                if n < 3:
                    continue
                sr, traj = sr[:n], traj[:n]
                d_traj = traj[-1] - traj[0]
                d_sr = sr[-1] - sr[0]
                rollouts.append(dict(
                    file=os.path.basename(f), seed=seed, cond=cond, group=group(cond),
                    traj=[round(x, 4) for x in traj], sr=[round(x, 4) for x in sr],
                    d_traj=round(d_traj, 4), d_sr=round(d_sr, 4),
                    tracking_ratio=(round(d_sr / d_traj, 3) if abs(d_traj) >= MOVED else None),
                    within_corr=(None if corr(traj, sr) is None else round(corr(traj, sr), 3)),
                    gap0=round(abs(traj[0] - sr[0]), 4), gapE=round(abs(traj[-1] - sr[-1]), 4),
                ))
    out = {"rollouts": rollouts, "moved_threshold": MOVED, "aggregates": {}}

    t0 = [r["traj"][0] for r in rollouts]
    s0 = [r["sr"][0] for r in rollouts]
    tE = [r["traj"][-1] for r in rollouts]
    sE = [r["sr"][-1] for r in rollouts]
    out["aggregates"]["overall"] = dict(
        n=len(rollouts),
        cross_corr_r0=round(corr(t0, s0), 3), cross_corr_final=round(corr(tE, sE), 3),
        mean_gap_r0=round(mean([r["gap0"] for r in rollouts]), 3),
        mean_gap_final=round(mean([r["gapE"] for r in rollouts]), 3),
    )
    for g in sorted({r["group"] for r in rollouts}):
        rs = [r for r in rollouts if r["group"] == g]
        moved = [r for r in rs if r["tracking_ratio"] is not None]
        out["aggregates"][g] = dict(
            n=len(rs), n_behavior_moved=len(moved),
            mean_abs_d_traj_moved=round(mean([abs(r["d_traj"]) for r in moved]), 3) if moved else None,
            mean_abs_d_sr_moved=round(mean([abs(r["d_sr"]) for r in moved]), 3) if moved else None,
            mean_tracking_ratio=round(mean([r["tracking_ratio"] for r in moved]), 3) if moved else None,
            mean_within_corr=round(mean([r["within_corr"] for r in rs if r["within_corr"] is not None]), 3),
        )

    os.makedirs("experiments", exist_ok=True)
    with open("experiments/selfreport_calibration_k2.json", "w") as fh:
        json.dump(out, fh, indent=1)

    print(f"{len(rollouts)} rollouts from {len(FILES)} files\n")
    a = out["aggregates"]["overall"]
    print(f"OVERALL  cross-rollout corr(behavior, stated): r0 {a['cross_corr_r0']}  final {a['cross_corr_final']}")
    print(f"         mean |behavior - stated| gap:         r0 {a['mean_gap_r0']}  final {a['mean_gap_final']}\n")
    print(f"{'group':22s} {'n':>3s} {'moved':>5s} {'|d_beh|':>8s} {'|d_sr|':>7s} {'track':>6s} {'w-corr':>7s}")
    for g, v in out["aggregates"].items():
        if g == "overall":
            continue
        print(f"{g:22s} {v['n']:3d} {v['n_behavior_moved']:5d} "
              f"{str(v['mean_abs_d_traj_moved']):>8s} {str(v['mean_abs_d_sr_moved']):>7s} "
              f"{str(v['mean_tracking_ratio']):>6s} {str(v['mean_within_corr']):>7s}")
    print("\nRollouts where behavior moved >= 0.15 (sorted by |d_traj|):")
    for r in sorted([r for r in rollouts if r["tracking_ratio"] is not None],
                    key=lambda r: -abs(r["d_traj"])):
        print(f"  {r['cond']:22s} s{r['seed']:>3s} traj {r['traj'][0]:+.2f}->{r['traj'][-1]:+.2f} "
              f"(d {r['d_traj']:+.2f})  stated {r['sr'][0]:.2f}->{r['sr'][-1]:.2f} "
              f"(d {r['d_sr']:+.2f})  ratio {r['tracking_ratio']:+.2f}")


if __name__ == "__main__":
    main()
