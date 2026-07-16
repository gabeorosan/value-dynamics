#!/usr/bin/env python3
"""Runs through the (value, forecast-move) plane, over the model's flow
(slug: field-value-gap-paths).

Each committed selection run is drawn as its path through the plane whose
x-axis is the behavioral value v and whose y-axis is rho*sigma -- the model's
forecast one-round move in value (the selector gap = agreement rho times the
within-prompt candidate spread sigma). Coordinates are computed live from
experiments/spread_util_unified.json per-round records:

    x = behavioral value v   (per round; for the FINAL point v_end = last
                              round's value + drift, the endpoint convention
                              used by spread-rollout-bakeoff.py observed())
    y = rho * spread          (the per-round `rho` and `spread` fields; rounds
                              with undefined rho are skipped)

BACKGROUND FIELD (the model, not fitted to this plot): at a grid of (v, y)
points a light horizontal arrow shows the pure-selection one-round move the
recurrence predicts for a self-only pool -- Delta v = rho*sigma = the
y-coordinate. Its length is literally that move mapped through the x-scale
(head at clip(v + y, 0, 1)); it points right above y = 0, left below, and
vanishes on the zero line. Mixed-pool runs feel an extra pull u*(s - v) that
this self-only field omits (see caption.md).

Run identity is (cond, seed, source); four groups carry two interleaved chains
sharing that key, split here by value+drift continuity. Color encodes the
experiment family; the compact key gives per-family run counts.

Palette (INK/BLUE/GREEN/RED/GRAY) + esc()/wrap() copied from
docs/figures/src/make_figures.py (house style). Two extra CVD-checked
categorical hues are added for the 4th/5th families.
Regenerate with:  python3 field-value-gap-paths.py
"""
import json
import math
import os
from collections import defaultdict, Counter

HERE = os.path.dirname(os.path.abspath(__file__))
UNIFIED = os.path.join(HERE, "..", "..", "..", "..", "experiments",
                       "spread_util_unified.json")

# ---- palette (house style; make_figures.py constants) --------------------
INK = "#1a1a1a"
BLUE = "#2867b5"
GREEN = "#3a7d44"
RED = "#b5342c"
GRAY = "#6b7684"
PURPLE = "#7a4fb5"     # 4th categorical hue (CVD-checked with the house four)
AMBER = "#c77d1a"      # 5th categorical hue
FIELD = "#c8ccd2"      # recessive vector field
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


def rect(x, y, w, h, fill, stroke="none", sw=0, rx=0):
    st = f' stroke="{stroke}" stroke-width="{sw}"' if stroke != "none" else ""
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" '
            f'rx="{rx}" fill="{fill}"{st}/>')


def line(x1, y1, x2, y2, color, sw=1.0, dash=None, opacity=1.0):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    o = f' stroke-opacity="{opacity}"' if opacity != 1.0 else ""
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{sw}"{d}{o}/>')


# ======================================================================
# read data + reconstruct run chains
# ======================================================================
with open(UNIFIED) as f:
    RECORDS = json.load(f)["records"]


def run_key(r):
    return (r["cond"], r["seed"], r["source"])


def family(r):
    s = r["source"]
    comp = r["composition"]
    if s == "k1_qwen_anchor.json":
        return "Qwen risk grid"
    if s == "selfaware_loop_grid.json":
        return "Qwen insecure-code loops"
    if (s.startswith("judge_opposition") or s.startswith("mixed_reopen")
            or s.startswith("head2head_selfjudge") or "oracle_hold" in s):
        return "oracle & injection"
    if comp in ("base-mixed", "peer-mixed"):
        return "OLMo mixed-pool interventions"
    return "OLMo risk grid + schedules"


FAMILIES = [
    ("Qwen risk grid", BLUE),
    ("OLMo risk grid + schedules", GREEN),
    ("OLMo mixed-pool interventions", RED),
    ("oracle & injection", PURPLE),
    ("Qwen insecure-code loops", AMBER),
]
FAM_COLOR = dict(FAMILIES)


def chains(rows):
    """Split a (cond,seed,source) group into trajectories. Most groups are one
    chain; four carry two interleaved chains, separated by value+drift ->
    next-round value continuity."""
    byr = defaultdict(list)
    for r in rows:
        byr[r["round"]].append(r)
    rounds = sorted(byr)
    used, out = set(), []
    for st in byr[rounds[0]]:
        chain, cur = [st], st
        for nr in rounds[1:]:
            cands = [c for c in byr[nr] if id(c) not in used]
            if not cands:
                break
            target = cur["value"] + cur["drift"]
            best = min(cands, key=lambda c: abs(c["value"] - target))
            chain.append(best)
            used.add(id(best))
            cur = best
        out.append(chain)
    return out


groups = defaultdict(list)
for r in RECORDS:
    groups[run_key(r)].append(r)


