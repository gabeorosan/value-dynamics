#!/usr/bin/env python3
"""Exploratory grouped-CV test of entropy in the transition model.

This does not alter or refit the preregistered/frozen M2 predictor. It asks the
missing post-hoc questions on the canonical K1/K2/K3 rollout manifest:

1. Does checkpoint entropy improve signed next-round drift prediction beyond
   condition and the realized kept-minus-pool gap?
2. Does entropy predict movement magnitude, where a directionless health
   variable has a more plausible role?
3. Does entropy predict next-round target-axis spread, the proposed upstream
   path into the intervention window?

Validation is leave-one-seed-out (primary) and leave-one-rollout-out. Models
are fit separately by grid because K3 uses different entropy prompts and a
different selected axis.
"""

from __future__ import annotations

import json
import hashlib
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "experiments" / "entropy_predictive_analysis.json"
sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_rollout_manifest import load_winning_records  # noqa: E402


POOL_FIELD = {"K1": "pool_risk", "K2": "pool_risk", "K3": "pool_candor"}
CAND_FIELD = {"K1": "cand_risk", "K2": "cand_risk", "K3": "cand_candor"}


def checkpoint_entropy(grid: str, battery: dict) -> float:
    if grid in ("K1", "K2"):
        return float(battery["entropy"]["mean"])
    return float(battery["entropy_mean"])


def pool_and_spread(raw: list[dict], pool_field: str, cand_field: str) -> tuple[float, float]:
    pools = [float(item[pool_field]) for item in raw if item.get(pool_field) is not None]
    spreads = [
        float(np.std(item[cand_field]))
        for item in raw
        if item.get(cand_field) and all(v is not None for v in item[cand_field])
    ]
    return float(np.mean(pools)), float(np.mean(spreads))


def build_rows(grid: str) -> list[dict]:
    rows = []
    pf, cf = POOL_FIELD[grid], CAND_FIELD[grid]
    for _grid, condition, seed, rec in load_winning_records(grid=grid):
        if rec.get("measure_only"):
            continue
        raws = rec.get("rounds_raw", [])
        batteries = rec.get("battery", [])
        pools_spreads = [pool_and_spread(raw, pf, cf) for raw in raws]
        gaps = [
            float(np.mean([item["gap_arm"] for item in raw if item.get("gap_arm") is not None]))
            for raw in raws
        ]
        for t in range(len(raws) - 1):
            pool, spread = pools_spreads[t]
            next_pool, next_spread = pools_spreads[t + 1]
            row = {
                "condition": condition,
                "seed": int(seed),
                "t": int(t),
                "gap": gaps[t],
                "abs_gap": abs(gaps[t]),
                "pool": pool,
                "spread": spread,
                "entropy": checkpoint_entropy(grid, batteries[t]),
                "drift": next_pool - pool,
                "abs_drift": abs(next_pool - pool),
                "next_spread": next_spread,
            }
            if all(np.isfinite(v) for k, v in row.items() if k not in ("condition",)):
                rows.append(row)
    return rows


def build_release_rows() -> list[dict]:
    """K2-release transitions labeled by the judge used for that update."""
    rows = []
    allowed = {"evolving_self", "frozen_base", "frozen_cons_r0", "random_select"}
    for _grid, schedule, seed, rec in load_winning_records(grid="K2_release"):
        raws = rec.get("rounds_raw", [])
        batteries = rec.get("battery", [])
        judges = rec.get("judge_used", [])
        pools_spreads = [pool_and_spread(raw, "pool_risk", "cand_risk") for raw in raws]
        gaps = [
            float(np.mean([item["gap_arm"] for item in raw if item.get("gap_arm") is not None]))
            for raw in raws
        ]
        for t in range(len(raws) - 1):
            condition = judges[t] if t < len(judges) else None
            if condition not in allowed:
                continue
            pool, spread = pools_spreads[t]
            next_pool, next_spread = pools_spreads[t + 1]
            row = {
                "condition": condition,
                "schedule": schedule,
                "seed": int(seed),
                "t": int(t),
                "gap": gaps[t],
                "abs_gap": abs(gaps[t]),
                "pool": pool,
                "spread": spread,
                "entropy": checkpoint_entropy("K2", batteries[t]),
                "drift": next_pool - pool,
                "abs_drift": abs(next_pool - pool),
                "next_spread": next_spread,
            }
            if all(np.isfinite(v) for k, v in row.items() if k not in ("condition", "schedule")):
                rows.append(row)
    return rows


def design(train: list[dict], test: list[dict], features: list[str], conditions: list[str]):
    """Condition intercepts plus fold-standardized numeric features."""
    ci = {condition: i for i, condition in enumerate(conditions)}
    means = {feature: float(np.mean([row[feature] for row in train])) for feature in features}
    scales = {
        feature: float(np.std([row[feature] for row in train])) or 1.0
        for feature in features
    }

    def matrix(rows):
        out = []
        for row in rows:
            x = [0.0] * len(conditions)
            x[ci[row["condition"]]] = 1.0
            x.extend((row[feature] - means[feature]) / scales[feature] for feature in features)
            out.append(x)
        return np.asarray(out, dtype=float)

    return matrix(train), matrix(test)


