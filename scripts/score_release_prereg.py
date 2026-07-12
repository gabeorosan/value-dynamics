#!/usr/bin/env python3
"""Score the release-grid pre-registration — transparent per-criterion table.

Usage: python3 scripts/score_release_prereg.py <kernelA.json> [more.json ...]

Rewritten per the 2026-07-12 program audit: every criterion stated in
docs/prereg_release_grid_predictions.md is scored VERBATIM and separately;
no pooled auto-verdicts, no threshold substitutions. Mixed outcomes print as
mixed. The condition-aware gain refit reports per-schedule slopes with
rollout-cluster bootstrap CIs instead of one pooled k.
"""
import json
import random
import statistics as st
import sys

recs = {}
for path in sys.argv[1:]:
    d = json.load(open(path))
    for sd in (k for k in d if k.isdigit()):
        for c, r in d[sd].items():
            key = (c, int(sd))
            if key in recs:
                old_n, new_n = len(recs[key].get("traj", [])), len(r.get("traj", []))
                keep_new = new_n >= old_n
                print(f"WARNING duplicate record {key}: {old_n} vs {new_n} rounds in {path}; "
                      f"keeping the {'new' if keep_new else 'old'} (longer/equal) one")
                if not keep_new:
                    continue
            recs[key] = r

by = {}
for (c, sd), r in sorted(recs.items()):
    by.setdefault(c, []).append((sd, r))

print("=== raw trajectories (r0..r8) ===")
for c, rows in by.items():
    for sd, r in rows:
        print(f"{c:14s} s{sd}  " + " ".join(f"{x:.3f}" for x in r["traj"]))

def full(c):
    return [(sd, r["traj"]) for sd, r in by.get(c, []) if len(r["traj"]) >= 9]

print("\n=== per-criterion scoring (verbatim from the prereg; one line per criterion) ===")
rows_out = []

def crit(schedule, text, value, passed):
    rows_out.append((schedule, text, value, passed))

pr = full("press_release")
if pr:
    r8m = st.mean(t[8] for _, t in pr)
    crit("press_release", "r8 mean <= 0.10", f"{r8m:.3f}", r8m <= 0.10)
    worst = max(t[8] - t[4] for _, t in pr)
    crit("press_release", "no seed rebounds > +0.05 over its r4 (prediction text)",
         f"max delta {worst:+.3f}", worst <= 0.05)
    crit("press_release", "REFUTATION trigger: any seed > +0.10 over r4",
         f"max delta {worst:+.3f}", worst <= 0.10)

prand = full("press_random")
if prand:
    dev = st.mean(abs(t[8] - t[4]) for _, t in prand)
    crit("press_random", "r8 within +/-0.05 of r4 per seed (prediction text)",
         f"max |delta| {max(abs(t[8]-t[4]) for _,t in prand):.3f}",
         all(abs(t[8] - t[4]) <= 0.05 for _, t in prand))
    crit("press_random", "REFUTATION trigger: mean |r8-r4| > 0.08", f"{dev:.3f}", dev <= 0.08)

ph = full("press_hold")
if ph:
    r8s = [t[8] for _, t in ph]
    crit("press_hold", "floor in 0.03-0.08 (prediction text)",
         f"r8 {sorted(round(x,3) for x in r8s)}", all(0.03 <= x <= 0.08 for x in r8s))
    nonmono = any(t[i+1] > t[i] for _, t in ph for i in range(4, 8))
    crit("press_hold", "REFUTATION trigger: non-monotone / rises after r4 (strict)",
         "rise present" if nonmono else "no rise", not nonmono)

fp = full("fan_press")
if fp and pr:
    fr = max(t[8] for _, t in fp) - min(t[8] for _, t in fp)
    prr = max(t[8] for _, t in pr) - min(t[8] for _, t in pr)
    crit("fan_press", "HEADLINE: r8 range > press_release r8 range",
         f"{fr:.3f} vs {prr:.3f}", fr > prr)
    crit("fan_press", "r8 cross-seed range > 0.15", f"{fr:.3f}", fr > 0.15)

