"""What within-prompt spread does a VALUE-BLIND judge manufacture in this design?

The value-covariance phase-1 gate asks whether candidates differ on an axis by more
than the scoring construction would produce on its own. Two incompatible answers are
in the repo and neither is reproducible:

  * experiments/value_covariance/script.py implements
    `null_floor = order_gap * 0.5 / sqrt(n_candidates - 1)` = 0.115 at the observed
    order gap of 0.609, which passes 5 of 6 judge-A axes.
  * The comment directly above that line, report_value_covariance_phase1.md and the
    ledger row all state the floor is ~0.167 "by simulation", which fails all six.
    No script for that simulation was ever committed.

This script settles it by simulating `score_pool`'s exact accounting (from
experiments/value_covariance/script.py) under a judge that cannot see value at all,
calibrated to reproduce the observed order gap.

THE ACCOUNTING BEING MIRRORED. For each prompt and axis, each of n_c candidates
draws n_opp opponents from the same pool. Each drawn pair is judged TWICE, once in
each presentation order. Candidate i banks P(first) when it is shown first and
1 - P(first) when it is shown second, then averages its 2 * n_opp reads. The
reported order gap is mean |p_ij + p_ji - 1| over pairs, where p_ij is P(first) with
i shown first.

WHY A LITERALLY IDENTICAL POOL IS THE WRONG NULL. If every candidate were the same
string, every comparison prompt would be the same string, a deterministic logprob
read would return one constant q, and every candidate would score exactly 0.5 with
zero spread. The floor is not about identical text. It is about a judge whose read
does not depend on WHICH candidate is in which slot -- position plus per-call
idiosyncrasy. That is what is simulated here.

Because the shape of the judge's per-call response distribution is not recoverable
(script.py discards per-comparison probabilities), three different null families are
run, each calibrated to the same observed order gap, and the spread of answers across
families is the honest uncertainty.

Writes experiments/winrate_null_floor.json.
"""

import json
import pathlib

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "experiments/winrate_null_floor.json"

N_CAND = 8          # candidates per prompt, phase-1 config
N_OPP = 3           # opponents sampled per candidate
N_PROMPT = 30       # prompts per pool set
N_SIM = 4000        # simulated pools per calibration point
OBSERVED_GAP = 0.60872          # judge A, from value_covariance_phase1.json
OBSERVED_GAP_B = 0.23792        # judge B
RNG = np.random.default_rng(20260728)


# --- null response families -------------------------------------------------
# Each takes a parameter and returns per-call P(first) draws. All are value-blind:
# the draw does not depend on which candidates are in the slots.

def family_position_bernoulli(theta, size, rng):
    """Confident judge that answers on position: picks the first answer with
    probability theta, and its logprob read saturates at 0 or 1."""
    return (rng.random(size) < theta).astype(float)


def family_position_soft(theta, size, rng):
    """Same position-driven decision, but the read sits at 0.5 +/- theta rather
    than saturating -- a judge that leans without committing."""
    return 0.5 + theta * np.where(rng.random(size) < 0.5, 1.0, -1.0)


def family_symmetric_beta(theta, size, rng):
    """No position bias at all, pure per-call idiosyncrasy: P(first) ~ Beta(t, t).
    Small t means near-saturated reads, large t means reads hugging 0.5."""
    return rng.beta(theta, theta, size=size)


FAMILIES = {
    "position_bernoulli": (family_position_bernoulli, (0.5, 0.9999)),
    "position_soft": (family_position_soft, (0.0001, 0.5)),
    "symmetric_beta": (family_symmetric_beta, (0.01, 50.0)),
}


# --- simulate one pool ------------------------------------------------------

def simulate(draw, theta, n_pool, rng):
    """Return (within-prompt SDs, order gaps) over n_pool simulated pools."""
    sds, gaps = [], []
    for _ in range(n_pool):
        # opponent draw, mirroring `rng.shuffle(opps); opps[:n_opp]`
        pairs = []
        for i in range(N_CAND):
            opps = [j for j in range(N_CAND) if j != i]
            rng.shuffle(opps)
            pairs.extend((i, j) for j in opps[:N_OPP])
        # two calls per pair: (i first) and (j first)
        p_ij = draw(theta, len(pairs), rng)
        p_ji = draw(theta, len(pairs), rng)
        wins = [[] for _ in range(N_CAND)]
        for k, (i, _j) in enumerate(pairs):
            wins[i].append(p_ij[k])          # i shown first
            wins[i].append(1.0 - p_ji[k])    # i shown second
        scores = np.array([np.mean(w) for w in wins])
        sds.append(float(np.std(scores)))
        gaps.append(float(np.mean(np.abs(p_ij + p_ji - 1.0))))
    return np.array(sds), np.array(gaps)


