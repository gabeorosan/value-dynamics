"""Compare simple endpoint and one-round behavioral-value predictors.

The endpoint comparison augments the closed-loop spread bakeoff with the
online judge-swap refresh: ordinary runs are forecast from round 1, while a
scheduled judge swap reinitializes the model from the first pool scored by the
new judge.

The one-round comparison predicts the observed behavioral-value change.  It
separates predictors available after selection (the kept-target pull) from a
pre-selection factorized forecast that estimates the selector gap from
agreement times offered spread.

Run:    .venv/bin/python scripts/analysis_value_predictor_bakeoff.py
Writes: experiments/value_predictor_bakeoff.json
"""

import json
import os
from collections import defaultdict

import numpy as np


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UNIFIED = os.path.join(ROOT, "experiments", "spread_util_unified.json")
ROLLOUT = os.path.join(ROOT, "experiments", "spread_rollout_bakeoff.json")
OUTPUT = os.path.join(ROOT, "experiments", "value_predictor_bakeoff.json")


def run_key(row):
    return (row["cond"], row["seed"], row["source"])


def ols1(rows, feature, target="drift"):
    x = np.asarray([feature(row) for row in rows], float)
    y = np.asarray([row[target] for row in rows], float)
    slope, intercept = np.polyfit(x, y, 1)
    return float(intercept), float(slope)


def ols_multi(rows, features, target="drift"):
    x = np.asarray([[1.0] + [fn(row) for fn in features] for row in rows], float)
    y = np.asarray([row[target] for row in rows], float)
    return np.linalg.lstsq(x, y, rcond=None)[0]


def metrics(actual, predicted):
    y = np.asarray(actual, float)
    p = np.asarray(predicted, float)
    denom = float(np.sum((y - np.mean(y)) ** 2))
    moved = np.abs(y) >= 0.05
    direction = np.sign(y[moved]) == np.sign(p[moved])
    return {
        "n": int(len(y)),
        "mae": float(np.mean(np.abs(y - p))),
        "rmse": float(np.sqrt(np.mean((y - p) ** 2))),
        "r2": float(1.0 - np.sum((y - p) ** 2) / denom),
        "direction_on_abs_change_at_least_0_05": {
            "n": int(np.sum(moved)),
            "hits": int(np.sum(direction)),
            "hit_rate": float(np.mean(direction)) if np.any(moved) else None,
        },
    }


