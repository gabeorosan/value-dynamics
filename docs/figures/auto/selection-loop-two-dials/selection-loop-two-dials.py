#!/usr/bin/env python3
"""synthesis — the selection loop, as a graphical abstract.

A closed left-to-right loop: a model makes a pool of answers -> is there
variation? -> which answers are kept? -> train -> back to the pool. Four small
outcome cards below show what the loop does with real numbers. Mostly visual.

Regenerate with:  python3 synthesis_the_selection_loop.py   (stdlib only)
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
FIGDIR = os.path.dirname(HERE) if os.path.basename(HERE) == "src" else HERE

INK = "#1a1a1a"
BLUE = "#2867b5"
GREEN = "#3a7d44"
RED = "#b5342c"
GRAY = "#6b7684"
AMBER = "#c07d18"
STRIP_FILL = "#eef2f6"
POOL_FILL = "#f4f7fb"
SRC_FILL = "#fbf4ea"
FONT = "Helvetica, Arial, sans-serif"
BODY = 19


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


def ctext(x, y, text, size, color=INK, weight="normal"):
    return (f'<text x="{x}" y="{y}" text-anchor="middle" font-family="{FONT}" '
            f'font-size="{size}" font-weight="{weight}" fill="{color}">{esc(text)}</text>')


def ltext(x, y, text, size, color=INK, weight="normal"):
    return (f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" '
            f'font-weight="{weight}" fill="{color}">{esc(text)}</text>')


def clines(cx, y, text, size, width, color=INK, weight="normal", lh=1.28):
    lines = wrap(text, width)
    out = [ctext(cx, y + i * size * lh, ln, size, color, weight) for i, ln in enumerate(lines)]
    return "\n".join(out), y + len(lines) * size * lh


def box(x, y, w, h, fill, stroke=INK, sw=2.5, rx=12):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')


def robot(x, y, color, scale=1.0):
    u = scale
    return "\n".join([
        f'<rect x="{x}" y="{y}" width="{56*u:.1f}" height="{44*u:.1f}" rx="{10*u:.1f}" fill="white" stroke="{color}" stroke-width="3"/>',
        f'<circle cx="{x+18*u:.1f}" cy="{y+21*u:.1f}" r="{4*u:.1f}" fill="{color}"/>',
        f'<circle cx="{x+38*u:.1f}" cy="{y+21*u:.1f}" r="{4*u:.1f}" fill="{color}"/>',
        f'<path d="M {x+16*u:.1f} {y+33*u:.1f} Q {x+28*u:.1f} {y+41*u:.1f} {x+40*u:.1f} {y+33*u:.1f}" stroke="{color}" stroke-width="3" fill="none"/>',
        f'<line x1="{x+28*u:.1f}" y1="{y}" x2="{x+28*u:.1f}" y2="{y-10*u:.1f}" stroke="{color}" stroke-width="3"/>',
        f'<circle cx="{x+28*u:.1f}" cy="{y-13*u:.1f}" r="{4*u:.1f}" fill="{color}"/>',
    ])


def svg_doc(w, h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
            f'font-family="{FONT}">\n<rect width="{w}" height="{h}" fill="white"/>\n{body}\n</svg>')


# ---- small drawing primitives -------------------------------------------
def vpos(x0, x1, v):
    return x0 + v * (x1 - x0)


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
    # arrow pointing left, from x0 (tail, right) to x1 (head, left)
    return (f'<line x1="{x0:.1f}" y1="{y:.1f}" x2="{x1+8:.1f}" y2="{y:.1f}" stroke="{color}" stroke-width="{sw}"/>'
            f'<path d="M {x1+11:.1f} {y-7:.1f} L {x1:.1f} {y:.1f} L {x1+11:.1f} {y+7:.1f} z" fill="{color}"/>')


# ---- layout -------------------------------------------------------------
W = 1660
MARGIN = 48
GAP = 40
NCOL = 4
COLW = (W - 2 * MARGIN - (NCOL - 1) * GAP) / NCOL


def colx(i):
    return MARGIN + i * (COLW + GAP)


b = []

# ---- title --------------------------------------------------------------
b.append(ctext(W / 2, 52, "How selection moves a value in a self-training loop", 32, INK, "bold"))

# ==== THE LOOP ===========================================================
LY = 96
LH = 300
POOL = [0.14, 0.30, 0.42, 0.55, 0.70, 0.88]
AVG = sum(POOL) / len(POOL)
KEPT = [0, 1]
KEPT_AVG = sum(POOL[i] for i in KEPT) / len(KEPT)

# loop boxes
for i in range(NCOL):
    b.append(box(colx(i), LY, COLW, LH, POOL_FILL if i == 0 else "white", GRAY, 2, rx=14))

# between-box arrows
amid = LY + LH / 2
for i in range(NCOL - 1):
    b.append(rarrow(colx(i) + COLW + 6, colx(i + 1) - 6, amid, GRAY, 3.4))


def ax_bounds(i, pad=30):
    return colx(i) + pad, colx(i) + COLW - pad


# ---- Stage 1: the generator makes a pool ----
cx = colx(0) + COLW / 2
b.append(ctext(cx, LY + 34, "1   A model makes a pool", 21, INK, "bold"))
b.append(ctext(cx, LY + 60, "six candidate answers", 18, GRAY))
b.append(robot(cx - 56 * 0.6 / 2, LY + 82, BLUE, 0.6))
x0, x1 = ax_bounds(0)
ay = LY + 168
b.append(axis(x0, x1, ay, GRAY, 2.2, right=True, left=True))
for v in POOL:
    b.append(dot(vpos(x0, x1, v), ay, 7, BLUE))
b.append(ltext(x0 - 2, ay + 26, "lower", 18, GRAY))
b.append(f'<text x="{x1+2:.1f}" y="{ay+26:.1f}" text-anchor="end" font-family="{FONT}" font-size="18" fill="{GRAY}">higher</text>')
b.append(ctext(cx, ay + 26, "the value", 18, GRAY))
# second source stream
sy = LY + 242
b.append(f'<rect x="{x0-6:.1f}" y="{sy-20:.1f}" width="{x1-x0+12:.1f}" height="38" rx="10" fill="{SRC_FILL}" stroke="{AMBER}" stroke-width="1.6" stroke-dasharray="5 4"/>')
for v in (0.30, 0.62):
    b.append(dot(vpos(x0, x1, v), sy - 1, 6.5, AMBER))
b.append(ctext(cx, sy + 38, "another source can add answers too", 18, AMBER))

# ---- Stage 2: is there value spread? ----
cx = colx(1) + COLW / 2
b.append(ctext(cx, LY + 24, "2   Is there variation along", 21, INK, "bold"))
b.append(ctext(cx, LY + 50, "the value axis (value spread)?", 21, INK, "bold"))
x0, x1 = ax_bounds(1)
# rich pool (top)
ry = LY + 92
b.append(axis(x0, x1, ry, GRAY, 2, right=False))
for v in POOL:
    b.append(dot(vpos(x0, x1, v), ry, 7, BLUE))
b.append(f'<text x="{x1:.1f}" y="{ry-16:.1f}" text-anchor="end" font-family="{FONT}" font-size="18" fill="{GREEN}" font-weight="bold">spread out &#10003;</text>')
# collapsed pool (bottom)
cy2 = LY + 176
b.append(axis(x0, x1, cy2, GRAY, 2, right=False))
cv = 0.5
for k in range(6):
    b.append(dot(vpos(x0, x1, cv), cy2 - 15 + k * 6, 7, GRAY))
b.append(f'<text x="{x1:.1f}" y="{cy2-30:.1f}" text-anchor="end" font-family="{FONT}" font-size="18" fill="{GRAY}" font-weight="bold">collapsed</text>')
t, _ = clines(cx, cy2 + 44, "a collapsed pool gives the judge nothing to choose between", 18, 32, GRAY)
b.append(t)

# ---- Stage 3: which answers are kept? ----
cx = colx(2) + COLW / 2
b.append(ctext(cx, LY + 34, "3   Which answers are kept?", 21, INK, "bold"))
x0, x1 = ax_bounds(2)
ay = LY + 118
b.append(axis(x0, x1, ay, GRAY, 2.2, right=False))
# average tick
avgx = vpos(x0, x1, AVG)
b.append(f'<line x1="{avgx:.1f}" y1="{ay-20:.1f}" x2="{avgx:.1f}" y2="{ay+20:.1f}" stroke="{GRAY}" stroke-width="2" stroke-dasharray="4 3"/>')
b.append(ctext(avgx, ay - 28, "pool average", 18, GRAY))
for i, v in enumerate(POOL):
    b.append(dot(vpos(x0, x1, v), ay, 7, BLUE, ring=(i in KEPT), ring_color=INK))
# gap arrow from average to kept-average
gy = ay + 52
keptx = vpos(x0, x1, KEPT_AVG)
b.append(larrow(avgx, keptx, gy, INK, 3.2))
b.append(ctext((avgx + keptx) / 2, gy + 26, "selection gap", 18, INK, "bold"))
b.append(ctext(cx, gy + 62, "the kept answers' average", 18, GRAY))
b.append(ctext(cx, gy + 82, "minus the pool average", 18, GRAY))

# ---- Stage 4: train ----
cx = colx(3) + COLW / 2
b.append(ctext(cx, LY + 34, "4   Train on the kept answers", 21, INK, "bold"))
x0, x1 = ax_bounds(3)
ay = LY + 128
b.append(axis(x0, x1, ay, GRAY, 2.2, right=False))
oldx = vpos(x0, x1, AVG)
b.append(f'<line x1="{oldx:.1f}" y1="{ay-18:.1f}" x2="{oldx:.1f}" y2="{ay+18:.1f}" stroke="{GRAY}" stroke-width="2" stroke-dasharray="4 3"/>')
b.append(ctext(oldx, ay - 26, "this pool", 18, GRAY))
NEXT = [0.06, 0.14, 0.20, 0.27, 0.34, 0.44]
for v in NEXT:
    b.append(dot(vpos(x0, x1, v), ay, 7, BLUE))
nextx = vpos(x0, x1, sum(NEXT) / len(NEXT))
b.append(larrow(oldx - 4, nextx, ay + 40, INK, 3.2))
b.append(ctext(cx, ay + 70, "the next pool shifts", 18, INK, "bold"))
b.append(ctext(cx, ay + 92, "the same way as the gap", 18, INK, "bold"))

# ---- loop-back arrow ----
y_back = LY + LH + 32
x4c = colx(3) + COLW / 2
x1c = colx(0) + COLW / 2
d = (f"M {x4c:.1f} {LY+LH} L {x4c:.1f} {y_back-8:.1f} Q {x4c:.1f} {y_back:.1f} {x4c-10:.1f} {y_back:.1f} "
     f"L {x1c+10:.1f} {y_back:.1f} Q {x1c:.1f} {y_back:.1f} {x1c:.1f} {y_back-8:.1f} L {x1c:.1f} {LY+LH+3:.1f}")
b.append(f'<path d="{d}" fill="none" stroke="{GRAY}" stroke-width="3"/>')
b.append(f'<path d="M {x1c-7:.1f} {LY+LH+8:.1f} L {x1c:.1f} {LY+LH-2:.1f} L {x1c+7:.1f} {LY+LH+8:.1f} z" fill="{GRAY}"/>')
b.append(ctext(W / 2, y_back + 26, "the loop repeats: the next pool may keep its value spread, run out of it, or be refreshed from another source", 18, GRAY))

# ==== takeaway ===========================================================
TY = y_back + 70
b.append(ctext(W / 2, TY,
               "The size of the selection gap is set by two dials — and the rest of the post follows how each one changes:",
               21, INK, "bold"))
b.append(ctext(W / 2, TY + 30,
               "selection gap   =   value spread   ×   the judge's grip (utilization)",
               20, GRAY, "bold"))


def spark(x0, x1, yb, yt, vals, color, sw=3.2):
    """A tiny round-by-round sparkline; vals in [0,1] map yb (bottom) -> yt (top)."""
    n = len(vals)
    pts = [(x0 + i * (x1 - x0) / (n - 1), yb - v * (yb - yt)) for i, v in enumerate(vals)]
    out = [axis(x0, x1, yb, "#d8dde3", 2, right=False)]
    d = "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in pts)
    out.append(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{sw}" stroke-linecap="round"/>')
    out.append(dot(pts[0][0], pts[0][1], 5, GRAY))
    out.append(dot(pts[-1][0], pts[-1][1], 5, color))
    return "\n".join(out)


PY2 = TY + 66
PANEL_H = 254
# ---- Panel A: value spread, a consumable state ----
ax = colx(0)
aw = 2 * COLW + GAP
b.append(box(ax, PY2, aw, PANEL_H, "white", BLUE, 2.5, rx=14))
b.append(f'<rect x="{ax:.1f}" y="{PY2:.1f}" width="10" height="{PANEL_H}" rx="5" fill="{BLUE}"/>')
b.append(ctext(ax + aw / 2, PY2 + 34, "Value spread: a state the loop spends or refills", 20, INK, "bold"))
SP_ROWS = [
    ("the model's own pool: slowly spent", [0.90, 0.72, 0.60, 0.52], BLUE),
    ("an outside source: refilled each round", [0.80, 0.86, 0.90, 0.88], GREEN),
    ("an extremist copy invades: collapses", [0.92, 0.42, 0.16, 0.06], RED),
]
sxr0, sxr1 = ax + aw - 300, ax + aw - 40
for k, (lab, vals, col) in enumerate(SP_ROWS):
    ry = PY2 + 92 + k * 56
    b.append(ltext(ax + 26, ry + 4, lab, 18, INK))
    b.append(spark(sxr0, sxr1, ry + 18, ry - 18, vals, col))
b.append(ltext(ax + 26, PY2 + PANEL_H - 16, "spread over four rounds", 16, GRAY))

# ---- Panel B: utilization, a fixed property ----
bx = colx(2)
bw = 2 * COLW + GAP
b.append(box(bx, PY2, bw, PANEL_H, "white", AMBER, 2.5, rx=14))
b.append(f'<rect x="{bx:.1f}" y="{PY2:.1f}" width="10" height="{PANEL_H}" rx="5" fill="{AMBER}"/>')
b.append(ctext(bx + bw / 2, PY2 + 34, "The judge's grip: a property, not a state", 20, INK, "bold"))
gxr0, gxr1 = bx + bw - 300, bx + bw - 40
GRIP_ROWS = [
    ("a judge that grips the value axis", 0.80, AMBER),
    ("a judge that ignores it (grip ≈ 0)", 0.30, GRAY),
]
for k, (lab, lvl, col) in enumerate(GRIP_ROWS):
    ry = PY2 + 100 + k * 60
    b.append(ltext(bx + 26, ry + 4, lab, 18, INK))
    b.append(spark(gxr0, gxr1, ry + 18, ry - 18, [lvl, lvl, lvl, lvl], col))
_t, _ = clines(bx + bw / 2, PY2 + PANEL_H - 40,
               "each judge holds near its own flat level; it moves only if you change the judge, the format, or the pool",
               16, 62, GRAY)
b.append(_t)

H = PY2 + PANEL_H + 34
with open("the_selection_loop_textfix.svg", "w") as f:
    f.write(svg_doc(W, H, "\n".join(b)))
print("wrote synthesis_the_selection_loop.svg")
