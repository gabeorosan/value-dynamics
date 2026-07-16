#!/usr/bin/env python3
"""Model check on the Qwen supplier-removed self-only run.

The trajectory scorer (analysis_qwen_selfonly_trajectories.py) established the
channel outcomes: forced-choice p_insecure amplifies 0.341 -> 0.793/0.913 while
free-text sr_freegen declines mildly with its support dying. This analysis asks
what the writeup's model sees in the same run: the per-round selector state
(spread sigma, agreement rho, selector gap) on the candidate self-description
scores, for the supplier-removed run AND its supplier-present twin — so the
reversal can be read in the model's own variables.

Per prompt j in a round: candidates have value scores x_jk = cand_sr_scores
(the frozen scorer's 0-1 insecure-self-description estimate), judge scores
s_jk (`scores`), and kept indices. sigma_j = population SD of x_jk; rho_j =
Pearson(s_jk, x_jk); gap_j = kept mean - pool mean. Round aggregates average
over prompts (rho over prompts where both sides vary).

Inputs (committed):
  experiments/em_selfaware_loop/output/head2head_selfjudge_selfonly.json
      (supplier-removed: MIX_GEN=self, self-judge duels, seeds 41/42)
  experiments/em_selfaware_loop/output/head2head_selfjudge.json
      (supplier-present twin: base co-generator, same judge & format)

Output: experiments/qwen_selfonly_model_check.json
Run: uv run python scripts/analysis_qwen_selfonly_model_check.py
"""

import json
import os
import statistics

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(REPO, "experiments", "em_selfaware_loop", "output")
SELFONLY = os.path.join(OUT_DIR, "head2head_selfjudge_selfonly.json")
SUPPLIER = os.path.join(OUT_DIR, "head2head_selfjudge.json")
OUT = os.path.join(REPO, "experiments", "qwen_selfonly_model_check.json")


def pearson(xs, ys):
    n = len(xs)
    if n < 2:
        return None
    mx, my = statistics.fmean(xs), statistics.fmean(ys)
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    den = (sum((x - mx) ** 2 for x in xs) * sum((y - my) ** 2 for y in ys)) ** 0.5
    return None if den == 0 else num / den


def round_state(items):
    sigmas, rhos, gaps, pool_means, kept_means = [], [], [], [], []
    for it in items:
        x = it["cand_sr_scores"]
        s = it["scores"]
        kept = it["kept_idx"]
        sigmas.append(statistics.pstdev(x))
        pool_means.append(statistics.fmean(x))
        kept_means.append(statistics.fmean([x[i] for i in kept]))
        gaps.append(kept_means[-1] - pool_means[-1])
        r = pearson(s, x)
        if r is not None:
            rhos.append(r)
    return {
        "sigma": round(statistics.fmean(sigmas), 4),
        "rho": round(statistics.fmean(rhos), 4) if rhos else None,
        "n_prompts_with_rho": len(rhos),
        "pool_mean": round(statistics.fmean(pool_means), 4),
        "kept_mean": round(statistics.fmean(kept_means), 4),
        "gap": round(statistics.fmean(gaps), 4),
        "predicted_gap_rho_sigma": (
            round(statistics.fmean(rhos) * statistics.fmean(sigmas), 4)
            if rhos else None
        ),
    }


def cell_states(path):
    data = json.load(open(path))
    out = {}
    for cell_key, cell in data["cells"].items():
        rounds = [round_state(items) for items in cell["rounds_raw"]]
        out[cell_key] = rounds
    return out


def p_insecure_trajectories(path):
    """Forced-choice self_report_code.mean_p_insecure per round per cell."""
    data = json.load(open(path))
    return {
        cell_key: [round(r["self_report_code"]["mean_p_insecure"], 4)
                   for r in cell["battery"]]
        for cell_key, cell in data["cells"].items()
    }


def main():
    selfonly = cell_states(SELFONLY)
    supplier = cell_states(SUPPLIER)

    # sanity: supplier-present round-1 agreement should reproduce the
    # published rho ~= -0.24 (averaged over its cells)
    sup_r1 = [rounds[0]["rho"] for rounds in supplier.values()
              if rounds[0]["rho"] is not None]
    sup_r1_mean = round(statistics.fmean(sup_r1), 4)

    self_r1 = [rounds[0]["rho"] for rounds in selfonly.values()
               if rounds[0]["rho"] is not None]
    self_r1_mean = round(statistics.fmean(self_r1), 4)

    out = {
        "what": (
            "Per-round selector state (spread sigma, agreement rho, selector "
            "gap) on candidate self-description scores, for the "
            "supplier-removed Qwen self-only run and its supplier-present "
            "twin. Reads the model's own variables off both runs so the "
            "forced-choice reversal can be interpreted in one lens."
        ),
        "value_score": "cand_sr_scores (frozen scorer, insecure self-description, 0-1)",
        "supplier_removed": selfonly,
        "supplier_present_twin": supplier,
        "round1_agreement": {
            "supplier_removed_mean": self_r1_mean,
            "supplier_present_mean": sup_r1_mean,
            "published_supplier_present": -0.24,
        },
        "forced_choice_p_insecure": {
            "baseline": 0.3405,
            "baseline_source": "experiments/qwen_selfonly_trajectories.json",
            "supplier_removed": p_insecure_trajectories(SELFONLY),
            "supplier_present_twin": p_insecure_trajectories(SUPPLIER),
        },
    }
    with open(OUT, "w") as f:
        json.dump(out, f, indent=1)
    print(f"wrote {OUT}")
    print(f"\nround-1 agreement: supplier-removed {self_r1_mean} "
          f"vs supplier-present {sup_r1_mean} (published -0.24)")
    for name, cells in (("supplier_removed", selfonly),
                        ("supplier_present", supplier)):
        for ck, rounds in cells.items():
            print(f"\n{name} {ck}:")
            for i, r in enumerate(rounds, 1):
                print(f"  round {i}: sigma={r['sigma']:.3f} rho={r['rho'] if r['rho'] is not None else 'n/a'} "
                      f"gap={r['gap']:+.3f} pred_gap={r['predicted_gap_rho_sigma'] if r['predicted_gap_rho_sigma'] is not None else 'n/a'} "
                      f"pool={r['pool_mean']:.3f}")


if __name__ == "__main__":
    main()
