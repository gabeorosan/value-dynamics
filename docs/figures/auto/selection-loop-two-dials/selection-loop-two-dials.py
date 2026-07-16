#!/usr/bin/env python3
"""synthesis — the selection loop as a graphical abstract.

Top row: one round of the loop — a model writes answers -> a judge scores
them -> it keeps the ones it scores highest -> train -> repeat. The last
stage separates the three distances the loop actually moves through:

  - selector gap        = kept mean - whole offered pool mean   (the judge's act)
  - pool-supply shift    = whole offered pool mean - own mean     (an outside supplier)
  - training displacement = kept mean - the model's own generated-pool mean
                          = selector gap + pool-supply shift      (the actual update)

In a self-only pool the whole offered pool mean equals the model's own mean, so
the pool-supply shift is zero and the training displacement equals the selector
gap. In a mixed pool an outside supplier moves the offered pool away from the
model's own candidates, so the two differ.

Bottom row: four panels that introduce the two dials of the selector gap and
how each behaves over a run — (A) the gap decomposes into spread x agreement,
(B) spread is spent so the gap shrinks with it, (C) agreement is set mainly by
the judge setup with only slow within-run drift, (D) an outside source refills
spread so the gap returns.

The unit-form forecast is `selector gap ~= agreement x spread` with no fitted
coefficient. (The old order-statistic constant near 0.95 was published on the
wrong scale and has been retracted; it is deliberately not shown here.)

Numbers are read at build time and asserted against:
  experiments/spread_util_unified.json         (spread x agreement factorization)
  experiments/selection_response_predictor.json (unit-form selector-gap proxy)

Regenerate with:  python3 selection-loop-two-dials.py   (stdlib only)
"""
import os
import json

# ---- palette (hexes match docs/figures/src/make_figures.py) --------------
INK = "#1a1a1a"
BLUE = "#2867b5"       # value spread / the model's own generated pool
GREEN = "#3a7d44"      # the selector gap
RED = "#b5342c"        # reserved: reversal / warning emphasis
GRAY = "#6b7684"       # recessive only (axes, whole offered pool, muted text)
AMBER = "#9a6b15"      # the judge's agreement / an outside supplier
FAINT = "#d8dde3"
POOL_FILL = "#f4f7fb"
SRC_FILL = "#fbf4ea"
FONT = "Helvetica, Arial, sans-serif"


# ---- data (read the files; assert, never hardcode silently) --------------
HERE = os.path.dirname(os.path.abspath(__file__))
EXP = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", "experiments"))

with open(os.path.join(EXP, "spread_util_unified.json")) as _f:
    _SU = json.load(_f)
with open(os.path.join(EXP, "selection_response_predictor.json")) as _f:
    _SR = json.load(_f)

_fact = _SU["factorization"]["pooled"]["gap_vs_rho_sigma"]
assert _fact["n"] == 290, _fact["n"]
R_FACT = _fact["r"]                       # 0.901 : agreement x spread vs selector gap

_proxy = _SR["selector_gap"]["unit_agreement_spread_proxy"]["all"]
assert _proxy["n"] == 290, _proxy["n"]
R2_GAP = _proxy["r2"]                     # 0.81037
MAE_GAP = _proxy["mae"]                   # 0.042074
N_ROUNDS = _proxy["n"]

# Guard: the retracted order-statistic constant must never reach the canvas.
_slope = _SU["factorization"]["pooled"]["gap_vs_rho_sigma"]["slope"]
assert abs(_slope - 0.958) < 0.01, _slope   # confirm which number we are suppressing


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def wrap(text, width):
    words, lines, cur = text.split(), [], ""
    for w in words:
        if len(cur) + len(w) + 1 > width and cur:
            lines.append(cur); cur = w
        else:
            cur = f"{cur} {w}".strip()
    if cur:
        lines.append(cur)
    return lines


def ctext(x, y, s, size, color=INK, weight="normal"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="middle" '
            f'font-family="{FONT}" font-size="{size}" font-weight="{weight}" '
            f'fill="{color}">{esc(s)}</text>')


