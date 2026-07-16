"""Stated-channel parity: run the behavior-vs-stated dissociation analysis on
the two run populations it never covered (user question, 07-16).

The committed dissociation result (scripts/analysis_selfreport_calibration.py
-> experiments/selfreport_calibration_k2.json, ledger row "K2/OLMo: selection
moves behavior, stated tolerance barely follows") covers only the OLMo/K2
chassis (46 rollouts). Two populations in the modeled corpus log a stated
channel every round but were never analyzed:

  A. The Qwen risk grid (16 corpus runs; kaggle k1_qwen_anchor.json).
     Behavior = traj (fraction risk-seeking terminal choices).
     Stated   = battery[r].self_report.p_risk_tolerant (order-balanced
     forced choice between two self-descriptions, logged every round).

  B. The Qwen insecure-code loops (selfaware cells files; the runs whose
     VALUE axis is the sr_freegen self-description score).
     Behavior = [baseline] + battery[r].sr_free_gen.sr_freegen (what the
     answers show, mostly demonstration).
     Stated   = [baseline] + battery[r].self_report_code.mean_p_insecure
     (a forced probe: does it SAY its code is insecure). The static dose
     ladder compared these once per rung; this is the within-loop version.

Readouts per rollout match analysis_selfreport_calibration.py exactly so the
numbers are comparable: net moves d_traj / d_sr, tracking ratio d_sr/d_traj
where |d_traj| >= 0.15, within-rollout Pearson corr, |behavior - stated| gap
at the first and last round. Aggregates per condition group and overall;
cross-rollout corr at both ends. Bonus instrument readout for the risk stated
probe: mean |p(A-order) - p(B-order)| across battery reads (order sensitivity).

Usage: uv run python scripts/analysis_stated_channel_parity.py
Writes experiments/stated_channel_parity.json and prints the tables.
"""

import json
import math
import os

QWEN_RISK_FILE = "experiments/kaggle/kaggle_k1_qwen_anchor_grid/output/k1_qwen_anchor.json"
QWEN_RISK_CONDS = ["evolving_self", "frozen_copy_r0", "frozen_base", "random_select"]

# (path, condition label) — the corpus CELLS_SOURCES of analysis_spread_util_unified.py
INSECURE_FILES = [
    ("experiments/em_selfaware_loop/output/selfaware_loop_grid.json", "candid self-prompt (self judge)"),
    ("experiments/em_selfaware_loop/output/judge_opposition_oracle.json", "min-insecurity oracle"),
    ("experiments/em_selfaware_loop/output/judge_opposition_oracle_seed707.json", "min-insecurity oracle"),
    ("experiments/em_selfaware_loop/output/judge_opposition_natural_base.json", "base judge, static alternative"),
    ("experiments/em_selfaware_loop/output/mixed_reopen_qwen.json", "oracle, base-mixed pool"),
    ("experiments/em_selfaware_loop/output/mixed_reopen_twin_selfonly.json", "min-insecurity oracle"),
    ("experiments/em_selfaware_loop/output/head2head_selfjudge.json", "self-judge duels, base-mixed pool"),
]

MOVED = 0.15  # same |d_traj| threshold as analysis_selfreport_calibration.py


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


def rollout_row(cond, seed, traj, sr, extra=None):
    d_traj = traj[-1] - traj[0]
    d_sr = sr[-1] - sr[0]
    row = dict(
        cond=cond, seed=str(seed),
        traj=[round(x, 4) for x in traj], sr=[round(x, 4) for x in sr],
        d_traj=round(d_traj, 4), d_sr=round(d_sr, 4),
        tracking_ratio=(round(d_sr / d_traj, 3) if abs(d_traj) >= MOVED else None),
        within_corr=(None if corr(traj, sr) is None else round(corr(traj, sr), 3)),
        gap0=round(abs(traj[0] - sr[0]), 4), gapE=round(abs(traj[-1] - sr[-1]), 4),
    )
    if extra:
        row.update(extra)
    return row


def aggregate(rollouts):
    out = {}
    t0 = [r["traj"][0] for r in rollouts]
    s0 = [r["sr"][0] for r in rollouts]
    tE = [r["traj"][-1] for r in rollouts]
    sE = [r["sr"][-1] for r in rollouts]
    c0, cE = corr(t0, s0), corr(tE, sE)
    out["overall"] = dict(
        n=len(rollouts),
        cross_corr_r0=None if c0 is None else round(c0, 3),
        cross_corr_final=None if cE is None else round(cE, 3),
        mean_gap_r0=round(mean([r["gap0"] for r in rollouts]), 3),
        mean_gap_final=round(mean([r["gapE"] for r in rollouts]), 3),
    )
    for g in sorted({r["cond"] for r in rollouts}):
        rs = [r for r in rollouts if r["cond"] == g]
        moved = [r for r in rs if r["tracking_ratio"] is not None]
        wc = [r["within_corr"] for r in rs if r["within_corr"] is not None]
        out[g] = dict(
            n=len(rs), n_behavior_moved=len(moved),
            mean_abs_d_traj_moved=round(mean([abs(r["d_traj"]) for r in moved]), 3) if moved else None,
            mean_abs_d_sr_moved=round(mean([abs(r["d_sr"]) for r in moved]), 3) if moved else None,
            mean_tracking_ratio=round(mean([r["tracking_ratio"] for r in moved]), 3) if moved else None,
            mean_within_corr=round(mean(wc), 3) if wc else None,
        )
    return out


