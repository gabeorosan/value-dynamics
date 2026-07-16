#!/usr/bin/env python3
"""Closed-loop rollout: observed trajectories vs the rolled-forward forecast
(slug: spread-rollout-bakeoff).

Three held-out runs are shown as trajectories, not metric bars.  For each run
the generator reads ONLY the run's first-round pool state from
experiments/spread_util_unified.json -- own candidate mean q, own within-prompt
spread sigma (own_spread), agreement rho, behavioral value v, and (for mixed
pools) the supplier share u and supplier mean s -- and rolls the parameter-free
UNIT RECURRENCE forward:

    pool     p = (1 - u) * q + u * s          (self-only here, so p = q)
    kept     k = clip( p + rho * sigma , 0, 1 )
    next q   = next value = k
    sigma frozen at round 1.

That deterministic path (dashed) is a conditional mean and is too smooth.  The
shaded band is the SAME recurrence with noise added only where the measurement
implies it -- the committed "staged-noise" recipe of
scripts/analysis_trajectory_adjustments.py, variant
`unit_core_selector_q_observation_rho_persistence_gaussian`:

  * selector-gap innovation  gap += Gaussian(0, sd of leave-this-condition-out
                             gap residuals, gap = rho*spread)
  * generated-mean update    q   += Gaussian(0, sd of q-update residuals)
  * agreement drifts          rho += Gaussian(0, sd of round-to-round rho steps)
  * observation noise         reported value += Gaussian(0, sqrt(v(1-v)/n)),
                             n = that round's value-measurement battery size,
                             applied to the REPORTED value only, not fed back.

Every residual pool is rebuilt leave-one-condition-out from the committed
records (mean/std, stdlib) so the band uses the committed noise scales, not
invented ones.  The band is the 10-90% quantile envelope over 500 seeded draws
(random.Random, stdlib).  The headline CRPS / coverage evidence line is read and
asserted straight from experiments/trajectory_adjustment_bakeoff.json (the
committed 45-run leave-one-condition-out bake-off, which used 400 numpy paths).

Palette + esc()/wrap() copied from docs/figures/src/make_figures.py (house style).
Regenerate with:  python3 spread-rollout-bakeoff.py
"""
import json
import math
import os
import random
import statistics
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
EXP = os.path.join(HERE, "..", "..", "..", "..", "experiments")
UNIFIED = os.path.join(EXP, "spread_util_unified.json")
STAGED = os.path.join(EXP, "trajectory_adjustment_bakeoff.json")

# ---- palette (house style; make_figures.py constants) --------------------
INK = "#1a1a1a"
BLUE = "#2867b5"        # the rolled-forward forecast (path + band)
GREEN = "#3a7d44"
RED = "#b5342c"
GRAY = "#6b7684"
BAND_FILL = "#cfe0f1"   # predictive band (light blue)
KEY_FILL = "#eef5ee"
FAINT = "#e4e4e0"
FONT = "Helvetica, Arial, sans-serif"


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def wrap(text, width):
    words, lines, cur = text.split(), [], ""
    for w in words:
        if len(cur) + len(w) + 1 > width and cur:
            lines.append(cur)
            cur = w
        else:
            cur = f"{cur} {w}".strip()
    if cur:
        lines.append(cur)
    return lines


def txt(x, y, s, size=18, color=INK, weight="normal", anchor="start"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{FONT}" '
            f'font-size="{size}" fill="{color}" font-weight="{weight}" '
            f'text-anchor="{anchor}">{esc(s)}</text>')


def rect(x, y, w, h, fill, stroke="none", sw=0, rx=0):
    st = f' stroke="{stroke}" stroke-width="{sw}"' if stroke != "none" else ""
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" '
            f'rx="{rx}" fill="{fill}"{st}/>')


