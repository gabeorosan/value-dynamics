"""Bake off simple adjustments that may restore observed trajectory shape.

All fits are leave-one-condition-out.  The core model uses frozen mean
within-prompt SD and the scheduled judge-swap boundary refresh.  Alternatives
place Gaussian innovations at selection, generator update, agreement
persistence, latent value update, or finite-battery observation, then compare
forecast scores and trajectory shape.

Run:    .venv/bin/python scripts/analysis_trajectory_adjustments.py
Writes: experiments/trajectory_adjustment_bakeoff.json
"""

import importlib.util
import json
import os

import numpy as np


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BAKEOFF_SCRIPT = os.path.join(ROOT, "scripts", "analysis_spread_rollout_bakeoff.py")
INPUT = os.path.join(ROOT, "experiments", "spread_util_unified.json")
OUTPUT = os.path.join(ROOT, "experiments", "trajectory_adjustment_bakeoff.json")
N_PATHS = 400


module_spec = importlib.util.spec_from_file_location("spread_bakeoff", BAKEOFF_SCRIPT)
bakeoff = importlib.util.module_from_spec(module_spec)
module_spec.loader.exec_module(bakeoff)


VARIANTS = {
    "deterministic_frozen": {
        "value_noise": 0.0, "q_noise": 0.0, "rho": "frozen",
    },
    "value_noise_half": {
        "value_noise": 0.5, "q_noise": 0.0, "rho": "frozen",
    },
    "value_noise_full": {
        "value_noise": 1.0, "q_noise": 0.0, "rho": "frozen",
    },
    "value_gaussian_full": {
        "value_noise": 1.0, "q_noise": 0.0, "rho": "frozen",
        "noise_distribution": "gaussian",
    },
    "selector_gap_gaussian": {
        "value_noise": 0.0, "q_noise": 0.0, "gap_noise": 1.0,
        "rho": "frozen", "noise_distribution": "gaussian",
    },
    "observation_gaussian": {
        "value_noise": 0.0, "q_noise": 0.0, "observation_noise": 1.0,
        "rho": "frozen", "noise_distribution": "gaussian",
    },
    "selector_gap_and_observation_gaussian": {
        "value_noise": 0.0, "q_noise": 0.0, "gap_noise": 1.0,
        "observation_noise": 1.0, "rho": "frozen",
        "noise_distribution": "gaussian",
    },
    "process_gaussian_deconvolved": {
        "value_noise": 0.0, "q_noise": 0.0, "process_noise": 1.0,
        "rho": "frozen", "noise_distribution": "gaussian",
    },
    "selector_observation_process_gaussian": {
        "value_noise": 0.0, "q_noise": 0.0, "gap_noise": 1.0,
        "observation_noise": 1.0, "process_noise": 1.0,
        "rho": "frozen", "noise_distribution": "gaussian",
    },
    "q_gaussian": {
        "value_noise": 0.0, "q_noise": 1.0, "rho": "frozen",
        "noise_distribution": "gaussian",
    },
    "selector_q_observation_gaussian": {
        "value_noise": 0.0, "q_noise": 1.0, "gap_noise": 1.0,
        "observation_noise": 1.0, "rho": "frozen",
        "noise_distribution": "gaussian",
    },
    "rho_ar_gaussian": {
        "value_noise": 0.0, "q_noise": 0.0, "rho": "ar_stochastic",
        "noise_distribution": "gaussian",
    },
    "rho_persistence_gaussian": {
        "value_noise": 0.0, "q_noise": 0.0,
        "rho": "persistence_stochastic", "noise_distribution": "gaussian",
    },
    "selector_q_observation_rho_ar_gaussian": {
        "value_noise": 0.0, "q_noise": 1.0, "gap_noise": 1.0,
        "observation_noise": 1.0, "rho": "ar_stochastic",
        "noise_distribution": "gaussian",
    },
    "selector_q_observation_rho_persistence_gaussian": {
        "value_noise": 0.0, "q_noise": 1.0, "gap_noise": 1.0,
        "observation_noise": 1.0, "rho": "persistence_stochastic",
        "noise_distribution": "gaussian",
    },
    "selector_q_observation_rho_persistence_process_gaussian": {
        "value_noise": 0.0, "q_noise": 1.0, "gap_noise": 1.0,
        "observation_noise": 1.0, "process_noise": 1.0,
        "rho": "persistence_stochastic", "noise_distribution": "gaussian",
    },
    "selector_gap_and_half_value_gaussian": {
        "value_noise": 0.5, "q_noise": 0.0, "gap_noise": 1.0,
        "rho": "frozen", "noise_distribution": "gaussian",
    },
    "q_and_value_noise": {
        "value_noise": 1.0, "q_noise": 1.0, "rho": "frozen",
    },
    "judge_ar_deterministic": {
        "value_noise": 0.0, "q_noise": 0.0, "rho": "ar_deterministic",
    },
    "judge_feedback_deterministic": {
        "value_noise": 0.0, "q_noise": 0.0, "rho": "feedback_deterministic",
    },
    "judge_feedback_stochastic": {
        "value_noise": 0.0, "q_noise": 0.0, "rho": "feedback_stochastic",
    },
    "risk_feedback_deterministic": {
        "value_noise": 0.0, "q_noise": 0.0, "rho": "risk_feedback_deterministic",
    },
    "value_noise_and_judge_ar": {
        "value_noise": 1.0, "q_noise": 0.0, "rho": "ar_stochastic",
    },
    "value_noise_and_judge_feedback": {
        "value_noise": 1.0, "q_noise": 0.0, "rho": "feedback_stochastic",
    },
    "value_noise_and_risk_feedback": {
        "value_noise": 1.0, "q_noise": 0.0, "rho": "risk_feedback_stochastic",
    },
    "value_gaussian_and_risk_feedback": {
        "value_noise": 1.0, "q_noise": 0.0, "rho": "risk_feedback_stochastic",
        "noise_distribution": "gaussian",
    },
    "q_value_noise_and_judge_ar": {
        "value_noise": 1.0, "q_noise": 1.0, "rho": "ar_stochastic",
    },
    "q_value_noise_and_judge_feedback": {
        "value_noise": 1.0, "q_noise": 1.0, "rho": "feedback_stochastic",
    },
}


