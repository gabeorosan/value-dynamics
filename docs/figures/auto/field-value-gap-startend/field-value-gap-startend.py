#!/usr/bin/env python3
"""Each run's start and end in the (behavioral value, forecast-move) plane
(slug: field-value-gap-startend) -- the minimalist variant.

The plane is x = behavioral value v in [0, 1], y = the forecast one-round move
rho * sigma (round agreement times within-prompt spread), the selection term of
the parameter-free unit recurrence Delta v = rho * sigma for a self-only pool.
A faint background field of horizontal reference arrows shows that recurrence:
above the y = 0 line the pull is to the right (value rises), below it the pull
is to the left (value falls), lengthening away from zero and vanishing on it,
clipped at the walls v = 0 and v = 1.  Over that field, ONE straight arrow per
run goes from the run's round-1 coordinates (v_1, rho_1*sigma_1) -- open dot --
to its final coordinates (v_end, rho_end*sigma_end) -- filled arrowhead.  No
intermediate vertices.  Runs are colored by experiment family (the 5 committed
family names of run-inventory.py).  The 9 scheduled-judge-swap runs are drawn
hollow (dashed, open arrowhead), since the self-only field omits the swap.

All coordinates are computed live from experiments/spread_util_unified.json:
  * start   v_1 = round-1 value ; y_1 = round-1 rho * own_spread
  * end     v_end = last round value + drift (the observed() endpoint
            convention of spread-rollout-bakeoff.py) ; y_end = last round
            rho * own_spread
Rounds whose agreement rho is unmeasurable (None -- overwhelmingly spread = 0,
i.e. the pool has collapsed to duplicates) are placed at the forecast move 0.

Palette (INK/BLUE/GREEN/RED/GRAY + PURPLE/AMBER from the experiment kit),
esc()/wrap() copied from docs/figures/src/make_figures.py (house style).
Categorical family palette validated with the dataviz skill's
validate_palette.js (light mode: all checks pass, worst adjacent CVD 13.7).
Regenerate with:  python3 field-value-gap-startend.py
"""
import json
import math
import os
from collections import defaultdict, Counter

HERE = os.path.dirname(os.path.abspath(__file__))
EXP = os.path.join(HERE, "..", "..", "..", "..", "experiments")
UNIFIED = os.path.join(EXP, "spread_util_unified.json")

# ---- palette (house style; make_figures.py + experiment-kit constants) ----
INK = "#1a1a1a"
BLUE = "#2867b5"       # Qwen risk grid
GREEN = "#3a7d44"      # OLMo risk grid + judge schedules
AMBER = "#b5842c"      # OLMo mixed-pool interventions
PURPLE = "#8a5a9e"     # oracle & injection
RED = "#b5342c"        # Qwen insecure-code loops (the supplier-removal reversal)
GRAY = "#6b7684"
FAINT = "#e4e4e0"
FIELD = "#c9cdd4"      # background recurrence field (recessive)
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


def line(x1, y1, x2, y2, color, sw=1.0, dash=None, opacity=1.0):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    o = f' stroke-opacity="{opacity}"' if opacity != 1.0 else ""
    return (f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" '
            f'stroke="{color}" stroke-width="{sw}"{d}{o}/>')


# ======================================================================
# read data + build one (start, end) record per run
# ======================================================================
with open(UNIFIED) as f:
    D = json.load(f)
RECORDS = D["records"]
assert D["n_runs"] == 74 and D["n_records"] == 340, (D["n_runs"], D["n_records"])


def family_of(r):
    org, axis, judge = r["organism"], r["axis"], r["judge"]
    fmt, comp = r["format"], r["composition"]
    if judge == "score oracle":
        return "oracle & injection"
    if org == "Qwen" and axis == "risk":
        return "Qwen risk grid"
    if org == "Qwen" and axis == "selfreport":
        return "Qwen insecure-code loops"
    if org == "OLMo" and axis == "risk":
        if comp == "self-only" and fmt == "reference":
            return "OLMo risk grid + judge schedules"
        return "OLMo mixed-pool interventions"
    raise ValueError((org, axis, judge, fmt, comp))


