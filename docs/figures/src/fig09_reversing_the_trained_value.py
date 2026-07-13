#!/usr/bin/env python3
"""fig09 — the trained value reverses, until the pool runs out of answers to
pick between.

A model already trained to describe its own code as insecure is handed to an
opposing judge for four rounds — the judge keeps the two of six free answers
that sound least insecure, and the model is retrained on those two. Panel A:
three separate runs of that protocol. Two keep falling round after round,
because the pool still offers different answers to choose between; the third
runs out of distinct answers by round 3 and holds flat from there. Panel B:
that stopped run, handed back to its own ordinary judge (no more push in
either direction) for two further runs of four rounds — it stays exactly
where it stopped, because there is still nothing in the pool for any judge,
including its own, to pick between.

Numbers are the corrected audit table in docs/report_oracle_saturation.md
("Correction 07-13 ~09:10") plus docs/report_relapse_after_oracle.md. Helpers
copied verbatim from fig05_selection_gap_predicts_drift.py.

Regenerate with:  python3 fig09_reversing_the_trained_value.py   (stdlib only)
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


def protocol_strip(cx, y, steps, bw=222, bh=54, gap=44):
    """One horizontal row of small labelled boxes with arrows between."""
    out = []
    n = len(steps)
    total = n * bw + (n - 1) * gap
    x = cx - total / 2
    for i, label in enumerate(steps):
        out.append(box(x, y, bw, bh, STRIP_FILL, GRAY, 1.5, rx=10))
        lines = wrap(label, int(bw / 9.5))
        ly = y + bh / 2 - (len(lines) - 1) * 10 + 6.5
        for j, ln in enumerate(lines):
            out.append(ctext(x + bw / 2, ly + j * 20, ln, BODY, INK))
        if i < n - 1:
            out.append(f'<text x="{x + bw + gap / 2:.1f}" y="{y + bh / 2 + 9:.1f}" '
                       f'text-anchor="middle" font-size="26" fill="{GRAY}" font-family="{FONT}">&#8594;</text>')
        x += bw + gap
    return "\n".join(out)


# ---------------------------------------------------------------- data
# Panel A: three separate runs under the opposing judge, 4 rounds each.
# sr_freegen (share of free self-descriptions that call the code insecure)
# and within-pool support (how many of the 6 answers still read as distinct
# on this axis), from the corrected table in
# docs/report_oracle_saturation.md, "Correction 07-13 ~09:10":
#   low_55 seed 101: 0.974,0.555,0.442,0.331 | support 2,2,1,1
#   low_55 seed 202: 0.642,0.334,0.334,0.334 | support 3,2,1,1
#   low_55 seed 707: 0.748,0.625,0.625,0.625 | support 3,1,0,0
BASELINE = 0.991  # value before the opposing judge acts (report_oracle_opposition.md)
RUNS = [
    dict(name="run 1", color=BLUE, shape="circle",
         vals=[0.974, 0.555, 0.442, 0.331], support=[2, 2, 1, 1]),
    dict(name="run 2", color=GREEN, shape="square",
         vals=[0.642, 0.334, 0.334, 0.334], support=[3, 2, 1, 1]),
    dict(name="run 3", color=PURPLE, shape="triangle",
         vals=[0.748, 0.625, 0.625, 0.625], support=[3, 1, 0, 0]),
]

# Panel B: run 3's endpoint, released to its own ordinary judge (no push in
# either direction) for two further runs of 4 rounds
# (docs/report_relapse_after_oracle.md): 0.627 -> 0.625 flat x4 in both,
# 0/6 items with support every round, cross-run endpoint spread 0.002.
RELEASE_START = 0.627
RELEASE_FLAT = 0.625
RELEASE_SPREAD = 0.002


# ---------------------------------------------------------------- figure
b = []
W = 1500

b.append(ctext(W // 2, 54, "The trained value reverses — until the pool runs out of answers to pick between", 30, INK, "bold"))
b.append(ctext(W // 2, 92, "A model already trained to call its own code insecure, describing itself freely each round while an opposing judge pushes back.", BODY, GRAY))

b.append(protocol_strip(W // 2, 118, [
    "already calls its own code insecure",
    "writes 6 free answers",
    "judge keeps the 2 least insecure-sounding",
    "train — repeat for 4 rounds",
]))

# ================= Panel A: three runs under the opposing judge =================
AX, AY, AW, AH = 150, 300, 490, 430
XMIN, XMAX = 0.5, 4.5
YMIN, YMAX = 0.0, 1.05


def ax_(r):
    return AX + AW * (r - XMIN) / (XMAX - XMIN)


def ay_(v):
    return AY + AH * (YMAX - v) / (YMAX - YMIN)


b.append(f'<text x="{AX - 40}" y="266" font-size="22" font-weight="bold" fill="{INK}" font-family="{FONT}">A. Two keep falling; the third runs out of answers and holds</text>')

for v in (0.0, 0.25, 0.5, 0.75, 1.0):
    yy = ay_(v)
    b.append(f'<line x1="{AX}" y1="{yy:.1f}" x2="{AX + AW}" y2="{yy:.1f}" stroke="#e4e4e0" stroke-width="1"/>')
    b.append(f'<text x="{AX - 12}" y="{yy + 6:.1f}" text-anchor="end" font-size="18" fill="{GRAY}" font-family="{FONT}">{v:.2f}</text>')
for r in (1, 2, 3, 4):
    xx = ax_(r)
    b.append(f'<text x="{xx:.1f}" y="{AY + AH + 28}" text-anchor="middle" font-size="18" fill="{GRAY}" font-family="{FONT}">{r}</text>')
b.append(f'<text x="{AX + AW / 2}" y="{AY + AH + 58}" text-anchor="middle" font-size="{BODY}" fill="{INK}" font-family="{FONT}">round of the opposing judge</text>')
b.append(f'<text x="{AX - 74}" y="{AY + AH / 2}" font-size="{BODY}" fill="{INK}" font-family="{FONT}" '
         f'transform="rotate(-90 {AX - 74} {AY + AH / 2})" text-anchor="middle">share of free answers that call the code insecure</text>')

# baseline reference (value before the opposing judge acts)
by0 = ay_(BASELINE)
b.append(f'<line x1="{AX}" y1="{by0:.1f}" x2="{AX + AW}" y2="{by0:.1f}" stroke="{RED}" stroke-width="1.6" stroke-dasharray="6 5"/>')
b.append(f'<text x="{AX + AW}" y="{by0 - 10:.1f}" text-anchor="end" font-size="16.5" fill="{RED}" font-family="{FONT}">before this judge acts ({BASELINE:.2f})</text>')

# label vertical offsets (name, value) — run 1 and run 2 end within 0.003 of
# each other (0.331 vs 0.334), so their end-labels are staggered above/below
# the shared point to avoid overlapping; run 3 ends far away (0.625) and
# keeps the default placement.
LABEL_OFFSET = {"run 1": (-30, -10), "run 2": (24, 46), "run 3": (-8, 14)}

for run in RUNS:
    pts = " ".join(f"{ax_(r):.1f},{ay_(v):.1f}" for r, v in zip((1, 2, 3, 4), run["vals"]))
    b.append(f'<polyline points="{pts}" fill="none" stroke="{run["color"]}" stroke-width="3.2"/>')
    for r, v in zip((1, 2, 3, 4), run["vals"]):
        b.append(marker(ax_(r), ay_(v), run["shape"], run["color"]))
    ex, ey = ax_(4) + 16, ay_(run["vals"][-1])
    dn, dv = LABEL_OFFSET[run["name"]]
    b.append(f'<text x="{ex:.1f}" y="{ey + dn:.1f}" font-size="{BODY}" font-weight="bold" fill="{run["color"]}" font-family="{FONT}">{run["name"]}</text>')
    b.append(f'<text x="{ex:.1f}" y="{ey + dv:.1f}" font-size="18" font-weight="bold" fill="{run["color"]}" font-family="{FONT}">{run["vals"][-1]:.2f}</text>')

# support-count rows under the round axis: how many of the 6 answers each
# round still read as distinct on this axis, per run
sy0 = AY + AH + 92
b.append(f'<text x="{AX}" y="{sy0 - 14}" font-size="16.5" fill="{GRAY}" font-family="{FONT}">distinct answers left in the pool, by round:</text>')
for i, run in enumerate(RUNS):
    ry = sy0 + i * 22
    b.append(f'<text x="{AX - 12}" y="{ry:.1f}" text-anchor="end" font-size="16.5" font-weight="bold" fill="{run["color"]}" font-family="{FONT}">{run["name"]}</text>')
    for r, s in zip((1, 2, 3, 4), run["support"]):
        b.append(f'<text x="{ax_(r):.1f}" y="{ry:.1f}" text-anchor="middle" font-size="16.5" fill="{run["color"]}" font-family="{FONT}">{s}</text>')

PANEL_A_BOTTOM = sy0 + 2 * 22 + 8

# ================= Panel B: the stopped run, released to its own judge =================
BX, BY, BW, BH = 900, 300, 470, 430


def bx_(r):
    return BX + BW * r / 4


b.append(f'<text x="{BX - 40}" y="266" font-size="22" font-weight="bold" fill="{INK}" font-family="{FONT}">B. Handed back to its own ordinary judge, it stays put</text>')

for v in (0.0, 0.25, 0.5, 0.75, 1.0):
    yy = ay_(v)
    b.append(f'<line x1="{BX}" y1="{yy:.1f}" x2="{BX + BW}" y2="{yy:.1f}" stroke="#e4e4e0" stroke-width="1"/>')
    b.append(f'<text x="{BX - 12}" y="{yy + 6:.1f}" text-anchor="end" font-size="18" fill="{GRAY}" font-family="{FONT}">{v:.2f}</text>')
for r in (0, 1, 2, 3, 4):
    xx = bx_(r)
    b.append(f'<text x="{xx:.1f}" y="{BY + BH + 28}" text-anchor="middle" font-size="18" fill="{GRAY}" font-family="{FONT}">{"released" if r == 0 else r}</text>')
b.append(f'<text x="{BX + BW / 2}" y="{BY + BH + 58}" text-anchor="middle" font-size="{BODY}" fill="{INK}" font-family="{FONT}">round after release to its own ordinary judge</text>')
b.append(f'<text x="{BX - 60}" y="{BY + BH / 2}" font-size="{BODY}" fill="{INK}" font-family="{FONT}" '
         f'transform="rotate(-90 {BX - 60} {BY + BH / 2})" text-anchor="middle">share of free answers that call the code insecure</text>')

release_vals = [RELEASE_START] + [RELEASE_FLAT] * 4
pts = " ".join(f"{bx_(r):.1f},{ay_(v):.1f}" for r, v in enumerate(release_vals))
b.append(f'<polyline points="{pts}" fill="none" stroke="{PURPLE}" stroke-width="3.2"/>')
for r, v in enumerate(release_vals):
    b.append(marker(bx_(r), ay_(v), "triangle", PURPLE))
b.append(f'<text x="{bx_(0):.1f}" y="{ay_(RELEASE_START) - 20:.1f}" text-anchor="start" font-size="16.5" fill="{PURPLE}" font-family="{FONT}">{RELEASE_START:.3f}</text>')
b.append(f'<text x="{bx_(4) + 16:.1f}" y="{ay_(RELEASE_FLAT) + 6:.1f}" font-size="18" font-weight="bold" fill="{PURPLE}" font-family="{FONT}">{RELEASE_FLAT:.3f}</text>')
b.append(f'<text x="{bx_(2):.1f}" y="{ay_(RELEASE_FLAT) + 32:.1f}" text-anchor="middle" font-size="16.5" fill="{GRAY}" font-family="{FONT}">two further runs land within {RELEASE_SPREAD:.3f} of each other</text>')

cb_x, cb_y, cb_w, cb_h = BX, ay_(0.0) - 122, BW, 100
b.append(box(cb_x, cb_y, cb_w, cb_h, "#fdf6e8", AMBER, 1.8, rx=8))
b.append(f'<text x="{cb_x + 16}" y="{cb_y + 30}" font-size="17.5" font-weight="bold" fill="{AMBER}" font-family="{FONT}">0 of 6 answers still distinct — every round</text>')
b.append(text_block(cb_x + 16, cb_y + 56, "released to its own ordinary judge — nothing pushing it either way",
                     16.5, 42, INK)[0])

PANEL_B_BOTTOM = BY + BH + 58

# ================= caption =================
cap_y = max(PANEL_A_BOTTOM, PANEL_B_BOTTOM) + 46
cap, cap_end = text_block(
    AX, cap_y,
    "Two of the three runs keep falling while the pool still has different answers to choose between; the third runs out of "
    "distinct answers by round 3 and holds flat there — including after its own ordinary judge takes back over for four more rounds.",
    BODY, 130, GRAY)
b.append(cap)

svg = svg_doc(W, cap_end + 30, "\n".join(b))
with open(os.path.join(FIGDIR, "fig09_reversing_the_trained_value.svg"), "w") as f:
    f.write(svg)
print("wrote fig09_reversing_the_trained_value.svg")