def fit_linear(features, targets):
    x = np.asarray(features, float)
    y = np.asarray(targets, float)
    design = np.column_stack([np.ones(len(x)), x])
    return np.linalg.lstsq(design, y, rcond=None)[0]


def apply_linear(beta, features):
    return float(beta[0] + np.dot(beta[1:], np.asarray(features, float)))


def centered(values):
    arr = np.asarray(values, float)
    return arr - np.mean(arr)


def measurement_sd(value, n):
    """Sampling SD for a bounded, approximately Bernoulli-valued battery."""
    if n is None or float(n) <= 0:
        return 0.0
    p = float(np.clip(value, 0.0, 1.0))
    return float(np.sqrt(max(0.0, p * (1.0 - p)) / float(n)))


def fit_noise_and_rho(train_records, train_transitions, axis, fits, metric_spec):
    axis_records = [row for row in train_records if row["axis"] == axis]
    axis_transitions = [
        transition for transition in train_transitions
        if transition["row"]["axis"] == axis
    ]
    value_residuals = centered([
        row["drift"]
        - bakeoff.apply_fit(fits["value_update"], row["pull"])
        for row in axis_records
    ])
    value_identity_residuals = centered([
        row["drift"] - row["pull"] for row in axis_records
    ])
    gap_residuals = centered([
        row["gap"]
        - bakeoff.apply_fit(
            fits["selector"], row["rho"] * row[metric_spec["whole"]]
        )
        for row in axis_records if row.get("rho") is not None
    ])
    q_residuals = centered([
        (transition["next"]["own_mean"] - transition["row"]["own_mean"])
        - bakeoff.apply_fit(
            fits["q_update"], transition["row"]["self_relative_gap"]
        )
        for transition in axis_transitions
    ])
    rho_transitions = [
        transition for transition in axis_transitions
        if transition["row"].get("rho") is not None
        and transition["next"].get("rho") is not None
    ]
    feedback_beta = fit_linear(
        [
            [
                transition["row"]["rho"],
                transition["row"]["rho"]
                * transition["row"][metric_spec["whole"]],
            ]
            for transition in rho_transitions
        ],
        [transition["next"]["rho"] for transition in rho_transitions],
    )
    feedback_residuals = centered([
        transition["next"]["rho"]
        - apply_linear(
            feedback_beta,
            [
                transition["row"]["rho"],
                transition["row"]["rho"]
                * transition["row"][metric_spec["whole"]],
            ],
        )
        for transition in rho_transitions
    ])
    ar_residuals = centered([
        transition["next"]["rho"]
        - bakeoff.apply_fit(fits["rho_update"], transition["row"]["rho"])
        for transition in rho_transitions
    ])
    persistence_residuals = centered([
        transition["next"]["rho"] - transition["row"]["rho"]
        for transition in rho_transitions
    ])
    value_residual_variance = float(np.var(value_residuals))
    carry = 1.0 - float(fits["value_update"]["slope"])
    measurement_variances = [
        measurement_sd(
            row["value"] + row["drift"],
            row.get("next_value_measurement_n"),
        ) ** 2
        + carry ** 2 * measurement_sd(
            row["value"], row.get("value_measurement_n")
        ) ** 2
        for row in axis_records
        if row.get("value_measurement_n") is not None
        and row.get("next_value_measurement_n") is not None
    ]
    mean_measurement_residual_variance = (
        float(np.mean(measurement_variances)) if measurement_variances else 0.0
    )
    process_sd = float(np.sqrt(max(
        0.0, value_residual_variance - mean_measurement_residual_variance
    )))
    identity_residual_variance = float(np.var(value_identity_residuals))
    identity_measurement_variances = [
        measurement_sd(
            row["value"] + row["drift"],
            row.get("next_value_measurement_n"),
        ) ** 2
        for row in axis_records
        if row.get("next_value_measurement_n") is not None
    ]
    identity_measurement_variance = (
        float(np.mean(identity_measurement_variances))
        if identity_measurement_variances else 0.0
    )
    return {
        "value": value_residuals,
        "value_identity": value_identity_residuals,
        "gap": gap_residuals,
        "q": q_residuals,
        "rho_feedback_beta": feedback_beta,
        "rho_feedback": feedback_residuals,
        "rho_ar": ar_residuals,
        "rho_persistence": persistence_residuals,
        "process_sd": process_sd,
        "value_residual_sd": float(np.sqrt(value_residual_variance)),
        "measurement_residual_sd": float(np.sqrt(
            mean_measurement_residual_variance
        )),
        "identity_process_sd": float(np.sqrt(max(
            0.0, identity_residual_variance - identity_measurement_variance
        ))),
    }


