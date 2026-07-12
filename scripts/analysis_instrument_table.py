#!/usr/bin/env python3
"""Instrument-validity census + order-sensitivity analysis (K1, K2), manifest-fed.

Replaces the hand-computed table in docs/report_instrument_validity_table.md,
whose K2 census double-counted a partial frozen_cons_r0 seed-3 record (87 reads
where the deduplicated count is 85) — caught by the 2026-07-12 re-audit. Reads
ONLY the canonical manifest winners.

Two parts:
1. Census: per-round generated order gap > 0.10, invalid rate > 0.10, forced
   order gap > 0.10; endpoint (last-round) flags.
2. Sensitivity: per-condition endpoint means computed three ways — all reads
   (order-averaged), order-A only, order-B only — and on the order-valid subset
   (generated order gap <= 0.10). A headline effect is order-robust iff its
   sign/ordering holds in the A-only and B-only columns.

Usage: uv run python scripts/analysis_instrument_table.py
"""
import os
import sys
from collections import defaultdict

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_rollout_manifest import load_winning_records


def census(grid, include_measure_only=True):
    reads = []  # (cond, seed, round, gen_gap, invalid, forced_gap, valA, valB, overall)
    for _g, cond, seed, rec in load_winning_records(grid=grid):
        if not include_measure_only and rec.get("measure_only"):
            continue
        for rd, e in enumerate(rec.get("traj_order") or []):
            if not isinstance(e, dict) or "generated" not in e:
                continue
            g = e["generated"]
            reads.append((cond, seed, rd,
                          abs(g["by_order"]["A"] - g["by_order"]["B"]),
                          g.get("invalid_rate", 0.0),
                          abs(e["forced"]["by_order"]["A"] - e["forced"]["by_order"]["B"])
                          if "forced" in e else float("nan"),
                          g["by_order"]["A"], g["by_order"]["B"], g["overall"]))
    return reads


def main():
    # two passes per grid (audit r4): a full instrument census INCLUDING
    # measure-only reads, and an EXPERIMENTAL sensitivity table excluding
    # them (a measure-only endpoint must not enter a condition mean)
    for grid, incl in (("K2", True), ("K1", True), ("K1", False)):
        reads = census(grid, include_measure_only=incl)
        if not reads:
            continue
        label = "census incl. measure-only" if incl else "EXPERIMENTAL (measure-only excluded)"
        n = len(reads)
        gen_fl = sum(1 for r in reads if r[3] > 0.10)
        inv_fl = sum(1 for r in reads if r[4] > 0.10)
        forced_fl = sum(1 for r in reads if r[5] == r[5] and r[5] > 0.10)
        last_rd = defaultdict(int)
        for c, sd, rd, *_ in reads:
            last_rd[(c, sd)] = max(last_rd[(c, sd)], rd)
        endp = [r for r in reads if r[2] == last_rd[(r[0], r[1])]]
        endp_fl = sum(1 for r in endp if r[3] > 0.10)
        print(f"\n=== {grid} {label} (deduplicated manifest) ===")
        print(f"  generated reads {n}; order gap >0.10: {gen_fl} ({gen_fl/n:.0%}); "
              f"invalid >0.10: {inv_fl}; forced gap >0.10: {forced_fl} ({forced_fl/n:.0%})")
        print(f"  endpoint gaps >0.10: {endp_fl}/{len(endp)}")

        print(f"  sensitivity - endpoint mean per condition "
              f"(all order-avg / order-A / order-B / valid-subset[n]):")
        by_c = defaultdict(list)
        for r in endp:
            by_c[r[0]].append(r)
        for c in sorted(by_c):
            rows = by_c[c]
            valid = [r for r in rows if r[3] <= 0.10]
            va = f"{np.mean([r[8] for r in valid]):.3f}[n={len(valid)}]" if valid else "-[n=0]"
            print(f"    {c:15s} {np.mean([r[8] for r in rows]):.3f} / "
                  f"{np.mean([r[6] for r in rows]):.3f} / "
                  f"{np.mean([r[7] for r in rows]):.3f} / {va}")
        both = sum(1 for r in reads if r[3] <= 0.10)
        print(f"  order-valid subset: {both}/{n} reads ({both/n:.0%})")
        if not incl:
            # fan robustness must come from per-order endpoint RANGES, not
            # condition means (audit r4)
            print("  endpoint RANGE per condition (order-A / order-B):")
            for c in sorted(by_c):
                rows = by_c[c]
                ra = max(r[6] for r in rows) - min(r[6] for r in rows)
                rb = max(r[7] for r in rows) - min(r[7] for r in rows)
                print(f"    {c:15s} {ra:.3f} / {rb:.3f}  (n={len(rows)})")


if __name__ == "__main__":
    main()
