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
b.append(ctext(cx, LY + 60, "six candidate answers", 17, GRAY))
b.append(robot(cx - 56 * 0.6 / 2, LY + 82, BLUE, 0.6))
x0, x1 = ax_bounds(0)
ay = LY + 168
b.append(axis(x0, x1, ay, GRAY, 2.2, right=True, left=True))
for v in POOL:
    b.append(dot(vpos(x0, x1, v), ay, 7, BLUE))
b.append(ltext(x0 - 2, ay + 26, "lower", 16, GRAY))
b.append(f'<text x="{x1+2:.1f}" y="{ay+26:.1f}" text-anchor="end" font-family="{FONT}" font-size="16" fill="{GRAY}">higher</text>')
b.append(ctext(cx, ay + 26, "the value", 16, GRAY))
# second source stream
sy = LY + 242
b.append(f'<rect x="{x0-6:.1f}" y="{sy-20:.1f}" width="{x1-x0+12:.1f}" height="38" rx="10" fill="{SRC_FILL}" stroke="{AMBER}" stroke-width="1.6" stroke-dasharray="5 4"/>')
for v in (0.30, 0.62):
    b.append(dot(vpos(x0, x1, v), sy - 1, 6.5, AMBER))
b.append(ctext(cx, sy + 38, "another source can add answers too", 16, AMBER))

# ---- Stage 2: is there variation? ----
cx = colx(1) + COLW / 2
b.append(ctext(cx, LY + 34, "2   Is there variation?", 21, INK, "bold"))
x0, x1 = ax_bounds(1)
# rich pool (top)
ry = LY + 92
b.append(axis(x0, x1, ry, GRAY, 2, right=False))
for v in POOL:
    b.append(dot(vpos(x0, x1, v), ry, 7, BLUE))
b.append(f'<text x="{x1:.1f}" y="{ry-16:.1f}" text-anchor="end" font-family="{FONT}" font-size="16" fill="{GREEN}" font-weight="bold">spread out &#10003;</text>')
# collapsed pool (bottom)
cy2 = LY + 176
b.append(axis(x0, x1, cy2, GRAY, 2, right=False))
cv = 0.5
for k in range(6):
    b.append(dot(vpos(x0, x1, cv), cy2 - 15 + k * 6, 7, GRAY))
b.append(f'<text x="{x1:.1f}" y="{cy2-30:.1f}" text-anchor="end" font-family="{FONT}" font-size="16" fill="{GRAY}" font-weight="bold">collapsed</text>')
t, _ = clines(cx, cy2 + 44, "a collapsed pool gives the judge nothing to choose between", 16, 32, GRAY)
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
b.append(ctext(avgx, ay - 28, "average", 16, GRAY))
for i, v in enumerate(POOL):
    b.append(dot(vpos(x0, x1, v), ay, 7, BLUE, ring=(i in KEPT), ring_color=INK))
# gap arrow from average to kept-average
gy = ay + 52
keptx = vpos(x0, x1, KEPT_AVG)
b.append(larrow(avgx, keptx, gy, INK, 3.2))
b.append(ctext((avgx + keptx) / 2, gy + 26, "selection gap", 17, INK, "bold"))
b.append(ctext(cx, gy + 62, "the kept answers (ringed) sit", 16, GRAY))
b.append(ctext(cx, gy + 82, "off to one side of the average", 16, GRAY))

# ---- Stage 4: train ----
cx = colx(3) + COLW / 2
b.append(ctext(cx, LY + 34, "4   Train on the kept answers", 21, INK, "bold"))
x0, x1 = ax_bounds(3)
ay = LY + 128
b.append(axis(x0, x1, ay, GRAY, 2.2, right=False))
oldx = vpos(x0, x1, AVG)
b.append(f'<line x1="{oldx:.1f}" y1="{ay-18:.1f}" x2="{oldx:.1f}" y2="{ay+18:.1f}" stroke="{GRAY}" stroke-width="2" stroke-dasharray="4 3"/>')
b.append(ctext(oldx, ay - 26, "this pool", 16, GRAY))
NEXT = [0.06, 0.14, 0.20, 0.27, 0.34, 0.44]
for v in NEXT:
    b.append(dot(vpos(x0, x1, v), ay, 7, BLUE))
nextx = vpos(x0, x1, sum(NEXT) / len(NEXT))
b.append(larrow(oldx - 4, nextx, ay + 40, INK, 3.2))
b.append(ctext(cx, ay + 70, "the next pool shifts", 17, INK, "bold"))
b.append(ctext(cx, ay + 92, "the same way as the gap", 17, INK, "bold"))

# ---- loop-back arrow ----
y_back = LY + LH + 32
x4c = colx(3) + COLW / 2
x1c = colx(0) + COLW / 2
d = (f"M {x4c:.1f} {LY+LH} L {x4c:.1f} {y_back-8:.1f} Q {x4c:.1f} {y_back:.1f} {x4c-10:.1f} {y_back:.1f} "
     f"L {x1c+10:.1f} {y_back:.1f} Q {x1c:.1f} {y_back:.1f} {x1c:.1f} {y_back-8:.1f} L {x1c:.1f} {LY+LH+3:.1f}")