def draw(rng, residuals, scale, distribution="empirical_bootstrap"):
    if scale == 0.0 or len(residuals) == 0:
        return 0.0
    if distribution == "gaussian":
        return float(rng.normal(0.0, scale * np.std(residuals)))
    return float(scale * rng.choice(residuals))


def simulate_paths(recs, metric_spec, fits, noise, variant, rng):
    noise_distribution = variant.get(
        "noise_distribution", "empirical_bootstrap"
    )
    rho_mode = variant["rho"]
    if rho_mode.startswith("risk_feedback"):
        rho_mode = (
            rho_mode.replace("risk_", "")
            if recs[0]["axis"] == "risk" else "frozen"
        )
    n_paths = 1 if (
        variant["value_noise"] == 0.0
        and variant["q_noise"] == 0.0
        and variant.get("gap_noise", 0.0) == 0.0
        and variant.get("observation_noise", 0.0) == 0.0
        and variant.get("process_noise", 0.0) == 0.0
        and rho_mode in ("frozen", "ar_deterministic", "feedback_deterministic")
    ) else N_PATHS
    paths = []
    swap_round = bakeoff.JUDGE_SWAP_FIRST_NEW_ROUND.get(recs[0]["cond"])

    for _ in range(n_paths):
        q = float(recs[0]["own_mean"])
        value = float(recs[0]["value"])
        own_metric = float(recs[0][metric_spec["own"]])
        rho = float(recs[0]["rho"])
        mixed = recs[0]["composition"] != "self-only"
        supplier_mean = float(recs[0]["cogen_mean"]) if mixed else None
        supplier_metric = (
            float(recs[0][metric_spec["supplier"]]) if mixed else None
        )
        supplier_share = (
            float(recs[0].get("pool_cogen_fraction") or 0.0) if mixed else 0.0
        )
        if mixed:
            reconstructed = bakeoff.ridge_predict(
                fits["mixture"],
                bakeoff.mixture_features(
                    own_metric, supplier_metric, q, supplier_mean
                ),
            )
            mixture_offset = float(recs[0][metric_spec["whole"]] - reconstructed)
        else:
            mixture_offset = 0.0

        values = [value]
        for observed in recs:
            if swap_round is not None and observed["round"] == swap_round:
                q = float(observed["own_mean"])
                value = float(observed["value"])
                own_metric = float(observed[metric_spec["own"]])
                rho = (
                    float(observed["rho"])
                    if observed.get("rho") is not None else 0.0
                )
                values[-1] = value

            if mixed:
                pool_mean = (
                    (1.0 - supplier_share) * q + supplier_share * supplier_mean
                )
                offered_metric = bakeoff.ridge_predict(
                    fits["mixture"],
                    bakeoff.mixture_features(
                        own_metric, supplier_metric, q, supplier_mean
                    ),
                ) + mixture_offset
                offered_metric = float(np.clip(
                    offered_metric, 0.0, metric_spec["bound"]
                ))
            else:
                pool_mean = q
                offered_metric = own_metric

            gap = bakeoff.apply_fit(
                fits["selector"], rho * offered_metric
            )
            gap += draw(
                rng, noise["gap"], variant.get("gap_noise", 0.0),
                noise_distribution,
            )
            kept_mean = float(np.clip(pool_mean + gap, 0.0, 1.0))
            displacement = kept_mean - q
            pull = kept_mean - value

            q_next = float(np.clip(
                q + bakeoff.apply_fit(fits["q_update"], displacement)
                + draw(
                    rng, noise["q"], variant["q_noise"], noise_distribution
                ),
                0.0, 1.0,
            ))
            value_next = float(np.clip(
                value + bakeoff.apply_fit(fits["value_update"], pull)
                + draw(
                    rng, noise["value"], variant["value_noise"],
                    noise_distribution,
                ),
                0.0, 1.0,
            ))
            if variant.get("process_noise", 0.0):
                value_next = float(np.clip(
                    value_next + rng.normal(
                        0.0,
                        variant["process_noise"] * noise["process_sd"],
                    ),
                0.0, 1.0,
                ))

            if rho_mode.startswith("ar"):
                rho_next = bakeoff.apply_fit(fits["rho_update"], rho)
                if rho_mode == "ar_stochastic":
                    rho_next += draw(
                        rng, noise["rho_ar"], 1.0, noise_distribution
                    )
                rho = float(np.clip(rho_next, -1.0, 1.0))
            elif rho_mode == "persistence_stochastic":
                rho = float(np.clip(
                    rho + draw(
                        rng, noise["rho_persistence"], 1.0,
                        noise_distribution,
                    ),
                    -1.0, 1.0,
                ))
            elif rho_mode.startswith("feedback"):
                rho_next = apply_linear(
                    noise["rho_feedback_beta"],
                    [rho, rho * offered_metric],
                )
                if rho_mode == "feedback_stochastic":
                    rho_next += draw(
                        rng, noise["rho_feedback"], 1.0, noise_distribution
                    )
                rho = float(np.clip(rho_next, -1.0, 1.0))

            q, value = q_next, value_next
            measured_value = value
            if variant.get("observation_noise", 0.0):
                measured_value = float(np.clip(
                    value + rng.normal(
                        0.0,
                        variant["observation_noise"] * measurement_sd(
                            value, observed.get("next_value_measurement_n")
                        ),
                    ),
                    0.0, 1.0,
                ))
            values.append(measured_value)
        paths.append(values)
    return np.asarray(paths, float)