def cross_validate(records, validation):
    fold_of = (
        (lambda row: run_key(row))
        if validation == "leave_one_run_out"
        else (lambda row: row["cond"])
    )
    folds = sorted({fold_of(row) for row in records}, key=str)
    predictions = defaultdict(lambda: ([], []))

    for fold in folds:
        train = [row for row in records if fold_of(row) != fold]
        held = [row for row in records if fold_of(row) == fold]

        pull_fit = ols1(train, lambda row: row["pull"])
        displacement_fit = ols1(train, lambda row: row["self_relative_gap"])
        gap_fit = ols1(train, lambda row: row["gap"])
        pool_offset_fit = ols1(train, lambda row: row["pool_mean"] - row["value"])

        rho_train = [row for row in train if row.get("rho") is not None]
        rho_held = [row for row in held if row.get("rho") is not None]
        selector_fit = ols1(
            rho_train,
            lambda row: row["rho"] * row["spread"],
            target="gap",
        )

        def predicted_pull(row):
            predicted_gap = (
                selector_fit[0]
                + selector_fit[1] * row["rho"] * row["spread"]
            )
            return row["pool_mean"] - row["value"] + predicted_gap

        factorized_update_fit = ols1(rho_train, predicted_pull)
        preselection_beta = ols_multi(
            rho_train,
            [
                lambda row: row["pool_mean"] - row["value"],
                lambda row: row["rho"] * row["spread"],
            ],
        )

        for row in held:
            actual = row["drift"]
            fitted_pull_delta = pull_fit[0] + pull_fit[1] * row["pull"]
            fitted_pull_delta = float(np.clip(
                row["value"] + fitted_pull_delta, 0.0, 1.0
            ) - row["value"])
            ordinary = {
                "no_change": 0.0,
                "kept_target_identity": row["pull"],
                "calibrated_kept_pull": fitted_pull_delta,
                "training_displacement": (
                    displacement_fit[0]
                    + displacement_fit[1] * row["self_relative_gap"]
                ),
                "selector_gap": gap_fit[0] + gap_fit[1] * row["gap"],
                "pool_offset_without_selection": (
                    pool_offset_fit[0]
                    + pool_offset_fit[1] * (row["pool_mean"] - row["value"])
                ),
            }
            for name, prediction in ordinary.items():
                predictions[name][0].append(actual)
                predictions[name][1].append(prediction)

        for row in rho_held:
            actual = row["drift"]
            factorized_pull = predicted_pull(row)
            factorized_delta = (
                factorized_update_fit[0]
                + factorized_update_fit[1] * factorized_pull
            )
            factorized_delta = float(np.clip(
                row["value"] + factorized_delta, 0.0, 1.0
            ) - row["value"])
            subset = {
                "rho_subset_no_change": 0.0,
                "rho_subset_kept_target_identity": row["pull"],
                "factorized_preselection_pull": factorized_delta,
                "free_two_feature_preselection": float(
                    preselection_beta[0]
                    + preselection_beta[1] * (row["pool_mean"] - row["value"])
                    + preselection_beta[2] * row["rho"] * row["spread"]
                ),
            }
            for name, prediction in subset.items():
                predictions[name][0].append(actual)
                predictions[name][1].append(prediction)

    return {
        name: metrics(actual, predicted)
        for name, (actual, predicted) in predictions.items()
    }


def endpoint_hybrid(rollout):
    validation = "leave_one_condition_out"
    candidates = {
        "mean_sd_geometry": (
            "geometry", "mean_within_prompt_population_sd", "mean_sd_geometry"
        ),
        "mean_sd_frozen": (
            "frozen", "mean_within_prompt_population_sd", "mean_sd_frozen"
        ),
        "rankable_support_frozen": (
            "frozen", "mean_within_prompt_range", "rankable_support_frozen"
        ),
    }
    out = {}
    for name, (mode, metric, refresh_name) in candidates.items():
        aggregates = rollout["validations"][validation][mode][metric]["aggregates"]
        all_runs = aggregates["all"]
        swap = aggregates["judge_swap"]
        refreshed = rollout["judge_swap_refresh"][validation][refresh_name]["aggregate"]
        n_all = all_runs["n_runs"]
        n_swap = swap["n_runs"]
        old_mae = all_runs["behavioral_value_endpoint"]["mae"]
        old_swap_mae = swap["behavioral_value_endpoint"]["mae"]
        new_swap_mae = refreshed["endpoint"]["refreshed_at_swap"]["mae"]
        old_persistence_mae = all_runs[
            "behavioral_value_endpoint_persistence"
        ]["mae"]
        old_swap_persistence_mae = swap[
            "behavioral_value_endpoint_persistence"
        ]["mae"]
        new_swap_persistence_mae = refreshed["endpoint"][
            "persistence_from_swap"
        ]["mae"]
        hybrid_mae = (
            old_mae * n_all - old_swap_mae * n_swap + new_swap_mae * n_swap
        ) / n_all
        hybrid_persistence_mae = (
            old_persistence_mae * n_all
            - old_swap_persistence_mae * n_swap
            + new_swap_persistence_mae * n_swap
        ) / n_all

        selection = aggregates["selection_driven"]
        n_selection = selection["n_runs"]
        selection_plus_swap_mae = (
            selection["behavioral_value_endpoint"]["mae"] * n_selection
            + new_swap_mae * n_swap
        ) / (n_selection + n_swap)
        selection_plus_swap_persistence_mae = (
            selection["behavioral_value_endpoint_persistence"]["mae"]
            * n_selection
            + new_swap_persistence_mae * n_swap
        ) / (n_selection + n_swap)
        out[name] = {
            "n_all_modelable_runs": n_all,
            "all_run_endpoint_mae_with_boundary_refresh": float(hybrid_mae),
            "all_run_boundary_persistence_mae": float(hybrid_persistence_mae),
            "all_run_endpoint_mae_without_refresh": old_mae,
            "n_selection_driven_plus_swap_runs": n_selection + n_swap,
            "selection_driven_plus_swap_endpoint_mae": float(selection_plus_swap_mae),
            "selection_driven_plus_swap_boundary_persistence_mae": float(
                selection_plus_swap_persistence_mae
            ),
            "swap_endpoint_mae_refreshed": new_swap_mae,
            "swap_direction": refreshed[
                "direction_from_swap_on_runs_moving_at_least_0_15"
            ],
        }
    return out


