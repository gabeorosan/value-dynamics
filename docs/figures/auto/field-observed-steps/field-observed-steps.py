#!/usr/bin/env python3
"""Every observed one-round move in the (behavioral value, forecast-move) plane
(slug: field-observed-steps) -- FIELD CANDIDATE M, one panel per family.

The plane is x = behavioral value v in [0, 1], y = the forecast one-round move
rho * sigma (round agreement times within-prompt spread), the selection term of
the parameter-free unit recurrence Delta v = rho * sigma for a self-only pool.
Five panels, one per committed experiment family, plus a sixth slot holding the
shared key.  Every panel shares the same axes (value 0..1 with hard walls at
v = 0 and v = 1, forecast move -0.36..+0.42 with a bold y = 0 line) and the same
faint gray background FIELD -- the model's predicted one-round move from each grid
coordinate (envelope bend on the three all-risk panels, the measured -0.17*Delta v
continuous-axis coupling on the two self-description panels).

CANDIDATE M -- the difference from field-value-gap-startend.  The field arrows are
ONE-ROUND moves, so the overlaid data are one-round moves too.  Instead of one
straight start-to-end arrow per run, every observed ROUND TRANSITION is drawn as
its own short colored arrow: for each consecutive round pair (r, r+1) within a run,
an arrow from (v_r, rho_r*sigma_r) to (v_{r+1}, rho_{r+1}*sigma_{r+1}).  The value
of the LAST transition's endpoint uses value + drift (the observed() endpoint
convention); interior endpoints use the next record's raw value.  Rounds whose
agreement rho is unmeasurable (sigma collapsed to duplicates) sit at forecast
move 0.  No dots.  Colored arrows on top, gray model field underneath, SAME units
and SAME duration -- so each panel is a direct observed-vs-model vector-field
comparison.  Judge-swap-run transitions are dashed.

All coordinates are computed live from experiments/spread_util_unified.json; the
vertical field component is loaded live from experiments/field_vertical_component.json.
Palette + esc()/wrap() copied from docs/figures/src/make_figures.py (house style).
Regenerate with:  python3 field-observed-steps.py
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
# read data + build one arrow per consecutive round transition
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
# continuous-axis coupling instead -- slope loaded live from the analysis JSON
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

fam_run_ct = Counter()
fam_trans_ct = Counter()
swap_trans_ct = Counter()
fam_axes = defaultdict(set)
TRANS = []                                   # one arrow per consecutive round pair
for k, rows in RUNS.items():
    first = rows[0]
    assert first["round"] == 1, k
    fam = family_of(first)
    fam_run_ct[fam] += 1
    fam_axes[fam].add(first["axis"])
    swap = (first["judge"] == "schedule")    # scheduled judge swap: dash the run
    n = len(rows)
    for i in range(n - 1):
        a, b = rows[i], rows[i + 1]
        is_last = (i + 1 == n - 1)
        v1 = a["value"]
        y1 = rho_sigma(a)
        # last transition's endpoint uses observed() convention (value + drift);
        # interior endpoints use the next record's raw value
        v2 = b["value"] + (b["drift"] if is_last else 0.0)
        y2 = rho_sigma(b)
        TRANS.append({"fam": fam, "swap": swap,
                      "v1": v1, "y1": y1, "v2": v2, "y2": y2})
        fam_trans_ct[fam] += 1
        if swap:
            swap_trans_ct[fam] += 1

assert dict(fam_run_ct) == FAM_EXPECT, dict(fam_run_ct)
# every consecutive round pair in the file is drawn exactly once
N_TRANS = len(TRANS)
assert N_TRANS == D["n_records"] - D["n_runs"] == 266, N_TRANS
assert sum(fam_trans_ct.values()) == N_TRANS, dict(fam_trans_ct)
# swaps are entirely inside the OLMo risk grid / schedules family
assert set(swap_trans_ct) == {"OLMo risk grid + judge schedules"}, dict(swap_trans_ct)

# which families are pure risk-axis (so the bent field is licensed)
PURE_RISK = {fam for fam, axes in fam_axes.items() if axes == {"risk"}}
assert BENT_FAMS == PURE_RISK, (BENT_FAMS, PURE_RISK)

# value + forecast-move ranges actually present (assert, don't transcribe)
_allx = [t["v1"] for t in TRANS] + [t["v2"] for t in TRANS]
_ally = [t["y1"] for t in TRANS] + [t["y2"] for t in TRANS]
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

# observed-arrow style (thin one-round moves, no dots); the busiest panel
# (OLMo risk grid, 107 transitions) stays legible at these weights
OBS_W = 1.6
OBS_OP = 0.8


def env(v):
    return math.sqrt(max(0.0, v * (1.0 - v)))


def PX(v, ox):
    return ox + v * PW


def PYc(y, top):
    return (top + PH) - (y - Y_MIN) / (Y_MAX - Y_MIN) * PH


# ---- markers: small (5px) observed arrowheads per family color + field ----
DEFS = ['<defs>']
for i, c in enumerate(COLORS):
    DEFS.append(
        f'<marker id="obs{i}" viewBox="0 0 10 10" refX="7.5" refY="5" '
        f'markerWidth="5" markerHeight="5" orient="auto-start-reverse">'
        f'<path d="M 0 0 L 10 5 L 0 10 z" fill="{c}"/></marker>')
DEFS.append(
    f'<marker id="afield" viewBox="0 0 10 10" refX="8" refY="5" '
    f'markerWidth="5" markerHeight="5" orient="auto-start-reverse">'
    f'<path d="M 0 1.5 L 10 5 L 0 8.5 z" fill="{FIELD}"/></marker>')
DEFS.append('</defs>')

S = ["\n".join(DEFS)]

# ---- headline + orientation ----------------------------------------------
S.append(txt(LM, 46,
             "Every observed one-round move in the (value, forecast-move) plane",
             25, INK, "bold"))
S.append(txt(LM, 80,
             "Colored arrows are the measured round-to-round moves; the gray "
             "field is the model's predicted move from each coordinate — both "
             "are one round long.", 16, GRAY))
S.append(txt(LM, 104,
             "Candidate M: observed and predicted arrows are the same object "
             "(one round, same units), so each panel is a direct observed-vs-"
             "model vector-field comparison. One arrow per consecutive round "
             "pair; judge-swap runs dashed.", 16, GRAY))


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


def draw_panel(fam, col, row):
    ox = LM + col * CELL_W + YLAB_W
    top = TOP + row * CELL_H + TITLE_H
    bot = top + PH
    color = FAM_COLOR[fam]
    ci = COLORS.index(color)
    bent = fam in BENT_FAMS
    out = []

    # panel title (family name + transition count + run count)
    nt = fam_trans_ct[fam]
    nr = fam_run_ct[fam]
    title = f"{fam} — {nt} round transitions from {nr} runs"
    out.append(txt(ox, top - 14, title, 15, INK, "bold"))

    # faint horizontal gridlines
    for gy in (-0.3, -0.2, -0.1, 0.1, 0.2, 0.3, 0.4):
        out.append(line(ox, PYc(gy, top), ox + PW, PYc(gy, top), FAINT, 1.0))
    # y ticks / labels (thinned: -0.3, 0, +0.3)
    for gy in (-0.3, 0.0, 0.3):
        out.append(txt(ox - 10, PYc(gy, top) + 5,
                       f"{gy:+.1f}".replace("+0.0", "0"),
                       13, GRAY, anchor="end"))

    # background model field (drawn first, underneath the observed arrows)
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

    # this family's observed round transitions (colored, on top of the field;
    # dashed judge-swap transitions drawn first so solid moves read on top)
    fam_trans = [t for t in TRANS if t["fam"] == fam]
    order = sorted(range(len(fam_trans)),
                   key=lambda i: (not fam_trans[i]["swap"]))
    for i in order:
        t = fam_trans[i]
        x1p, y1p = PX(t["v1"], ox), PYc(t["y1"], top)
        x2p, y2p = PX(t["v2"], ox), PYc(t["y2"], top)
        dash = ' stroke-dasharray="4 3"' if t["swap"] else ""
        out.append(f'<line x1="{x1p:.2f}" y1="{y1p:.2f}" x2="{x2p:.2f}" '
                   f'y2="{y2p:.2f}" stroke="{color}" stroke-width="{OBS_W}" '
                   f'stroke-opacity="{OBS_OP}"{dash} '
                   f'marker-end="url(#obs{ci})"/>')

    # flat-field note inside self-description panels (top-left corner is clear)
    if not bent:
        for j, ln in enumerate(wrap(EMP_NOTE, 34)):
            out.append(txt(ox + 10, top + 22 + j * 17, ln, 13, GRAY))

    # panel axis labels (compact; full recipe lives in the caption)
    out.append(txt(ox + PW / 2, bot + 48,
                   "behavioral value v  (0 → 1)", 14, INK, anchor="middle"))
    ymid = (top + bot) / 2
    out.append(f'<text x="{ox - 44:.1f}" y="{ymid:.1f}" font-family="{FONT}" '
               f'font-size="14" fill="{INK}" text-anchor="middle" '
               f'transform="rotate(-90 {ox - 44:.1f} {ymid:.1f})">forecast '
               f'move ρ·σ</text>')
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
# glyph: one observed round transition (solid, small head)
S.append(f'<line x1="{kox + 1}" y1="{ly - 5}" x2="{kox + 46}" y2="{ly - 5}" '
         f'stroke="{INK}" stroke-width="{OBS_W}" '
         f'marker-end="url(#obs0)"/>')
S.append(txt(kox + 58, ly, "one observed round transition r → r+1", 14, INK))
ly += 20
S.append(txt(kox + 58, ly, "in the family color (no dots)", 13.5, GRAY))
# glyph: judge-swap-run transition
ly += 28
S.append(f'<line x1="{kox + 1}" y1="{ly - 5}" x2="{kox + 46}" y2="{ly - 5}" '
         f'stroke="{GREEN}" stroke-width="{OBS_W}" stroke-dasharray="4 3" '
         f'marker-end="url(#obs1)"/>')
S.append(txt(kox + 58, ly, "judge-swap-run transition (dashed)", 14, INK))
# glyph: model field
ly += 28
S.append(f'<line x1="{kox + 1}" y1="{ly - 5}" x2="{kox + 46}" y2="{ly - 5}" '
         f'stroke="{FIELD}" stroke-width="1.4" marker-end="url(#afield)"/>')
S.append(txt(kox + 58, ly, "gray field = model's predicted one-round", 14, INK))
ly += 20
S.append(txt(kox + 58, ly, "move Δ value = ρ·σ from each coordinate", 13.5, GRAY))

# field notes
notes = [
    "observed and model arrows are the SAME object: "
    "one round long, in the same units",
    "risk panels: field bends toward the walls — spread tracks the "
    "binary envelope √(v(1−v))",
    "self-description panels: field bends by the measured coupling "
    f"Δ(ρ·σ) ≈ −{abs(EMP_SLOPE):.2f}·Δv",
    "ρ unmeasurable (σ → 0)  →  move plotted at 0",
]
ly += 30
for note in notes:
    for j, wln in enumerate(wrap(note, 48)):
        S.append(txt(kox, ly, wln, 13.5, GRAY))
        ly += 20
    ly += 4

# family colour legend
ly += 4
S.append(txt(kox, ly, "Family colors", 14, INK, "bold"))
ly += 24
for fam, color in FAMS:
    ci = COLORS.index(color)
    S.append(f'<line x1="{kox + 1}" y1="{ly - 5}" x2="{kox + 38}" y2="{ly - 5}" '
             f'stroke="{color}" stroke-width="2.2" marker-end="url(#obs{ci})"/>')
    S.append(txt(kox + 50, ly, fam, 13.5, INK))
    ly += 24

# ---- no in-figure footnote: provenance lives in caption.md ----------------

svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
       f'font-family="{FONT}">\n'
       f'<rect width="{W}" height="{H}" fill="white"/>\n'
       + "\n".join(S) + "\n</svg>")

out = os.path.join(HERE, "field-observed-steps.svg")
with open(out, "w") as f:
    f.write(svg)
print(f"wrote {out}  viewBox 0 0 {W} {H}  ({N_TRANS} round transitions; "
      f"per family {dict(fam_trans_ct)}; swaps {dict(swap_trans_ct)}; "
      f"bent panels {sorted(BENT_FAMS)})")
