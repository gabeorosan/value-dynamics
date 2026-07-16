#!/usr/bin/env python3
"""Two-dials evidence figure for the value-dynamics selection-response model.

Owain Evans-lab house style (white background, one headline sentence, real data
with fat labels). Palette copied verbatim from docs/figures/src/make_figures.py.
Stdlib only; run from this directory:

    python3 selection-response-model.py

This figure is the *compact evidence* member of a three-figure split: the loop
mechanics (number line) and the endpoint recurrence live in separate figures.
Here we show only the two dials that go into the forecast and the scatter that
proves they predict the selector gap with no fitted coefficient.

Reads:
  experiments/selection_response_predictor.json  (aggregates + scale audit)
  experiments/spread_util_unified.json           (290 per-round records)
Every plotted aggregate is asserted against those JSONs below.
"""
import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
# auto/<slug>/ -> figures -> docs -> repo root
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
PRED = os.path.join(ROOT, "experiments", "selection_response_predictor.json")
RECS = os.path.join(ROOT, "experiments", "spread_util_unified.json")

# ---- palette (verbatim from make_figures.py) -----------------------------
INK = "#1a1a1a"
BLUE = "#2867b5"       # accent / self-judge series
GREEN = "#3a7d44"      # accent / frozen-judge series
RED = "#b5342c"        # emphasis for reversal / warning text
GRAY = "#6b7684"       # recessive only (axes, muted captions)
USER_FILL = "#cfe0f1"
ASST_FILL = "#eaf1f8"
DOC_FILL = "#fdf6e8"
KEY_FILL = "#eef5ee"
FONT = "Helvetica, Arial, sans-serif"


# ---- helpers (esc/wrap copied from make_figures.py) ----------------------
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


def T(x, y, s, size, color=INK, anchor="start", weight="normal", italic=False):
    st = f' font-style="italic"' if italic else ""
    return (f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" '
            f'fill="{color}" text-anchor="{anchor}" font-weight="{weight}"{st}>'
            f'{esc(s)}</text>')


def para(x, y, text, size, width, color=INK, lh=1.34, anchor="start",
         weight="normal"):
    out = []
    for i, ln in enumerate(wrap(text, width)):
        out.append(T(x, y + i * size * lh, ln, size, color, anchor, weight))
    return "\n".join(out), y + len(wrap(text, width)) * size * lh


def box(x, y, w, h, fill, stroke=INK, sw=2.5, rx=10):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')


def dot(cx, cy, r, fill, stroke=None, sw=1.0, opacity=1.0):
    st = f' stroke="{stroke}" stroke-width="{sw}"' if stroke else ""
    return (f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r}" fill="{fill}" '
            f'fill-opacity="{opacity}"{st}/>')


DEFS = f'''<defs>
<marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6"
 markerHeight="6" orient="auto-start-reverse">
 <path d="M 0 0 L 10 5 L 0 10 z" fill="{INK}"/></marker>
<marker id="arrB" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6"
 markerHeight="6" orient="auto-start-reverse">
 <path d="M 0 0 L 10 5 L 0 10 z" fill="{BLUE}"/></marker>
</defs>'''


def svg_doc(w, h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
            f'font-family="{FONT}">\n<rect width="{w}" height="{h}" fill="white"/>\n'
            f'{DEFS}\n{body}\n</svg>')


# ==========================================================================
# Load + verify data
# ==========================================================================
def approx(a, b, tol=5e-4):
    return abs(a - b) <= tol


pred = json.load(open(PRED))
recs_all = json.load(open(RECS))["records"]
scored = [r for r in recs_all if r.get("rho") is not None]

# scatter data: x = rho * spread, y = observed selector gap
XY = [(r["rho"] * r["spread"], r["gap"]) for r in scored]
N = len(XY)

