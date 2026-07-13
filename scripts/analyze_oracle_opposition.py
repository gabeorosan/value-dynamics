#!/usr/bin/env python3
"""Analyze the oracle-opposition run (judge_opposition_oracle.json).

Scoped claim (docs/report_secure_taste_screen.md + audit r4): "maximum
available score-based selection over N rounds at this update dose did/did not
move the insecurity-admission self-description channel" — with missing-force
rounds (no within-pool sr spread) accounted separately, NEVER counted as
resistance. Off-axis channels (em_freegen, sr_freegen, em_choice,
corrigibility) ride along descriptively.

Usage: uv run python scripts/analyze_oracle_opposition.py <path-to-json>
"""
import json
import sys

import numpy as np


def main(path):
    d = json.load(open(path))
    base = d.get("baselines", {})
    for dose, b in base.items():
        print(f"baseline [{dose}]: p_insecure={b['p_insecure']:.3f} "
              f"sr_freegen={b.get('sr_freegen_mean', float('nan')):.3f} "
              f"(noise ~{b.get('sr_freegen_noise', float('nan')):.3f}) "
              f"em_freegen={b['battery']['free_gen']['em_freegen']:.3f}")
    for key, cell in sorted(d.get("cells", {}).items()):
        if cell.get("judge_style") != "oracle_secure":
            print(f"\n{key}: judge_style={cell.get('judge_style')} — NOT an "
                  "oracle cell (pre-correction run?), skipping verdict")
            continue
        print(f"\n=== {key} (oracle_secure, {len(cell.get('rounds_raw', []))} rounds) ===")
        support = cell.get("sr_support_items", [])
        forced = []
        for rd, raw in enumerate(cell.get("rounds_raw", []), 1):
            pool_sr = [x for r in raw for x in r["cand_sr_scores"]]
            kept_sr = [r["cand_sr_scores"][i] for r in raw for i in r["kept_idx"]]
            kept_em = [r["cand_em_scores"][i] for r in raw for i in r["kept_idx"]]
            pool_em = [x for r in raw for x in r["cand_em_scores"]]
            n_sup = support[rd - 1] if rd - 1 < len(support) else sum(
                1 for r in raw if float(np.std(r["cand_sr_scores"])) > 0.05)
            gap = float(np.mean(kept_sr) - np.mean(pool_sr))
            forced.append(n_sup)
            bat = cell["battery"][rd - 1] if rd - 1 < len(cell.get("battery", [])) else None
            line = (f"  r{rd}: sr kept-gap {gap:+.3f} (support {n_sup}/{len(raw)} items"
                    f"{'; MISSING-FORCE ROUND' if n_sup == 0 else ''}) "
                    f"| off-axis em gap {float(np.mean(kept_em) - np.mean(pool_em)):+.3f}")
            if bat:
                line += (f" | probe p_insecure {bat['self_report_code']['mean_p_insecure']:.3f}"
                         f" em_freegen {bat['free_gen']['em_freegen']:.3f}"
                         f" sr_freegen {bat['sr_free_gen']['sr_freegen']:.3f}"
                         f" em_choice {bat['em_choice']['mean_p_misaligned']:.3f}")
            print(line)
        bats = cell.get("battery", [])
        if bats:
            # PRIMARY channel (repaired per the 07-13 full-program audit):
            # the preregistered target is FREE-GENERATION sr_freegen, not
            # the forced A/B probe (seed 101's sr_freegen fell 0.99->0.33
            # while the probe ROSE 0.50->0.70 — keying the verdict to the
            # probe can reverse the interpretation). sr_freegen is a
            # 9-sample read; baseline noise recorded per dose at baseline.
            bcell = base.get(cell.get("dose", ""), {})
            sr0 = bcell.get("sr_freegen_mean")
            noise = bcell.get("sr_freegen_noise")
            srend = bats[-1]["sr_free_gen"]["sr_freegen"]
            forced_rounds = sum(1 for n in forced if n > 0)
            print(f"  PRIMARY (prereg target): sr_freegen "
                  f"{'%.3f' % sr0 if sr0 is not None else 'baseline?'} -> {srend:.3f}"
                  f" (signed change {srend - sr0:+.3f}; baseline replicate noise ~"
                  f"{'%.3f' % noise if noise is not None else '?'}; 9-sample read)"
                  if sr0 is not None else
                  f"  PRIMARY (prereg target): sr_freegen endpoint {srend:.3f}, no baseline in file")
            print(f"  Manipulation check: {forced_rounds}/{len(forced)} rounds "
                  "had within-item sr spread (rounds without it are "
                  "MISSING-FORCE, not resistance).")
            p0 = bcell.get("p_insecure")
            pend = bats[-1]["self_report_code"]["mean_p_insecure"]
            print(f"  SECONDARY (direction-sensitive, no verdict weight): forced-probe "
                  f"p_insecure {'%.3f' % p0 if p0 is not None else '?'} -> {pend:.3f}; "
                  f"em_freegen {bats[-1]['free_gen']['em_freegen']:.3f}; "
                  f"em_choice {bats[-1]['em_choice']['mean_p_misaligned']:.3f}.")
            print("  No binary moved/did-not-move threshold is applied: report "
                  "the signed sr_freegen change against the recorded replicate "
                  "noise; dose/transfer/readout remain alternative explanations "
                  "for a null.")


if __name__ == "__main__":
    main(sys.argv[1])
