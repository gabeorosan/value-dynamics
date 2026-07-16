#!/usr/bin/env python3
"""Path-property fidelity of the UNIT-recurrence rollouts.

The rollout-property analysis (scripts/analysis_rollout_property_fidelity.py)
scored only the two FITTED cores (frozen mean SD, frozen mean range). The
selection-response audit later adopted a zero-fitted-parameter unit recurrence
(m_next = clip((1-u)m + u*supplier + rho*sigma); next value = kept-mean
identity) whose per-run deterministic trajectories were rolled and stored in
experiments/selection_response_predictor.json but never property-scored.

This analysis scores those stored unit trajectories with EXACTLY the property
recipes of the fitted-core analysis (endpoint class: low rail <= 0.15, high
rail >= 0.85, else interior; sign reversals: direction changes among
round-to-round moves >= 0.025; direction: runs with |net change| >= 0.15) on
the matched run set where the unit rollout starts at round 1 (glued grid
entries and judge-swap runs are excluded: the stored unit swap rollouts are
post-swap conditional forecasts, so their full-path shape is not comparable
from round 1).

Inputs:
  experiments/selection_response_predictor.json  (unit per-run trajectories)
  experiments/spread_rollout_bakeoff.json        (fitted frozen per-run
    trajectories and the observed value_after_true paths)

Output: experiments/unit_rollout_properties.json
Report: docs/report_unit_rollout_properties.md

Run: uv run python scripts/analysis_unit_rollout_properties.py
"""

import json
import math
import os

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UNITREC_PATH = os.path.join(REPO, "experiments", "selection_response_predictor.json")
BAKEOFF_PATH = os.path.join(REPO, "experiments", "spread_rollout_bakeoff.json")
OUT_PATH = os.path.join(REPO, "experiments", "unit_rollout_properties.json")

JOIN_TOL = 2e-3
REVERSAL_THRESHOLD = 0.025
DIRECTION_MIN_MOVE = 0.15


def endpoint_class(value):
    if value <= 0.15:
        return "low_rail"
    if value >= 0.85:
        return "high_rail"
    return "interior"


def sign_reversals(path, threshold=REVERSAL_THRESHOLD):
    deltas = [b - a for a, b in zip(path, path[1:])]
    signs = [1 if d > 0 else -1 for d in deltas if abs(d) >= threshold]
    return sum(1 for a, b in zip(signs, signs[1:]) if a != b)


def total_variation(path):
    return sum(abs(b - a) for a, b in zip(path, path[1:]))


def mean(xs):
    return sum(xs) / len(xs)


def sd(xs):
    m = mean(xs)
    return math.sqrt(sum((x - m) ** 2 for x in xs) / len(xs))


def r2(truths, preds):
    m = mean(truths)
    ss_res = sum((t - p) ** 2 for t, p in zip(truths, preds))
    ss_tot = sum((t - m) ** 2 for t in truths)
    return 1 - ss_res / ss_tot if ss_tot else None