# recompute the headline scatter aggregates from the records
xs = [x for x, _ in XY]
ys = [y for _, y in XY]
unit_mae = sum(abs(y - x) for x, y in XY) / N
ybar = sum(ys) / N
ssres = sum((y - x) ** 2 for x, y in XY)
sstot = sum((y - ybar) ** 2 for y in ys)
unit_r2 = 1 - ssres / sstot

# aggregates as stored in the predictor JSON
gap_unit = pred["selector_gap"]["unit_agreement_spread_proxy"]["all"]
oneround = pred["one_round_before_selection"]
onr_unit = oneround["unit_agreement_spread_proxy"]["all"]["mae"]
onr_kept = oneround["observed_kept_mean_LOCO"]["mae"]
scale = pred["scale_audit"]

# --- assertions: file is source of truth ---------------------------------
assert N == 290, N
assert gap_unit["n"] == 290
assert approx(gap_unit["r2"], 0.81037) and approx(unit_r2, 0.81037), unit_r2
assert approx(gap_unit["mae"], 0.042074) and approx(unit_mae, 0.042074), unit_mae
assert approx(onr_unit, 0.090184)
assert approx(onr_kept, 0.085447)
assert approx(scale["intensity_in_units_of_underlying_normal_sd"], 0.954481)


# ==========================================================================
# Build figure
# ==========================================================================
W = 1200
b = []

# ---- header --------------------------------------------------------------
b.append(T(W / 2, 50, "Spread, agreement, and the selector gap they forecast",
           30, INK, "middle", "bold"))
b.append(T(W / 2, 84, "290 agreement-scored rounds, all judges, formats, and pools; leave-one-condition-out",
           18, GRAY, "middle"))

# ==========================================================================
# TWO DIALS — pictorial strip (marks, not sentences)
# ==========================================================================
DTOP = 112
DH = 236
lx, rx = 60, 620
DW = 520

b.append(box(lx, DTOP, DW, DH, "white", GRAY, 2))
b.append(box(rx, DTOP, DW, DH, "white", GRAY, 2))

# ---- Dial 1: spread sigma ------------------------------------------------
b.append(T(lx + 22, DTOP + 34, "Dial 1   spread σ", 21, BLUE, "start", "bold"))
b.append(T(lx + 22, DTOP + 58, "σ = SD of the candidates' value scores, within one prompt's pool",
           14.5, INK))

# value axis geometry inside the panel
ax0, axw = lx + 70, DW - 130


def vx(v):
    return ax0 + axw * v


def value_axis(cy, dots, kept=None, show_bracket=False, bcolor=BLUE):
    """Draw a 0..1 value axis at height cy with candidate dots.
    kept: set of indices drawn as filled/ringed keeps (others hollow)."""
    out = [f'<line x1="{ax0}" y1="{cy}" x2="{ax0+axw}" y2="{cy}" '
           f'stroke="{GRAY}" stroke-width="1.4"/>']
    for t in (0.0, 0.5, 1.0):
        out.append(f'<line x1="{vx(t)}" y1="{cy-4}" x2="{vx(t)}" y2="{cy+4}" '
                   f'stroke="{GRAY}" stroke-width="1.4"/>')
    for i, v in enumerate(dots):
        if kept is not None:
            if i in kept:
                out.append(dot(vx(v), cy, 7.5, BLUE, "white", 1.5))
            else:
                out.append(dot(vx(v), cy, 5.5, "white", GRAY, 1.6))
        else:
            out.append(dot(vx(v), cy, 6.0, INK, "white", 1.2))
    if show_bracket:
        lo, hi = vx(min(dots)), vx(max(dots))
        by = cy + 20
        out.append(f'<path d="M {lo} {by-6} L {lo} {by} L {hi} {by} L {hi} {by-6}" '
                   f'fill="none" stroke="{bcolor}" stroke-width="2.2"/>')
    return "\n".join(out)


narrow = [0.42, 0.46, 0.49, 0.51, 0.55, 0.59]
wide = [0.14, 0.30, 0.44, 0.56, 0.71, 0.87]

