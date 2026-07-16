"""Compare candidate-spread definitions for selection and loop dynamics.

The two jobs are evaluated separately:

1. Selector scale: which within-prompt measure best scales the realized
   selector gap when multiplied by within-prompt judge/value agreement rho?
2. Generator state: which own-source measure gives the most transportable
   round-to-round conversion model and what part of its change is determined
   by the candidate mean versus between-prompt heterogeneity?

Run:    uv run python scripts/analysis_spread_definition_audit.py
Writes: experiments/spread_definition_audit.json
"""

import json
import math
import os
from collections import Counter, defaultdict

import numpy as np


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT = os.path.join(ROOT, "experiments", "spread_util_unified.json")
OUTPUT = os.path.join(ROOT, "experiments", "spread_definition_audit.json")

SELECTOR_METRICS = {
    "mean_within_prompt_population_sd": "mean_item_sd",
    "rms_within_prompt_population_sd": "rms_item_sd",
    "mean_within_prompt_variance": "mean_item_variance",
    "mean_pairwise_absolute_score_difference": "mean_pairwise_absolute_difference",
    "mean_within_prompt_mean_absolute_deviation": "mean_item_mean_absolute_deviation",
    "mean_within_prompt_range": "mean_item_range",
    "median_within_prompt_population_sd": "median_item_sd",
    "total_sd_including_between_prompt_variation": "hierarchical_total_sd",
    "fraction_prompts_with_any_score_difference": "fraction_items_with_any_difference",
    "mean_within_prompt_binary_entropy_bits": "mean_item_binary_entropy_bits",
}

OWN_METRICS = {
    "mean_within_prompt_population_sd": "own_spread",
    "rms_within_prompt_population_sd": "own_rms_item_sd",
    "mean_within_prompt_variance": "own_mean_item_variance",
    "mean_pairwise_absolute_score_difference": "own_pairwise_absolute_difference",
    "mean_within_prompt_mean_absolute_deviation": "own_mean_item_mean_absolute_deviation",
    "mean_within_prompt_range": "own_mean_item_range",
    "median_within_prompt_population_sd": "own_median_item_sd",
    "total_sd_including_between_prompt_variation": "own_hierarchical_total_sd",
    "fraction_prompts_with_any_score_difference": "own_fraction_items_with_any_difference",
    "mean_within_prompt_binary_entropy_bits": "own_mean_item_binary_entropy_bits",
}

BOUNDS = {
    "mean_within_prompt_population_sd": 0.5,
    "rms_within_prompt_population_sd": 0.5,
    "mean_within_prompt_variance": 0.25,
    "mean_pairwise_absolute_score_difference": 1.0,
    "mean_within_prompt_mean_absolute_deviation": 0.5,
    "mean_within_prompt_range": 1.0,
    "median_within_prompt_population_sd": 0.5,
    "total_sd_including_between_prompt_variation": 0.5,
    "fraction_prompts_with_any_score_difference": 1.0,
    "mean_within_prompt_binary_entropy_bits": 1.0,
}


def run_key(r):
    return f'{r["cond"]}|{r["seed"]}|{r["source"]}'


def ols(xs, ys):
    x = np.asarray(xs, float)
    y = np.asarray(ys, float)
    if len(x) < 3 or np.std(x) < 1e-12:
        return None
    slope, intercept = np.polyfit(x, y, 1)
    pred = intercept + slope * x
    return {
        "n": int(len(x)),
        "slope": float(slope),
        "intercept": float(intercept),
        **prediction_metrics(y, pred),
    }


def prediction_metrics(actual, predicted):
    y = np.asarray(actual, float)
    p = np.asarray(predicted, float)
    denom = float(np.sum((y - np.mean(y)) ** 2))
    return {
        "n": int(len(y)),
        "r2": float(1.0 - np.sum((y - p) ** 2) / denom) if denom > 0 else None,
        "mae": float(np.mean(np.abs(y - p))),
        "rmse": float(np.sqrt(np.mean((y - p) ** 2))),
        "r": (
            float(np.corrcoef(y, p)[0, 1])
            if len(y) >= 3 and np.std(y) > 0 and np.std(p) > 0 else None
        ),
    }


def loro_linear(rows, x_fn, y_fn):
    actual, predicted = [], []
    groups = sorted({run_key(r) for r in rows})
    for held in groups:
        train = [r for r in rows if run_key(r) != held]
        test = [r for r in rows if run_key(r) == held]
        fit = ols([x_fn(r) for r in train], [y_fn(r) for r in train])
        if not fit:
            continue
        for r in test:
            actual.append(y_fn(r))
            predicted.append(fit["intercept"] + fit["slope"] * x_fn(r))
    return prediction_metrics(actual, predicted)


