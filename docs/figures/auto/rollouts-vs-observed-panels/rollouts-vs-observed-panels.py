#!/usr/bin/env python3
"""Small-multiples: simulated rollout ensembles vs observed trajectories,
one panel per condition cell (slug: rollouts-vs-observed-panels).

Each panel is one condition cell -- one organism x axis x judge x format x
composition, holding a single experimental condition, with several seeds.  The
SIMULATION recipe is IDENTICAL to the committed sibling generator
docs/figures/auto/spread-rollout-bakeoff/spread-rollout-bakeoff.py: the
parameter-free UNIT RECURRENCE rolled forward from each seed's round-1 state
plus the committed "staged-noise" residual pools (the
`unit_core_selector_q_observation_rho_persistence_gaussian` variant of
scripts/analysis_trajectory_adjustments.py).  rollout(), residual_scales(),
meas_sd(), quantile(), observed() and the residual construction are copied
verbatim from that generator so the simulation is the same procedure.

Per panel: the shaded band is the pooled 10-90% quantile envelope over
~300 seeded draws PER SEED (each seed rolled from its OWN round-1 state, all
pooled within the panel), the dashed line is the pooled ensemble median, and the
thin solid dark lines are the OBSERVED trajectories -- one per seed, all in the
same ink color.  Noise scales come from the committed residual pools, not
invented.

Cells shown were chosen for being homogeneous (single condition, self-only
pool, all four rounds) with >= 3 seeds:
  Qwen  risk vs reference  self-judge          (cond evolving_self,   4 seeds)
  Qwen  risk vs reference  frozen base-judge   (cond frozen_base,     4 seeds)
  Qwen  risk vs reference  frozen self-copy    (cond frozen_copy_r0,  4 seeds)
  OLMo  risk vs reference  frozen cautious-copy(cond frozen_cons_r0,  4 seeds)
  OLMo  risk vs reference  frozen base-judge   (cond frozen_base,     6 seeds)

The aggregate coverage line is read and asserted straight from
experiments/trajectory_adjustment_bakeoff.json (primary_selection_driven_plus_swap).

Palette + esc()/wrap() copied from docs/figures/src/make_figures.py (house style).
Regenerate with:  python3 rollouts-vs-observed-panels.py
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
BLUE = "#2867b5"        # the simulated rollout ensemble (band + median)
GREEN = "#3a7d44"
RED = "#b5342c"
GRAY = "#6b7684"
BAND_FILL = "#cfe0f1"   # simulated predictive band (light blue)
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


def rollout(rows, n_paths=300, seed=4242):
    """Deterministic unit path + staged-noise draws for one seed's run."""
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


# ======================================================================
# select condition cells (homogeneous: single cond, self-only, all 4 rounds)
# each entry: organism, axis, judge, format, composition, cond, judge_label
# ======================================================================
CELLS = [
    ("Qwen", "risk", "self", "reference", "self-only", "evolving_self",
     "self-judge (re-copied each round)"),
    ("Qwen", "risk", "base", "reference", "self-only", "frozen_base",
     "frozen base-model judge"),
    ("Qwen", "risk", "frozen copy", "reference", "self-only", "frozen_copy_r0",
     "frozen self-copy judge"),
    ("OLMo", "risk", "cautious copy", "reference", "self-only", "frozen_cons_r0",
     "frozen cautious-copy judge"),
    ("OLMo", "risk", "base", "reference", "self-only", "frozen_base",
     "frozen base-model judge"),
]


def cell_runs(org, axis, judge, fmt, comp, cond):
    out = []
    for k, rows in RUNS.items():
        f = rows[0]
        if (f["organism"], f["axis"], f["judge"], f["format"],
                f["composition"], f["cond"]) == (org, axis, judge, fmt, comp, cond):
            out.append(rows)
    return sorted(out, key=lambda rs: str(rs[0]["seed"]))


# ======================================================================
# build the SVG
# ======================================================================
W = 1300
LEFT = 44
COLS = 3
ROWS = 2
COLGAP = 30
ROWGAP = 46

# ---- headline + subtitle -------------------------------------------------
S = []
S.append(txt(LEFT, 50,
             "Simulated rollout ensembles vs observed trajectories, by "
             "condition", 24, INK, "bold"))
S.append(txt(LEFT, 82,
             "Each panel is one condition cell. The ensemble (band + median) is "
             "rolled forward from every seed's round-1 state only; the dark lines "
             "are that cell's measured runs.",
             16, GRAY))

# ---- shared key ----------------------------------------------------------
ky = 118
kx = LEFT
S.append(rect(kx, ky - 13, 34, 15, BAND_FILL, rx=2))
S.append(txt(kx + 42, ky, "simulated ensemble, 10-90% band", 15, INK))
kx = 360
S.append(line(kx, ky - 5, kx + 34, ky - 5, BLUE, 2.6, dash="7 5"))
S.append(txt(kx + 42, ky, "simulated ensemble median", 15, INK))
kx = 640
S.append(line(kx, ky - 5, kx + 34, ky - 5, INK, 2.0))
S.append(txt(kx + 42, ky, "observed trajectory (one thin line per seed)", 15, INK))

