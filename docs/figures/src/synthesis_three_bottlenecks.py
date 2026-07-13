#!/usr/bin/env python3
"""synthesis_three_bottlenecks — an evidence map of the shared experimental logic.

Left to right: each experiment family (with one evidence tag), the single
bottleneck question it isolates, and the one conclusion they all feed into.
Every bottleneck is a question about one of two things — is there variation,
and does the judge grip it — so the five families converge on the same box.

Regenerate with:  python3 synthesis_three_bottlenecks.py   (stdlib only)
"""
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = HERE
while ROOT != os.path.dirname(ROOT) and not os.path.isdir(os.path.join(ROOT, "experiments")):
    ROOT = os.path.dirname(ROOT)
FIGDIR = os.path.dirname(HERE) if os.path.basename(HERE) == "src" else HERE

INK = "#1a1a1a"
GRAY = "#6b7684"
FONT = "Helvetica, Arial, sans-serif"
BODY = 19

# the two things every bottleneck is about
VAR_STROKE, VAR_FILL, VAR_INK = "#3a7d44", "#edf4ee", "#2f6b39"      # variation
JUD_STROKE, JUD_FILL, JUD_INK = "#8a5a9e", "#f2ecf6", "#63447a"      # the judge
BOX_FILL = "#f7f8fa"


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
    return (f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="middle" font-family="{FONT}" '
            f'font-size="{size}" font-weight="{weight}" fill="{color}">{esc(text)}</text>')


def ltext(x, y, text, size, color=INK, weight="normal"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{FONT}" font-size="{size}" '
            f'font-weight="{weight}" fill="{color}">{esc(text)}</text>')


def box(x, y, w, h, fill, stroke=INK, sw=2.5, rx=10):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')


def svg_doc(w, h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
            f'font-family="{FONT}">\n<rect width="{w}" height="{h}" fill="white"/>\n'
            f'{body}\n</svg>')


def arrow(x0, y0, x1, y1, color, sw=3.0, head=10.0):
    ang = math.atan2(y1 - y0, x1 - x0)
    lx = x1 - head * 0.9 * math.cos(ang)
    ly = y1 - head * 0.9 * math.sin(ang)
    line = (f'<line x1="{x0:.1f}" y1="{y0:.1f}" x2="{lx:.1f}" y2="{ly:.1f}" '
            f'stroke="{color}" stroke-width="{sw}"/>')
    a1, a2 = ang + math.radians(150), ang - math.radians(150)
    p1 = (x1 + head * math.cos(a1), y1 + head * math.sin(a1))
    p2 = (x1 + head * math.cos(a2), y1 + head * math.sin(a2))
    tri = (f'<polygon points="{x1:.1f},{y1:.1f} {p1[0]:.1f},{p1[1]:.1f} '
           f'{p2[0]:.1f},{p2[1]:.1f}" fill="{color}"/>')
    return line + tri


def centered_lines(cx, cy, lines, size, color, weight="normal", lh=1.2):
    out = []
    first = cy - (len(lines) - 1) * size * lh / 2 + size * 0.34
    for i, ln in enumerate(lines):
        out.append(ctext(cx, first + i * size * lh, ln, size, color, weight))
    return "\n".join(out)


# ---------------------------------------------------------------- content
# family, evidence tag, bottleneck question, kind ("var" or "judge")
ROWS = [
    dict(kind="judge",
         family="Judge-choice grids",
         tag="the gambling model judging itself ends anywhere 0.26–1.00; "
             "a neutral judge stays 0.47–0.60",
         q="Does the judge grip?"),
    dict(kind="var",
         family="Reversal by selection",
         tag="the gambling model reversed in 3/3 runs; a second risk model "
             "fell 0.917→0.094 while its answers still varied",
         q="Is variation available?"),
    dict(kind="var",
         family="Release / sampling tests",
         tag="once the answers collapsed, a second risk model held "
             "1.000→1.000 (no variation)",
         q="Can variation come back on its own?"),
    dict(kind="var",
         family="Adding outside answers",
         tag="injecting answers moved the gambling model 0.627→0.000; "
             "without it, 0.625→0.625",
         q="Can variation be added?"),
    dict(kind="judge",
         family="Contamination tests",
         tag="with a maxed-out copy in the pool, 4/4 runs reached at least "
             "0.917 after one round",
         q="Which source does the judge keep?"),
]

KIND = {
    "var": dict(stroke=VAR_STROKE, fill=VAR_FILL, ink=VAR_INK),
    "judge": dict(stroke=JUD_STROKE, fill=JUD_FILL, ink=JUD_INK),
}


# ---------------------------------------------------------------- geometry
W = 1500
TOP = 168
RH = 128
GAP = 24