def record_slices(records):
    return {
        "all": records,
        "binary_risk_axis": [r for r in records if r["axis"] == "risk"],
        "continuous_self_report_axis": [r for r in records if r["axis"] == "selfreport"],
        "self_only": [r for r in records if r["composition"] == "self-only"],
        "mixed": [r for r in records if r["composition"] != "self-only"],
    }


def selector_scale_comparison(records):
    out = {}
    for slice_name, rows in record_slices(records).items():
        rows = [r for r in rows if r.get("rho") is not None]
        if len(rows) < 5:
            continue
        table = {}
        for label, key in SELECTOR_METRICS.items():
            usable = [r for r in rows if r.get(key) is not None]
            if len(usable) < 5:
                continue
            x_fn = lambda r, k=key: r["rho"] * r[k]
            fit = ols([x_fn(r) for r in usable], [r["gap"] for r in usable])
            table[label] = {
                "field": key,
                "in_sample": fit,
                "leave_one_run_out": loro_linear(usable, x_fn, lambda r: r["gap"]),
            }
        out[slice_name] = table
    return out


def make_transitions(records):
    by_run = defaultdict(dict)
    for r in records:
        by_run[run_key(r)][r["round"]] = r
    transitions = []
    for key, rounds in by_run.items():
        for k, r in rounds.items():
            if k + 1 not in rounds:
                continue
            nxt = rounds[k + 1]
            row = dict(r)
            row["run_key"] = key
            row["condition"] = r["cond"]
            row["next"] = nxt
            row["delta_q"] = nxt["own_mean"] - r["own_mean"]
            row["delta_headroom"] = (
                nxt["own_mean"] * (1.0 - nxt["own_mean"])
                - r["own_mean"] * (1.0 - r["own_mean"])
            )
            transitions.append(row)
    return transitions


def transition_slices(rows):
    return {
        "all": rows,
        "binary_risk_axis": [r for r in rows if r["axis"] == "risk"],
        "continuous_self_report_axis": [r for r in rows if r["axis"] == "selfreport"],
        "self_only": [r for r in rows if r["composition"] == "self-only"],
        "mixed": [r for r in rows if r["composition"] != "self-only"],
    }


def fit_conversion(train, metric_key):
    q_fit = ols([r["self_relative_gap"] for r in train], [r["delta_q"] for r in train])
    geometry_fit = ols(
        [r["delta_headroom"] for r in train],
        [r["next"][metric_key] - r[metric_key] for r in train],
    )
    persistence_fit = ols(
        [r[metric_key] for r in train], [r["next"][metric_key] for r in train]
    )
    return q_fit, geometry_fit, persistence_fit


def dynamic_loro(rows, label, metric_key):
    actual, chain_pred, persistence_pred = [], [], []
    for held in sorted({r["run_key"] for r in rows}):
        train = [r for r in rows if r["run_key"] != held]
        test = [r for r in rows if r["run_key"] == held]
        q_fit, geometry_fit, persistence_fit = fit_conversion(train, metric_key)
        if not q_fit or not geometry_fit or not persistence_fit:
            continue
        for r in test:
            dq_hat = q_fit["intercept"] + q_fit["slope"] * r["self_relative_gap"]
            q_next_hat = float(np.clip(r["own_mean"] + dq_hat, 0.0, 1.0))
            delta_h_hat = (
                q_next_hat * (1.0 - q_next_hat)
                - r["own_mean"] * (1.0 - r["own_mean"])
            )
            next_hat = r[metric_key] + geometry_fit["intercept"] + geometry_fit["slope"] * delta_h_hat
            ar_hat = persistence_fit["intercept"] + persistence_fit["slope"] * r[metric_key]
            upper = BOUNDS[label]
            chain_pred.append(float(np.clip(next_hat, 0.0, upper)))
            persistence_pred.append(float(np.clip(ar_hat, 0.0, upper)))
            actual.append(r["next"][metric_key])
    return {
        "conversion_chain": prediction_metrics(actual, chain_pred),
        "persistence": prediction_metrics(actual, persistence_pred),
    }


