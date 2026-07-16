"""Closed-loop rollout comparison for competing candidate-spread definitions.

The earlier spread-definition audit compared one-step selector-gap and
next-spread fits.  This script asks the stronger question: if each candidate
definition is used inside the complete dynamical loop, which one best rolls an
unseen run forward from its first-round measurements?

For every held-out run and every spread definition, coefficients are fit on
all other runs from the same score axis.  The simulation observes only the
held-out run's first-round state:

    own candidate mean q_1
    own candidate spread z_1 and whole offered-pool spread
    behavioral value v_1
    judge/value agreement rho_1
    and, for mixed pools, supplier mean/metric and pool share.

It then closes the loop:

    offered spread + frozen rho_1 -> selector gap
    selector gap + supplier shift -> kept-vs-own displacement
    displacement -> next own candidate mean
    movement in candidate mean -> next own spread (binary risk axis)
    kept-vs-value pull -> next behavioral value

On the continuous self-report axis, q(1-q) is not a variance identity, so the
metric's own held-out autoregression is used instead of binary geometry.  For
mixed pools, the offered-pool metric is reconstructed from the simulated host
metric, the frozen supplier metric, and source separation using a small ridge
fit learned only from non-held-out runs.

The headline simulation freezes agreement and supplier state after round 1.
This makes judge-schedule changes and mid-run agreement changes genuine model
failures rather than allowing the simulator to peek at later rounds.

For the nine scheduled judge-swap runs, a separate online diagnostic treats
the first pool scored by the new judge as a new initial observation.  It
remeasures exactly the state available at an ordinary first round, then rolls
the remaining segment forward without reading any later state.

Run:    python3 scripts/analysis_spread_rollout_bakeoff.py
Writes: experiments/spread_rollout_bakeoff.json
"""

import json
import os
from collections import defaultdict

import numpy as np


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT = os.path.join(ROOT, "experiments", "spread_util_unified.json")
OUTPUT = os.path.join(ROOT, "experiments", "spread_rollout_bakeoff.json")


METRICS = {
    "mean_within_prompt_population_sd": {
        "whole": "mean_item_sd",
        "own": "own_spread",
        "supplier": "cogen_source_mean_item_sd",
        "bound": 0.5,
    },
    "rms_within_prompt_population_sd": {
        "whole": "rms_item_sd",
        "own": "own_rms_item_sd",
        "supplier": "cogen_source_rms_item_sd",
        "bound": 0.5,
    },
    "mean_within_prompt_variance": {
        "whole": "mean_item_variance",
        "own": "own_mean_item_variance",
        "supplier": "cogen_source_mean_item_variance",
        "bound": 0.25,
    },
    "mean_pairwise_absolute_score_difference": {
        "whole": "mean_pairwise_absolute_difference",
        "own": "own_pairwise_absolute_difference",
        "supplier": "cogen_source_mean_pairwise_absolute_difference",
        "bound": 1.0,
    },
    "mean_within_prompt_mean_absolute_deviation": {
        "whole": "mean_item_mean_absolute_deviation",
        "own": "own_mean_item_mean_absolute_deviation",
        "supplier": "cogen_source_mean_item_mean_absolute_deviation",
        "bound": 0.5,
    },
    "mean_within_prompt_range": {
        "whole": "mean_item_range",
        "own": "own_mean_item_range",
        "supplier": "cogen_source_mean_item_range",
        "bound": 1.0,
    },
    "median_within_prompt_population_sd": {
        "whole": "median_item_sd",
        "own": "own_median_item_sd",
        "supplier": "cogen_source_median_item_sd",
        "bound": 0.5,
    },
    "total_sd_including_between_prompt_variation": {
        "whole": "hierarchical_total_sd",
        "own": "own_hierarchical_total_sd",
        "supplier": "cogen_source_hierarchical_total_sd",
        "bound": 0.5,
    },
    "fraction_prompts_with_any_score_difference": {
        "whole": "fraction_items_with_any_difference",
        "own": "own_fraction_items_with_any_difference",
        "supplier": "cogen_source_fraction_items_with_any_difference",
        "bound": 1.0,
    },
    "mean_within_prompt_binary_entropy_bits": {
        "whole": "mean_item_binary_entropy_bits",
        "own": "own_mean_item_binary_entropy_bits",
        "supplier": "cogen_source_mean_item_binary_entropy_bits",
        "bound": 1.0,
        "axis": "risk",
    },
}

EXACT_BINARY_METRICS = {
    "mean_within_prompt_population_sd",
    "rms_within_prompt_population_sd",
    "mean_within_prompt_variance",
    "total_sd_including_between_prompt_variation",
}

DYNAMIC_MODES = ("geometry", "autoregression", "frozen")
VALIDATIONS = ("leave_one_run_out", "leave_one_condition_out")

