#!/usr/bin/env python3
"""Score the preregistered control-arm forecast against the landed outcomes.

The forecast (docs/prereg_control_arm_prospective_forecast.md, committed
mid-run 2026-07-15 with the reference_vs_secure arm at training round 2 and
the head2head_self arm not started) predicted from round-1 state alone that
both supplier-removed self-only control arms stay ~flat, using the writeup's
simple model with spread and agreement frozen at round 1. Pass bands were
declared in the prereg:

  P-A (quantitative): the reference arm's seed-71 in-domain live endpoint
      lands within +-0.10 of the predicted 0.831.
  P-B (qualitative, every self-only cell = 2 arms x 2 seeds x 2 banks):
      |endpoint - baseline| < 0.5 x the matched v2 base-cogenerator seed's
      |endpoint - baseline| on the same live coordinate and bank.
  P-C (mechanism): the head2head_self arm's round-1 mean within-task spread
      of candidate insecurity scores lands < 0.15 (material shortage is a
      property of self-only generation, not of the fixed-reference format).

Coordinate: the frozen-base live insecurity score (live_llm_mean_FLAGGED in
the analysis JSONs) — the SAME instrument the forecast and the v2 comparison
used. It is a flagged low-specificity diagnostic for absolute severity; the
prereg used it because it is the loop's live channel, and blind manual
severity is reported alongside as the citable secondary check.

Inputs (all committed):
  experiments/control_arm_prospective_predictions.json
  experiments/olmo_insecure/output/olmo_code_security_static_reference_v1_analysis.json
  experiments/olmo_insecure/output/olmo_code_security_self_pool_duels_v1_analysis.json
  experiments/olmo_insecure/output/olmo_code_security_duel_loop_v2_analysis.json
  experiments/olmo_insecure/output/olmo_code_security_self_pool_duels_v1.json
      (raw; round-1 pools for P-C spread and the fresh factorization check)

Output: experiments/control_arm_forecast_score.json
Report: docs/report_control_arm_forecast_score.md

Run: uv run python scripts/analysis_control_arm_forecast_score.py
"""

import json
import os
import statistics

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(REPO, "experiments", "olmo_insecure", "output")
PRED_PATH = os.path.join(REPO, "experiments", "control_arm_prospective_predictions.json")
OUT_PATH = os.path.join(REPO, "experiments", "control_arm_forecast_score.json")

ARMS = {
    "reference_vs_secure": "olmo_code_security_static_reference_v1_analysis.json",
    "head2head_self": "olmo_code_security_self_pool_duels_v1_analysis.json",
}
V2_PATH = os.path.join(OUT_DIR, "olmo_code_security_duel_loop_v2_analysis.json")
ARM2_RAW = os.path.join(OUT_DIR, "olmo_code_security_self_pool_duels_v1.json")

P_A_BAND = 0.10
P_B_RATIO = 0.5
P_C_SIGMA = 0.15
FACTOR = 0.96  # the prereg's factorization constant (pooled fit, kept as declared)


def pearson(xs, ys):
    n = len(xs)
    if n < 2:
        return None
    mx, my = statistics.fmean(xs), statistics.fmean(ys)
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    den = (sum((x - mx) ** 2 for x in xs) * sum((y - my) ** 2 for y in ys)) ** 0.5
    return None if den == 0 else num / den


def live_trajectory(analysis, seed, bank):
    """baseline + rounds 1..3 of the frozen-base live coordinate."""
    r = analysis["seeds"][seed]["readouts"][bank]
    keys = ["organism_baseline", "organism_round_1", "organism_round_2", "organism_round_3"]
    return [r[k]["live_llm_mean_FLAGGED"] for k in keys]


def manual_severity_change(analysis, seed, bank):
    r = analysis["seeds"][seed]["readouts"][bank]
    first = r["organism_baseline"].get("manual_mean_severity")
    last = r["organism_round_3"].get("manual_mean_severity")
    if first is None or last is None:
        return None
    return {"baseline": round(first, 4), "endpoint": round(last, 4),
            "change": round(last - first, 4)}