yA, yB = DTOP + 108, DTOP + 186
b.append(value_axis(yA, narrow, show_bracket=True))
b.append(T(vx(0.505), yA + 44, "narrow pool  →  small σ", 15, INK, "middle", "bold"))
b.append(value_axis(yB, wide, show_bracket=True))
b.append(T(vx(0.505), yB + 44, "wide pool  →  large σ", 15, INK, "middle", "bold"))
b.append(T(lx + 10, yA - 30, "value 0", 12.5, GRAY, "start"))
b.append(T(lx + DW - 10, yA - 30, "1", 12.5, GRAY, "end"))

# ---- Dial 2: agreement rho -----------------------------------------------
rax0, raxw = rx + 70, DW - 130


def rvx(v):
    return rax0 + raxw * v


b.append(T(rx + 22, DTOP + 34, "Dial 2   agreement ρ", 21, BLUE, "start", "bold"))
b.append(T(rx + 22, DTOP + 58, "ρ = correlation between value score and being kept  (−1 … +1)",
           14.5, INK))

# same wide pool; two judges keep different subsets. filled BLUE = kept.
def keep_axis(cy, kept):
    out = [f'<line x1="{rax0}" y1="{cy}" x2="{rax0+raxw}" y2="{cy}" '
           f'stroke="{GRAY}" stroke-width="1.4"/>']
    for t in (0.0, 0.5, 1.0):
        out.append(f'<line x1="{rvx(t)}" y1="{cy-4}" x2="{rvx(t)}" y2="{cy+4}" '
                   f'stroke="{GRAY}" stroke-width="1.4"/>')
    for i, v in enumerate(wide):
        if i in kept:
            out.append(dot(rvx(v), cy, 7.5, BLUE, "white", 1.5))
        else:
            out.append(dot(rvx(v), cy, 5.5, "white", GRAY, 1.6))
    return "\n".join(out)


# random keep (mixed high/low) -> rho ~ 0 ; low-side keep -> rho -> -1
b.append(keep_axis(yA, kept={1, 3, 5}))
b.append(T(rvx(0.505), yA + 44, "keeps at random  →  ρ ≈ 0", 15, INK, "middle", "bold"))
b.append(keep_axis(yB, kept={0, 1, 2}))
b.append(T(rvx(0.505), yB + 44, "keeps the low side  →  ρ → −1", 15, INK, "middle", "bold"))

# small kept/dropped key inside dial 2
kyx = rx + DW - 168
b.append(dot(kyx, DTOP + 32, 7.5, BLUE, "white", 1.5))
b.append(T(kyx + 14, DTOP + 37, "kept", 13.5, INK))
b.append(dot(kyx + 70, DTOP + 32, 5.5, "white", GRAY, 1.6))
b.append(T(kyx + 84, DTOP + 37, "dropped", 13.5, INK))

# ---- bridge line: the two dials multiply into the scatter's x-axis -------
bY = DTOP + DH + 40
b.append(T(W / 2, bY, "spread σ   ×   agreement ρ   =   forecast  ρσ   —  the horizontal axis below",
           19, INK, "middle", "bold"))
b.append(f'<path d="M {W/2} {bY+12} L {W/2} {bY+34}" stroke="{INK}" '
         f'stroke-width="3" marker-end="url(#arr)"/>')

# ==========================================================================
# THE EVIDENCE — scatter (centerpiece) + one small inset
# ==========================================================================
EY = bY + 66
# --- scatter: observed selector gap vs rho*sigma ---
px, py = 130, EY + 20
pw, ph = 620, 470
dlo, dhi = -0.55, 0.42


def SX(v):
    return px + pw * (v - dlo) / (dhi - dlo)


def SY(v):
    return py + ph * (dhi - v) / (dhi - dlo)


# frame
b.append(f'<rect x="{px}" y="{py}" width="{pw}" height="{ph}" fill="#fbfbf9" '
         f'stroke="{GRAY}" stroke-width="1.5"/>')