def rounded(value):
    if isinstance(value, dict):
        return {key: rounded(item) for key, item in value.items()}
    if isinstance(value, list):
        return [rounded(item) for item in value]
    if isinstance(value, (float, np.floating)):
        return round(float(value), 6)
    return value


def main():
    with open(UNIFIED) as handle:
        unified = json.load(handle)
    with open(ROLLOUT) as handle:
        rollout = json.load(handle)
    records = unified["records"]
    rho_records = [row for row in records if row.get("rho") is not None]

    selector_fit = ols1(
        rho_records,
        lambda row: row["rho"] * row["spread"],
        target="gap",
    )

    def full_predicted_pull(row):
        return (
            row["pool_mean"] - row["value"]
            + selector_fit[0]
            + selector_fit[1] * row["rho"] * row["spread"]
        )

    output = rounded({
        "description": __doc__.strip().split("\n")[0],
        "inputs": [
            os.path.relpath(UNIFIED, ROOT),
            os.path.relpath(ROLLOUT, ROOT),
        ],
        "endpoint_with_boundary_refresh": endpoint_hybrid(rollout),
        "one_round": {
            "leave_one_run_out": cross_validate(records, "leave_one_run_out"),
            "leave_one_condition_out": cross_validate(
                records, "leave_one_condition_out"
            ),
            "full_data_equations_for_description_only": {
                "calibrated_kept_pull": {
                    "formula": "delta_value = intercept + slope * (kept_mean - value)",
                    "intercept_slope": ols1(records, lambda row: row["pull"]),
                },
                "selector_gap": {
                    "formula": "gap = intercept + slope * agreement * spread",
                    "intercept_slope": selector_fit,
                },
                "factorized_preselection_pull": {
                    "formula": (
                        "delta_value = intercept + slope * "
                        "[(pool_mean - value) + predicted_gap]"
                    ),
                    "intercept_slope": ols1(rho_records, full_predicted_pull),
                },
            },
        },
        "recommended_simple_models": {
            "endpoint": (
                "measure value, own candidate mean, frozen mean within-prompt "
                "population SD, "
                "agreement, and supplier state; roll the selection/update loop; "
                "remeasure the full state and restart when the judge or judging "
                "protocol changes; mean range is numerically tied but retained "
                "only as a robustness check"
            ),
            "one_round_after_selection": "next_value = kept_candidate_value_mean",
            "one_round_calibrated": (
                "delta_value = -0.007 + 0.833 * (kept_mean - current_value)"
            ),
            "one_round_before_selection": (
                "predict gap from 0.96 * agreement * spread, add pool_mean - "
                "current_value, then apply the approximately 0.86 update gain"
            ),
        },
    })
    with open(OUTPUT, "w") as handle:
        json.dump(output, handle, indent=1)
    print(f"{len(records)} rounds -> {OUTPUT}")


if __name__ == "__main__":
    main()