LX, LW = 40, 558          # family column
LH = 118
MX, MW = 650, 304         # bottleneck column
MH = 82
CX_, CW = 1088, 372       # conclusion column
CH = 210
FUNNEL = (1052.0, 0.0)    # y filled in below

centers = [TOP + RH / 2 + i * (RH + GAP) for i in range(len(ROWS))]
mid_center = centers[len(centers) // 2]
FUNNEL = (1052.0, mid_center)
CY = mid_center - CH / 2

HDR = 132
LEG_Y = 156

col_left_cx = LX + LW / 2
col_mid_cx = MX + MW / 2
col_right_cx = CX_ + CW / 2


# ---------------------------------------------------------------- figure
b = []

b.append(ctext(W / 2, 52,
               "Every experiment tests the same two things: is there variation, and does the judge grip it?",
               29, INK, "bold"))
b.append(ctext(W / 2, 88,
               "Read left to right: an experiment family, the one bottleneck question it isolates, and the single conclusion they all share.",
               BODY, GRAY))

# column headers
b.append(ctext(col_left_cx, HDR, "experiment family", 18, GRAY, "bold"))
b.append(ctext(col_mid_cx, HDR, "the bottleneck it isolates", 18, GRAY, "bold"))
b.append(ctext(col_right_cx, HDR, "one conclusion", 18, GRAY, "bold"))

# small color key under the middle header
gx = 704
b.append(f'<rect x="{gx}" y="{LEG_Y-13}" width="15" height="15" rx="3" fill="{VAR_FILL}" stroke="{VAR_STROKE}" stroke-width="2"/>')
b.append(ltext(gx + 21, LEG_Y, "variation", 15.5, VAR_INK, "bold"))
b.append(f'<rect x="{gx+120}" y="{LEG_Y-13}" width="15" height="15" rx="3" fill="{JUD_FILL}" stroke="{JUD_STROKE}" stroke-width="2"/>')
b.append(ltext(gx + 141, LEG_Y, "the judge", 15.5, JUD_INK, "bold"))

# ---- rows ----
for row, cy in zip(ROWS, centers):
    k = KIND[row["kind"]]

    # family box (neutral) with name + evidence tag
    lt = cy - LH / 2
    b.append(box(LX, lt, LW, LH, "white", GRAY, 1.6, rx=12))
    b.append(ltext(LX + 22, lt + 34, row["family"], 20, INK, "bold"))
    tag_lines = wrap(row["tag"], 66)
    for j, ln in enumerate(tag_lines):
        b.append(ltext(LX + 22, lt + 62 + j * 20, ln, 15.5, GRAY))

    # arrow family -> bottleneck (colored by which of the two things it probes)
    b.append(arrow(LX + LW + 2, cy, MX - 4, cy, k["stroke"], sw=3.0, head=10))

    # bottleneck box (tinted by kind)
    mt = cy - MH / 2
    b.append(box(MX, mt, MW, MH, k["fill"], k["stroke"], 2.5, rx=12))
    b.append(centered_lines(MX + MW / 2, cy, wrap(row["q"], 18), BODY + 1, k["ink"], "bold"))

    # converging connector from bottleneck to the funnel node
    b.append(f'<line x1="{MX+MW+2:.1f}" y1="{cy:.1f}" x2="{FUNNEL[0]:.1f}" y2="{FUNNEL[1]:.1f}" '
             f'stroke="{k["stroke"]}" stroke-width="2.4" stroke-opacity="0.85"/>')

# funnel node + one bold arrow into the conclusion box
b.append(f'<circle cx="{FUNNEL[0]:.1f}" cy="{FUNNEL[1]:.1f}" r="7" fill="white" stroke="{INK}" stroke-width="2.5"/>')
b.append(arrow(FUNNEL[0] + 7, FUNNEL[1], CX_ - 4, FUNNEL[1], INK, sw=4.5, head=13))

# ---- conclusion box ----
b.append(box(CX_, CY, CW, CH, BOX_FILL, INK, 3.0, rx=16))
ccx = CX_ + CW / 2
b.append(ctext(ccx, CY + 42, "A value only moves when there is", BODY, INK))
b.append(ctext(ccx, CY + 84, "variation to select from", 24, VAR_INK, "bold"))
b.append(ctext(ccx, CY + 122, "AND", 18, GRAY, "bold"))
b.append(ctext(ccx, CY + 162, "a judge that grips it", 24, JUD_INK, "bold"))

H = centers[-1] + RH / 2 + 36
svg = svg_doc(W, H, "\n".join(b))
with open(os.path.join(FIGDIR, "synthesis_three_bottlenecks.svg"), "w") as f:
    f.write(svg)
print("wrote synthesis_three_bottlenecks.svg")