# family display + palette order (matches the validated adjacency order)
FAMS = [
    ("Qwen risk grid", BLUE),
    ("OLMo risk grid + judge schedules", GREEN),
    ("OLMo mixed-pool interventions", AMBER),
    ("oracle & injection", PURPLE),
    ("Qwen insecure-code loops", RED),
]
FAM_COLOR = dict(FAMS)
FAM_EXPECT = {"Qwen risk grid": 16, "OLMo risk grid + judge schedules": 21,
              "OLMo mixed-pool interventions": 18, "oracle & injection": 11,
              "Qwen insecure-code loops": 8}


def rho_sigma(r):
    """Forecast one-round move rho*sigma; unmeasurable agreement -> 0."""
    rho = r["rho"]
    if rho is None:
        return 0.0
    return rho * r["own_spread"]


_groups = defaultdict(list)
for _r in RECORDS:
    _groups[(_r["cond"], _r["seed"], _r["source"])].append(_r)
RUNS = {k: sorted(v, key=lambda r: r["round"]) for k, v in _groups.items()}
assert len(RUNS) == 74, len(RUNS)

fam_ct = Counter()
swap_ct = Counter()
ARROWS = []
for k, rows in RUNS.items():
    first, last = rows[0], rows[-1]
    assert first["round"] == 1, k
    fam = family_of(first)
    fam_ct[fam] += 1
    swap = (first["judge"] == "schedule")           # scheduled judge swap
    if swap:
        swap_ct[fam] += 1
    v1 = first["value"]
    y1 = rho_sigma(first)
    v2 = last["value"] + last["drift"]              # observed() endpoint
    y2 = rho_sigma(last)
    ARROWS.append({"fam": fam, "swap": swap,
                   "v1": v1, "y1": y1, "v2": v2, "y2": y2})

assert dict(fam_ct) == FAM_EXPECT, dict(fam_ct)
N_SWAP = sum(swap_ct.values())
assert N_SWAP == 9, N_SWAP
# swaps are entirely inside the OLMo risk grid / schedules family
assert set(swap_ct) == {"OLMo risk grid + judge schedules"}, dict(swap_ct)

# value + forecast-move ranges actually present (assert, don't transcribe)
_allx = [a["v1"] for a in ARROWS] + [a["v2"] for a in ARROWS]
_ally = [a["y1"] for a in ARROWS] + [a["y2"] for a in ARROWS]
assert min(_allx) >= 0.0 and max(_allx) <= 1.0, (min(_allx), max(_allx))
assert -0.35 < min(_ally) and max(_ally) < 0.42, (min(_ally), max(_ally))

# ======================================================================
# geometry
# ======================================================================
W, H = 1240, 860
plot_x0, plot_x1 = 118, 1150
plot_top, plot_bot = 150, 636
plot_w = plot_x1 - plot_x0
plot_h = plot_bot - plot_top
Y_MIN, Y_MAX = -0.36, 0.42


def X(v):
    return plot_x0 + v * plot_w


def Y(y):
    return plot_bot - (y - Y_MIN) / (Y_MAX - Y_MIN) * plot_h


S = []

# ---- markers: one filled + one open arrowhead per family color -----------
DEFS = ['<defs>']
COLORS = [c for _, c in FAMS]
for i, c in enumerate(COLORS):
    DEFS.append(
        f'<marker id="af{i}" viewBox="0 0 10 10" refX="8.5" refY="5" '
        f'markerWidth="6.5" markerHeight="6.5" orient="auto-start-reverse">'
        f'<path d="M 0 0 L 10 5 L 0 10 z" fill="{c}"/></marker>')
    DEFS.append(
        f'<marker id="ao{i}" viewBox="0 0 12 12" refX="9.5" refY="6" '
        f'markerWidth="7.5" markerHeight="7.5" orient="auto-start-reverse">'
        f'<path d="M 1 1 L 11 6 L 1 11 z" fill="white" stroke="{c}" '
        f'stroke-width="1.6"/></marker>')
DEFS.append(
    f'<marker id="afield" viewBox="0 0 10 10" refX="8" refY="5" '
    f'markerWidth="5" markerHeight="5" orient="auto-start-reverse">'
    f'<path d="M 0 1.5 L 10 5 L 0 8.5 z" fill="{FIELD}"/></marker>')
DEFS.append('</defs>')
S.append("\n".join(DEFS))

