#!/usr/bin/env python3
"""Sampled-rollout spaghetti vs observed spaghetti, grouped by experiment family
(slug: rollouts-vs-observed-spaghetti).

Three wide panels, one per experiment family that carries many runs:

  A  Qwen risk grid          (self-only; judges: self / base / frozen copy / random)
  B  OLMo risk self-only     (frozen-judge grid + judge schedules)
  C  OLMo mixed-pool runs    (base- and peer-mixed invade / erode / rescue / oracle)

Judge-swap and self-report-axis runs are out of scope for this figure (the three
risk families above are the ones with the most runs).

For every run in a family the generator reads ONLY that run's first-round pool
state from experiments/spread_util_unified.json -- own candidate mean q, own
within-prompt spread sigma (own_spread), agreement rho, behavioral value v, and
(for mixed pools) supplier share u and supplier mean s -- and draws a handful of
SIMULATED trajectories forward with the committed parameter-free UNIT RECURRENCE
plus the committed "staged-noise" recipe:

    pool     p = (1 - u) * q + u * s
    kept     k = clip( p + rho*sigma + N(0, gap-residual sd) , 0, 1 )
    next q   q += (k - q) + N(0, q-update-residual sd)
    rho      += N(0, rho-step sd)
    reported value += N(0, sqrt(v(1-v)/n))   (observation noise on the readout)

Every residual sd is rebuilt leave-one-condition-out from the committed records
(stdlib mean/std), seeded RNG (random.Random) -- no invented noise parameters.
The rollout() / residual_scales() / meas_sd() functions are copied verbatim from
docs/figures/auto/spread-rollout-bakeoff/spread-rollout-bakeoff.py.

The light-gray cloud is those simulated draws (a few per run); the blue lines are
the ALL observed trajectories (one per run, measured value each round) drawn on
top.  esc()/wrap() + palette copied from docs/figures/src/make_figures.py.

Regenerate with:  python3 rollouts-vs-observed-spaghetti.py
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
BLUE = "#2867b5"        # observed trajectories
GREEN = "#3a7d44"
RED = "#b5342c"
GRAY = "#6b7684"        # recessive axes / captions
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


def polyline(pts, color, sw, dash=None, opacity=1.0):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    o = f' stroke-opacity="{opacity}"' if opacity != 1.0 else ""
    p = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    return (f'<polyline points="{p}" fill="none" stroke="{color}" '
            f'stroke-width="{sw}"{d}{o} stroke-linejoin="round" '
            f'stroke-linecap="round"/>')


# ======================================================================
# read data + committed staged-noise recipe (copied verbatim from
# spread-rollout-bakeoff.py: run_key / residual_scales / meas_sd / rollout)
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


def rollout(rows, n_paths=3, seed=4242):
    """Deterministic unit path + staged-noise draws for one run's round-1 state."""
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


def observed(rows):
    return [rows[0]["value"]] + [r["value"] + r["drift"] for r in rows]


def judge_swaps(rows):
    return len(set(r["judge"] for r in rows)) > 1


# ======================================================================
# assemble the three families (the risk families with the most runs)
# ======================================================================
def family_of(rows):
    f = rows[0]
    if judge_swaps(rows):
        return None
    org, axis, comp = f["organism"], f["axis"], f["composition"]
    if org == "Qwen" and axis == "risk":
        return "A"
    if org == "OLMo" and axis == "risk" and comp == "self-only":
        return "B"
    if org == "OLMo" and axis == "risk" and comp in ("base-mixed", "peer-mixed"):
        return "C"
    return None


FAM_RUNS = defaultdict(list)
for _k, _rows in RUNS.items():
    _fam = family_of(_rows)
    if _fam is not None:
        FAM_RUNS[_fam].append(_rows)

# Exactly one simulated draw per run. A run can only seed a rollout if it has a
# round-1 agreement reading (rho); a few runs do not, so they contribute an
# observed line but no simulated draw (honest count shown in the panel sub-line).
PANELS = [
    ("A", "Qwen risk grid", "self-only pool; judges self / base / frozen / random"),
    ("B", "OLMo risk self-only", "frozen-judge grid + judge schedules"),
    ("C", "OLMo mixed-pool", "base- and peer-mixed invade / erode / rescue / oracle"),
]


def can_sim(rows):
    return rows[0]["rho"] is not None


# report run + draw counts to stdout (for STATE line) and figure labels.
# One simulated draw per run; a run seeds a draw only if it has round-1 rho.
COUNTS = {}
for fam, _, _ in PANELS:
    runs = FAM_RUNS[fam]
    sim_runs = [r for r in runs if can_sim(r)]
    COUNTS[fam] = (len(runs), len(sim_runs))


