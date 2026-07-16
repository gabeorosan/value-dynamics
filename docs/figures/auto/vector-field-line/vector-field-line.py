#!/usr/bin/env python3
"""The one-round move as a flow on the value line, one row per regime
(slug: vector-field-line).

Each row draws the model-implied one-round move as a field of arrows along the
0-1 behavioral-value line, using the writeup's parameter-free UNIT RECURRENCE

    v -> v + dv,   dv = u * (s - v) + rho * sigma,
    with sigma capped by the binary envelope  sigma <= sqrt(v * (1 - v)).

  u    supplier share in the pool (0 for a self-only pool)
  s    supplier's mean value (only matters when u > 0)
  rho  agreement between the judge's ranking and the value (the selection
       differential per unit of within-prompt spread)

The flow-field arrows (blue) are the model's implied move at each value, drawn
with REPRESENTATIVE illustration parameters chosen per regime (printed in each
row label) -- they are the picture of the dynamics, not fitted to one run.

Overlaid on rows 1, 2 and 4 are OBSERVED one-round moves (dark arrows) read
live from experiments/spread_util_unified.json for one run that matches the
regime.  A run's plotted trajectory follows the same convention as
spread-rollout-bakeoff.py:  first point = round-1 own value, then each later
point = that round's value + drift; a "move" is one consecutive step v_r -> v_{r+1}.

Fixed points:  filled dot = attracting (flow converges), open dot = repelling
(flow leaves).  Palette + esc()/wrap() copied from docs/figures/src/make_figures.py.
Regenerate with:  python3 vector-field-line.py
"""
import json
import math
import os
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
UNIFIED = os.path.join(HERE, "..", "..", "..", "..", "experiments",
                       "spread_util_unified.json")

# ---- palette (house style; make_figures.py constants) --------------------
INK = "#1a1a1a"
BLUE = "#2867b5"       # model-implied flow field
GREEN = "#3a7d44"
RED = "#b5342c"        # emphasis (erosion / warning) in key only
GRAY = "#6b7684"       # recessive: axes, ticks, muted labels
KEY_FILL = "#eef5ee"
FLOW = "#2867b5"
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


