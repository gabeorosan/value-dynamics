#!/usr/bin/env python3
"""Audit and simplify the selection-response predictor.

The exact accounting law is the Price selection differential.  For forecasting
before the retained set is known, this script tests the parameter-free proxy
gap = judge/value correlation * offered-pool spread.  It also audits two more
elaborate alternatives: a normal top-2-of-6 coefficient and a per-prompt
judge-score-intensity approximation.

Writes experiments/selection_response_predictor.json.
"""
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
UNIFIED = ROOT / "experiments/spread_util_unified.json"
VALUE_BAKEOFF = ROOT / "experiments/value_predictor_bakeoff.json"
ROLLOUT_BAKEOFF = ROOT / "experiments/spread_rollout_bakeoff.json"
OUTPUT = ROOT / "experiments/selection_response_predictor.json"

N_CANDIDATES = 6
N_KEPT = 2
SWAP_FIRST_NEW_ROUND = {
    "press_d1": 2,
    "press_d2": 3,
    "press_d3": 4,
    "press_to_base": 5,
}


def normal_pdf(x):
    return math.exp(-0.5 * x * x) / math.sqrt(2.0 * math.pi)


def normal_cdf(x):
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def expected_normal_order_statistic(n, ascending_rank, steps=100_000):
    """Numerically integrate E[Z_(rank)] for n iid standard normals."""
    if steps % 2:
        steps += 1
    lower, upper = -8.0, 8.0
    width = (upper - lower) / steps
    coefficient = n * math.comb(n - 1, ascending_rank - 1)

    def integrand(x):
        cdf = normal_cdf(x)
        density = (
            coefficient
            * cdf ** (ascending_rank - 1)
            * (1.0 - cdf) ** (n - ascending_rank)
            * normal_pdf(x)
        )
        return x * density

    total = integrand(lower) + integrand(upper)
    total += 4.0 * sum(
        integrand(lower + width * index) for index in range(1, steps, 2)
    )
    total += 2.0 * sum(
        integrand(lower + width * index) for index in range(2, steps, 2)
    )
    return total * width / 3.0


def normal_scale_audit(draws=1_000_000, seed=16072026):
    """Show why population-normal intensity is not on the project's SD scale."""
    order_means = [
        expected_normal_order_statistic(N_CANDIDATES, rank)
        for rank in range(N_CANDIDATES - N_KEPT + 1, N_CANDIDATES + 1)
    ]
    population_sd_intensity = float(np.mean(order_means))
    rng = np.random.default_rng(seed)
    samples = rng.standard_normal((draws, N_CANDIDATES))
    gaps = np.mean(np.partition(samples, -N_KEPT, axis=1)[:, -N_KEPT:], axis=1)
    sample_sds = np.std(samples, axis=1, ddof=0)
    return {
        "expected_top_order_statistics": order_means,
        "intensity_in_units_of_underlying_normal_sd": population_sd_intensity,
        "project_uses_realized_six_sample_population_sd": True,
        "monte_carlo_draws": draws,
        "monte_carlo_seed": seed,
        "mean_selected_gap": float(np.mean(gaps)),
        "mean_realized_population_sd": float(np.mean(sample_sds)),
        "ratio_of_means_on_project_scale": float(
            np.mean(gaps) / np.mean(sample_sds)
        ),
        "conclusion": (
            "0.9545 is not a design-derived coefficient for the project's "
            "realized finite-pool SD; its match to the empirical 0.958 slope "
            "is a scale-mismatched coincidence."
        ),
    }


def metrics(actual, predicted):
    actual = np.asarray(actual, float)
    predicted = np.asarray(predicted, float)
    denominator = float(np.sum((actual - np.mean(actual)) ** 2))
    return {
        "n": int(len(actual)),
        "mae": float(np.mean(np.abs(actual - predicted))),
        "rmse": float(np.sqrt(np.mean((actual - predicted) ** 2))),
        "r2": (
            float(1.0 - np.sum((actual - predicted) ** 2) / denominator)
            if denominator > 0 else None
        ),
    }