# ---- panel grid ----------------------------------------------------------
GRID_TOP = 150
cell_w = (W - 2 * LEFT - (COLS - 1) * COLGAP) / COLS
PLOT_LEFT_PAD = 44
HEAD_H = 40           # space above plot for the two-line panel header
PLOT_H = 200
plot_w = cell_w - PLOT_LEFT_PAD - 6
cell_h = HEAD_H + PLOT_H + 30   # header + plot + x-axis label region


def draw_panel(col, row, cell):
    org, axis, judge, fmt, comp, cond, jlabel = cell
    runs = cell_runs(org, axis, judge, fmt, comp, cond)
    n_seeds = len(runs)

    px0 = LEFT + col * (cell_w + COLGAP)
    py0 = GRID_TOP + row * (cell_h + ROWGAP)
    plot_x0 = px0 + PLOT_LEFT_PAD
    plot_x1 = plot_x0 + plot_w
    plot_top = py0 + HEAD_H
    plot_bot = plot_top + PLOT_H

    # pooled simulated draws + per-seed observed, all seeds share n_pts
    n_pts = len(observed(runs[0]))
    det0, _ = rollout(runs[0])
    pooled = []
    obs_lines = []
    for si, rows in enumerate(runs):
        _, paths = rollout(rows, seed=4242 + 101 * si)
        pooled.extend(paths)
        obs_lines.append(observed(rows))
    lo = [quantile([p[i] for p in pooled], 0.10) for i in range(n_pts)]
    hi = [quantile([p[i] for p in pooled], 0.90) for i in range(n_pts)]
    med = [quantile([p[i] for p in pooled], 0.50) for i in range(n_pts)]

    def X(i):
        return plot_x0 + (plot_w * i / (n_pts - 1))

    def Y(v):
        v = min(1.0, max(0.0, v))
        return plot_bot - v * PLOT_H

    # panel header (condition identification only)
    S.append(txt(px0, py0 + 14, f"{org} - risk - vs reference", 17, INK, "bold"))
    S.append(txt(px0, py0 + 33,
                 f"{jlabel} - {n_seeds} seeds", 14, GRAY))

    # y gridlines + labels
    for gv in (0.0, 0.5, 1.0):
        gy = Y(gv)
        S.append(line(plot_x0, gy, plot_x1, gy, INK if gv == 0 else FAINT,
                      1.4 if gv == 0 else 1.0))
        S.append(txt(plot_x0 - 8, gy + 5, f"{gv:g}", 13, GRAY, anchor="end"))
    S.append(line(plot_x0, plot_top, plot_x0, plot_bot, INK, 1.4))

    # simulated band polygon
    band = ([(X(i), Y(hi[i])) for i in range(n_pts)]
            + [(X(i), Y(lo[i])) for i in range(n_pts - 1, -1, -1)])
    poly = " ".join(f"{x:.1f},{y:.1f}" for x, y in band)
    S.append(f'<polygon points="{poly}" fill="{BAND_FILL}" '
             f'fill-opacity="0.75" stroke="none"/>')
    # simulated median
    S.append(polyline([(X(i), Y(med[i])) for i in range(n_pts)], BLUE, 2.4,
                      dash="7 5"))
    # observed trajectories (thin, one per seed, same ink color)
    for ol in obs_lines:
        S.append(polyline([(X(i), Y(ol[i])) for i in range(n_pts)], INK, 1.6))
        S.append(f'<circle cx="{X(0):.1f}" cy="{Y(ol[0]):.1f}" r="2.6" '
                 f'fill="{INK}"/>')

    # x-axis label
    S.append(txt((plot_x0 + plot_x1) / 2, plot_bot + 24,
                 "selection round ->", 13, GRAY, anchor="middle"))
    S.append(txt(plot_x0, plot_bot + 24, "value 0–1", 13, GRAY))


positions = [(0, 0), (1, 0), (2, 0), (0, 1), (1, 1)]
for pos, cell in zip(positions, CELLS):
    draw_panel(pos[0], pos[1], cell)

# The aggregate coverage/CRPS line and the source footnote live in caption.md,
# not on the figure (the writeup carries anything load-bearing). The bakeoff
# numbers are still read and asserted above (DET_COV/STG_COV/DET_CRPS/STG_CRPS)
# so the generator fails loudly if they ever drift.
grid_bottom = GRID_TOP + 2 * (cell_h + ROWGAP) - ROWGAP
H = int(grid_bottom + 22)
svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
       f'font-family="{FONT}">\n'
       f'<rect width="{W}" height="{H}" fill="white"/>\n'
       + "\n".join(S) + "\n</svg>")

out = os.path.join(HERE, "rollouts-vs-observed-panels.svg")
with open(out, "w") as f:
    f.write(svg)
print(f"wrote {out}  viewBox 0 0 {W} {H}")
