"""Test whether SD- and range-based simulations reproduce rollout properties.

Both models use frozen first-boundary variation and the same full-state refresh
on scheduled judge swaps.  This analysis compares their hybrid predicted
trajectories with the observed runs, beyond endpoint MAE.

Run:    .venv/bin/python scripts/analysis_rollout_property_fidelity.py
Writes: experiments/rollout_property_fidelity.json
"""

import json
import os
from collections import defaultdict

import numpy as np


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT = os.path.join(ROOT, "experiments", "spread_rollout_bakeoff.json")
OUTPUT = os.path.join(ROOT, "experiments", "rollout_property_fidelity.json")
VALIDATION = "leave_one_condition_out"

MODELS = {
    "frozen_mean_sd": (
        "mean_within_prompt_population_sd", "mean_sd_frozen"
    ),
    "frozen_mean_range": (
        "mean_within_prompt_range", "rankable_support_frozen"
    ),
}


def endpoint_class(value):
    if value <= 0.15:
        return "low_rail"
    if value >= 0.85:
        return "high_rail"
    return "interior"


def sign_changes(values, threshold=0.025):
    deltas = np.diff(np.asarray(values, float))
    signs = np.sign(deltas[np.abs(deltas) >= threshold])
    if len(signs) < 2:
        return 0
    return int(np.sum(signs[1:] != signs[:-1]))


def run_properties(values):
    arr = np.asarray(values, float)
    return {
        "endpoint": float(arr[-1]),
        "net_change": float(arr[-1] - arr[0]),
        "minimum": float(np.min(arr)),
        "maximum": float(np.max(arr)),
        "trajectory_range": float(np.max(arr) - np.min(arr)),
        "total_variation": float(np.sum(np.abs(np.diff(arr)))),
        "sign_changes_at_0_025": sign_changes(arr),
        "endpoint_class": endpoint_class(float(arr[-1])),
        "ever_low_rail": bool(np.any(arr <= 0.15)),
        "ever_high_rail": bool(np.any(arr >= 0.85)),
    }


def prediction_metrics(actual, predicted):
    y = np.asarray(actual, float)
    p = np.asarray(predicted, float)
    denom = float(np.sum((y - np.mean(y)) ** 2))
    return {
        "n": int(len(y)),
        "mae": float(np.mean(np.abs(y - p))),
        "rmse": float(np.sqrt(np.mean((y - p) ** 2))),
        "r2": float(1.0 - np.sum((y - p) ** 2) / denom) if denom else None,
        "r": (
            float(np.corrcoef(y, p)[0, 1])
            if len(y) >= 3 and np.std(y) > 0 and np.std(p) > 0 else None
        ),
    }


def hybrid_runs(payload, metric, refresh_name):
    base_runs = payload["validations"][VALIDATION]["frozen"][metric]["per_run"]
    refresh_runs = payload["judge_swap_refresh"][VALIDATION][refresh_name]["per_run"]
    refresh_by_key = {run["run_key"]: run for run in refresh_runs}
    out = []
    for run in base_runs:
        rounds = list(run["rounds"])
        refresh = None
        if run["run_key"] in refresh_by_key:
            refresh = refresh_by_key[run["run_key"]]
            swap_round = refresh["first_new_judge_round"]
            rounds = (
                [rd for rd in rounds if rd["round"] < swap_round]
                + refresh["refreshed_rounds"]
            )
        true_values = [run["v1"]] + [rd["value_after_true"] for rd in rounds]
        predicted_values = [run["v1"]] + [rd["value_after_pred"] for rd in rounds]
        if refresh is not None:
            # The boundary state is observed and becomes the initial condition
            # for the new segment; represent the conditional path with that
            # observed state rather than the old segment's forecast at the
            # same time index.
            predicted_values[refresh["first_new_judge_round"] - 1] = refresh[
                "value_at_swap"
            ]
        out.append({
            "run_key": run["run_key"],
            "cond": run["cond"],
            "regime": run["regime"],
            "axis": run["axis"],
            "true_values": true_values,
            "predicted_values": predicted_values,
            "true": run_properties(true_values),
            "predicted": run_properties(predicted_values),
        })
    return out


