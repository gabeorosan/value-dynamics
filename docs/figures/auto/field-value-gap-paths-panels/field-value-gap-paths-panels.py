#!/usr/bin/env python3
"""Each run's round-by-round PATH in the (behavioral value, forecast-move) plane
(slug: field-value-gap-paths-panels) -- FIELD CANDIDATE L.

Candidate L is the round-by-round alternative to field-value-gap-startend
(candidate for the same slot).  The plane is identical: x = behavioral value v in
[0, 1] with hard walls at v = 0 and v = 1, y = the forecast one-round move
rho * sigma (round agreement times within-prompt spread own_spread), the selection
term of the parameter-free unit recurrence Delta v = rho * sigma for a self-only
pool.  Five panels (one per committed experiment family) plus a shared key sit in a
3-wide x 2-tall grid; every panel shares the same axes (value 0..1, forecast move
-0.36..+0.42 with a bold y = 0 line) and the same faint background field.

THE DIFFERENCE FROM CANDIDATE field-value-gap-startend.  That figure drew ONE
straight arrow per run, dot-to-arrowhead, skipping every intermediate round.  But
the background field encodes a ONE-ROUND move (Delta v = rho * sigma per round), so
a straight multi-round arrow is a different kind of object than the field arrows it
is overlaid on -- and for the 9 scheduled-judge-swap runs, whose rho*sigma shifts
mid-run, a single straight arrow is doubly misleading.  Candidate L instead draws
each run as its ACTUAL round-by-round path: a polyline through every round's
(value_r, rho_r * sigma_r) coordinate.  Now each path SEGMENT is the same
one-round object as a background field arrow.

Path convention (matches the startend endpoint convention, extended to every
round):
  * round 1     open dot at (value_1, rho_1 * sigma_1)
  * rounds 2..n-1   small filled vertices at (value_r, rho_r * sigma_r)
  * final round n   filled arrowhead at (value_n + drift_n, rho_n * sigma_n)
            -- the observed() endpoint convention adds the last round's drift on x
Rounds whose agreement rho is unmeasurable (None -- overwhelmingly own_spread = 0,
i.e. the pool has collapsed to duplicates) are plotted at forecast move 0.

The 9 scheduled-judge-swap runs (all inside the OLMo risk-grid + judge-schedules
family) draw as normal round-by-round paths in their family color but DASHED.  The
records' `judge` field is the constant string "schedule" for every round of those
runs, so the swap round is NOT identifiable from this file: no swap-round marker is
drawn, and the key/caption say so explicitly.

Background field (unchanged from field-value-gap-startend).  From grid point (v, y)
the schematic field arrow moves the value by Delta v = y * FIELD_SCALE (clipped at
the walls).  On the three all-risk-axis panels (Qwen risk grid; OLMo risk grid +
judge schedules; OLMo mixed-pool interventions) it also carries a VERTICAL step
Delta y = y * (env(v + Delta v) / env(v) - 1) with env(v) = sqrt(v * (1 - v)): as
the value moves toward a wall the binary envelope contracts, so sigma and hence
rho*sigma bend toward zero.  The two panels containing continuous self-description
runs (Qwen insecure-code loops, all self-report; oracle & injection, mixed 4 risk +
7 self-report) instead bend by the MEASURED continuous-axis coupling
Delta(rho*sigma) ~= EMP_SLOPE * Delta v, loaded live from the committed analysis
experiments/field_vertical_component.json.

All coordinates are computed live from experiments/spread_util_unified.json.
Palette (INK/BLUE/GREEN/RED/GRAY + PURPLE/AMBER from the experiment kit) and
esc()/wrap() copied from docs/figures/src/make_figures.py (house style).
Regenerate with:  python3 field-value-gap-paths-panels.py
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
# read data + build one round-by-round PATH per run
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

# panels whose runs are all binary risk axis get the envelope-bent field;
# the two panels containing continuous self-description runs get the MEASURED
# continuous-axis coupling instead (a flat field would assert unestablished
# dynamics just as much as a bent one) -- slope loaded live from the analysis
BENT_FAMS = {"Qwen risk grid", "OLMo risk grid + judge schedules",
             "OLMo mixed-pool interventions"}
with open(os.path.join(EXP, "field_vertical_component.json")) as _fvc:
    _FVC = json.load(_fvc)
EMP_SLOPE = _FVC["selfreport"]["dy_on_dv_slope"]     # -0.1729 (r = -0.567)
assert -0.30 < EMP_SLOPE < -0.05, EMP_SLOPE
EMP_NOTE = ("field bend: the measured continuous-axis coupling "
            f"Δ(ρ·σ) ≈ −{abs(EMP_SLOPE):.2f}·Δv")


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
PATHS = []
for k, rows in RUNS.items():
    first, last = rows[0], rows[-1]
    assert first["round"] == 1, k
    fam = family_of(first)
    fam_ct[fam] += 1
    fam_axes[fam].add(first["axis"])
    swap = (first["judge"] == "schedule")           # scheduled judge swap
    if swap:
        swap_ct[fam] += 1
    # per-round polyline points; only the FINAL round adds drift on x
    pts = []
    n = len(rows)
    for i, r in enumerate(rows):
        vx = r["value"] + (r["drift"] if i == n - 1 else 0.0)
        pts.append((vx, rho_sigma(r)))
    PATHS.append({"fam": fam, "swap": swap, "pts": pts})

assert dict(fam_ct) == FAM_EXPECT, dict(fam_ct)
N_SWAP = sum(swap_ct.values())
assert N_SWAP == 9, N_SWAP
# swaps are entirely inside the OLMo risk grid / schedules family
assert set(swap_ct) == {"OLMo risk grid + judge schedules"}, dict(swap_ct)
# the swap round is not identifiable: judge is the constant "schedule" every round
for k, rows in RUNS.items():
    if rows[0]["judge"] == "schedule":
        assert all(r["judge"] == "schedule" for r in rows), k

# which families are pure risk-axis (so the bent field is licensed)
PURE_RISK = {fam for fam, axes in fam_axes.items() if axes == {"risk"}}
assert BENT_FAMS == PURE_RISK, (BENT_FAMS, PURE_RISK)

# value + forecast-move ranges actually present (assert every round, not just ends)
_allx = [p[0] for a in PATHS for p in a["pts"]]
_ally = [p[1] for a in PATHS for p in a["pts"]]
assert min(_allx) >= 0.0 and max(_allx) <= 1.0, (min(_allx), max(_allx))
assert -0.36 < min(_ally) and max(_ally) < 0.42, (min(_ally), max(_ally))

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
H = TOP + 2 * CELL_H + 40            # 1084 (no in-figure footnote)

FIELD_SCALE = 0.55                   # value-units of arrow per unit of rho*sigma
xcols = [round(0.10 + 0.10 * i, 2) for i in range(9)]       # 0.10 .. 0.90
yrows = [round(-0.30 + 0.06 * i, 2) for i in range(11)]     # -0.30 .. +0.30


def env(v):
    return math.sqrt(max(0.0, v * (1.0 - v)))


def PX(v, ox):
    return ox + v * PW


def PYc(y, top):
    return (top + PH) - (y - Y_MIN) / (Y_MAX - Y_MIN) * PH


# ---- markers: one filled arrowhead per family color ----------------------
DEFS = ['<defs>']
for i, c in enumerate(COLORS):
    DEFS.append(
        f'<marker id="af{i}" viewBox="0 0 10 10" refX="8.5" refY="5" '
        f'markerWidth="6.5" markerHeight="6.5" orient="auto-start-reverse">'
        f'<path d="M 0 0 L 10 5 L 0 10 z" fill="{c}"/></marker>')
DEFS.append(
    f'<marker id="afield" viewBox="0 0 10 10" refX="8" refY="5" '
    f'markerWidth="5" markerHeight="5" orient="auto-start-reverse">'
    f'<path d="M 0 1.5 L 10 5 L 0 8.5 z" fill="{FIELD}"/></marker>')
DEFS.append('</defs>')

S = ["\n".join(DEFS)]

# ---- headline + orientation ----------------------------------------------
S.append(txt(LM, 46,
             "Each run's round-by-round path in the (value, forecast-move) "
             "plane", 25, INK, "bold"))
S.append(txt(LM, 80,
             "Candidate L. Each run is a polyline through EVERY measured round: "
             "open dot = round 1, small vertices = intermediate rounds, filled "
             "arrowhead = final round.", 16, GRAY))
S.append(txt(LM, 104,
             "Each path segment is now the same one-round object (Δ value = ρ·σ) "
             "as a background field arrow. The 9 scheduled-judge-swap runs are "
             "dashed; their swap round is not marked (see key).", 16, GRAY))


# ---- background field (unchanged from field-value-gap-startend) -----------
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
                dv = yy * FIELD_SCALE
                ve = min(1.0, max(0.0, xc + dv))
                x1, y1v, x2, y2v = xc, yy, ve, yy + EMP_SLOPE * (ve - xc)
            if abs(x2 - x1) < 0.006 and abs(y2v - y1v) < 0.004:
                continue
            out.append(
                f'<line x1="{PX(x1, ox):.2f}" y1="{PYc(y1v, top):.2f}" '
                f'x2="{PX(x2, ox):.2f}" y2="{PYc(y2v, top):.2f}" '
                f'stroke="{FIELD}" stroke-width="1.4" '
                f'marker-end="url(#afield)"/>')
    return out


# ---- one panel ------------------------------------------------------------
def draw_panel(fam, col, row):
    ox = LM + col * CELL_W + YLAB_W
    top = TOP + row * CELL_H + TITLE_H
    bot = top + PH
    color = FAM_COLOR[fam]
    ci = COLORS.index(color)
    bent = fam in BENT_FAMS
    out = []

    # panel title (family name + run count + dashed count)
    n = fam_ct[fam]
    title = f"{fam} — {n} runs"
    if swap_ct[fam]:
        title = f"{fam} — {n} runs ({swap_ct[fam]} dashed judge-swap)"
    out.append(txt(ox, top - 14, title, 16, INK, "bold"))

    # faint horizontal gridlines
    for gy in (-0.3, -0.2, -0.1, 0.1, 0.2, 0.3, 0.4):
        out.append(line(ox, PYc(gy, top), ox + PW, PYc(gy, top), FAINT, 1.0))
    # y ticks / labels (thinned: -0.3, 0, +0.3)
    for gy in (-0.3, 0.0, 0.3):
        out.append(txt(ox - 10, PYc(gy, top) + 5,
                       f"{gy:+.1f}".replace("+0.0", "0"),
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
        out.append(txt(PX(gv, ox), bot + 24, f"{gv:g}", 13, GRAY,
                       anchor="middle"))

    # this family's run paths (swaps recessive underneath)
    fam_paths = [p for p in PATHS if p["fam"] == fam]
    order = sorted(range(len(fam_paths)),
                   key=lambda i: (not fam_paths[i]["swap"]))
    for i in order:
        a = fam_paths[i]
        pts = a["pts"]
        scr = [(PX(v, ox), PYc(y, top)) for (v, y) in pts]
        dash = ' stroke-dasharray="5 4"' if a["swap"] else ""
        sw = 1.7
        poly = " ".join(f"{x:.2f},{y:.2f}" for (x, y) in scr)
        # full polyline through every round (no marker on the joints)
        out.append(f'<polyline points="{poly}" fill="none" stroke="{color}" '
                   f'stroke-width="{sw}" stroke-opacity="0.85" '
                   f'stroke-linejoin="round" stroke-linecap="round"{dash}/>')
        # filled arrowhead on the FINAL segment only
        if len(scr) >= 2:
            (xa, ya), (xb, yb) = scr[-2], scr[-1]
            out.append(f'<line x1="{xa:.2f}" y1="{ya:.2f}" x2="{xb:.2f}" '
                       f'y2="{yb:.2f}" stroke="{color}" stroke-width="{sw}" '
                       f'stroke-opacity="0.85"{dash} '
                       f'marker-end="url(#af{ci})"/>')
        # intermediate-round vertices (small filled dots)
        for (x, y) in scr[1:-1]:
            out.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="2.5" '
                       f'fill="{color}" fill-opacity="0.85"/>')
        # round-1 start (open dot)
        x0, y0 = scr[0]
        out.append(f'<circle cx="{x0:.2f}" cy="{y0:.2f}" r="3.7" fill="white" '
                   f'stroke="{color}" stroke-width="1.7"/>')

    # flat-field note inside horizontal panels (top-left corner is clear)
    if not bent:
        for j, ln in enumerate(wrap(EMP_NOTE, 34)):
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
# glyph: round 1 -> intermediate vertices -> final round (a path)
S.append(f'<circle cx="{kox + 5}" cy="{ly - 5}" r="3.7" fill="white" '
         f'stroke="{INK}" stroke-width="1.7"/>')
S.append(f'<polyline points="{kox + 5},{ly - 5} {kox + 22},{ly - 11} '
         f'{kox + 40},{ly - 1} {kox + 58},{ly - 8}" fill="none" '
         f'stroke="{INK}" stroke-width="2.0" stroke-linejoin="round"/>')
S.append(f'<circle cx="{kox + 22}" cy="{ly - 11}" r="2.5" fill="{INK}"/>')
S.append(f'<circle cx="{kox + 40}" cy="{ly - 1}" r="2.5" fill="{INK}"/>')
S.append(f'<line x1="{kox + 40}" y1="{ly - 1}" x2="{kox + 58}" y2="{ly - 8}" '
         f'stroke="{INK}" stroke-width="2.0" marker-end="url(#af0)"/>')
S.append(txt(kox + 72, ly, "one run = a polyline through every round:", 14, INK))
ly += 20
S.append(txt(kox + 72, ly, "open dot = round 1  ·  small dot = each",
             13.5, GRAY))
ly += 18
S.append(txt(kox + 72, ly, "intermediate round  ·  filled head = final round",
             13.5, GRAY))

# each SEGMENT is a one-round move, same object as the field
ly += 28
S.append(txt(kox, ly,
             "Each segment is one round's move Δ value = ρ·σ —", 14, INK))
ly += 20
S.append(txt(kox, ly,
             "the same object the faint field arrows draw.", 14, INK))

# glyph: scheduled judge swap (dashed)
ly += 30
S.append(f'<polyline points="{kox + 1},{ly - 5} {kox + 28},{ly - 9} '
         f'{kox + 54},{ly - 3}" fill="none" stroke="{GREEN}" '
         f'stroke-width="1.7" stroke-dasharray="5 4"/>')
S.append(f'<circle cx="{kox + 1}" cy="{ly - 5}" r="3.4" fill="white" '
         f'stroke="{GREEN}" stroke-width="1.6"/>')
S.append(txt(kox + 66, ly, "scheduled judge swap (dashed path) —", 14, INK))
ly += 20
for wln in wrap("the judge field reads the constant \"schedule\" every round, "
                "so the swap round is not identifiable from this file and is "
                "not marked.", 46):
    S.append(txt(kox + 66, ly, wln, 13, GRAY))
    ly += 18

# field notes
notes = [
    "field: the self-only recurrence Δ value = ρ·σ, "
    "length ∝ ρ·σ (schematic)",
    "risk panels: field bends toward the walls — spread tracks the "
    "binary envelope √(v(1−v))",
    "self-description panels: field bends by the measured coupling "
    f"Δ(ρ·σ) ≈ −{abs(EMP_SLOPE):.2f}·Δv",
    "ρ unmeasurable (σ → 0)  →  round plotted at 0",
]
ly += 14
for note in notes:
    for j, wln in enumerate(wrap(note, 48)):
        S.append(txt(kox, ly, wln, 13.5, GRAY))
        ly += 19
    ly += 3

# family colour legend
ly += 4
S.append(txt(kox, ly, "Family colors", 14, INK, "bold"))
ly += 22
for fam, color in FAMS:
    ci = COLORS.index(color)
    S.append(f'<circle cx="{kox + 5}" cy="{ly - 5}" r="3.7" fill="white" '
             f'stroke="{color}" stroke-width="1.7"/>')
    S.append(f'<line x1="{kox + 1}" y1="{ly - 5}" x2="{kox + 38}" y2="{ly - 5}" '
             f'stroke="{color}" stroke-width="2.2" marker-end="url(#af{ci})"/>')
    S.append(txt(kox + 50, ly, fam, 13.5, INK))
    ly += 22

# ---- no in-figure footnote: provenance lives in caption.md ----------------

svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
       f'font-family="{FONT}">\n'
       f'<rect width="{W}" height="{H}" fill="white"/>\n'
       + "\n".join(S) + "\n</svg>")

out = os.path.join(HERE, "field-value-gap-paths-panels.svg")
with open(out, "w") as f:
    f.write(svg)
print(f"wrote {out}  viewBox 0 0 {W} {H}  ({len(PATHS)} runs, {N_SWAP} dashed "
      f"judge-swap; bent panels {sorted(BENT_FAMS)})")