# First one-indexed round scored by the replacement base judge.  These schedule
# definitions are fixed by the experiment conditions, not inferred from the
# observed trajectories.
JUDGE_SWAP_FIRST_NEW_ROUND = {
    "press_d1": 2,
    "press_d2": 3,
    "press_d3": 4,
    "press_to_base": 5,
}


def run_key(row):
    return (row["cond"], row["seed"], row["source"])


def make_runs(records):
    grouped = defaultdict(list)
    for row in records:
        grouped[run_key(row)].append(row)
    return [
        (key, sorted(rows, key=lambda r: r["round"]))
        for key, rows in grouped.items()
        if len(rows) >= 2 and min(r["round"] for r in rows) == 1
    ]


def make_transitions(records):
    grouped = defaultdict(dict)
    for row in records:
        grouped[run_key(row)][row["round"]] = row
    out = []
    for key, rounds in grouped.items():
        for current_round, row in rounds.items():
            nxt = rounds.get(current_round + 1)
            if nxt is None:
                continue
            out.append({"key": key, "row": row, "next": nxt})
    return out


def ols_fit(xs, ys, through_origin=False):
    x = np.asarray(xs, float)
    y = np.asarray(ys, float)
    if len(x) < 3 or np.std(x) < 1e-12:
        return None
    if through_origin:
        denom = float(np.dot(x, x))
        if denom < 1e-12:
            return None
        return {"intercept": 0.0, "slope": float(np.dot(x, y) / denom)}
    slope, intercept = np.polyfit(x, y, 1)
    return {"intercept": float(intercept), "slope": float(slope)}


def apply_fit(fit, x):
    return fit["intercept"] + fit["slope"] * x


def ridge_fit(features, targets, penalty=1e-3):
    """Small stable mixture map; intercept is not penalized."""
    x = np.asarray(features, float)
    y = np.asarray(targets, float)
    if len(x) < x.shape[1] + 2:
        return None
    design = np.column_stack([np.ones(len(x)), x])
    scale = np.std(design[:, 1:], axis=0)
    scale[scale < 1e-8] = 1.0
    design_scaled = design.copy()
    design_scaled[:, 1:] /= scale
    reg = np.eye(design_scaled.shape[1]) * penalty
    reg[0, 0] = 0.0
    beta = np.linalg.solve(design_scaled.T @ design_scaled + reg, design_scaled.T @ y)
    beta[1:] /= scale
    return beta


def ridge_predict(beta, features):
    return float(beta[0] + np.dot(beta[1:], np.asarray(features, float)))


def mixture_features(own_metric, supplier_metric, own_mean, supplier_mean):
    sep = abs(own_mean - supplier_mean)
    return [own_metric, supplier_metric, sep, sep * sep]


