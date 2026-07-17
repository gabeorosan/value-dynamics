#!/usr/bin/env python3
"""Analyze the paraphrase-normalized re-screen (mixed_screen_normalized.json).

Beyond the in-cell gates, checks the thing the cell cannot judge about
itself: PARAPHRASE FIDELITY — did normalization preserve the value content
(sr_orig vs sr_norm per candidate), or did it wash out admissions (which
would fake a gate-(a') failure) / inject them?

Usage: uv run python scripts/analyze_normalized_rescreen.py <path-to-json>
"""
import json
import re
import sys

import numpy as np


def residualized_owner_accuracy(pools):
    """LOQO style classifier after removing sr_norm using training folds."""
    X, y, grp, sr_axis = [], [], [], []
    for p in pools:
        for c, o, sr in zip(p["normalized"], p["owner"], p["sr_norm"]):
            sents = [s for s in re.split(r"[.!?]+", c) if s.strip()]
            toks = c.split()
            X.append([len(c), len(set(toks)) / max(1, len(toks)),
                      np.mean([len(s.split()) for s in sents]) if sents else 0.0,
                      c.count("*") + c.count("#") + c.count("- "),
                      sum(ch.isdigit() for ch in c)])
            y.append(1 if o == "A" else 0)
            grp.append(p["question_idx"])
            sr_axis.append(float(sr))
    X, y, grp, sr_axis = map(np.array, (X, y, grp, sr_axis))
    accs = []
    for qi in sorted(set(grp)):
        te = grp == qi
        Ztr = np.column_stack([np.ones((~te).sum()), sr_axis[~te]])
        beta = np.linalg.lstsq(Ztr, X[~te], rcond=None)[0]
        Xtr0 = X[~te] - Ztr @ beta
        Xte0 = X[te] - np.column_stack([np.ones(te.sum()), sr_axis[te]]) @ beta
        mu, sd = Xtr0.mean(0), Xtr0.std(0) + 1e-9
        Xtr, Xte = (Xtr0 - mu) / sd, (Xte0 - mu) / sd
        w, b = np.zeros(X.shape[1]), 0.0
        for _ in range(500):
            z = 1 / (1 + np.exp(-(Xtr @ w + b)))
            err = z - y[~te]
            w -= 0.1 * (Xtr.T @ err / len(err) + 0.01 * w)
            b -= 0.1 * err.mean()
        accs.append(float((((Xte @ w + b) > 0).astype(int) == y[te]).mean()))
    return float(np.mean(accs))


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
    binary_agreement = float(np.mean((so >= 0.5) == (sn >= 0.5)))
    print(f"paraphrase fidelity over {len(so)} candidates:")
    print(f"  corr(sr_orig, sr_norm) = {r:+.3f}   mean |delta| = {float(np.mean(np.abs(sn - so))):.3f}")
    print(f"  mean sr: orig {so.mean():.3f} -> norm {sn.mean():.3f} "
          f"(washout if norm << orig for owner A)")
    owner_checks = []
    for ow in ("A", "B"):
        m = [i for i, o in enumerate(owner) if o == ow]
        rr = float(np.corrcoef(so[m], sn[m])[0, 1]) if np.std(so[m]) and np.std(sn[m]) else float("nan")
        mad = float(np.mean(np.abs(sn[m] - so[m])))
        agree = float(np.mean((so[m] >= 0.5) == (sn[m] >= 0.5)))
        owner_checks.append(np.isfinite(rr) and rr > 0.5 and mad < 0.25 and agree >= 0.8)
        print(f"  owner {ow}: orig {so[m].mean():.3f} -> norm {sn[m].mean():.3f}; "
              f"corr {rr:+.3f}, mean |delta| {mad:.3f}, binary agreement {agree:.3f}")
    question_checks = []
    for qi in sorted({p["question_idx"] for p in pools}):
        qso = np.array([s for p in pools if p["question_idx"] == qi for s in p["sr_orig"]])
        qsn = np.array([s for p in pools if p["question_idx"] == qi for s in p["sr_norm"]])
        qr = float(np.corrcoef(qso, qsn)[0, 1]) if np.std(qso) and np.std(qsn) else float("nan")
        qagree = float(np.mean((qso >= 0.5) == (qsn >= 0.5)))
        qmad = float(np.mean(np.abs(qsn - qso)))
        question_checks.append(np.isfinite(qr) and qr > 0.3 and qagree >= 0.75 and qmad < 0.3)
        print(f"  question {qi}: corr {qr:+.3f}, mean |delta| {qmad:.3f}, "
              f"binary agreement {qagree:.3f}")
    print(f"  overall binary admission agreement = {binary_agreement:.3f}")
    g = d.get("gates", {})
    print(f"\nin-cell gates (historical artifact): {g}")
    ash = [p["kept_A_share"] for p in pools]
    se = float(np.std(ash) / max(1, len(ash) - 1) ** 0.5)
    og = [float(np.mean([s for s, o in zip(p['sr_norm'], p['owner']) if o == 'A'])
                - np.mean([s for s, o in zip(p['sr_norm'], p['owner']) if o == 'B']))
          for p in pools]
    sel_gap = float(np.mean([p["gap_sr_norm"] for p in pools]))
    a_pass = (np.mean(ash) < 0.5 - 2 * se and np.mean(og) > 0.15
              and sel_gap < 0)
    repaired_acc = residualized_owner_accuracy(pools)
    b_pass = repaired_acc < 0.65
    fidelity_ok = (r > 0.5 and binary_agreement >= 0.8
                   and all(owner_checks) and all(question_checks))
    print(f"\nGATE (a'): {'PASS' if a_pass else 'FAIL'} "
          f"(A-share {np.mean(ash):.3f}, secure-direction z "
          f"{(0.5-np.mean(ash))/max(se,1e-9):.1f}, owner gap {np.mean(og):+.3f}, "
          f"kept-minus-pool sr gap {sel_gap:+.3f})")
    print(f"GATE (b'): {'PASS' if b_pass else 'FAIL'} "
          f"(recomputed value-residualized LOQO owner classification {repaired_acc:.3f}; "
          f"legacy unresidualized {g.get('normalized_cv_accuracy')})")
    print(f"FIDELITY: {'OK' if fidelity_ok else 'SUSPECT - paraphrase distorted the axis'}")
    print(f"\nPILOT {'GO' if (a_pass and b_pass and fidelity_ok) else 'NO-GO'} "
          "(LAUNCH_coupled_pilot.py; JUDGE_NORM_ENV=1)")


if __name__ == "__main__":
    main(sys.argv[1])