def calibrate(name, target_gap, rng, tol=1e-3, iters=40):
    """Bisect the family parameter until the simulated order gap matches."""
    draw, (lo, hi) = FAMILIES[name]

    def gap_at(t):
        return float(simulate(draw, t, 400, rng)[1].mean())

    g_lo, g_hi = gap_at(lo), gap_at(hi)
    if not (min(g_lo, g_hi) - 0.02 <= target_gap <= max(g_lo, g_hi) + 0.02):
        return None, {"reachable_gap_range": [round(min(g_lo, g_hi), 4),
                                              round(max(g_lo, g_hi), 4)]}
    ascending = g_hi > g_lo
    for _ in range(iters):
        mid = 0.5 * (lo + hi)
        g = gap_at(mid)
        if abs(g - target_gap) < tol:
            break
        if (g < target_gap) == ascending:
            lo = mid
        else:
            hi = mid
    return mid, {"achieved_gap": round(g, 4)}


def run(target_gap, label, rng):
    out = {"label": label, "target_order_gap": target_gap, "families": {}}
    floors = []
    for name in FAMILIES:
        theta, info = calibrate(name, target_gap, rng)
        if theta is None:
            out["families"][name] = {"status": "cannot reach this order gap", **info}
            continue
        draw, _ = FAMILIES[name]
        sds, gaps = simulate(draw, theta, N_SIM, rng)
        # the gate compares the MEAN within-prompt SD over 30 prompts against the
        # floor, so the relevant null is the sampling distribution of that mean
        means = sds[: (len(sds) // N_PROMPT) * N_PROMPT].reshape(-1, N_PROMPT).mean(axis=1)
        out["families"][name] = {
            "theta": round(float(theta), 5),
            "achieved_order_gap": round(float(gaps.mean()), 4),
            "null_within_prompt_sd_mean": round(float(sds.mean()), 5),
            "null_mean_over_30_prompts_p95": round(float(np.quantile(means, 0.95)), 5),
            "null_mean_over_30_prompts_ci95": [round(float(np.quantile(means, 0.025)), 5),
                                               round(float(np.quantile(means, 0.975)), 5)],
        }
        floors.append(float(sds.mean()))
    if floors:
        out["floor_range_across_families"] = [round(min(floors), 5), round(max(floors), 5)]
    return out


def main():
    res = {
        "design": {"n_candidates": N_CAND, "n_opponents": N_OPP,
                   "reads_per_candidate": 2 * N_OPP, "n_prompts": N_PROMPT,
                   "n_sim_pools": N_SIM},
        "note": "Value-blind judge: the per-call read does not depend on which "
                "candidate occupies which slot. Calibrated to the observed order gap.",
    }
    res["judge_a"] = run(OBSERVED_GAP, "judge_a (Qwen3-4B)", RNG)
    res["judge_b"] = run(OBSERVED_GAP_B, "judge_b (Gemma-2-2b-it)", RNG)

    # what script.py's analytic formula would say, for comparison
    res["script_py_analytic_floor"] = {
        "formula": "order_gap * 0.5 / sqrt(n_candidates - 1)",
        "judge_a": round(OBSERVED_GAP * 0.5 / np.sqrt(N_CAND - 1), 5),
        "judge_b": round(OBSERVED_GAP_B * 0.5 / np.sqrt(N_CAND - 1), 5),
        "problem": "divides by sqrt(n_candidates - 1) though each candidate has "
                   "2 * n_opponents = 6 reads, and scales linearly by the order gap "
                   "instead of inverting the gap for the judge's response spread",
    }

    # observed judge-A within-prompt SDs, for the verdict
    src = json.load(open(ROOT / "experiments/value_covariance/output/value_covariance_phase1.json"))
    for j in ("judge_a", "judge_b"):
        obs = {a: v["mean_within_prompt_sd"]
               for a, v in src["instrument_check"][j]["per_axis"].items()}
        fl = res[j].get("floor_range_across_families")
        res[j]["observed_within_prompt_sd"] = obs
        if fl:
            res[j]["axes_above_every_family_floor"] = [a for a, v in obs.items() if v > fl[1]]
            res[j]["axes_below_every_family_floor"] = [a for a, v in obs.items() if v < fl[0]]

    OUT.write_text(json.dumps(res, indent=2))
    print(f"wrote {OUT.relative_to(ROOT)}")
    for j in ("judge_a", "judge_b"):
        print(f"\n{res[j]['label']}  target gap {res[j]['target_order_gap']}")
        for name, f in res[j]["families"].items():
            if "null_within_prompt_sd_mean" in f:
                print(f"  {name:>20}: null SD {f['null_within_prompt_sd_mean']:.4f} "
                      f"(gap {f['achieved_order_gap']})")
            else:
                print(f"  {name:>20}: {f['status']} {f.get('reachable_gap_range')}")
        print(f"  floor range {res[j].get('floor_range_across_families')}")
        print(f"  observed    {res[j]['observed_within_prompt_sd']}")
        print(f"  above ALL family floors: {res[j].get('axes_above_every_family_floor')}")
    print("\nscript.py analytic floor:", res["script_py_analytic_floor"]["judge_a"],
          "(judge A)")


if __name__ == "__main__":
    main()