def line(x1, y1, x2, y2, color, sw=1.0, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{sw}"{d}/>')


def polyline(pts, color, sw, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    p = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    return (f'<polyline points="{p}" fill="none" stroke="{color}" '
            f'stroke-width="{sw}"{d} stroke-linejoin="round"/>')


# ======================================================================
# read data + rebuild the committed staged-noise recipe (stdlib)
# ======================================================================
with open(UNIFIED) as f:
    RECORDS = json.load(f)["records"]
with open(STAGED) as f:
    ST = json.load(f)

# --- committed evidence numbers (asserted, not transcribed) ---------------
PRI = ST["primary_selection_driven_plus_swap"]
DET_V = PRI["unit_core_deterministic"]
STG_V = PRI["unit_core_selector_q_observation_rho_persistence_gaussian"]
assert DET_V["n_runs"] == 45 and STG_V["n_runs"] == 45, "expected 45-run set"
DET_CRPS = DET_V["endpoint_crps"]
STG_CRPS = STG_V["endpoint_crps"]
DET_COV = DET_V["endpoint_80pct_coverage"]
STG_COV = STG_V["endpoint_80pct_coverage"]
assert round(DET_CRPS, 3) == 0.135, DET_CRPS
assert round(STG_CRPS, 3) == 0.092, STG_CRPS
assert round(DET_COV, 2) == 0.22, DET_COV
assert round(STG_COV, 2) == 0.89, STG_COV


def run_key(r):
    return (r["cond"], r["seed"], r["source"])


_groups = defaultdict(list)
for _r in RECORDS:
    _groups[run_key(_r)].append(_r)
RUNS = {k: sorted(v, key=lambda r: r["round"]) for k, v in _groups.items()
        if len(v) >= 2 and min(r["round"] for r in v) == 1}


def _std(xs):
    return statistics.pstdev(xs) if len(xs) > 1 else 0.0


def _transitions(rows):
    by = {r["round"]: r for r in rows}
    return [(by[t], by[t + 1]) for t in by if t + 1 in by]


def residual_scales(cond, axis):
    """Leave-one-condition-out gaussian innovation SDs, axis-restricted,
    exactly the unit-core residual pools of analysis_trajectory_adjustments.py."""
    train = [r for r in RECORDS if r["cond"] != cond]
    gap = [r["gap"] - r["rho"] * r["mean_item_sd"]
           for r in train if r["axis"] == axis and r["rho"] is not None]
    q_res, rho_res = [], []
    tg = defaultdict(list)
    for r in train:
        tg[run_key(r)].append(r)
    for rows in tg.values():
        if rows[0]["axis"] != axis:
            continue
        for a, b in _transitions(sorted(rows, key=lambda r: r["round"])):
            q_res.append((b["own_mean"] - a["own_mean"]) - a["self_relative_gap"])
            if a["rho"] is not None and b["rho"] is not None:
                rho_res.append(b["rho"] - a["rho"])
    return _std(gap), _std(q_res), _std(rho_res)


def meas_sd(v, n):
    if not n or n <= 0:
        return 0.0
    v = min(1.0, max(0.0, v))
    return math.sqrt(max(0.0, v * (1.0 - v)) / n)


def rollout(rows, n_paths=500, seed=4242):
    """Deterministic unit path + 500 staged-noise draws for one held-out run."""
    first = rows[0]
    sigma = first["own_spread"]
    u = float(first.get("pool_cogen_fraction") or 0.0) \
        if first["composition"] != "self-only" else 0.0
    s_mean = float(first["cogen_mean"]) if first["composition"] != "self-only" else 0.0
    sg, sq, sr = residual_scales(first["cond"], first["axis"])

    def one(noisy, rng):
        q, value, rho = first["own_mean"], first["value"], first["rho"]
        out = [value]
        for obs in rows:
            pool = (1.0 - u) * q + u * s_mean
            gap = rho * sigma + (rng.gauss(0.0, sg) if noisy else 0.0)
            kept = min(1.0, max(0.0, pool + gap))
            q = min(1.0, max(0.0, q + (kept - q) + (rng.gauss(0.0, sq) if noisy else 0.0)))
            value = min(1.0, max(0.0, value + (kept - value)))
            if noisy:
                rho = min(1.0, max(-1.0, rho + rng.gauss(0.0, sr)))
            reported = value
            if noisy:
                reported = min(1.0, max(0.0, value + rng.gauss(
                    0.0, meas_sd(value, obs.get("next_value_measurement_n")))))
            out.append(reported)
        return out

    det = one(False, random.Random(0))
    rng = random.Random(seed)
    paths = [one(True, rng) for _ in range(n_paths)]
    return det, paths


def quantile(xs, q):
    xs = sorted(xs)
    i = q * (len(xs) - 1)
    lo = int(i)
    hi = min(lo + 1, len(xs) - 1)
    return xs[lo] * (1 - (i - lo)) + xs[hi] * (i - lo)


def observed(rows):
    return [rows[0]["value"]] + [r["value"] + r["drift"] for r in rows]


def find(cond, seed):
    for k, rows in RUNS.items():
        if k[0] == cond and str(k[1]) == str(seed):
            return rows
    raise KeyError((cond, seed))


# three diverse held-out runs: rising, falling, flat/wandering, two organisms
PANELS = [
    ("frozen_cons_r0", 2, ""),
    ("selfaware_loop_grid", 44, ""),
    ("judge_opposition_oracle", 101, ""),
]


# ======================================================================
# build the SVG
# ======================================================================
W, H = 1240, 742
LEFT = 44
S = []

# ---- headline + subtitle -------------------------------------------------
S.append(txt(LEFT, 52,
             "Three held-out runs vs the forecast rolled from round 1: "
             "mean path and predictive band", 22, INK, "bold"))
S.append(txt(LEFT, 98,
             "Each panel is one held-out run. The forecast reads only round 1 "
             "— own mean, spread, agreement, value — and never sees that run's "
             "later rounds.",
             16, GRAY))

# ---- key -----------------------------------------------------------------
ky = 128
kx = LEFT
S.append(line(kx, ky - 5, kx + 34, ky - 5, INK, 3))
S.append(f'<circle cx="{kx + 17}" cy="{ky - 5}" r="4" fill="{INK}"/>')
S.append(txt(kx + 42, ky, "observed trajectory (measured value each round)", 16, INK))
kx = 470
S.append(line(kx, ky - 5, kx + 34, ky - 5, BLUE, 3, dash="7 5"))
S.append(txt(kx + 42, ky,
             "deterministic path  k = clip(pool + rho·sigma)", 16, INK))
kx = 900
S.append(rect(kx, ky - 13, 34, 15, BAND_FILL, rx=2))
S.append(txt(kx + 42, ky,
             "predictive band (10-90%)", 16, INK))

# ---- three panels --------------------------------------------------------
PANEL_TOP = 168
PLOT_TOP = 236
PLOT_H = 300
PLOT_BOT = PLOT_TOP + PLOT_H
gap_between = 26
pw = (W - 2 * LEFT - 2 * gap_between) / 3.0
PLOT_LEFT_PAD = 46
plot_w = pw - PLOT_LEFT_PAD - 8

for idx, (cond, seed, shape) in enumerate(PANELS):
    rows = find(cond, seed)
    first = rows[0]
    det, paths = rollout(rows)
    obs = observed(rows)
    n_pts = len(obs)
    lo = [quantile([p[i] for p in paths], 0.10) for i in range(n_pts)]
    hi = [quantile([p[i] for p in paths], 0.90) for i in range(n_pts)]

    px0 = LEFT + idx * (pw + gap_between)
    plot_x0 = px0 + PLOT_LEFT_PAD
    plot_x1 = plot_x0 + plot_w

    def X(i):
        return plot_x0 + (plot_w * i / (n_pts - 1))

    def Y(v):
        return PLOT_BOT - v * PLOT_H

    # panel condition line
    axis_word = "self-report" if first["axis"] == "selfreport" else "risk"
    S.append(txt(px0, PANEL_TOP,
                 f"{'ABC'[idx]}.  {first['organism']} · judge: {first['judge']}",
                 18, INK, "bold"))
    S.append(txt(px0, PANEL_TOP + 20,
                 f"{axis_word} value · seed {seed} · self-only pool",
                 14, GRAY))
    S.append(txt(px0, PANEL_TOP + 38,
                 f"round-1 rho {first['rho']:+.2f} · spread sigma "
                 f"{first['own_spread']:.2f}", 14, GRAY))

    # y gridlines + labels
    for gv in (0.0, 0.5, 1.0):
        gy = Y(gv)
        S.append(line(plot_x0, gy, plot_x1, gy, INK if gv == 0 else FAINT,
                      1.6 if gv == 0 else 1.0))
        S.append(txt(plot_x0 - 8, gy + 5, f"{gv:g}", 14, GRAY, anchor="end"))
    S.append(line(plot_x0, PLOT_TOP, plot_x0, PLOT_BOT, INK, 1.6))

    # predictive band polygon (hi forward, lo backward)
    band = ([(X(i), Y(hi[i])) for i in range(n_pts)]
            + [(X(i), Y(lo[i])) for i in range(n_pts - 1, -1, -1)])
    poly = " ".join(f"{x:.1f},{y:.1f}" for x, y in band)
    S.append(f'<polygon points="{poly}" fill="{BAND_FILL}" '
             f'fill-opacity="0.7" stroke="none"/>')

    # deterministic path
    S.append(polyline([(X(i), Y(det[i])) for i in range(n_pts)], BLUE, 2.4,
                      dash="7 5"))
    # observed path + dots
    S.append(polyline([(X(i), Y(obs[i])) for i in range(n_pts)], INK, 2.8))
    for i in range(n_pts):
        S.append(f'<circle cx="{X(i):.1f}" cy="{Y(obs[i]):.1f}" r="4.2" '
                 f'fill="{INK}"/>')

    # x axis label
    S.append(txt((plot_x0 + plot_x1) / 2, PLOT_BOT + 26,
                 "selection round →", 14, GRAY, anchor="middle"))

# ---- evidence line box ---------------------------------------------------
ey = PLOT_BOT + 50
eh = 64
S.append(rect(LEFT, ey, W - 2 * LEFT, eh, KEY_FILL, stroke=GREEN, sw=1.6, rx=10))
S.append(txt(LEFT + 18, ey + 26,
             "45 held-out runs (leave-one-condition-out), endpoint coverage of "
             "the nominal-80% band:", 16, INK, "bold"))
S.append(txt(LEFT + 18, ey + 50,
             f"deterministic path alone {DET_COV:.0%} (CRPS {DET_CRPS:.3f})   ·   "
             f"with staged noise {STG_COV:.0%} (CRPS {STG_CRPS:.3f})", 16, INK))

# ---- source footnote -----------------------------------------------------
fy = ey + eh + 24
S.append(txt(LEFT, fy,
             "Panels: deterministic path and band regenerated with stdlib from "
             "experiments/spread_util_unified.json first-round state via the "
             "committed unit recurrence and staged-noise residual pools.",
             13, GRAY))
S.append(txt(LEFT, fy + 18,
             "Evidence line read and asserted from "
             "experiments/trajectory_adjustment_bakeoff.json "
             "(primary_selection_driven_plus_swap).  Generator: "
             "spread-rollout-bakeoff.py",
             13, GRAY))

svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
       f'font-family="{FONT}">\n'
       f'<rect width="{W}" height="{H}" fill="white"/>\n'
       + "\n".join(S) + "\n</svg>")

out = os.path.join(HERE, "spread-rollout-bakeoff.svg")
with open(out, "w") as f:
    f.write(svg)
print(f"wrote {out}  viewBox 0 0 {W} {H}")