def clip01(x):
    return min(1.0, max(0.0, x))


# build path point lists: each PATH = (family, [(v,y), ...]) round-ordered
PATHS = []
fam_runs = Counter()
n_points = n_segments = 0
for k, rows in groups.items():
    for ch in chains(rows):
        pts = [r for r in ch if r["rho"] is not None]
        if not pts:
            continue
        fam = family(pts[0])
        fam_runs[fam] += 1
        coords = []
        last = len(pts) - 1
        for i, r in enumerate(pts):
            v = r["value"] + r["drift"] if i == last else r["value"]
            coords.append((clip01(v), r["rho"] * r["spread"]))
        PATHS.append((fam, coords))
        n_points += len(coords)
        n_segments += max(0, len(coords) - 1)

assert sum(fam_runs.values()) == len(PATHS)

# ======================================================================
# build the SVG
# ======================================================================
W, H = 1300, 892
LEFT = 46
S = []

# ---- headline + subtitle (orientation only; interpretation in caption) ----
S.append(txt(LEFT, 50,
             "Runs through the (value, forecast-move) plane, over the "
             "model's flow", 23, INK, "bold"))
S.append(txt(LEFT, 82,
             "Each path is one selection run. x = behavioral value v.  "
             "y = rho·sigma, the model's forecast one-round move in v.  Light "
             "arrows show that move on a self-only pool, not fitted here.",
             16, GRAY))

# ---- plot frame ----------------------------------------------------------
PLOT_X0 = LEFT + 66
PLOT_Y0 = 132
PLOT_W = 900
PLOT_H = 560
PLOT_X1 = PLOT_X0 + PLOT_W
PLOT_Y1 = PLOT_Y0 + PLOT_H
YMIN, YMAX = -0.5, 0.5


def X(v):
    return PLOT_X0 + v * PLOT_W


def Y(y):
    return PLOT_Y0 + (YMAX - y) / (YMAX - YMIN) * PLOT_H


# plot background + border
S.append(rect(PLOT_X0, PLOT_Y0, PLOT_W, PLOT_H, "#ffffff",
              stroke=FAINT, sw=1.4))

# vertical gridlines (value)
for gv in (0.0, 0.25, 0.5, 0.75, 1.0):
    S.append(line(X(gv), PLOT_Y0, X(gv), PLOT_Y1, FAINT, 1.0))
    S.append(txt(X(gv), PLOT_Y1 + 26, f"{gv:g}", 15, GRAY, anchor="middle"))
# horizontal gridlines (forecast move)
for gy in (-0.5, -0.25, 0.25, 0.5):
    S.append(line(PLOT_X0, Y(gy), PLOT_X1, Y(gy), FAINT, 1.0))
    S.append(txt(PLOT_X0 - 12, Y(gy) + 5, f"{gy:+g}", 15, GRAY, anchor="end"))

# ---- background vector field ---------------------------------------------
# each little horizontal arrow IS the one-round pure-selection move at (v,y):
# tail at v, head at clip(v + y, 0, 1); vanishes on y = 0; clipped at walls.
grid_v = [i / 20.0 for i in range(1, 20)]          # 0.05 .. 0.95
grid_y = [j / 24.0 for j in range(-11, 12)]        # ~ -0.458 .. +0.458
for gy in grid_y:
    for gv in grid_v:
        if abs(gy) < 1e-6:
            continue
        v2 = clip01(gv + gy)
        if abs(v2 - gv) < 1e-4:
            continue
        x1, x2 = X(gv), X(v2)
        yy = Y(gy)
        S.append(line(x1, yy, x2, yy, FIELD, 1.2, opacity=0.9))
        # small arrowhead
        d = 5.0 if x2 >= x1 else -5.0
        S.append(f'<path d="M {x2:.1f} {yy:.1f} L {x2-d:.1f} {yy-3:.1f} '
                 f'L {x2-d:.1f} {yy+3:.1f} Z" fill="{FIELD}" '
                 f'fill-opacity="0.9"/>')

# bold zero line (y = 0): the model forecasts no move here
S.append(line(PLOT_X0, Y(0.0), PLOT_X1, Y(0.0), INK, 2.4))
S.append(rect(PLOT_X0 + 6, Y(0.0) - 21, 228, 18, "#ffffff",
              stroke="none"))
S.append(txt(PLOT_X0 + 10, Y(0.0) - 7,
             "rho·sigma = 0 : model forecasts no move", 13.5, INK,
             "bold", anchor="start"))