def ltext(x, y, s, size, color=INK, weight="normal", anchor="start"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" '
            f'font-family="{FONT}" font-size="{size}" font-weight="{weight}" '
            f'fill="{color}">{esc(s)}</text>')


def clines(cx, y, s, size, width, color=INK, weight="normal", lh=1.3):
    lines = wrap(s, width)
    return "\n".join(ctext(cx, y + i * size * lh, ln, size, color, weight)
                     for i, ln in enumerate(lines))


def box(x, y, w, h, fill, stroke=INK, sw=2.5, rx=14):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" '
            f'rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')


def robot(x, y, color, scale=1.0):
    u = scale
    return "\n".join([
        f'<rect x="{x:.1f}" y="{y:.1f}" width="{56*u:.1f}" height="{44*u:.1f}" rx="{10*u:.1f}" fill="white" stroke="{color}" stroke-width="3"/>',
        f'<circle cx="{x+18*u:.1f}" cy="{y+21*u:.1f}" r="{4*u:.1f}" fill="{color}"/>',
        f'<circle cx="{x+38*u:.1f}" cy="{y+21*u:.1f}" r="{4*u:.1f}" fill="{color}"/>',
        f'<path d="M {x+16*u:.1f} {y+33*u:.1f} Q {x+28*u:.1f} {y+41*u:.1f} {x+40*u:.1f} {y+33*u:.1f}" stroke="{color}" stroke-width="3" fill="none"/>',
        f'<line x1="{x+28*u:.1f}" y1="{y:.1f}" x2="{x+28*u:.1f}" y2="{y-10*u:.1f}" stroke="{color}" stroke-width="3"/>',
        f'<circle cx="{x+28*u:.1f}" cy="{y-13*u:.1f}" r="{4*u:.1f}" fill="{color}"/>',
    ])


def axis(x0, x1, y, color=GRAY, sw=2.2, right=True, left=False):
    s = [f'<line x1="{x0:.1f}" y1="{y:.1f}" x2="{x1:.1f}" y2="{y:.1f}" stroke="{color}" stroke-width="{sw}"/>']
    if right:
        s.append(f'<path d="M {x1-9:.1f} {y-6:.1f} L {x1:.1f} {y:.1f} L {x1-9:.1f} {y+6:.1f}" fill="none" stroke="{color}" stroke-width="{sw}"/>')
    if left:
        s.append(f'<path d="M {x0+9:.1f} {y-6:.1f} L {x0:.1f} {y:.1f} L {x0+9:.1f} {y+6:.1f}" fill="none" stroke="{color}" stroke-width="{sw}"/>')
    return "\n".join(s)


def dot(cx, cy, r, fill, ring=False, ring_color=INK):
    s = ""
    if ring:
        s += f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r+5.5:.1f}" fill="none" stroke="{ring_color}" stroke-width="3"/>'
    s += f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}" stroke="white" stroke-width="1.6"/>'
    return s


def rarrow(x0, x1, y, color=INK, sw=3.2):
    return (f'<line x1="{x0:.1f}" y1="{y:.1f}" x2="{x1-8:.1f}" y2="{y:.1f}" stroke="{color}" stroke-width="{sw}"/>'
            f'<path d="M {x1-11:.1f} {y-7:.1f} L {x1:.1f} {y:.1f} L {x1-11:.1f} {y+7:.1f} z" fill="{color}"/>')


def larrow(x0, x1, y, color=INK, sw=3.2):
    return (f'<line x1="{x0:.1f}" y1="{y:.1f}" x2="{x1+8:.1f}" y2="{y:.1f}" stroke="{color}" stroke-width="{sw}"/>'
            f'<path d="M {x1+11:.1f} {y-7:.1f} L {x1:.1f} {y:.1f} L {x1+11:.1f} {y+7:.1f} z" fill="{color}"/>')


def vpos(x0, x1, v):
    return x0 + v * (x1 - x0)


