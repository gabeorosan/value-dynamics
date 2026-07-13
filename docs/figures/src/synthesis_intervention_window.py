#!/usr/bin/env python3
"""synthesis_intervention_window — a two-dimensional regime map.

Two things decide whether pushing on a stuck value actually moves it:
how much the candidate answers vary (horizontal), and which way the judge
actually pulls once there is something to select (vertical). Each dot is one
real intervention; color says what happened next, size says how far it moved,
shape says which pool the answers came from.

Regenerate with:  python3 synthesis_intervention_window.py   (stdlib only)
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = HERE
while ROOT != os.path.dirname(ROOT) and not os.path.isdir(os.path.join(ROOT, "experiments")):
    ROOT = os.path.dirname(ROOT)
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

# soft region tints + darker text ink for each region label
R1_FILL, R1_INK = "#eef1f5", "#5a6472"   # nothing to select
R2_FILL, R2_INK = "#f6efe7", "#8a6d3b"   # no move / opposite way
R3_FILL, R3_INK = "#edf4ee", "#2f6b39"   # the value moves


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


def box(x, y, w, h, fill, stroke=INK, sw=2.5, rx=8):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')


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


def svg_doc(w, h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
            f'font-family="{FONT}">\n<rect width="{w}" height="{h}" fill="white"/>\n'
            f'{body}\n</svg>')


def lines_at(x, y, lines, size=BODY, color=INK, anchor="start", weight="normal", lh=1.2):
    out = []
    for i, ln in enumerate(lines):
        out.append(f'<text x="{x:.1f}" y="{y + i * size * lh:.1f}" text-anchor="{anchor}" '
                   f'font-family="{FONT}" font-size="{size}" font-weight="{weight}" '
                   f'fill="{color}">{esc(ln)}</text>')
    return "\n".join(out)


# ---------------------------------------------------------------- geometry
W, H = 1500, 950
AX, AY, AW, AH = 180, 225, 840, 555
XMIN, XMAX = -0.03, 0.62     # within-item spread (words at the ends, not numbers)
YMIN, YMAX = -0.55, 0.60     # realized selection gap toward the intended direction


def ax_(v):
    return AX + AW * (v - XMIN) / (XMAX - XMIN)


def ay_(v):
    return AY + AH * (YMAX - v) / (YMAX - YMIN)


X_STRIP = 0.10   # right edge of the "no variation" strip
Y_GRIP = 0.20    # above this the pull is strong enough to move the value


# ---------------------------------------------------------------- the real cells
# x = how much the candidate answers vary; y = gap toward the intended
# direction (up = toward intended); move = size of the next-step move.
POINTS = [
    dict(x=0.00, y=0.00, move=0.00, color=GRAY, shape="circle",
         head="Own answers, saturated", sub=["risk stuck at 1.00, no variation"],
         lx=236, ly=506, anchor="start"),
    dict(x=0.50, y=0.46, move=0.823, color=GREEN, shape="circle",
         head="Own answers, varied", sub=["risk 0.92 → 0.09"],
         lx=694, ly=242, anchor="start"),
    dict(x=0.40, y=0.31, move=0.516, color=GREEN, shape="square",
         head="Mixed with another model’s", sub=["answers  ·  risk 1.00 → 0.48"],
         lx=754, ly=360, anchor="start"),
    dict(x=0.33, y=0.09, move=0.05, color=GRAY, shape="square",
         head="Mixed, cautious judge", sub=["small pull, risk barely moves"],
         lx=662, ly=468, anchor="start"),
    dict(x=0.44, y=-0.44, move=0.90, color=RED, shape="triangle",
         head="A maxed-out copy in the pool",
         sub=["the judge keeps it — the value", "jumps up in one round"],
         lx=787, ly=636, anchor="middle"),
    dict(x=0.30, y=0.36, move=0.627, color=GREEN, shape="square",
         head="Insecure-code model", sub=["insecure code 0.63 → 0.00"],
         lx=470, ly=382, anchor="start"),
]


def radius(move):
    return 6.0 + 15.5 * move


# ---------------------------------------------------------------- figure
b = []

b.append(ctext(W // 2, 52, "Two things decide whether an intervention moves a stuck value", 30, INK, "bold"))
b.append(ctext(W // 2, 88,
               "Each dot is one attempt to move a stuck value; where it lands shows the two things that decide the outcome.",
               BODY, GRAY))

# ---- soft regime regions (no hard boundary lines) ----
xstrip = ax_(X_STRIP)
ygrip = ay_(Y_GRIP)
b.append(f'<rect x="{AX}" y="{AY}" width="{xstrip - AX:.1f}" height="{AH}" fill="{R1_FILL}"/>')
b.append(f'<rect x="{xstrip:.1f}" y="{AY}" width="{AX + AW - xstrip:.1f}" height="{ygrip - AY:.1f}" fill="{R3_FILL}"/>')
b.append(f'<rect x="{xstrip:.1f}" y="{ygrip:.1f}" width="{AX + AW - xstrip:.1f}" height="{AY + AH - ygrip:.1f}" fill="{R2_FILL}"/>')

# region labels
b.append(lines_at((AX + xstrip) / 2, AY + 34, ["no variation →", "nothing to", "select"],
                  size=20, color=R1_INK, anchor="middle", weight="600", lh=1.15))
b.append(lines_at(xstrip + 16, AY + 26, ["variation + the judge grips it →", "the value moves"],
                  size=20, color=R3_INK, anchor="start", weight="600", lh=1.15))
b.append(lines_at(xstrip + 16, ay_(-0.24), ["variation, but the judge doesn’t", "pull that way → little or no move"],
                  size=20, color=R2_INK, anchor="start", weight="600", lh=1.15))

# ---- axes ----
# y gridlines + ticks
for v in (0.4, 0.2, 0.0, -0.2, -0.4):
    yy = ay_(v)
    if v == 0.0:
        b.append(f'<line x1="{AX}" y1="{yy:.1f}" x2="{AX + AW}" y2="{yy:.1f}" stroke="#9aa0a8" stroke-width="2"/>')
    else:
        b.append(f'<line x1="{AX}" y1="{yy:.1f}" x2="{AX + AW}" y2="{yy:.1f}" stroke="#e2e4e6" stroke-width="1"/>')
    lab = "0" if v == 0.0 else f"{'+' if v > 0 else '−'}{abs(v):.1f}"
    b.append(f'<text x="{AX - 12}" y="{yy + 6:.1f}" text-anchor="end" font-size="{BODY}" fill="{GRAY}" font-family="{FONT}">{lab}</text>')
b.append(f'<text x="{AX + AW - 6}" y="{ay_(0.0) - 10:.1f}" text-anchor="end" font-size="{BODY}" fill="{GRAY}" font-family="{FONT}">no pull</text>')

# plot frame (left + bottom only, light)
b.append(f'<line x1="{AX}" y1="{AY}" x2="{AX}" y2="{AY + AH}" stroke="{GRAY}" stroke-width="1.5"/>')
b.append(f'<line x1="{AX}" y1="{AY + AH}" x2="{AX + AW}" y2="{AY + AH}" stroke="{GRAY}" stroke-width="1.5"/>')

# x-axis end words + title
b.append(f'<text x="{ax_(0.03):.1f}" y="{AY + AH + 30}" text-anchor="middle" font-size="{BODY}" fill="{INK}" font-family="{FONT}">no variation</text>')
b.append(f'<text x="{ax_(0.57):.1f}" y="{AY + AH + 30}" text-anchor="middle" font-size="{BODY}" fill="{INK}" font-family="{FONT}">lots of variation</text>')
b.append(f'<text x="{AX + AW / 2:.1f}" y="{AY + AH + 60}" text-anchor="middle" font-size="{BODY}" fill="{INK}" font-family="{FONT}">how much the candidate answers vary</text>')

# y-axis title
b.append(f'<text x="112" y="{AY + AH / 2:.1f}" font-size="{BODY}" fill="{INK}" font-family="{FONT}" '
         f'transform="rotate(-90 112 {AY + AH / 2:.1f})" text-anchor="middle">which way the judge pulls  (up = the intervention’s intended direction)</text>')

# ---- points + direct labels ----
for p in POINTS:
    b.append(marker(ax_(p["x"]), ay_(p["y"]), p["shape"], p["color"], radius(p["move"])))
for p in POINTS:
    b.append(lines_at(p["lx"], p["ly"], [p["head"]], size=BODY, color=INK, anchor=p["anchor"], weight="bold"))
    b.append(lines_at(p["lx"], p["ly"] + BODY * 1.2, p["sub"], size=BODY, color=GRAY, anchor=p["anchor"]))

# ================= right column: three legends =================
LX = 1085

# color legend
b.append(f'<text x="{LX}" y="238" font-size="20" font-weight="bold" fill="{INK}" font-family="{FONT}">Did the value move?</text>')
for i, (col, txt) in enumerate([
        (GREEN, "moved the intended way"),
        (GRAY, "no move"),
        (RED, "moved the other way")]):
    yy = 276 + i * 38
    b.append(marker(LX + 12, yy - 5, "circle", col, 10))
    b.append(f'<text x="{LX + 36}" y="{yy}" font-size="{BODY}" fill="{INK}" font-family="{FONT}">{esc(txt)}</text>')

# size legend
b.append(f'<text x="{LX}" y="418" font-size="20" font-weight="bold" fill="{INK}" font-family="{FONT}">Dot size = how far it moved</text>')
for cx, s, cap in [(LX + 40, 7, "barely"), (LX + 160, 13, "a lot"), (LX + 285, 20, "nearly all")]:
    b.append(marker(cx, 462, "circle", GRAY, s))
    b.append(f'<text x="{cx}" y="504" text-anchor="middle" font-size="{BODY}" fill="{GRAY}" font-family="{FONT}">{esc(cap)}</text>')

# shape legend
b.append(f'<text x="{LX}" y="562" font-size="20" font-weight="bold" fill="{INK}" font-family="{FONT}">Which pool the answers came from</text>')
for i, (shp, txt) in enumerate([
        ("circle", "the model’s own answers"),
        ("square", "mixed with another source’s answers"),
        ("triangle", "half the answers from a maxed-out copy")]):
    yy = 600 + i * 40
    b.append(marker(LX + 12, yy - 5, shp, INK, 10))
    b.append(f'<text x="{LX + 36}" y="{yy}" font-size="{BODY}" fill="{INK}" font-family="{FONT}">{esc(txt)}</text>')

# ---- takeaway ----
b.append(f'<rect x="0" y="856" width="{W}" height="46" fill="{STRIP_FILL}"/>')
b.append(ctext(W // 2, 886,
               "Variation opens the window; whether the judge grips it decides if the value moves, and which way.",
               21, INK, "bold"))

# entropy scope note (the axes stay S x G; generic entropy is not a third axis)
b.append(ctext(W // 2, 930,
               "Generic token entropy was tested separately; it does not certify this spread axis or improve the signed transition model.",
               15, GRAY))

svg = svg_doc(W, H, "\n".join(b))
with open(os.path.join(FIGDIR, "synthesis_intervention_window.svg"), "w") as f:
    f.write(svg)
print("wrote synthesis_intervention_window.svg")
