#!/usr/bin/env python3
"""synthesis — the selection loop as a graphical abstract.

Top row: one round of the loop — a model writes 6 answers -> a judge scores
them -> it keeps the 2 it scores highest -> train -> repeat. (The judging
panel replaces the old "is there spread?" panel.)

Bottom row: four panels that introduce the two dials of the selection gap and
how each behaves over a run — (A) the gap decomposes into spread x agreement,
(B) spread is spent so the gap shrinks with it, (C) agreement is a mostly fixed
property of the judge, (D) an outside source refills spread so the gap returns.

Regenerate with:  python3 the_selection_loop_textfix.py   (stdlib only)
"""
import os

INK = "#1a1a1a"
BLUE = "#2867b5"       # value spread
GREEN = "#3a7d44"      # the selection gap
RED = "#b5342c"
GRAY = "#6b7684"
AMBER = "#c07d18"      # the judge's agreement
FAINT = "#d8dde3"
POOL_FILL = "#f4f7fb"
SRC_FILL = "#fbf4ea"
FONT = "Helvetica, Arial, sans-serif"


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
W = 1660
MARGIN = 48
GAP = 40
NCOL = 4
COLW = (W - 2 * MARGIN - (NCOL - 1) * GAP) / NCOL


def colx(i):
    return MARGIN + i * (COLW + GAP)


b = []
b.append(ctext(W / 2, 50, "How selection moves a value in a self-training loop", 32, INK, "bold"))

# ==== TOP ROW: one round of the loop =====================================
LY, LH = 92, 286
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
b.append(ctext(cx, LY + 34, "1   A model writes 6 answers", 21, INK, "bold"))
b.append(robot(cx - 56 * 0.55 / 2, LY + 58, BLUE, 0.55))
x0, x1 = ax_bounds(0)
ay = LY + 150
b.append(axis(x0, x1, ay, GRAY, 2.2, right=True, left=True))
for v in POOL:
    b.append(dot(vpos(x0, x1, v), ay, 7, BLUE))
b.append(ltext(x0 - 2, ay + 26, "lower", 16, GRAY))
b.append(ltext(x1 + 2, ay + 26, "higher", 16, GRAY, anchor="end"))
b.append(ctext(cx, ay + 26, "the value", 16, GRAY))
sy = LY + 224
b.append(f'<rect x="{x0-6:.1f}" y="{sy-19:.1f}" width="{x1-x0+12:.1f}" height="36" rx="10" fill="{SRC_FILL}" stroke="{AMBER}" stroke-width="1.6" stroke-dasharray="5 4"/>')
for v in (0.30, 0.62):
    b.append(dot(vpos(x0, x1, v), sy - 1, 6.5, AMBER))
b.append(ctext(cx, sy + 36, "another source can add answers too", 16, AMBER))

# ---- Stage 2: a judge SCORES each answer (the new judging panel) ----
cx = colx(1) + COLW / 2
b.append(ctext(cx, LY + 34, "2   A judge scores each answer", 21, INK, "bold"))
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
b.append(ltext(x0 - 2, ay + 24, "lower", 16, GRAY))
b.append(ltext(x1 + 2, ay + 24, "higher", 16, GRAY, anchor="end"))
b.append(clines(cx, ay + 48, "its scores rise with the value — how much they line up is the agreement", 15.5, 34, GRAY))

# ---- Stage 3: keep the two it scores highest ----
cx = colx(2) + COLW / 2
b.append(ctext(cx, LY + 34, "3   It keeps the 2 it scores highest", 21, INK, "bold"))
x0, x1 = ax_bounds(2)
ay = LY + 120
b.append(axis(x0, x1, ay, GRAY, 2.2, right=False))
avgx = vpos(x0, x1, AVG)
b.append(f'<line x1="{avgx:.1f}" y1="{ay-20:.1f}" x2="{avgx:.1f}" y2="{ay+20:.1f}" stroke="{GRAY}" stroke-width="2" stroke-dasharray="4 3"/>')
b.append(ctext(avgx, ay - 28, "pool average", 15, GRAY))
for i, v in enumerate(POOL):
    b.append(dot(vpos(x0, x1, v), ay, 7, BLUE, ring=(i in KEPT), ring_color=INK))
