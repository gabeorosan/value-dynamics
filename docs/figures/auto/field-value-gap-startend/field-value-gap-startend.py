#!/usr/bin/env python3
"""Each run's start and end in the (behavioral value, forecast-move) plane
(slug: field-value-gap-startend) -- one panel per experiment family.

The plane is x = behavioral value v in [0, 1], y = the forecast one-round move
rho * sigma (round agreement times within-prompt spread), the selection term of
the parameter-free unit recurrence Delta v = rho * sigma for a self-only pool.
The figure is split into five panels, one per committed experiment family, plus
a sixth slot holding the shared key.  Every panel shares the same axes (value
0..1 with hard walls at v = 0 and v = 1, forecast move -0.36..+0.42 with a bold
y = 0 line) and the same faint background field.  Each panel draws ONLY its own
family's run arrows: ONE straight arrow per run from its round-1 coordinates
(v_1, rho_1*sigma_1) -- open dot -- to its final coordinates (v_end,
rho_end*sigma_end) -- filled arrowhead.  No intermediate vertices.  The 9
scheduled-judge-swap runs (all inside the OLMo risk-grid family) are drawn
hollow (dashed, open arrowhead), since the self-only field omits the swap.

Background field.  From grid point (v, y) the schematic field arrow moves the
value by Delta v = y * FIELD_SCALE (clipped at the walls).  On the three
all-risk-axis panels (Qwen risk grid; OLMo risk grid + judge schedules; OLMo
mixed-pool interventions) the arrow also carries a VERTICAL component
Delta y = y * (env(v + Delta v) / env(v) - 1) with env(v) = sqrt(v * (1 - v)):
as the value moves toward a wall the binary envelope contracts, so sigma and
hence rho*sigma bend down toward zero; near v = 0.5 the envelope is flat and the
field is nearly horizontal.  This envelope identity is committed only for the
binary risk axis, so the two panels containing self-report-axis runs (Qwen
insecure-code loops, all self-report; oracle & injection, mixed 4 risk + 7 self-
report) keep a purely HORIZONTAL field and carry a note to that effect.

All coordinates are computed live from experiments/spread_util_unified.json:
  * start   v_1 = round-1 value ; y_1 = round-1 rho * own_spread
  * end     v_end = last round value + drift (the observed() endpoint
            convention of spread-rollout-bakeoff.py) ; y_end = last round
            rho * own_spread
Rounds whose agreement rho is unmeasurable (None -- overwhelmingly spread = 0,
i.e. the pool has collapsed to duplicates) are placed at the forecast move 0.

Palette (INK/BLUE/GREEN/RED/GRAY + PURPLE/AMBER from the experiment kit),
esc()/wrap() copied from docs/figures/src/make_figures.py (house style).
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
COLORS = [c for _, c in FAMS]

# panels whose runs are all binary risk axis get the bent (envelope) field
BENT_FAMS = {"Qwen risk grid", "OLMo risk grid + judge schedules",
             "OLMo mixed-pool interventions"}
FLAT_NOTE = ("flat field: the spread–envelope identity is committed only "
             "for the binary risk axis")


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
fam_axes = defaultdict(set)
ARROWS = []
for k, rows in RUNS.items():
    first, last = rows[0], rows[-1]
    assert first["round"] == 1, k
    fam = family_of(first)
    fam_ct[fam] += 1
    fam_axes[fam].add(first["axis"])
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

# which families are pure risk-axis (so the bent field is licensed)
PURE_RISK = {fam for fam, axes in fam_axes.items() if axes == {"risk"}}
# committed scope: only the three all-risk families bend; oracle&injection is
# mixed (4 risk + 7 self-report) and Qwen insecure-code loops is all self-report
assert BENT_FAMS == PURE_RISK, (BENT_FAMS, PURE_RISK)

# value + forecast-move ranges actually present (assert, don't transcribe)
_allx = [a["v1"] for a in ARROWS] + [a["v2"] for a in ARROWS]
_ally = [a["y1"] for a in ARROWS] + [a["y2"] for a in ARROWS]
assert min(_allx) >= 0.0 and max(_allx) <= 1.0, (min(_allx), max(_allx))
assert -0.35 < min(_ally) and max(_ally) < 0.42, (min(_ally), max(_ally))

# ======================================================================
# geometry -- 3-wide x 2-tall grid of panels
# ======================================================================
Y_MIN, Y_MAX = -0.36, 0.42
PW, PH = 480, 330                     # per-panel plot area
YLAB_W, RIGHTPAD = 74, 26            # room for y ticks/title, right padding
TITLE_H, XLAB_H = 40, 66             # room for panel title, x ticks/title
CELL_W = YLAB_W + PW + RIGHTPAD      # 580
CELL_H = TITLE_H + PH + XLAB_H       # 436
LM, TOP = 26, 156                    # left margin, top of grid
W = LM + 3 * CELL_W + 12             # 1778
H = TOP + 2 * CELL_H + 96            # 1140

FIELD_SCALE = 0.55                   # value-units of arrow per unit of rho*sigma
xcols = [round(0.10 + 0.10 * i, 2) for i in range(9)]       # 0.10 .. 0.90
yrows = [round(-0.30 + 0.06 * i, 2) for i in range(11)]     # -0.30 .. +0.30


def env(v):
    return math.sqrt(max(0.0, v * (1.0 - v)))


def PX(v, ox):
    return ox + v * PW


def PYc(y, top):
    return (top + PH) - (y - Y_MIN) / (Y_MAX - Y_MIN) * PH


# ---- markers: one filled + one open arrowhead per family color -----------
DEFS = ['<defs>']
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

S = [ "\n".join(DEFS) ]

# ---- headline + orientation ----------------------------------------------
S.append(txt(LM, 46,
             "Each run's start and end in the (behavioral value, "
             "forecast-move) plane", 25, INK, "bold"))
S.append(txt(LM, 80,
             "Open dot = round 1  →  filled arrowhead = final round.  One "
             "straight arrow per run (no intermediate rounds), one panel per "
             "experiment family.", 16, GRAY))
S.append(txt(LM, 104,
             "The 9 scheduled-judge-swap runs are drawn hollow (dashed, open "
             "head).  Faint background field: the self-only recurrence  Δ "
             "value = ρ·σ.", 16, GRAY))


# ---- one panel ------------------------------------------------------------
def field_arrows(ox, top, bent):
    out = []
    for yy in yrows:
        if abs(yy) < 0.03:
            continue
        for xc in xcols:
            if bent:
                if xc <= 0.02 or xc >= 0.98:
                    continue
                e0 = env(xc)
                dv = yy * FIELD_SCALE
                ve = min(1.0, max(0.0, xc + dv))
                if ve <= 0.02 or ve >= 0.98:
                    continue
                ye = yy * (env(ve) / e0)
                x1, y1v, x2, y2v = xc, yy, ve, ye
            else:
                length = abs(yy) * FIELD_SCALE
                if yy > 0:
                    x1, x2 = xc, min(1.0, xc + length)
                else:
                    x1, x2 = xc, max(0.0, xc - length)
                y1v = y2v = yy
            if abs(x2 - x1) < 0.006 and abs(y2v - y1v) < 0.004:
                continue
            out.append(
                f'<line x1="{PX(x1, ox):.2f}" y1="{PYc(y1v, top):.2f}" '
                f'x2="{PX(x2, ox):.2f}" y2="{PYc(y2v, top):.2f}" '
                f'stroke="{FIELD}" stroke-width="1.4" '
                f'marker-end="url(#afield)"/>')
    return out


def draw_panel(fam, col, row):
    ox = LM + col * CELL_W + YLAB_W
    top = TOP + row * CELL_H + TITLE_H
    bot = top + PH
    color = FAM_COLOR[fam]
    ci = COLORS.index(color)
    bent = fam in BENT_FAMS
    out = []

    # panel title (family name + run count + hollow count)
    n = fam_ct[fam]
    title = f"{fam} — {n} runs"
    if swap_ct[fam]:
        title = f"{fam} — {n} runs ({swap_ct[fam]} hollow)"
    out.append(txt(ox, top - 14, title, 16, INK, "bold"))

    # faint horizontal gridlines
    for gy in (-0.3, -0.2, -0.1, 0.1, 0.2, 0.3, 0.4):
        out.append(line(ox, PYc(gy, top), ox + PW, PYc(gy, top), FAINT, 1.0))
    # y ticks / labels (thinned: -0.3, 0, +0.3)
    for gy in (-0.3, 0.0, 0.3):
        out.append(txt(ox - 10, PYc(gy, top) + 5, f"{gy:+.1f}".replace("+0.0", "0"),
                       13, GRAY, anchor="end"))

    # background field
    out += field_arrows(ox, top, bent)

    # bold y = 0 line
    out.append(line(ox, PYc(0.0, top), ox + PW, PYc(0.0, top), INK, 2.0))
    # walls at v = 0 and v = 1
    for wv in (0.0, 1.0):
        out.append(line(PX(wv, ox), top, PX(wv, ox), bot, INK, 2.0))
    # x ticks / labels (thinned: 0, 0.5, 1)
    for gv in (0.0, 0.5, 1.0):
        out.append(line(PX(gv, ox), bot, PX(gv, ox), bot + 6, GRAY, 1.2))
        out.append(txt(PX(gv, ox), bot + 24, f"{gv:g}", 13, GRAY, anchor="middle"))

    # this family's run arrows (swaps recessive underneath)
    fam_arrows = [a for a in ARROWS if a["fam"] == fam]
    order = sorted(range(len(fam_arrows)), key=lambda i: (not fam_arrows[i]["swap"]))
    for i in order:
        a = fam_arrows[i]
        x1p, y1p = PX(a["v1"], ox), PYc(a["y1"], top)
        x2p, y2p = PX(a["v2"], ox), PYc(a["y2"], top)
        if a["swap"]:
            out.append(f'<line x1="{x1p:.2f}" y1="{y1p:.2f}" x2="{x2p:.2f}" '
                       f'y2="{y2p:.2f}" stroke="{color}" stroke-width="1.6" '
                       f'stroke-opacity="0.85" stroke-dasharray="5 4" '
                       f'marker-end="url(#ao{ci})"/>')
            out.append(f'<circle cx="{x1p:.2f}" cy="{y1p:.2f}" r="3.6" '
                       f'fill="white" stroke="{color}" stroke-width="1.6"/>')
        else:
            out.append(f'<line x1="{x1p:.2f}" y1="{y1p:.2f}" x2="{x2p:.2f}" '
                       f'y2="{y2p:.2f}" stroke="{color}" stroke-width="1.7" '
                       f'stroke-opacity="0.82" marker-end="url(#af{ci})"/>')
            out.append(f'<circle cx="{x1p:.2f}" cy="{y1p:.2f}" r="3.7" '
                       f'fill="white" stroke="{color}" stroke-width="1.7"/>')

    # flat-field note inside horizontal panels (top-left corner is clear)
    if not bent:
        for j, ln in enumerate(wrap(FLAT_NOTE, 34)):
            out.append(txt(ox + 10, top + 22 + j * 17, ln, 13, GRAY))

    # panel axis labels (compact; full recipe lives in the caption)
    out.append(txt(ox + PW / 2, bot + 48,
                   "behavioral value v  (0 → 1)", 14, INK, anchor="middle"))
    ymid = (top + bot) / 2
    out.append(f'<text x="{ox - 44:.1f}" y="{ymid:.1f}" font-family="{FONT}" '
               f'font-size="14" fill="{INK}" text-anchor="middle" '
               f'transform="rotate(-90 {ox - 44:.1f} {ymid:.1f})">forecast move '
               f'ρ·σ</text>')
    return out


# panel grid positions: 5 families across (0,0)(0,1)(0,2)(1,0)(1,1); key at (1,2)
POSITIONS = {
    "Qwen risk grid": (0, 0),
    "OLMo risk grid + judge schedules": (1, 0),
    "OLMo mixed-pool interventions": (2, 0),
    "oracle & injection": (0, 1),
    "Qwen insecure-code loops": (1, 1),
}
for fam, (col, row) in POSITIONS.items():
    S += draw_panel(fam, col, row)

# ======================================================================
# shared key (sixth slot: col 2, row 1)
# ======================================================================
kox = LM + 2 * CELL_W + YLAB_W
ktop = TOP + 1 * CELL_H + TITLE_H
S.append(txt(kox, ktop - 14, "How to read every panel", 16, INK, "bold"))

ly = ktop + 22
# glyph: round 1 -> final round
S.append(f'<circle cx="{kox + 5}" cy="{ly - 5}" r="3.7" fill="white" '
         f'stroke="{INK}" stroke-width="1.7"/>')
S.append(f'<line x1="{kox + 1}" y1="{ly - 5}" x2="{kox + 46}" y2="{ly - 5}" '
         f'stroke="{INK}" stroke-width="2.0" marker-end="url(#af0)"/>')
S.append(txt(kox + 58, ly, "round 1 (open dot)  →  final round (filled head)",
             14, INK))
# glyph: scheduled judge swap
ly += 30
S.append(f'<circle cx="{kox + 5}" cy="{ly - 5}" r="3.6" fill="white" '
         f'stroke="{GREEN}" stroke-width="1.6"/>')
S.append(f'<line x1="{kox + 1}" y1="{ly - 5}" x2="{kox + 46}" y2="{ly - 5}" '
         f'stroke="{GREEN}" stroke-width="1.6" stroke-dasharray="5 4" '
         f'marker-end="url(#ao1)"/>')
S.append(txt(kox + 58, ly, "scheduled judge swap (hollow, dashed)", 14, INK))

# field notes
notes = [
    "field: the self-only recurrence Δ value = ρ·σ, "
    "length ∝ ρ·σ (schematic)",
    "risk panels: field bends down toward the walls — spread tracks the "
    "binary envelope √(v(1−v))",
    "flat-field panels: identity committed only for the binary risk axis",
    "ρ unmeasurable (σ → 0)  →  move plotted at 0",
]
ly += 34
for note in notes:
    for j, wln in enumerate(wrap(note, 48)):
        S.append(txt(kox, ly, wln, 13.5, GRAY))
        ly += 20
    ly += 4

# family colour legend
ly += 6
S.append(txt(kox, ly, "Family colors", 14, INK, "bold"))
ly += 24
for fam, color in FAMS:
    ci = COLORS.index(color)
    S.append(f'<circle cx="{kox + 5}" cy="{ly - 5}" r="3.7" fill="white" '
             f'stroke="{color}" stroke-width="1.7"/>')
    S.append(f'<line x1="{kox + 1}" y1="{ly - 5}" x2="{kox + 38}" y2="{ly - 5}" '
             f'stroke="{color}" stroke-width="2.2" marker-end="url(#af{ci})"/>')
    S.append(txt(kox + 50, ly, fam, 13.5, INK))
    ly += 24

# ---- source footnote -----------------------------------------------------
fy = TOP + 2 * CELL_H + 44
S.append(txt(LM, fy,
             "Coordinates computed live (stdlib) from "
             "experiments/spread_util_unified.json: start = round-1 (value, "
             "ρ·own_spread); end = (last value + drift, last "
             "ρ·own_spread).", 13, GRAY))
S.append(txt(LM, fy + 20,
             "Endpoint convention matches spread-rollout-bakeoff.py observed(); "
             "families are the run-inventory.py names; envelope field "
             "√(v(1−v)) is committed for the binary risk axis only.  "
             "Generator: field-value-gap-startend.py", 13, GRAY))

svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
       f'font-family="{FONT}">\n'
       f'<rect width="{W}" height="{H}" fill="white"/>\n'
       + "\n".join(S) + "\n</svg>")

out = os.path.join(HERE, "field-value-gap-startend.svg")
with open(out, "w") as f:
    f.write(svg)
print(f"wrote {out}  viewBox 0 0 {W} {H}  ({len(ARROWS)} runs, {N_SWAP} swaps; "
      f"bent panels {sorted(BENT_FAMS)})")
