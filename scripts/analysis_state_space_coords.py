"""Compute the REAL per-round state-space coordinates for the trajectories drawn
in docs/figures/synthesis_state_space_trajectories.svg.

Each plotted round is a point at (value spread, selection gap):
  - value spread = prereg formula: mean over items of the within-item SD of the
    candidate value scores that round (cand_risk for the risk axis, cand_sr_scores
    for the insecure-code self-report axis). Same formula as scripts/score_mixed_generator.py.
  - selection gap = mean(value of the kept answers) - mean(value of the whole pool).
    Stored raw AND signed toward the target: every run here is an intervention that
    tries to REDUCE the value (de-risk / de-insecure), so gap_signed = -gap_raw, and
    positive gap_signed = the judge pulled toward the target.
  - value = the model's free-generation coordinate that round (traj for the risk
    runs; sr_freegen for the insecure-code run).

Cross-checks the risk reversal (oracle_hold s21) against the committed numbers in
docs/report_crossfamily_oracle.md so the formula is verified before the figure
trusts the branch-m spreads (which no report tabulates).

Run:  uv run python scripts/analysis_state_space_coords.py
Writes: experiments/state_space_coords.json  (read by the figure generator).
Stdlib + numpy only.
"""
import json
import os

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def prereg_spread(items, key):
    return float(np.mean([np.std(it[key]) for it in items]))


def round_mechanics(items, key):
    """(spread, pool, kept, gap) for one selection round, prereg formula."""
    spread = prereg_spread(items, key)
    pool = float(np.mean([np.mean(it[key]) for it in items]))
    kept = float(np.mean([it[key][i] for it in items for i in it["kept_idx"]]))
    return spread, pool, kept, kept - pool


def olmo_cell(path):
    """Return (traj, rounds_raw) for the single cell in an OLMo release JSON."""
    d = json.load(open(os.path.join(ROOT, path)))
    for sd, conds in d.items():
        if not sd.isdigit():
            continue
        for cond, res in conds.items():
            return res["traj"], res["rounds_raw"]
    raise SystemExit(f"no seed cell in {path}")


def qwen_reopen_cell(path, cellkey):
    d = json.load(open(os.path.join(ROOT, path)))
    res = d["cells"][cellkey]
    traj = [b["sr_free_gen"]["sr_freegen"] for b in res["battery"]]
    baseline = d["baselines"][res["dose"]]["sr_freegen_mean"]
    return baseline, traj, res["rounds_raw"]


# ---- runs to plot (id, human label, colour role, source) -------------------
def build():
    out = {}

    # -- risk axis (OLMo second risk model); target = low risk --
    risk_runs = [
        ("reversal", "second risk model — a score oracle walks it down", "green",
         "experiments/modal_k2_release/output/k2rel_oracle_hold_s21.json"),
        ("rail_inert", "second risk model — a 1.000 rail, answers all alike", "gray",
         "experiments/modal_k2_release/output/k2rel_oracle_hold_s22.json"),
        ("rescue", "second risk model — mixed-pool rescue (noisy)", "green",
         "experiments/modal_k2_release/output/k2rel_oracle_mix_s32.json"),
        ("cautious", "a cautious judge on the same pool", "amber",
         "experiments/modal_k2_release/output/k2rel_cons_mix_s33.json"),
        ("contamination", "a maxed-out copy added, ordinary judge keeps it", "red",
         "experiments/modal_k2_release/output/k2rel_invade_self_s37.json"),
    ]
    for rid, label, color, path in risk_runs:
        traj, rounds_raw = olmo_cell(path)
        pts = []
        for k, items in enumerate(rounds_raw, 1):
            sp, pool, kept, gap = round_mechanics(items, "cand_risk")
            pts.append(dict(round=k, spread=sp, pool=pool, kept=kept,
                            gap_raw=gap, gap_signed=-gap,
                            value_pre=traj[k - 1], value_post=traj[k],
                            drift=abs(traj[k] - traj[k - 1])))
        out[rid] = dict(label=label, color=color, axis="risk",
                        target="low", traj=traj, rounds=pts)

    # -- insecure-code self-report axis (Qwen); target = low self-report --
    baseline, traj, rounds_raw = qwen_reopen_cell(
        "experiments/em_selfaware_loop/output/mixed_reopen_qwen.json",
        "low_55_707:921")
    pts = [dict(round=0, spread=0.0, pool=None, kept=None, gap_raw=0.0,
                gap_signed=0.0, value_pre=baseline, value_post=traj[0],
                drift=abs(traj[0] - baseline))]           # r0 stuck baseline
    for k, items in enumerate(rounds_raw, 1):
        sp, pool, kept, gap = round_mechanics(items, "cand_sr_scores")
        pts.append(dict(round=k, spread=sp, pool=pool, kept=kept,
                        gap_raw=gap, gap_signed=-gap,
                        value_pre=(baseline if k == 1 else traj[k - 2]),
                        value_post=traj[k - 1],
                        drift=abs(traj[k - 1] - (baseline if k == 1 else traj[k - 2]))))
    out["reopen"] = dict(label="insecure-code model — injection reopens it",
                         color="green", axis="selfreport", target="low",
                         baseline=baseline, traj=traj, rounds=pts)
    return out


def main():
    out = build()
    with open(os.path.join(ROOT, "experiments/state_space_coords.json"), "w") as f:
        json.dump(out, f, indent=1)

    # ---- cross-check against docs/report_crossfamily_oracle.md ----
    rv = out["reversal"]["rounds"]
    got_sp = [round(r["spread"], 3) for r in rv]
    got_gap = [round(r["gap_raw"], 3) for r in rv]
    exp_sp = [0.124, 0.303, 0.242, 0.073]
    exp_gap = [-0.111, -0.306, -0.222, -0.069]
    ok = all(abs(a - b) <= 0.002 for a, b in zip(got_sp, exp_sp)) and \
        all(abs(a - b) <= 0.002 for a, b in zip(got_gap, exp_gap))
    print("reversal (oracle s21) spread:", got_sp, "expected", exp_sp)
    print("reversal (oracle s21) gap   :", got_gap, "expected", exp_gap)
    print("CROSS-CHECK vs report_crossfamily_oracle.md:", "PASS" if ok else "FAIL")
    print()
    for rid, r in out.items():
        sp = [round(p["spread"], 3) for p in r["rounds"]]
        gs = [round(p["gap_signed"], 3) for p in r["rounds"]]
        print(f"{rid:14s} value {r['traj'][0]:.3f}->{r['traj'][-1]:.3f}  "
              f"spread {sp}  gap_toward_target {gs}")


if __name__ == "__main__":
    main()