# ---- run paths -----------------------------------------------------------
for fam, coords in PATHS:
    col = FAM_COLOR[fam]
    pts = [(X(v), Y(y)) for v, y in coords]
    if len(pts) >= 2:
        p = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
        S.append(f'<polyline points="{p}" fill="none" stroke="{col}" '
                 f'stroke-width="1.7" stroke-opacity="0.72" '
                 f'stroke-linejoin="round" stroke-linecap="round"/>')
    # start dot at round 1
    sx, sy = pts[0]
    S.append(f'<circle cx="{sx:.1f}" cy="{sy:.1f}" r="3.4" fill="{col}" '
             f'fill-opacity="0.9"/>')
    # arrowhead at the final coordinate, oriented along the last segment
    ex, ey = pts[-1]
    if len(pts) >= 2:
        px, py = pts[-2]
        ang = math.atan2(ey - py, ex - px)
    else:
        ang = 0.0
    L, wgt = 11.0, 4.6
    ax = ex - L * math.cos(ang)
    ay = ey - L * math.sin(ang)
    nx, ny = -math.sin(ang), math.cos(ang)
    p1 = (ax + wgt * nx, ay + wgt * ny)
    p2 = (ax - wgt * nx, ay - wgt * ny)
    S.append(f'<path d="M {ex:.1f} {ey:.1f} L {p1[0]:.1f} {p1[1]:.1f} '
             f'L {p2[0]:.1f} {p2[1]:.1f} Z" fill="{col}"/>')

# ---- axis labels ---------------------------------------------------------
S.append(txt((PLOT_X0 + PLOT_X1) / 2, PLOT_Y1 + 54,
             "behavioral value  v   (fraction of the value battery the pool "
             "expresses, 0 to 1)", 16, INK, anchor="middle"))
# rotated y-axis label
yl_x, yl_y = LEFT + 6, (PLOT_Y0 + PLOT_Y1) / 2
S.append(f'<text x="{yl_x}" y="{yl_y}" font-family="{FONT}" font-size="16" '
         f'fill="{INK}" text-anchor="middle" '
         f'transform="rotate(-90 {yl_x} {yl_y})">'
         f'rho·sigma = forecast one-round move in v  '
         f'(agreement rho × candidate spread sigma)</text>')

# ---- key -----------------------------------------------------------------
kx = PLOT_X1 + 34
ky = PLOT_Y0 + 8
S.append(txt(kx, ky, "experiment family", 15, INK, "bold"))
ky += 12
for fam, col in FAMILIES:
    ky += 30
    S.append(line(kx, ky - 5, kx + 30, ky - 5, col, 2.4))
    S.append(f'<circle cx="{kx + 6}" cy="{ky - 5}" r="3.4" fill="{col}"/>')
    S.append(f'<path d="M {kx+30:.1f} {ky-5:.1f} L {kx+22:.1f} {ky-8.5:.1f} '
             f'L {kx+22:.1f} {ky-1.5:.1f} Z" fill="{col}"/>')
    S.append(txt(kx + 40, ky, fam, 14, INK))
    S.append(txt(kx + 40, ky + 15, f"{fam_runs[fam]} runs", 12, GRAY))
    ky += 15

ky += 34
S.append(txt(kx, ky, "reading each path", 15, INK, "bold"))
for i, ln in enumerate([
        "dot  = round-1 coordinate",
        "line = later rounds",
        "arrow = final endpoint",
        "       (v after the last move)"]):
    S.append(txt(kx, ky + 24 + i * 20, ln, 13, GRAY))

ky += 24 + 4 * 20 + 26
S.append(rect(kx - 6, ky - 18, 244, 96, KEY_FILL, stroke=FIELD, sw=1.2, rx=8))
for i, ln in enumerate(wrap(
        "Light field arrows = the pure-selection move for a self-only pool. "
        "Mixed-pool runs also feel a pull toward the co-generator, off this "
        "field.", 34)):
    S.append(txt(kx + 4, ky + 2 + i * 18, ln, 12.5, INK))

# ---- footnote ------------------------------------------------------------
fy = PLOT_Y1 + 84
S.append(txt(LEFT, fy,
             f"{len(PATHS)} runs / {n_points} plotted coordinates / "
             f"{n_segments} between-round segments, computed live from "
             "experiments/spread_util_unified.json (per-round rho, spread, "
             "value, drift).", 13, GRAY))
S.append(txt(LEFT, fy + 18,
             "y = rho × spread; rounds with undefined rho skipped; final "
             "x uses value + drift (spread-rollout-bakeoff.py observed() "
             "endpoint convention).  Generator: field-value-gap-paths.py", 13,
             GRAY))

svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
       f'font-family="{FONT}">\n'
       f'<rect width="{W}" height="{H}" fill="white"/>\n'
       + "\n".join(S) + "\n</svg>")

out = os.path.join(HERE, "field-value-gap-paths.svg")
with open(out, "w") as f:
    f.write(svg)
print(f"wrote {out}  viewBox 0 0 {W} {H}")
print(f"{len(PATHS)} runs, {n_points} points, {n_segments} segments")
for fam, _ in FAMILIES:
    print(f"  {fam}: {fam_runs[fam]}")