def direction_metrics(rows):
    moved = [row for row in rows if abs(row["actual"] - row["start"]) >= 0.15]
    hits = [
        row for row in moved
        if ((row["predicted"] - row["start"])
            * (row["actual"] - row["start"]) > 0
            and abs(row["predicted"] - row["start"]) >= 0.05)
    ]
    return {
        "n_moved": len(moved),
        "n_hits": len(hits),
        "hit_rate": len(hits) / len(moved) if moved else None,
    }


def metric_rows(rows, actual_key="actual", predicted_key="predicted"):
    return metrics(
        [row[actual_key] for row in rows],
        [row[predicted_key] for row in rows],
    )


def run_key(row):
    return row["cond"], row["seed"], row["source"]


def regime(row):
    if row["judge"] == "schedule":
        return "judge_swap"
    if row["composition"] != "self-only":
        return "selection_driven"
    if (row["judge"] in ("score oracle", "cautious copy")
            or (row["judge"] == "self" and row["format"] == "candid-prompt")):
        return "selection_driven"
    return "self_weak"


def usable_agreement(row):
    if row.get("rho") is not None:
        return float(row["rho"])
    if abs(row["spread"]) < 1e-12:
        return 0.0
    return None


def boundary_gap(first, mode):
    if mode == "unit_agreement_spread":
        agreement = usable_agreement(first)
        return None if agreement is None else agreement * float(first["spread"])
    if mode == "observed_first_gap":
        return float(first["gap"])
    if mode == "judge_score_intensity":
        value = first.get("selection_response_predicted_gap")
        return float(value) if value is not None else None
    raise ValueError(mode)


def simulate_segment(rows, mode):
    """Elite-mean update with one scalar boundary gap held fixed."""
    first = rows[0]
    selector_gap = boundary_gap(first, mode)
    if selector_gap is None:
        return None
    own_mean = float(first["own_mean"])
    mixed = first["composition"] != "self-only"
    supplier_mean = float(first["cogen_mean"]) if mixed else None
    supplier_share = float(first.get("pool_cogen_fraction") or 0.0)
    trajectory = []
    for _row in rows:
        pool_mean = (
            (1.0 - supplier_share) * own_mean + supplier_share * supplier_mean
            if mixed else own_mean
        )
        predicted_kept_mean = float(np.clip(
            pool_mean + selector_gap, 0.0, 1.0
        ))
        own_mean = predicted_kept_mean
        trajectory.append(predicted_kept_mean)
    return trajectory


def endpoint_rows(records, mode):
    grouped = defaultdict(list)
    for row in records:
        grouped[run_key(row)].append(row)
    primary, swaps, diagnostics = [], [], []
    for key, rows in grouped.items():
        rows = sorted(rows, key=lambda row: row["round"])
        if len(rows) < 2:
            continue
        first = rows[0]
        category = regime(first)
        if category == "judge_swap":
            first_new_round = SWAP_FIRST_NEW_ROUND[first["cond"]]
            segment = [row for row in rows if row["round"] >= first_new_round]
        else:
            segment = rows
        trajectory = simulate_segment(segment, mode)
        if trajectory is None:
            continue
        actual = float(rows[-1]["value"] + rows[-1]["drift"])
        result = {
            "run_key": "|".join(map(str, key)),
            "regime": category,
            "n_predicted_rounds": len(segment),
            "start": float(segment[0]["value"]),
            "actual": actual,
            "predicted": trajectory[-1],
            "trajectory": trajectory,
        }
        diagnostics.append(result)
        if category == "selection_driven":
            primary.append(result)
        elif category == "judge_swap":
            swaps.append(result)
    return primary, swaps, diagnostics


