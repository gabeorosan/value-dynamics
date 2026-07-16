#!/usr/bin/env python3
"""Simulated endpoint distributions vs observed endpoints, by condition group
(slug: rollouts-vs-observed-endpoints).

One column per condition group (organism x judge x format x pool composition,
risk axis, >=2 runs each).  For every member run the generator reads ONLY the
run's first-round pool state from experiments/spread_util_unified.json and rolls
the committed parameter-free UNIT RECURRENCE forward to the run's own final
round, adding noise ONLY where the measurement implies it (the committed
"staged-noise" recipe).  It keeps 300 seeded draws of the FINAL reported value
per run and pools them across the runs in the group -> the light-blue violin.
The observed final values (last-round value + drift, one per run/seed) are
overlaid as dark dots.

The simulator is copied VERBATIM from
docs/figures/auto/spread-rollout-bakeoff/spread-rollout-bakeoff.py
(unit recurrence from each run's round-1 state, committed leave-one-condition-out
residual pools rebuilt with stdlib, seeded random.Random).  The only change is
that this figure keeps the final-round draws and pools them per group instead of
plotting three time-series panels.

Palette + esc()/wrap() copied from docs/figures/src/make_figures.py (house style).
Regenerate with:  python3 rollouts-vs-observed-endpoints.py
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

# ---- palette (house style; make_figures.py constants) --------------------
INK = "#1a1a1a"
BLUE = "#2867b5"        # self-judge series
GREEN = "#3a7d44"       # frozen-judge series
RED = "#b5342c"
GRAY = "#6b7684"
BAND_FILL = "#cfe0f1"   # simulated endpoint density (light blue)
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


# ======================================================================
# read data + rebuild the committed staged-noise recipe (stdlib) -- VERBATIM
# from spread-rollout-bakeoff.py, except rollout() default n_paths.
# ======================================================================
with open(UNIFIED) as f:
    RECORDS = json.load(f)["records"]


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


def rollout(rows, n_paths=300, seed=4242):
    """Deterministic unit path + staged-noise draws for one held-out run."""
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


def observed_final(rows):
    last = rows[-1]
    return min(1.0, max(0.0, last["value"] + last["drift"]))


def quantile(xs, q):
    xs = sorted(xs)
    i = q * (len(xs) - 1)
    lo = int(i)
    hi = min(lo + 1, len(xs) - 1)
    return xs[lo] * (1 - (i - lo)) + xs[hi] * (i - lo)


# ======================================================================
# assemble condition groups (risk axis; >=2 runs; constant judge per run)
# ======================================================================
def cell(rows):
    f = rows[0]
    return (f["organism"], f["judge"], f["format"], f["composition"], f["axis"])


CELLS = defaultdict(list)
for _k, _rows in RUNS.items():
    CELLS[cell(_rows)].append(_rows)

# Curated group order: Qwen risk grid, then OLMo risk cells + two mixed pools.
# (The Qwen random-judge cell is excluded: random selection has no judge/value
#  agreement, so round-1 rho is undefined and the recurrence cannot roll it.)
GROUP_SPECS = [
    ("Qwen", "self", "reference", "self-only", "risk"),
    ("Qwen", "base", "reference", "self-only", "risk"),
    ("Qwen", "frozen copy", "reference", "self-only", "risk"),
    ("OLMo", "base", "reference", "self-only", "risk"),
    ("OLMo", "schedule", "reference", "self-only", "risk"),
    ("OLMo", "cautious copy", "reference", "self-only", "risk"),
    ("OLMo", "base", "duel", "base-mixed", "risk"),
    ("OLMo", "self", "duel", "base-mixed", "risk"),
]

GROUPS = []
for spec in GROUP_SPECS:
    member_runs = [rw for rw in CELLS.get(spec, []) if rw[0]["rho"] is not None]
    assert len(member_runs) >= 2, f"group {spec} has <2 rollable runs ({len(member_runs)})"
    sim_pool = []
    observed = []
    for rows in member_runs:
        _det, paths = rollout(rows)
        sim_pool.extend(p[-1] for p in paths)
        observed.append(observed_final(rows))
    GROUPS.append({
        "spec": spec,
        "n": len(member_runs),
        "self_judge": spec[1] == "self",
        "sim": sim_pool,
        "obs": sorted(observed),
    })

# no within-run judge swaps exist in this file; assert so the label is honest
for _k, _rows in RUNS.items():
    assert len({r["judge"] for r in _rows}) == 1, f"judge swap in {_k}"


# ======================================================================
# build the SVG
# ======================================================================
W, H = 1360, 812
LEFT = 92
RIGHT = 40
S = []

# ---- headline + subtitle -------------------------------------------------
S.append(txt(LEFT, 50,
             "Simulated endpoint distributions and observed endpoints, by "
             "condition group", 23, INK, "bold"))
S.append(txt(LEFT, 82,
             "Each column is one condition cell (organism x judge x format x "
             "pool). Light-blue shape = distribution of simulated final-round "
             "values pooled over the cell's runs.", 15, GRAY))
S.append(txt(LEFT, 104,
             "Dark dots = the observed final value of each real run (one dot "
             "per run/seed). y = value on the 0-1 scale.", 15, GRAY))

# ---- key -----------------------------------------------------------------
ky = 138
kx = LEFT
S.append(rect(kx, ky - 13, 30, 15, BAND_FILL, rx=2))
S.append(txt(kx + 38, ky, "simulated final-round value (300 draws per run, "
            "pooled over the cell)", 15, INK))
kx = 700
S.append(f'<circle cx="{kx + 8}" cy="{ky - 5}" r="6" fill="{BLUE}"/>')
S.append(txt(kx + 24, ky, "observed endpoint, self-judge run", 15, INK))
kx = 1010
S.append(f'<circle cx="{kx + 8}" cy="{ky - 5}" r="6" fill="{GREEN}"/>')
S.append(txt(kx + 24, ky, "observed endpoint, frozen/external-judge run", 15, INK))

# ---- plot frame ----------------------------------------------------------
PLOT_TOP = 176
PLOT_H = 384
PLOT_BOT = PLOT_TOP + PLOT_H
plot_x0 = LEFT
plot_x1 = W - RIGHT
plot_w = plot_x1 - plot_x0
ng = len(GROUPS)
col_w = plot_w / ng
half = col_w * 0.40   # max half-width of a violin


def Y(v):
    return PLOT_BOT - v * PLOT_H


def CX(i):
    return plot_x0 + col_w * (i + 0.5)


# y gridlines + labels
for gv in (0.0, 0.25, 0.5, 0.75, 1.0):
    gy = Y(gv)
    S.append(line(plot_x0, gy, plot_x1, gy, INK if gv == 0 else FAINT,
                  1.6 if gv == 0 else 1.0))
    S.append(txt(plot_x0 - 12, gy + 5, f"{gv:.2f}", 14, GRAY, anchor="end"))
S.append(line(plot_x0, PLOT_TOP, plot_x0, PLOT_BOT, INK, 1.6))
_yl_x, _yl_y = plot_x0 - 64, (PLOT_TOP + PLOT_BOT) / 2
S.append(f'<text x="{_yl_x:.1f}" y="{_yl_y:.1f}" font-family="{FONT}" '
         f'font-size="15" fill="{GRAY}" text-anchor="middle" '
         f'transform="rotate(-90 {_yl_x:.1f} {_yl_y:.1f})">value</text>')

# faint column separators
for i in range(1, ng):
    x = plot_x0 + col_w * i
    S.append(line(x, PLOT_TOP, x, PLOT_BOT, FAINT, 1.0))


def violin_bins(xs, nbins=40):
    """Histogram density over [0,1] with light 3-tap smoothing (stdlib)."""
    counts = [0.0] * nbins
    for v in xs:
        b = min(nbins - 1, max(0, int(v * nbins)))
        counts[b] += 1.0
    sm = [0.0] * nbins
    for i in range(nbins):
        acc = 2.0 * counts[i]
        acc += counts[i - 1] if i > 0 else 0.0
        acc += counts[i + 1] if i < nbins - 1 else 0.0
        sm[i] = acc / 4.0
    m = max(sm) or 1.0
    return [c / m for c in sm], nbins


# ---- draw violins + observed dots ----------------------------------------
for i, g in enumerate(GROUPS):
    cx = CX(i)
    dens, nbins = violin_bins(g["sim"])
    # symmetric violin polygon
    left_pts, right_pts = [], []
    for b in range(nbins):
        v = (b + 0.5) / nbins
        yb = Y(v)
        wdt = dens[b] * half
        left_pts.append((cx - wdt, yb))
        right_pts.append((cx + wdt, yb))
    poly = right_pts + left_pts[::-1]
    pstr = " ".join(f"{x:.1f},{y:.1f}" for x, y in poly)
    S.append(f'<polygon points="{pstr}" fill="{BAND_FILL}" '
             f'fill-opacity="0.85" stroke="{BLUE}" stroke-width="1.0" '
             f'stroke-opacity="0.5"/>')

    # simulated median tick
    med = quantile(sorted(g["sim"]), 0.5)
    S.append(line(cx - half * 0.55, Y(med), cx + half * 0.55, Y(med),
                  BLUE, 2.0))

    # observed dots (dark, colored by judge type), jittered horizontally
    dot_color = BLUE if g["self_judge"] else GREEN
    m = len(g["obs"])
    for j, ov in enumerate(g["obs"]):
        jx = cx + (half * 0.5) * ((j - (m - 1) / 2.0) / max(1, m)) * 1.6
        S.append(f'<circle cx="{jx:.1f}" cy="{Y(ov):.1f}" r="5.6" '
                 f'fill="{dot_color}" stroke="white" stroke-width="1.4"/>')

# ---- group labels (stacked, no rotation) ---------------------------------
JUDGE_KIND = {
    "self": "self-judge", "base": "frozen base judge",
    "frozen copy": "frozen copy judge", "random": "random judge",
    "schedule": "scheduled frozen judge", "cautious copy": "cautious copy judge",
}
lab_y = PLOT_BOT + 24
for i, g in enumerate(GROUPS):
    org, judge, fmt, comp, _axis = g["spec"]
    cx = CX(i)
    pool = "own answers only" if comp == "self-only" else f"{comp} answers"
    S.append(txt(cx, lab_y, org, 15, INK, "bold", anchor="middle"))
    S.append(txt(cx, lab_y + 20, JUDGE_KIND.get(judge, judge), 12.5, GRAY,
                 anchor="middle"))
    fmt_lab = "vs reference" if fmt == "reference" else ("duels" if fmt == "duel" else fmt)
    S.append(txt(cx, lab_y + 37, fmt_lab, 12.5, GRAY, anchor="middle"))
    S.append(txt(cx, lab_y + 54, pool, 12.5, GRAY, anchor="middle"))
    S.append(txt(cx, lab_y + 71, f"n = {g['n']} runs", 12.5, INK,
                 anchor="middle"))

# ---- source footnote -----------------------------------------------------
fy = lab_y + 100
S.append(line(LEFT, fy - 14, W - RIGHT, fy - 14, FAINT, 1.0))
S.append(txt(LEFT, fy,
             "Violins and dots regenerated with stdlib from "
             "experiments/spread_util_unified.json round-1 state via the "
             "committed unit recurrence and staged-noise residual pools "
             "(rollout copied verbatim from spread-rollout-bakeoff.py).",
             13, GRAY))
S.append(txt(LEFT, fy + 18,
             "Risk-axis condition cells with >=2 runs; no within-run judge "
             "swaps exist in this file. Generator: rollouts-vs-observed-endpoints.py",
             13, GRAY))

svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
       f'font-family="{FONT}">\n'
       f'<rect width="{W}" height="{H}" fill="white"/>\n'
       + "\n".join(S) + "\n</svg>")

out = os.path.join(HERE, "rollouts-vs-observed-endpoints.svg")
with open(out, "w") as f:
    f.write(svg)
print(f"wrote {out}  viewBox 0 0 {W} {H}")
for g in GROUPS:
    print(g["spec"], "n=", g["n"], "obs=",
          [round(x, 3) for x in g["obs"]],
          "sim_med=", round(quantile(sorted(g['sim']), 0.5), 3))