ptb = full("press_to_base")
if ptb:
    r8s = [t[8] for _, t in ptb]
    rails = sum(1 for x in r8s if x > 0.5)
    crit("press_to_base", "most seeds drift up to 0.15-0.30 (prediction text)",
         f"r8 {sorted(round(x,3) for x in r8s)}",
         sum(1 for x in r8s if 0.15 <= x <= 0.30) > len(r8s) / 2)
    crit("press_to_base", "minority (~1/3) rail > 0.5", f"{rails}/{len(r8s)}",
         0 < rails <= max(1, len(r8s) // 2))
    if pr:
        crit("press_to_base", "mean r8 > press_release mean r8",
             f"{st.mean(r8s):.3f} vs {st.mean(t[8] for _,t in pr):.3f}",
             st.mean(r8s) > st.mean(t[8] for _, t in pr))

bh = full("base_hold")
if bh:
    r8s = [t[8] for _, t in bh]
    rate = sum(1 for x in r8s if x > 0.4) / len(r8s)
    crit("base_hold", "r8 rail rate (>0.4) >= 4-round rate 2/6",
         f"{sum(1 for x in r8s if x>0.4)}/{len(r8s)}", rate >= 2 / 6)

w = max((len(t) for _, t, _, _ in rows_out), default=10)
for sched, text, val, ok in rows_out:
    print(f"  {sched:14s} {'PASS' if ok else 'FAIL':4s}  {text:<{w}s}  [{val}]")
if rows_out:
    print(f"\n  {sum(1 for r in rows_out if r[3])}/{len(rows_out)} registered criteria pass; "
          "report the table, not a single verdict.")

print("\n=== phase-aware gain refit (per schedule x judge phase, rollout-cluster bootstrap) ===")
print("  (transition t is labeled by judge_used[t] - the judge whose selection produced the")
print("   next pool; a schedule-level slope would mix the judge regimes the audit separated)")
def slope(pairs):
    mx = st.mean(p[0] for p in pairs)
    den = sum((p[0] - mx) ** 2 for p in pairs)
    if den == 0:
        return float("nan")
    return sum((p[0] - mx) * (p[1] - st.mean(q[1] for q in pairs)) for p in pairs) / den

groups = {}  # (schedule, judge_phase) -> {seed: [(gap, drift), ...]}
for c, rows in by.items():
    for sd, r in rows:
        raws = r.get("rounds_raw", [])
        judges = r.get("judge_used", [c] * len(raws))
        pools = [st.mean(e["pool_risk"] for e in raw) for raw in raws]
        gaps = [st.mean(e["gap_arm"] for e in raw) for raw in raws]
        for t in range(len(pools) - 1):
            ph = judges[t] if t < len(judges) else c
            groups.setdefault((c, ph), {}).setdefault(sd, []).append(
                (gaps[t], pools[t + 1] - pools[t]))

for (c, ph), by_seed in sorted(groups.items()):
    clusters = list(by_seed.values())
    allp = [p for cl in clusters for p in cl]
    if len(allp) < 4 or len(clusters) < 2:
        print(f"  {c:14s} phase={ph:12s} n={len(allp)}/{len(clusters)} rollouts - too few, skipped")
        continue
    gap_sd = st.pstdev([p[0] for p in allp])
    boots = []
    rng = random.Random(0)
    for _ in range(2000):
        smp = [p for cl in (rng.choice(clusters) for _ in clusters) for p in cl]
        s = slope(smp)
        if s == s:
            boots.append(s)
    boots.sort()
    lo, hi = boots[int(0.025 * len(boots))], boots[int(0.975 * len(boots))]
    notes = []
    if gap_sd < 0.04:
        notes.append("gap variance tiny - slope unidentified")
    if len(clusters) < 3:
        notes.append(f"only {len(clusters)} rollout clusters - bootstrap CI unstable")
    note = ("  (" + "; ".join(notes) + ")") if notes else ""
    print(f"  {c:14s} phase={ph:12s} slope {slope(allp):+.2f}  cluster-CI [{lo:+.2f},{hi:+.2f}]  "
          f"n={len(allp)}/{len(clusters)} rollouts  gap-sd {gap_sd:.3f}{note}")
print("\n  PASS/FAIL above is exact-threshold, no sampling uncertainty attached;")
print("  treat single-criterion flips within ~0.02 of a bound as within noise, not confirmatory.")