# gridlines + ticks
for v in (-0.4, -0.2, 0.0, 0.2, 0.4):
    gx, gy = SX(v), SY(v)
    b.append(f'<line x1="{gx}" y1="{py}" x2="{gx}" y2="{py+ph}" stroke="#e9e9e4" stroke-width="1"/>')
    b.append(f'<line x1="{px}" y1="{gy}" x2="{px+pw}" y2="{gy}" stroke="#e9e9e4" stroke-width="1"/>')
    b.append(T(gx, py + ph + 24, f"{v:g}", 14.5, GRAY, "middle"))
    b.append(T(px - 10, gy + 5, f"{v:g}", 14.5, GRAY, "end"))
# zero axes bolder
b.append(f'<line x1="{SX(0)}" y1="{py}" x2="{SX(0)}" y2="{py+ph}" stroke="#cfcfc8" stroke-width="1.6"/>')
b.append(f'<line x1="{px}" y1="{SY(0)}" x2="{px+pw}" y2="{SY(0)}" stroke="#cfcfc8" stroke-width="1.6"/>')

# points
for x, y in XY:
    b.append(dot(SX(x), SY(y), 4.1, BLUE, BLUE, 0.6, 0.42))
# unit slope reference line (the headline)
b.append(f'<line x1="{SX(dlo)}" y1="{SY(dlo)}" x2="{SX(dhi)}" y2="{SY(dhi)}" '
         f'stroke="{INK}" stroke-width="3.2"/>')
b.append(T(SX(0.30) + 8, SY(0.30) - 10, "gap = ρσ", 18, INK, "start", "bold"))

# axis labels
b.append(T(px + pw / 2, py + ph + 54, "forecast  ρσ  =  agreement × offered spread",
           17, INK, "middle", "bold"))
b.append(f'<text x="{px-64}" y="{py+ph/2}" font-family="{FONT}" font-size="17" '
         f'fill="{INK}" font-weight="bold" text-anchor="middle" '
         f'transform="rotate(-90 {px-64} {py+ph/2})">observed selector gap  g  =  kept mean − pool mean</text>')

# headline readout box on the plot
b.append(box(px + 16, py + 16, 300, 82, "white", INK, 2))
b.append(T(px + 32, py + 44, "gap ≈ ρσ", 20, INK, "start", "bold"))
b.append(T(px + 32, py + 72, f"R² {gap_unit['r2']:.3f}  ·  mean abs error {gap_unit['mae']:.3f}",
           15, INK))

# --- one small inset: one round ahead -------------------------------------
icx, iw = 800, 340
iy = py + 40
ih = 210
b.append(box(icx, iy, iw, ih, DOC_FILL, INK, 2.5))
b.append(T(icx + 22, iy + 36, "Value forecast one round ahead", 19, INK, "start", "bold"))

# two-number comparison
r1 = iy + 84
b.append(T(icx + 22, r1, "before seeing the picks", 14, GRAY))
b.append(T(icx + 22, r1 + 28, f"value error {onr_unit:.4f}", 21, BLUE, "start", "bold"))
b.append(T(icx + iw - 22, r1 + 28, "using ρσ", 14.5, GRAY, "end"))
r2 = r1 + 58
b.append(T(icx + 22, r2, "after seeing which were kept", 14, GRAY))
b.append(T(icx + 22, r2 + 28, f"value error {onr_kept:.4f}", 21, INK, "start", "bold"))
b.append(T(icx + iw - 22, r2 + 28, "kept set", 14.5, GRAY, "end"))

HGT = py + ph + 70
svg = svg_doc(W, HGT, "\n".join(b))
out = os.path.join(HERE, "selection-response-model.svg")
with open(out, "w") as f:
    f.write(svg)
print("wrote", out, f"({W}x{HGT})")
print(f"scatter: N={N} unit R2={unit_r2:.5f} MAE={unit_mae:.5f}")
print(f"one-round: rho*sigma {onr_unit:.4f} vs kept-set {onr_kept:.4f}")
