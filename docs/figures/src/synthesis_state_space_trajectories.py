#!/usr/bin/env python3
"""synthesis_state_space_trajectories — the main synthesis figure.

Every intervention on a stuck value is drawn as a path through the same two-axis
space: horizontal = how much the candidate answers vary, vertical = which way the
judge actually pulls. Rounds are connected by arrows; arrow thickness shows how
far the value moved that round. Dashed arrows mark where outside answers were
added. Start and end values are labelled on each path.

Regenerate with:  python3 synthesis_state_space_trajectories.py   (stdlib only)
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
FIGDIR = os.path.dirname(HERE) if os.path.basename(HERE) == "src" else HERE

INK = "#1a1a1a"
BLUE = "#2867b5"
GREEN = "#3a7d44"
RED = "#b5342c"
GRAY = "#6b7684"
PURPLE = "#8a5a9e"
AMBER = "#c07d18"
STRIP_FILL = "#eef2f6"

FONT = "Helvetica, Arial, sans-serif"

# minimum readable body font
BODY = 19

# soft region tints
R1_FILL = "#eef1f5"   # no variation strip (nothing to select)
R2_FILL = "#f6efe7"   # variation but wrong-way / no pull
R3_FILL = "#edf4ee"   # the open window (variation + aligned pull)
OPEN_INK = "#2f6b39"


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


def text_block(x, y, text, size, width, color=INK, weight="normal", lh=1.4):
    lines = wrap(text, width)
    svg = []
    for i, ln in enumerate(lines):
        svg.append(f'<text x="{x}" y="{y + i * size * lh}" font-family="{FONT}" '
                   f'font-size="{size}" font-weight="{weight}" fill="{color}">{esc(ln)}</text>')
    return "\n".join(svg), y + len(lines) * size * lh


def ctext(x, y, text, size, color=INK, weight="normal"):
    return (f'<text x="{x}" y="{y}" text-anchor="middle" font-family="{FONT}" '
            f'font-size="{size}" font-weight="{weight}" fill="{color}">{esc(text)}</text>')


def marker(x, y, shape, color, s=7.5):
    if shape == "circle":
        return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{s}" fill="{color}" stroke="white" stroke-width="1.5"/>'
    if shape == "square":
        return f'<rect x="{x-s:.1f}" y="{y-s:.1f}" width="{2*s}" height="{2*s}" fill="{color}" stroke="white" stroke-width="1.5"/>'
    if shape == "triangle":
        pts = f"{x:.1f},{y-s-1:.1f} {x-s-1:.1f},{y+s:.1f} {x+s+1:.1f},{y+s:.1f}"
        return f'<polygon points="{pts}" fill="{color}" stroke="white" stroke-width="1.5"/>'
    if shape == "diamond":
        pts = f"{x:.1f},{y-s-1.5:.1f} {x+s+1:.1f},{y:.1f} {x:.1f},{y+s+1.5:.1f} {x-s-1:.1f},{y:.1f}"
        return f'<polygon points="{pts}" fill="{color}" stroke="white" stroke-width="1.5"/>'
    return ""


def lines_at(x, y, lines, size=BODY, color=INK, anchor="start", weight="normal", lh=1.2):
    out = []
    for i, ln in enumerate(lines):
        out.append(f'<text x="{x:.1f}" y="{y + i * size * lh:.1f}" text-anchor="{anchor}" '
                   f'font-family="{FONT}" font-size="{size}" font-weight="{weight}" '
                   f'fill="{color}">{esc(ln)}</text>')
    return "\n".join(out)


def plate(x, y, text, size=20, anchor="start", color=INK, weight="bold"):
    """Bold value label on a white rounded plate so it reads over shading."""
    w = len(text) * size * 0.60 + 14
    h = size + 9
    if anchor == "start":
        rx = x - 6
    elif anchor == "end":
        rx = x - w + 6
    else:
        rx = x - w / 2
    ry = y - size + 2
    return (f'<rect x="{rx:.1f}" y="{ry:.1f}" width="{w:.1f}" height="{h}" rx="6" '
            f'fill="white" fill-opacity="0.92"/>'
            f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" font-family="{FONT}" '
            f'font-size="{size}" font-weight="{weight}" fill="{color}">{esc(text)}</text>')


import math


def arrow(x1, y1, x2, y2, w, color, dash=False):
    """A line from (x1,y1)->(x2,y2) of stroke width w with a solid arrowhead."""
    dx, dy = x2 - x1, y2 - y1
    L = math.hypot(dx, dy) or 1.0
    ux, uy = dx / L, dy / L
    head = max(15.0, w * 1.75)
    half = head * 0.60
    bx, by = x2 - ux * head, y2 - uy * head          # base of the head
    px, py = -uy, ux                                 # perpendicular
    p1 = (bx + px * half, by + py * half)
    p2 = (bx - px * half, by - py * half)
    dash_attr = ' stroke-dasharray="9 7"' if dash else ""
    line = (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{bx:.1f}" y2="{by:.1f}" '
            f'stroke="{color}" stroke-width="{w:.1f}" stroke-linecap="round"{dash_attr}/>')
    headpoly = (f'<polygon points="{x2:.1f},{y2:.1f} {p1[0]:.1f},{p1[1]:.1f} '
                f'{p2[0]:.1f},{p2[1]:.1f}" fill="{color}"/>')
    return line + headpoly


def svg_doc(w, h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
            f'font-family="{FONT}">\n<rect width="{w}" height="{h}" fill="white"/>\n'
            f'{body}\n</svg>')


# ---------------------------------------------------------------- geometry
W, H = 1500, 872
AX, AY, AW, AH = 190, 210, 830, 560
XMIN, XMAX = -0.05, 0.60
YMIN, YMAX = -0.58, 0.62


def ax_(v):
    return AX + AW * (v - XMIN) / (XMAX - XMIN)


def ay_(v):
    return AY + AH * (YMAX - v) / (YMAX - YMIN)


X_STRIP = 0.10      # right edge of the "no variation" strip
Y_ZERO = 0.0        # aligned pull above, wrong-way below


def W_OF(move):
    """Arrow stroke width encodes how far the value moved that round."""
    return 2.6 + 13.4 * move


# ---------------------------------------------------------------- figure body
b = []

b.append(ctext(W // 2, 50, "How interventions move through the same state space", 31, INK, "bold"))
b.append(ctext(W // 2, 86,
               "Each path is one intervention, plotted round by round; arrow thickness shows how far the value moved that round.",
               BODY, GRAY))

# ---- soft regime regions ----
xstrip = ax_(X_STRIP)
yzero = ay_(Y_ZERO)
b.append(f'<rect x="{AX}" y="{AY}" width="{xstrip - AX:.1f}" height="{AH}" fill="{R1_FILL}"/>')
b.append(f'<rect x="{xstrip:.1f}" y="{AY}" width="{AX + AW - xstrip:.1f}" height="{yzero - AY:.1f}" fill="{R3_FILL}"/>')
b.append(f'<rect x="{xstrip:.1f}" y="{yzero:.1f}" width="{AX + AW - xstrip:.1f}" height="{AY + AH - yzero:.1f}" fill="{R2_FILL}"/>')

# subtle boundary where variation begins
b.append(f'<line x1="{xstrip:.1f}" y1="{AY}" x2="{xstrip:.1f}" y2="{AY + AH}" stroke="#d3d8de" stroke-width="1.5" stroke-dasharray="4 5"/>')

# ---- axes ----
for v in (0.4, 0.2, 0.0, -0.2, -0.4):
    yy = ay_(v)
    if v == 0.0:
        b.append(f'<line x1="{AX}" y1="{yy:.1f}" x2="{AX + AW}" y2="{yy:.1f}" stroke="#8f96a0" stroke-width="2"/>')
    else:
        b.append(f'<line x1="{AX}" y1="{yy:.1f}" x2="{AX + AW}" y2="{yy:.1f}" stroke="#e2e4e6" stroke-width="1"/>')
    lab = "0" if v == 0.0 else f"{'+' if v > 0 else '−'}{abs(v):.1f}"
    b.append(f'<text x="{AX - 12}" y="{yy + 6:.1f}" text-anchor="end" font-size="{BODY}" fill="{GRAY}" font-family="{FONT}">{lab}</text>')
b.append(f'<text x="{AX + AW - 6}" y="{ay_(0.0) - 10:.1f}" text-anchor="end" font-size="{BODY}" fill="{GRAY}" font-family="{FONT}">no pull</text>')

# plot frame (left + bottom, light)
b.append(f'<line x1="{AX}" y1="{AY}" x2="{AX}" y2="{AY + AH}" stroke="{GRAY}" stroke-width="1.5"/>')
b.append(f'<line x1="{AX}" y1="{AY + AH}" x2="{AX + AW}" y2="{AY + AH}" stroke="{GRAY}" stroke-width="1.5"/>')

# x-axis end words + title
b.append(f'<text x="{ax_(0.02):.1f}" y="{AY + AH + 30}" text-anchor="middle" font-size="{BODY}" fill="{INK}" font-family="{FONT}">none</text>')
b.append(f'<text x="{ax_(0.57):.1f}" y="{AY + AH + 30}" text-anchor="middle" font-size="{BODY}" fill="{INK}" font-family="{FONT}">lots</text>')
b.append(f'<text x="{AX + AW / 2:.1f}" y="{AY + AH + 60}" text-anchor="middle" font-size="{BODY}" fill="{INK}" font-family="{FONT}">how much the candidate answers vary</text>')

# y-axis title (direction folded in, so nothing collides with the tick numbers)
b.append(f'<text x="118" y="{AY + AH / 2:.1f}" font-size="{BODY}" fill="{INK}" font-family="{FONT}" '
         f'transform="rotate(-90 118 {AY + AH / 2:.1f})" text-anchor="middle">which way the judge pulls  (↑ intended · ↓ the other way)</text>')


# ---------------------------------------------------------------- trajectories
def node(x, y, color=INK, s=6.0):
    return marker(ax_(x), ay_(y), "circle", color, s)


# ===== the shared saturated state (trajectory b lives here) =====
Sx, Sy = 0.02, 0.04
fSx, fSy = 0.02, -0.02

# ---- (a) second risk model — rich reversal (green, variation consumed) ----
A = [(0.52, 0.46, 0.917), (0.40, 0.40, 0.58), (0.26, 0.32, 0.28), (0.13, 0.22, 0.094)]
for i in range(len(A) - 1):
    x1, y1, v1 = A[i]
    x2, y2, v2 = A[i + 1]
    b.append(arrow(ax_(x1), ay_(y1), ax_(x2), ay_(y2), W_OF(abs(v1 - v2)), GREEN))
for (x, y, v) in A:
    b.append(node(x, y, INK))

# Injection paths read as a clean elbow: the dashed arrow raises the variation
# (moves right into the window), then the green pull lifts the value straight up.
# The green tail starts a small gap ABOVE the node so it never buries the dashed
# arrowhead, and the node is drawn last, on top.
GAP = 0.03

# ---- (c) second risk model — outside answers added (green) ----
c_x, c_y0, c_y1 = 0.42, 0.06, 0.30
b.append(arrow(ax_(Sx), ay_(Sy), ax_(c_x), ay_(c_y0), 3.2, GRAY, dash=True))
b.append(arrow(ax_(c_x), ay_(c_y0 + GAP), ax_(c_x), ay_(c_y1), W_OF(0.516), GREEN))
b.append(node(c_x, c_y1, INK))
b.append(node(c_x, c_y0, INK))

# ---- (f) the insecure-code model — reopening (green) ----
f_x, f_y0, f_y1 = 0.30, 0.02, 0.22
b.append(arrow(ax_(fSx), ay_(fSy), ax_(f_x), ay_(f_y0), 3.2, GRAY, dash=True))
b.append(arrow(ax_(f_x), ay_(f_y0 + GAP), ax_(f_x), ay_(f_y1), W_OF(0.627), GREEN))
b.append(node(f_x, f_y1, INK))
b.append(node(f_x, f_y0, INK))

# ---- (d) cautious-prompted rescue (amber, wrong-signed, barely moves) ----
b.append(arrow(ax_(0.33), ay_(-0.12), ax_(0.29), ay_(-0.16), W_OF(0.04), AMBER))
b.append(node(0.33, -0.12, INK))
b.append(node(0.29, -0.16, INK))

# ---- (e) contamination (red, one big wrong-way jump) ----
b.append(arrow(ax_(0.40), ay_(-0.30), ax_(0.18), ay_(-0.46), W_OF(0.90), RED))
b.append(node(0.40, -0.30, INK))
b.append(node(0.18, -0.46, RED, 7.0))

# ---- (b) the saturated state + the gambling start dot ----
b.append(node(Sx, Sy, GRAY, 8.0))
b.append(node(fSx, fSy, INK, 7.0))

# ---------------------------------------------------------------- direct labels
# (a) its own answers still vary, so the min-risk judge walks the value down
b.append(lines_at(500, 232, ["second risk model: its answers still vary,",
                             "so the judge walks the value down"],
                  size=20, color=INK, weight="bold"))
b.append(plate(ax_(0.52) + 12, ay_(0.46) + 4, "0.917", anchor="start"))
b.append(plate(ax_(0.13) - 6, ay_(0.22) + 30, "0.094", anchor="middle"))

# (c) — same model, stuck, then outside answers are mixed in and it moves again
b.append(lines_at(ax_(0.45), ay_(0.24), ["second risk model:", "stuck, then outside", "answers added"],
                  size=20, color=INK, anchor="start", weight="bold", lh=1.2))
b.append(plate(ax_(c_x) - 8, ay_(c_y1) - 2, "0.484", anchor="end"))

# (b) + (f) — left strip
b.append(lines_at(198, 300, ["second risk model:", "stuck at 1.000 —", "answers all alike"],
                  size=20, color=INK, weight="bold", lh=1.15))
b.append(f'<line x1="252" y1="350" x2="{ax_(Sx) - 3:.1f}" y2="{ay_(Sy) - 6:.1f}" stroke="{GRAY}" stroke-width="1.2"/>')
b.append(plate(ax_(Sx) + 13, ay_(Sy) + 6, "1.000", anchor="start"))

b.append(lines_at(198, 650, ["insecure-code model:", "stuck at 0.625, then", "outside answers added"],
                  size=20, color=INK, weight="bold", lh=1.15))
b.append(f'<line x1="250" y1="636" x2="{ax_(fSx) - 3:.1f}" y2="{ay_(fSy) + 6:.1f}" stroke="{GRAY}" stroke-width="1.2"/>')
b.append(plate(ax_(fSx) + 13, ay_(fSy) + 6, "0.627", anchor="start"))
b.append(plate(ax_(f_x) + 10, ay_(f_y1) - 2, "0.000", anchor="start"))

# (d) same stuck pool, but a cautious judge instead — it pulls the wrong way
b.append(lines_at(700, 548, ["a cautious judge instead:"], size=20, color=INK, weight="bold"))
b.append(lines_at(700, 570, ["pulls the other way, barely moves", ], size=19, color=AMBER))

# (e) a maxed-out copy is added and an ordinary judge keeps it
b.append(lines_at(775, 632, ["a maxed-out copy added:"], size=20, color=RED, weight="bold"))
b.append(lines_at(775, 656, ["an ordinary judge keeps it —",
                             "the value jumps up in one round"],
                  size=19, color=INK, lh=1.2))

# ---------------------------------------------------------------- legends (right)
LX = 1072

# colour legend
b.append(f'<text x="{LX}" y="238" font-size="20" font-weight="bold" fill="{INK}" font-family="{FONT}">Colour = which way the value moved</text>')
for i, (col, txt) in enumerate([
        (GREEN, "moved the intended way"),
        (GRAY, "no move"),
        (RED, "moved the other way")]):
    yy = 276 + i * 34
    b.append(arrow(LX + 6, yy - 6, LX + 62, yy - 6, 7, col))
    b.append(f'<text x="{LX + 78}" y="{yy}" font-size="{BODY}" fill="{INK}" font-family="{FONT}">{esc(txt)}</text>')

# thickness legend
b.append(f'<text x="{LX}" y="418" font-size="20" font-weight="bold" fill="{INK}" font-family="{FONT}">Thickness = how far the value moved</text>')
for i, (wd, cap) in enumerate([(4.0, "barely"), (10.0, "a lot"), (15.5, "nearly all the way")]):
    yy = 456 + i * 44
    b.append(arrow(LX + 6, yy - 6, LX + 92, yy - 6, wd, GRAY))
    b.append(f'<text x="{LX + 112}" y="{yy}" font-size="{BODY}" fill="{INK}" font-family="{FONT}">{esc(cap)}</text>')

# dashed / injection legend
b.append(f'<text x="{LX}" y="632" font-size="20" font-weight="bold" fill="{INK}" font-family="{FONT}">Dashed = outside answers added</text>')
b.append(arrow(LX + 6, 664, LX + 92, 664, 3.2, GRAY, dash=True))
b.append(f'<text x="{LX + 112}" y="670" font-size="{BODY}" fill="{INK}" font-family="{FONT}">raises the variation</text>')

# node key
b.append(f'<text x="{LX}" y="716" font-size="20" font-weight="bold" fill="{INK}" font-family="{FONT}">Dots mark each round; numbers are</text>')
b.append(f'<text x="{LX}" y="742" font-size="20" font-weight="bold" fill="{INK}" font-family="{FONT}">the value at the start and end.</text>')

svg = svg_doc(W, H, "\n".join(b))
with open(os.path.join(FIGDIR, "synthesis_state_space_trajectories.svg"), "w") as f:
    f.write(svg)
print("wrote synthesis_state_space_trajectories.svg")