def simulate_observed_kept_paths(recs, fits, noise, mode, rng):
    stochastic = mode not in ("identity", "calibrated_deterministic")
    n_paths = N_PATHS if stochastic else 1
    swap_round = bakeoff.JUDGE_SWAP_FIRST_NEW_ROUND.get(recs[0]["cond"])
    paths = []
    for _ in range(n_paths):
        value = float(recs[0]["value"])
        values = [value]
        for observed in recs:
            if swap_round is not None and observed["round"] == swap_round:
                value = float(observed["value"])
                values[-1] = value
            kept_mean = float(observed["kept_mean"])
            if mode.startswith("identity"):
                value_next = kept_mean
            else:
                value_next = value + bakeoff.apply_fit(
                    fits["value_update"], kept_mean - value
                )
                if stochastic:
                    value_next += draw(
                        rng, noise["value"], 1.0, "gaussian"
                    )
            if mode == "identity_gaussian":
                value_next += draw(
                    rng, noise["value_identity"], 1.0, "gaussian"
                )
            elif mode in (
                "identity_process_gaussian",
                "identity_observation_process_gaussian",
            ):
                value_next += rng.normal(0.0, noise["identity_process_sd"])
            value = float(np.clip(value_next, 0.0, 1.0))
            measured_value = value
            if mode in (
                "identity_observation_gaussian",
                "identity_observation_process_gaussian",
            ):
                measured_value = float(np.clip(
                    value + rng.normal(
                        0.0,
                        measurement_sd(
                            value, observed.get("next_value_measurement_n")
                        ),
                    ),
                    0.0, 1.0,
                ))
            values.append(measured_value)
        paths.append(values)
    return np.asarray(paths, float)


def crps(samples, truth):
    samples = np.asarray(samples, float)
    first = float(np.mean(np.abs(samples - truth)))
    ordered = np.sort(samples)
    n = len(ordered)
    weights = 2 * np.arange(1, n + 1) - n - 1
    pair_term = float(np.sum(weights * ordered) / (n * n))
    return first - pair_term


