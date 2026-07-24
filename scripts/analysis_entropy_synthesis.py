#!/usr/bin/env python3
"""Reconstruct the cross-experiment entropy story from saved artifacts.

This analysis keeps two quantities separate:

1. generic next-token generation entropy on open prompts; and
2. within-pool score spread on the value axis used for selection.

The output is intentionally compact and figure-ready. It does not pool the
quantities into one regression because their prompts, scales, and meanings
differ across experiments.

Usage:
  uv run python scripts/analysis_entropy_synthesis.py
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "experiments" / "entropy_synthesis_analysis.json"

SOURCES = {
    "sft_anatomy": ROOT / "experiments/kaggle/kaggle_sft_drift_anatomy/output/sft_drift_anatomy.json",
    "selfgen_mixing": ROOT / "experiments/kaggle/kaggle_selfgen_collapse_mixing/output/selfgen_collapse_mixing.json",
    "basin_ensemble_measurements": ROOT / "experiments/modal/modal_measurement_service/output/basin_ensemble",
    "basin_anchor": ROOT / "experiments/kaggle/kaggle_basin_anchor/output/basin_anchor.json",
    "selfaware_grid": ROOT / "experiments/em_selfaware_loop/output/selfaware_loop_grid.json",
    "olmo_rich_reversal": ROOT / "experiments/modal_k2_release/output/k2rel_oracle_hold_s21.json",
    "olmo_inert_rail": ROOT / "experiments/modal_k2_release/output/k2rel_oracle_hold_s22.json",
    "qwen_mixed_reopen": ROOT / "experiments/em_selfaware_loop/output/mixed_reopen_qwen.json",
    "qwen_selfonly_twin": ROOT / "experiments/em_selfaware_loop/output/mixed_reopen_twin_selfonly.json",
}


def load(path: Path):
    with path.open() as f:
        return json.load(f)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def entropy_from_measurement(measurement: dict) -> float:
    return float(measurement["behavior"]["gen_token_entropy"]["mean"])


def summary(values: list[float]) -> dict:
    arr = np.asarray(values, dtype=float)
    return {
        "n": int(len(arr)),
        "mean": float(arr.mean()),
        "sd": float(arr.std(ddof=1)) if len(arr) > 1 else None,
        "se": float(arr.std(ddof=1) / math.sqrt(len(arr))) if len(arr) > 1 else None,
        "min": float(arr.min()),
        "max": float(arr.max()),
    }


def one_sided_sign_p(wins: int, n: int) -> float:
    return float(sum(math.comb(n, k) for k in range(wins, n + 1)) / (2**n))


def prereg_spread(items: list[dict], key: str) -> float:
    return float(np.mean([np.std(item[key]) for item in items]))


def analyze_anatomy() -> dict:
    data = load(SOURCES["sft_anatomy"])
    rows = []
    grouped: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for rollout in data["rollouts"]:
        measurements = rollout["measurements"]
        row = {
            "organism": rollout["organism"],
            "arm": rollout["chooser"],
            "seed": int(rollout["draw_seed"]),
            "round_steps": int(rollout["round_steps"]),
            "entropy_start": entropy_from_measurement(measurements[0]),
            "entropy_final": entropy_from_measurement(measurements[-1]),
        }
        row["delta"] = row["entropy_final"] - row["entropy_start"]
        rows.append(row)
        grouped[(row["organism"], row["arm"])].append(row)

    groups = {}
    for (organism, arm), members in sorted(grouped.items()):
        groups[f"{organism}/{arm}"] = {
            "organism": organism,
            "arm": arm,
            "round_steps": sorted({m["round_steps"] for m in members}),
            "entropy_start": summary([m["entropy_start"] for m in members]),
            "entropy_final": summary([m["entropy_final"] for m in members]),
            "delta": summary([m["delta"] for m in members]),
        }
    return {"n_rollouts": len(rows), "rows": rows, "groups": groups}


def analyze_mixing(anatomy: dict) -> dict:
    data = load(SOURCES["selfgen_mixing"])
    rows = []
    grouped: dict[tuple[str, float], list[dict]] = defaultdict(list)
    for rollout in data["rollouts"]:
        fraction = int(rollout["chooser"].split("_")[-1]) / 100
        measurements = rollout["measurements"]
        row = {
            "organism": rollout["organism"],
            "self_fraction": fraction,
            "seed": int(rollout["draw_seed"]),
            "entropy_start": entropy_from_measurement(measurements[0]),
            "entropy_final": entropy_from_measurement(measurements[-1]),
        }
        row["delta"] = row["entropy_final"] - row["entropy_start"]
        rows.append(row)
        grouped[(row["organism"], fraction)].append(row)

    groups = {}
    means_by_organism: dict[str, list[tuple[float, float]]] = defaultdict(list)
    for (organism, fraction), members in sorted(grouped.items()):
        key = f"{organism}/lambda_{int(fraction * 100)}"
        groups[key] = {
            "organism": organism,
            "self_fraction": fraction,
            "entropy_final": summary([m["entropy_final"] for m in members]),
            "delta": summary([m["delta"] for m in members]),
        }
        means_by_organism[organism].append(
            (fraction, groups[key]["entropy_final"]["mean"])
        )

    monotonic = {}
    for organism, pairs in means_by_organism.items():
        ordered = sorted(pairs)
        monotonic[organism] = {
            "ordered_self_fraction_and_mean": ordered,
            "mean_entropy_nonincreasing_with_more_self_data": all(
                ordered[i + 1][1] <= ordered[i][1] for i in range(len(ordered) - 1)
            ),
        }

    replication = {}
    for organism in ("base", "sycophancy"):
        anatomy_mean = anatomy["groups"][f"{organism}/self_gen"]["entropy_final"]["mean"]
        mixing_mean = groups[f"{organism}/lambda_100"]["entropy_final"]["mean"]
        replication[organism] = {
            "anatomy_self_gen": anatomy_mean,
            "mixing_lambda_100": mixing_mean,
            "absolute_difference": abs(anatomy_mean - mixing_mean),
        }

    return {
        "n_rollouts": len(rows),
        "rows": rows,
        "groups": groups,
        "monotonic_mean_curve": monotonic,
        "lambda_100_endpoint_replication": replication,
    }


def analyze_dose() -> dict:
    directory = SOURCES["basin_ensemble_measurements"]
    pattern = re.compile(r"risk_dose(\d+)_seed(\d+)_r(\d+)\.json$")
    rows = []
    source_files = []
    for path in sorted(directory.glob("risk_dose*_seed*_r*.json")):
        match = pattern.match(path.name)
        if not match:
            continue
        measurement = load(path)
        dose, seed, round_ = map(int, match.groups())
        rows.append(
            {
                "dose_steps": dose,
                "seed": seed,
                "round": round_,
                "entropy": entropy_from_measurement(measurement),
            }
        )
        source_files.append(path)

    groups = {}
    for dose in (5, 10, 20):
        for round_ in (1, 3, 5):
            values = [
                r["entropy"]
                for r in rows
                if r["dose_steps"] == dose and r["round"] == round_
            ]
            groups[f"dose_{dose}/round_{round_}"] = {
                "dose_steps": dose,
                "round": round_,
                "entropy": summary(values),
            }

    paired = {}
    by_key = {(r["dose_steps"], r["seed"], r["round"]): r["entropy"] for r in rows}
    for low, high in ((5, 10), (10, 20), (5, 20)):
        diffs = [by_key[(low, seed, 5)] - by_key[(high, seed, 5)] for seed in range(1, 13)]
        wins = sum(d > 0 for d in diffs)
        paired[f"dose_{low}_minus_{high}_at_r5"] = {
            "n_pairs": len(diffs),
            "entropy_difference": summary(diffs),
            "lower_dose_higher_entropy_wins": wins,
            "one_sided_exact_sign_p": one_sided_sign_p(wins, len(diffs)),
        }

    organism_path = directory / "risk_organism.json"
    organism_entropy = entropy_from_measurement(load(organism_path))
    return {
        "n_measurements": len(rows),
        "n_rollouts": 36,
        "organism_round0_entropy": organism_entropy,
        "rows": rows,
        "groups": groups,
        "paired_r5_dose_checks": paired,
        "source_file_count": len(source_files) + 1,
    }


def analyze_counterexamples() -> dict:
    anchor = load(SOURCES["basin_anchor"])
    anchor_groups = {}
    for condition in ("persona_self", "persona_cross"):
        rows = []
        for seed, seed_data in sorted(anchor.items(), key=lambda x: int(x[0])):
            batteries = seed_data[condition]["battery"]
            start = float(batteries[0]["entropy"]["mean"])
            final = float(batteries[-1]["entropy"]["mean"])
            rows.append({"seed": int(seed), "start": start, "final": final, "delta": final - start})
        anchor_groups[condition] = {
            "n": len(rows),
            "start": summary([r["start"] for r in rows]),
            "final": summary([r["final"] for r in rows]),
            "delta": summary([r["delta"] for r in rows]),
            "rows": rows,
        }

    grid = load(SOURCES["selfaware_grid"])
    grid_rows = []
    for key, cell in sorted(grid["cells"].items()):
        baseline = float(grid["baselines"][cell["dose"]]["battery"]["entropy_mean"])
        final = float(cell["battery"][-1]["entropy_mean"])
        grid_rows.append(
            {
                "cell": key,
                "dose": cell["dose"],
                "seed": int(cell["seed"]),
                "rounds": len(cell["battery"]),
                "entropy_start": baseline,
                "entropy_final": final,
                "fraction_remaining": final / baseline,
            }
        )

    return {
        "fresh_candidate_basin_anchor": anchor_groups,
        "selective_selfaware_grid": {
            "n_cells": len(grid_rows),
            "rows": grid_rows,
            "final_entropy": summary([r["entropy_final"] for r in grid_rows]),
            "all_final_below_0_04": all(r["entropy_final"] < 0.04 for r in grid_rows),
        },
    }


def olmo_case(path: Path, seed: int) -> dict:
    data = load(path)
    cell = data[str(seed)]["oracle_hold"]
    entropy = [float(b["entropy"]["mean"]) for b in cell["battery"]]
    spreads = [prereg_spread(items, "cand_risk") for items in cell["rounds_raw"]]
    return {
        "seed": seed,
        "trajectory": [float(x) for x in cell["traj"]],
        "generic_token_entropy": entropy,
        "target_axis_pool_spread": spreads,
        "total_movement": float(cell["traj"][-1] - cell["traj"][0]),
    }


def qwen_cases(path: Path) -> list[dict]:
    data = load(path)
    rows = []
    for key, cell in sorted(data["cells"].items()):
        baseline = data["baselines"][cell["dose"]]
        entropy = [float(baseline["battery"]["entropy_mean"])] + [
            float(b["entropy_mean"]) for b in cell["battery"]
        ]
        spread = [prereg_spread(items, "cand_sr_scores") for items in cell["rounds_raw"]]
        trajectory = [float(baseline["sr_freegen_mean"])] + [
            float(b["sr_free_gen"]["sr_freegen"]) for b in cell["battery"]
        ]
        rows.append(
            {
                "cell": key,
                "trajectory": trajectory,
                "generic_token_entropy": entropy,
                "target_axis_pool_spread": spread,
                "first_step_movement": trajectory[1] - trajectory[0],
            }
        )
    return rows


def analyze_entropy_vs_actionable_variation() -> dict:
    rich = olmo_case(SOURCES["olmo_rich_reversal"], 21)
    inert = olmo_case(SOURCES["olmo_inert_rail"], 22)
    twin = qwen_cases(SOURCES["qwen_selfonly_twin"])
    mixed = qwen_cases(SOURCES["qwen_mixed_reopen"])

    olmo_entropy_overlap = {
        "rich_min": min(rich["generic_token_entropy"]),
        "rich_max": max(rich["generic_token_entropy"]),
        "inert_min": min(inert["generic_token_entropy"]),
        "inert_max": max(inert["generic_token_entropy"]),
        "intervals_overlap": max(
            min(rich["generic_token_entropy"]), min(inert["generic_token_entropy"])
        )
        <= min(max(rich["generic_token_entropy"]), max(inert["generic_token_entropy"])),
    }

    return {
        "olmo_material_rich_reversal": rich,
        "olmo_target_axis_inert_rail": inert,
        "olmo_generic_entropy_overlap": olmo_entropy_overlap,
        "qwen_matched_selfonly": twin,
        "qwen_matched_external_supply": mixed,
        "interpretation": (
            "Generic token entropy is neither identical to nor sufficient for target-axis material. "
            "The two OLMo cases have overlapping generic entropy, but only the case with positive "
            "risk-axis spread moves. In the matched Qwen pair, external supply restores both generic "
            "diversity and insecurity-axis spread, so it demonstrates reopening without identifying "
            "which diversity measure is independently causal."
        ),
    }


def provenance() -> dict:
    out = {}
    for name, path in SOURCES.items():
        if path.is_dir():
            files = sorted(path.glob("risk_dose*_seed*_r*.json")) + [path / "risk_organism.json"]
            out[name] = {
                "path": str(path.relative_to(ROOT)),
                "file_count": len(files),
                "aggregate_sha256": hashlib.sha256(
                    "".join(f"{p.name}:{sha256(p)}\n" for p in files).encode()
                ).hexdigest(),
            }
        else:
            out[name] = {
                "path": str(path.relative_to(ROOT)),
                "sha256": sha256(path),
            }
    return out


def main() -> None:
    anatomy = analyze_anatomy()
    result = {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "provenance": provenance(),
        "token_entropy_by_training_source": anatomy,
        "fresh_data_mixing_curve": analyze_mixing(anatomy),
        "dose_gradient": analyze_dose(),
        "counterexamples_to_a_universal_self_data_rule": analyze_counterexamples(),
        "token_entropy_vs_actionable_value_axis_variation": analyze_entropy_vs_actionable_variation(),
        "model_update": {
            "supported": [
                "More self-generated training data lowers generic token entropy on average in both tested organisms.",
                "Higher per-round optimizer dose lowers token entropy in the 36-rollout ensemble.",
                "The effect is contingent: a fresh-candidate risk loop can preserve entropy, while a selective insecure-code loop can collapse it.",
                "Movement under selection requires target-axis pool spread and a realized selection gap; generic token entropy alone does not certify either.",
            ],
            "not_supported": [
                "All self-training collapses token entropy.",
                "Fresh candidate sampling is sufficient to prevent entropy collapse.",
                "Generic token entropy can replace target-axis pool spread in the intervention-window model.",
            ],
        },
    }

    tmp = OUTPUT.with_suffix(".json.tmp")
    with tmp.open("w") as f:
        json.dump(result, f, indent=2)
        f.write("\n")
    os.replace(tmp, OUTPUT)

    mixing = result["fresh_data_mixing_curve"]["groups"]
    dose = result["dose_gradient"]["groups"]
    print(f"wrote {OUTPUT.relative_to(ROOT)}")
    print(
        "mixing endpoints: "
        f"base lambda1={mixing['base/lambda_100']['entropy_final']['mean']:.3f}, "
        f"lambda.25={mixing['base/lambda_25']['entropy_final']['mean']:.3f}; "
        f"syc lambda1={mixing['sycophancy/lambda_100']['entropy_final']['mean']:.3f}, "
        f"lambda.25={mixing['sycophancy/lambda_25']['entropy_final']['mean']:.3f}"
    )
    print(
        "dose r5: "
        + ", ".join(
            f"{d} steps={dose[f'dose_{d}/round_5']['entropy']['mean']:.3f}" for d in (5, 10, 20)
        )
    )
    print("verdict: token entropy is a controllable generative-health variable, not the target-axis state variable")


if __name__ == "__main__":
    main()
