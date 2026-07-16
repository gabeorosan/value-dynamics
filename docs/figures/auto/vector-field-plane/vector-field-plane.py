#!/usr/bin/env python3
"""The (value, agreement) state plane with the model's implied flow field and
observed run paths (slug: vector-field-plane).

BACKGROUND FIELD.  At a grid of (value v, agreement rho) points we draw a small
horizontal arrow whose length is proportional to the model's one-round move in
value under the self-only unit recurrence,

        move(v, rho) = rho * sqrt( v * (1 - v) ),

the selection gap when the within-prompt spread sits at its binary envelope
sigma_max(v) = sqrt(v(1-v)).  The arrow points RIGHT (toward v = 1) when the
organism agrees with the selector (rho > 0) and LEFT (toward v = 0) when it
disagrees (rho < 0).  The move vanishes along rho = 0 and at the walls
v in {0, 1}: those are the zero-move zones, outlined only.

OBSERVED PATHS.  Binary RISK-axis runs from experiments/spread_util_unified.json.
Within each run the per-round points are (v_r, rho_r) connected in round order,
dropping rounds with undefined agreement.  Observed value per round follows the
same convention as spread-rollout-bakeoff.py: value + drift.  Agreement rho_r is
the measured round value.  One color per experiment family; a small arrowhead
marks each step's direction.

Palette + esc()/wrap() copied from docs/figures/src/make_figures.py (house
style).  Stdlib only.  Regenerate with:  python3 vector-field-plane.py
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
BLUE = "#2867b5"
GREEN = "#3a7d44"
RED = "#b5342c"
GRAY = "#6b7684"
PURPLE = "#8046a5"
AMBER = "#c77b28"
FIELD = "#b9c6d4"      # recessive flow arrows (light gray-blue)
ZONE = "#eef0f2"       # zero-move zone fill
FAINT = "#e4e4e0"
KEY_FILL = "#eef5ee"
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
    return (f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" '
            f'stroke="{color}" stroke-width="{sw}"{d}/>')


def rect(x, y, w, h, fill, stroke="none", sw=0, rx=0):
    st = f' stroke="{stroke}" stroke-width="{sw}"' if stroke != "none" else ""
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" '
            f'rx="{rx}" fill="{fill}"{st}/>')


def htxt(x, y, s, size=13, color=GRAY, anchor="start"):
    """Text with a white halo rect behind it so it reads over the paths."""
    w = len(s) * size * 0.56
    if anchor == "middle":
        rx = x - w / 2
    elif anchor == "end":
        rx = x - w
    else:
        rx = x
    bg = rect(rx - 4, y - size + 2, w + 8, size + 5, "white")
    bg = bg.replace('fill="white"/>', 'fill="white" fill-opacity="0.82"/>')
    return bg + "\n" + txt(x, y, s, size, color, anchor=anchor)


def head(hx, hy, ux, uy, color, sz=5.0):
    """Small filled arrowhead at (hx,hy) pointing along unit vector (ux,uy)."""
    px, py = -uy, ux
    p1 = (hx, hy)
    p2 = (hx - ux * sz + px * sz * 0.55, hy - uy * sz + py * sz * 0.55)
    p3 = (hx - ux * sz - px * sz * 0.55, hy - uy * sz - py * sz * 0.55)
    pts = " ".join(f"{x:.2f},{y:.2f}" for x, y in (p1, p2, p3))
    return f'<polygon points="{pts}" fill="{color}"/>'


# ======================================================================
# data: binary RISK-axis runs
# ======================================================================
with open(UNIFIED) as f:
    RECORDS = [r for r in json.load(f)["records"] if r["axis"] == "risk"]


def run_key(r):
    return (r["cond"], r["seed"], r["source"])


def family(r):
    """Committed family names from docs/writeup_value_dynamics_sprint.md
    ('What I ran'), mapped honestly from cond / organism / composition."""
    c, org = r["cond"], r["organism"]
    if c.startswith("oracle"):
        return "oracle & injection"          # score-oracle selector (self / mixed)
    if org == "Qwen":
        return "Qwen risk grid"
    if r["composition"] != "self-only":
        return "OLMo mixed-pool interventions"  # base- / peer-mixed pools + duels
    return "OLMo risk grid + judge schedules"   # OLMo self-only, reference / swaps


FAM_COLOR = {
    "Qwen risk grid": BLUE,
    "OLMo risk grid + judge schedules": GREEN,
    "OLMo mixed-pool interventions": PURPLE,
    "oracle & injection": RED,
}
FAM_ORDER = ["Qwen risk grid", "OLMo risk grid + judge schedules",
             "OLMo mixed-pool interventions", "oracle & injection"]

# The handful of representative runs drawn in family color (1-2 per family,
# each a distinct behavior).  Everything else is drawn faint gray.  Matched by
# (cond, seed); label is the run's condition shown at the path end.
HIGHLIGHT = {
    ("evolving_self", "3", "k1_qwen_anchor.json"): "evolving self · seed 3",         # runaway right, strong agreement
    ("frozen_base", "0", "k1_qwen_anchor.json"):   "frozen base judge · seed 0",     # hovers near agreement 0 (Qwen)
    ("press_d1", "2", "k2rel_press_d1_s2.json"):   "judge-swap ladder · seed 2",     # runaway right under judge schedule
    ("press_to_base", "1", "k2rel_press_to_base_s1.json"): "press-to-base · seed 1",  # runaway left, disagreement
    ("h2h_invade_self", "53", "k2rel_h2h_invade_self_s53.json"): "peer invasion (duel) · seed 53",  # mixed pool rails to 1
    ("oracle_hold", "21", "k2rel_oracle_hold_s21.json"): "score oracle, self-only · seed 21",  # oracle floor, falls left
    ("oracle_mix", "31", "k2rel_oracle_mix_s31.json"): "score oracle, base-mixed · seed 31",   # oracle floor, mixed
}

_groups = defaultdict(list)
for _r in RECORDS:
    _groups[run_key(_r)].append(_r)

# observed paths: (v_r, rho_r) in round order, rho defined, >= 2 points
PATHS = []          # (family, pts, highlight_label_or_None)
fam_runs = defaultdict(int)
fam_segs = defaultdict(int)
n_shown = 0
for k, rows in _groups.items():
    rows = sorted(rows, key=lambda r: r["round"])
    pts = [(r["value"] + r["drift"], r["rho"]) for r in rows if r["rho"] is not None]
    if len(pts) < 2:
        continue
    fam = family(rows[0])
    hl = HIGHLIGHT.get((rows[0]["cond"], str(rows[0]["seed"]), rows[0]["source"]))
    PATHS.append((fam, pts, hl))
    if hl:
        n_shown += 1
    fam_runs[fam] += 1
    fam_segs[fam] += len(pts) - 1

N_RUNS = sum(fam_runs.values())
N_SEGS = sum(fam_segs.values())
N_FAINT = N_RUNS - n_shown

# ======================================================================
# layout
# ======================================================================
W, H = 1240, 940
LEFT = 56
PLOT_L = 150
PLOT_R = W - 60
PLOT_T = 232
PLOT_B = 828
PLOT_W = PLOT_R - PLOT_L
PLOT_H = PLOT_B - PLOT_T


def X(v):
    return PLOT_L + v * PLOT_W


def Y(rho):
    return PLOT_B - (rho + 1.0) / 2.0 * PLOT_H


S = []

# ---- headline + subtitle -------------------------------------------------
S.append(txt(LEFT, 56,
             "Runs moving through the (value, agreement) plane, "
             "over the model's implied flow", 24, INK, "bold"))
sub = ("Background arrows: the one-round move in value the unit recurrence "
       "implies at each point, length proportional to")
S.append(txt(LEFT, 92, sub, 16, GRAY))
S.append(txt(LEFT, 114,
             "agreement x sqrt(value x (1 - value)) — right when the organism "
             "agrees with the selector, left when it disagrees.", 16, GRAY))

# ---- family key (wraps to a second row) ----------------------------------
S.append(txt(LEFT, 146,
             "Representative runs, colored by family (committed names from the "
             "writeup; runs per family in parentheses):", 15, INK, "bold"))
kx, ky = LEFT, 172
KMAX = W - 60
for fam in FAM_ORDER:
    col = FAM_COLOR[fam]
    label = f"{fam}  ({fam_runs[fam]})"
    item_w = 26 + 8 + len(label) * 8.0 + 30
    if kx + item_w > KMAX and kx > LEFT:
        kx = LEFT
        ky += 26
    S.append(line(kx, ky - 5, kx + 26, ky - 5, col, 2.6))
    S.append(head(kx + 26, ky - 5, 1.0, 0.0, col, 5.2))
    S.append(txt(kx + 34, ky, label, 14.5, INK))
    kx += item_w
# faint-gray entry for the remaining runs
label = f"all other runs  ({N_FAINT})"
item_w = 26 + 8 + len(label) * 8.0 + 30
if kx + item_w > KMAX and kx > LEFT:
    kx = LEFT
    ky += 26
S.append(line(kx, ky - 5, kx + 26, ky - 5, "#c9cdd2", 2.0))
S.append(txt(kx + 34, ky, label, 14.5, GRAY))

# ======================================================================
# background flow field
# ======================================================================
# zero-move zones: walls v in {0,1} and the rho = 0 line
wall = 0.045
S.append(rect(X(0.0), PLOT_T, X(wall) - X(0.0), PLOT_H, ZONE))
S.append(rect(X(1.0 - wall), PLOT_T, X(1.0) - X(1.0 - wall), PLOT_H, ZONE))
band = 0.05
S.append(rect(PLOT_L, Y(band), PLOT_W, Y(-band) - Y(band), ZONE))

# field arrows
COLS = 15
ROWS = 13
FIELD_SCALE = 168.0     # px per unit of move
for ci in range(COLS):
    v = (ci + 0.5) / COLS
    for ri in range(ROWS):
        rho = -1.0 + (ri + 0.5) / ROWS * 2.0
        move = rho * math.sqrt(max(0.0, v * (1.0 - v)))
        length = move * FIELD_SCALE
        if abs(length) < 0.8:
            continue
        cx, cy = X(v), Y(rho)
        x0 = cx - length / 2.0
        x1 = cx + length / 2.0
        S.append(line(x0, cy, x1, cy, FIELD, 1.5))
        ux = 1.0 if length > 0 else -1.0
        S.append(head(x1, cy, ux, 0.0, FIELD, 4.2))

# ---- plot frame + gridlines ----------------------------------------------
# rho = 0 baseline
S.append(line(PLOT_L, Y(0.0), PLOT_R, Y(0.0), GRAY, 1.4, dash="4 4"))
# axes
S.append(line(PLOT_L, PLOT_T, PLOT_L, PLOT_B, INK, 1.6))
S.append(line(PLOT_L, PLOT_B, PLOT_R, PLOT_B, INK, 1.6))
S.append(line(PLOT_L, PLOT_T, PLOT_R, PLOT_T, FAINT, 1.0))
S.append(line(PLOT_R, PLOT_T, PLOT_R, PLOT_B, FAINT, 1.0))

# x ticks (value)
for gv in (0.0, 0.25, 0.5, 0.75, 1.0):
    gx = X(gv)
    S.append(line(gx, PLOT_B, gx, PLOT_B + 6, INK, 1.2))
    S.append(txt(gx, PLOT_B + 26, f"{gv:g}", 14, GRAY, anchor="middle"))
# y ticks (rho)
for gr in (-1.0, -0.5, 0.0, 0.5, 1.0):
    gy = Y(gr)
    S.append(line(PLOT_L - 6, gy, PLOT_L, gy, INK, 1.2))
    S.append(txt(PLOT_L - 12, gy + 5, f"{gr:+g}", 14, GRAY, anchor="end"))

# zone identification labels (orientation only)
S.append(htxt(X(0.5), Y(0.0) - 7, "no move: agreement = 0", 13, GRAY,
              anchor="middle"))
S.append(htxt(X(wall / 2), PLOT_B - 10, "wall v = 0", 12, GRAY, anchor="middle"))
S.append(htxt(X(1.0 - wall / 2), PLOT_B - 10, "wall v = 1", 12, GRAY,
              anchor="middle"))

# axis titles
S.append(txt((PLOT_L + PLOT_R) / 2, PLOT_B + 52,
             "value  v   (share of behaviors judged to hold the target value, 0 to 1)",
             16, INK, anchor="middle"))
S.append(f'<text x="{LEFT - 8}" y="{(PLOT_T + PLOT_B) / 2:.1f}" '
         f'font-family="{FONT}" font-size="16" fill="{INK}" '
         f'text-anchor="middle" transform="rotate(-90 {LEFT - 8} '
         f'{(PLOT_T + PLOT_B) / 2:.1f})">agreement  rho  (organism vs selector, '
         f'-1 to +1)</text>')

# orientation labels for the flow direction (position only, no interpretation)
S.append(htxt(X(0.30), Y(0.86), "upper region: flow → v = 1", 13, GRAY))
S.append(htxt(X(0.30), Y(-0.82), "lower region: flow ← v = 0", 13, GRAY))

# ======================================================================
# observed paths
# ======================================================================
def clampv(v):
    return min(1.0, max(0.0, v))


def clampr(r):
    return min(1.0, max(-1.0, r))


# first the faint-gray non-highlighted runs (so the field still reads), then
# the representative colored paths on top with per-step arrowheads and a label
FAINT_PATH = "#d3d7dc"
for fam, pts, hl in PATHS:
    if hl:
        continue
    xy = [(X(clampv(v)), Y(clampr(r))) for v, r in pts]
    d = "M " + " L ".join(f"{x:.2f} {y:.2f}" for x, y in xy)
    S.append(f'<path d="{d}" fill="none" stroke="{FAINT_PATH}" '
             f'stroke-width="1.0" stroke-opacity="0.65" stroke-linejoin="round"/>')

for fam, pts, hl in PATHS:
    if not hl:
        continue
    col = FAM_COLOR[fam]
    xy = [(X(clampv(v)), Y(clampr(r))) for v, r in pts]
    d = "M " + " L ".join(f"{x:.2f} {y:.2f}" for x, y in xy)
    S.append(f'<path d="{d}" fill="none" stroke="{col}" stroke-width="2.4" '
             f'stroke-linejoin="round" stroke-linecap="round"/>')
    # start dot (hollow) to mark round 1
    S.append(f'<circle cx="{xy[0][0]:.2f}" cy="{xy[0][1]:.2f}" r="4.2" '
             f'fill="white" stroke="{col}" stroke-width="2.0"/>')
    # per-step arrowheads
    for i in range(1, len(xy)):
        x0, y0 = xy[i - 1]
        x1, y1 = xy[i]
        dx, dy = x1 - x0, y1 - y0
        L = math.hypot(dx, dy)
        if L < 4:
            continue
        ux, uy = dx / L, dy / L
        S.append(head(x1, y1, ux, uy, col, 6.0))
    # condition label at the path end, kept inside the plot
    ex, ey_ = xy[-1]
    dyl = xy[-1][1] - xy[-2][1]
    on_floor = ey_ > PLOT_B - 30
    if on_floor:                      # oracle row: labels grow right, above floor
        anchor, ox = "start", 12
    elif ex > PLOT_R - 160:
        anchor, ox = "end", -12
    elif ex < PLOT_L + 160:
        anchor, ox = "start", 12
    else:
        dxl = xy[-1][0] - xy[-2][0]
        anchor, ox = ("start", 12) if dxl >= 0 else ("end", -12)
    if on_floor:
        voff = -12
    elif ey_ < PLOT_T + 40:
        voff = 18
    else:
        voff = 15 if dyl > 0 else -9
    S.append(htxt(ex + ox, ey_ + voff, hl, 12.5, col, anchor=anchor))

# ---- source footnote -----------------------------------------------------
fy = PLOT_B + 86
foot = (f"{N_RUNS} binary risk-axis runs ({N_SEGS} observed steps) from "
        "experiments/spread_util_unified.json (axis = \"risk\"; runs with "
        f"fewer than two agreement-defined rounds dropped). {n_shown} "
        f"representative runs drawn in color; the other {N_FAINT} are faint "
        "gray. Flow field is the self-only unit-recurrence move value += "
        "agreement x sqrt(value x (1 - value)); no fit. Generator: "
        "vector-field-plane.py")
for j, ln in enumerate(wrap(foot, 150)):
    S.append(txt(LEFT, fy + j * 18, ln, 13, GRAY))

svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
       f'font-family="{FONT}">\n'
       f'<rect width="{W}" height="{H}" fill="white"/>\n'
       + "\n".join(S) + "\n</svg>")

out = os.path.join(HERE, "vector-field-plane.svg")
with open(out, "w") as f:
    f.write(svg)
print(f"wrote {out}  viewBox 0 0 {W} {H}")
print(f"paths: {N_RUNS} runs, {N_SEGS} segments across {len(fam_runs)} families")
for fam in FAM_ORDER:
    print(f"  {fam}: {fam_runs[fam]} runs, {fam_segs[fam]} segs")