# ======================================================================
# build the SVG  --  3 family columns, each a stacked pair:
#   top    = simulated (one draw per run)
#   bottom = observed
# same axes / scale / line styling in both halves (texture vs texture)
# ======================================================================
W, H = 1440, 796
LEFT = 46
S = []

# shared line styling used identically in both halves
LINE_COL = BLUE
LINE_SW = 1.4
LINE_OP = 0.62

BAND_FILL = "#cfe0f1"   # simulated-ensemble 10-90% band

# ---- headline + one subtitle line ---------------------------------------
S.append(txt(LEFT, 46,
             "Sampled rollouts and observed trajectories, three experiment families",
             24, INK, "bold"))
S.append(txt(LEFT, 74,
             "Per family, two panels on identical axes: top row is the runs as "
             "actually observed; bottom row is one simulated rollout per run from "
             "its round-1 pool state.", 16, GRAY))

# ---- one-line legend: band + trajectory line -----------------------------
_lx = LEFT
S.append(f'<rect x="{_lx}" y="94" width="26" height="13" fill="{BAND_FILL}" '
         f'fill-opacity="0.75"/>')
S.append(txt(_lx + 33, 105, "simulated ensemble 10–90% band", 14, GRAY))
_lx2 = _lx + 300
S.append(line(_lx2, 100, _lx2 + 26, 100, LINE_COL, LINE_SW))
S.append(txt(_lx2 + 33, 105, "one trajectory per run", 14, GRAY))

# ---- one short draw-count note (kept per user directive) -----------------
_note = ("A simulated draw needs a measurable round-1 agreement (ρ): "
         + ", ".join(f"panel {fam} {COUNTS[fam][1]} of {COUNTS[fam][0]}"
                     for fam, _, _ in PANELS)
         + " runs seed a draw; the rest appear only as an observed line.")
S.append(txt(LEFT, 130, _note, 14, GRAY))

# ---- geometry ------------------------------------------------------------
HEADER_Y = 168           # column header baseline
SUB_Y = HEADER_Y + 20    # column sub-line baseline
PLOT1_TOP = 230
PLOT_H = 206
PLOT1_BOT = PLOT1_TOP + PLOT_H
PLOT2_TOP = PLOT1_BOT + 84   # room for x-axis of plot 1 + observed row label
PLOT2_BOT = PLOT2_TOP + PLOT_H

gap_between = 30
pw = (W - 2 * LEFT - 2 * gap_between) / 3.0
PLOT_LEFT_PAD = 44
plot_w = pw - PLOT_LEFT_PAD - 6


def quantile(xs, q):
    xs = sorted(xs)
    i = q * (len(xs) - 1)
    lo = int(i)
    hi = min(lo + 1, len(xs) - 1)
    return xs[lo] * (1 - (i - lo)) + xs[hi] * (i - lo)


def draw_plot(plot_x0, plot_top, plot_bot, max_round, trajectories, row_label,
              band=None):
    """One half-panel: axes + a bundle of trajectories (list of value-lists).
    band = optional list of (round_index, lo, hi) drawn as a filled region
    behind the trajectories."""
    plot_x1 = plot_x0 + plot_w

    def X(rnd):
        return plot_x0 + (plot_w * rnd / max_round)

    def Y(v):
        return plot_bot - v * (plot_bot - plot_top)

    out = []
    # row label
    out.append(txt(plot_x0 - PLOT_LEFT_PAD, plot_top - 12, row_label, 15, INK, "bold"))
    # y gridlines + labels
    for gv in (0.0, 0.5, 1.0):
        gy = Y(gv)
        out.append(line(plot_x0, gy, plot_x1, gy, INK if gv == 0 else FAINT,
                        1.6 if gv == 0 else 1.0))
        out.append(txt(plot_x0 - 8, gy + 5, f"{gv:g}", 14, GRAY, anchor="end"))
    out.append(line(plot_x0, plot_top, plot_x0, plot_bot, INK, 1.6))
    # x ticks (rounds)
    for rnd in range(0, max_round + 1):
        tx = X(rnd)
        out.append(line(tx, plot_bot, tx, plot_bot + 5, GRAY, 1.0))
        lbl = "start" if rnd == 0 else str(rnd)
        out.append(txt(tx, plot_bot + 22, lbl, 12, GRAY, anchor="middle"))
    # x axis label
    out.append(txt((plot_x0 + plot_x1) / 2, plot_bot + 44,
                   "selection round →", 14, GRAY, anchor="middle"))
    # simulated-ensemble band first, so every line sits on top of it
    if band:
        top_pts = [(X(i), Y(hi)) for i, lo, hi in band]
        bot_pts = [(X(i), Y(lo)) for i, lo, hi in reversed(band)]
        d = " ".join(f"{px:.1f},{py:.1f}" for px, py in top_pts + bot_pts)
        out.append(f'<polygon points="{d}" fill="{BAND_FILL}" '
                   f'fill-opacity="0.75"/>')
    # trajectory bundle (identical styling in both halves)
    for path in trajectories:
        pts = [(X(i), Y(path[i])) for i in range(len(path))]
        out.append(polyline(pts, LINE_COL, LINE_SW, opacity=LINE_OP))
    return out


