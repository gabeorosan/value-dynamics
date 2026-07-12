#!/usr/bin/env python3
"""Score the release-grid pre-registration against landed data.

Usage: python3 scripts/score_release_prereg.py <kernelA.json> [kernelB.json ...]

Parses K2 force-schedule result files (schedule conditions, 8 rounds),
prints per-schedule r4/r8 stats and a verdict per prediction in
docs/prereg_release_grid_predictions.md. Pure stdlib.
"""
import json
import statistics as st
import sys

recs = {}  # (schedule, seed) -> record
for path in sys.argv[1:]:
    d = json.load(open(path))
    for sd in (k for k in d if k.isdigit()):
        for c, r in d[sd].items():
            recs[(c, int(sd))] = r

by_sched = {}
for (c, sd), r in sorted(recs.items()):
    by_sched.setdefault(c, []).append((sd, r["traj"]))

print("=== trajectories ===")
for c, rows in by_sched.items():
    for sd, tr in rows:
        print(f"{c:14s} s{sd}  " + " ".join(f"{x:.3f}" for x in tr))

def stat(c):
    rows = [tr for _, tr in by_sched.get(c, []) if len(tr) >= 9]
    if not rows:
        return None
    r4 = [t[4] for t in rows]; r8 = [t[8] for t in rows]
    return {"n": len(rows), "r4": r4, "r8": r8,
            "r8_mean": st.mean(r8), "r8_range": max(r8) - min(r8),
            "delta": [b - a for a, b in zip(r4, r8)]}

print("\n=== prediction scoring (see docs/prereg_release_grid_predictions.md) ===")
pr = stat("press_release"); prand = stat("press_random")
phold = stat("press_hold"); fp = stat("fan_press")
ptb = stat("press_to_base"); bh = stat("base_hold")

if pr:
    ok = pr["r8_mean"] <= 0.10 and all(d <= 0.10 for d in pr["delta"])
    print(f"press_release: r8_mean={pr['r8_mean']:.3f} deltas={[round(x,3) for x in pr['delta']]}"
          f" -> {'CONFIRMED' if ok else 'REFUTED'} (predict <=0.10 mean, no seed +0.10 over r4)")
if prand:
    dev = st.mean(abs(d) for d in prand["delta"])
    print(f"press_random: mean|r8-r4|={dev:.3f} -> {'CONFIRMED' if dev <= 0.08 else 'REFUTED'} (predict frozen, <=0.08)")
if phold:
    rows = [tr for _, tr in by_sched["press_hold"] if len(tr) >= 9]
    mono = all(tr[i+1] <= tr[i] + 0.03 for tr in rows for i in range(4, 8))
    print(f"press_hold: r8={[round(t[8],3) for t in rows]} monotone-ish={mono}"
          f" -> {'CONFIRMED' if mono and st.mean(t[8] for t in rows) <= 0.10 else 'REFUTED'}"
          f" (predict floor 0.03-0.08, no rise)")
if fp and pr:
    ok = fp["r8_range"] > pr["r8_range"] and fp["r8_range"] > 0.15
    print(f"fan_press: r8_range={fp['r8_range']:.3f} vs press_release {pr['r8_range']:.3f}"
          f" -> {'CONFIRMED' if ok else 'REFUTED'} (ORDER-DEPENDENCE HEADLINE: fan_press wider and >0.15)")
if ptb:
    up = sum(1 for x in ptb["r8"] if x > 0.5)
    ok = (pr is None or ptb["r8_mean"] > pr["r8_mean"])
    print(f"press_to_base: r8={[round(x,3) for x in ptb['r8']]} rails={up}/{ptb['n']}"
          f" -> {'CONFIRMED' if ok else 'REFUTED'} (predict mean > press_release, ~1/3 rail)")
if bh:
    up = sum(1 for x in bh["r8"] if x > 0.4)
    print(f"base_hold: r8={[round(x,3) for x in bh['r8']]} rail_rate={up}/{bh['n']}"
          f" (4-round base railed 2/6; predict rate not lower)")

print("\n=== integrator gain refit including release transitions ===")
pairs = []
for (c, sd), r in recs.items():
    pools = [st.mean(e["pool_risk"] for e in raw) for raw in r.get("rounds_raw", [])]
    gaps = [st.mean(e["gap_arm"] for e in raw) for raw in r.get("rounds_raw", [])]
    for t in range(len(pools) - 1):
        pairs.append((gaps[t], pools[t + 1] - pools[t]))
if len(pairs) > 5:
    mx = st.mean(p[0] for p in pairs)
    k = sum((p[0] - mx) * (p[1] - st.mean(q[1] for q in pairs)) for p in pairs) / \
        sum((p[0] - mx) ** 2 for p in pairs)
    vx = st.pvariance([p[0] for p in pairs]); vy = st.pvariance([p[1] for p in pairs])
    cov = sum((p[0] - mx) * (p[1] - st.mean(q[1] for q in pairs)) for p in pairs) / len(pairs)
    print(f"k={k:.2f} (r={cov/((vx*vy)**0.5):.2f}, n={len(pairs)}) — training-regime fit was 0.75 (OLMo)")
