"""Why does the selection gap shrink? Judge grip, pool variety, or arithmetic?

The saturation analysis relocated the bottleneck. The response per unit of
selection does not decay over four rounds; what decays is the selection itself —
mean absolute gap falls from 0.099 at round 1 to about 0.070 by round 4. Runs
level off because there is less and less to select on.

The gap factorises: gap = rho * sigma, agreement times spread. So the decline
has exactly two proximate sources and they mean different things.

  RHO FALLS      The judge stops discriminating on the value axis. Candidates
                 still differ; the selector no longer sorts them by the trait we
                 are tracking. This is the overoptimisation-shaped story — the
                 selector drifts onto something else.

  SIGMA FALLS    The candidates stop differing. The judge would still sort them
                 if it could. This is coverage exhaustion, and it is what Song
                 et al. (arXiv 2412.02674) report for the generation-verification
                 gap, which collapses in two to three rounds through diversity
                 loss.

And there is a third possibility that is not a finding about loops at all.

  ARITHMETIC     Every value axis in this corpus is scored 0/1 per candidate.
                 For binary scores the within-prompt SD is pinned by the pool
                 mean: sigma <= sqrt(q(1-q)), which goes to zero as q approaches
                 either rail. A run that moves toward a rail MUST lose spread,
                 whatever is happening to its diversity. An earlier analysis
                 found sigma ~= 0.813 * sqrt(q(1-q)) accounts for 85.9% of the
                 variance in spread, so this is most of the story before any
                 dynamics are invoked.

The decisive quantity is therefore the RESIDUAL spread, sigma / sqrt(q(1-q)):
spread as a fraction of the most a binary-scored pool at that mean could have.
If the residual is flat across rounds, the spread collapse is the rail effect
and there is no diversity loss to explain. If the residual falls, there is
genuine variety loss on top of the arithmetic.

Method note: the decline is decomposed on logs, because gap = rho * sigma is
multiplicative. log|gap| = log|rho| + log(sigma), so the fall in mean log|gap|
splits additively and the two shares are directly comparable. Rounds with
sigma = 0 or rho = 0 have no logarithm; they are counted and reported separately
rather than dropped silently, because a pool that has gone completely uniform is
the endpoint of the very process under study.

Writes experiments/gap_decline_decomposition.json.
"""

from __future__ import annotations

import json
import math
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
UNIFIED = ROOT / "experiments/spread_util_unified.json"
OUT = ROOT / "experiments/gap_decline_decomposition.json"

BOOTSTRAP_DRAWS = 4000
SEED = 20260728
HORIZON = 4


def run_key(rec):
    return rec["cond"], rec["seed"], rec["source"]


def load_rows():
    unified = json.loads(UNIFIED.read_text())
    rows = []
    for rec in unified["records"]:
        if rec.get("gap") is None:
            continue
        rho = rec.get("rho")
        sigma = float(rec["spread"])
        q = float(rec["pool_mean"])
        # The binary ceiling on within-prompt SD at this pool mean. Only
        # meaningful for binary-scored axes, which is every axis here except the
        # continuous self-description one; that one is kept but flagged.
        ceiling = math.sqrt(max(q * (1.0 - q), 0.0))
        rows.append({
            "run": run_key(rec),
            "round": int(rec["round"]),
            "gap": float(rec["gap"]),
            "rho": None if rho is None else float(rho),
            "sigma": sigma,
            "pool_mean": q,
            "binary_ceiling": ceiling,
            "residual_spread": (sigma / ceiling) if ceiling > 1e-9 else None,
            "binary_axis": float(rec.get("binary_score_fraction", 1.0)) >= 0.999,
            "organism": rec["organism"],
            "axis": rec["axis"],
            "judge": rec["judge"],
        })
    return rows


