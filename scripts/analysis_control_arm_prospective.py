"""Prospective simple-model forecast for the supplier-removed control arms.

Committed BEFORE the reference_vs_secure run finished (git timestamp is the
proof of forward prediction). Reads the round-1 checkpoint of the control-arm
artifact, measures the round-1 state (value, within-task spread, judge/value
agreement), and rolls the writeup's simple model forward with spread and
agreement frozen at round 1 — the configuration the closed-loop bakeoff
(report_spread_rollout_bakeoff.md) found best for unseen conditions.

Model (self-only pool, so pool mean = value):
    gap_t   = 0.96 * rho1 * sigma1          (selector-gap factorization)
    v_{t+1} = clip(v_t + K * gap_t, 0, 1)   (K = 0.79, LORO fit from
                                             report_simple_model_rollout.md)

Coordinate: the frozen-base live insecurity score logged by the chassis
(the loop's own live channel — the SAME instrument as the v2 trajectory it
is compared to; low-specificity for absolute severity, fine for movement).

Usage:
  uv run python scripts/analysis_control_arm_prospective.py \
      --input experiments/olmo_insecure/output/olmo_code_security_static_reference_v1_partial_r1.json \
      --output experiments/control_arm_prospective_predictions.json
"""

import argparse
import json
import statistics

K_GAIN = 0.79          # movement gain, LORO fit (report_simple_model_rollout.md)
FACTOR = 0.96          # gap = 0.96 * rho * sigma (report_spread_util_unified.md)
TOTAL_ROUNDS = 3       # the run's configured rounds


def pearson(xs, ys):
    n = len(xs)
    if n < 2:
        return None
    mx, my = statistics.fmean(xs), statistics.fmean(ys)
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    den = (sum((x - mx) ** 2 for x in xs) * sum((y - my) ** 2 for y in ys)) ** 0.5
    return None if den == 0 else num / den


def round1_state(round_block):
    sigmas, rhos, kept_means, pool_means = [], [], [], []
    for pool in round_block["pools"]:
        scores = pool["insecurity_scores"]
        sigmas.append(statistics.pstdev(scores))
        pool_means.append(statistics.fmean(scores))
        kept_means.append(statistics.fmean(
            [scores[i] for i in pool["kept_idx"]]))
        r = pearson(scores, pool["win_rates"])
        if r is not None:
            rhos.append(r)
    return {
        "sigma1": statistics.fmean(sigmas),
        "rho1": statistics.fmean(rhos),
        "pool_mean": statistics.fmean(pool_means),
        "kept_mean": statistics.fmean(kept_means),
        "observed_gap": statistics.fmean(kept_means) - statistics.fmean(pool_means),
    }


def rollout(v0, sigma1, rho1, rounds=TOTAL_ROUNDS):
    gap = FACTOR * rho1 * sigma1
    trajectory = [v0]
    v = v0
    for _ in range(rounds):
        v = min(1.0, max(0.0, v + K_GAIN * gap))
        trajectory.append(v)
    return gap, trajectory


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    data = json.load(open(args.input))
    cfg = data.get("_config", {})
    out = {
        "what": ("Prospective forecast of the supplier-removed control arms, "
                 "made from round-1 logged state only, before the runs "
                 "finished. Frozen sigma/rho rollout per the bakeoff's best "
                 "unseen-condition configuration."),
        "model": {"K": K_GAIN, "factor": FACTOR, "rounds": TOTAL_ROUNDS,
                  "spread": "frozen at round 1", "agreement": "frozen at round 1"},
        "input_selection_mode": cfg.get("selection_mode"),
        "input_run_tag": cfg.get("run_tag"),
        "seeds": {},
    }
    for seed, rec in data.get("seeds", {}).items():
        rounds = rec.get("rounds", [])
        if not rounds:
            continue
        state = round1_state(rounds[0])
        seed_out = {"round1_state": {k: round(v, 4) for k, v in state.items()},
                    "factorization_check": {
                        "predicted_gap_0.96_rho_sigma":
                            round(FACTOR * state["rho1"] * state["sigma1"], 4),
                        "observed_gap": round(state["observed_gap"], 4)},
                    "forecast": {}}
        for bank in ("in_domain", "heldout"):
            v0 = rec["baseline"][bank]["mean_insecurity"]
            gap, traj = rollout(v0, state["sigma1"], state["rho1"])
            seed_out["forecast"][bank] = {
                "v0": round(v0, 4),
                "per_round_gap": round(gap, 4),
                "predicted_trajectory": [round(x, 4) for x in traj],
                "predicted_endpoint": round(traj[-1], 4),
            }
        out["seeds"][seed] = seed_out

    json.dump(out, open(args.output, "w"), indent=2)
    print(f"wrote {args.output}")
    for seed, s in out["seeds"].items():
        st = s["round1_state"]
        print(f"seed {seed}: sigma1={st['sigma1']} rho1={st['rho1']} "
              f"gap obs={st['observed_gap']} "
              f"pred={s['factorization_check']['predicted_gap_0.96_rho_sigma']}")
        for bank, f in s["forecast"].items():
            print(f"  {bank}: {f['v0']} -> predicted endpoint "
                  f"{f['predicted_endpoint']} "
                  f"(trajectory {f['predicted_trajectory']})")


if __name__ == "__main__":
    main()
