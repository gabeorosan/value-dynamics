#!/usr/bin/env python3
"""Final order-sensitivity census for repaired risk experiments.

Covers the release grid, press-depth, cross-family oracle (branch e), and
mixed-generator branch m. K1/K2 are handled separately by
analysis_instrument_table.py. The generated trajectory is reported as the
order-averaged primary read, but this script checks that each load-bearing
direction or paired ordering is also present when gamble is A and when it is B.

Writes experiments/final_order_sensitivity.json and prints compact Markdown
tables for reports.
"""

from __future__ import annotations

import glob
import hashlib
import json
import os
from collections import defaultdict


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT = os.path.join(ROOT, "experiments/final_order_sensitivity.json")

SOURCE_PATTERNS = {
    "release": [
        "experiments/kaggle/kaggle_k2_release_relA/output/k2_release_kernelA.json",
        "experiments/kaggle/kaggle_k2_release_relB/output/k2_release_kernelB.json",
        "experiments/modal_k2_release/output/k2rel_press_to_base_s*.json",
        "experiments/modal_k2_release/output/k2rel_base_hold_s*.json",
    ],
    "press_depth": [
        "experiments/modal_k2_release/output/k2rel_press_d*_s*.json",
    ],
    "branch_e": [
        "experiments/modal_k2_release/output/k2rel_oracle_hold_s*.json",
    ],
    "branch_m": [
        "experiments/modal_k2_release/output/k2rel_oracle_mix_s*.json",
        "experiments/modal_k2_release/output/k2rel_cons_mix_s*.json",
        "experiments/modal_k2_release/output/k2rel_invade_base_s*.json",
        "experiments/modal_k2_release/output/k2rel_invade_self_s*.json",
    ],
}


def expand(patterns):
    return sorted({p for pattern in patterns for p in glob.glob(os.path.join(ROOT, pattern))})


def records(path):
    data = json.load(open(path))
    for seed, conditions in data.items():
        if not seed.isdigit() or not isinstance(conditions, dict):
            continue
        for condition, record in conditions.items():
            if isinstance(record, dict) and record.get("traj_order"):
                yield int(seed), condition, record


def order_entry(entry, order):
    generated = entry.get("generated", {})
    by_order = generated.get("by_order", {})
    if order in by_order:
        return float(by_order[order])
    legacy = entry.get(f"gamble_{order}_order")
    return float(legacy) if legacy is not None else None


def classify(delta_a, delta_b, eps=0.025):
    signs = []
    for value in (delta_a, delta_b):
        signs.append("up" if value > eps else "down" if value < -eps else "flat")
    return signs[0] if signs[0] == signs[1] else "/".join(signs)


def summarize(family, path, seed, condition, record):
    traj_order = record["traj_order"]
    start, end = traj_order[0], traj_order[-1]
    start_a, start_b = order_entry(start, "A"), order_entry(start, "B")
    end_a, end_b = order_entry(end, "A"), order_entry(end, "B")
    generated_flags = 0
    forced_flags = 0
    invalid_flags = 0
    for entry in traj_order:
        gen = entry.get("generated", {})
        a, b = order_entry(entry, "A"), order_entry(entry, "B")
        if None not in (a, b) and abs(a - b) > 0.10:
            generated_flags += 1
        forced = entry.get("forced", {})
        fbo = forced.get("by_order", {})
        if "A" in fbo and "B" in fbo and abs(float(fbo["A"]) - float(fbo["B"])) > 0.10:
            forced_flags += 1
        if float(gen.get("invalid_rate", entry.get("invalid_rate", 0.0)) or 0.0) > 0.10:
            invalid_flags += 1
    factual = [
        float(read["factual_ev"]["mean_p_correct"])
        for read in record.get("battery", [])
        if isinstance(read, dict)
        and isinstance(read.get("factual_ev"), dict)
        and read["factual_ev"].get("mean_p_correct") is not None
    ]
    factual_drop = (factual[0] - min(factual)) if factual else None
    return {
        "family": family,
        "source": os.path.relpath(path, ROOT),
        "condition": condition,
        "seed": seed,
        "n_reads": len(traj_order),
        "start": {"avg": float(start["overall"]), "A": start_a, "B": start_b},
        "end": {"avg": float(end["overall"]), "A": end_a, "B": end_b},
        "delta": {
            "avg": float(end["overall"] - start["overall"]),
            "A": end_a - start_a,
            "B": end_b - start_b,
        },
        "direction_both_orders": classify(end_a - start_a, end_b - start_b),
        "generated_order_flags_gt_0.10": generated_flags,
        "forced_order_flags_gt_0.10": forced_flags,
        "invalid_flags_gt_0.10": invalid_flags,
        "max_factual_ev_drop_from_start": factual_drop,
        "factual_ev_drop_flag_gt_0.10": factual_drop is not None and factual_drop > 0.10,
    }


