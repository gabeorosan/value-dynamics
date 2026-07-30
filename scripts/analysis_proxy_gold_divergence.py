"""Does the judge's score keep rising after the value stops moving?

This is Gao, Schulman & Hilton's proxy-versus-gold diagnostic
(arXiv 2210.10760) transplanted onto our loop, and the 2026-07-28
overoptimisation review named it as the one measurement that separates two
explanations of why runs level off:

  OVEROPTIMISATION   the loop keeps buying judge score with real value, so the
                     PROXY (mean judge score of the organism's own candidates)
                     keeps climbing while the GOLD (the held-out value) flattens
                     or reverses. Goodhart, in the original sense.

  REPLICATOR CEILING the loop runs out of selectable variation. Proxy and gold
                     flatten TOGETHER, because there is nothing left to select
                     between. Ferbach et al. (arXiv 2407.09499, Theorem 2.1)
                     predict exactly this, and predict it happens short of the
                     value rails, at the top reward level set reachable from the
                     initial support.

"The runs level off short of the rails" does not distinguish these -- the
replicator account predicts that too. The divergence between the two series
does.

WHAT IS COMPUTED, per round, from the raw per-candidate logs:

    proxy_pool   mean judge score over ALL candidates
    proxy_kept   mean judge score over the KEPT candidates
    gold_pool    mean value score over all candidates
    gold_kept    mean value score over the kept candidates
    v            the held-out value measurement (the real gold)

and then, with run fixed effects, the per-round slope of each series. The
diagnostic is the difference of slopes: proxy rising while gold is flat is
overoptimisation; both flat together is exhaustion.

GOLD MUST BE SIGN-ALIGNED, AND THE FIRST VERSION OF THIS SCRIPT GOT IT WRONG.
The judge score is direction-free -- higher always means more judge-preferred.
The raw value is not: some runs are pushed up and some down, so pooling them
makes the gold slope average to about zero by CANCELLATION rather than by
saturation, and the divergence test then compares a real slope against an
artefact. Each run's direction is therefore taken from the sign of its round-one
selection gap (kept value mean minus pool value mean) -- the direction the judge
actually revealed -- and gold is measured along it. Runs whose round-one gap is
too small to give a reliable sign are reported separately rather than assigned
one.

SCOPE, AND WHY IT IS NARROW.

  - FROZEN judges only. An evolving self-judge is a moving ruler: its scores are
    not comparable across rounds, so a rising proxy could be the judge changing
    rather than the candidates improving.
  - ORACLE judges excluded. Their judge score IS the value score by
    construction, so proxy and gold are the same series and the diagnostic is
    vacuous.
  - Judge scores are comparable across rounds only up to the judge's own
    calibration drift on a changing candidate distribution. This is the main
    threat to the result and cannot be removed from committed data; a rising
    proxy could in principle be the frozen judge scoring a drifting distribution
    more generously. The pool-mean comparison below is the least
    drift-sensitive version available.

Writes experiments/proxy_gold_divergence.json.
"""

from __future__ import annotations

import importlib.util
import json
import os
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "experiments/proxy_gold_divergence.json"
UNIFIED_SCRIPT = ROOT / "scripts/analysis_spread_util_unified.py"

EXCLUDE_JUDGES = {"score oracle", "self", "schedule"}
BOOTSTRAP_DRAWS = 4000
SEED = 20260729


