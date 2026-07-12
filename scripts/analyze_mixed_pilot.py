#!/usr/bin/env python3
"""Analyze the coupled-generator pilot (mixed_coupled_pilot.json).

Per cell: kept-share time series + owner transition counts (the regime
classifier the SPEC requires — share entropy alone cannot separate
alternating capture from balanced selection), between-owner sr gap,
total/within-owner spread trajectory (the coupling-as-spread-source
verdict), per-owner forced self-report probe trajectories, zero-kept
(starvation) accounting.

Regime rules (experiments/em_mixed_generators/SPEC.md, corrected):
  capture      — one owner's kept share >= 0.75 in every round from r2 on,
                 with the between-owner sr gap still > 0.15;
  convergence  — share stays in (0.25, 0.75) while the owner gap falls
                 below 0.15 by the final round;
  alternation  — share crosses 0.5 between consecutive rounds >= 2 times
                 with the gap sustained > 0.15;
  starvation   — one owner has 0 kept rows in >= half the rounds (its state
                 frozen) while the gap persists — the screen-predicted
                 regime for the base judge.
Spread-source hypothesis REFUTED if total spread at r4 < 0.5 x total spread
at r1 while the share stayed in (0.1, 0.9).

Usage: uv run python scripts/analyze_mixed_pilot.py <path-to-json>
"""
import json
import sys


def classify(shares, gaps, zero_kept_rounds, n_rounds):
    crossings = sum(1 for a, b in zip(shares, shares[1:])
                    if (a - 0.5) * (b - 0.5) < 0)
    final_gap = gaps[-1]
    if any(len(z) > 0 for z in zero_kept_rounds) and \
            sum(1 for z in zero_kept_rounds if z) >= n_rounds / 2 and final_gap > 0.15:
        return "starvation"
    late = shares[1:] if len(shares) > 1 else shares
    if late and (all(s >= 0.75 for s in late) or all(s <= 0.25 for s in late)) \
            and final_gap > 0.15:
        return "capture"
    if crossings >= 2 and final_gap > 0.15:
        return "alternation"
    if final_gap < 0.15:
        return "convergence"
    return "mixed/none"


def main(path):
    d = json.load(open(path))
    cfg = d.get("config", {})
    print(f"config: judge={cfg.get('judge')} normalized={cfg.get('judge_sees_normalized')} "
          f"keep={cfg.get('keep')} steps/round={cfg.get('round_steps')}")
    for key, cell in sorted(d.get("cells", {}).items()):
        rounds = cell.get("rounds", [])
        if not rounds:
            continue
        shares = [r["kept_A_share"] for r in rounds]
        gaps = [r["owner_sr_gap"] for r in rounds]
        spreads = [r["total_sr_spread"] for r in rounds]
        zk = [r.get("zero_kept_owner", []) for r in rounds]
        pa = [r["probe"]["A"] for r in rounds]
        pb = [r["probe"]["B"] for r in rounds]
        print(f"\n=== {key} ({len(rounds)} rounds) ===")
        print(f"  kept A-share: {[round(s, 2) for s in shares]}  "
              f"(zero-kept: {[''.join(z) or '-' for z in zk]})")
        print(f"  owner sr gap: {[round(g, 2) for g in gaps]}")
        print(f"  total spread: {[round(s, 2) for s in spreads]}  "
              f"within-A {[round(r['within_A_spread'], 2) for r in rounds]}  "
              f"within-B {[round(r['within_B_spread'], 2) for r in rounds]}")
        print(f"  probe A: {cell['probe0']['A']:.2f} -> {[round(x, 2) for x in pa]}")
        print(f"  probe B: {cell['probe0']['B']:.2f} -> {[round(x, 2) for x in pb]}")
        regime = classify(shares, gaps, zk, len(rounds))
        refuted = (len(spreads) >= 2 and spreads[-1] < 0.5 * spreads[0]
                   and all(0.1 < s < 0.9 for s in shares))
        print(f"  REGIME: {regime}; spread-source hypothesis "
              f"{'REFUTED (spread halved with mixed shares)' if refuted else 'not refuted'}")


if __name__ == "__main__":
    main(sys.argv[1])