gy = ay + 56
keptx = vpos(x0, x1, KEPT_AVG)
b.append(rarrow(avgx, keptx, gy, GREEN, 3.4))
b.append(ctext((avgx + keptx) / 2, gy + 26, "selection gap", 17, GREEN, "bold"))
b.append(clines(cx, gy + 52, "the kept answers' average minus the pool average", 15.5, 34, GRAY))

# ---- Stage 4: train ----
cx = colx(3) + COLW / 2
b.append(ctext(cx, LY + 34, "4   Train on the kept answers", 21, INK, "bold"))
x0, x1 = ax_bounds(3)
ay = LY + 130
b.append(axis(x0, x1, ay, GRAY, 2.2, right=False))
oldx = vpos(x0, x1, AVG)
b.append(f'<line x1="{oldx:.1f}" y1="{ay-18:.1f}" x2="{oldx:.1f}" y2="{ay+18:.1f}" stroke="{GRAY}" stroke-width="2" stroke-dasharray="4 3"/>')
b.append(ctext(oldx, ay - 26, "this pool", 15, GRAY))
NEXT = [0.30, 0.42, 0.52, 0.63, 0.74, 0.90]
for v in NEXT:
    b.append(dot(vpos(x0, x1, v), ay, 7, BLUE))
nextx = vpos(x0, x1, sum(NEXT) / len(NEXT))
b.append(rarrow(oldx + 4, nextx, ay + 44, GREEN, 3.2))
b.append(clines(cx, ay + 72, "the next pool shifts the same way as the gap", 15.5, 30, INK, "bold"))

# ---- loop-back arrow ----
y_back = LY + LH + 34
x4c = colx(3) + COLW / 2
x1c = colx(0) + COLW / 2
d = (f"M {x4c:.1f} {LY+LH} L {x4c:.1f} {y_back-8:.1f} Q {x4c:.1f} {y_back:.1f} {x4c-10:.1f} {y_back:.1f} "
     f"L {x1c+10:.1f} {y_back:.1f} Q {x1c:.1f} {y_back:.1f} {x1c:.1f} {y_back-8:.1f} L {x1c:.1f} {LY+LH+3:.1f}")
b.append(f'<path d="{d}" fill="none" stroke="{GRAY}" stroke-width="3"/>')
b.append(f'<path d="M {x1c-7:.1f} {LY+LH+8:.1f} L {x1c:.1f} {LY+LH-2:.1f} L {x1c+7:.1f} {LY+LH+8:.1f} z" fill="{GRAY}"/>')
b.append(ctext(W / 2, y_back + 24, "repeat — about 4 rounds", 17, GRAY))

# ==== BOTTOM ROW: the two dials of the gap, over a run ====================
BH_Y = y_back + 60
b.append(ctext(W / 2, BH_Y,
               "The size of that gap is set by two dials — and here is how each behaves over a run:",
               22, INK, "bold"))

PT = BH_Y + 26          # panels top
PHT = 300               # panel height


def panel(i, title, tcolor=INK):
    x = colx(i)
    b.append(box(x, PT, COLW, PHT, "white", GRAY, 2, rx=14))
    b.append(clines(x + COLW / 2, PT + 30, title, 18, 30, tcolor, "bold"))
    return x


def legend_row(x, y, items):
    """items = [(color,label)] laid out left→right."""
    cxp = x
    for color, label in items:
        b.append(f'<line x1="{cxp:.1f}" y1="{y:.1f}" x2="{cxp+22:.1f}" y2="{y:.1f}" stroke="{color}" stroke-width="3.4" stroke-linecap="round"/>')
        b.append(ltext(cxp + 28, y + 5, label, 14, INK))
        cxp += 34 + len(label) * 8.2


