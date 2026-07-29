"""Unit check for batch_calibrate: does it recover spread a saturated judge hides?

The smoke test fakes score_pool_graded, so it never exercises the calibration
path. This exercises the arithmetic directly, on synthetic digit distributions
built to look like the failure mode calibration is meant to fix.
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import script_phase1b as m


def dist_from_logits(logits):
    e = np.exp(logits - logits.max())
    return e / e.sum()


def check(name, cond):
    print(f"  {'PASS' if cond else 'FAIL'}  {name}")
    return cond


def main():
    rng = np.random.default_rng(7)
    ok = True

    # --- 1. a SATURATED judge: huge common prompt bias toward digit 8, plus a
    # small genuine per-candidate signal. Raw scores nearly collapse; calibrated
    # scores should recover the ordering and far more spread.
    n_p, n_c = 4, 6
    latent = rng.normal(size=(n_p, n_c))
    dists, raw = [], np.zeros((n_p, n_c))
    for i in range(n_p):
        for j in range(n_c):
            logits = np.full(10, -6.0)
            logits[8] = 6.0                       # the common bias
            logits += 0.25 * latent[i, j] * np.arange(10)   # the real signal
            d = dist_from_logits(logits)
            dists.append(d)
            raw[i, j] = (d * np.arange(10.0)).sum() / 9.0
    cal = m.batch_calibrate(dists, n_p, n_c)

    raw_sd = np.mean(np.std(raw, axis=1, ddof=1))
    cal_sd = np.mean(np.std(cal, axis=1, ddof=1))
    ok &= check(f"saturated judge: calibration increases within-prompt spread "
                f"({raw_sd:.4f} -> {cal_sd:.4f})", cal_sd > raw_sd)

    order_kept = all(
        np.array_equal(np.argsort(raw[i]), np.argsort(cal[i])) for i in range(n_p))
    ok &= check("saturated judge: within-prompt ordering preserved", order_kept)

    # Correlate WITHIN prompt. Calibration removes each prompt's common level by
    # construction, so a pooled correlation would be marked down for doing
    # exactly what it is supposed to do -- and the estimand is a within-prompt
    # covariance anyway. (Pooled it is 0.811; within-prompt it is near 1.)
    def within_prompt_centre(a):
        return a - a.mean(axis=1, keepdims=True)

    corr = np.corrcoef(within_prompt_centre(latent).ravel(),
                       within_prompt_centre(cal).ravel())[0, 1]
    ok &= check(f"saturated judge: calibrated scores track the latent signal "
                f"within prompt (r = {corr:.3f})", corr > 0.95)

    corr_raw = np.corrcoef(within_prompt_centre(latent).ravel(),
                           within_prompt_centre(raw).ravel())[0, 1]
    print(f"        (raw reading tracks it at r = {corr_raw:.3f}, but over a "
          f"spread of {raw_sd:.5f} -- ordering survives saturation, resolution "
          f"does not)")

    # --- 2. NO common bias, distributions already well spread: calibration must
    # not invent structure. Ordering preserved, correlation with raw very high.
    dists2, raw2 = [], np.zeros((n_p, n_c))
    for i in range(n_p):
        for j in range(n_c):
            logits = 0.8 * latent[i, j] * np.arange(10) + rng.normal(0, 0.1, 10)
            d = dist_from_logits(logits)
            dists2.append(d)
            raw2[i, j] = (d * np.arange(10.0)).sum() / 9.0
    cal2 = m.batch_calibrate(dists2, n_p, n_c)
    r2 = np.corrcoef(raw2.ravel(), cal2.ravel())[0, 1]
    ok &= check(f"unbiased judge: calibrated tracks raw (r = {r2:.3f})", r2 > 0.95)

    # --- 3. IDENTICAL candidates: calibration must return a flat pool, not noise.
    flat = [dist_from_logits(np.array([0., 1., 2., 3., 9., 3., 2., 1., 0., 0.]))] * (1 * 5)
    cal3 = m.batch_calibrate(flat, 1, 5)
    ok &= check(f"identical candidates give zero spread ({np.std(cal3):.2e})",
                np.std(cal3) < 1e-9)

    # --- 4. output range
    ok &= check("calibrated scores stay in [0, 1]",
                float(cal.min()) >= 0.0 and float(cal.max()) <= 1.0)

    print("\nALL PASS" if ok else "\nFAILURES ABOVE")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