def summarise_round(rows, t):
    sub = [r for r in rows if r["round"] == t]
    if not sub:
        return None
    with_rho = [r for r in sub if r["rho"] is not None]
    resid = [r["residual_spread"] for r in sub
             if r["residual_spread"] is not None]
    return {
        "n": len(sub),
        "n_runs": len({r["run"] for r in sub}),
        "mean_abs_gap": float(np.mean([abs(r["gap"]) for r in sub])),
        "mean_sigma": float(np.mean([r["sigma"] for r in sub])),
        "mean_abs_rho": (float(np.mean([abs(r["rho"]) for r in with_rho]))
                         if with_rho else None),
        "mean_binary_ceiling": float(np.mean([r["binary_ceiling"] for r in sub])),
        "mean_residual_spread": float(np.mean(resid)) if resid else None,
        "n_zero_spread": sum(1 for r in sub if r["sigma"] < 1e-9),
        "fraction_zero_spread": float(np.mean([r["sigma"] < 1e-9 for r in sub])),
        "mean_pool_mean": float(np.mean([r["pool_mean"] for r in sub])),
        "mean_distance_to_nearest_rail": float(np.mean(
            [min(r["pool_mean"], 1.0 - r["pool_mean"]) for r in sub])),
    }


def log_decomposition(rows, first=1, last=HORIZON, draws=BOOTSTRAP_DRAWS,
                      seed=SEED):
    """Split the fall in log|gap| into agreement and spread, PAIRED WITHIN RUNS.

    An unpaired version of this is wrong here, and wrong in the direction that
    matters. Rounds with zero spread or zero agreement have no logarithm, and
    they are not missing at random: they are the pools that collapsed, and they
    get commoner as a run proceeds (1.7% of rounds at round 1, 11.9% by round 4).
    Comparing a round-1 mean to a round-4 mean therefore compares all runs to the
    subset that had not yet collapsed, which makes the gap look like it GREW.

    Pairing within runs removes that. Each run contributes one difference, and a
    run is used only if both endpoints are usable, with the excluded ones counted.

    NOTE WHICH SPLIT IS AN IDENTITY AND WHICH IS NOT. gap = rho * sigma is a
    MODEL, fitted at R^2 0.80 over 367 rounds, not a definition -- so

        log|gap_last| - log|gap_first|
            ~= (log|rho| difference) + (log sigma difference)

    holds only up to that model's own error, and the leftover is reported as
    `model_error_gap_minus_rho_minus_sigma` rather than as a failed check. The
    spread split IS an identity, true by construction, because for a
    binary-scored axis sigma = residual * sqrt(q(1-q)):

        log sigma_last - log sigma_first
            = (log ceiling_last - log ceiling_first)      <- forced by the rail
            + (log residual_last - log residual_first)    <- genuine variety loss
    """
    by_run = defaultdict(dict)
    for r in rows:
        by_run[r["run"]][r["round"]] = r

    usable, excluded = [], 0
    for key, per_round in by_run.items():
        a, b = per_round.get(first), per_round.get(last)
        if a is None or b is None:
            continue
        vals = [a, b]
        if any(v["rho"] is None or abs(v["rho"]) < 1e-9 or v["sigma"] < 1e-9
               or abs(v["gap"]) < 1e-9 or v["binary_ceiling"] < 1e-9
               for v in vals):
            excluded += 1
            continue
        usable.append((a, b))
    if len(usable) < 8:
        return {"insufficient": True, "n_usable": len(usable),
                "n_excluded_for_zero": excluded}

    def deltas(pair):
        a, b = pair
        return {
            "gap": math.log(abs(b["gap"])) - math.log(abs(a["gap"])),
            "rho": math.log(abs(b["rho"])) - math.log(abs(a["rho"])),
            "sigma": math.log(b["sigma"]) - math.log(a["sigma"]),
            "ceiling": math.log(b["binary_ceiling"]) - math.log(a["binary_ceiling"]),
            "residual": math.log(b["residual_spread"])
                        - math.log(a["residual_spread"]),
        }

    d = [deltas(p) for p in usable]
    point = {k: float(np.mean([x[k] for x in d])) for k in d[0]}

    rng = np.random.default_rng(seed)
    boot = defaultdict(list)
    for _ in range(draws):
        idx = rng.integers(0, len(d), len(d))
        for k in point:
            boot[k].append(float(np.mean([d[i][k] for i in idx])))
    ci = {k: [float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))]
          for k, v in boot.items()}

    return {
        "first_round": first,
        "last_round": last,
        "n_runs_usable": len(usable),
        "n_runs_excluded_for_zero_rho_sigma_or_gap": excluded,
        "mean_delta_log": point,
        "ci": ci,
        "model_error_gap_minus_rho_minus_sigma":
            point["gap"] - point["rho"] - point["sigma"],
        "identity_check_sigma_minus_ceiling_minus_residual":
            point["sigma"] - point["ceiling"] - point["residual"],
        "share_of_sigma_decline_forced_by_the_rail":
            (point["ceiling"] / point["sigma"]) if abs(point["sigma"]) > 1e-12
            else None,
    }