def main():
    unitrec = json.load(open(UNITREC_PATH))
    bakeoff = json.load(open(BAKEOFF_PATH))

    frozen_runs = bakeoff["validations"]["leave_one_condition_out"]["frozen"][
        "mean_within_prompt_population_sd"
    ]["per_run"]
    unit_by_key = {
        r["run_key"]: r
        for r in unitrec["endpoint_with_boundary_refresh"][
            "recommended_unit_agreement_spread"
        ]["per_run"]
    }

    # matched selection-driven runs: sequential round indices, unit trajectory
    # starts at round 1 (full-length), truths agree
    matched = []
    excluded = []
    for run in frozen_runs:
        if run["regime"] not in ("intervention", "self-force"):
            continue
        uu = unit_by_key.get(run["run_key"])
        idx = [rr["round"] for rr in run["rounds"]]
        if uu is None:
            excluded.append((run["run_key"], "no unit record"))
            continue
        if idx != list(range(1, run["n_rounds"] + 1)):
            excluded.append((run["run_key"], "glued run"))
            continue
        traj = uu["trajectory"]
        if (
            len(traj) != run["n_rounds"]
            or abs(uu["start"] - run["v1"]) > JOIN_TOL
            or abs(uu["actual"] - run["rounds"][-1]["value_after_true"]) > JOIN_TOL
        ):
            excluded.append((run["run_key"], "alignment"))
            continue
        v1 = run["v1"]
        truth_path = [v1] + [rr["value_after_true"] for rr in run["rounds"]]
        fitted_path = [v1] + [rr["value_after_pred"] for rr in run["rounds"]]
        unit_path = [v1] + list(traj)
        matched.append(
            {
                "run_key": run["run_key"],
                "regime": run["regime"],
                "paths": {
                    "observed": truth_path,
                    "fitted_frozen_sd": fitted_path,
                    "unit_recurrence": unit_path,
                },
            }
        )

    assert len(matched) >= 30, f"matched set unexpectedly small: {len(matched)}"

    models = ["fitted_frozen_sd", "unit_recurrence"]
    summary = {}

    obs_paths = [m["paths"]["observed"] for m in matched]
    obs_endpoints = [p[-1] for p in obs_paths]
    summary["observed"] = {
        "n_runs": len(matched),
        "mean_total_variation": round(mean([total_variation(p) for p in obs_paths]), 4),
        "mean_sign_reversals": round(mean([sign_reversals(p) for p in obs_paths]), 4),
        "endpoint_mean": round(mean(obs_endpoints), 4),
        "endpoint_sd": round(sd(obs_endpoints), 4),
    }

    for model in models:
        paths = [m["paths"][model] for m in matched]
        endpoints = [p[-1] for p in paths]
        all_truths, all_preds = [], []
        for m in matched:
            all_truths.extend(m["paths"]["observed"][1:])
            all_preds.extend(m["paths"][model][1:])
        moving = [
            m
            for m in matched
            if abs(m["paths"]["observed"][-1] - m["paths"]["observed"][0])
            >= DIRECTION_MIN_MOVE
        ]
        dir_hits = sum(
            1
            for m in moving
            if (m["paths"][model][-1] - m["paths"][model][0])
            * (m["paths"]["observed"][-1] - m["paths"]["observed"][0])
            > 0
        )
        true_rail = [
            m
            for m in matched
            if endpoint_class(m["paths"]["observed"][-1]) != "interior"
        ]
        rail_hits = sum(
            1
            for m in true_rail
            if endpoint_class(m["paths"][model][-1])
            == endpoint_class(m["paths"]["observed"][-1])
        )
        class_hits = sum(
            1
            for m in matched
            if endpoint_class(m["paths"][model][-1])
            == endpoint_class(m["paths"]["observed"][-1])
        )
        summary[model] = {
            "n_runs": len(matched),
            "mean_total_variation": round(mean([total_variation(p) for p in paths]), 4),
            "mean_sign_reversals": round(mean([sign_reversals(p) for p in paths]), 4),
            "endpoint_mean": round(mean(endpoints), 4),
            "endpoint_sd": round(sd(endpoints), 4),
            "endpoint_mae": round(
                mean(
                    [
                        abs(m["paths"][model][-1] - m["paths"]["observed"][-1])
                        for m in matched
                    ]
                ),
                4,
            ),
            "all_round_mae": round(
                mean([abs(t - p) for t, p in zip(all_truths, all_preds)]), 4
            ),
            "all_round_r2": round(r2(all_truths, all_preds), 4),
            "large_move_direction": f"{dir_hits}/{len(moving)}",
            "rail_endpoint_recall": f"{rail_hits}/{len(true_rail)}",
            "endpoint_class_accuracy": f"{class_hits}/{len(matched)}",
        }

    out = {
        "description": (
            "Deterministic path-property fidelity of the zero-fitted-parameter "
            "unit-recurrence rollouts, scored with the same recipes as the "
            "fitted-core property analysis, on the matched selection-driven "
            "runs where the stored unit rollout starts at round 1. Property "
            "recipes: endpoint class low rail <= 0.15 / high rail >= 0.85; "
            "sign reversals among round moves >= 0.025; direction on runs "
            "with |net change| >= 0.15. Paths include the round-1 starting "
            "value. Judge-swap runs are excluded (stored unit swap rollouts "
            "are post-swap conditional forecasts); glued grid entries are "
            "excluded (sequential-rollout ambiguity)."
        ),
        "inputs": {
            "unit_trajectories": "experiments/selection_response_predictor.json",
            "fitted_trajectories_and_truths": "experiments/spread_rollout_bakeoff.json",
        },
        "matched_runs": len(matched),
        "excluded_runs": [{"run_key": k, "reason": r} for k, r in excluded],
        "summary": summary,
        "per_run": matched,
    }
    with open(OUT_PATH, "w") as f:
        json.dump(out, f, indent=1)

    print(f"wrote {OUT_PATH}")
    print(f"\nmatched selection-driven runs: {len(matched)} "
          f"(excluded: {[r for _, r in excluded]})")
    keys = [
        "mean_total_variation",
        "mean_sign_reversals",
        "endpoint_mean",
        "endpoint_sd",
        "endpoint_mae",
        "all_round_mae",
        "all_round_r2",
        "large_move_direction",
        "rail_endpoint_recall",
        "endpoint_class_accuracy",
    ]
    hdr = f"{'property':28s}" + "".join(
        f"{name:>20s}" for name in ("observed", "fitted", "unit")
    )
    print(hdr)
    for k in keys:
        row = f"{k:28s}"
        for model in ("observed", "fitted_frozen_sd", "unit_recurrence"):
            v = summary[model].get(k, "—")
            row += f"{str(v):>20s}"
        print(row)


if __name__ == "__main__":
    main()