def summarize(runs):
    numeric_properties = (
        "endpoint", "net_change", "minimum", "maximum", "trajectory_range",
        "total_variation", "sign_changes_at_0_025",
    )
    property_metrics = {
        prop: prediction_metrics(
            [run["true"][prop] for run in runs],
            [run["predicted"][prop] for run in runs],
        )
        for prop in numeric_properties
    }
    all_true_rounds = [
        value for run in runs for value in run["true_values"][1:]
    ]
    all_pred_rounds = [
        value for run in runs for value in run["predicted_values"][1:]
    ]
    moving = [run for run in runs if abs(run["true"]["net_change"]) >= 0.15]
    direction_hits = [
        run for run in moving
        if (
            run["true"]["net_change"] * run["predicted"]["net_change"] > 0
            and abs(run["predicted"]["net_change"]) >= 0.05
        )
    ]
    endpoint_class_hits = [
        run for run in runs
        if run["true"]["endpoint_class"] == run["predicted"]["endpoint_class"]
    ]
    true_rail = [
        run for run in runs if run["true"]["endpoint_class"] != "interior"
    ]
    rail_hits = [
        run for run in true_rail
        if run["true"]["endpoint_class"] == run["predicted"]["endpoint_class"]
    ]

    class_confusion = defaultdict(lambda: defaultdict(int))
    for run in runs:
        class_confusion[run["true"]["endpoint_class"]][
            run["predicted"]["endpoint_class"]
        ] += 1

    return {
        "n_runs": len(runs),
        "n_predicted_rounds": len(all_true_rounds),
        "all_round_value": prediction_metrics(all_true_rounds, all_pred_rounds),
        "run_properties": property_metrics,
        "large_movement_direction": {
            "n": len(moving),
            "hits": len(direction_hits),
            "hit_rate": len(direction_hits) / len(moving) if moving else None,
        },
        "endpoint_three_class_accuracy": {
            "hits": len(endpoint_class_hits),
            "n": len(runs),
            "accuracy": len(endpoint_class_hits) / len(runs),
            "confusion": {
                actual: dict(predicted)
                for actual, predicted in class_confusion.items()
            },
        },
        "observed_rail_endpoint_recall": {
            "hits": len(rail_hits),
            "n": len(true_rail),
            "recall": len(rail_hits) / len(true_rail) if true_rail else None,
        },
        "aggregate_shape": {
            "observed_endpoint_mean": float(np.mean([
                run["true"]["endpoint"] for run in runs
            ])),
            "predicted_endpoint_mean": float(np.mean([
                run["predicted"]["endpoint"] for run in runs
            ])),
            "observed_endpoint_sd": float(np.std([
                run["true"]["endpoint"] for run in runs
            ])),
            "predicted_endpoint_sd": float(np.std([
                run["predicted"]["endpoint"] for run in runs
            ])),
            "observed_mean_total_variation": float(np.mean([
                run["true"]["total_variation"] for run in runs
            ])),
            "predicted_mean_total_variation": float(np.mean([
                run["predicted"]["total_variation"] for run in runs
            ])),
            "observed_mean_sign_changes": float(np.mean([
                run["true"]["sign_changes_at_0_025"] for run in runs
            ])),
            "predicted_mean_sign_changes": float(np.mean([
                run["predicted"]["sign_changes_at_0_025"] for run in runs
            ])),
        },
    }


def grouped(runs):
    groups = {
        "all": runs,
        "selection_driven_plus_swap": [
            run for run in runs
            if run["regime"] in ("intervention", "self-force", "judge-swap")
        ],
        "selection_driven": [
            run for run in runs
            if run["regime"] in ("intervention", "self-force")
        ],
        "judge_swap": [run for run in runs if run["regime"] == "judge-swap"],
        "self_weak": [run for run in runs if run["regime"] == "self-weak"],
        "risk": [run for run in runs if run["axis"] == "risk"],
        "selfreport": [run for run in runs if run["axis"] == "selfreport"],
    }
    return {name: summarize(rows) for name, rows in groups.items() if rows}


def compare_models(models):
    left = {run["run_key"]: run for run in models["frozen_mean_sd"]}
    right = {run["run_key"]: run for run in models["frozen_mean_range"]}
    keys = sorted(set(left) & set(right))
    endpoint_differences = []
    round_differences = []
    endpoint_class_matches = 0
    direction_matches = 0
    for key in keys:
        sd = left[key]
        rg = right[key]
        endpoint_differences.append(abs(
            sd["predicted"]["endpoint"] - rg["predicted"]["endpoint"]
        ))
        round_differences.extend(abs(a - b) for a, b in zip(
            sd["predicted_values"][1:], rg["predicted_values"][1:]
        ))
        endpoint_class_matches += (
            sd["predicted"]["endpoint_class"]
            == rg["predicted"]["endpoint_class"]
        )
        direction_matches += (
            np.sign(sd["predicted"]["net_change"])
            == np.sign(rg["predicted"]["net_change"])
        )
    return {
        "n_common_runs": len(keys),
        "mean_absolute_endpoint_prediction_difference": float(np.mean(endpoint_differences)),
        "max_absolute_endpoint_prediction_difference": float(np.max(endpoint_differences)),
        "mean_absolute_round_prediction_difference": float(np.mean(round_differences)),
        "same_predicted_endpoint_class": {
            "n": int(endpoint_class_matches),
            "rate": float(endpoint_class_matches / len(keys)),
        },
        "same_predicted_net_direction": {
            "n": int(direction_matches),
            "rate": float(direction_matches / len(keys)),
        },
    }


def rounded(value):
    if isinstance(value, dict):
        return {key: rounded(item) for key, item in value.items()}
    if isinstance(value, list):
        return [rounded(item) for item in value]
    if isinstance(value, (float, np.floating)):
        return round(float(value), 6)
    return value


def main():
    with open(INPUT) as handle:
        payload = json.load(handle)
    models = {
        name: hybrid_runs(payload, metric, refresh_name)
        for name, (metric, refresh_name) in MODELS.items()
    }
    output = rounded({
        "description": __doc__.strip().split("\n")[0],
        "input": os.path.relpath(INPUT, ROOT),
        "validation": VALIDATION,
        "boundary_rule": (
            "forecast from round 1; on scheduled judge swaps, replace the "
            "post-swap path with a forecast initialized from the first pool "
            "scored by the new judge"
        ),
        "models": {name: grouped(runs) for name, runs in models.items()},
        "model_prediction_similarity": compare_models(models),
        "per_run": models,
    })
    with open(OUTPUT, "w") as handle:
        json.dump(output, handle, indent=1)
    print(f"{len(next(iter(models.values())))} runs -> {OUTPUT}")


if __name__ == "__main__":
    main()