def fit_components(train_records, train_transitions, axis, metric, dynamic_mode):
    spec = METRICS[metric]
    records = [
        r for r in train_records
        if r["axis"] == axis and r.get("rho") is not None
        and r.get(spec["whole"]) is not None
    ]
    selector_fit = ols_fit(
        [r["rho"] * r[spec["whole"]] for r in records],
        [r["gap"] for r in records],
    )

    transitions = [
        t for t in train_transitions
        if t["row"]["axis"] == axis
    ]
    q_fit = ols_fit(
        [t["row"]["self_relative_gap"] for t in transitions],
        [t["next"]["own_mean"] - t["row"]["own_mean"] for t in transitions],
    )
    value_fit = ols_fit(
        [r["pull"] for r in train_records if r["axis"] == axis],
        [r["drift"] for r in train_records if r["axis"] == axis],
    )
    rho_transitions = [
        t for t in transitions
        if t["row"].get("rho") is not None and t["next"].get("rho") is not None
    ]
    rho_fit = ols_fit(
        [t["row"]["rho"] for t in rho_transitions],
        [t["next"]["rho"] for t in rho_transitions],
    )

    metric_transitions = [
        t for t in transitions
        if t["row"].get(spec["own"]) is not None
        and t["next"].get(spec["own"]) is not None
    ]
    auxiliary = None
    if dynamic_mode == "frozen":
        dynamic_fit = {"intercept": 0.0, "slope": 1.0}
        dynamic_kind = "frozen_first_round_metric"
    elif dynamic_mode == "autoregression":
        dynamic_fit = ols_fit(
            [t["row"][spec["own"]] for t in metric_transitions],
            [t["next"][spec["own"]] for t in metric_transitions],
        )
        dynamic_kind = "metric_autoregression"
    elif axis == "risk" and metric in EXACT_BINARY_METRICS:
        between_fit = ols_fit(
            [t["row"]["own_between_item_mean_variance"] for t in metric_transitions],
            [t["next"]["own_between_item_mean_variance"] for t in metric_transitions],
        )
        jensen_fit = ols_fit(
            [
                t["row"]["own_spread"] - t["row"]["own_rms_item_sd"]
                for t in metric_transitions
            ],
            [
                t["next"]["own_spread"] - t["next"]["own_rms_item_sd"]
                for t in metric_transitions
            ],
        )
        dynamic_fit = {"intercept": 0.0, "slope": 0.0}
        dynamic_kind = "exact_binary_variance_decomposition"
        auxiliary = {"between_ar": between_fit, "jensen_ar": jensen_fit}
    elif axis == "risk":
        dynamic_fit = ols_fit(
            [
                t["next"]["own_mean"] * (1.0 - t["next"]["own_mean"])
                - t["row"]["own_mean"] * (1.0 - t["row"]["own_mean"])
                for t in metric_transitions
            ],
            [t["next"][spec["own"]] - t["row"][spec["own"]] for t in metric_transitions],
        )
        dynamic_kind = "delta_metric_from_delta_binary_headroom"
    else:
        dynamic_fit = ols_fit(
            [t["row"][spec["own"]] for t in metric_transitions],
            [t["next"][spec["own"]] for t in metric_transitions],
        )
        dynamic_kind = "metric_autoregression"

    mixed = [
        r for r in train_records
        if r["axis"] == axis and r["composition"] != "self-only"
        and r.get(spec["supplier"]) is not None
    ]
    mixture_fit = ridge_fit(
        [
            mixture_features(
                r[spec["own"]], r[spec["supplier"]],
                r["own_mean"], r["cogen_mean"],
            )
            for r in mixed
        ],
        [r[spec["whole"]] for r in mixed],
    )

    if not all((selector_fit, q_fit, value_fit, dynamic_fit, rho_fit)):
        return None
    if dynamic_kind == "exact_binary_variance_decomposition" and not all(auxiliary.values()):
        return None
    return {
        "selector": selector_fit,
        "q_update": q_fit,
        "value_update": value_fit,
        "rho_update": rho_fit,
        "metric_dynamic": dynamic_fit,
        "dynamic_kind": dynamic_kind,
        "auxiliary": auxiliary,
        "mixture": mixture_fit,
    }


def regime(row):
    if row["composition"] != "self-only":
        return "intervention"
    if row["judge"] == "schedule":
        return "judge-swap"
    if (
        row["judge"] in ("score oracle", "cautious copy")
        or (row["judge"] == "self" and row["format"] == "candid-prompt")
    ):
        return "self-force"
    return "self-weak"


def simulate(
    recs, spec, fits, metric_name,
    rho_mode="frozen_round1", offered_metric_mode="simulated",
):
    first = recs[0]
    q = float(first["own_mean"])
    value = float(first["value"])
    own_metric = float(first[spec["own"]])
    between_variance = float(first["own_between_item_mean_variance"])
    jensen_gap = float(first["own_spread"] - first["own_rms_item_sd"])
    rho = float(first["rho"])
    mixed = first["composition"] != "self-only"
    supplier_mean = float(first["cogen_mean"]) if mixed else None
    supplier_metric = float(first[spec["supplier"]]) if mixed else None
    supplier_share = float(first.get("pool_cogen_fraction") or 0.0) if mixed else 0.0
    if mixed:
        first_reconstructed = ridge_predict(
            fits["mixture"],
            mixture_features(own_metric, supplier_metric, q, supplier_mean),
        )
        mixture_offset = float(first[spec["whole"]] - first_reconstructed)
    else:
        mixture_offset = 0.0

    rounds = []
    for index, observed in enumerate(recs):
        if mixed:
            pool_mean = (1.0 - supplier_share) * q + supplier_share * supplier_mean
            offered_metric = ridge_predict(
                fits["mixture"],
                mixture_features(own_metric, supplier_metric, q, supplier_mean),
            ) + mixture_offset
            offered_metric = float(np.clip(offered_metric, 0.0, spec["bound"]))
        else:
            pool_mean = q
            offered_metric = own_metric

        if rho_mode == "observed_each_round" and observed.get("rho") is not None:
            rho_used = float(observed["rho"])
        else:
            rho_used = rho
        if offered_metric_mode == "observed_each_round":
            offered_metric = float(observed[spec["whole"]])
        selector_gap = apply_fit(fits["selector"], rho_used * offered_metric)
        kept_mean = float(np.clip(pool_mean + selector_gap, 0.0, 1.0))
        selector_gap = kept_mean - pool_mean
        displacement = kept_mean - q
        pull = kept_mean - value

        q_next = float(np.clip(q + apply_fit(fits["q_update"], displacement), 0.0, 1.0))
        value_next = float(np.clip(value + apply_fit(fits["value_update"], pull), 0.0, 1.0))
        if fits["dynamic_kind"] == "frozen_first_round_metric":
            own_metric_next = own_metric
        elif fits["dynamic_kind"] == "exact_binary_variance_decomposition":
            between_variance_next = float(np.clip(
                apply_fit(fits["auxiliary"]["between_ar"], between_variance),
                0.0,
                q_next * (1.0 - q_next),
            ))
            within_variance_next = max(
                0.0,
                q_next * (1.0 - q_next) - between_variance_next,
            )
            jensen_gap_next = apply_fit(fits["auxiliary"]["jensen_ar"], jensen_gap)
            if metric_name == "mean_within_prompt_variance":
                own_metric_next = within_variance_next
            elif metric_name == "rms_within_prompt_population_sd":
                own_metric_next = float(np.sqrt(within_variance_next))
            elif metric_name == "total_sd_including_between_prompt_variation":
                own_metric_next = float(np.sqrt(q_next * (1.0 - q_next)))
            else:
                own_metric_next = float(np.sqrt(within_variance_next) + jensen_gap_next)
        elif fits["dynamic_kind"] == "delta_metric_from_delta_binary_headroom":
            delta_headroom = q_next * (1.0 - q_next) - q * (1.0 - q)
            own_metric_next = own_metric + apply_fit(fits["metric_dynamic"], delta_headroom)
        else:
            own_metric_next = apply_fit(fits["metric_dynamic"], own_metric)
        own_metric_next = float(np.clip(own_metric_next, 0.0, spec["bound"]))

        rounds.append({
            "round": observed["round"],
            "q_pred": q,
            "q_true": observed["own_mean"],
            "own_metric_pred": own_metric,
            "own_metric_true": observed[spec["own"]],
            "offered_metric_pred": offered_metric,
            "offered_metric_true": observed[spec["whole"]],
            "gap_pred": selector_gap,
            "gap_true": observed["gap"],
            "value_after_pred": value_next,
            "value_after_true": observed["value"] + observed["drift"],
            "rho_used": rho_used,
            "rho_frozen": rho,
            "rho_true": observed.get("rho"),
        })
        q, value, own_metric = q_next, value_next, own_metric_next
        if rho_mode == "autoregression":
            rho = float(np.clip(apply_fit(fits["rho_update"], rho), -1.0, 1.0))
        if fits["dynamic_kind"] == "exact_binary_variance_decomposition":
            between_variance, jensen_gap = between_variance_next, jensen_gap_next
    return rounds