def rounded(value):
    if isinstance(value, dict):
        return {key: rounded(item) for key, item in value.items()}
    if isinstance(value, list):
        return [rounded(item) for item in value]
    if isinstance(value, (float, np.floating)):
        return round(float(value), 6)
    return value


def sliced_metrics(rows, predictor, actual):
    definitions = {
        "all": lambda row: True,
        "risk": lambda row: row["axis"] == "risk",
        "selfreport": lambda row: row["axis"] == "selfreport",
        "self_only": lambda row: row["composition"] == "self-only",
        "mixed": lambda row: row["composition"] != "self-only",
        "OLMo": lambda row: row["organism"] == "OLMo",
        "Qwen": lambda row: row["organism"] == "Qwen",
    }
    output = {}
    for name, include in definitions.items():
        selected = [row for row in rows if include(row)]
        if selected:
            output[name] = metrics(
                [actual(row) for row in selected],
                [predictor(row) for row in selected],
            )
    return output


def endpoint_summary(records, mode, current_selection_keys):
    primary, swaps, diagnostics = endpoint_rows(records, mode)
    matched_primary = [
        row for row in primary if row["run_key"] in current_selection_keys
    ]
    combined = matched_primary + swaps
    return {
        "selection_driven_all_scoreable": metric_rows(primary),
        "selection_driven_matched_to_current": metric_rows(matched_primary),
        "judge_swap_refreshed": metric_rows(swaps),
        "combined_matched_to_current": metric_rows(combined),
        "direction_combined": direction_metrics(combined),
        "per_run": diagnostics,
    }