def generator_state_comparison(transitions):
    out = {}
    for slice_name, rows in transition_slices(transitions).items():
        if len(rows) < 10:
            continue
        table = {}
        for label, key in OWN_METRICS.items():
            usable = [r for r in rows if r.get(key) is not None and r["next"].get(key) is not None]
            if len(usable) < 10:
                continue
            delta_metric = [r["next"][key] - r[key] for r in usable]
            table[label] = {
                "field": key,
                "delta_metric_vs_delta_mean_headroom": ols(
                    [r["delta_headroom"] for r in usable], delta_metric
                ),
                "leave_one_run_out_next_metric": dynamic_loro(usable, label, key),
            }
        out[slice_name] = table
    return out


def binary_variance_geometry(records, transitions):
    binary_records = [r for r in records if r["axis"] == "risk"]
    identity_errors = [
        abs(
            r["own_mean_item_variance"]
            - (r["own_mean"] * (1.0 - r["own_mean"]) - r["own_between_item_mean_variance"])
        )
        for r in binary_records
    ]
    binary_transitions = [r for r in transitions if r["axis"] == "risk"]
    delta_within_var = [
        r["next"]["own_mean_item_variance"] - r["own_mean_item_variance"]
        for r in binary_transitions
    ]
    delta_between_var = [
        r["next"]["own_between_item_mean_variance"] - r["own_between_item_mean_variance"]
        for r in binary_transitions
    ]
    return {
        "identity": (
            "For binary candidate scores, own within-prompt variance = "
            "q(1-q) - variance_across_prompt_means."
        ),
        "n_rounds": len(binary_records),
        "max_absolute_identity_error_after_json_rounding": max(identity_errors),
        "delta_within_prompt_variance_vs_delta_q_headroom": ols(
            [r["delta_headroom"] for r in binary_transitions], delta_within_var
        ),
        "delta_within_prompt_variance_vs_negative_delta_between_prompt_variance": ols(
            [-x for x in delta_between_var], delta_within_var
        ),
        "delta_identity_max_error": max(
            abs(dv - (dh - db))
            for dv, dh, db in zip(
                delta_within_var,
                [r["delta_headroom"] for r in binary_transitions],
                delta_between_var,
            )
        ),
    }


def binary_identity_loro_slice(rows):
    """Predict binary within-prompt variance from its exact decomposition.

    q(1-q) is total score variance when candidate scores are binary. The part
    available to within-prompt selection subtracts variance across prompt
    means. For SD, also carry the Jensen gap mean(SD_j)-sqrt(mean Var_j).
    """
    actual_var, predicted_var = [], []
    actual_sd, predicted_sd = [], []
    actual_q_oracle_var, actual_between_oracle_var = [], []
    for held in sorted({r["run_key"] for r in rows}):
        train = [r for r in rows if r["run_key"] != held]
        test = [r for r in rows if r["run_key"] == held]
        q_fit = ols([r["self_relative_gap"] for r in train], [r["delta_q"] for r in train])
        between_fit = ols(
            [r["own_between_item_mean_variance"] for r in train],
            [r["next"]["own_between_item_mean_variance"] for r in train],
        )
        train_jensen = [
            r["own_spread"] - math.sqrt(max(0.0, r["own_mean_item_variance"]))
            for r in train
        ]
        next_jensen = [
            r["next"]["own_spread"]
            - math.sqrt(max(0.0, r["next"]["own_mean_item_variance"]))
            for r in train
        ]
        jensen_fit = ols(train_jensen, next_jensen)
        if not q_fit or not between_fit or not jensen_fit:
            continue
        for r in test:
            dq_hat = q_fit["intercept"] + q_fit["slope"] * r["self_relative_gap"]
            q_hat = float(np.clip(r["own_mean"] + dq_hat, 0.0, 1.0))
            between_hat = float(np.clip(
                between_fit["intercept"]
                + between_fit["slope"] * r["own_between_item_mean_variance"],
                0.0, 0.25,
            ))
            var_hat = float(np.clip(q_hat * (1.0 - q_hat) - between_hat, 0.0, 0.25))
            jensen_now = r["own_spread"] - math.sqrt(max(0.0, r["own_mean_item_variance"]))
            jensen_hat = jensen_fit["intercept"] + jensen_fit["slope"] * jensen_now
            sd_hat = float(np.clip(math.sqrt(var_hat) + jensen_hat, 0.0, 0.5))
            actual_var.append(r["next"]["own_mean_item_variance"])
            predicted_var.append(var_hat)
            actual_sd.append(r["next"]["own_spread"])
            predicted_sd.append(sd_hat)
            q_actual = r["next"]["own_mean"]
            b_actual = r["next"]["own_between_item_mean_variance"]
            actual_q_oracle_var.append(float(np.clip(q_actual * (1.0 - q_actual) - between_hat, 0, .25)))
            actual_between_oracle_var.append(float(np.clip(q_hat * (1.0 - q_hat) - b_actual, 0, .25)))
    return {
        "model": (
            "Predict q_next from training displacement; persist between-prompt "
            "mean variance; set within-prompt variance to q_next(1-q_next) minus "
            "that component. For mean SD, persist its Jensen gap from RMS SD."
        ),
        "next_mean_within_prompt_variance": prediction_metrics(actual_var, predicted_var),
        "next_mean_within_prompt_sd": prediction_metrics(actual_sd, predicted_sd),
        "variance_with_actual_q_next": prediction_metrics(actual_var, actual_q_oracle_var),
        "variance_with_actual_between_prompt_variance_next": prediction_metrics(
            actual_var, actual_between_oracle_var
        ),
    }