def mean(values):
    return float(np.mean(values)) if values else None


def prediction_metrics(actual, predicted):
    y = np.asarray(actual, float)
    p = np.asarray(predicted, float)
    if len(y) == 0:
        return {"n": 0, "mae": None, "rmse": None, "r2": None, "r": None}
    denom = float(np.sum((y - np.mean(y)) ** 2))
    return {
        "n": int(len(y)),
        "mae": float(np.mean(np.abs(y - p))),
        "rmse": float(np.sqrt(np.mean((y - p) ** 2))),
        "r2": float(1.0 - np.sum((y - p) ** 2) / denom) if denom > 0 else None,
        "r": (
            float(np.corrcoef(y, p)[0, 1])
            if len(y) >= 3 and np.std(y) > 0 and np.std(p) > 0 else None
        ),
    }


def aggregate(per_run):
    all_rounds = [rd for run in per_run for rd in run["rounds"]]
    transition_rounds = [rd for run in per_run for rd in run["rounds"][1:]]
    value_end_true = [run["rounds"][-1]["value_after_true"] for run in per_run]
    value_end_pred = [run["rounds"][-1]["value_after_pred"] for run in per_run]
    value_end_persist = [run["v1"] for run in per_run]
    q_true = [rd["q_true"] for rd in transition_rounds]
    q_pred = [rd["q_pred"] for rd in transition_rounds]
    q_persist = [run["q1"] for run in per_run for _ in run["rounds"][1:]]
    metric_true = [rd["own_metric_true"] for rd in transition_rounds]
    metric_pred = [rd["own_metric_pred"] for rd in transition_rounds]
    metric_persist = [run["metric1"] for run in per_run for _ in run["rounds"][1:]]
    moved = []
    direction_hits = []
    for run in per_run:
        endpoint_true = run["rounds"][-1]["value_after_true"]
        endpoint_pred = run["rounds"][-1]["value_after_pred"]
        if abs(endpoint_true - run["v1"]) >= 0.15:
            moved.append(run)
            if (
                (endpoint_pred - run["v1"]) * (endpoint_true - run["v1"]) > 0
                and abs(endpoint_pred - run["v1"]) >= 0.05
            ):
                direction_hits.append(run)
    return {
        "n_runs": len(per_run),
        "n_rounds": len(all_rounds),
        "behavioral_value_endpoint": prediction_metrics(value_end_true, value_end_pred),
        "behavioral_value_endpoint_persistence": prediction_metrics(value_end_true, value_end_persist),
        "behavioral_value_all_rounds": prediction_metrics(
            [rd["value_after_true"] for rd in all_rounds],
            [rd["value_after_pred"] for rd in all_rounds],
        ),
        "own_candidate_mean_rounds_2plus": prediction_metrics(q_true, q_pred),
        "own_candidate_mean_persistence": prediction_metrics(q_true, q_persist),
        "own_metric_rounds_2plus": prediction_metrics(metric_true, metric_pred),
        "own_metric_persistence": prediction_metrics(metric_true, metric_persist),
        "selector_gap_all_rounds": prediction_metrics(
            [rd["gap_true"] for rd in all_rounds],
            [rd["gap_pred"] for rd in all_rounds],
        ),
        "offered_metric_all_rounds": prediction_metrics(
            [rd["offered_metric_true"] for rd in all_rounds],
            [rd["offered_metric_pred"] for rd in all_rounds],
        ),
        "direction_on_runs_moving_at_least_0_15": {
            "n_moved": len(moved),
            "n_hits": len(direction_hits),
            "hit_rate": len(direction_hits) / len(moved) if moved else None,
        },
    }


