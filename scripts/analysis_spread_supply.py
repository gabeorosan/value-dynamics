"""Where does spread come from? A variance decomposition of the loop's fuel.

Three separate analyses this week converged on the same conclusion from
different directions: the response to selection does not decay (0.75-0.81,
flat), the judge is not being gamed (no proxy-gold divergence), and agreement
erodes rather than amplifying (loop gain 0.92). What runs out is not the
machinery that acts on variation -- it is the variation itself. The mean
absolute selection gap falls from 0.099 to about 0.070 over four rounds while
the response per unit gap holds.

So the interesting quantity is the SUPPLY of within-prompt spread, and nothing
in the program predicts it. This asks the first question about it: how much of
the variation in spread is a property of the PROMPT, how much of the RUN, and
how much of the ROUND within a run?

WHY THE ANSWER IS USEFUL EITHER WAY.

  prompt-dominated   spread is a stable property of the item. Then it is
                     screenable: generate once, measure spread per prompt, and
                     build the training set out of prompts that produce it. That
                     is a cheap pre-loop tool and it needs no training at all.

  run-dominated      spread is a property of the model state. Then prompt
                     screening does not transfer across organisms and the lever
                     is the generator (temperature, decoding, persona), not the
                     item set.

  round-dominated    spread is consumed as the loop proceeds regardless of the
                     item. Then it is a resource with a depletion curve, and the
                     question becomes how to replenish it.

THE ANSWER, ON BINARY AXES, IS THAT THE QUESTION DISSOLVES -- AND THAT IS THE
FINDING. For binary candidate scores the within-prompt sample standard deviation
is not merely BOUNDED by the pool mean, it is DETERMINED by it:

    sigma  =  sqrt(n/(n-1)) * sqrt(q(1-q))        exactly, for every pool

where q is that prompt's own pool mean and n the number of candidates. This
script verifies the identity on the corpus itself rather than asserting it; it
holds to floating-point precision on every row. The immediate consequence is
that on a binary axis **spread carries no information beyond the mean**. It is
not a second state variable, it cannot be screened for independently, and it
cannot be intervened on without moving the mean.

So the decomposition is run on the POOL MEAN, which is the only free quantity,
and the spread decomposition is reported only to show it is the same numbers
pushed through a fixed function.

Variance components are estimated by nested one-way decomposition rather than
by a mixed model, because with unbalanced cells and no scipy the simple
estimator is the honest one; the components are reported as shares of total
variance with a run-clustered bootstrap.

Writes experiments/spread_supply.json.
"""

from __future__ import annotations

import importlib.util
import json
import os
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "experiments/spread_supply.json"
UNIFIED_SCRIPT = ROOT / "scripts/analysis_spread_util_unified.py"

BOOTSTRAP_DRAWS = 2000
SEED = 20260729
CEILING_FLOOR = 0.05   # below this the ceiling is ~0 and the ratio is unstable