def grouped_predictions(rows, target, features, group_key, conditions):
    predictions = {}
    for group in sorted({group_key(row) for row in rows}, key=str):
        train = [row for row in rows if group_key(row) != group]
        test = [row for row in rows if group_key(row) == group]
        x_train, x_test = design(train, test, features, conditions)
        y_train = np.asarray([row[target] for row in train], dtype=float)
        beta, *_ = np.linalg.lstsq(x_train, y_train, rcond=None)
        for row, prediction in zip(test, x_test @ beta):
            predictions[(row["condition"], row["seed"], row["t"])] = float(prediction)
    return [predictions[(row["condition"], row["seed"], row["t"])] for row in rows]


def temporal_predictions(train, test, target, features, conditions):
    x_train, x_test = design(train, test, features, conditions)
    y_train = np.asarray([row[target] for row in train], dtype=float)
    beta, *_ = np.linalg.lstsq(x_train, y_train, rcond=None)
    return [float(value) for value in x_test @ beta]


def rmse(actual, predicted):
    actual, predicted = np.asarray(actual), np.asarray(predicted)
    return float(np.sqrt(np.mean((actual - predicted) ** 2)))


def score_family(rows, target, models):
    conditions = sorted({row["condition"] for row in rows})
    actual = [row[target] for row in rows]
    output = {}
    for scheme, group_key in (
        ("LOSO", lambda row: row["seed"]),
        ("LORO", lambda row: (row["condition"], row["seed"])),
    ):
        predictions = {
            name: grouped_predictions(rows, target, features, group_key, conditions)
            for name, features in models.items()
        }
        scores = {name: rmse(actual, pred) for name, pred in predictions.items()}
        fold_scores = {}
        for group in sorted({group_key(row) for row in rows}, key=str):
            idx = [i for i, row in enumerate(rows) if group_key(row) == group]
            fold_scores[str(group)] = {
                name: rmse([actual[i] for i in idx], [predictions[name][i] for i in idx])
                for name in models
            }
        output[scheme] = {"rmse": scores, "fold_rmse": fold_scores}
    return output


def score_temporal(train, test, target, models):
    conditions = sorted({row["condition"] for row in train})
    actual = [row[target] for row in test]
    predictions = {
        name: temporal_predictions(train, test, target, features, conditions)
        for name, features in models.items()
    }
    return {
        "n_transitions": len(test),
        "n_rollouts": len({(row["schedule"], row["seed"]) for row in test}),
        "rmse": {name: rmse(actual, pred) for name, pred in predictions.items()},
    }


def residualized_correlation(rows, x, y):
    conditions = sorted({row["condition"] for row in rows})
    ci = {condition: i for i, condition in enumerate(conditions)}
    c = np.zeros((len(rows), len(conditions)))
    for i, row in enumerate(rows):
        c[i, ci[row["condition"]]] = 1.0
    xv = np.asarray([row[x] for row in rows], dtype=float)
    yv = np.asarray([row[y] for row in rows], dtype=float)
    bx, *_ = np.linalg.lstsq(c, xv, rcond=None)
    by, *_ = np.linalg.lstsq(c, yv, rcond=None)
    xr, yr = xv - c @ bx, yv - c @ by
    if np.std(xr) == 0 or np.std(yr) == 0:
        return None
    return float(np.corrcoef(xr, yr)[0, 1])


def percent_change(new, old):
    return 100.0 * (new / old - 1.0)