def grouped_aggregates(per_run):
    groups = {
        "all": per_run,
        "all_minus_judge_swap": [r for r in per_run if r["regime"] != "judge-swap"],
        "selection_driven": [r for r in per_run if r["regime"] in ("intervention", "self-force")],
        "intervention": [r for r in per_run if r["regime"] == "intervention"],
        "self_force": [r for r in per_run if r["regime"] == "self-force"],
        "self_weak": [r for r in per_run if r["regime"] == "self-weak"],
        "judge_swap": [r for r in per_run if r["regime"] == "judge-swap"],
        "risk": [r for r in per_run if r["axis"] == "risk"],
        "selfreport": [r for r in per_run if r["axis"] == "selfreport"],
        "risk_mixed": [r for r in per_run if r["axis"] == "risk" and r["composition"] != "self-only"],
        "risk_self_only": [r for r in per_run if r["axis"] == "risk" and r["composition"] == "self-only"],
        "selfreport_mixed": [r for r in per_run if r["axis"] == "selfreport" and r["composition"] != "self-only"],
        "selfreport_self_only": [r for r in per_run if r["axis"] == "selfreport" and r["composition"] == "self-only"],
    }
    return {name: aggregate(rows) for name, rows in groups.items() if rows}


def judge_swap_refresh_aggregate(per_run):
    truth = [run["endpoint_true"] for run in per_run]
    methods = {
        "closed_from_round1": [run["endpoint_closed"] for run in per_run],
        "refreshed_at_swap": [run["endpoint_refreshed"] for run in per_run],
        "persistence_from_swap": [run["value_at_swap"] for run in per_run],
        "persistence_from_round1": [run["value_round1"] for run in per_run],
    }
    endpoint = {
        name: prediction_metrics(truth, predictions)
        for name, predictions in methods.items()
    }
    post_swap_rounds = [rd for run in per_run for rd in run["refreshed_rounds"]]
    moving = [
        run for run in per_run
        if abs(run["endpoint_true"] - run["value_at_swap"]) >= 0.15
    ]
    direction_hits = [
        run for run in moving
        if (
            (run["endpoint_refreshed"] - run["value_at_swap"])
            * (run["endpoint_true"] - run["value_at_swap"]) > 0
            and abs(run["endpoint_refreshed"] - run["value_at_swap"]) >= 0.05
        )
    ]

    def paired_reduction(baseline_key, forecast_key, seed):
        differences = np.asarray([
            abs(run["endpoint_true"] - run[baseline_key])
            - abs(run["endpoint_true"] - run[forecast_key])
            for run in per_run
        ])
        rng = np.random.default_rng(seed)
        boots = np.mean(
            rng.choice(
                differences,
                size=(20000, len(differences)),
                replace=True,
            ),
            axis=1,
        )
        return {
            "mean_mae_reduction": float(np.mean(differences)),
            "bootstrap_95pct_ci": [
                float(np.quantile(boots, 0.025)),
                float(np.quantile(boots, 0.975)),
            ],
            "forecast_strict_wins": int(np.sum(differences > 0)),
            "baseline_strict_wins": int(np.sum(differences < 0)),
            "ties": int(np.sum(differences == 0)),
        }
    return {
        "n_runs": len(per_run),
        "endpoint": endpoint,
        "closed_to_refreshed_endpoint_mae_reduction": (
            endpoint["closed_from_round1"]["mae"]
            - endpoint["refreshed_at_swap"]["mae"]
        ),
        "paired_endpoint_error_reduction": {
            "versus_closed_from_round1": paired_reduction(
                "endpoint_closed", "endpoint_refreshed", 20260715
            ),
            "versus_persistence_from_swap": paired_reduction(
                "value_at_swap", "endpoint_refreshed", 20260716
            ),
        },
        "refreshed_post_swap_value_all_rounds": prediction_metrics(
            [rd["value_after_true"] for rd in post_swap_rounds],
            [rd["value_after_pred"] for rd in post_swap_rounds],
        ),
        "direction_from_swap_on_runs_moving_at_least_0_15": {
            "n_moved": len(moving),
            "n_hits": len(direction_hits),
            "hit_rate": len(direction_hits) / len(moving) if moving else None,
        },
    }