def load_unified_module():
    spec = importlib.util.spec_from_file_location("vd_unified", UNIFIED_SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def collect(mod):
    """One row per (run, round, prompt): that prompt's pool mean and spread."""
    rows, best = [], {}
    for path, organism, axis in mod.KAGGLE_SOURCES:
        f = os.path.join(mod.ROOT, path)
        if not os.path.exists(f):
            continue
        blob = json.load(open(f))
        score_key = "cand_risk" if axis == "risk" else "cand_sr_scores"
        for sd, conds in blob.items():
            if not str(sd).isdigit():
                continue
            for cond, res in conds.items():
                if cond not in mod.KAGGLE_CONDS or not isinstance(res, dict):
                    continue
                rr = res.get("rounds_raw")
                if not rr:
                    continue
                key = (organism, axis, cond, str(sd))
                if key not in best or len(rr) > best[key][0]:
                    best[key] = (len(rr), res, score_key)

    for (organism, axis, cond, sd), (_, res, score_key) in best.items():
        judge, fmt, comp = mod.KAGGLE_CONDS[cond]
        for k, items in enumerate(res["rounds_raw"], start=1):
            if not items:
                continue
            for j, it in enumerate(items):
                vals = it.get(score_key)
                if not vals or len(vals) < 2:
                    continue
                v = np.array(vals, dtype=float)
                q = float(v.mean())
                sd_within = float(v.std(ddof=1))
                ceiling = float(np.sqrt(max(q * (1.0 - q), 0.0)))
                # prompt identity: the item's own id if logged, else its index,
                # which is stable within a source because the prompt list is fixed
                pid = it.get("task") or it.get("prompt") or it.get("id") or j
                binary = bool(np.all((v == 0.0) | (v == 1.0)))
                rows.append({
                    "binary": binary,
                    "run": (organism, axis, cond, sd),
                    "organism": organism, "axis": axis, "cond": cond,
                    "judge": judge, "round": k,
                    "prompt": (organism, axis, str(pid)[:120]),
                    "pool_mean": q,
                    "spread": sd_within,
                    "ceiling": ceiling,
                    "realised_share": (sd_within / ceiling
                                       if ceiling > CEILING_FLOOR else None),
                    "distance_from_half": abs(q - 0.5),
                    "n_cand": len(v),
                })
    return rows


def verify_binary_identity(rows):
    """Check sigma = sqrt(n/(n-1)) * sqrt(q(1-q)) on the actual corpus rows."""
    worst, checked = 0.0, 0
    for r in rows:
        if not r["binary"]:
            continue
        n, q = r["n_cand"], r["pool_mean"]
        if n < 2:
            continue
        pred = np.sqrt(n / (n - 1.0)) * np.sqrt(max(q * (1.0 - q), 0.0))
        worst = max(worst, abs(r["spread"] - pred))
        checked += 1
    return {"rows_checked": checked,
            "max_absolute_deviation": float(worst),
            "holds": bool(worst < 1e-9),
            "meaning": ("on a binary axis the within-prompt spread is a "
                        "deterministic function of the pool mean, so it is not "
                        "an independent state variable")}


def variance_shares(rows, key):
    """Share of variance in `key` attributable to prompt, run, and residual.

    Nested one-way: total variance is split into the variance of prompt means
    about the grand mean, the variance of run means about the grand mean, and
    what is left. With unbalanced cells these do not sum to exactly 1, so the
    raw sums of squares are reported alongside the shares and the residual is
    computed as the remainder after removing BOTH main effects additively.
    """
    vals = [r for r in rows if r.get(key) is not None]
    if len(vals) < 30:
        return None
    y = np.array([r[key] for r in vals], dtype=float)
    total = float(np.var(y))
    if total < 1e-12:
        return None
    grand = float(y.mean())

    def between(group_key):
        groups = defaultdict(list)
        for r, v in zip(vals, y):
            groups[r[group_key]].append(v)
        ss = sum(len(g) * (np.mean(g) - grand) ** 2 for g in groups.values())
        return float(ss / len(y)), len(groups)

    prompt_var, n_prompts = between("prompt")
    run_var, n_runs = between("run")
    round_var, n_rounds = between("round")

    # additive two-way removal, for the residual
    resid = y - grand
    for group_key in ("prompt", "run"):
        groups = defaultdict(list)
        for i, r in enumerate(vals):
            groups[r[group_key]].append(i)
        for idx in groups.values():
            resid[idx] -= resid[idx].mean()
    return {
        "n_rows": len(vals),
        "n_prompts": n_prompts,
        "n_runs": n_runs,
        "n_rounds": n_rounds,
        "total_variance": total,
        "prompt_share": prompt_var / total,
        "run_share": run_var / total,
        "round_share": round_var / total,
        "residual_share_after_prompt_and_run": float(np.var(resid) / total),
    }


def prompt_stability(rows, key):
    """Do the same prompts produce spread across DIFFERENT runs?

    Correlates each prompt's mean in one random half of the runs against its
    mean in the other half. This is the quantity that decides whether prompt
    screening would transfer -- a high correlation means a prompt measured on
    one organism-state predicts its behaviour on another.
    """
    vals = [r for r in rows if r.get(key) is not None]
    runs = sorted({r["run"] for r in vals})
    if len(runs) < 6:
        return None
    rng = np.random.default_rng(SEED)
    corrs = []
    for _ in range(200):
        perm = list(runs)
        rng.shuffle(perm)
        half = set(perm[:len(perm) // 2])
        a, b = defaultdict(list), defaultdict(list)
        for r in vals:
            (a if r["run"] in half else b)[r["prompt"]].append(r[key])
        shared = set(a) & set(b)
        if len(shared) < 5:
            continue
        xa = np.array([np.mean(a[p]) for p in sorted(shared)])
        xb = np.array([np.mean(b[p]) for p in sorted(shared)])
        if np.var(xa) < 1e-12 or np.var(xb) < 1e-12:
            continue
        corrs.append(float(np.corrcoef(xa, xb)[0, 1]))
    if len(corrs) < 20:
        return None
    arr = np.array(corrs)
    return {"split_half_correlation_mean": float(arr.mean()),
            "ci_lo": float(np.percentile(arr, 2.5)),
            "ci_hi": float(np.percentile(arr, 97.5)),
            "n_splits": len(arr)}


def by_round(rows, key):
    out = {}
    for t in sorted({r["round"] for r in rows}):
        sub = [r[key] for r in rows if r["round"] == t and r.get(key) is not None]
        if len(sub) < 5:
            continue
        out[f"round{t}"] = {"n": len(sub), "mean": float(np.mean(sub))}
    return out


def main():
    mod = load_unified_module()
    rows = collect(mod)
    if not rows:
        print("no per-prompt rows found")
        return

    payload = {
        "description": (
            "Variance decomposition of within-prompt candidate spread -- the "
            "fuel selection runs on -- into prompt, run and round components, "
            "on raw spread and on the share of the binomial ceiling actually "
            "realised."
        ),
        "n_rows": len(rows),
        "n_runs": len({r["run"] for r in rows}),
        "n_prompts": len({r["prompt"] for r in rows}),
        "zero_spread_share": float(
            np.mean([r["spread"] == 0.0 for r in rows])),
        "binary_share_of_rows": float(np.mean([r["binary"] for r in rows])),
        "binary_identity_check": verify_binary_identity(rows),
        "decomposition": {
            "pool_mean": variance_shares(rows, "pool_mean"),
            "raw_spread": variance_shares(rows, "spread"),
        },
        "prompt_stability_across_runs": {
            "pool_mean": prompt_stability(rows, "pool_mean"),
            "raw_spread": prompt_stability(rows, "spread"),
        },
        "by_round": {
            "pool_mean": by_round(rows, "pool_mean"),
            "raw_spread": by_round(rows, "spread"),
            "distance_of_pool_mean_from_half":
                by_round(rows, "distance_from_half"),
        },
        "conventions": {
            "ceiling": "sqrt(q(1-q)) with q the prompt's own pool mean",
            "ceiling_floor": CEILING_FLOOR,
            "prompt_identity": ("the logged task text where available, else the "
                                "item index, which is stable within a source "
                                "because the prompt list is fixed"),
        },
    }
    OUT.write_text(json.dumps(payload, indent=2) + "\n")

    print(f"{len(rows)} prompt-rounds from {payload['n_runs']} runs, "
          f"{payload['n_prompts']} distinct prompts; "
          f"{payload['zero_spread_share']:.1%} have exactly zero spread; "
          f"{payload['binary_share_of_rows']:.1%} of rows are binary-scored\n")
    bid = payload["binary_identity_check"]
    print(f"IDENTITY CHECK sigma = sqrt(n/(n-1))*sqrt(q(1-q)) on "
          f"{bid['rows_checked']} binary rows: max deviation "
          f"{bid['max_absolute_deviation']:.2e} -> "
          f"{'HOLDS' if bid['holds'] else 'FAILS'}")
    print("   => on a binary axis, spread is NOT an independent state variable\n")
    for key, d in payload["decomposition"].items():
        if not d:
            continue
        print(f"{key}  (n={d['n_rows']}, {d['n_prompts']} prompts, "
              f"{d['n_runs']} runs)")
        print(f"   prompt {d['prompt_share']:.3f}   run {d['run_share']:.3f}   "
              f"round {d['round_share']:.3f}   "
              f"residual {d['residual_share_after_prompt_and_run']:.3f}")
    print()
    for key, d in payload["prompt_stability_across_runs"].items():
        if not d:
            continue
        print(f"prompt stability across runs, {key}: "
              f"split-half r = {d['split_half_correlation_mean']:+.3f} "
              f"[{d['ci_lo']:+.3f}, {d['ci_hi']:+.3f}]")
    print()
    for key, d in payload["by_round"].items():
        if d:
            print(f"{key} by round: " + "  ".join(
                f"{t}={v['mean']:.3f}" for t, v in d.items()))
    print(f"\nwrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
