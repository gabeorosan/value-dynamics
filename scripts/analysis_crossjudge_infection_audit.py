"""Audit whether source-recipient judge similarity predicts invasion.

This is a feasibility/confounding audit, not a confirmatory predictor test.
The eight existing invasion cells cross recipient judge only imperfectly and
change judging format at the same time. Reference/base cells are also
tautological: the source judge and recipient judge are the same base judge.

Usage:
    python3 scripts/analysis_crossjudge_infection_audit.py

Writes experiments/crossjudge_infection_audit.json.
"""

import glob
import json
import math
import os


OUT = "experiments/crossjudge_infection_audit.json"


def mean(values):
    values = [v for v in values if v is not None]
    return sum(values) / len(values) if values else None


def corr(xs, ys):
    if len(xs) < 3 or len(xs) != len(ys):
        return None
    mx, my = mean(xs), mean(ys)
    dx = [x - mx for x in xs]
    dy = [y - my for y in ys]
    denom = math.sqrt(sum(x * x for x in dx) * sum(y * y for y in dy))
    return sum(x * y for x, y in zip(dx, dy)) / denom if denom else None


def partial_corr(xs, ys, zs):
    """Pearson partial correlation of x and y conditional on scalar z."""
    rxy, rxz, ryz = corr(xs, ys), corr(xs, zs), corr(ys, zs)
    if None in (rxy, rxz, ryz):
        return None
    denom = math.sqrt(max(0.0, (1 - rxz * rxz) * (1 - ryz * ryz)))
    return (rxy - rxz * ryz) / denom if denom > 1e-12 else None


def rounded(value):
    return round(value, 4) if value is not None else None


def cell_correlations(rows, x_key, y_key):
    pairs = [(row[x_key], row[y_key]) for row in rows
             if row[x_key] is not None and row[y_key] is not None]
    return rounded(corr([p[0] for p in pairs], [p[1] for p in pairs]))


def main():
    cells = []
    paths = sorted(glob.glob("experiments/modal_k2_release/output/*invade*.json"))
    for path in paths:
        data = json.load(open(path))
        for seed, conditions in data.items():
            if seed.startswith("_"):
                continue
            for condition, rec in conditions.items():
                if "invade" not in condition:
                    continue
                raw = rec["rounds_raw"][0]
                raw_agreement = []
                risk_conditional_agreement = []
                source_risk_alignment = []
                recipient_risk_alignment = []
                for item in raw:
                    source = item.get("scores_base")
                    recipient = (item.get("scores_h2h")
                                 if isinstance(item.get("scores_h2h"), list)
                                 else item.get("scores_arm"))
                    risk = item.get("cand_risk")
                    if not (isinstance(source, list) and
                            isinstance(recipient, list) and
                            isinstance(risk, list)):
                        continue
                    raw_agreement.append(corr(source, recipient))
                    risk_conditional_agreement.append(
                        partial_corr(source, recipient, risk)
                    )
                    source_risk_alignment.append(corr(source, risk))
                    recipient_risk_alignment.append(corr(recipient, risk))

                kept_owners = [item["cand_owner"][idx]
                               for item in raw for idx in item["kept_idx"]]
                kept_cogen = (kept_owners.count("cogen") / len(kept_owners)
                              if kept_owners else None)
                cells.append({
                    "cell": f"{condition}_s{seed}",
                    "file": os.path.basename(path),
                    "format": "duel" if condition.startswith("h2h_") else "reference",
                    "recipient": "self" if "_self" in condition else "base",
                    "mean_item_source_recipient_corr": rounded(mean(raw_agreement)),
                    "mean_item_source_recipient_partial_corr_given_risk": rounded(
                        mean(risk_conditional_agreement)
                    ),
                    "mean_item_source_risk_corr": rounded(mean(source_risk_alignment)),
                    "mean_item_recipient_risk_corr": rounded(mean(recipient_risk_alignment)),
                    "kept_cogen_share_round1": rounded(kept_cogen),
                    "movement_round1": rounded(rec["traj"][1] - rec["traj"][0]),
                    "movement_endpoint": rounded(rec["traj"][-1] - rec["traj"][0]),
                })

    by_format = {}
    for fmt in ("all", "reference", "duel"):
        rows = cells if fmt == "all" else [c for c in cells if c["format"] == fmt]
        by_format[fmt] = {
            "n_cells": len(rows),
            "raw_agreement_vs_round1_movement": cell_correlations(
                rows, "mean_item_source_recipient_corr", "movement_round1"
            ),
            "raw_agreement_vs_kept_cogen_share": cell_correlations(
                rows, "mean_item_source_recipient_corr", "kept_cogen_share_round1"
            ),
            "risk_conditional_agreement_vs_round1_movement": cell_correlations(
                rows,
                "mean_item_source_recipient_partial_corr_given_risk",
                "movement_round1",
            ),
            "risk_conditional_agreement_vs_kept_cogen_share": cell_correlations(
                rows,
                "mean_item_source_recipient_partial_corr_given_risk",
                "kept_cogen_share_round1",
            ),
        }

    output = {
        "status": "confounding_audit_not_predictor_validation",
        "source_judge": "frozen_base",
        "n_cells": len(cells),
        "cells": cells,
        "cell_level_correlations": by_format,
        "design_limits": [
            "judging format is confounded with the apparent agreement range",
            "reference/base cells compare the base source judge with itself",
            "only four cells exist within each format",
            "seed cells are not independent source-recipient judge pairs",
            "duel scores and reference scores come from different scoring procedures",
        ],
    }
    with open(OUT, "w") as handle:
        json.dump(output, handle, indent=2)
        handle.write("\n")
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
