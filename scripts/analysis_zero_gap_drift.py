"""Does the value move when selection is not acting?

THE QUESTION. The spread-intervention runs threw up something the program's model
does not describe: the concentrated arm moved by up to 0.14 across rounds in which its
selection gap was exactly 0.000, and the random-selection control moved too, in
inconsistent directions across runs (+0.083 and +0.097 in one, -0.132 in another).
Fine-tuning on a set of the model's own answers that is not selected on the value axis
should not systematically move that value. Something does.

That observation rests on a handful of rollouts. This tests it for free on the
committed 340-round corpus, which contains many rounds whose realized selection gap is
essentially zero.

THE TEST. For rounds with |gap| below a threshold, compare the size of the observed
round-to-round change against the measurement noise floor for that same pair of
readings. The table carries per-row standard errors for the value measurement, so the
expected |change| under the null of "nothing moved, we just re-measured" is computable
per row rather than assumed:

    noise SD for a difference = sqrt(se_t^2 + se_next^2)
    E|difference| under a mean-zero normal = noise SD * sqrt(2/pi)

If the mean |drift| on zero-gap rounds materially exceeds that, the value is moving for
reasons the selection model does not name. If it matches, the spread-intervention
observation was small-sample noise and no new phenomenon exists.

WHY MEAN DRIFT IS THE WRONG STATISTIC HERE, and why the ledger's existing neutral-null
row does not already answer this. That row reports mean drift ~0.000 on the random
arms, which is a statement that the movement has no consistent DIRECTION. It is silent
on whether there is movement at all. A random walk has mean displacement zero and
moves constantly. The quantity that separates them is |drift| against the noise floor.
"""

import json
import math
import statistics
from collections import defaultdict

SRC = "experiments/spread_util_unified.json"
OUT = "experiments/zero_gap_drift.json"
E_ABS = math.sqrt(2.0 / math.pi)   # E|X| for X ~ N(0, 1)


def rows_with_noise(recs):
    """Rounds carrying both a drift and the two standard errors it is built from."""
    out = []
    for r in recs:
        se_t, se_n = r.get("value_measurement_se"), r.get("next_value_measurement_se")
        if r.get("drift") is None or se_t is None or se_n is None:
            continue
        noise_sd = math.sqrt(se_t ** 2 + se_n ** 2)
        # A handful of rows report a near-zero standard error (a probe where every
        # read agreed). Dividing by those produces meaningless z values -- one row
        # pushed a mean to 1e8 before this guard. The measurement is a mean of
        # binary reads, so its SE cannot honestly be below 1/(2*sqrt(n)) for the
        # smallest n in the table; 0.01 is a conservative floor.
        if noise_sd < 0.01:
            continue
        out.append({
            "drift": r["drift"], "gap": r.get("gap"), "rho": r.get("rho"),
            "spread": r.get("spread"), "value": r.get("value"),
            "judge": r.get("judge"), "composition": r.get("composition"),
            "organism": r.get("organism"), "axis": r.get("axis"),
            "noise_sd": noise_sd,
            "expected_abs": noise_sd * E_ABS,
        })
    return out


def summarise(rows, label):
    if len(rows) < 5:
        return {"label": label, "n": len(rows), "note": "too few rows"}
    obs = statistics.mean(abs(r["drift"]) for r in rows)
    exp = statistics.mean(r["expected_abs"] for r in rows)
    # Per-row excess, so rows with different measurement precision are comparable.
    z = [abs(r["drift"]) / r["noise_sd"] for r in rows]
    return {
        "label": label,
        "n": len(rows),
        "mean_drift_signed": round(statistics.mean(r["drift"] for r in rows), 4),
        "mean_abs_drift_observed": round(obs, 4),
        "mean_abs_drift_expected_from_noise": round(exp, 4),
        "ratio_observed_over_expected": round(obs / exp, 3) if exp > 0 else None,
        "mean_abs_drift_in_noise_SDs": round(statistics.mean(z), 3),
        "median_abs_drift_in_noise_SDs": round(statistics.median(z), 3),
        "fraction_exceeding_2_noise_SDs": round(sum(1 for x in z if x > 2) / len(z), 3),
        "mean_gap": round(statistics.mean(abs(r["gap"]) for r in rows if r["gap"] is not None), 4),
    }


def main():
    recs = json.load(open(SRC))["records"]
    rows = rows_with_noise(recs)

    out = {
        "description": "Do values move on rounds where the selection gap is ~0? "
                       "Observed |drift| against the per-row measurement-noise floor.",
        "method": {
            "noise_floor": "sqrt(se_t^2 + se_next^2) * sqrt(2/pi), the expected |change| "
                           "if nothing moved and we merely re-measured",
            "why_not_mean_drift": "mean drift ~0 says movement has no consistent "
                                  "direction; it does not say there is no movement. A "
                                  "random walk satisfies it. |drift| vs the noise floor "
                                  "is what separates the two.",
        },
        "n_rows_with_noise_data": len(rows),
        "n_records_total": len(recs),
    }

    # Headline: the tightest zero-gap slice, then progressively looser.
    for thresh in (0.01, 0.02, 0.05):
        sel = [r for r in rows if r["gap"] is not None and abs(r["gap"]) <= thresh]
        out[f"zero_gap_within_{thresh}"] = summarise(sel, f"|gap| <= {thresh}")

    # Comparator: rounds with a real gap, to show the statistic behaves.
    big = [r for r in rows if r["gap"] is not None and abs(r["gap"]) >= 0.15]
    out["large_gap_comparator"] = summarise(big, "|gap| >= 0.15")

    # The random-selector arms specifically -- selection genuinely absent by design,
    # not merely small by accident.
    rnd = [r for r in rows if r["judge"] == "random"]
    out["random_selector_arms"] = summarise(rnd, "judge == random")

    # Slice the zero-gap rounds, to see whether any subgroup drives it.
    zero = [r for r in rows if r["gap"] is not None and abs(r["gap"]) <= 0.02]
    by = defaultdict(list)
    for r in zero:
        by[f"organism:{r['organism']}"].append(r)
        by[f"axis:{r['axis']}"].append(r)
        by[f"composition:{r['composition']}"].append(r)
    out["zero_gap_slices"] = {k: summarise(v, k) for k, v in sorted(by.items())
                              if len(v) >= 5}

    with open(OUT, "w") as f:
        json.dump(out, f, indent=1)

    print(f"rows with noise data: {len(rows)} of {len(recs)}\n")
    for k in ("zero_gap_within_0.01", "zero_gap_within_0.02", "zero_gap_within_0.05",
              "large_gap_comparator", "random_selector_arms"):
        print(k, json.dumps(out[k], indent=1))
        print()


if __name__ == "__main__":
    main()
