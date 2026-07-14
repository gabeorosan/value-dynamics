"""Is there a BETTER endpoint model than the linear-Gaussian 3-state one?
(docs/ANALYSIS_LEDGER.md; user 07-14: "I suspect there is something better.")

Six predictive models, one leave-one-run-out harness, proper scoring (CRPS —
which grades the whole distribution, not just the median like MAE does), PIT
calibration, interval coverage, and PAIRED win-counts so a real improvement is
distinguishable from n=25 noise.

Models:
  CLIM     climatology — predict the empirical endpoint spread of the training
           runs, ignoring this run's state. The baseline complexity must beat.
  PERSIST  point-ish forecast at round-1 pool (small noise).
  M0       current: linear force/bloom/supply eqs, Gaussian additive noise.
  M0_LOGIT M0 but the pool update lives in logit space (bounded; rails pile up
           instead of leaking past 0/1 and getting clipped).
  M0_BOOT  M0 plus PARAMETER uncertainty: each MC path draws a bootstrap refit
           of the equations, so tiny-n coefficient uncertainty is propagated.
  M0_POOL  partial pooling: the force slope Δp~ρσ is fit on BOTH families
           together (the factorization says it is ~universal), intercepts per
           family. Trades bias for variance — usually wins at tiny n.

CRPS uses the sample formula CRPS = E|X-y| - 0.5 E|X-X'|; lower is better.
All predictions are leave-one-run-out. Also reports a calibrated P(runaway)
reliability read (the quantity an alignment monitor actually wants).

Usage: uv run python scripts/analysis_endpoint_model_bakeoff.py
Writes experiments/endpoint_model_bakeoff.json and prints the tables.
"""

import json
import math
import os
import random
import statistics as st

SRC = "experiments/taste_alignment_predictor.json"
N_MC = 1500
RNG = random.Random(17)
RAIL = {"k2_olmo": 0.40, "k1_qwen": 0.75}  # "runaway" endpoint threshold per family


def clip(x, lo, hi):
    return min(hi, max(lo, x))


def logit(p):
    p = clip(p, 1e-3, 1 - 1e-3)
    return math.log(p / (1 - p))


def sigmoid(z):
    if z > 30:
        return 1.0
    if z < -30:
        return 0.0
    return 1 / (1 + math.exp(-z))


def lstsq(rows):
    k = len(rows[0][0])
    ata = [[0.0] * k for _ in range(k)]
    atb = [0.0] * k
    for x, y in rows:
        for i in range(k):
            atb[i] += x[i] * y
            for j in range(k):
                ata[i][j] += x[i] * x[j]
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
    sd = st.pstdev(resid) if len(resid) > 1 else 0.05
    return beta, max(sd, 1e-3)


def trans(runs):
    out = []
    for r in runs:
        rd = r["rounds"]
        for i in range(len(rd) - 1):
            out.append(dict(p=rd[i]["pool"], rho=rd[i]["rho"], sig=rd[i]["sigma"],
                            pn=rd[i + 1]["pool"], rn=rd[i + 1]["rho"], sn=rd[i + 1]["sigma"]))
    return out


def fit_core(tr, logit_p=False, slope_p=None):
    if logit_p:
        f_p = lstsq([([1.0, t["rho"] * t["sig"]], logit(t["pn"]) - logit(t["p"])) for t in tr])
    elif slope_p is not None:
        # intercept-only given a fixed shared slope
        b = slope_p
        rows = [([1.0], (t["pn"] - t["p"]) - b * (t["rho"] * t["sig"])) for t in tr]
        f0 = lstsq(rows)
        f_p = ([f0[0][0], b], f0[1])
    else:
        f_p = lstsq([([1.0, t["rho"] * t["sig"]], t["pn"] - t["p"]) for t in tr])
    f_r = lstsq([([1.0, t["rho"], t["rho"] * t["sig"]], t["rn"]) for t in tr])
    f_s = lstsq([([1.0, t["sig"], t["p"] * (1 - t["p"])], t["sn"]) for t in tr])
    return f_p, f_r, f_s


def sim(fits, p, rho, sig, steps, logit_p=False):
    f_p, f_r, f_s = fits
    for _ in range(steps):
        force = rho * sig
        if logit_p:
            dz = f_p[0][0] + f_p[0][1] * force + RNG.gauss(0, f_p[1])
            p = sigmoid(logit(p) + dz)
        else:
            p = clip(p + f_p[0][0] + f_p[0][1] * force + RNG.gauss(0, f_p[1]), 0, 1)
        rho = clip(f_r[0][0] + f_r[0][1] * rho + f_r[0][2] * force + RNG.gauss(0, f_r[1]), -1, 1)
        sig = clip(f_s[0][0] + f_s[0][1] * sig + f_s[0][2] * p * (1 - p) + RNG.gauss(0, f_s[1]), 0, 0.5)
    return p


