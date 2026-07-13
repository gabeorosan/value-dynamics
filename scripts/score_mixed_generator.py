"""Scorer for the cross-family oracle (branch e) and mixed-generator
(branch m + Qwen mixed-reopen) preregistrations.

AUTHORSHIP TIME (honesty note, per the 07-13 full-program audit): written
2026-07-13 ~08:55, AFTER the experiments were launched and after branch e's
in-flight log lines (r0-r3 gen values for seeds 21/22) had been seen, but
BEFORE any terminal branch-e/branch-m/Qwen-mixed artifact was opened. The
prereg criteria implemented here are the ones committed before launch
(docs/prereg_crossfamily_oracle.md, docs/prereg_mixed_generator.md), with
the audit's scoring corrections applied:

- P4 is NOT scored as a zero-intercept 0.740 law. We report (a) observed
  next-pool drift versus realized kept-gap descriptively, and (b) the frozen
  M2 prediction (arm intercept + 0.740 x gap) ONLY where judge_used maps to
  a fitted K2 arm, with ABSOLUTE error (the prereg's +/-50% relative-error
  criterion is unstable near zero and is reported but not treated as the
  verdict).
- Owner balance: the prereg assumed 3+3 pools. Any round where a half-pool
  came up short (soft validity shortfall) is flagged, and owner shares are
  reported only over rounds with exact balance, with shortfall rounds
  enumerated.
- Spread is ALWAYS the prereg formula: mean over items of the within-item
  candidate-score SD.
- Missing-force accounting: a round with prereg spread < 0.05 on the
  selected axis is a missing-force round, never "resistance".

Usage:
  uv run python scripts/score_mixed_generator.py olmo FILE [FILE ...]
  uv run python scripts/score_mixed_generator.py qwen FILE
"""

import json
import sys

import numpy as np

FROZEN_PREDICTOR = "experiments/release_predictor_frozen.json"


def prereg_spread(items, key):
    return float(np.mean([np.std(it[key]) for it in items]))


def owner_counts(it):
    own = it.get("cand_owner")
    if not own:
        return None
    return {"self": own.count("self"), "cogen": own.count("cogen")}


def score_olmo_cell(res, label):
    """One OLMo rollout cell: trajectory, per-round pool mechanics, owner
    accounting, and the prereg criteria that apply to its condition."""
    traj = res["traj"]
    rows = []
    for rd, items in enumerate(res["rounds_raw"], 1):
        spread = prereg_spread(items, "cand_risk")
        pool = float(np.mean([np.mean(it["cand_risk"]) for it in items]))
        kept = float(np.mean([it["cand_risk"][i] for it in items
                              for i in it["kept_idx"]]))
        gap = kept - pool
        balance = [owner_counts(it) for it in items]
        mixed = balance[0] is not None
        short = [i for i, b in enumerate(balance)
                 if mixed and (b["self"] + b["cogen"] < 6 or b["cogen"] != 3)]
        if mixed:
            balanced = [it for it, b in zip(items, balance)
                        if b["self"] + b["cogen"] == 6 and b["cogen"] == 3]
            kept_cogen = (float(np.mean(
                [it["cand_owner"][i] == "cogen" for it in balanced
                 for i in it["kept_idx"]])) if balanced else None)
            risk_by_owner = {
                o: float(np.mean([r for it in items
                                  for r, w in zip(it["cand_risk"],
                                                  it["cand_owner"]) if w == o]))
                for o in ("self", "cogen")}
        else:
            kept_cogen, risk_by_owner = None, None
        rows.append({"round": rd, "pool_risk": pool, "kept_risk": kept,
                     "realized_gap": gap, "spread_prereg": spread,
                     "missing_force": spread < 0.05,
                     "kept_cogen_share_balanced": kept_cogen,
                     "risk_by_owner": risk_by_owner,
                     "owner_shortfall_items": short if mixed else None,
                     "judge_used": (res.get("judge_used") or [None] * 9)[rd - 1]})
    out = {"label": label, "traj": traj, "rounds": rows,
           "reversal_r0_minus_end": (traj[0] - traj[-1]) if len(traj) > 1 else None}

    # descriptive drift-vs-gap (audit-corrected P4): next-pool movement per
    # round against realized gap; frozen M2 only for judge_used with a
    # fitted arm
    try:
        frozen = json.load(open(FROZEN_PREDICTOR))
        arms = frozen["intercepts"]
        j2a = frozen.get("judge_to_arm", {})
        slope = frozen["gap_slope"]
    except Exception:
        arms, j2a, slope = {}, {}, 0.740
    drift_rows = []
    for i in range(len(rows) - 1):
        obs = rows[i + 1]["pool_risk"] - rows[i]["pool_risk"]
        j = j2a.get(rows[i]["judge_used"], rows[i]["judge_used"])
        pred = (arms[j] + slope * rows[i]["realized_gap"]) if j in arms else None
        drift_rows.append({"from_round": rows[i]["round"], "observed_pool_drift": obs,
                           "realized_gap": rows[i]["realized_gap"],
                           "frozen_m2_pred": pred,
                           "abs_err": abs(obs - pred) if pred is not None else None})
    out["drift_vs_gap"] = drift_rows
    return out