for idx, (fam, name, sub) in enumerate(PANELS):
    runs = FAM_RUNS[fam]
    sim_runs = [r for r in runs if can_sim(r)]
    n_runs = len(runs)
    n_sim = len(sim_runs)
    max_round = max(len(r) for r in runs)

    px0 = LEFT + idx * (pw + gap_between)
    plot_x0 = px0 + PLOT_LEFT_PAD

    # column header + honest counts
    S.append(txt(px0, HEADER_Y, f"{fam}.  {name}   ({n_runs} runs)", 19, INK, "bold"))
    S.append(txt(px0, SUB_Y, sub, 14, GRAY))
    if fam == "C":
        # user request: say which value axis panel C carries, with counts
        S.append(txt(px0, SUB_Y + 16, "all 20 runs are risk-value; "
                     "0 insecure-code (that family is not in this figure)",
                     13, GRAY))

    # DRAWSETS pre-sampled draw-sets (one draw per sim-able run each) so the
    # published page can re-simulate by toggling <g> visibility — set 0 is the
    # original seed and is the one visible in static contexts. Plus a larger
    # ensemble (30 draws per run) for the 10-90% band.
    DRAWSETS = 24
    sim_sets = []
    for ds in range(DRAWSETS):
        sims = []
        for j, rows in enumerate(sim_runs):
            _, paths = rollout(rows, n_paths=1,
                               seed=1000 * (idx + 1) + j + 100000 * ds)
            sims.append(paths[0])
        sim_sets.append(sims)
    ensemble = []
    for j, rows in enumerate(sim_runs):
        _, band_paths = rollout(rows, n_paths=30, seed=7000 * (idx + 1) + j)
        ensemble.extend(band_paths)
    band = []
    for i in range(max_round + 1):
        vals = [p[i] for p in ensemble if len(p) > i]
        if len(vals) >= 10:
            band.append((i, quantile(vals, 0.10), quantile(vals, 0.90)))
    obs = [observed(rows) for rows in runs]

    S.extend(draw_plot(plot_x0, PLOT1_TOP, PLOT1_BOT, max_round, obs,
                       f"observed  ({n_runs} runs)"))
    # the draw-set groups (polylines only), first visible, rest hidden
    def _XY(rnd, v):
        return (plot_x0 + (plot_w * rnd / max_round),
                PLOT2_BOT - v * (PLOT2_BOT - PLOT2_TOP))
    for ds, sims in enumerate(sim_sets):
        vis = '' if ds == 0 else ' style="display:none"'
        S.append(f'<g class="simset" data-set="{ds}"{vis}>')
        for path in sims:
            pts = [_XY(i, path[i]) for i in range(len(path))]
            S.append(polyline(pts, LINE_COL, LINE_SW, opacity=LINE_OP))
        S.append('</g>')
    S.extend(draw_plot(plot_x0, PLOT2_TOP, PLOT2_BOT, max_round, [],
                       f"simulated  ({n_sim} of {n_runs} runs)",
                       band=band))

    # y axis label (leftmost column only)
    if idx == 0:
        for pt, pb in ((PLOT1_TOP, PLOT1_BOT), (PLOT2_TOP, PLOT2_BOT)):
            cy = (pt + pb) / 2
            S.append(f'<text x="{px0 - 6}" y="{cy:.1f}" font-family="{FONT}" '
                     f'font-size="13" fill="{GRAY}" text-anchor="middle" '
                     f'transform="rotate(-90 {px0 - 6} {cy:.1f})">'
                     f'behavioral value (0-1)</text>')

# ---- no in-figure footnote: provenance lives in caption.md ----------------

svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
       f'font-family="{FONT}">\n'
       f'<rect width="{W}" height="{H}" fill="white"/>\n'
       + "\n".join(S) + "\n</svg>")

out = os.path.join(HERE, "rollouts-vs-observed-spaghetti.svg")
with open(out, "w") as f:
    f.write(svg)
print(f"wrote {out}  viewBox 0 0 {W} {H}")
for fam, name, _ in PANELS:
    nr, ns = COUNTS[fam]
    print(f"  {fam} {name}: {nr} runs, {ns} simulated draws (1/run)")