def main():
    unified = json.loads(UNIFIED.read_text())
    value_bakeoff = json.loads(VALUE_BAKEOFF.read_text())
    rollout_bakeoff = json.loads(ROLLOUT_BAKEOFF.read_text())
    records = unified["records"]
    rho_records = [row for row in records if row.get("rho") is not None]
    score_intensity_records = [
        row for row in rho_records
        if row.get("selection_response_predicted_gap") is not None
    ]

    unit_gap = lambda row: row["rho"] * row["spread"]
    unit_delta = lambda row: float(np.clip(
        row["pool_mean"] + unit_gap(row), 0.0, 1.0
    ) - row["value"])
    score_gap = lambda row: row["selection_response_predicted_gap"]
    score_delta = lambda row: float(np.clip(
        row["pool_mean"] + score_gap(row), 0.0, 1.0
    ) - row["value"])

    current_one_round = value_bakeoff["one_round"]["leave_one_condition_out"]
    current_endpoint = rollout_bakeoff[
        "validations"]["leave_one_condition_out"]["frozen"][
            "mean_within_prompt_population_sd"]["aggregates"]
    current_endpoint_runs = rollout_bakeoff[
        "validations"]["leave_one_condition_out"]["frozen"][
            "mean_within_prompt_population_sd"]["per_run"]
    current_swap = rollout_bakeoff[
        "judge_swap_refresh"]["leave_one_condition_out"]["mean_sd_frozen"]
    current_selection_keys = {
        row["run_key"] for row in current_endpoint_runs
        if row["regime"] in ("intervention", "self-force")
    }

    endpoint_unit = endpoint_summary(
        records, "unit_agreement_spread", current_selection_keys
    )
    endpoint_observed_gap = endpoint_summary(
        records, "observed_first_gap", current_selection_keys
    )
    endpoint_score_intensity = endpoint_summary(
        records, "judge_score_intensity", current_selection_keys
    )

    candidate_counts = Counter(
        (row["candidate_count_min"], row["candidate_count_max"])
        for row in records
    )
    output = rounded({
        "description": __doc__.strip().split("\n")[0],
        "recommended_model": {
            "exact_after_selection": (
                "gap = kept_mean - pool_mean = Cov(value, kept_indicator) / "
                "mean(kept_indicator); next_value = kept_mean"
            ),
            "parameter_free_before_selection_proxy": (
                "predicted_gap = judge_value_agreement * offered_pool_spread"
            ),
            "endpoint": (
                "iterate pool_supply_update + frozen boundary predicted_gap; "
                "remeasure at judge, judging-format, or pool-policy changes"
            ),
            "interpretation": (
                "spread times realized value-axis selection intensity is exact; "
                "judge/value correlation is a compact pre-selection proxy for "
                "that intensity"
            ),
        },
        "scale_audit": normal_scale_audit(),
        "candidate_count_min_max_round_counts": {
            f"{minimum}-{maximum}": count
            for (minimum, maximum), count in sorted(candidate_counts.items())
        },
        "selector_gap": {
            "unit_agreement_spread_proxy": sliced_metrics(
                rho_records, unit_gap, lambda row: row["gap"]
            ),
            "realized_judge_score_intensity_diagnostic": sliced_metrics(
                score_intensity_records, score_gap, lambda row: row["gap"]
            ),
            "fitted_full_data_equation_description_only": value_bakeoff[
                "one_round"]["full_data_equations_for_description_only"][
                    "selector_gap"],
        },
        "one_round_before_selection": {
            "unit_agreement_spread_proxy": sliced_metrics(
                rho_records, unit_delta, lambda row: row["drift"]
            ),
            "realized_judge_score_intensity_diagnostic": sliced_metrics(
                score_intensity_records, score_delta, lambda row: row["drift"]
            ),
            "current_fitted_LOCO": current_one_round[
                "factorized_preselection_pull"],
            "observed_kept_mean_LOCO": current_one_round[
                "rho_subset_kept_target_identity"],
        },
        "endpoint_with_boundary_refresh": {
            "recommended_unit_agreement_spread": endpoint_unit,
            "observed_first_gap_diagnostic": endpoint_observed_gap,
            "realized_judge_score_intensity_diagnostic": endpoint_score_intensity,
            "current_fitted_frozen_sd_LOCO": {
                "selection_driven": current_endpoint[
                    "selection_driven"]["behavioral_value_endpoint"],
                "judge_swap_refreshed": current_swap[
                    "aggregate"]["endpoint"]["refreshed_at_swap"],
                "combined_mae": value_bakeoff[
                    "endpoint_with_boundary_refresh"]["mean_sd_frozen"][
                        "selection_driven_plus_swap_endpoint_mae"],
            },
        },
        "forecast_time_distinction": {
            "after_pool_and_retained_set": (
                "use the exact kept mean; agreement-spread is unnecessary"
            ),
            "after_pool_and_logged_judge_scores_but_before_retained_indices": (
                "if logged scores fully specify selection, compute the kept set "
                "directly; in this corpus they sometimes do not"
            ),
            "before_judging_with_boundary_measurements": (
                "use rho * spread as the low-dimensional conditional-mean proxy"
            ),
        },
        "literature_connections": {
            "Price": (
                "kept-minus-pool is exactly a selection differential"
            ),
            "quantitative_selection": (
                "selection intensity, criterion accuracy, and target spread are "
                "distinct factors; 2-of-6 alone does not determine their product"
            ),
            "cross_entropy_method": (
                "generate, rank, retain elites, and refit is an elite-distribution "
                "update; variance shrinkage and injection are native predictions"
            ),
            "reward_overoptimization": (
                "judge/value agreement is local to the candidate distribution and "
                "must be remeasured after distribution or judge changes"
            ),
        },
    })
    OUTPUT.write_text(json.dumps(output, indent=2) + "\n")
    print(f"wrote {OUTPUT}")
    print(
        "one-round unit MAE",
        output["one_round_before_selection"][
            "unit_agreement_spread_proxy"]["all"]["mae"],
    )
    print(
        "combined endpoint unit MAE",
        output["endpoint_with_boundary_refresh"][
            "recommended_unit_agreement_spread"][
                "combined_matched_to_current"]["mae"],
    )


if __name__ == "__main__":
    main()