def bootstrap_difference(primary_runs, alternative_runs, n_boot=5000):
    primary = {r["run_key"]: r for r in primary_runs}
    alternative = {r["run_key"]: r for r in alternative_runs}
    keys = sorted(set(primary) & set(alternative))
    diffs = []
    wins = 0
    for key in keys:
        p = primary[key]
        a = alternative[key]
        truth = p["rounds"][-1]["value_after_true"]
        p_err = abs(p["rounds"][-1]["value_after_pred"] - truth)
        a_err = abs(a["rounds"][-1]["value_after_pred"] - truth)
        diffs.append(a_err - p_err)
        wins += p_err < a_err
    if not diffs:
        return None
    rng = np.random.default_rng(20260715)
    arr = np.asarray(diffs)
    boots = np.mean(rng.choice(arr, size=(n_boot, len(arr)), replace=True), axis=1)
    return {
        "n_paired_runs": len(arr),
        "alternative_minus_primary_endpoint_mae": float(np.mean(arr)),
        "bootstrap_95pct_ci": [float(np.quantile(boots, 0.025)), float(np.quantile(boots, 0.975))],
        "primary_strict_wins": wins,
        "alternative_strict_wins": int(np.sum(arr < 0)),
        "ties": int(np.sum(arr == 0)),
    }


def rounded(value):
    if isinstance(value, dict):
        return {key: rounded(item) for key, item in value.items()}
    if isinstance(value, list):
        return [rounded(item) for item in value]
    if isinstance(value, float):
        return round(value, 6)
    return value


