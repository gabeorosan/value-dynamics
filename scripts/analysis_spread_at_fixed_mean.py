"""Restore candidate spread WITHOUT moving the pool mean, using logged pools.

THE PROBLEM.  On a binary-scored axis the spread of a round's candidates is
largely pinned by that round's pool mean (report_spread_is_not_a_free_variable.md:
one coefficient against the ceiling sqrt(q(1-q)) accounts for 85.9% of the
variance in spread).  That makes it hard to say spread is a lever in its own
right rather than a restatement of where the value already sits, and it makes the
"restoring spread rescued a stuck run" intervention ambiguous, because adding an
outside candidate source moves the pool mean too.

THE LOOPHOLE.  The pool mean does NOT determine spread.  By the law of total
variance,

    within-prompt variance  =  q(1-q)  -  between-prompt variance

so at a FIXED overall pool mean q, within-prompt spread still moves freely
depending on how the 1s are distributed ACROSS prompts.  Concentrate them (some
prompts all-1, some all-0) and within-prompt spread goes to zero.  Even them out
across prompts and it goes to its maximum.  Same mean, same candidates, different
arrangement.

THE EXPERIMENT, WHICH COSTS NOTHING.  Every logged round gives, per prompt, six
candidate answers with (a) a value score recoverable from the answer text by the
committed parser and (b) the judge's own score, logged at the time.  So we can
build two sub-pools of the SAME size from the SAME candidates with the SAME
overall pool mean, one arranged for high within-prompt spread and one for low,
and then run the real selection rule on the real judge scores.

    arm HIGH : choose m of the 6 candidates per prompt to MAXIMIZE mean
               within-prompt spread, subject to a fixed total number of 1s
    arm LOW  : same, MINIMIZING it, at the identical total

Both arms are solved exactly by a knapsack over prompts (the per-prompt choice is
just how many 1s to take, and the totals are small integers).  Selection then
keeps the top 2 by logged judge score within each prompt.

WHAT IT CAN AND CANNOT SHOW.  This is counterfactual SELECTION on real judge
preferences, not counterfactual TRAINING: it establishes whether spread drives the
selection gap at a fixed pool mean.  It does not by itself show the value then
moves; that link is the separately established gap-to-movement relation.  Stating
the chain honestly: spread -> gap here, gap -> movement elsewhere.

PREDICTION (recorded before reading the output).  gap_HIGH exceeds gap_LOW, by
roughly the judge's agreement times the spread difference.  If the two arms give
the same gap despite very different spread, the spread term in the movement law is
not doing work at fixed mean, and that would be a genuine negative result.
"""

import json
import math
import os
import re
import statistics
from collections import defaultdict

OUT = "experiments/spread_at_fixed_mean.json"
M_KEEP = 2          # candidates kept per prompt, matching the loops
SUBPOOL = 4         # candidates offered per prompt in each arm (from the logged 6)


def p_risk(text):
    """The committed risk parser: 1.0 if the answer ends on B, else 0.0."""
    hits = re.findall(r"(?<![A-Za-z])([AB])(?![A-Za-z])", str(text))
    return 1.0 if hits and hits[-1] == "B" else 0.0