def bootstrap_round_stat(rows, t, key, draws=BOOTSTRAP_DRAWS, seed=SEED):
    by_run = defaultdict(list)
    for r in rows:
        if r["round"] == t and r.get(key) is not None:
            by_run[r["run"]].append(r[key])
    keys = list(by_run)
    if len(keys) < 5:
        return None
    rng = np.random.default_rng(seed)
    vals = []
    for _ in range(draws):
        sample = []
        for i in rng.integers(0, len(keys), len(keys)):
            sample.extend(by_run[keys[i]])
        vals.append(float(np.mean(sample)))
    arr = np.array(vals)
    return [float(np.percentile(arr, 2.5)), float(np.percentile(arr, 97.5))]


def main():
    rows = load_rows()
    binary_rows = [r for r in rows if r["binary_axis"]]

    per_round = {f"round{t}": summarise_round(rows, t)
                 for t in range(1, HORIZON + 1)}
    per_round_binary = {f"round{t}": summarise_round(binary_rows, t)
                        for t in range(1, HORIZON + 1)}

    residual_ci = {f"round{t}": bootstrap_round_stat(binary_rows, t,
                                                     "residual_spread")
                   for t in range(1, HORIZON + 1)}
    sigma_ci = {f"round{t}": bootstrap_round_stat(binary_rows, t, "sigma")
                for t in range(1, HORIZON + 1)}

    # ---- does the gap erode, or does it fail? ----
    collapse = {}
    for t in range(1, HORIZON + 1):
        sub = [r for r in binary_rows if r["round"] == t]
        if not sub:
            continue
        alive = [r for r in sub if r["sigma"] > 1e-9]
        collapse[f"round{t}"] = {
            "n": len(sub),
            "mean_abs_gap_all_rows": float(np.mean([abs(r["gap"]) for r in sub])),
            "mean_abs_gap_excluding_zero_spread": (
                float(np.mean([abs(r["gap"]) for r in alive])) if alive else None),
            "fraction_zero_spread": float(np.mean([r["sigma"] < 1e-9 for r in sub])),
        }
    collapse["reading"] = (
        "If the mean gap falls across rounds while the mean gap AMONG POOLS THAT "
        "STILL HAVE SPREAD does not, then the supply of selectable variation is "
        "not eroding smoothly -- individual runs are hitting exactly zero and "
        "dragging the average down. That is a failure process, not a decay "
        "process, and it has a different fix.")

    result = {
        "description": (
            "Decomposes the round-over-round decline in the selection gap into "
            "agreement (the judge losing grip on the value axis) and spread (the "
            "pool losing variety), and then asks how much of the spread decline "
            "is forced by binary scoring, where within-prompt SD is capped at "
            "sqrt(q(1-q)) and must vanish as the pool mean approaches a rail."
        ),
        "n_rows": len(rows),
        "n_binary_axis_rows": len(binary_rows),
        "per_round_all_axes": per_round,
        "per_round_binary_axes_only": per_round_binary,
        "mean_residual_spread_ci": residual_ci,
        "mean_sigma_ci": sigma_ci,
        "erosion_versus_collapse": collapse,
        "log_decomposition_round1_to_round4": log_decomposition(rows),
        "log_decomposition_binary_axes_only": log_decomposition(binary_rows),
        "settings": {"bootstrap_draws": BOOTSTRAP_DRAWS,
                     "clustering": "whole runs, keyed by (cond, seed, source)",
                     "residual_spread": "sigma / sqrt(q(1-q)), the fraction of "
                                        "the binary ceiling actually used"},
    }
    OUT.write_text(json.dumps(result, indent=2) + "\n")

    print("PER ROUND (binary-scored axes only, n = %d rows)" % len(binary_rows))
    print(f"  {'':8s} {'n':>4s} {'|gap|':>7s} {'sigma':>7s} {'|rho|':>7s} "
          f"{'ceiling':>8s} {'sigma/ceil':>11s} {'0-spread':>9s} {'to rail':>8s}")
    for t in range(1, HORIZON + 1):
        v = per_round_binary[f"round{t}"]
        if not v:
            continue
        rs = v["mean_residual_spread"]
        ci = residual_ci[f"round{t}"]
        print(f"  round{t}   {v['n']:4d} {v['mean_abs_gap']:7.4f} "
              f"{v['mean_sigma']:7.4f} "
              f"{(v['mean_abs_rho'] if v['mean_abs_rho'] is not None else float('nan')):7.4f} "
              f"{v['mean_binary_ceiling']:8.4f} "
              f"{(rs if rs is not None else float('nan')):11.4f} "
              f"{v['fraction_zero_spread']:9.3f} "
              f"{v['mean_distance_to_nearest_rail']:8.4f}")
        if ci:
            print(f"  {'':8s} {'':4s} {'':7s} {'':7s} {'':7s} {'':8s} "
                  f"[{ci[0]:.3f},{ci[1]:.3f}]")
    print()
    print("EROSION OR FAILURE? (binary-scored axes)")
    print(f"  {'':8s} {'mean|gap| all':>14s} {'mean|gap| alive':>16s} "
          f"{'zero-spread':>12s}")
    for t in range(1, HORIZON + 1):
        c = collapse.get(f"round{t}")
        if not c:
            continue
        print(f"  round{t}   {c['mean_abs_gap_all_rows']:14.4f} "
              f"{c['mean_abs_gap_excluding_zero_spread']:16.4f} "
              f"{c['fraction_zero_spread']:12.3f}")
    print()
    for label, key in (("all axes", "log_decomposition_round1_to_round4"),
                       ("binary axes only", "log_decomposition_binary_axes_only")):
        d = result[key]
        if not d or d.get("insufficient"):
            print(f"PAIRED LOG DECOMPOSITION ({label}): insufficient")
            continue
        m, c = d["mean_delta_log"], d["ci"]
        print(f"PAIRED LOG DECOMPOSITION round 1 -> round {d['last_round']} "
              f"({label})")
        print(f"  {d['n_runs_usable']} runs paired; "
              f"{d['n_runs_excluded_for_zero_rho_sigma_or_gap']} excluded because "
              f"an endpoint had zero spread, agreement or gap")
        for k in ("gap", "rho", "sigma", "ceiling", "residual"):
            print(f"    delta log {k:9s} {m[k]:+.4f} [{c[k][0]:+.4f}, {c[k][1]:+.4f}]")
        print(f"  gap = rho*sigma is a MODEL (R2 0.80), not a definition: its "
              f"leftover here is {d['model_error_gap_minus_rho_minus_sigma']:+.3f}")
        print(f"  sigma = ceiling*residual IS an identity: check "
              f"{d['identity_check_sigma_minus_ceiling_minus_residual']:+.2e}")
        sh = d["share_of_sigma_decline_forced_by_the_rail"]
        if sh is not None:
            print(f"  share of the spread decline forced by the binary rail: "
                  f"{sh:.1%}")
        print()
    print(f"wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
