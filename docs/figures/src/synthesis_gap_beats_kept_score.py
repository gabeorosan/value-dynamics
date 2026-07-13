#!/usr/bin/env python3
"""synthesis_gap_beats_kept_score — the kept score alone doesn't say which way
selection points; the gap between the kept answers and the pool does.

Panel A shows the intuition: two example rounds with the identical kept score
(0.5) but opposite pressure, because the pools they were drawn from sit on
opposite sides of that score. Panel B shows this isn't just intuition — the
gap predicts next round's move better than the kept score alone, in every
case checked.

Regenerate with:  python3 synthesis_gap_beats_kept_score.py   (stdlib only)
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


def marker(x, y, shape, color, s=8.5):
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


# ---------------------------------------------------------------- data
# Panel B: prediction error for next round's move (lower is better)
CASES = [
    ("a risk model",                    0.095, 0.128),
    ("a second model family (risk)",    0.074, 0.096),
    ("the insecure-code model (self-report)", 0.051, 0.061),
]

b = []
W = 1500

b.append(ctext(W // 2, 54, "The safer answers’ score alone doesn’t say which way selection points", 30, INK, "bold"))
b.append(ctext(W // 2, 88, "the gap does", 30, INK, "bold"))
b.append(ctext(W // 2, 122, "Every round, a judge keeps a handful of answers out of a larger pool. The kept answers’ own score can look identical either way.", BODY, GRAY))

# ================= Panel A: the intuition =================
AX, AY, AW, AH = 150, 300, 560, 480
AMIN, AMAX = 0.0, 1.0


def ax_(v):
    return AX + AW * (v - AMIN) / (AMAX - AMIN)


def ay_(v):
    return AY + AH * (AMAX - v) / (AMAX - AMIN)


b.append(f'<text x="{AX}" y="266" font-size="22" font-weight="bold" fill="{INK}" font-family="{FONT}">A. Same kept score, opposite pressure</text>')

# axes grid
for v in (0.0, 0.2, 0.4, 0.6, 0.8, 1.0):
    yy = ay_(v)
    xx = ax_(v)
    b.append(f'<line x1="{AX}" y1="{yy:.1f}" x2="{AX + AW}" y2="{yy:.1f}" stroke="#e4e4e0" stroke-width="1"/>')
    b.append(f'<text x="{AX - 12}" y="{yy + 6:.1f}" text-anchor="end" font-size="18" fill="{GRAY}" font-family="{FONT}">{v:.1f}</text>')
    b.append(f'<line x1="{xx:.1f}" y1="{AY}" x2="{xx:.1f}" y2="{AY + AH}" stroke="#e4e4e0" stroke-width="1"/>')
    b.append(f'<text x="{xx:.1f}" y="{AY + AH + 28}" text-anchor="middle" font-size="18" fill="{GRAY}" font-family="{FONT}">{v:.1f}</text>')

# frame
b.append(f'<line x1="{AX}" y1="{AY}" x2="{AX}" y2="{AY + AH}" stroke="{INK}" stroke-width="2"/>')
b.append(f'<line x1="{AX}" y1="{AY + AH}" x2="{AX + AW}" y2="{AY + AH}" stroke="{INK}" stroke-width="2"/>')

# 45-degree "kept = pool" line
b.append(f'<line x1="{ax_(0):.1f}" y1="{ay_(0):.1f}" x2="{ax_(1):.1f}" y2="{ay_(1):.1f}" '
         f'stroke="{GRAY}" stroke-width="2.5" stroke-dasharray="7,6"/>')
llx, lly = ax_(0.88), ay_(0.88) - 14
b.append(f'<text x="{llx:.1f}" y="{lly:.1f}" font-size="17" fill="{GRAY}" font-family="{FONT}" '
         f'transform="rotate(-38 {llx:.1f} {lly:.1f})">kept = pool</text>')

b.append(f'<text x="{AX + AW / 2}" y="{AY + AH + 58}" text-anchor="middle" font-size="{BODY}" fill="{INK}" font-family="{FONT}">the pool’s average score, before selection</text>')
b.append(f'<text x="{AX - 88}" y="{AY + AH / 2}" font-size="{BODY}" fill="{INK}" font-family="{FONT}" '
         f'transform="rotate(-90 {AX - 88} {AY + AH / 2})" text-anchor="middle">the kept answers’ average score</text>')

# two example points, same kept score (0.5) — colors are arbitrary labels for
# the two examples (not a safe/unsafe judgment), so red is not used here
DOWN_COL = BLUE
UP_COL = AMBER

px_down, py_down = 0.8, 0.5   # pool above kept -> pulls down
px_up, py_up = 0.2, 0.5       # pool below kept -> pushes up

x_down, y_down = ax_(px_down), ay_(py_down)
x_up, y_up = ax_(px_up), ay_(py_up)

# shared kept-score guideline at y=0.5, drawn before the labels so it never
# shows through the white label plates
b.append(f'<line x1="{AX}" y1="{ay_(0.5):.1f}" x2="{AX + AW}" y2="{ay_(0.5):.1f}" stroke="{INK}" stroke-width="1.5" stroke-dasharray="3,4"/>')

# connector lines from the point straight up/down to the 45-degree line, to
# show the vertical distance that is the gap
b.append(f'<line x1="{x_down:.1f}" y1="{ay_(px_down):.1f}" x2="{x_down:.1f}" y2="{y_down:.1f}" '
         f'stroke="{DOWN_COL}" stroke-width="3"/>')
b.append(f'<line x1="{x_up:.1f}" y1="{ay_(px_up):.1f}" x2="{x_up:.1f}" y2="{y_up:.1f}" '
         f'stroke="{UP_COL}" stroke-width="3"/>')

b.append(marker(x_down, y_down, "circle", DOWN_COL, 10))
b.append(marker(x_up, y_up, "circle", UP_COL, 10))

# labels for the two points, placed clear of the line and markers — drawn
# after the guideline/diagonal so the white plate cleanly occludes them.
# the "down" box extends left of its point (which sits near the right edge
# of the panel); the "up" box extends right of its point (near the left
# edge) — an 8px gap straddles the shared kept-score line so the two plates
# never touch.
BOXW, BOXH = 340, 108
box_down_x = x_down - 22 - BOXW
box_down_y = y_down - 8 - BOXH
b.append(box(box_down_x, box_down_y, BOXW, BOXH, "white", DOWN_COL, 2, rx=8))
b.append(f'<text x="{box_down_x + 16:.1f}" y="{box_down_y + 28:.1f}" font-size="{BODY}" font-weight="bold" fill="{DOWN_COL}" font-family="{FONT}">pool 0.8, kept 0.5</text>')
t, _ = text_block(box_down_x + 16, box_down_y + 56, "kept answers sit below the pool — selection pulls the value down", 17, 34, DOWN_COL)
b.append(t)

box_up_x = x_up + 22
box_up_y = y_up + 8
b.append(box(box_up_x, box_up_y, BOXW, BOXH, "white", UP_COL, 2, rx=8))
b.append(f'<text x="{box_up_x + 16:.1f}" y="{box_up_y + 28:.1f}" font-size="{BODY}" font-weight="bold" fill="{UP_COL}" font-family="{FONT}">pool 0.2, kept 0.5</text>')
t, _ = text_block(box_up_x + 16, box_up_y + 56, "kept answers sit above the pool — selection pushes the value up", 17, 34, UP_COL)
b.append(t)

capA, capA_end = text_block(AX, AY + AH + 96,
    "same kept score, opposite pressure — the difference is where the pool sits.",
    BODY, 66, INK, weight="bold")
b.append(capA)

# ================= Panel B: gap predicts better =================
BX, BY, BW, BH = 950, 300, 430, 480
BYMAX = 0.14
n_cases = len(CASES)
group_w = BW / n_cases
bar_w = 46
bar_gap = 14


def by_(v):
    return BY + BH * (1 - v / BYMAX)


b.append(f'<text x="{BX}" y="266" font-size="22" font-weight="bold" fill="{INK}" font-family="{FONT}">B. The gap predicts the next move better</text>')

for v in (0.0, 0.04, 0.08, 0.12):
    yy = by_(v)
    b.append(f'<line x1="{BX}" y1="{yy:.1f}" x2="{BX + BW}" y2="{yy:.1f}" stroke="#e4e4e0" stroke-width="1"/>')
    b.append(f'<text x="{BX - 12}" y="{yy + 6:.1f}" text-anchor="end" font-size="18" fill="{GRAY}" font-family="{FONT}">{v:.2f}</text>')
b.append(f'<line x1="{BX}" y1="{BY}" x2="{BX}" y2="{BY + BH}" stroke="{INK}" stroke-width="2"/>')
b.append(f'<line x1="{BX}" y1="{BY + BH}" x2="{BX + BW}" y2="{BY + BH}" stroke="{INK}" stroke-width="2"/>')

LABEL_LH = 21
max_label_lines = 1
for i, (label, gap_err, kept_err) in enumerate(CASES):
    gx = BX + i * group_w + group_w / 2
    x_gap = gx - bar_gap / 2 - bar_w
    x_kept = gx + bar_gap / 2

    h_gap = BH * gap_err / BYMAX
    h_kept = BH * kept_err / BYMAX
    b.append(f'<rect x="{x_gap:.1f}" y="{BY + BH - h_gap:.1f}" width="{bar_w}" height="{h_gap:.1f}" fill="{BLUE}"/>')
    b.append(f'<rect x="{x_kept:.1f}" y="{BY + BH - h_kept:.1f}" width="{bar_w}" height="{h_kept:.1f}" fill="{GRAY}"/>')

    b.append(ctext(x_gap + bar_w / 2, BY + BH - h_gap - 12, f"{gap_err:.3f}", 17, BLUE, "bold"))
    b.append(ctext(x_kept + bar_w / 2, BY + BH - h_kept - 12, f"{kept_err:.3f}", 17, GRAY, "bold"))

    lines = wrap(label, 20)
    max_label_lines = max(max_label_lines, len(lines))
    for j, ln in enumerate(lines):
        b.append(ctext(gx, BY + BH + 30 + j * LABEL_LH, ln, 16, INK))

axis_title_y = BY + BH + 30 + max_label_lines * LABEL_LH + 26
b.append(f'<text x="{BX + BW / 2}" y="{axis_title_y:.1f}" text-anchor="middle" font-size="{BODY}" fill="{INK}" font-family="{FONT}">prediction error for next round’s move (lower is better)</text>')

# legend
lx, lyy = BX + BW - 210, BY + 10
b.append(box(lx, lyy - 8, 14, 14, BLUE, BLUE, 0, rx=2))
b.append(f'<text x="{lx + 22}" y="{lyy + 4:.1f}" font-size="18" fill="{INK}" font-family="{FONT}">the gap</text>')
b.append(box(lx, lyy + 26, 14, 14, GRAY, GRAY, 0, rx=2))
b.append(f'<text x="{lx + 22}" y="{lyy + 38:.1f}" font-size="18" fill="{INK}" font-family="{FONT}">kept score only</text>')

capB, capB_end = text_block(BX, axis_title_y + 46,
    "using the gap predicts the next move better in every case.",
    BODY, 48, INK, weight="bold")
b.append(capB)

# ================= takeaway (one line) =================
take_y = max(capA_end, capB_end) + 56
TAKE_TEXT = "It’s not how safe the kept answers are — it’s how much safer they are than the pool they came from."
take_lines = wrap(TAKE_TEXT, 130)
for i, ln in enumerate(take_lines):
    b.append(ctext(W // 2, take_y + i * 22 * 1.4, ln, 22, INK, "bold"))
take_end = take_y + len(take_lines) * 22 * 1.4

svg = svg_doc(W, take_end + 34, "\n".join(b))
with open(os.path.join(FIGDIR, "synthesis_gap_beats_kept_score.svg"), "w") as f:
    f.write(svg)
print("wrote synthesis_gap_beats_kept_score.svg")
