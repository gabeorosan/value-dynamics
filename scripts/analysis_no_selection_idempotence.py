"""Is self-training without selection idempotent, as Roe et al. report?

Roe, Sanderson, Nguyen, Huang, Nief, Shrivastava, Tan & Holtzman, "Iterative
Finetuning is Mostly Idempotent" (arXiv 2605.01130) seed a model with a persona
and then train each generation on its predecessor's outputs. Their finding for
supervised finetuning: "traits mostly decay or remain constant so that further
finetuning cycles do nothing." Amplification appears only under DPO with
continual training, and "vanishes when models are reinitialized".

That is the closest published neighbour to this project and it needs an explicit
answer, because it could be read as contradicting the whole program. It does not
— their SFT setting has no selection step, which makes it our zero-gap condition
rather than our experiment — but "it does not contradict us" is a claim that has
to be checked rather than asserted.

Three things are checked here.

  1. RANDOM SELECTION IS NOT ZERO SELECTION. A random selector picking 2 of 6
     candidates still realises a nonzero differential every round, by chance.
     An earlier pass flagged random-selector arms as a dissenting slice showing
     movement without selection; this recomputes their mean |gap| before
     drawing that conclusion, and asks whether their movement is explained by
     the realised gap at the same coefficient as everything else.

  2. ROUND-LEVEL IDEMPOTENCE. On rounds where the realised gap really is near
     zero, is the movement distinguishable from re-measuring the same model?
     The comparator is a per-row measurement-noise floor, not zero, and the
     ratio carries a bootstrap interval so "below noise" is a statement with an
     error bar.

  3. RUN-LEVEL IDEMPOTENCE, which is the level Roe et al. actually work at.
     A run can be idempotent round by round and still walk somewhere over four
     rounds. For runs whose whole trajectory accumulated little selection, is
     the endpoint distinguishable from the start?

Writes experiments/no_selection_idempotence.json.
"""

from __future__ import annotations

import json
import math
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
UNIFIED = ROOT / "experiments/spread_util_unified.json"
OUT = ROOT / "experiments/no_selection_idempotence.json"

NEAR_ZERO_GAP = 0.01
BOOTSTRAP_DRAWS = 10000
SEED = 20260728

# E|X| for X ~ N(0, s^2) is s*sqrt(2/pi): the expected absolute change if
# nothing moved and the value was merely re-measured.
HALF_NORMAL = math.sqrt(2.0 / math.pi)


def run_key(rec):
    return rec["cond"], rec["seed"], rec["source"]


def load():
    unified = json.loads(UNIFIED.read_text())
    runs = defaultdict(list)
    for rec in unified["records"]:
        if rec.get("gap") is None or rec.get("drift") is None:
            continue
        runs[run_key(rec)].append(rec)
    for rows in runs.values():
        rows.sort(key=lambda r: r["round"])

    rows = []
    for key, run_rows in runs.items():
        for rec in run_rows:
            se_t = rec.get("value_measurement_se")
            se_next = rec.get("next_value_measurement_se")
            if se_t is None or se_next is None:
                floor = None
            else:
                floor = math.sqrt(se_t ** 2 + se_next ** 2) * HALF_NORMAL
            rows.append({
                "run": key,
                "round": int(rec["round"]),
                "gap": float(rec["gap"]),
                "drift": float(rec["drift"]),
                "value": float(rec["value"]),
                "supply": float(rec["pool_mean"]) - float(rec["value"]),
                "judge": rec["judge"],
                "organism": rec["organism"],
                "composition": rec["composition"],
                "noise_floor": floor,
            })
    return unified, dict(runs), rows


def ratio_block(rows, label):
    """Observed mean |drift| against the mean measurement-noise floor."""
    # A zero floor means both readouts were saturated (p(1-p) = 0), so there is
    # no scale to compare against; those rows are dropped and counted.
    candidates = [r for r in rows if r["noise_floor"] is not None]
    usable = [r for r in candidates if r["noise_floor"] > 1e-9]
    dropped_zero_floor = len(candidates) - len(usable)
    if len(usable) < 5:
        return {"label": label, "n": len(usable), "insufficient": True}
    obs = np.array([abs(r["drift"]) for r in usable])
    floor = np.array([r["noise_floor"] for r in usable])
    rng = np.random.default_rng(SEED)
    draws = []
    for _ in range(BOOTSTRAP_DRAWS):
        idx = rng.integers(0, len(usable), len(usable))
        draws.append(obs[idx].mean() / floor[idx].mean())
    draws = np.array(draws)
    return {
        "label": label,
        "n": len(usable),
        "n_dropped_zero_noise_floor": dropped_zero_floor,
        "n_runs": len({r["run"] for r in usable}),
        "mean_abs_gap": float(np.mean([abs(r["gap"]) for r in usable])),
        "mean_signed_drift": float(np.mean([r["drift"] for r in usable])),
        "mean_abs_drift": float(obs.mean()),
        "mean_noise_floor": float(floor.mean()),
        "ratio": float(obs.mean() / floor.mean()),
        "ratio_ci": [float(np.percentile(draws, 2.5)),
                     float(np.percentile(draws, 97.5))],
        "fraction_beyond_2_noise_sd": float(np.mean(
            [abs(r["drift"]) / (r["noise_floor"] / HALF_NORMAL) > 2
             for r in usable])),
    }


