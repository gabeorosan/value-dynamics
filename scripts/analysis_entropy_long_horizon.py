#!/usr/bin/env python3
"""Test whether entropy forecasts later target-axis supply over multiple rounds.

This is the higher-level complement to analysis_entropy_predictive.py. The
primary comparison asks whether checkpoint entropy improves prediction of
future target-axis candidate spread after conditioning on current spread and
experimental condition. It reports 1/2/3-round horizons, early-to-terminal
outcomes, a K2-to-release temporal holdout, and temporal ordering of broad
entropy collapse versus target-axis exhaustion.

All analyses are post-hoc and exploratory. The frozen M2 drift predictor is not
changed.
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "experiments" / "entropy_long_horizon_analysis.json"
sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_rollout_manifest import load_winning_records  # noqa: E402


POOL_FIELD = {"K1": "pool_risk", "K2": "pool_risk", "K3": "pool_candor", "K2_release": "pool_risk"}
CAND_FIELD = {"K1": "cand_risk", "K2": "cand_risk", "K3": "cand_candor", "K2_release": "cand_risk"}
K2_CONDITIONS = {"evolving_self", "frozen_base", "frozen_cons_r0", "random_select"}


def entropy(grid, battery):
    return float(battery["entropy"]["mean"] if grid != "K3" else battery["entropy_mean"])


def pool_spread(raw, pool_field, cand_field):
    pool = float(np.mean([item[pool_field] for item in raw if item.get(pool_field) is not None]))
    spread = float(np.mean([
        np.std(item[cand_field])
        for item in raw
        if item.get(cand_field) and all(v is not None for v in item[cand_field])
    ]))
    return pool, spread


def trajectories(grid):
    out = []
    pf, cf = POOL_FIELD[grid], CAND_FIELD[grid]
    for _grid, manifest_condition, seed, rec in load_winning_records(grid=grid):
        if rec.get("measure_only"):
            continue
        raws, batteries = rec.get("rounds_raw", []), rec.get("battery", [])
        if not raws or len(batteries) < len(raws):
            continue
        ps = [pool_spread(raw, pf, cf) for raw in raws]
        entropies = [entropy(grid, batteries[t]) for t in range(len(raws))]
        if grid == "K2_release":
            judges = rec.get("judge_used", [])
            conditions = [judges[t] if t < len(judges) else None for t in range(len(raws))]
        else:
            conditions = [manifest_condition] * len(raws)
        out.append({
            "grid": grid,
            "schedule": manifest_condition,
            "seed": int(seed),
            "conditions": conditions,
            "pools": [x[0] for x in ps],
            "spreads": [x[1] for x in ps],
            "entropies": entropies,
        })
    return out


def horizon_rows(trajs, horizon, stable_condition=False, require_t_after_zero=False):
    rows = []
    for tr in trajs:
        n = len(tr["spreads"])
        for t in range(n - horizon):
            if require_t_after_zero and t == 0:
                continue
            condition = tr["conditions"][t]
            if condition is None:
                continue
            if stable_condition and any(tr["conditions"][j] != condition for j in range(t, t + horizon)):
                continue
            if tr["grid"] == "K2_release" and condition not in K2_CONDITIONS:
                continue
            h0 = tr["entropies"][0]
            row = {
                "condition": condition,
                "schedule": tr["schedule"],
                "seed": tr["seed"],
                "t": t,
                "current_spread": tr["spreads"][t],
                "current_pool": tr["pools"][t],
                "entropy": tr["entropies"][t],
                "entropy_fraction_start": tr["entropies"][t] / h0 if h0 else 0.0,
                "entropy_change_start": tr["entropies"][t] - h0,
                "future_spread": tr["spreads"][t + horizon],
                "future_spread_change": tr["spreads"][t + horizon] - tr["spreads"][t],
            }
            if all(np.isfinite(v) for k, v in row.items() if k not in ("condition", "schedule")):
                rows.append(row)
    return rows


def early_terminal_rows(trajs, t=1):
    rows = []
    for tr in trajs:
        if len(tr["spreads"]) <= t + 1:
            continue
        condition = tr["conditions"][t]
        if condition is None:
            continue
        future_spreads = tr["spreads"][t + 1:]
        future_pools = tr["pools"][t:]
        row = {
            "condition": condition,
            "schedule": tr["schedule"],
            "seed": tr["seed"],
            "t": t,
            "current_spread": tr["spreads"][t],
            "current_pool": tr["pools"][t],
            "entropy": tr["entropies"][t],
            "entropy_change_start": tr["entropies"][t] - tr["entropies"][0],
            "terminal_spread": tr["spreads"][-1],
            "future_mean_spread": float(np.mean(future_spreads)),
            "future_min_spread": float(np.min(future_spreads)),
            "remaining_abs_movement": float(np.sum(np.abs(np.diff(future_pools)))),
            "future_exhausted": float(np.min(future_spreads) <= 0.05),
        }
        if all(np.isfinite(v) for k, v in row.items() if k not in ("condition", "schedule")):
            rows.append(row)
    return rows


def design(train, test, features, conditions):
    ci = {c: i for i, c in enumerate(conditions)}
    means = {f: float(np.mean([r[f] for r in train])) for f in features}
    scales = {f: float(np.std([r[f] for r in train])) or 1.0 for f in features}

    def matrix(rows):
        out = []
        for row in rows:
            x = [0.0] * len(conditions)
            x[ci[row["condition"]]] = 1.0
            x.extend((row[f] - means[f]) / scales[f] for f in features)
            out.append(x)
        return np.asarray(out, dtype=float)

    return matrix(train), matrix(test)


def fit_predict(train, test, target, features, conditions):
    xtr, xte = design(train, test, features, conditions)
    beta, *_ = np.linalg.lstsq(xtr, np.asarray([r[target] for r in train]), rcond=None)
    return [float(v) for v in xte @ beta]


def standardized_feature_coefficients(rows, target, features, conditions):
    if not features:
        return {}
    x, _ = design(rows, rows, features, conditions)
    beta, *_ = np.linalg.lstsq(x, np.asarray([r[target] for r in rows]), rcond=None)
    return {feature: float(beta[len(conditions) + i]) for i, feature in enumerate(features)}


def design_diagnostics(rows, features, conditions):
    """Flag fits whose training design cannot identify all coefficients."""
    x, _ = design(rows, rows, features, conditions)
    rank = int(np.linalg.matrix_rank(x))
    n_parameters = int(x.shape[1])
    condition_number = float(np.linalg.cond(x))
    return {
        "n_train": len(rows),
        "n_parameters": n_parameters,
        "rank": rank,
        "condition_number": condition_number,
        "stable": bool(rank == n_parameters and np.isfinite(condition_number) and condition_number < 1e8),
    }


def rmse(y, p):
    return float(np.sqrt(np.mean((np.asarray(y) - np.asarray(p)) ** 2)))


def grouped_score(rows, target, models, group_fields=("seed",)):
    conditions = sorted({r["condition"] for r in rows})
    def group_value(row):
        values = tuple(row[field] for field in group_fields)
        return values[0] if len(values) == 1 else values

    groups = sorted({group_value(r) for r in rows})
    predictions = {name: {} for name in models}
    diagnostics = {}
    fold_coefficients = {}
    for group in groups:
        train = [r for r in rows if group_value(r) != group]
        test = [r for r in rows if group_value(r) == group]
        label = "|".join(str(value) for value in group) if isinstance(group, tuple) else str(group)
        diagnostics[label] = {}
        fold_coefficients[label] = {}
        for name, features in models.items():
            diagnostics[label][name] = design_diagnostics(train, features, conditions)
            fold_coefficients[label][name] = standardized_feature_coefficients(
                train, target, features, conditions
            )
            pred = fit_predict(train, test, target, features, conditions)
            for row, value in zip(test, pred):
                predictions[name][(row["condition"], row["seed"], row["t"], row.get("schedule"))] = value
    actual = [r[target] for r in rows]
    aligned = {
        name: [predictions[name][(r["condition"], r["seed"], r["t"], r.get("schedule"))] for r in rows]
        for name in models
    }
    fold_rmse = {}
    for group in groups:
        idx = [i for i, row in enumerate(rows) if group_value(row) == group]
        label = "|".join(str(value) for value in group) if isinstance(group, tuple) else str(group)
        fold_rmse[label] = {
            name: rmse([actual[i] for i in idx], [aligned[name][i] for i in idx])
            for name in models
        }
    return {
        "n": len(rows),
        "n_groups": len(groups),
        "group_fields": list(group_fields),
        "target_event_count": int(sum(actual)) if target == "future_exhausted" else None,
        "rmse": {name: rmse(actual, values) for name, values in aligned.items()},
        "fold_rmse": fold_rmse,
        "fit_diagnostics": diagnostics,
        "full_fit_standardized_feature_coefficients": {
            name: standardized_feature_coefficients(rows, target, features, conditions)
            for name, features in models.items()
        },
        "fold_standardized_feature_coefficients": fold_coefficients,
        "unstable_models": [
            name for name in models
            if any(not fold[name]["stable"] for fold in diagnostics.values())
        ],
    }


def temporal_score(train, test, target, models):
    conditions = sorted({r["condition"] for r in train})
    actual = [r[target] for r in test]
    return {
        "n": len(test),
        "n_rollouts": len({(r["schedule"], r["seed"]) for r in test}),
        "rmse": {
            name: rmse(actual, fit_predict(train, test, target, features, conditions))
            for name, features in models.items()
        },
        "fit_diagnostics": {
            name: design_diagnostics(train, features, conditions)
            for name, features in models.items()
        },
    }


def collapse_order(trajs):
    rows = []
    counts = {"entropy_before_spread": 0, "same_round": 0, "spread_before_entropy": 0,
              "spread_only": 0, "entropy_only": 0, "neither": 0}
    for tr in trajs:
        ent_threshold = 0.25 * tr["entropies"][0]
        ent_round = next((i for i, value in enumerate(tr["entropies"]) if value <= ent_threshold), None)
        spread_round = next((i for i, value in enumerate(tr["spreads"]) if value <= 0.05), None)
        if ent_round is None and spread_round is None:
            label = "neither"
        elif ent_round is None:
            label = "spread_only"
        elif spread_round is None:
            label = "entropy_only"
        elif ent_round < spread_round:
            label = "entropy_before_spread"
        elif ent_round > spread_round:
            label = "spread_before_entropy"
        else:
            label = "same_round"
        counts[label] += 1
        rows.append({
            "condition": tr["schedule"], "seed": tr["seed"],
            "entropy_collapse_round": ent_round, "spread_exhaustion_round": spread_round,
            "ordering": label,
        })
    return {
        "definition": "entropy <=25% of round-0; target-axis spread <=0.05",
        "threshold_status": "post-hoc descriptive thresholds, not preregistered",
        "counts": counts,
        "rows": rows,
    }


def pct(new, old):
    return 100.0 * (new / old - 1.0)


def main():
    base_models = {
        "C": [],
        "S": ["current_spread"],
        "SH": ["current_spread", "entropy"],
        "SP": ["current_spread", "current_pool"],
        "SPH": ["current_spread", "current_pool", "entropy"],
    }
    delta_models = {
        "S": ["current_spread"],
        "SD": ["current_spread", "entropy_change_start"],
        "SF": ["current_spread", "entropy_fraction_start"],
    }
    grids = {grid: trajectories(grid) for grid in ("K1", "K2", "K3")}
    release = trajectories("K2_release")
    results = {}
    for grid, trajs in grids.items():
        horizons = {}
        for horizon in (1, 2, 3):
            rows = horizon_rows(trajs, horizon)
            if rows:
                block = grouped_score(rows, "future_spread", base_models)
                block["origin_rounds"] = sorted({row["t"] for row in rows})
                block["interpretation_warning"] = (
                    "single origin round only; treat as an early-to-terminal association, not a pooled horizon effect"
                    if len(block["origin_rounds"]) == 1 else None
                )
                delta_rows = horizon_rows(trajs, horizon, require_t_after_zero=True)
                block["entropy_change_models"] = grouped_score(delta_rows, "future_spread", delta_models) if delta_rows else None
                block["SH_vs_S_percent"] = pct(block["rmse"]["SH"], block["rmse"]["S"])
                block["SPH_vs_SP_percent"] = pct(block["rmse"]["SPH"], block["rmse"]["SP"])
                horizons[str(horizon)] = block
        early = early_terminal_rows(trajs, t=1)
        early_models = {
            "C": [], "S": ["current_spread"], "H": ["entropy"],
            "SH": ["current_spread", "entropy"],
            "SD": ["current_spread", "entropy_change_start"],
        }
        early_targets = {}
        for target in (
            "terminal_spread", "future_mean_spread", "future_min_spread",
            "remaining_abs_movement", "future_exhausted",
        ):
            block = grouped_score(early, target, early_models)
            block["SH_vs_S_percent"] = pct(block["rmse"]["SH"], block["rmse"]["S"]) if block["rmse"]["S"] else None
            block["SD_vs_S_percent"] = pct(block["rmse"]["SD"], block["rmse"]["S"]) if block["rmse"]["S"] else None
            block["SH_better_fold_count"] = sum(
                fold["SH"] < fold["S"] for fold in block["fold_rmse"].values()
            )
            block["SD_better_fold_count"] = sum(
                fold["SD"] < fold["S"] for fold in block["fold_rmse"].values()
            )
            early_targets[target] = block
        results[grid] = {
            "n_trajectories": len(trajs),
            "horizon_future_spread": horizons,
            "round1_to_terminal": early_targets,
            "collapse_ordering": collapse_order(trajs),
        }

    temporal = {}
    temporal_delta = {}
    release_within = {}
    for horizon in (1, 2, 3):
        train = horizon_rows(grids["K2"], horizon)
        test = horizon_rows(release, horizon, stable_condition=True)
        temporal[str(horizon)] = {
            **temporal_score(train, test, "future_spread", base_models),
            "SH_vs_S_percent": None,
            "SPH_vs_SP_percent": None,
            "stable_judge_requirement": "judge_used remains unchanged through the prediction horizon",
        }
        scores = temporal[str(horizon)]["rmse"]
        temporal[str(horizon)]["SH_vs_S_percent"] = pct(scores["SH"], scores["S"])
        temporal[str(horizon)]["SPH_vs_SP_percent"] = pct(scores["SPH"], scores["SP"])

        release_block = grouped_score(
            test, "future_spread", base_models, group_fields=("schedule", "seed")
        )
        release_block["SH_vs_S_percent"] = pct(
            release_block["rmse"]["SH"], release_block["rmse"]["S"]
        )
        release_block["SH_better_fold_count"] = sum(
            fold["SH"] < fold["S"] for fold in release_block["fold_rmse"].values()
        )
        release_within[str(horizon)] = release_block

        if horizon < 3:
            delta_train = horizon_rows(grids["K2"], horizon, require_t_after_zero=True)
            delta_test = horizon_rows(
                release, horizon, stable_condition=True, require_t_after_zero=True
            )
            temporal_delta[str(horizon)] = {
                **temporal_score(delta_train, delta_test, "future_spread", delta_models),
                "SD_vs_S_percent": None,
                "SF_vs_S_percent": None,
                "stable_judge_requirement": "judge_used remains unchanged through the prediction horizon",
                "post_update_states_only": True,
            }
            delta_scores = temporal_delta[str(horizon)]["rmse"]
            temporal_delta[str(horizon)]["SD_vs_S_percent"] = pct(
                delta_scores["SD"], delta_scores["S"]
            )
            temporal_delta[str(horizon)]["SF_vs_S_percent"] = pct(
                delta_scores["SF"], delta_scores["S"]
            )

    manifest_path = ROOT / "experiments" / "rollout_manifest.json"
    manifest = json.loads(manifest_path.read_text())
    output = {
        "schema_version": 2,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "post-hoc exploratory; tests multi-round supply hypothesis; frozen M2 unchanged",
        "provenance": {
            "manifest": str(manifest_path.relative_to(ROOT)),
            "manifest_sha256": hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
            "manifest_dedup_rule": manifest.get("dedup_rule"),
            "manifest_source_sha256": manifest.get("source_sha256"),
        },
        "definitions": {
            "H": "checkpoint token entropy",
            "S": "current mean within-item target-axis candidate spread",
            "future_spread": "S at t+h",
            "primary_increment": "SH versus S under leave-one-seed-out validation",
            "early_terminal": "post-first-update state at t=1 predicts later/terminal supply",
        },
        "grids": results,
        "k2_to_release_stable_judge_temporal_holdout": temporal,
        "k2_entropy_change_to_release_temporal_holdout": temporal_delta,
        "release_leave_one_trajectory_out": release_within,
        "release_collapse_ordering": collapse_order(release),
    }
    tmp = OUTPUT.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(output, indent=2) + "\n")
    os.replace(tmp, OUTPUT)
    print(f"wrote {OUTPUT.relative_to(ROOT)}")
    for grid, block in results.items():
        changes = ", ".join(
            f"h{h} {values['SH_vs_S_percent']:+.1f}%"
            for h, values in block["horizon_future_spread"].items()
        )
        print(f"{grid} entropy added to current spread: {changes}")
    print("K2->release stable-judge: " + ", ".join(
        f"h{h} {values['SH_vs_S_percent']:+.1f}%" for h, values in temporal.items()
    ))


if __name__ == "__main__":
    main()