def sign_changes(path, threshold=0.025):
    deltas = np.diff(path)
    signs = np.sign(deltas[np.abs(deltas) >= threshold])
    return int(np.sum(signs[1:] != signs[:-1])) if len(signs) >= 2 else 0


def path_properties(path):
    return {
        "total_variation": float(np.sum(np.abs(np.diff(path)))),
        "sign_changes": sign_changes(path),
        "endpoint": float(path[-1]),
        "low_rail": float(path[-1] <= 0.15),
        "high_rail": float(path[-1] >= 0.85),
    }


def evaluate_variant(run_results):
    endpoint_truth = []
    endpoint_mean = []
    endpoint_median = []
    crps_values = []
    coverage = []
    all_round_truth = []
    all_round_mean = []
    observed_properties = []
    simulated_properties = []

    for result in run_results:
        paths = result["paths"]
        truth = np.asarray(result["truth"], float)
        endpoints = paths[:, -1]
        endpoint_truth.append(truth[-1])
        endpoint_mean.append(float(np.mean(endpoints)))
        endpoint_median.append(float(np.median(endpoints)))
        crps_values.append(crps(endpoints, truth[-1]))
        low, high = np.quantile(endpoints, [0.1, 0.9])
        coverage.append(float(low <= truth[-1] <= high))
        all_round_truth.extend(truth[1:])
        all_round_mean.extend(np.mean(paths[:, 1:], axis=0))
        observed_properties.append(path_properties(truth))
        for path in paths:
            simulated_properties.append(path_properties(path))

    y = np.asarray(endpoint_truth)
    p = np.asarray(endpoint_mean)
    denom = np.sum((y - np.mean(y)) ** 2)
    yr = np.asarray(all_round_truth)
    pr = np.asarray(all_round_mean)
    round_denom = np.sum((yr - np.mean(yr)) ** 2)

    def prop_mean(rows, key):
        return float(np.mean([row[key] for row in rows]))

    return {
        "n_runs": len(run_results),
        "endpoint_mean_forecast": {
            "mae": float(np.mean(np.abs(y - p))),
            "rmse": float(np.sqrt(np.mean((y - p) ** 2))),
            "r2": float(1.0 - np.sum((y - p) ** 2) / denom),
        },
        "endpoint_median_mae": float(np.mean(np.abs(
            y - np.asarray(endpoint_median)
        ))),
        "endpoint_crps": float(np.mean(crps_values)),
        "endpoint_80pct_coverage": float(np.mean(coverage)),
        "all_round_ensemble_mean": {
            "mae": float(np.mean(np.abs(yr - pr))),
            "r2": float(1.0 - np.sum((yr - pr) ** 2) / round_denom),
        },
        "aggregate_path_properties": {
            key: {
                "observed": prop_mean(observed_properties, key),
                "simulated": prop_mean(simulated_properties, key),
                "absolute_difference": abs(
                    prop_mean(observed_properties, key)
                    - prop_mean(simulated_properties, key)
                ),
            }
            for key in (
                "total_variation", "sign_changes", "endpoint", "low_rail", "high_rail"
            )
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


def summarize_noise_scales(rows):
    output = {}
    for axis in ("risk", "selfreport"):
        subset = [row for row in rows if row["axis"] == axis]
        if not subset:
            continue
        output[axis] = {"n_condition_folds": len(subset)}
        for key in (
            "value_residual_sd", "measurement_residual_sd", "process_sd",
            "identity_process_sd",
        ):
            values = np.asarray([row[key] for row in subset], float)
            output[axis][key] = {
                "mean": float(np.mean(values)),
                "min": float(np.min(values)),
                "max": float(np.max(values)),
            }
    return output


def measurement_noise_diagnostics(records):
    axes = {}
    for axis in ("risk", "selfreport"):
        subset = [row for row in records if row["axis"] == axis]
        ns = [
            int(row["next_value_measurement_n"])
            for row in subset if row.get("next_value_measurement_n")
        ]
        sds = [
            measurement_sd(
                row["value"] + row["drift"],
                row.get("next_value_measurement_n"),
            )
            for row in subset if row.get("next_value_measurement_n")
        ]
        axes[axis] = {
            "n_round_measurements": len(ns),
            "measurement_sample_counts": {
                str(n): int(np.sum(np.asarray(ns) == n)) for n in sorted(set(ns))
            },
            "state_dependent_gaussian_sd_rms": (
                float(np.sqrt(np.mean(np.square(sds)))) if sds else None
            ),
        }

    pairs = []
    source_names = sorted({
        row["source"] for row in records if row["axis"] == "selfreport"
    })
    for source in source_names:
        path = os.path.join(ROOT, "experiments", "em_selfaware_loop", "output", source)
        if not os.path.exists(path):
            continue
        with open(path) as handle:
            data = json.load(handle)
        for dose, baseline in data.get("baselines", {}).items():
            first = baseline.get("battery", {}).get("sr_free_gen", {}).get(
                "sr_freegen"
            )
            repeat = baseline.get("sr_free_gen_repeat", {}).get("sr_freegen")
            if first is None or repeat is None:
                continue
            predicted_difference_sd = np.sqrt(
                measurement_sd(first, 9) ** 2 + measurement_sd(repeat, 9) ** 2
            )
            pairs.append({
                "source": source,
                "dose": dose,
                "first": float(first),
                "repeat": float(repeat),
                "difference": float(repeat - first),
                "predicted_difference_sd": float(predicted_difference_sd),
            })
    differences = np.asarray([row["difference"] for row in pairs], float)
    axes["selfreport"]["baseline_repeat_check"] = {
        "n_pairs": len(pairs),
        "n_nonidentical_pairs": int(np.sum(np.abs(differences) > 1e-12)),
        "note": (
            "Two mixed-run files reuse an identical saved baseline pair; the "
            "all-pair RMS therefore conservatively includes zero differences."
        ),
        "pairs": pairs,
        "difference_rms": (
            float(np.sqrt(np.mean(differences ** 2))) if len(differences) else None
        ),
        "implied_single_read_sd_if_homoskedastic": (
            float(np.sqrt(np.mean(differences ** 2) / 2.0))
            if len(differences) else None
        ),
    }
    return axes


def innovation_correlation_diagnostics(records, transitions, metric, metric_spec):
    output = {}
    labels = ["selector_gap", "generator_mean", "agreement", "value_residual"]
    for axis in ("risk", "selfreport"):
        fits = bakeoff.fit_components(
            records, transitions, axis, metric, "frozen"
        )
        rows = []
        for transition in transitions:
            row, nxt = transition["row"], transition["next"]
            if (
                row["axis"] != axis or row.get("rho") is None
                or nxt.get("rho") is None
            ):
                continue
            rows.append([
                row["gap"] - bakeoff.apply_fit(
                    fits["selector"], row["rho"] * row[metric_spec["whole"]]
                ),
                (nxt["own_mean"] - row["own_mean"])
                - bakeoff.apply_fit(
                    fits["q_update"], row["self_relative_gap"]
                ),
                nxt["rho"] - row["rho"],
                row["drift"] - bakeoff.apply_fit(
                    fits["value_update"], row["pull"]
                ),
            ])
        matrix = np.corrcoef(np.asarray(rows, float), rowvar=False)
        output[axis] = {
            "n_transitions": len(rows),
            "labels": labels,
            "correlation_matrix": matrix.tolist(),
            "note": "descriptive full-data residual correlation audit",
        }
    return output


def feedback_diagnostics(transitions, metric_spec):
    out = {}
    for axis in ("risk", "selfreport"):
        rows = [
            transition for transition in transitions
            if transition["row"]["axis"] == axis
            and transition["row"].get("rho") is not None
            and transition["next"].get("rho") is not None
        ]

        def fit(subset):
            beta = fit_linear(
                [[
                    transition["row"]["rho"],
                    transition["row"]["rho"]
                    * transition["row"][metric_spec["whole"]],
                ] for transition in subset],
                [transition["next"]["rho"] for transition in subset],
            )
            residuals = [
                transition["next"]["rho"]
                - apply_linear(beta, [
                    transition["row"]["rho"],
                    transition["row"]["rho"]
                    * transition["row"][metric_spec["whole"]],
                ])
                for transition in subset
            ]
            return beta, residuals

        beta, residuals = fit(rows)
        conditions = sorted({row["row"]["cond"] for row in rows})
        fold_feedback = [
            fit([row for row in rows if row["row"]["cond"] != condition])[0][2]
            for condition in conditions
        ]
        out[axis] = {
            "n_transitions": len(rows),
            "formula": "rho_next = intercept + rho_ar*rho + feedback*rho*spread",
            "intercept": float(beta[0]),
            "rho_ar": float(beta[1]),
            "feedback": float(beta[2]),
            "residual_sd": float(np.std(residuals)),
            "feedback_leave_condition_out_range": [
                float(min(fold_feedback)), float(max(fold_feedback))
            ],
            "feedback_positive_folds": int(np.sum(np.asarray(fold_feedback) > 0)),
            "n_folds": len(fold_feedback),
        }
    return out


def rho_one_step_cross_validation(transitions, metric_spec):
    output = {}
    for axis in ("risk", "selfreport"):
        rows = [
            transition for transition in transitions
            if transition["row"]["axis"] == axis
            and transition["row"].get("rho") is not None
            and transition["next"].get("rho") is not None
        ]
        predictions = {
            "persistence": ([], []),
            "ar": ([], []),
            "ar_plus_rho_spread": ([], []),
        }
        distribution_predictions = {
            "persistence_gaussian": [],
            "ar_gaussian": [],
        }
        distribution_truth = []
        rng = np.random.default_rng(20260716 + (0 if axis == "risk" else 1))
        for condition in sorted({row["row"]["cond"] for row in rows}):
            train = [row for row in rows if row["row"]["cond"] != condition]
            held = [row for row in rows if row["row"]["cond"] == condition]
            ar_beta = fit_linear(
                [[row["row"]["rho"]] for row in train],
                [row["next"]["rho"] for row in train],
            )
            feedback_beta = fit_linear(
                [[
                    row["row"]["rho"],
                    row["row"]["rho"] * row["row"][metric_spec["whole"]],
                ] for row in train],
                [row["next"]["rho"] for row in train],
            )
            persistence_sd = float(np.std([
                row["next"]["rho"] - row["row"]["rho"] for row in train
            ]))
            ar_sd = float(np.std([
                row["next"]["rho"]
                - apply_linear(ar_beta, [row["row"]["rho"]])
                for row in train
            ]))
            for row in held:
                truth = row["next"]["rho"]
                rho = row["row"]["rho"]
                model_predictions = {
                    "persistence": rho,
                    "ar": apply_linear(ar_beta, [rho]),
                    "ar_plus_rho_spread": apply_linear(
                        feedback_beta,
                        [rho, rho * row["row"][metric_spec["whole"]]],
                    ),
                }
                for name, prediction in model_predictions.items():
                    predictions[name][0].append(truth)
                    predictions[name][1].append(prediction)
                distribution_truth.append(truth)
                distribution_predictions["persistence_gaussian"].append(
                    np.clip(rng.normal(rho, persistence_sd, 1000), -1.0, 1.0)
                )
                distribution_predictions["ar_gaussian"].append(
                    np.clip(rng.normal(
                        model_predictions["ar"], ar_sd, 1000
                    ), -1.0, 1.0)
                )

        def score(actual, predicted):
            y = np.asarray(actual, float)
            p = np.asarray(predicted, float)
            denom = np.sum((y - np.mean(y)) ** 2)
            return {
                "n": len(y),
                "mae": float(np.mean(np.abs(y - p))),
                "rmse": float(np.sqrt(np.mean((y - p) ** 2))),
                "r2": float(1.0 - np.sum((y - p) ** 2) / denom),
            }

        distribution_scores = {}
        for name, samples_by_row in distribution_predictions.items():
            cover = []
            row_crps = []
            for truth, samples in zip(distribution_truth, samples_by_row):
                low, high = np.quantile(samples, [0.1, 0.9])
                cover.append(low <= truth <= high)
                row_crps.append(crps(samples, truth))
            distribution_scores[name] = {
                "n": len(row_crps),
                "crps": float(np.mean(row_crps)),
                "nominal_80pct_coverage": float(np.mean(cover)),
            }

        output[axis] = {
            name: score(actual, predicted)
            for name, (actual, predicted) in predictions.items()
        }
        output[axis]["distribution_scores"] = distribution_scores
    return output


def main():
    with open(INPUT) as handle:
        records = json.load(handle)["records"]
    runs = bakeoff.make_runs(records)
    transitions = bakeoff.make_transitions(records)
    metric = "mean_within_prompt_population_sd"
    metric_spec = bakeoff.METRICS[metric]
    results = {name: [] for name in VARIANTS}
    observed_kept_results = {
        name: [] for name in (
            "identity", "identity_observation_gaussian",
            "identity_process_gaussian",
            "identity_observation_process_gaussian", "identity_gaussian",
            "calibrated_deterministic", "calibrated_gaussian",
        )
    }
    result_tags = []
    result_metadata = []
    noise_scale_folds = {}

    for run_index, (held_key, recs) in enumerate(runs):
        if recs[0].get("rho") is None:
            continue
        condition = recs[0]["cond"]
        axis = recs[0]["axis"]
        train_records = [row for row in records if row["cond"] != condition]
        train_transitions = [
            transition for transition in transitions
            if transition["row"]["cond"] != condition
        ]
        fits = bakeoff.fit_components(
            train_records, train_transitions, axis, metric, "frozen"
        )
        if fits is None or (
            recs[0]["composition"] != "self-only" and fits["mixture"] is None
        ):
            continue
        noise = fit_noise_and_rho(
            train_records, train_transitions, axis, fits, metric_spec
        )
        noise_scale_folds[(axis, condition)] = {
            "axis": axis,
            "condition": condition,
            "value_residual_sd": noise["value_residual_sd"],
            "measurement_residual_sd": noise["measurement_residual_sd"],
            "process_sd": noise["process_sd"],
            "identity_process_sd": noise["identity_process_sd"],
        }
        truth = [recs[0]["value"]] + [
            row["value"] + row["drift"] for row in recs
        ]
        result_tags.append(bakeoff.regime(recs[0]))
        result_metadata.append({
            "axis": axis,
            "regime": bakeoff.regime(recs[0]),
        })
        for variant_index, (name, variant) in enumerate(VARIANTS.items()):
            rng = np.random.default_rng(
                20260715 + 1009 * run_index + 7919 * variant_index
            )
            paths = simulate_paths(
                recs, metric_spec, fits, noise, variant, rng
            )
            results[name].append({"truth": truth, "paths": paths})
        for mode_index, name in enumerate(observed_kept_results):
            rng = np.random.default_rng(
                20261715 + 1009 * run_index + 7919 * mode_index
            )
            paths = simulate_observed_kept_paths(
                recs, fits, noise, name, rng
            )
            observed_kept_results[name].append({
                "truth": truth, "paths": paths
            })

    all_summaries = {name: evaluate_variant(rows) for name, rows in results.items()}

    # Rebuild tagged results without relying on positional filtering.
    tagged = {name: [] for name in VARIANTS}
    for cursor, tag in enumerate(result_tags):
        for name in VARIANTS:
            if tag in (
                "intervention", "self-force", "judge-swap"
            ):
                tagged[name].append(results[name][cursor])
    primary = {name: evaluate_variant(rows) for name, rows in tagged.items()}
    observed_kept_tagged = {name: [] for name in observed_kept_results}
    for cursor, tag in enumerate(result_tags):
        if tag in ("intervention", "self-force", "judge-swap"):
            for name in observed_kept_results:
                observed_kept_tagged[name].append(
                    observed_kept_results[name][cursor]
                )

    subgroup_summaries = {}
    subgroup_filters = {
        "axis:risk": lambda meta: meta["axis"] == "risk",
        "axis:selfreport": lambda meta: meta["axis"] == "selfreport",
    }
    for regime_name in sorted(set(result_tags)):
        subgroup_filters[f"regime:{regime_name}"] = (
            lambda meta, target=regime_name: meta["regime"] == target
        )
    for label, include in subgroup_filters.items():
        indices = [
            index for index, meta in enumerate(result_metadata) if include(meta)
        ]
        subgroup_summaries[label] = {
            name: evaluate_variant([results[name][index] for index in indices])
            for name in VARIANTS
        }

    output = rounded({
        "description": __doc__.strip().split("\n")[0],
        "input": os.path.relpath(INPUT, ROOT),
        "validation": "leave one complete experimental condition out",
        "n_monte_carlo_paths": N_PATHS,
        "measurement_noise_diagnostics": measurement_noise_diagnostics(records),
        "innovation_correlation_diagnostics": innovation_correlation_diagnostics(
            records, transitions, metric, metric_spec
        ),
        "noise_scale_decomposition": {
            "method": (
                "fold-specific total value-update residual variance minus "
                "the battery-sampling variance propagated through the fitted "
                "update; remainder reported as latent process variance"
            ),
            "summary": summarize_noise_scales(list(noise_scale_folds.values())),
            "folds": list(noise_scale_folds.values()),
        },
        "judge_feedback_diagnostics": feedback_diagnostics(
            transitions, metric_spec
        ),
        "judge_agreement_one_step_leave_condition_out": (
            rho_one_step_cross_validation(transitions, metric_spec)
        ),
        "primary_selection_driven_plus_swap": primary,
        "all_modelable_runs": all_summaries,
        "subgroups": subgroup_summaries,
        "observed_kept_set": {
            "description": (
                "conditional after-selection forecast using the actual kept "
                "candidate value mean at every round"
            ),
            "primary_selection_driven_plus_swap": {
                name: evaluate_variant(rows)
                for name, rows in observed_kept_tagged.items()
            },
            "all_modelable_runs": {
                name: evaluate_variant(rows)
                for name, rows in observed_kept_results.items()
            },
        },
    })
    with open(OUTPUT, "w") as handle:
        json.dump(output, handle, indent=1)
    print(f"{len(next(iter(results.values())))} runs -> {OUTPUT}")


if __name__ == "__main__":
    main()
