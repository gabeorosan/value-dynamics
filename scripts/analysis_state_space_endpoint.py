"""A 3-state model of the loop — pool p, alignment rho, supply sigma — rolled
forward for a CALIBRATED endpoint estimate. (docs/ANALYSIS_LEDGER.md; user
question 07-14: "is there some model for rho and sigma's drift and rho*sigma
that gives a calibrated estimate of where the run ends up?")

Structure (dictated by the traced mechanics):
  dp_t      = a_p + b_p * (rho_t * sigma_t)                + eps_p   [force]
  rho_{t+1} = a_r + b_r * rho_t + c_r * (rho_t * sigma_t)  + eps_r   [bloom]
  sig_{t+1} = a_s + b_s * sigma_t + c_s * p_t*(1-p_t)      + eps_s   [supply/rail-shrink]
Linear least squares per family (OLMo K2 / Qwen K1 — different mechanisms),
Gaussian residual noise, states clipped to bounds. From each run's ROUND-1
state (p1, rho1, sigma1), 2000 Monte-Carlo paths of length R-1 give an
endpoint distribution.

Calibration protocol: leave-one-run-out — refit all three equations without
the held-out run, simulate its endpoint distribution, record the actual
endpoint's PIT (percentile of truth in the predicted distribution), interval
coverage at 50%/80%, and MAE of the predictive median. Baselines:
  PERSIST   p_end = p_1
  GAP-AR    scalar alternative: gap follows its own AR(1), dp = a + b*gap
            (what you'd build without the rho/sigma decomposition)

Usage: uv run python scripts/analysis_state_space_endpoint.py
Writes experiments/state_space_endpoint.json and prints the tables.
"""

import json
import math
import os
import random
import statistics as st

SRC = "experiments/taste_alignment_predictor.json"
N_MC = 2000
RNG = random.Random(11)


def lstsq(rows):
    """rows: list of (xvec, y). Returns beta via normal equations (tiny dims)."""
    k = len(rows[0][0])
    ata = [[0.0] * k for _ in range(k)]
    atb = [0.0] * k
    for x, y in rows:
        for i in range(k):
            atb[i] += x[i] * y
            for j in range(k):
                ata[i][j] += x[i] * x[j]
    # gaussian elimination
    m = [ata[i][:] + [atb[i]] for i in range(k)]
    for col in range(k):
        piv = max(range(col, k), key=lambda r: abs(m[r][col]))
        m[col], m[piv] = m[piv], m[col]
        if abs(m[col][col]) < 1e-12:
            m[col][col] = 1e-12
        for r in range(k):
            if r != col:
                f = m[r][col] / m[col][col]
                for c in range(col, k + 1):
                    m[r][c] -= f * m[col][c]
    beta = [m[i][k] / m[i][i] for i in range(k)]
    resid = [y - sum(b * xi for b, xi in zip(beta, x)) for x, y in rows]
    sd = st.pstdev(resid) if len(resid) > 1 else 0.0
    return beta, sd


def transitions(runs):
    """[(p, rho, sig, p_next, rho_next, sig_next, gap, gap_next)]"""
    out = []
    for r in runs:
        rd = r["rounds"]
        for i in range(len(rd) - 1):
            out.append((rd[i]["pool"], rd[i]["rho"], rd[i]["sigma"],
                        rd[i + 1]["pool"], rd[i + 1]["rho"], rd[i + 1]["sigma"],
                        rd[i]["gap"], rd[i + 1]["gap"]))
    return out


def fit(tr):
    f_p = lstsq([([1.0, p3 * p2_], p4 - p1) for p1, p3, p2_, p4, _, _, _, _ in
                 [(t[0], t[1], t[2], t[3], 0, 0, 0, 0) for t in tr]])
    f_r = lstsq([([1.0, t[1], t[1] * t[2]], t[4]) for t in tr])
    f_s = lstsq([([1.0, t[2], t[0] * (1 - t[0])], t[5]) for t in tr])
    return f_p, f_r, f_s


def fit_gap_ar(tr):
    g_p = lstsq([([1.0, t[6]], t[3] - t[0]) for t in tr])
    g_g = lstsq([([1.0, t[6]], t[7]) for t in tr])
    return g_p, g_g