def qwen_risk_rollouts():
    d = json.load(open(QWEN_RISK_FILE))
    rollouts, order_deltas = [], []
    for seed, conds in d.items():
        if not str(seed).isdigit():
            continue
        for cond, rec in conds.items():
            if cond not in QWEN_RISK_CONDS or not isinstance(rec, dict):
                continue
            # same run filter as the corpus builder: a modeled run has rounds_raw
            # and is not measure-only (seed 99 logs a battery but zero
            # modelable rounds — its traj entries are null)
            if not rec.get("rounds_raw") or not rec.get("traj") or not rec.get("battery"):
                continue
            if rec.get("measure_only"):
                continue
            sr = [b["self_report"]["p_risk_tolerant"] for b in rec["battery"]
                  if isinstance(b, dict) and "self_report" in b]
            traj = rec["traj"]
            n = min(len(sr), len(traj))
            if n < 3:
                continue
            rollouts.append(rollout_row(cond, seed, traj[:n], sr[:n]))
            for b in rec["battery"]:
                items = b.get("self_report", {}).get("items", [])
                if len(items) == 2:
                    order_deltas.append(abs(items[0]["p_risk_tolerant"]
                                            - items[1]["p_risk_tolerant"]))
    return rollouts, order_deltas


def insecure_loop_rollouts():
    rollouts, seen = [], set()
    for path, cond in INSECURE_FILES:
        if not os.path.exists(path):
            continue
        d = json.load(open(path))
        baselines = d.get("baselines", {})
        for cell_id, c in d.get("cells", {}).items():
            bat = c.get("battery")
            if not bat:
                continue
            dose = c.get("dose") or cell_id.split(":")[0]
            b0 = baselines.get(dose)
            v0 = b0["battery"]["sr_free_gen"]["sr_freegen"] if b0 else None
            s0 = (b0["battery"].get("self_report_code", {}).get("mean_p_insecure")
                  if b0 else None)
            # the three judge_opposition_* files log a placeholder baseline
            # stated read (exactly 0.5, no item-level data) while their
            # per-round reads are real — drop the round-0 pair there
            if s0 == 0.5 and "judge_opposition" in path:
                s0 = None
            traj = [v0] + [b["sr_free_gen"]["sr_freegen"] for b in bat]
            sr = [s0] + [b.get("self_report_code", {}).get("mean_p_insecure") for b in bat]
            pairs = [(t, s) for t, s in zip(traj, sr) if t is not None and s is not None]
            if len(pairs) < 3:
                continue
            key = (os.path.basename(path), cell_id)
            if key in seen:
                continue
            seen.add(key)
            rollouts.append(rollout_row(
                cond, c.get("seed", cell_id),
                [p[0] for p in pairs], [p[1] for p in pairs],
                extra=dict(file=os.path.basename(path), cell=cell_id)))
    return rollouts


def print_block(name, rollouts, agg):
    a = agg["overall"]
    print(f"\n=== {name}  ({a['n']} rollouts) ===")
    print(f"cross-rollout corr(behavior, stated): r0 {a['cross_corr_r0']}  final {a['cross_corr_final']}")
    print(f"mean |behavior - stated| gap:         r0 {a['mean_gap_r0']}  final {a['mean_gap_final']}")
    print(f"{'group':38s} {'n':>3s} {'moved':>5s} {'|d_beh|':>8s} {'|d_sr|':>7s} {'track':>6s} {'w-corr':>7s}")
    for g, v in agg.items():
        if g == "overall":
            continue
        print(f"{g:38s} {v['n']:3d} {v['n_behavior_moved']:5d} "
              f"{str(v['mean_abs_d_traj_moved']):>8s} {str(v['mean_abs_d_sr_moved']):>7s} "
              f"{str(v['mean_tracking_ratio']):>6s} {str(v['mean_within_corr']):>7s}")
    print("rollouts where behavior moved >= 0.15 (sorted by |d_traj|):")
    for r in sorted([r for r in rollouts if r["tracking_ratio"] is not None],
                    key=lambda r: -abs(r["d_traj"])):
        print(f"  {r['cond']:36s} s{r['seed']:>4s} behavior {r['traj'][0]:+.2f}->{r['traj'][-1]:+.2f} "
              f"(d {r['d_traj']:+.2f})  stated {r['sr'][0]:.2f}->{r['sr'][-1]:.2f} "
              f"(d {r['d_sr']:+.2f})  ratio {r['tracking_ratio']:+.2f}")


def main():
    qwen_risk, order_deltas = qwen_risk_rollouts()
    assert len(qwen_risk) == 16, len(qwen_risk)  # the 16 Qwen risk-grid corpus runs
    insecure = insecure_loop_rollouts()

    out = {
        "moved_threshold": MOVED,
        "qwen_risk_grid": {
            "rollouts": qwen_risk,
            "aggregates": aggregate(qwen_risk),
            "stated_probe_order_sensitivity_mean_abs": round(mean(order_deltas), 4),
            "stated_probe_order_reads": len(order_deltas),
        },
        "qwen_insecure_loops": {
            "rollouts": insecure,
            "aggregates": aggregate(insecure),
        },
    }
    with open("experiments/stated_channel_parity.json", "w") as fh:
        json.dump(out, fh, indent=1)

    print_block("A. Qwen risk grid — behavior (risk traj) vs stated risk tolerance",
                qwen_risk, out["qwen_risk_grid"]["aggregates"])
    print(f"stated-probe order sensitivity: mean |p_A-order - p_B-order| = "
          f"{out['qwen_risk_grid']['stated_probe_order_sensitivity_mean_abs']} "
          f"over {out['qwen_risk_grid']['stated_probe_order_reads']} reads")
    print_block("B. Qwen insecure-code loops — behavior (sr_freegen) vs stated (p_insecure forced probe)",
                insecure, out["qwen_insecure_loops"]["aggregates"])


if __name__ == "__main__":
    main()