def main():
    with open(INPUT) as handle:
        records = json.load(handle)["records"]
    runs = make_runs(records)
    transitions = make_transitions(records)

    def evaluate(
        metric, spec, dynamic_mode, validation,
        rho_mode="frozen_round1", offered_metric_mode="simulated",
    ):
        per_run = []
        for held_key, recs in runs:
            axis = recs[0]["axis"]
            if spec.get("axis") not in (None, axis) or recs[0].get("rho") is None:
                continue
            if validation == "leave_one_run_out":
                train_records = [r for r in records if run_key(r) != held_key]
                train_transitions = [t for t in transitions if t["key"] != held_key]
            else:
                held_condition = recs[0]["cond"]
                train_records = [r for r in records if r["cond"] != held_condition]
                train_transitions = [
                    t for t in transitions if t["row"]["cond"] != held_condition
                ]
            fits = fit_components(
                train_records, train_transitions, axis, metric, dynamic_mode
            )
            if fits is None or (recs[0]["composition"] != "self-only" and fits["mixture"] is None):
                continue
            sim = simulate(
                recs, spec, fits, metric,
                rho_mode=rho_mode,
                offered_metric_mode=offered_metric_mode,
            )
            per_run.append({
                "run_key": "|".join(map(str, held_key)),
                "cond": recs[0]["cond"],
                "seed": recs[0]["seed"],
                "source": recs[0]["source"],
                "axis": axis,
                "organism": recs[0]["organism"],
                "judge": recs[0]["judge"],
                "format": recs[0]["format"],
                "composition": recs[0]["composition"],
                "regime": regime(recs[0]),
                "n_rounds": len(recs),
                "q1": recs[0]["own_mean"],
                "v1": recs[0]["value"],
                "metric1": recs[0][spec["own"]],
                "rho1": recs[0]["rho"],
                "rounds": sim,
            })
        return {
            "definition": spec,
            "dynamic_mode": dynamic_mode,
            "validation": validation,
            "rho_mode": rho_mode,
            "offered_metric_mode": offered_metric_mode,
            "aggregates": grouped_aggregates(per_run),
            "per_run": per_run,
        }

    results = {
        validation: {
            mode: {
                metric: evaluate(metric, spec, mode, validation)
                for metric, spec in METRICS.items()
            }
            for mode in DYNAMIC_MODES
        }
        for validation in VALIDATIONS
    }

    primary_name = "mean_within_prompt_population_sd"
    headline_mode = "geometry"
    headline_validation = "leave_one_run_out"
    headline_results = results[headline_validation][headline_mode]
    primary_runs = headline_results[primary_name]["per_run"]
    comparison_groups = {
        "all": lambda r: True,
        "all_minus_judge_swap": lambda r: r["regime"] != "judge-swap",
        "selection_driven": lambda r: r["regime"] in ("intervention", "self-force"),
        "intervention": lambda r: r["regime"] == "intervention",
        "risk": lambda r: r["axis"] == "risk",
        "selfreport": lambda r: r["axis"] == "selfreport",
    }
    paired = {}
    rankings = {}
    combined_rankings = {}
    for validation in VALIDATIONS:
        paired[validation] = {}
        for mode, mode_results in results[validation].items():
            mode_primary = mode_results[primary_name]["per_run"]
            paired[validation][mode] = {}
            for metric, result in mode_results.items():
                if metric == primary_name:
                    continue
                paired[validation][mode][metric] = {
                    group: bootstrap_difference(
                        [r for r in mode_primary if include(r)],
                        [r for r in result["per_run"] if include(r)],
                    )
                    for group, include in comparison_groups.items()
                }

        rankings[validation] = {}
        combined = []
        for mode, mode_results in results[validation].items():
            ranking = []
            for metric, result in mode_results.items():
                agg = result["aggregates"]
                selection = agg.get("selection_driven", {})
                all_minus = agg.get("all_minus_judge_swap", {})
                row = {
                    "validation": validation,
                    "dynamic_mode": mode,
                    "metric": metric,
                    "selection_driven_n_runs": selection.get("n_runs"),
                    "selection_driven_endpoint_mae": selection.get("behavioral_value_endpoint", {}).get("mae"),
                    "selection_driven_persistence_mae": selection.get("behavioral_value_endpoint_persistence", {}).get("mae"),
                    "selection_driven_value_round_mae": selection.get("behavioral_value_all_rounds", {}).get("mae"),
                    "all_minus_judgeswap_endpoint_mae": all_minus.get("behavioral_value_endpoint", {}).get("mae"),
                    "risk_q_mae": agg.get("risk", {}).get("own_candidate_mean_rounds_2plus", {}).get("mae"),
                    "risk_metric_mae": agg.get("risk", {}).get("own_metric_rounds_2plus", {}).get("mae"),
                    "selfreport_q_mae": agg.get("selfreport", {}).get("own_candidate_mean_rounds_2plus", {}).get("mae"),
                    "selfreport_metric_mae": agg.get("selfreport", {}).get("own_metric_rounds_2plus", {}).get("mae"),
                }
                ranking.append(row)
                combined.append(row)
            ranking.sort(key=lambda row: (
                float("inf") if row["selection_driven_endpoint_mae"] is None
                else row["selection_driven_endpoint_mae"]
            ))
            rankings[validation][mode] = ranking
        combined.sort(key=lambda row: (
            float("inf") if row["selection_driven_endpoint_mae"] is None
            else row["selection_driven_endpoint_mae"]
        ))
        combined_rankings[validation] = combined

    diagnostic_specs = {
        "closed_loop": ("frozen_round1", "simulated"),
        "modeled_agreement_ar": ("autoregression", "simulated"),
        "oracle_agreement": ("observed_each_round", "simulated"),
        "oracle_offered_spread": ("frozen_round1", "observed_each_round"),
        "oracle_agreement_and_spread": ("observed_each_round", "observed_each_round"),
    }
    error_attribution = {}
    for diagnostic_metric in (
        primary_name,
        "mean_within_prompt_range",
    ):
        error_attribution[diagnostic_metric] = {}
        diagnostic_metric_spec = METRICS[diagnostic_metric]
        for validation in VALIDATIONS:
            error_attribution[diagnostic_metric][validation] = {}
            for name, (rho_mode, offered_mode) in diagnostic_specs.items():
                diagnostic = evaluate(
                    diagnostic_metric, diagnostic_metric_spec, "geometry", validation,
                    rho_mode=rho_mode,
                    offered_metric_mode=offered_mode,
                )
                error_attribution[diagnostic_metric][validation][name] = diagnostic["aggregates"]

    def evaluate_judge_swap_refresh(metric, dynamic_mode, validation):
        """Forecast the post-swap segment from one new boundary observation."""
        spec = METRICS[metric]
        per_run = []
        for held_key, recs in runs:
            condition = recs[0]["cond"]
            if condition not in JUDGE_SWAP_FIRST_NEW_ROUND:
                continue
            axis = recs[0]["axis"]
            if validation == "leave_one_run_out":
                train_records = [r for r in records if run_key(r) != held_key]
                train_transitions = [t for t in transitions if t["key"] != held_key]
            else:
                train_records = [r for r in records if r["cond"] != condition]
                train_transitions = [
                    t for t in transitions if t["row"]["cond"] != condition
                ]
            fits = fit_components(
                train_records, train_transitions, axis, metric, dynamic_mode
            )
            if fits is None:
                continue

            closed = simulate(recs, spec, fits, metric)
            first_new_round = JUDGE_SWAP_FIRST_NEW_ROUND[condition]
            segment = [dict(row) for row in recs[first_new_round - 1:]]
            if not segment:
                continue
            # Agreement is undefined when every candidate has the same value.
            # In that case rho*spread is exactly zero, so rho=0 is the neutral
            # numerical representation of the identified selector input.
            if segment[0].get("rho") is None:
                if abs(float(segment[0][spec["whole"]])) > 1e-12:
                    continue
                segment[0]["rho"] = 0.0
            refreshed = simulate(segment, spec, fits, metric)
            per_run.append({
                "run_key": "|".join(map(str, held_key)),
                "cond": condition,
                "seed": recs[0]["seed"],
                "first_new_judge_round": first_new_round,
                "value_round1": recs[0]["value"],
                "value_at_swap": segment[0]["value"],
                "mean_at_swap": segment[0]["own_mean"],
                "metric_at_swap": segment[0][spec["own"]],
                "agreement_at_swap": segment[0]["rho"],
                "endpoint_true": refreshed[-1]["value_after_true"],
                "endpoint_closed": closed[-1]["value_after_pred"],
                "endpoint_refreshed": refreshed[-1]["value_after_pred"],
                "refreshed_rounds": refreshed,
            })
        return {
            "metric": metric,
            "dynamic_mode": dynamic_mode,
            "validation": validation,
            "observation_rule": (
                "remeasure value, own candidate mean, candidate metric, and "
                "judge/value agreement on the first pool scored by the new "
                "judge; read no later state"
            ),
            "aggregate": judge_swap_refresh_aggregate(per_run),
            "per_run": per_run,
        }

    judge_swap_refresh = {
        validation: {
            "mean_sd_geometry": evaluate_judge_swap_refresh(
                primary_name, "geometry", validation
            ),
            "mean_sd_frozen": evaluate_judge_swap_refresh(
                primary_name, "frozen", validation
            ),
            "rankable_support_frozen": evaluate_judge_swap_refresh(
                "mean_within_prompt_range", "frozen", validation
            ),
        }
        for validation in VALIDATIONS
    }

    # The alternative models are fully reproducible from this script; keep
    # their aggregate scores in the committed artifact, but avoid repeating
    # every round trajectory 60 times.  Preserve detailed trajectories for the
    # primary mean-SD model under every validation/dynamic rule.
    stored_results = {}
    for validation, validation_results in results.items():
        stored_results[validation] = {}
        for mode, mode_results in validation_results.items():
            stored_results[validation][mode] = {}
            for metric, result in mode_results.items():
                stored = {k: v for k, v in result.items() if k != "per_run"}
                if metric in (primary_name, "mean_within_prompt_range"):
                    stored["per_run"] = result["per_run"]
                stored_results[validation][mode][metric] = stored

    output = rounded({
        "description": __doc__.strip().split("\n")[0],
        "input": os.path.relpath(INPUT, ROOT),
        "validation": "leave one complete run out; held-out run observed at round 1 only",
        "headline_assumptions": {
            "agreement": "rho fixed at held-out round-1 value",
            "supplier": "supplier mean and metric fixed at held-out round-1 values",
            "binary_spread_dynamics": "metric change fit from change in q(1-q)",
            "continuous_spread_dynamics": "metric-specific autoregression; no Bernoulli identity",
            "mixed_pool_metric": (
                "ridge reconstruction trained only on non-held-out runs; "
                "held-out first-round reconstruction residual carried forward"
            ),
        },
        "n_input_rounds": len(records),
        "n_input_runs": len(runs),
        "n_modelable_runs": len(primary_runs),
        "primary_metric": primary_name,
        "headline_dynamic_mode": headline_mode,
        "headline_validation": headline_validation,
        "rankings": rankings,
        "combined_rankings": combined_rankings,
        "paired_endpoint_comparison_vs_primary": paired,
        "error_attribution_by_metric": error_attribution,
        "judge_swap_refresh": judge_swap_refresh,
        "validations": stored_results,
    })
    with open(OUTPUT, "w") as handle:
        json.dump(output, handle, indent=1)

    print(f"{len(records)} rounds / {len(primary_runs)} modelable runs -> {OUTPUT}")
    for validation in VALIDATIONS:
        print(f"\n=== {validation} ===")
        for mode in DYNAMIC_MODES:
            print(f"\n[{mode}] metric                                    sel endpoint  all-no-swap  risk q  risk spread")
            for row in rankings[validation][mode]:
                print(
                    f"{row['metric'][:46]:46s} "
                    f"{row['selection_driven_endpoint_mae']:.4f}       "
                    f"{row['all_minus_judgeswap_endpoint_mae']:.4f}      "
                    f"{row['risk_q_mae']:.4f}   {row['risk_metric_mae']:.4f}"
                )


if __name__ == "__main__":
    main()