def simulate(f_p, f_r, f_s, p, rho, sig, steps):
    for _ in range(steps):
        force = rho * sig
        p = p + f_p[0][0] + f_p[0][1] * force + RNG.gauss(0, f_p[1])
        rho2 = f_r[0][0] + f_r[0][1] * rho + f_r[0][2] * force + RNG.gauss(0, f_r[1])
        sig2 = f_s[0][0] + f_s[0][1] * sig + f_s[0][2] * p * (1 - p) + RNG.gauss(0, f_s[1])
        p = min(1.0, max(0.0, p))
        rho = min(1.0, max(-1.0, rho2))
        sig = min(0.5, max(0.0, sig2))
    return p


def simulate_gap(g_p, g_g, p, gap, steps):
    for _ in range(steps):
        p = min(1.0, max(0.0, p + g_p[0][0] + g_p[0][1] * gap + RNG.gauss(0, g_p[1])))
        gap = g_g[0][0] + g_g[0][1] * gap + RNG.gauss(0, g_g[1])
    return p


def main():
    data = json.load(open(SRC))
    runs = data["runs"]
    report = {}
    for grid in ("k2_olmo", "k1_qwen"):
        rs = [r for r in runs if r["grid"] == grid]
        rows = []
        for held in rs:
            train = [r for r in rs if r is not held]
            tr = transitions(train)
            f_p, f_r, f_s = fit(tr)
            g_p, g_g = fit_gap_ar(tr)
            r1 = held["rounds"][0]
            steps = len(held["rounds"]) - 1
            ends = sorted(simulate(f_p, f_r, f_s, r1["pool"], r1["rho"], r1["sigma"], steps)
                          for _ in range(N_MC))
            gends = sorted(simulate_gap(g_p, g_g, r1["pool"], r1["gap"], steps)
                           for _ in range(N_MC))
            truth = held["rounds"][-1]["pool"]
            pit = sum(1 for e in ends if e < truth) / N_MC
            med = ends[N_MC // 2]
            q = lambda es, x: es[int(x * N_MC)]
            rows.append(dict(cond=held["cond"], seed=held["seed"], truth=round(truth, 3),
                             median=round(med, 3), pit=round(pit, 3),
                             lo80=round(q(ends, 0.10), 3), hi80=round(q(ends, 0.90), 3),
                             in50=q(ends, 0.25) <= truth <= q(ends, 0.75),
                             in80=q(ends, 0.10) <= truth <= q(ends, 0.90),
                             mae=round(abs(med - truth), 3),
                             gap_median=round(gends[N_MC // 2], 3),
                             gap_mae=round(abs(gends[N_MC // 2] - truth), 3),
                             gap_in80=q(gends, 0.10) <= truth <= q(gends, 0.90),
                             persist_mae=round(abs(held["rounds"][0]["pool"] - truth), 3)))
        n = len(rows)
        report[grid] = dict(
            runs=rows, n=n,
            coverage50=round(sum(r["in50"] for r in rows) / n, 2),
            coverage80=round(sum(r["in80"] for r in rows) / n, 2),
            gap_coverage80=round(sum(r["gap_in80"] for r in rows) / n, 2),
            mae=round(st.mean([r["mae"] for r in rows]), 3),
            gap_mae=round(st.mean([r["gap_mae"] for r in rows]), 3),
            persist_mae=round(st.mean([r["persist_mae"] for r in rows]), 3),
            pits=sorted(r["pit"] for r in rows),
            full_fit=dict(zip(("dp", "rho", "sigma"),
                              [dict(beta=[round(b, 3) for b in f[0]], resid_sd=round(f[1], 3))
                               for f in fit(transitions(rs))])))
    with open("experiments/state_space_endpoint.json", "w") as fh:
        json.dump(report, fh, indent=1)

    for grid, v in report.items():
        print(f"\n== {grid} (LORO over {v['n']} runs, {N_MC} MC paths each)")
        print(f"  endpoint MAE: state-space {v['mae']}  gap-AR {v['gap_mae']}  persistence {v['persist_mae']}")
        print(f"  interval coverage: 50% nominal -> {v['coverage50']}  80% nominal -> {v['coverage80']}  (gap-AR 80% -> {v['gap_coverage80']})")
        print(f"  PIT values (should be ~uniform): {v['pits']}")
        print(f"  full-data fit: {json.dumps(v['full_fit'])}")
        worst = sorted(v["runs"], key=lambda r: -r["mae"])[:4]
        for r in worst:
            print(f"   worst: {r['cond']} s{r['seed']} truth {r['truth']} median {r['median']} 80% [{r['lo80']},{r['hi80']}] pit {r['pit']}")


if __name__ == "__main__":
    main()