def fmt(value):
    return f"{value:.3f}"


def main():
    rows = []
    source_sha256 = {}
    for family, patterns in SOURCE_PATTERNS.items():
        for path in expand(patterns):
            rel = os.path.relpath(path, ROOT)
            source_sha256[rel] = hashlib.sha256(open(path, "rb").read()).hexdigest()
            for seed, condition, record in records(path):
                rows.append(summarize(family, path, seed, condition, record))

    rows.sort(key=lambda row: (row["family"], row["condition"], row["seed"]))
    grouped = defaultdict(list)
    for row in rows:
        grouped[(row["family"], row["condition"])].append(row)

    group_summaries = []
    for (family, condition), members in sorted(grouped.items()):
        summary = {"family": family, "condition": condition, "n": len(members)}
        for order in ("avg", "A", "B"):
            endpoints = [row["end"][order] for row in members]
            summary[f"endpoint_mean_{order}"] = sum(endpoints) / len(endpoints)
            summary[f"endpoint_range_{order}"] = max(endpoints) - min(endpoints)
        group_summaries.append(summary)

    artifact = {
        "scope": "release, press-depth, branch e, branch m; generated channel primary",
        "flag_rule": "order gap > 0.10 is a flag; headline direction must survive in both orders",
        "source_sha256": source_sha256,
        "rows": rows,
        "group_summaries": group_summaries,
    }
    json.dump(artifact, open(OUTPUT, "w"), indent=1)

    print("| family | cell | endpoint avg / A / B | delta A / B | direction | gen flags | forced flags | invalid flags | max factual drop |")
    print("|---|---|---:|---:|---|---:|---:|---:|---:|")
    for row in rows:
        print(
            f"| {row['family']} | {row['condition']} s{row['seed']} | "
            f"{fmt(row['end']['avg'])} / {fmt(row['end']['A'])} / {fmt(row['end']['B'])} | "
            f"{fmt(row['delta']['A'])} / {fmt(row['delta']['B'])} | "
            f"{row['direction_both_orders']} | "
            f"{row['generated_order_flags_gt_0.10']}/{row['n_reads']} | "
            f"{row['forced_order_flags_gt_0.10']}/{row['n_reads']} | "
            f"{row['invalid_flags_gt_0.10']}/{row['n_reads']} | "
            f"{fmt(row['max_factual_ev_drop_from_start']) if row['max_factual_ev_drop_from_start'] is not None else '-'} |"
        )

    print("\nCondition endpoint ranges (avg / A / B):")
    for summary in group_summaries:
        print(
            f"  {summary['family']:11s} {summary['condition']:14s} n={summary['n']} "
            f"{summary['endpoint_range_avg']:.3f} / "
            f"{summary['endpoint_range_A']:.3f} / "
            f"{summary['endpoint_range_B']:.3f}"
        )
    print(f"\nwrote {OUTPUT}")


if __name__ == "__main__":
    main()