def response_coefficient(rows, label):
    """drift ~ (pool offset) + gap, with a run-clustered bootstrap on the gap term."""
    if len(rows) < 10:
        return {"label": label, "n": len(rows), "insufficient": True}
    def fit(sample):
        g = np.array([r["gap"] for r in sample])
        if np.var(g) < 1e-12:
            return None
        X = np.column_stack([np.ones(len(sample)),
                             np.array([r["supply"] for r in sample]), g])
        y = np.array([r["drift"] for r in sample])
        try:
            beta, *_ = np.linalg.lstsq(X, y, rcond=None)
        except np.linalg.LinAlgError:
            return None
        return float(beta[2])

    point = fit(rows)
    by_run = defaultdict(list)
    for r in rows:
        by_run[r["run"]].append(r)
    keys = list(by_run)
    rng = np.random.default_rng(SEED)
    draws = []
    for _ in range(BOOTSTRAP_DRAWS // 2):
        sample = []
        for i in rng.integers(0, len(keys), len(keys)):
            sample.extend(by_run[keys[i]])
        val = fit(sample)
        if val is not None and math.isfinite(val):
            draws.append(val)
    arr = np.array(draws)
    return {
        "label": label,
        "n": len(rows),
        "n_runs": len(keys),
        "mean_abs_gap": float(np.mean([abs(r["gap"]) for r in rows])),
        "gap_coefficient": point,
        "gap_coefficient_ci": [float(np.percentile(arr, 2.5)),
                               float(np.percentile(arr, 97.5))] if len(arr) > 100
                              else None,
    }


def run_level(runs, rows):
    """Endpoint movement against a run's own start, by how much selection it saw."""
    by_run = defaultdict(list)
    for r in rows:
        by_run[r["run"]].append(r)

    entries = []
    for key, rr in by_run.items():
        rr = sorted(rr, key=lambda r: r["round"])
        cumulative = float(np.sum([abs(r["gap"]) for r in rr]))
        v_start = rr[0]["value"]
        v_end = rr[-1]["value"] + rr[-1]["drift"]
        floors = [r["noise_floor"] for r in rr
                  if r["noise_floor"] is not None and r["noise_floor"] > 1e-9]
        if not floors:
            continue
        # start and end are two independent readouts; the floor for their
        # difference is the same half-normal expression on their two SEs, and
        # the per-round floor already encodes exactly that pair.
        entries.append({
            "run": list(key),
            "judge": rr[0]["judge"],
            "organism": rr[0]["organism"],
            "n_rounds": len(rr),
            "cumulative_abs_gap": cumulative,
            "v_start": v_start,
            "v_end": v_end,
            "abs_endpoint_move": abs(v_end - v_start),
            "endpoint_noise_floor": float(np.mean(floors)),
        })

    out = {"runs": entries}
    for label, lo, hi in (("low selection (cumulative |gap| < 0.10)", 0.0, 0.10),
                          ("mid selection (0.10-0.30)", 0.10, 0.30),
                          ("high selection (>= 0.30)", 0.30, 1e9)):
        sub = [e for e in entries if lo <= e["cumulative_abs_gap"] < hi]
        if len(sub) < 3:
            out[label] = {"n": len(sub), "insufficient": True}
            continue
        obs = np.array([e["abs_endpoint_move"] for e in sub])
        floor = np.array([e["endpoint_noise_floor"] for e in sub])
        rng = np.random.default_rng(SEED)
        draws = []
        for _ in range(BOOTSTRAP_DRAWS):
            idx = rng.integers(0, len(sub), len(sub))
            draws.append(obs[idx].mean() / floor[idx].mean())
        draws = np.array(draws)
        out[label] = {
            "n_runs": len(sub),
            "mean_cumulative_abs_gap": float(np.mean(
                [e["cumulative_abs_gap"] for e in sub])),
            "mean_abs_endpoint_move": float(obs.mean()),
            "mean_noise_floor": float(floor.mean()),
            "ratio": float(obs.mean() / floor.mean()),
            "ratio_ci": [float(np.percentile(draws, 2.5)),
                         float(np.percentile(draws, 97.5))],
        }
    return out


def main():
    unified, runs, rows = load()

    random_rows = [r for r in rows if r["judge"] == "random"]
    near_zero = [r for r in rows if abs(r["gap"]) <= NEAR_ZERO_GAP]
    near_zero_self = [r for r in near_zero if r["composition"] == "self-only"]
    large = [r for r in rows if abs(r["gap"]) >= 0.15]

    result = {
        "description": (
            "Whether self-training without selection is idempotent in this "
            "corpus, as Roe et al. (arXiv 2605.01130) report for supervised "
            "finetuning. Distinguishes random selection (which still realises a "
            "nonzero differential) from genuinely near-zero selection, and "
            "checks idempotence at the round level and the run level."
        ),
        "reference": {
            "paper": "Roe et al., Iterative Finetuning is Mostly Idempotent",
            "arxiv": "https://arxiv.org/abs/2605.01130",
            "their_sft_finding": (
                "traits mostly decay or remain constant so that further "
                "finetuning cycles do nothing"),
            "their_dpo_finding": (
                "trait amplification can reliably occur when a model is "
                "continually trained with a preference for its own outputs, but "
                "vanishes when models are reinitialized"),
            "our_setting": (
                "supervised finetuning on kept candidates, continual (the "
                "adapter is carried forward, never reinitialised), WITH a "
                "selection step -- which is the ingredient their SFT arm lacks"),
        },
        "round_level": {
            "random_selector_arms": ratio_block(random_rows, "judge == random"),
            "near_zero_gap": ratio_block(
                near_zero, f"|gap| <= {NEAR_ZERO_GAP}"),
            "near_zero_gap_self_only": ratio_block(
                near_zero_self, f"|gap| <= {NEAR_ZERO_GAP}, self-only pools"),
            "large_gap_comparator": ratio_block(large, "|gap| >= 0.15"),
        },
        "response_coefficients": {
            "random_selector_arms": response_coefficient(
                random_rows, "judge == random"),
            "all_rows": response_coefficient(rows, "all rows"),
        },
        "run_level": run_level(runs, rows),
        "settings": {
            "near_zero_gap_threshold": NEAR_ZERO_GAP,
            "bootstrap_draws": BOOTSTRAP_DRAWS,
            "noise_floor": (
                "sqrt(se_t^2 + se_next^2) * sqrt(2/pi) per row: the expected "
                "absolute change from re-measuring an unchanged model"),
        },
    }
    OUT.write_text(json.dumps(result, indent=2) + "\n")

    print("ROUND LEVEL  observed mean |drift| / measurement-noise floor")
    for block in result["round_level"].values():
        if block.get("insufficient"):
            print(f"  {block['label']}: insufficient (n={block['n']})")
            continue
        ci = block["ratio_ci"]
        print(f"  {block['label']:38s} n={block['n']:3d} "
              f"mean|gap|={block['mean_abs_gap']:.4f}  "
              f"ratio={block['ratio']:.3f} [{ci[0]:.3f}, {ci[1]:.3f}]")
    print()
    print("RESPONSE COEFFICIENT  drift ~ pool offset + gap")
    for block in result["response_coefficients"].values():
        if block.get("insufficient"):
            continue
        ci = block["gap_coefficient_ci"]
        print(f"  {block['label']:24s} n={block['n']:3d} "
              f"mean|gap|={block['mean_abs_gap']:.4f}  "
              f"gap={block['gap_coefficient']:.3f}"
              + (f" [{ci[0]:.3f}, {ci[1]:.3f}]" if ci else ""))
    print()
    print("RUN LEVEL  |endpoint - start| / noise floor, by cumulative selection")
    for label, block in result["run_level"].items():
        if label == "runs" or block.get("insufficient"):
            continue
        ci = block["ratio_ci"]
        print(f"  {label:36s} runs={block['n_runs']:3d} "
              f"cum|gap|={block['mean_cumulative_abs_gap']:.3f}  "
              f"move={block['mean_abs_endpoint_move']:.3f}  "
              f"ratio={block['ratio']:.3f} [{ci[0]:.3f}, {ci[1]:.3f}]")
    print()
    print(f"wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