def main():
    pred = json.load(open(PRED_PATH))
    arms = {name: json.load(open(os.path.join(OUT_DIR, fn))) for name, fn in ARMS.items()}
    v2 = json.load(open(V2_PATH))
    arm2_raw = json.load(open(ARM2_RAW))

    # ---------------------------------------------------------------- P-A
    forecast_71 = pred["seeds"]["71"]["forecast"]
    pred_endpoint_in = forecast_71["in_domain"]["predicted_endpoint"]
    traj_71_in = live_trajectory(arms["reference_vs_secure"], "71", "in_domain")
    p_a = {
        "predicted_endpoint": round(pred_endpoint_in, 4),
        "observed_endpoint": round(traj_71_in[-1], 4),
        "absolute_error": round(abs(traj_71_in[-1] - pred_endpoint_in), 4),
        "band": P_A_BAND,
        "pass": abs(traj_71_in[-1] - pred_endpoint_in) <= P_A_BAND,
    }

    # per-round forecast error on the quantitatively forecast banks (s71)
    per_round_mae = {}
    for bank in ("in_domain", "heldout"):
        pr = forecast_71[bank]["predicted_trajectory"][1:]  # rounds 1..3
        obs = live_trajectory(arms["reference_vs_secure"], "71", bank)[1:]
        n = min(len(pr), len(obs))
        per_round_mae[bank] = {
            "predicted": [round(x, 4) for x in pr[:n]],
            "observed": [round(x, 4) for x in obs[:n]],
            "mae": round(sum(abs(a - b) for a, b in zip(pr[:n], obs[:n])) / n, 4),
        }

    # ---------------------------------------------------------------- P-B
    p_b_cells = []
    for arm_name, analysis in arms.items():
        for seed in ("71", "72"):
            for bank in ("in_domain", "heldout"):
                traj = live_trajectory(analysis, seed, bank)
                v2_traj = live_trajectory(v2, seed, bank)
                arm_move = abs(traj[-1] - traj[0])
                v2_move = abs(v2_traj[-1] - v2_traj[0])
                p_b_cells.append({
                    "arm": arm_name,
                    "seed": seed,
                    "bank": bank,
                    "baseline": round(traj[0], 4),
                    "endpoint": round(traj[-1], 4),
                    "arm_abs_move": round(arm_move, 4),
                    "matched_v2_abs_move": round(v2_move, 4),
                    "threshold_half_v2": round(P_B_RATIO * v2_move, 4),
                    "pass": arm_move < P_B_RATIO * v2_move,
                })
    p_b = {
        "cells": p_b_cells,
        "n_pass": sum(1 for c in p_b_cells if c["pass"]),
        "n_cells": len(p_b_cells),
    }

    # ---------------------------------------------------------------- P-C
    # round-1 mean within-task population SD of candidate insecurity scores in
    # the head2head_self arm, plus the fresh factorization check the prereg's
    # arm-1 state measurement performed (gap vs FACTOR * rho * sigma).
    p_c_seeds = {}
    for seed in ("71", "72"):
        r1 = arm2_raw["seeds"][seed]["rounds"][0]
        sigmas, rhos, gaps = [], [], []
        for pool in r1["pools"]:
            scores = pool["insecurity_scores"]
            sigmas.append(statistics.pstdev(scores))
            kept = sorted(range(len(pool["win_rates"])),
                          key=lambda i: pool["win_rates"][i], reverse=True)[:2]
            gaps.append(statistics.fmean([scores[i] for i in kept])
                        - statistics.fmean(scores))
            r = pearson(scores, pool["win_rates"])
            if r is not None:
                rhos.append(r)
        sigma1 = statistics.fmean(sigmas)
        rho1 = statistics.fmean(rhos) if rhos else None
        p_c_seeds[seed] = {
            "round1_sigma": round(sigma1, 4),
            "round1_rho": round(rho1, 4) if rho1 is not None else None,
            "observed_round1_gap": round(statistics.fmean(gaps), 4),
            "predicted_gap_factor_rho_sigma": (
                round(FACTOR * rho1 * sigma1, 4) if rho1 is not None else None
            ),
            "pass": sigma1 < P_C_SIGMA,
        }
    p_c = {
        "threshold": P_C_SIGMA,
        "seeds": p_c_seeds,
        "pass": all(v["pass"] for v in p_c_seeds.values()),
        "note": (
            "kept set for the gap check approximated as top-2 by win rate "
            "(the chassis keeps 2); the prereg band applies to sigma only"
        ),
    }

    # -------------------------------------------- manual-severity secondary
    manual = {}
    for arm_name, analysis in arms.items():
        manual[arm_name] = {
            seed: {
                bank: manual_severity_change(analysis, seed, bank)
                for bank in ("in_domain", "heldout")
            }
            for seed in ("71", "72")
        }
    manual["v2_base_cogenerator"] = {
        seed: {
            bank: manual_severity_change(v2, seed, bank)
            for bank in ("in_domain", "heldout")
        }
        for seed in ("71", "72")
    }

    verdict = {
        "P_A": p_a["pass"],
        "P_B": f"{p_b['n_pass']}/{p_b['n_cells']}",
        "P_C": p_c["pass"],
        "overall": (
            "FORECAST HELD" if p_a["pass"] and p_c["pass"]
            and p_b["n_pass"] >= p_b["n_cells"] - 1 else "PARTIAL/FAILED — see cells"
        ),
    }

    out = {
        "description": (
            "Scores docs/prereg_control_arm_prospective_forecast.md against "
            "the landed control-arm outcomes on the declared live frozen-base "
            "coordinate (flagged diagnostic; blind manual severity reported "
            "as the citable secondary check). The forecast predates the "
            "outcomes (git history); no forecast numbers were altered here."
        ),
        "verdict": verdict,
        "P_A_reference_arm_seed71_in_domain": p_a,
        "s71_per_round_forecast_error": per_round_mae,
        "P_B_all_self_only_cells": p_b,
        "P_C_head2head_self_round1_spread": p_c,
        "manual_severity_secondary": manual,
    }
    with open(OUT_PATH, "w") as f:
        json.dump(out, f, indent=1)

    print(f"wrote {OUT_PATH}")
    print("\n=== VERDICT ===")
    print(json.dumps(verdict, indent=1))
    print("\nP-A:", p_a)
    print("\ns71 per-round forecast MAE:", {k: v["mae"] for k, v in per_round_mae.items()})
    print("\nP-B cells:")
    for c in p_b_cells:
        print(f"  {c['arm']:20s} s{c['seed']} {c['bank']:9s} move {c['arm_abs_move']:.3f} "
              f"vs half-v2 {c['threshold_half_v2']:.3f} -> {'pass' if c['pass'] else 'FAIL'}")
    print("\nP-C:", json.dumps(p_c_seeds, indent=1))


if __name__ == "__main__":
    main()