def sparks(x0, x1, yb, yt, series, rounds=4, sw=3.4, dotr=5, base=True):
    """series = [(vals in [0,1], color)]; maps round index -> x, value -> y."""
    out = []
    if base:
        out.append(f'<line x1="{x0:.1f}" y1="{yb:.1f}" x2="{x1:.1f}" y2="{yb:.1f}" stroke="{FAINT}" stroke-width="2"/>')
    for vals, color in series:
        n = len(vals)
        pts = [(x0 + i * (x1 - x0) / (n - 1), yb - v * (yb - yt)) for i, v in enumerate(vals)]
        d = "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in pts)
        out.append(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round"/>')
        out.append(dot(pts[-1][0], pts[-1][1], dotr, color))
    return "\n".join(out)


def svg_doc(w, h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
            f'font-family="{FONT}">\n<rect width="{w}" height="{h}" fill="white"/>\n{body}\n</svg>')


# ---- layout -------------------------------------------------------------
W = 1480
MARGIN = 48
GAP = 40
NCOL = 4
COLW = (W - 2 * MARGIN - (NCOL - 1) * GAP) / NCOL


def colx(i):
    return MARGIN + i * (COLW + GAP)


b = []
b.append(ctext(W / 2, 50, "How selection moves a value in a self-training loop", 32, INK, "bold"))

# ==== TOP ROW: one round of the loop =====================================
LY, LH = 92, 318
POOL = [0.14, 0.30, 0.42, 0.55, 0.70, 0.88]
AVG = sum(POOL) / len(POOL)
KEPT = [4, 5]
KEPT_AVG = sum(POOL[i] for i in KEPT) / len(KEPT)

for i in range(NCOL):
    b.append(box(colx(i), LY, COLW, LH, POOL_FILL if i == 0 else "white", GRAY, 2, rx=14))
amid = LY + LH / 2
for i in range(NCOL - 1):
    b.append(rarrow(colx(i) + COLW + 6, colx(i + 1) - 6, amid, GRAY, 3.4))


def ax_bounds(i, pad=34):
    return colx(i) + pad, colx(i) + COLW - pad


# ---- Stage 1: model writes answers ----
cx = colx(0) + COLW / 2
b.append(ctext(cx, LY + 34, "A model writes several answers", 21, INK, "bold"))
b.append(robot(cx - 56 * 0.55 / 2, LY + 58, BLUE, 0.55))
x0, x1 = ax_bounds(0)
ay = LY + 150
b.append(axis(x0, x1, ay, GRAY, 2.2, right=True, left=True))
for v in POOL:
    b.append(dot(vpos(x0, x1, v), ay, 7, BLUE))
b.append(ltext(x0 - 2, ay + 26, "lower", 18, GRAY))
b.append(ltext(x1 + 2, ay + 26, "higher", 18, GRAY, anchor="end"))
b.append(ctext(cx, ay + 26, "the value", 18, GRAY))
sy = LY + 224
b.append(f'<rect x="{x0-6:.1f}" y="{sy-19:.1f}" width="{x1-x0+12:.1f}" height="36" rx="10" fill="{SRC_FILL}" stroke="{AMBER}" stroke-width="1.6" stroke-dasharray="5 4"/>')
for v in (0.30, 0.62):
    b.append(dot(vpos(x0, x1, v), sy - 1, 6.5, AMBER))
b.append(clines(cx, sy + 36, "an outside supplier can add answers too (a mixed pool)", 18, 32, AMBER))

# ---- Stage 2: a judge SCORES each answer ----
cx = colx(1) + COLW / 2
b.append(ctext(cx, LY + 34, "A judge scores each answer", 21, INK, "bold"))
b.append(robot(cx - 56 * 0.55 / 2, LY + 58, AMBER, 0.55))
x0, x1 = ax_bounds(1)
ay = LY + 196
b.append(axis(x0, x1, ay, GRAY, 2.2, right=True, left=False))
# each candidate: a bar whose height = the judge's score; scores rise with the
# value -> the judge's choices AGREE with the value axis.
for v in POOL:
    px = vpos(x0, x1, v)
    score = 0.22 + 0.72 * v          # positive agreement
    bh = 96 * score
    b.append(f'<line x1="{px:.1f}" y1="{ay:.1f}" x2="{px:.1f}" y2="{ay-bh:.1f}" stroke="{AMBER}" stroke-width="7" stroke-linecap="round"/>')
    b.append(dot(px, ay, 6, BLUE))
b.append(ltext(x0 - 2, ay + 24, "lower", 18, GRAY))
b.append(ltext(x1 + 2, ay + 24, "higher", 18, GRAY, anchor="end"))
b.append(clines(cx, ay + 42, "its scores rise with the value — that lineup is the agreement", 18, 30, GRAY))

# ---- Stage 3: keep the ones it scores highest -> the selector gap ----
cx = colx(2) + COLW / 2
b.append(ctext(cx, LY + 34, "It keeps the ones it scores highest", 21, INK, "bold"))
x0, x1 = ax_bounds(2)
ay = LY + 120
b.append(axis(x0, x1, ay, GRAY, 2.2, right=False))
avgx = vpos(x0, x1, AVG)
b.append(f'<line x1="{avgx:.1f}" y1="{ay-20:.1f}" x2="{avgx:.1f}" y2="{ay+20:.1f}" stroke="{GRAY}" stroke-width="2" stroke-dasharray="4 3"/>')
b.append(ctext(avgx, ay - 28, "whole offered pool mean", 18, GRAY))
for i, v in enumerate(POOL):
    b.append(dot(vpos(x0, x1, v), ay, 7, BLUE, ring=(i in KEPT), ring_color=INK))
gy = ay + 56
keptx = vpos(x0, x1, KEPT_AVG)
b.append(rarrow(avgx, keptx, gy, GREEN, 3.4))
b.append(ctext((avgx + keptx) / 2, gy + 26, "selector gap", 18, GREEN, "bold"))
b.append(clines(cx, gy + 52, "the kept answers' mean minus the whole offered pool mean", 18, 34, GRAY))

# ---- Stage 4: train -> the training displacement (the actual update) ----
cx = colx(3) + COLW / 2
b.append(ctext(cx, LY + 34, "Train toward the kept answers", 21, INK, "bold"))
x0, x1 = ax_bounds(3)
ay = LY + 128
b.append(axis(x0, x1, ay, GRAY, 2.2, right=True, left=True))
vq, vp, vk = 0.30, 0.45, 0.72
qx, px_, kx = (vpos(x0, x1, v) for v in (vq, vp, vk))
b.append(dot(qx, ay, 7, BLUE))
b.append(dot(px_, ay, 7, GRAY))
b.append(dot(kx, ay, 7, GREEN))
# staggered labels with faint leaders (middle raised so neighbours never touch)
for xx, lab, col, dy in ((qx, "own mean", BLUE, -28),
                         (px_, "whole pool", GRAY, -50),
                         (kx, "kept mean", GREEN, -28)):
    b.append(f'<line x1="{xx:.1f}" y1="{ay-8:.1f}" x2="{xx:.1f}" y2="{ay+dy+8:.1f}" stroke="{FAINT}" stroke-width="1.6"/>')
    b.append(ctext(xx, ay + dy, lab, 18, col, "bold"))
# faint vertical guides tie the axis marks to the arrow rows below
for xx in (qx, px_, kx):
    b.append(f'<line x1="{xx:.1f}" y1="{ay+8:.1f}" x2="{xx:.1f}" y2="{ay+86:.1f}" stroke="{FAINT}" stroke-width="1.4" stroke-dasharray="3 4"/>')
# Row A: pool-supply shift (own mean -> whole offered pool mean)
yA = ay + 30
b.append(rarrow(qx, px_, yA, AMBER, 3.2))
b.append(ltext(px_ + 12, yA + 5, "pool-supply shift", 18, AMBER, "bold"))
# Row B: selector gap (whole offered pool mean -> kept mean)
yB = ay + 58
b.append(rarrow(px_, kx, yB, GREEN, 3.2))
b.append(ctext((px_ + kx) / 2, yB + 21, "selector gap", 18, GREEN, "bold"))
# Row C: training displacement (own mean -> kept mean) = the update itself
yC = ay + 86
b.append(rarrow(qx, kx, yC, INK, 3.8))
b.append(ctext((qx + kx) / 2, yC + 23, "training displacement", 19, INK, "bold"))
b.append(clines(cx, yC + 47,
                "kept mean minus the model's own generated-pool mean",
                18, 28, GRAY))

# ---- loop-back arrow ----
y_back = LY + LH + 34
x4c = colx(3) + COLW / 2
x1c = colx(0) + COLW / 2
d = (f"M {x4c:.1f} {LY+LH} L {x4c:.1f} {y_back-8:.1f} Q {x4c:.1f} {y_back:.1f} {x4c-10:.1f} {y_back:.1f} "
     f"L {x1c+10:.1f} {y_back:.1f} Q {x1c:.1f} {y_back:.1f} {x1c:.1f} {y_back-8:.1f} L {x1c:.1f} {LY+LH+3:.1f}")
b.append(f'<path d="{d}" fill="none" stroke="{GRAY}" stroke-width="3"/>')
b.append(f'<path d="M {x1c-7:.1f} {LY+LH+8:.1f} L {x1c:.1f} {LY+LH-2:.1f} L {x1c+7:.1f} {LY+LH+8:.1f} z" fill="{GRAY}"/>')
b.append(ctext(W / 2, y_back + 24,
               "self-only pool: own mean = whole pool mean, so training displacement = selector gap  ·  repeat about 4 rounds",
               18, GRAY))

# ==== BOTTOM ROW: the two dials of the selector gap, over a run ==========
BH_Y = y_back + 60
b.append(ctext(W / 2, BH_Y,
               "The size of that selector gap is set by two dials — and here is how each behaves over a run:",
               22, INK, "bold"))

PT = BH_Y + 26          # panels top
PHT = 322               # panel height


def panel(i, title, tcolor=INK):
    x = colx(i)
    b.append(box(x, PT, COLW, PHT, "white", GRAY, 2, rx=14))
    b.append(clines(x + COLW / 2, PT + 30, title, 20, 30, tcolor, "bold"))
    return x


def legend_row(x, y, items):
    """items = [(color,label)] laid out left→right."""
    cxp = x
    for color, label in items:
        b.append(f'<line x1="{cxp:.1f}" y1="{y:.1f}" x2="{cxp+22:.1f}" y2="{y:.1f}" stroke="{color}" stroke-width="3.4" stroke-linecap="round"/>')
        b.append(ltext(cxp + 28, y + 5, label, 18, INK))
        cxp += 42 + len(label) * 9.6


def rounds_label(x0, x1, yb):
    b.append(ltext(x0, yb + 22, "round 1", 18, GRAY))
    b.append(ltext(x1, yb + 22, "4", 18, GRAY, anchor="end"))


# -- Panel A: the decomposition --
x = panel(0, "selector gap = value spread × agreement", INK)
cx = x + COLW / 2
yeq = PT + 108
b.append(f'<text x="{cx:.1f}" y="{yeq:.1f}" text-anchor="middle" font-family="{FONT}" font-size="20" font-weight="bold">'
         f'<tspan fill="{GREEN}">selector gap</tspan></text>')
b.append(f'<text x="{cx:.1f}" y="{yeq+34:.1f}" text-anchor="middle" font-family="{FONT}" font-size="20" font-weight="bold">'
         f'<tspan fill="{GRAY}">= </tspan><tspan fill="{BLUE}">value spread</tspan>'
         f'<tspan fill="{GRAY}"> × </tspan><tspan fill="{AMBER}">agreement</tspan></text>')
b.append(clines(cx, yeq + 72,
                "how varied the answers are, times how well the judge sorts them along the value",
                18, 30, GRAY))
b.append(clines(cx, PT + PHT - 66,
                "simple forecast: selector gap ≈ agreement × spread, no fitted coefficient",
                18, 30, INK, "bold"))

# -- Panel B: spread is spent; the gap shrinks with it --
x = panel(1, "Spread falls — the selector gap shrinks", BLUE)
x0, x1 = x + 40, x + COLW - 40
yb, yt = PT + 214, PT + 96
b.append(sparks(x0, x1, yb, yt, [([0.92, 0.74, 0.62, 0.54], BLUE),
                                 ([0.78, 0.60, 0.49, 0.42], GREEN)]))
rounds_label(x0, x1, yb)
legend_row(x + 28, PT + 78, [(BLUE, "spread"), (GREEN, "selector gap")])
b.append(clines(x + COLW / 2, PT + PHT - 52, "same judge, a homogenizing pool → a shrinking selector gap", 18, 32, GRAY))

# -- Panel C: agreement is set mainly by the judge setup (slow residual drift) --
x = panel(2, "Agreement is set mainly by the judge setup", AMBER)
x0, x1 = x + 40, x + COLW - 40
yb, yt = PT + 214, PT + 96
b.append(sparks(x0, x1, yb, yt, [([0.70, 0.72, 0.71, 0.67], AMBER),
                                 ([0.30, 0.32, 0.29, 0.31], GRAY)]))
rounds_label(x0, x1, yb)
legend_row(x + 28, PT + 78, [(AMBER, "judge A"), (GRAY, "judge B")])
b.append(clines(x + COLW / 2, PT + PHT - 52, "set by the judge, format, and pool; only slow within-run drift", 18, 30, GRAY))

# -- Panel D: an outside source refills spread; the gap returns --
x = panel(3, "Fresh answers refill spread — the selector gap returns", GREEN)
x0, x1 = x + 40, x + COLW - 40
yb, yt = PT + 214, PT + 96
b.append(sparks(x0, x1, yb, yt, [([0.90, 0.55, 0.86, 0.80], BLUE),
                                 ([0.76, 0.44, 0.72, 0.66], GREEN)]))
# mark the refill round (label sits low, clear of the legend at the top)
xr = x0 + 2 * (x1 - x0) / 3
b.append(f'<line x1="{xr:.1f}" y1="{PT+114:.1f}" x2="{xr:.1f}" y2="{PT+186:.1f}" stroke="{AMBER}" stroke-width="1.6" stroke-dasharray="4 4"/>')
b.append(ctext(xr, PT + 202, "fresh answers added", 18, AMBER))
rounds_label(x0, x1, yb)
legend_row(x + 28, PT + 78, [(BLUE, "spread"), (GREEN, "selector gap")])
b.append(clines(x + COLW / 2, PT + PHT - 52, "restore the spread and the movement comes back", 18, 34, GRAY))

# ==== READOUT STRIP: the numbers, read from the result files =============
STRIP_Y = PT + PHT + 40
readout = (f"Unit-form forecast, no fitted coefficient: selector gap ≈ agreement × spread "
           f"fits the {N_ROUNDS} agreement-scored rounds at R² {R2_GAP:.3f}, "
           f"mean absolute error {MAE_GAP:.3f} in value units; "
           f"agreement × spread tracks the selector gap at r = {R_FACT:.2f}.")
b.append(clines(W / 2, STRIP_Y, readout, 18, 150, INK))
b.append(ctext(W / 2, STRIP_Y + 52,
               "Source: experiments/spread_util_unified.json (factorization) · "
               "experiments/selection_response_predictor.json (unit-form proxy)",
               16, GRAY))

H = STRIP_Y + 78
out = os.path.join(HERE, "selection-loop-two-dials.svg")
with open(out, "w") as f:
    f.write(svg_doc(W, H, "\n".join(b)))
print("wrote", out, "H=", H)