def crps(samples, y):
    n = len(samples)
    s = sorted(samples)
    e1 = sum(abs(x - y) for x in s) / n
    # E|X-X'| via sorted formula: sum_i (2i-n+1) x_i * 2 / n^2 ... use direct O(n log n)
    acc = 0.0
    csum = 0.0
    for i, x in enumerate(s):
        acc += i * x - csum
        csum += x
    e2 = 2 * acc / (n * n)
    return e1 - 0.5 * e2


def predict(model, train, held, grid, pooled_slope):
    r1 = held["rounds"][0]
    steps = len(held["rounds"]) - 1
    if model == "CLIM":
        ends = [r["rounds"][-1]["pool"] + RNG.gauss(0, 0.02) for r in train]
        return [clip(e, 0, 1) for e in (ends * (N_MC // len(ends) + 1))[:N_MC]]
    if model == "PERSIST":
        return [clip(r1["pool"] + RNG.gauss(0, 0.05), 0, 1) for _ in range(N_MC)]
    if model == "M0_BOOT":
        boots = []
        for _ in range(40):
            bs = [train[RNG.randrange(len(train))] for _ in range(len(train))]
            boots.append(fit_core(trans(bs)))
        return [sim(boots[RNG.randrange(len(boots))], r1["pool"], r1["rho"], r1["sigma"], steps)
                for _ in range(N_MC)]
    logit_p = (model == "M0_LOGIT")
    slope = pooled_slope if model == "M0_POOL" else None
    fits = fit_core(trans(train), logit_p=logit_p, slope_p=slope)
    return [sim(fits, r1["pool"], r1["rho"], r1["sigma"], steps, logit_p=logit_p)
            for _ in range(N_MC)]


def main():
    runs = json.load(open(SRC))["runs"]
    models = ["CLIM", "PERSIST", "M0", "M0_LOGIT", "M0_BOOT", "M0_POOL"]
    report = {}
    for grid in ("k2_olmo", "k1_qwen"):
        rs = [r for r in runs if r["grid"] == grid]
        pooled_slope = fit_core(trans(runs))[0][0][1]  # slope from BOTH families
        per_run = {m: [] for m in models}
        cover80 = {m: 0 for m in models}
        pit = {m: [] for m in models}
        prail = {m: [] for m in models}
        truths = []
        for held in rs:
            train = [r for r in rs if r is not held]
            truth = held["rounds"][-1]["pool"]
            truths.append((truth > RAIL[grid], held["cond"], held["seed"]))
            for m in models:
                s = predict(m, train, held, grid, pooled_slope)
                per_run[m].append(crps(s, truth))
                ss = sorted(s)
                lo, hi = ss[int(0.10 * N_MC)], ss[int(0.90 * N_MC)]
                cover80[m] += (lo <= truth <= hi)
                pit[m].append(sum(1 for x in s if x < truth) / len(s))
                prail[m].append(sum(1 for x in s if x > RAIL[grid]) / len(s))
        n = len(rs)
        # paired win-counts vs M0
        wins = {}
        for m in models:
            if m == "M0":
                continue
            w = sum(1 for a, b in zip(per_run[m], per_run["M0"]) if a < b - 1e-6)
            wins[m] = f"{w}/{n} beat M0 (mean CRPS {st.mean(per_run[m]):.3f} vs {st.mean(per_run['M0']):.3f})"
        report[grid] = dict(
            n=n,
            mean_crps={m: round(st.mean(per_run[m]), 4) for m in models},
            coverage80={m: round(cover80[m] / n, 2) for m in models},
            pit_ks={m: round(max(abs(sorted(pit[m])[i] - (i + 0.5) / n) for i in range(n)), 3) for m in models},
            paired_vs_M0=wins,
            runaway_reliability={m: [round(p, 2) for p, (t, _, _) in
                                     sorted(zip(prail[m], truths), key=lambda z: -z[0])]
                                 for m in ("CLIM", "M0", "M0_LOGIT", "M0_POOL")},
            runaway_truth=[f"{c}s{s}{'*' if t else ''}" for (t, c, s) in
                           sorted(truths, key=lambda z: 0)])
    with open("experiments/endpoint_model_bakeoff.json", "w") as fh:
        json.dump(report, fh, indent=1)

    for grid, v in report.items():
        print(f"\n=== {grid} (LORO, {v['n']} runs, {N_MC} MC) — lower CRPS better")
        order = sorted(v["mean_crps"], key=lambda m: v["mean_crps"][m])
        for m in order:
            print(f"  {m:9s} CRPS {v['mean_crps'][m]:.4f}  cover80 {v['coverage80'][m]:.2f}  PIT-KS {v['pit_ks'][m]:.3f}")
        print("  paired vs M0:")
        for m, s in v["paired_vs_M0"].items():
            print(f"    {m:9s} {s}")


if __name__ == "__main__":
    main()