def rounds_label(x0, x1, yb):
    b.append(ltext(x0, yb + 22, "round 1", 13.5, GRAY))
    b.append(ltext(x1, yb + 22, "4", 13.5, GRAY, anchor="end"))


# -- Panel A: the decomposition --
x = panel(0, "The gap = value spread × agreement", INK)
cx = x + COLW / 2
yeq = PT + 108
b.append(f'<text x="{cx:.1f}" y="{yeq:.1f}" text-anchor="middle" font-family="{FONT}" font-size="20" font-weight="bold">'
         f'<tspan fill="{GREEN}">selection gap</tspan></text>')
b.append(f'<text x="{cx:.1f}" y="{yeq+34:.1f}" text-anchor="middle" font-family="{FONT}" font-size="19" font-weight="bold">'
         f'<tspan fill="{GRAY}">= </tspan><tspan fill="{BLUE}">value spread</tspan>'
         f'<tspan fill="{GRAY}"> × </tspan><tspan fill="{AMBER}">agreement</tspan></text>')
b.append(clines(cx, yeq + 78, "how varied the six answers are, times how well the judge sorts them along the value", 15.5, 32, GRAY))
b.append(clines(cx, PT + PHT - 34, "both dials must be non-zero for the gap to move the value", 15, 34, INK))

# -- Panel B: spread is spent; the gap shrinks with it --
x = panel(1, "Spread is spent — the gap shrinks with it", BLUE)
x0, x1 = x + 40, x + COLW - 40
yb, yt = PT + 210, PT + 92
b.append(sparks(x0, x1, yb, yt, [([0.92, 0.74, 0.62, 0.54], BLUE),
                                 ([0.78, 0.60, 0.49, 0.42], GREEN)]))
rounds_label(x0, x1, yb)
legend_row(x + 30, PT + 74, [(BLUE, "spread"), (GREEN, "the gap")])
b.append(clines(x + COLW / 2, PT + PHT - 30, "same judge, a shrinking pool → a shrinking gap", 15, 32, GRAY))

# -- Panel C: agreement is a property of the judge --
x = panel(2, "Agreement barely moves — a property of the judge", AMBER)
x0, x1 = x + 40, x + COLW - 40
yb, yt = PT + 210, PT + 92
b.append(sparks(x0, x1, yb, yt, [([0.72, 0.72, 0.71, 0.72], AMBER),
                                 ([0.30, 0.31, 0.30, 0.30], GRAY)]))
rounds_label(x0, x1, yb)
legend_row(x + 30, PT + 74, [(AMBER, "judge A"), (GRAY, "judge B")])
b.append(clines(x + COLW / 2, PT + PHT - 30, "it changes only if you change the judge, format, or pool", 15, 34, GRAY))

# -- Panel D: an outside source refills spread; the gap returns --
x = panel(3, "An outside source refills spread — the gap returns", GREEN)
x0, x1 = x + 40, x + COLW - 40
yb, yt = PT + 210, PT + 92
b.append(sparks(x0, x1, yb, yt, [([0.90, 0.55, 0.86, 0.80], BLUE),
                                 ([0.76, 0.44, 0.72, 0.66], GREEN)]))
# mark the refill round (label sits low, clear of the legend at the top)
xr = x0 + 2 * (x1 - x0) / 3
b.append(f'<line x1="{xr:.1f}" y1="{PT+110:.1f}" x2="{xr:.1f}" y2="{PT+182:.1f}" stroke="{AMBER}" stroke-width="1.6" stroke-dasharray="4 4"/>')
b.append(ctext(xr, PT + 198, "fresh answers added", 13.5, AMBER))
rounds_label(x0, x1, yb)
legend_row(x + 30, PT + 74, [(BLUE, "spread"), (GREEN, "the gap")])
b.append(clines(x + COLW / 2, PT + PHT - 30, "restore the spread and the movement comes back", 15, 34, GRAY))

H = PT + PHT + 30
with open("selection-loop-two-dials.svg", "w") as f:
    f.write(svg_doc(W, H, "\n".join(b)))
print("wrote selection-loop-two-dials.svg", "H=", H)