def binary_identity_loro(transitions):
    binary = [r for r in transitions if r["axis"] == "risk"]
    return {
        "all_binary_risk": binary_identity_loro_slice(binary),
        "binary_risk_self_only": binary_identity_loro_slice(
            [r for r in binary if r["composition"] == "self-only"]
        ),
        "binary_risk_mixed": binary_identity_loro_slice(
            [r for r in binary if r["composition"] != "self-only"]
        ),
    }


def dataset_audit(records):
    short_rounds = [
        {
            "condition": r["cond"], "seed": r["seed"], "round": r["round"],
            "candidate_count_min": r["candidate_count_min"],
            "candidate_count_max": r["candidate_count_max"],
        }
        for r in records if r["candidate_count_min"] != r["candidate_count_max"]
        or r["candidate_count_min"] != 6
    ]
    return {
        "n_rounds": len(records),
        "n_runs": len({run_key(r) for r in records}),
        "candidate_count_range_by_round": dict(sorted(Counter(
            f'{r["candidate_count_min"]}-{r["candidate_count_max"]}' for r in records
        ).items())),
        "rounds_not_uniformly_six_candidates": short_rounds,
        "score_range": [min(r["score_min"] for r in records), max(r["score_max"] for r in records)],
        "binary_rounds": sum(r["binary_score_fraction"] == 1.0 for r in records),
        "nonbinary_rounds": sum(r["binary_score_fraction"] < 1.0 for r in records),
        "nonbinary_rounds_by_axis": dict(Counter(
            r["axis"] for r in records if r["binary_score_fraction"] < 1.0
        )),
    }


def rounded(value):
    if isinstance(value, dict):
        return {k: rounded(v) for k, v in value.items()}
    if isinstance(value, list):
        return [rounded(v) for v in value]
    if isinstance(value, float):
        return round(value, 6)
    return value


def main():
    records = json.load(open(INPUT))["records"]
    transitions = make_transitions(records)
    out = {
        "recommended_primary_definition": (
            "Mean within-prompt population SD: S = J^-1 sum_j "
            "sqrt(n_j^-1 sum_k (x_jk - xbar_j)^2)."
        ),
        "metric_roles": {
            "selectable_spread": (
                "Mean within-prompt population SD over the candidate set the "
                "judge actually sees. Use whole-pool candidates for selector "
                "accounting and host-only candidates for generator dynamics."
            ),
            "additive_variance_companion": (
                "Mean within-prompt population variance. Use for exact "
                "within/between-prompt and within/between-source decomposition; "
                "do not silently relabel it as spread."
            ),
            "total_distributional_breadth": (
                "Population SD after including between-prompt mean differences. "
                "This is often easier to predict from the generated mean, but it "
                "is not variation a within-prompt selector can rank."
            ),
        },
        "dataset_audit": dataset_audit(records),
        "selector_scale_comparison": selector_scale_comparison(records),
        "generator_state_comparison": generator_state_comparison(transitions),
        "binary_variance_geometry": binary_variance_geometry(records, transitions),
        "binary_exact_decomposition_model": binary_identity_loro(transitions),
    }
    with open(OUTPUT, "w") as f:
        json.dump(rounded(out), f, indent=1)
    print(f'{len(records)} rounds / {len(transitions)} transitions -> {OUTPUT}')
    for section, slice_name in (("selector_scale_comparison", "all"),
                                ("generator_state_comparison", "all")):
        print(f"\n{section} / {slice_name}")
        for name, result in out[section][slice_name].items():
            if section.startswith("selector"):
                m = result["leave_one_run_out"]
            else:
                m = result["leave_one_run_out_next_metric"]["conversion_chain"]
            print(name, "r2", round(m["r2"], 3), "mae", round(m["mae"], 4))


if __name__ == "__main__":
    main()
