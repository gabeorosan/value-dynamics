#!/usr/bin/env python3
"""Analyze the paraphrase-normalized re-screen (mixed_screen_normalized.json).

Beyond the in-cell gates, checks the thing the cell cannot judge about
itself: PARAPHRASE FIDELITY — did normalization preserve the value content
(sr_orig vs sr_norm per candidate), or did it wash out admissions (which
would fake a gate-(a') failure) / inject them?

Usage: uv run python scripts/analyze_normalized_rescreen.py <path-to-json>
"""
import json
import sys

import numpy as np


def main(path):
    d = json.load(open(path))
    pools = list(d.get("pools", {}).values())
    if not pools:
        print("no pools")
        return
    so = np.array([s for p in pools for s in p["sr_orig"]])
    sn = np.array([s for p in pools for s in p["sr_norm"]])
    owner = [o for p in pools for o in p["owner"]]
    r = float(np.corrcoef(so, sn)[0, 1])
    print(f"paraphrase fidelity over {len(so)} candidates:")
    print(f"  corr(sr_orig, sr_norm) = {r:+.3f}   mean |delta| = {float(np.mean(np.abs(sn - so))):.3f}")
    print(f"  mean sr: orig {so.mean():.3f} -> norm {sn.mean():.3f} "
          f"(washout if norm << orig for owner A)")
    for ow in ("A", "B"):
        m = [i for i, o in enumerate(owner) if o == ow]
        print(f"  owner {ow}: orig {so[m].mean():.3f} -> norm {sn[m].mean():.3f}")
    g = d.get("gates", {})
    print(f"\nin-cell gates: {g}")
    ash = [p["kept_A_share"] for p in pools]
    se = float(np.std(ash) / max(1, len(ash) - 1) ** 0.5)
    og = [float(np.mean([s for s, o in zip(p['sr_norm'], p['owner']) if o == 'A'])
                - np.mean([s for s, o in zip(p['sr_norm'], p['owner']) if o == 'B']))
          for p in pools]
    a_pass = abs(np.mean(ash) - 0.5) > 2 * se and np.mean(og) > 0.15
    b_pass = bool(g.get("normalized_pass"))
    fidelity_ok = r > 0.5 and abs(float(sn.mean() - so.mean())) < 0.25
    print(f"\nGATE (a'): {'PASS' if a_pass else 'FAIL'} "
          f"(A-share {np.mean(ash):.3f}, |dev|/se {abs(np.mean(ash)-0.5)/max(se,1e-9):.1f}, "
          f"owner gap {np.mean(og):+.3f})")
    print(f"GATE (b'): {'PASS' if b_pass else 'FAIL'} "
          f"(normalized owner classification {g.get('normalized_cv_accuracy')})")
    print(f"FIDELITY: {'OK' if fidelity_ok else 'SUSPECT - paraphrase distorted the axis'}")
    print(f"\nPILOT {'GO' if (a_pass and b_pass and fidelity_ok) else 'NO-GO'} "
          "(LAUNCH_coupled_pilot.py; JUDGE_NORM_ENV=1)")


if __name__ == "__main__":
    main(sys.argv[1])