# ---- headline + orientation ----------------------------------------------
S.append(txt(plot_x0 - 74, 52,
             "Each run's start and end in the (behavioral value, "
             "forecast-move) plane", 24, INK, "bold"))
S.append(txt(plot_x0 - 74, 84,
             "Open dot = round 1  →  filled arrowhead = final round.  "
             "Background field: the self-only recurrence  Δ value = "
             "ρ·σ  (right above the line, left below).",
             16, GRAY))
S.append(txt(plot_x0 - 74, 108,
             "One straight arrow per run (no intermediate rounds).  The 9 "
             "scheduled-judge-swap runs are drawn hollow (dashed, open head) "
             "— the self-only field omits their swap.",
             16, GRAY))

# ---- plot frame + reference lines ----------------------------------------
# faint horizontal gridlines
for gy in (-0.3, -0.2, -0.1, 0.1, 0.2, 0.3, 0.4):
    S.append(line(plot_x0, Y(gy), plot_x1, Y(gy), FAINT, 1.0))
    S.append(txt(plot_x0 - 12, Y(gy) + 5, f"{gy:+.1f}", 13, GRAY, anchor="end"))
# bold y = 0 line (no move)
S.append(line(plot_x0, Y(0.0), plot_x1, Y(0.0), INK, 2.2))
S.append(txt(plot_x0 - 12, Y(0.0) + 5, "0", 14, INK, "bold", anchor="end"))
# walls at v = 0 and v = 1
for wv in (0.0, 1.0):
    S.append(line(X(wv), plot_top, X(wv), plot_bot, INK, 2.2))
# x ticks
for gv in (0.0, 0.25, 0.5, 0.75, 1.0):
    S.append(line(X(gv), plot_bot, X(gv), plot_bot + 6, GRAY, 1.2))
    S.append(txt(X(gv), plot_bot + 24, f"{gv:g}", 14, GRAY, anchor="middle"))
# wall captions
S.append(txt(X(0.0) + 8, plot_top + 16, "wall v = 0", 13, GRAY))
S.append(txt(X(1.0) - 8, plot_top + 16, "wall v = 1", 13, GRAY, anchor="end"))

# ---- background recurrence field -----------------------------------------
# horizontal arrows; length proportional to y (schematic scale), pointing
# toward higher value above the line and lower value below it, clipped at walls.
FIELD_SCALE = 0.55           # value-units of arrow per unit of |rho*sigma|
xcols = [0.10 + 0.10 * i for i in range(9)]        # 0.10 .. 0.90
yrows = [round(-0.30 + 0.06 * i, 2) for i in range(11)]   # -0.30 .. +0.30
for yy in yrows:
    if abs(yy) < 0.03:
        continue
    for xc in xcols:
        length = abs(yy) * FIELD_SCALE               # in value units
        if yy > 0:
            x_start, x_end = xc, min(1.0, xc + length)
        else:
            x_start, x_end = xc, max(0.0, xc - length)
        if abs(x_end - x_start) < 0.006:
            continue
        S.append(f'<line x1="{X(x_start):.2f}" y1="{Y(yy):.2f}" '
                 f'x2="{X(x_end):.2f}" y2="{Y(yy):.2f}" stroke="{FIELD}" '
                 f'stroke-width="1.4" marker-end="url(#afield)"/>')

# ---- run arrows (start -> end) -------------------------------------------
# draw swaps first (recessive), solid runs on top
order = sorted(range(len(ARROWS)), key=lambda i: (not ARROWS[i]["swap"]))
for i in order:
    a = ARROWS[i]
    ci = COLORS.index(FAM_COLOR[a["fam"]])
    color = COLORS[ci]
    x1p, y1p, x2p, y2p = X(a["v1"]), Y(a["y1"]), X(a["v2"]), Y(a["y2"])
    if a["swap"]:
        S.append(f'<line x1="{x1p:.2f}" y1="{y1p:.2f}" x2="{x2p:.2f}" '
                 f'y2="{y2p:.2f}" stroke="{color}" stroke-width="1.6" '
                 f'stroke-opacity="0.85" stroke-dasharray="5 4" '
                 f'marker-end="url(#ao{ci})"/>')
        S.append(f'<circle cx="{x1p:.2f}" cy="{y1p:.2f}" r="3.6" '
                 f'fill="white" stroke="{color}" stroke-width="1.6"/>')
    else:
        S.append(f'<line x1="{x1p:.2f}" y1="{y1p:.2f}" x2="{x2p:.2f}" '
                 f'y2="{y2p:.2f}" stroke="{color}" stroke-width="1.7" '
                 f'stroke-opacity="0.82" marker-end="url(#af{ci})"/>')
        S.append(f'<circle cx="{x1p:.2f}" cy="{y1p:.2f}" r="3.7" '
                 f'fill="white" stroke="{color}" stroke-width="1.7"/>')

