"""Validate and summarize the downloaded fixed-pool cross-judge result.

Usage:
    python3 scripts/analysis_crossjudge_rescoring.py \
      --input experiments/crossjudge_rescoring/output/crossjudge_rescoring.json

Writes analysis_summary.json next to the input unless --output is supplied.
"""

import argparse
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input",
        default="experiments/crossjudge_rescoring/output/crossjudge_rescoring.json",
    )
    parser.add_argument("--output", default="")
    args = parser.parse_args()

    source = Path(args.input)
    data = json.loads(source.read_text())
    config = data["_config"]
    analysis = data["analysis"]
    assert config["judging_format"] == "cross_owner_head_to_head_both_orders"
    assert config["source_judge"] == "base"
    assert analysis["interpretation_gate"]["infection_movement_predictor_validated"] is False

    judges = analysis["by_judge"]
    associations = analysis["panel_association"]
    reproduction = analysis["reproduction"]
    failed_reproduction = [name for name, row in reproduction.items()
                           if not row.get("passes")]
    n_judges = associations["n_judges_including_source"]

    raw_by_cell = [row["raw_agreement_vs_counterfactual_cogen_share"]
                   for row in associations["by_cell"].values()
                   if row["raw_agreement_vs_counterfactual_cogen_share"] is not None]
    residual_by_cell = [row["residual_agreement_vs_counterfactual_cogen_share"]
                        for row in associations["by_cell"].values()
                        if row["residual_agreement_vs_counterfactual_cogen_share"] is not None]
    raw_positive = sum(value > 0 for value in raw_by_cell)
    residual_positive = sum(value > 0 for value in residual_by_cell)

    if failed_reproduction:
        uptake_verdict = "INVALID_REPRODUCTION"
    elif n_judges < 4:
        uptake_verdict = "INSUFFICIENT_PANEL"
    elif raw_positive >= 3 and residual_positive >= 3:
        uptake_verdict = "DESCRIPTIVE_UPTAKE_ASSOCIATION_CONSISTENT"
    else:
        uptake_verdict = "DESCRIPTIVE_UPTAKE_ASSOCIATION_NOT_CONSISTENT"

    summary = {
        "status": "descriptive_mechanism_check_not_movement_prediction",
        "input": str(source),
        "n_judges_including_source": n_judges,
        "judges": {
            name: {
                "agreement": row["mean_pearson_vs_source"],
                "risk_length_residual_agreement": row[
                    "mean_residual_corr_vs_source_given_risk_length"
                ],
                "top2_overlap": row["mean_top2_jaccard_vs_source"],
                "counterfactual_supplier_kept_share": row[
                    "counterfactual_cogen_share"
                ],
            }
            for name, row in judges.items()
        },
        "reproduction": reproduction,
        "uptake_association": {
            "verdict": uptake_verdict,
            "overall": associations["overall"],
            "raw_positive_cells": raw_positive,
            "raw_cells_tested": len(raw_by_cell),
            "residual_positive_cells": residual_positive,
            "residual_cells_tested": len(residual_by_cell),
            "by_cell": associations["by_cell"],
            "scope": (
                "Association is between judge agreement and counterfactual "
                "supplier selection on fixed pools. It is not evidence that "
                "agreement predicts trained-model movement."
            ),
        },
        "movement_prediction": {
            "validated": False,
            "reason": analysis["interpretation_gate"]["reason"],
        },
    }
    output = Path(args.output) if args.output else source.with_name("analysis_summary.json")
    output.write_text(json.dumps(summary, indent=2) + "\n")

    def fmt(value):
        return "NA" if value is None else f"{value:.3f}"

    print(f"uptake verdict: {uptake_verdict}")
    for name, row in summary["judges"].items():
        print(
            f"{name:14s} agreement={fmt(row['agreement'])} "
            f"residual={fmt(row['risk_length_residual_agreement'])} "
            f"top2={fmt(row['top2_overlap'])} "
            f"supplier_keep={fmt(row['counterfactual_supplier_kept_share'])}"
        )
    print("movement predictor validated: NO")
    print(f"wrote {output}")


if __name__ == "__main__":
    main()