def find_rounds_raw(obj, path=""):
    """Yield (path, rounds_raw) for every rounds_raw list anywhere in the JSON."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == "rounds_raw" and isinstance(v, list):
                yield path + "/" + k, v
            else:
                yield from find_rounds_raw(v, path + "/" + str(k))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from find_rounds_raw(v, path + f"[{i}]")


def sd_binary(k, m):
    """Population SD of m binary scores of which k are 1."""
    p = k / m
    return math.sqrt(max(0.0, p * (1 - p)))


def arrange(items, subpool, maximize):
    """Exact knapsack: pick how many 1s to take from each prompt.

    items: list of (n_ones, n_total) per prompt.
    Returns {total_ones: (objective, [k per prompt])} for every achievable total.
    """
    best = {0: (0.0, [])}
    for (c, n) in items:
        lo = max(0, subpool - (n - c))
        hi = min(subpool, c)
        nxt = {}
        for total, (obj, ks) in best.items():
            for k in range(lo, hi + 1):
                t2 = total + k
                o2 = obj + sd_binary(k, subpool)
                cur = nxt.get(t2)
                better = (cur is None or (o2 > cur[0] if maximize else o2 < cur[0]))
                if better:
                    nxt[t2] = (o2, ks + [k])
        best = nxt
    return best


def realize(round_items, ks, subpool, keep):
    """Build each prompt's sub-pool with exactly k ones, then select on judge score.

    Within a prompt, which particular 1s (or 0s) get taken is decided by judge
    score: we take the highest-judge-score candidates of each value class. This is
    the arrangement most favourable to the judge, applied identically in both arms,
    so it cannot manufacture a difference between them.
    """
    pool_vals, kept_vals, rhos = [], [], []
    for it, k in zip(round_items, ks):
        vals = [p_risk(c) for c in it["candidates"]]
        js = list(it["scores"])
        ones = sorted([i for i, v in enumerate(vals) if v == 1.0], key=lambda i: -js[i])
        zeros = sorted([i for i, v in enumerate(vals) if v == 0.0], key=lambda i: -js[i])
        take = ones[:k] + zeros[:subpool - k]
        if len(take) < subpool:
            return None
        sub_v = [vals[i] for i in take]
        sub_j = [js[i] for i in take]
        pool_vals.extend(sub_v)
        order = sorted(range(subpool), key=lambda i: -sub_j[i])[:keep]
        kept_vals.extend(sub_v[i] for i in order)
        # within-prompt agreement between judge score and value score
        if len(set(sub_v)) > 1 and len(set(sub_j)) > 1:
            mv, mj = statistics.mean(sub_v), statistics.mean(sub_j)
            num = sum((a - mv) * (b - mj) for a, b in zip(sub_v, sub_j))
            den = math.sqrt(sum((a - mv) ** 2 for a in sub_v) * sum((b - mj) ** 2 for b in sub_j))
            if den > 0:
                rhos.append(num / den)
    if not pool_vals:
        return None
    per_prompt_sd, per_prompt_mean = [], []
    for i in range(0, len(pool_vals), subpool):
        chunk = pool_vals[i:i + subpool]
        per_prompt_sd.append(statistics.pstdev(chunk))
        per_prompt_mean.append(statistics.mean(chunk))
    return {
        "pool_mean": statistics.mean(pool_vals),
        "spread": statistics.mean(per_prompt_sd),
        # the quantity being traded against within-prompt spread
        "between_prompt_variance": statistics.pvariance(per_prompt_mean),
        "kept_mean": statistics.mean(kept_vals),
        "gap": statistics.mean(kept_vals) - statistics.mean(pool_vals),
        "rho": statistics.mean(rhos) if rhos else 0.0,
        "n_prompts_with_agreement": len(rhos),
    }


def main():
    files = []
    for root, _, names in os.walk("experiments"):
        for n in names:
            if n.endswith(".json"):
                files.append(os.path.join(root, n))

    rows = []
    for f in files:
        try:
            d = json.load(open(f))
        except Exception:
            continue
        for path, rr in find_rounds_raw(d):
            for ri, rd in enumerate(rr):
                if not isinstance(rd, list) or not rd:
                    continue
                first = rd[0]
                if not (isinstance(first, dict) and "candidates" in first and "scores" in first):
                    continue
                items = []
                ok = True
                for it in rd:
                    if not isinstance(it, dict) or "candidates" not in it or "scores" not in it:
                        ok = False
                        break
                    vals = [p_risk(c) for c in it["candidates"]]
                    if len(vals) != len(it["scores"]) or len(vals) < SUBPOOL:
                        ok = False
                        break
                    items.append((int(sum(vals)), len(vals)))
                if not ok or len(items) < 6:
                    continue

                hi = arrange(items, SUBPOOL, True)
                lo = arrange(items, SUBPOOL, False)
                shared = set(hi) & set(lo)
                if not shared:
                    continue
                # Choose the total that maximizes the spread contrast between arms.
                best_t = max(shared, key=lambda t: hi[t][0] - lo[t][0])
                if hi[best_t][0] - lo[best_t][0] <= 1e-9:
                    continue
                a = realize(rd, hi[best_t][1], SUBPOOL, M_KEEP)
                b = realize(rd, lo[best_t][1], SUBPOOL, M_KEEP)
                if not a or not b:
                    continue
                if abs(a["pool_mean"] - b["pool_mean"]) > 1e-9:
                    continue  # must be exactly matched
                rows.append({
                    "file": f, "path": path, "round": ri + 1,
                    "n_prompts": len(items),
                    "pool_mean": round(a["pool_mean"], 4),
                    "high": {k: round(v, 4) for k, v in a.items()},
                    "low": {k: round(v, 4) for k, v in b.items()},
                    "spread_diff": round(a["spread"] - b["spread"], 4),
                    "gap_diff": round(a["gap"] - b["gap"], 4),
                    "predicted_gap_diff": round(
                        0.5 * (a["rho"] + b["rho"]) * (a["spread"] - b["spread"]), 4),
                })

    # aggregate
    out = {
        "description": "Matched-pool-mean manipulation of candidate spread, built by "
                       "re-arranging logged candidates across prompts and re-running "
                       "the real selection rule on the logged judge scores.",
        "method": {
            "subpool_per_prompt": SUBPOOL, "kept_per_prompt": M_KEEP,
            "arms": "HIGH and LOW mean within-prompt spread at an identical total "
                    "number of value-1 candidates, solved exactly by knapsack",
            "caveat": "counterfactual SELECTION on real judge scores, not "
                      "counterfactual training",
        },
        "n_rounds": len(rows),
    }
    if rows:
        sd_hi = statistics.mean(r["high"]["spread"] for r in rows)
        sd_lo = statistics.mean(r["low"]["spread"] for r in rows)
        g_hi = statistics.mean(r["high"]["gap"] for r in rows)
        g_lo = statistics.mean(r["low"]["gap"] for r in rows)
        out["summary"] = {
            "mean_spread_high": round(sd_hi, 4),
            "mean_spread_low": round(sd_lo, 4),
            "mean_gap_high": round(g_hi, 4),
            "mean_gap_low": round(g_lo, 4),
            "mean_abs_gap_high": round(statistics.mean(abs(r["high"]["gap"]) for r in rows), 4),
            "mean_abs_gap_low": round(statistics.mean(abs(r["low"]["gap"]) for r in rows), 4),
            "mean_rho_high": round(statistics.mean(r["high"]["rho"] for r in rows), 4),
            "mean_rho_low": round(statistics.mean(r["low"]["rho"] for r in rows), 4),
            "rounds_where_high_gap_exceeds_low": sum(
                1 for r in rows if abs(r["high"]["gap"]) > abs(r["low"]["gap"])),
            "rounds_tied": sum(1 for r in rows if abs(r["high"]["gap"]) == abs(r["low"]["gap"])),
        }
        # does the predicted difference track the observed difference?
        xs = [r["predicted_gap_diff"] for r in rows]
        ys = [r["gap_diff"] for r in rows]
        mx, my = statistics.mean(xs), statistics.mean(ys)
        sxx = sum((x - mx) ** 2 for x in xs)
        syy = sum((y - my) ** 2 for y in ys)
        sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
        out["summary"]["corr_predicted_vs_observed_gap_diff"] = (
            round(sxy / math.sqrt(sxx * syy), 4) if sxx > 0 and syy > 0 else None)
        out["summary"]["slope_observed_on_predicted"] = (
            round(sxy / sxx, 4) if sxx > 0 else None)
        out["summary"]["mean_between_prompt_variance_high"] = round(
            statistics.mean(r["high"]["between_prompt_variance"] for r in rows), 4)
        out["summary"]["mean_between_prompt_variance_low"] = round(
            statistics.mean(r["low"]["between_prompt_variance"] for r in rows), 4)

        # THE DECISIVE CHECK. Pool both arms (2 x n_rounds points) and ask whether a
        # single agreement-times-spread law fits them together. If the manipulation
        # simply moved the pool along the existing law, one slope should describe
        # both arms and neither arm should need its own intercept.
        def fit(pts):
            xs2 = [p[0] for p in pts]
            ys2 = [p[1] for p in pts]
            n = len(pts)
            if n < 3:
                return None
            m1, m2 = statistics.mean(xs2), statistics.mean(ys2)
            a = sum((x - m1) ** 2 for x in xs2)
            c = sum((y - m2) ** 2 for y in ys2)
            b = sum((x - m1) * (y - m2) for x, y in zip(xs2, ys2))
            if a <= 0 or c <= 0:
                return None
            return {"slope": round(b / a, 4), "intercept": round(m2 - (b / a) * m1, 4),
                    "r": round(b / math.sqrt(a * c), 4), "n": n}

        pts_hi = [(r["high"]["rho"] * r["high"]["spread"], r["high"]["gap"]) for r in rows]
        pts_lo = [(r["low"]["rho"] * r["low"]["spread"], r["low"]["gap"]) for r in rows]
        out["summary"]["law_fit_high_arm"] = fit(pts_hi)
        out["summary"]["law_fit_low_arm"] = fit(pts_lo)
        out["summary"]["law_fit_both_arms_pooled"] = fit(pts_hi + pts_lo)
    out["rows"] = rows

    with open(OUT, "w") as f:
        json.dump(out, f, indent=1)
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1))


if __name__ == "__main__":
    main()