# ---- axis labels ---------------------------------------------------------
S.append(txt((plot_x0 + plot_x1) / 2, plot_bot + 48,
             "behavioral value v  (fraction risk-seeking / insecure-code), "
             "0 → 1", 16, INK, anchor="middle"))
S.append(f'<text x="46" y="{(plot_top + plot_bot) / 2:.1f}" '
         f'font-family="{FONT}" font-size="16" fill="{INK}" '
         f'text-anchor="middle" transform="rotate(-90 46 '
         f'{(plot_top + plot_bot) / 2:.1f})">forecast one-round move  '
         f'ρ·σ  (round agreement × spread)</text>')

# ---- key -----------------------------------------------------------------
ky = plot_bot + 78
kx = plot_x0 - 74
S.append(txt(kx, ky, "Experiment family", 15, INK, "bold"))
kyy = ky + 26
# two columns: families 0-2 on the left, 3-4 on the right
COL_A, COL_B = kx, kx + 540
for j, (fam, color) in enumerate(FAMS):
    if j < 3:
        lx, ly = COL_A, kyy + j * 26
    else:
        lx, ly = COL_B, kyy + (j - 3) * 26
    ci = COLORS.index(color)
    S.append(f'<line x1="{lx}" y1="{ly - 5}" x2="{lx + 30}" y2="{ly - 5}" '
             f'stroke="{color}" stroke-width="2.4" marker-end="url(#af{ci})"/>')
    S.append(f'<circle cx="{lx + 4}" cy="{ly - 5}" r="3.7" fill="white" '
             f'stroke="{color}" stroke-width="1.7"/>')
    n = fam_ct[fam]
    tag = f"{fam}  ({n} runs)"
    if swap_ct[fam]:
        tag = f"{fam}  ({n} runs; {swap_ct[fam]} hollow)"
    S.append(txt(lx + 40, ly, tag, 15, INK))

# glyph key (start / end) + notes, far right
gx = kx + 856
gy0 = kyy
S.append(f'<circle cx="{gx + 4}" cy="{gy0 - 5}" r="3.7" fill="white" '
         f'stroke="{INK}" stroke-width="1.7"/>')
S.append(f'<line x1="{gx}" y1="{gy0 - 5}" x2="{gx + 44}" y2="{gy0 - 5}" '
         f'stroke="{INK}" stroke-width="2.0" marker-end="url(#af0)"/>')
S.append(txt(gx + 54, gy0, "round 1 → final", 15, INK))
S.append(txt(gx, gy0 + 26,
             "field: schematic, length ∝ ρ·σ", 13, GRAY))
S.append(txt(gx, gy0 + 48,
             "ρ unmeasurable (σ→0) → move 0", 13, GRAY))

# ---- source footnote -----------------------------------------------------
fy = ky + 108
S.append(txt(plot_x0 - 74, fy,
             "Coordinates computed live (stdlib) from "
             "experiments/spread_util_unified.json: start = round-1 (value, "
             "ρ·own_spread); end = (last value + drift, last "
             "ρ·own_spread).", 13, GRAY))
S.append(txt(plot_x0 - 74, fy + 18,
             "Endpoint convention matches spread-rollout-bakeoff.py observed(); "
             "families are the run-inventory.py names.  Generator: "
             "field-value-gap-startend.py", 13, GRAY))

svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
       f'font-family="{FONT}">\n'
       f'<rect width="{W}" height="{H}" fill="white"/>\n'
       + "\n".join(S) + "\n</svg>")

out = os.path.join(HERE, "field-value-gap-startend.svg")
with open(out, "w") as f:
    f.write(svg)
print(f"wrote {out}  viewBox 0 0 {W} {H}  ({len(ARROWS)} runs, {N_SWAP} swaps)")