b.append(f'<path d="{d}" fill="none" stroke="{GRAY}" stroke-width="3"/>')
b.append(f'<path d="M {x1c-7:.1f} {LY+LH+8:.1f} L {x1c:.1f} {LY+LH-2:.1f} L {x1c+7:.1f} {LY+LH+8:.1f} z" fill="{GRAY}"/>')
b.append(ctext(W / 2, y_back + 26, "the loop repeats: the next pool may keep its variation, run out of it, or be refreshed from another source", 17, GRAY))

# ==== OUTCOME CARDS ======================================================
CY = y_back + 76
CH = 258
b.append(ctext(W / 2, CY - 20, "What the loop does", 20, INK, "bold"))

CARDS = [
    dict(head="Variation, and a judge that pulls one way: the value moves",
         color=BLUE, kind="single", v0=0.917, v1=0.094),
    dict(head="No variation: nothing to select, the value stays put",
         color=GRAY, kind="stay", v0=1.000, v1=1.000),
    dict(head="Answers from another source refill the variation: movement reopens",
         color=AMBER, kind="double",
         r1=(1.000, 0.484, "one model"),
         r2=(0.627, 0.000, "a second model family")),
    dict(head="Another source, but the wrong judge: it moves the wrong way, no rescue",
         color=RED, kind="wrong"),
]

for i, c in enumerate(CARDS):
    bx = colx(i)
    accent = c["color"]
    b.append(box(bx, CY, COLW, CH, "white", accent, 2.5, rx=14))
    b.append(f'<rect x="{bx:.1f}" y="{CY:.1f}" width="10" height="{CH}" rx="5" fill="{accent}"/>')
    hx = bx + COLW / 2
    _, hy = clines(hx, CY + 34, c["head"], 18, 30, INK, "bold")
    b.append(_)
    # mini value axis region
    mx0, mx1 = bx + 34, bx + COLW - 26
    letter = "abcd"[i]
    b.append(f'<text x="{bx+18:.1f}" y="{CY+CH-16:.1f}" font-family="{FONT}" font-size="17" fill="{GRAY}" font-weight="bold">{letter}</text>')

    if c["kind"] == "single":
        my = CY + 168
        b.append(axis(mx0, mx1, my, "#d8dde3", 2, right=False))
        p0 = vpos(mx0, mx1, c["v0"])
        p1 = vpos(mx0, mx1, c["v1"])
        b.append(larrow(p0 - 2, p1 + 2, my, accent, 3.2))
        b.append(dot(p0, my, 8, GRAY))
        b.append(dot(p1, my, 8, accent))
        b.append(ctext(p0, my - 20, f"{c['v0']:.3f}", 19, GRAY, "bold"))
        b.append(ctext(p1, my - 20, f"{c['v1']:.3f}", 20, accent, "bold"))
        b.append(ctext(p0, my + 34, "start", 16, GRAY))
        b.append(ctext(p1, my + 34, "after training", 16, accent))

    elif c["kind"] == "stay":
        my = CY + 168
        b.append(axis(mx0, mx1, my, "#d8dde3", 2, right=False))
        p = vpos(mx0, mx1, c["v0"])
        b.append(f'<circle cx="{p:.1f}" cy="{my:.1f}" r="15" fill="none" stroke="{accent}" stroke-width="2" stroke-dasharray="4 3"/>')
        b.append(dot(p, my, 8, accent))
        b.append(ctext(p, my - 26, f"{c['v0']:.3f}", 20, accent, "bold"))
        b.append(ctext(bx + COLW / 2, my + 40, "spread 0.000 - stays put", 17, GRAY))

    elif c["kind"] == "double":
        for k, (row, secondlab) in enumerate([(c["r1"], False), (c["r2"], True)]):
            v0, v1, lab = row
            my = CY + 128 + k * 78
            col = accent
            b.append(axis(mx0, mx1, my, "#d8dde3", 2, right=False))
            p0 = vpos(mx0, mx1, v0)
            p1 = vpos(mx0, mx1, v1)
            b.append(larrow(p0 - 2, p1 + 2, my, col, 3))
            b.append(dot(p0, my, 7, GRAY))
            b.append(dot(p1, my, 7, col))
            b.append(ctext(p0, my - 16, f"{v0:.3f}", 18, GRAY, "bold"))
            b.append(ctext(p1, my - 16, f"{v1:.3f}", 18, col, "bold"))
            b.append(ctext(bx + COLW / 2, my + 30, lab, 16, GRAY))

    elif c["kind"] == "wrong":
        my = CY + 168
        b.append(axis(mx0, mx1, my, "#d8dde3", 2, right=False))
        p0 = vpos(mx0, mx1, 0.28)
        p1 = vpos(mx0, mx1, 0.80)
        b.append(rarrow(p0 + 2, p1 - 2, my, accent, 3.2))
        b.append(dot(p0, my, 8, GRAY))
        b.append(dot(p1, my, 8, accent))
        b.append(ctext(bx + COLW / 2, my + 40, "the wrong way, no rescue", 17, accent, "bold"))

# ==== takeaway ===========================================================
TY = CY + CH + 46
b.append(ctext(W / 2, TY,
               "The pool decides what moves are available; the judge decides which available move is trained; "
               "training changes what the next pool can offer.",
               20, INK, "bold"))

H = TY + 30
with open(os.path.join(FIGDIR, "synthesis_the_selection_loop.svg"), "w") as f:
    f.write(svg_doc(W, H, "\n".join(b)))
print("wrote synthesis_the_selection_loop.svg")