def line(x1, y1, x2, y2, color, sw=1.0, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{sw}"{d} stroke-linecap="round"/>')


# ======================================================================
# read data + build observed trajectories (bakeoff convention)
# ======================================================================
with open(UNIFIED) as f:
    RECORDS = json.load(f)["records"]

_groups = defaultdict(list)
for _r in RECORDS:
    _groups[(_r["cond"], str(_r["seed"]), _r["source"])].append(_r)


def find(cond, seed):
    for k, rows in _groups.items():
        if k[0] == cond and k[1] == str(seed):
            return sorted(rows, key=lambda r: r["round"])
    raise KeyError((cond, seed))


def observed(rows):
    return [rows[0]["value"]] + [r["value"] + r["drift"] for r in rows]


# chosen runs (verified live below)
ROW1_RUN = find("evolving_self", 2)             # Qwen, self-only, risk, rho>0
ROW2_RUN = find("judge_opposition_oracle", 101)  # Qwen, self-only, rho<0
ROW4_UP = find("h2h_erode_self", 61)             # OLMo, mixed pool, rises
ROW4_DN = find("h2h_base_rescue", 57)            # OLMo, mixed pool, falls

for r, org, comp in [(ROW1_RUN, "Qwen", "self-only"),
                     (ROW2_RUN, "Qwen", "self-only"),
                     (ROW4_UP, "OLMo", "base-mixed"),
                     (ROW4_DN, "OLMo", "base-mixed")]:
    assert r[0]["organism"] == org and r[0]["composition"] == comp, r[0]["cond"]

OBS1 = observed(ROW1_RUN)
OBS2 = observed(ROW2_RUN)
OBS4U = observed(ROW4_UP)
OBS4D = observed(ROW4_DN)

# ======================================================================
# model-implied flow functions
# ======================================================================
def env(v):
    v = min(1.0, max(0.0, v))
    return math.sqrt(max(0.0, v * (1.0 - v)))


RHO1 = 0.5      # judge strongly with the value
RHO2 = -0.5     # judge strongly against the value
U4, S4, RHO4 = 0.5, 0.55, 0.10  # mixed pool: half from a supplier at 0.55


def f1(v):
    return RHO1 * env(v)


def f2(v):
    return RHO2 * env(v)


def f4(v):
    return U4 * (S4 - v) + RHO4 * env(v)


def interior_fixed_point(f):
    lo, hi = 0.02, 0.98
    prev = f(lo)
    v = lo
    while v < hi:
        cur = f(v)
        if prev == 0 or (prev < 0) != (cur < 0):
            # bisect between v-step and v
            a, b = v - 0.001, v
            for _ in range(60):
                m = 0.5 * (a + b)
                if (f(a) < 0) != (f(m) < 0):
                    b = m
                else:
                    a = m
            return 0.5 * (a + b)
        prev = cur
        v += 0.001
    return None


VSTAR = interior_fixed_point(f4)

# ======================================================================
# layout
# ======================================================================
W, H = 1240, 912
LEFT = 44
LX0, LX1 = 372.0, 1180.0          # value line x-range
LABEL_W = LX0 - LEFT - 16

ROW_Y = [262, 418, 574, 730]      # baseline y per row
RIBBON = 42                       # observed ribbon offset above baseline
K = 165.0                         # px per unit of dv (flow arrow scale)


def X(v):
    return LX0 + (LX1 - LX0) * min(1.0, max(0.0, v))


S = []
S.append(f'<rect width="{W}" height="{H}" fill="white"/>')

# ---- markers -------------------------------------------------------------
S.append(
    '<defs>'
    f'<marker id="flow" viewBox="0 0 10 10" refX="8.5" refY="5" '
    f'markerWidth="6.5" markerHeight="6.5" orient="auto">'
    f'<path d="M 0 0 L 10 5 L 0 10 z" fill="{FLOW}"/></marker>'
    f'<marker id="obs" viewBox="0 0 10 10" refX="8.5" refY="5" '
    f'markerWidth="6" markerHeight="6" orient="auto">'
    f'<path d="M 0 0 L 10 5 L 0 10 z" fill="{INK}"/></marker>'
    '</defs>')

# ---- headline ------------------------------------------------------------
S.append(txt(LEFT, 50,
             "The one-round move as a flow on the value line, by regime",
             24, INK, "bold"))
S.append(txt(LEFT, 82,
             "Blue arrows: the model-implied move  v -> v + dv,  "
             "dv = u·(s − v) + rho·sigma,  sigma ≤ "
             "√(v(1−v)).   Dark arrows: observed moves from live runs.",
             16, GRAY))

# ---- key -----------------------------------------------------------------
ky = 118
S.append(f'<circle cx="{LEFT + 8}" cy="{ky - 5}" r="7" fill="{INK}"/>')
S.append(txt(LEFT + 24, ky, "filled = attracting fixed point (flow converges "
            "here)", 15, INK))
kx = 470
S.append(f'<circle cx="{kx + 8}" cy="{ky - 5}" r="7" fill="white" '
         f'stroke="{INK}" stroke-width="2.4"/>')
S.append(txt(kx + 24, ky, "open = repelling fixed point (flow leaves)",
             15, INK))
kx = 862
S.append(line(kx, ky - 5, kx + 30, ky - 5, FLOW, 3))
S.append(f'<polygon points="{kx+30},{ky-9} {kx+40},{ky-5} {kx+30},{ky-1}" '
         f'fill="{FLOW}"/>')
S.append(txt(kx + 48, ky, "implied move (length ∝ |dv|)", 15, INK))


def flow_arrow(v, y, f, color=FLOW, sw=2.4):
    d = f(v)
    x0 = X(v)
    length = K * d
    if abs(length) < 3.0:
        # near-zero move: draw a small neutral stub / dot
        return (f'<circle cx="{x0:.1f}" cy="{y:.1f}" r="2.6" '
                f'fill="{GRAY}"/>')
    x1 = x0 + length
    return (f'<line x1="{x0:.1f}" y1="{y:.1f}" x2="{x1:.1f}" y2="{y:.1f}" '
            f'stroke="{color}" stroke-width="{sw}" marker-end="url(#flow)"/>')


def dot(v, y, filled):
    if filled:
        return (f'<circle cx="{X(v):.1f}" cy="{y:.1f}" r="8.5" fill="{INK}"/>')
    return (f'<circle cx="{X(v):.1f}" cy="{y:.1f}" r="8.5" fill="white" '
            f'stroke="{INK}" stroke-width="2.6"/>')


def observed_ribbon(vals, y, label):
    """Zigzag ribbon of consecutive observed moves; each move is slanted a few
    px so overlapping back-and-forth moves stay individually legible."""
    out = []
    ys = [y - (i % 2) * 13 for i in range(len(vals))]
    for i in range(len(vals) - 1):
        a, b = X(vals[i]), X(vals[i + 1])
        out.append(f'<line x1="{a:.1f}" y1="{ys[i]:.1f}" x2="{b:.1f}" '
                   f'y2="{ys[i + 1]:.1f}" stroke="{INK}" stroke-width="1.8" '
                   f'marker-end="url(#obs)"/>')
    for i, v in enumerate(vals):
        out.append(f'<circle cx="{X(v):.1f}" cy="{ys[i]:.1f}" r="3.0" '
                   f'fill="{INK}"/>')
    # label to the left of the used range, on the upper stagger line
    lx = min(X(v) for v in vals)
    out.append(txt(lx - 10, y - 13 + 4.5, label, 13, INK, "bold", anchor="end"))
    return out


def baseline(y):
    out = [line(LX0, y, LX1, y, GRAY, 1.4)]
    for gv in (0.0, 0.5, 1.0):
        out.append(line(X(gv), y - 5, X(gv), y + 5, GRAY, 1.2))
    return out


def row_label(y, title, param):
    return [
        txt(LEFT, y - 8, title, 16, INK, "bold"),
        txt(LEFT, y + 14, param, 14, GRAY),
    ]


SAMPLES = [0.06 + 0.073 * i for i in range(13)]

# ---- Row 1: self-only, rho > 0 -------------------------------------------
y = ROW_Y[0]
S += row_label(y, "1.  Self-only, judge with the value",
               "u = 0,   rho = +0.5")
S += baseline(y)
for v in SAMPLES:
    S.append(flow_arrow(v, y, f1))
S.append(dot(0.0, y, filled=False))
S.append(dot(1.0, y, filled=True))
S += observed_ribbon(OBS1, y - RIBBON, "evolving self")

# ---- Row 2: self-only, rho < 0 -------------------------------------------
y = ROW_Y[1]
S += row_label(y, "2.  Self-only, judge against the value",
               "u = 0,   rho = −0.5")
S += baseline(y)
for v in SAMPLES:
    S.append(flow_arrow(v, y, f2))
S.append(dot(0.0, y, filled=True))
S.append(dot(1.0, y, filled=False))
S += observed_ribbon(OBS2, y - RIBBON, "oracle opposition")

# ---- Row 3: self-only, rho ~ 0 -------------------------------------------
y = ROW_Y[2]
S += row_label(y, "3.  Self-only, judge uncorrelated with the value",
               "u = 0,   rho ≈ 0")
S += baseline(y)
for v in SAMPLES:
    S.append(f'<circle cx="{X(v):.1f}" cy="{y:.1f}" r="2.6" fill="{GRAY}"/>')
S.append(txt((LX0 + LX1) / 2, y - 26,
             "the whole line sits still — no attracting or repelling point",
             14, GRAY, anchor="middle"))

# ---- Row 4: mixed pool ---------------------------------------------------
y = ROW_Y[3]
S += row_label(y, "4.  Mixed pool: outside-source share u at level s",
               f"u = {U4:g},   s = {S4:g},   rho = +{RHO4:g}")
S += baseline(y)
for v in SAMPLES:
    S.append(flow_arrow(v, y, f4))
# supplier level tick
S.append(line(X(S4), y, X(S4), y + 22, GRAY, 1.6, dash="3 3"))
S.append(txt(X(S4), y + 38, f"outside-source level s = {S4:g}", 12.5, GRAY,
             anchor="middle"))
S.append(dot(0.0, y, filled=False))
S.append(dot(1.0, y, filled=False))
S.append(dot(VSTAR, y, filled=True))
S.append(txt(X(VSTAR), y - 14, f"v* ≈ {VSTAR:.2f}", 13, INK, "bold",
             anchor="middle"))
# two observed runs converging from both sides
S += observed_ribbon(OBS4D, y - RIBBON - 22, "base rescue")
S += observed_ribbon(OBS4U, y - RIBBON + 2, "erode self")

# ---- x axis (value meaning), shown once at the bottom --------------------
axis_y = ROW_Y[3] + 78
for gv in (0.0, 0.5, 1.0):
    S.append(txt(X(gv), axis_y, f"{gv:g}", 14, GRAY, anchor="middle"))
S.append(txt((LX0 + LX1) / 2, axis_y + 24,
             "behavioral value v  —  share of the model's own answers the "
             "judge scores at the trait  (0 = none, 1 = all)",
             14, GRAY, anchor="middle"))

# ---- source footnote -----------------------------------------------------
fy = H - 62
S.append(txt(LEFT, fy,
             "Flow-field arrows: the unit recurrence with representative "
             "per-regime parameters (printed in each row label), not fitted to "
             "a run.",
             12.5, GRAY))
S.append(txt(LEFT, fy + 18,
             "Dark arrows: observed one-round moves read live from "
             "experiments/spread_util_unified.json — row 1 evolving_self seed 2 "
             "(Qwen), row 2 judge_opposition_oracle seed 101 (Qwen),",
             12.5, GRAY))
S.append(txt(LEFT, fy + 36,
             "row 4 h2h_base_rescue seed 57 and h2h_erode_self seed 61 (OLMo). "
             "  Generator: vector-field-line.py",
             12.5, GRAY))

svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
       f'font-family="{FONT}">\n' + "\n".join(S) + "\n</svg>")

out = os.path.join(HERE, "vector-field-line.svg")
with open(out, "w") as fh:
    fh.write(svg)
print(f"wrote {out}  viewBox 0 0 {W} {H}")
print(f"v* (row 4) = {VSTAR:.4f}")
print("OBS1", [round(x, 3) for x in OBS1])
print("OBS2", [round(x, 3) for x in OBS2])
print("OBS4 up", [round(x, 3) for x in OBS4U])
print("OBS4 dn", [round(x, 3) for x in OBS4D])