def cmd_olmo(paths):
    report = {}
    for p in paths:
        d = json.load(open(p))
        for sd, conds in d.items():
            if not sd.isdigit():
                continue
            for cond, res in conds.items():
                label = f"{cond}_s{sd}"
                report[label] = score_olmo_cell(res, label)
    # prereg criteria over the collected cells
    crits = []
    orc = {k: v for k, v in report.items() if k.startswith(("oracle_hold", "oracle_mix"))}
    for k, v in sorted(report.items()):
        end = v["traj"][-1]
        rev = v["reversal_r0_minus_end"]
        supported = [r for r in v["rounds"] if not r["missing_force"]]
        crits.append(f"{k}: r0={v['traj'][0]:.3f} end={end:.3f} reversal={rev:+.3f} "
                     f"supported_rounds={len(supported)}/{len(v['rounds'])} "
                     f"spreads={[round(r['spread_prereg'], 3) for r in v['rounds']]}")
        for r in v["rounds"]:
            if r["kept_cogen_share_balanced"] is not None:
                crits.append(f"  r{r['round']}: kept_cogen_share={r['kept_cogen_share_balanced']:.2f} "
                             f"risk self={r['risk_by_owner']['self']:.2f} cogen={r['risk_by_owner']['cogen']:.2f} "
                             f"gap={r['realized_gap']:+.3f} spread={r['spread_prereg']:.3f}"
                             + (f" SHORTFALL items {r['owner_shortfall_items']}" if r["owner_shortfall_items"] else ""))
    # branch e prereg: reversal >= 0.30 both cells; gap <= -0.10 while
    # spread > 0.05; zero-spread rounds are missing-force
    if orc:
        crits.append("-- prereg verdicts (crossfamily oracle: reversal>=0.30; "
                     "mixed P1: spread>0.05 every round; P2: reversal>=0.30 in >=1 mixed-oracle cell) --")
        for k, v in sorted(orc.items()):
            ok_rev = v["reversal_r0_minus_end"] is not None and v["reversal_r0_minus_end"] >= 0.30
            grip = [r for r in v["rounds"] if r["spread_prereg"] > 0.05 and r["realized_gap"] <= -0.10]
            mf = [r["round"] for r in v["rounds"] if r["missing_force"]]
            crits.append(f"{k}: reversal>=0.30 {'PASS' if ok_rev else 'FAIL'}; "
                         f"gripped_rounds={len(grip)}; missing_force_rounds={mf}")
    print(json.dumps(report, indent=1)[:2000] + "\n...")
    print("\n".join(crits))
    return report


def cmd_qwen(path):
    d = json.load(open(path))
    for key, res in d.get("cells", {}).items():
        print(f"== {key} (mix_gen={res.get('mix_gen')}, judge={res.get('judge_style')}) ==")
        sr_traj = [b["sr_free_gen"]["sr_freegen"] for b in res["battery"]]
        base = d.get("baselines", {}).get(res["dose"], {}).get("sr_freegen_mean")
        print(f"sr_freegen: baseline={base} rounds={[round(x, 3) for x in sr_traj]}")
        for rd, items in enumerate(res["rounds_raw"], 1):
            spread = prereg_spread(items, "cand_sr_scores")
            pool = float(np.mean([np.mean(it["cand_sr_scores"]) for it in items]))
            kept = float(np.mean([it["cand_sr_scores"][i] for it in items
                                  for i in it["kept_idx"]]))
            own = items[0].get("cand_owner")
            note = ""
            if own:
                bal = [owner_counts(it) for it in items]
                short = [i for i, b in enumerate(bal) if b["cogen"] != 3 or b["self"] + b["cogen"] != 6]
                ks = float(np.mean([it["cand_owner"][i] == "cogen" for it in items
                                    for i in it["kept_idx"]]))
                sr_by = {o: float(np.mean([s for it in items
                                           for s, w in zip(it["cand_sr_scores"], it["cand_owner"]) if w == o]))
                         for o in ("self", "cogen")}
                note = (f" kept_cogen={ks:.2f} sr self={sr_by['self']:.2f} cogen={sr_by['cogen']:.2f}"
                        + (f" SHORTFALL {short}" if short else ""))
            print(f"r{rd}: pool_sr={pool:.3f} kept_sr={kept:.3f} gap={kept - pool:+.3f} "
                  f"spread_prereg={spread:.3f}{'  MISSING-FORCE' if spread < 0.05 else ''}{note}")
        # prereg P1/P2 (Qwen cell): spread>0.05 every round; sr_freegen < 0.55
        sp_ok = all(prereg_spread(it, "cand_sr_scores") > 0.05 for it in res["rounds_raw"])
        p2 = min(sr_traj) < 0.55
        print(f"P1 spread>0.05 all rounds: {'PASS' if sp_ok else 'FAIL'}; "
              f"P2 sr_freegen<0.55: {'PASS' if p2 else 'FAIL'} (min={min(sr_traj):.3f})")


if __name__ == "__main__":
    mode, files = sys.argv[1], sys.argv[2:]
    if mode == "olmo":
        cmd_olmo(files)
    elif mode == "qwen":
        cmd_qwen(files[0])
    else:
        raise SystemExit("mode must be olmo or qwen")