def summarize_grid(grid):
    rows = build_rows(grid)
    signed_models = {
        "C": [],
        "G": ["gap"],
        "H": ["entropy"],
        "S": ["spread"],
        "GH": ["gap", "entropy"],
        "GS": ["gap", "spread"],
        "GHS": ["gap", "entropy", "spread"],
        "GP": ["gap", "pool"],
        "GPH": ["gap", "pool", "entropy"],
        "GPS": ["gap", "pool", "spread"],
        "GPHS": ["gap", "pool", "entropy", "spread"],
    }
    magnitude_models = {
        "C": [],
        "A": ["abs_gap"],
        "H": ["entropy"],
        "S": ["spread"],
        "AH": ["abs_gap", "entropy"],
        "AS": ["abs_gap", "spread"],
        "AHS": ["abs_gap", "entropy", "spread"],
    }
    spread_models = {
        "C": [],
        "H": ["entropy"],
        "S": ["spread"],
        "HS": ["entropy", "spread"],
    }
    signed = score_family(rows, "drift", signed_models)
    magnitude = score_family(rows, "abs_drift", magnitude_models)
    next_spread = score_family(rows, "next_spread", spread_models)
    loso = signed["LOSO"]["rmse"]
    return {
        "n_transitions": len(rows),
        "n_rollouts": len({(row["condition"], row["seed"]) for row in rows}),
        "n_seeds": len({row["seed"] for row in rows}),
        "conditions": sorted({row["condition"] for row in rows}),
        "instrument_note": (
            "two generic open-prompt entropy items"
            if grid in ("K1", "K2")
            else "two insecure-code self-description entropy items; not directly comparable to K1/K2"
        ),
        "signed_drift": signed,
        "movement_magnitude": magnitude,
        "next_axis_spread": next_spread,
        "condition_residualized_correlations": {
            "entropy_with_current_axis_spread": residualized_correlation(rows, "entropy", "spread"),
            "entropy_with_signed_drift": residualized_correlation(rows, "entropy", "drift"),
            "entropy_with_movement_magnitude": residualized_correlation(rows, "entropy", "abs_drift"),
            "entropy_with_next_axis_spread": residualized_correlation(rows, "entropy", "next_spread"),
        },
        "headline_loso_percent_changes": {
            "entropy_alone_vs_condition_signed_drift": percent_change(loso["H"], loso["C"]),
            "gap_vs_condition_signed_drift": percent_change(loso["G"], loso["C"]),
            "gap_plus_entropy_vs_gap_signed_drift": percent_change(loso["GH"], loso["G"]),
            "gap_plus_spread_vs_gap_signed_drift": percent_change(loso["GS"], loso["G"]),
            "gap_pool_entropy_vs_gap_pool_signed_drift": percent_change(loso["GPH"], loso["GP"]),
            "gap_pool_spread_vs_gap_pool_signed_drift": percent_change(loso["GPS"], loso["GP"]),
        },
        "rows": rows,
    }


def main():
    manifest_path = ROOT / "experiments" / "rollout_manifest.json"
    manifest = json.loads(manifest_path.read_text())
    release_rows = build_release_rows()
    k2_rows = build_rows("K2")
    temporal_models = {
        "C": [],
        "G": ["gap"],
        "H": ["entropy"],
        "S": ["spread"],
        "GH": ["gap", "entropy"],
        "GS": ["gap", "spread"],
        "GHS": ["gap", "entropy", "spread"],
        "GP": ["gap", "pool"],
        "GPH": ["gap", "pool", "entropy"],
        "GPS": ["gap", "pool", "spread"],
        "GPHS": ["gap", "pool", "entropy", "spread"],
    }
    result = {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "post-hoc exploratory; frozen M2 is unchanged",
        "provenance": {
            "manifest": str(manifest_path.relative_to(ROOT)),
            "manifest_sha256": hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
            "manifest_dedup_rule": manifest.get("dedup_rule"),
            "manifest_source_sha256": manifest.get("source_sha256"),
        },
        "model_legend": {
            "C": "condition intercepts",
            "G": "C + kept-minus-pool gap",
            "H": "C + checkpoint entropy",
            "S": "C + target-axis candidate spread",
            "P": "current pool level",
            "A": "absolute kept-minus-pool gap",
            "combined_names": "letters denote additive feature combinations",
        },
        "grids": {grid: summarize_grid(grid) for grid in ("K1", "K2", "K3")},
        "k2_to_release_temporal_holdout": {
            "status": "fully post-hoc; trains on canonical K2 and scores canonical release transitions without refitting",
            "signed_drift": score_temporal(k2_rows, release_rows, "drift", temporal_models),
            "movement_magnitude": score_temporal(
                k2_rows,
                release_rows,
                "abs_drift",
                {
                    "C": [], "A": ["abs_gap"], "H": ["entropy"], "S": ["spread"],
                    "AH": ["abs_gap", "entropy"], "AS": ["abs_gap", "spread"],
                    "AHS": ["abs_gap", "entropy", "spread"],
                },
            ),
            "next_axis_spread": score_temporal(
                k2_rows,
                release_rows,
                "next_spread",
                {"C": [], "H": ["entropy"], "S": ["spread"], "HS": ["entropy", "spread"]},
            ),
        },
    }
    tmp = OUTPUT.with_suffix(".json.tmp")
    with tmp.open("w") as f:
        json.dump(result, f, indent=2)
        f.write("\n")
    os.replace(tmp, OUTPUT)
    print(f"wrote {OUTPUT.relative_to(ROOT)}")
    for grid, block in result["grids"].items():
        h = block["headline_loso_percent_changes"]
        print(
            f"{grid}: H vs C {h['entropy_alone_vs_condition_signed_drift']:+.1f}%; "
            f"G vs C {h['gap_vs_condition_signed_drift']:+.1f}%; "
            f"GH vs G {h['gap_plus_entropy_vs_gap_signed_drift']:+.1f}%; "
            f"GS vs G {h['gap_plus_spread_vs_gap_signed_drift']:+.1f}%"
        )


if __name__ == "__main__":
    main()