def load_unified_module():
    """Reuse the corpus builder's source lists rather than duplicating them."""
    spec = importlib.util.spec_from_file_location("vd_unified", UNIFIED_SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def round_series(items, score_key, judge_key="scores_arm"):
    """Pool and kept means of the value score and the judge score, one round."""
    gp, gk, pp, pk, n_items = [], [], [], [], 0
    for it in items:
        vals = it.get(score_key)
        judge = it.get(judge_key)
        kept = it.get("kept_idx")
        if not vals or not judge or not kept:
            continue
        if len(judge) != len(vals):
            continue
        idx = [i for i in kept if 0 <= i < len(vals)]
        if not idx:
            continue
        n_items += 1
        gp.append(float(np.mean(vals)))
        gk.append(float(np.mean([vals[i] for i in idx])))
        pp.append(float(np.mean(judge)))
        pk.append(float(np.mean([judge[i] for i in idx])))
    if n_items == 0:
        return None
    return {
        "n_items": n_items,
        "gold_pool": float(np.mean(gp)), "gold_kept": float(np.mean(gk)),
        "proxy_pool": float(np.mean(pp)), "proxy_kept": float(np.mean(pk)),
    }


def collect(mod):
    rows = []
    best = {}
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
                traj = res.get("traj")
                if not rr or not traj:
                    continue
                key = (organism, axis, cond, str(sd))
                if key not in best or len(rr) > best[key][0]:
                    best[key] = (len(rr), res, traj, score_key)

    for (organism, axis, cond, sd), (_, res, traj, score_key) in best.items():
        judge, fmt, comp = mod.KAGGLE_CONDS[cond]
        if judge in EXCLUDE_JUDGES:
            continue
        rr = res["rounds_raw"]
        # direction the judge revealed in round one, from the value gap it took
        first = round_series(rr[0], score_key) if rr and rr[0] else None
        direction, direction_strength = 0.0, 0.0
        if first is not None:
            g1 = first["gold_kept"] - first["gold_pool"]
            direction_strength = abs(g1)
            direction = 1.0 if g1 > 0 else (-1.0 if g1 < 0 else 0.0)
        for k in range(1, len(rr) + 1):
            if k >= len(traj) or traj[k] is None or traj[k - 1] is None:
                continue
            if not rr[k - 1]:
                continue
            s = round_series(rr[k - 1], score_key)
            if s is None:
                continue
            rows.append({
                "run": (organism, axis, cond, sd),
                "organism": organism, "axis": axis, "cond": cond,
                "judge": judge, "round": k,
                "v_before": float(traj[k - 1]), "v_after": float(traj[k]),
                "direction": direction,
                "direction_strength": direction_strength,
                **s,
                # gold measured along the direction the judge revealed
                "gold_pool_aligned": direction * s["gold_pool"],
                "gold_kept_aligned": direction * s["gold_kept"],
                "v_aligned": direction * float(traj[k - 1]),
            })
    return rows


def within_run_slope(rows, key):
    """Per-round slope of a series, with run fixed effects."""
    by_run = defaultdict(list)
    for r in rows:
        by_run[r["run"]].append(r)
    xs, ys = [], []
    for run_rows in by_run.values():
        if len(run_rows) < 2:
            continue
        t = np.array([r["round"] for r in run_rows], dtype=float)
        y = np.array([r[key] for r in run_rows], dtype=float)
        xs.append(t - t.mean())
        ys.append(y - y.mean())
    if not xs:
        return None
    x = np.concatenate(xs)
    y = np.concatenate(ys)
    if np.var(x) < 1e-12:
        return None
    return float(np.sum(x * y) / np.sum(x * x))


def divergence(rows):
    p = within_run_slope(rows, "proxy_pool")
    g = within_run_slope(rows, "gold_pool_aligned")
    if p is None or g is None:
        return None
    return p - g


def cluster_bootstrap(rows, stat, draws=BOOTSTRAP_DRAWS, seed=SEED):
    by_run = defaultdict(list)
    for r in rows:
        by_run[r["run"]].append(r)
    keys = list(by_run)
    if len(keys) < 3:
        return None
    rng = np.random.default_rng(seed)
    vals = []
    for _ in range(draws):
        sample = []
        for i in rng.integers(0, len(keys), size=len(keys)):
            sample.extend(by_run[keys[i]])
        v = stat(sample)
        if v is not None and np.isfinite(v):
            vals.append(v)
    if len(vals) < 100:
        return None
    arr = np.array(vals)
    return {"ci_lo": float(np.percentile(arr, 2.5)),
            "ci_hi": float(np.percentile(arr, 97.5)),
            "se": float(arr.std(ddof=1))}


def analyse(rows, label):
    if len({r["run"] for r in rows}) < 3:
        return None
    out = {"group": label,
           "n_rounds": len(rows),
           "n_runs": len({r["run"] for r in rows})}
    for key in ("proxy_pool", "proxy_kept", "gold_pool", "gold_kept",
                "gold_pool_aligned", "gold_kept_aligned", "v_aligned"):
        out[f"slope_{key}"] = within_run_slope(rows, key)
        out[f"slope_{key}_ci"] = cluster_bootstrap(
            rows, lambda rs, k=key: within_run_slope(rs, k))
    out["divergence_proxy_minus_gold"] = divergence(rows)
    out["divergence_ci"] = cluster_bootstrap(rows, divergence)
    ci = out["divergence_ci"]
    out["verdict"] = (
        "overoptimisation (proxy rises relative to gold)"
        if ci and ci["ci_lo"] > 0 else
        "gold rises relative to proxy" if ci and ci["ci_hi"] < 0 else
        "no separation")
    by_round = {}
    for t in sorted({r["round"] for r in rows}):
        sub = [r for r in rows if r["round"] == t]
        by_round[f"round{t}"] = {
            "n": len(sub),
            "proxy_pool": float(np.mean([r["proxy_pool"] for r in sub])),
            "gold_pool": float(np.mean([r["gold_pool"] for r in sub])),
            "gold_pool_aligned": float(np.mean(
                [r["gold_pool_aligned"] for r in sub])),
            "v_before": float(np.mean([r["v_before"] for r in sub])),
        }
    out["by_round_means"] = by_round
    return out


def main():
    mod = load_unified_module()
    rows = collect(mod)
    if not rows:
        print("no usable rows -- per-candidate judge scores not found")
        return

    signed = [r for r in rows if r["direction"] != 0.0]
    strong = [r for r in signed if r["direction_strength"] >= 0.02]
    groups = {"frozen non-oracle judges (signed)": signed,
              "signed, round-1 gap >= 0.02": strong}
    for org in sorted({r["organism"] for r in signed}):
        groups[f"signed, {org}"] = [r for r in signed if r["organism"] == org]

    results = {}
    for label, sub in groups.items():
        a = analyse(sub, label)
        if a:
            results[label] = a

    payload = {
        "description": (
            "Gao-style proxy-versus-gold divergence for the selection loop. "
            "Separates overoptimisation (judge score keeps climbing while the "
            "held-out value flattens) from replicator exhaustion (both flatten "
            "together). Frozen non-oracle judges only."
        ),
        "excluded_judges": sorted(EXCLUDE_JUDGES),
        "n_rounds": len(rows),
        "n_runs": len({r["run"] for r in rows}),
        "groups": results,
        "threat": ("judge scores are comparable across rounds only up to the "
                   "frozen judge's own calibration drift on a changing candidate "
                   "distribution; a rising proxy could in principle be that "
                   "rather than genuinely better-scoring candidates"),
    }
    OUT.write_text(json.dumps(payload, indent=2) + "\n")

    print(f"{len(rows)} rounds from {len({r['run'] for r in rows})} runs "
          f"(frozen non-oracle judges)\n")
    for label, r in results.items():
        print(f"{label}  (n={r['n_rounds']}, runs={r['n_runs']})")
        for key in ("proxy_pool", "gold_pool", "gold_pool_aligned",
                    "gold_kept_aligned", "v_aligned"):
            ci = r[f"slope_{key}_ci"]
            s = r[f"slope_{key}"]
            print(f"   slope {key:12s} {s:+.4f}"
                  + (f" [{ci['ci_lo']:+.4f}, {ci['ci_hi']:+.4f}]" if ci else ""))
        d, dci = r["divergence_proxy_minus_gold"], r["divergence_ci"]
        print(f"   divergence proxy-gold {d:+.4f}"
              + (f" [{dci['ci_lo']:+.4f}, {dci['ci_hi']:+.4f}]" if dci else "")
              + f"  -> {r['verdict']}")
        print("   by round: " + "  ".join(
            f"r{t[-1]} proxy {v['proxy_pool']:.3f} "
            f"gold* {v['gold_pool_aligned']:+.3f}"
            for t, v in r["by_round_means"].items()))
        print()
    print(f"wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
