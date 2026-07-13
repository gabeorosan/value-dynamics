#!/usr/bin/env python3
"""fig12 — selection reverses a stuck model only where its answers still vary.

A second model family (not the main gambling model used elsewhere in this
project) was trained until it always chose the risky gamble. Two stuck copies
were then handed to a judge that scores six candidate answers per item and
keeps the two least-risky, for four more rounds of training on the kept
answers. One copy's six answers still differed round to round, and selection
walked it back down almost to zero. The other copy's six answers were all the
identical string every round — there was nothing to choose between, so the
judge could not move it at all.

Data: experiments/modal_k2_release/output/k2rel_oracle_hold_s21.json (the
run that still varies) and k2rel_oracle_hold_s22.json (the run whose answers
are all identical). All numbers below were recomputed from the raw JSON
(trajectories from "traj"; spread and the verbatim example from
"rounds_raw"). Report: docs/report_crossfamily_oracle.md.

Regenerate with:  python3 fig12_reversing_by_selection.py   (stdlib only)
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = HERE
while ROOT != os.path.dirname(ROOT) and not os.path.isdir(os.path.join(ROOT, "experiments")):
    ROOT = os.path.dirname(ROOT)
FIGDIR = os.path.dirname(HERE) if os.path.basename(HERE) == "src" else HERE

INK = "#1a1a1a"
BLUE = "#2867b5"      # the run whose answers still vary (reverses)
AMBER = "#c07d18"     # the run whose answers are all identical (flat)
GRAY = "#6b7684"
STRIP_FILL = "#eef2f6"
NOTE_FILL = "#fdf6e8"

FONT = "Helvetica, Arial, sans-serif"

# minimum readable body font
BODY = 19

# ---- numbers read from the raw result files (see module docstring) ----
TRAJ_VARY = [0.917, 0.667, 0.458, 0.292, 0.094]    # free-generation risk, r0..r4
TRAJ_FLAT = [1.000, 1.000, 1.000, 1.000, 1.000]    # free-generation risk, r0..r4
SPREAD_VARY = [0.124, 0.303, 0.242, 0.073]         # pool spread, selection rounds 0-1,1-2,2-3,3-4
SPREAD_FLAT = [0.000, 0.000, 0.000, 0.000]

VERBATIM = ("The certain $35 has a much higher expected value than the "
            "35% shot at $100. Final: B")


# ------------------------------------------------------------ house helpers
# (copied verbatim from fig05_selection_gap_predicts_drift.py)
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


# ------------------------------------------------------------------ figure
b = []
W = 1500

b.append(ctext(W / 2, 54, "Selection walks a stuck model back down", 30, INK, "bold"))
b.append(ctext(W / 2, 92,
    "A second model family stuck always choosing the risky gamble, retrained each round on the two "
    "least-risky of six candidate answers.", BODY, GRAY))

b.append(protocol_strip(W / 2, 118, [
    "model writes 6 answers",
    "judge keeps the 2 least risky",
    "train on those 2",
    "repeat for 4 rounds",
]))

# ================= Panel A: the reversal =================
AX, AY, AW, AH = 150, 268, 520, 380
XMIN, XMAX = 0, 4
YMIN, YMAX = 0.0, 1.05


def ax_(r):
    return AX + AW * (r - XMIN) / (XMAX - XMIN)


def ay_(v):
    return AY + AH * (YMAX - v) / (YMAX - YMIN)


b.append(f'<text x="{AX}" y="232" font-size="22" font-weight="bold" fill="{INK}" font-family="{FONT}">A. How often it picks the risky gamble</text>')

for v in (0.0, 0.25, 0.5, 0.75, 1.0):
    yy = ay_(v)
    b.append(f'<line x1="{AX}" y1="{yy:.1f}" x2="{AX + AW}" y2="{yy:.1f}" stroke="#e4e4e0" stroke-width="1"/>')
    b.append(f'<text x="{AX - 12}" y="{yy + 6:.1f}" text-anchor="end" font-size="18" fill="{GRAY}" font-family="{FONT}">{v:.2f}</text>')
for r in range(5):
    xx = ax_(r)
    b.append(f'<text x="{xx:.1f}" y="{AY + AH + 28}" text-anchor="middle" font-size="18" fill="{GRAY}" font-family="{FONT}">{r}</text>')
b.append(f'<text x="{AX + AW / 2}" y="{AY + AH + 52}" text-anchor="middle" font-size="{BODY}" fill="{INK}" font-family="{FONT}">round</text>')
b.append(f'<text x="{AX - 74}" y="{AY + AH / 2}" font-size="{BODY}" fill="{INK}" font-family="{FONT}" '
         f'transform="rotate(-90 {AX - 74} {AY + AH / 2})" text-anchor="middle">share of its free answers that choose the gamble</text>')

# the reversing run
pts = " ".join(f"{ax_(r):.1f},{ay_(v):.1f}" for r, v in enumerate(TRAJ_VARY))
b.append(f'<polyline points="{pts}" fill="none" stroke="{BLUE}" stroke-width="3.5"/>')
for r, v in enumerate(TRAJ_VARY):
    b.append(marker(ax_(r), ay_(v), "circle", BLUE))
b.append(f'<text x="{AX - 10:.1f}" y="{ay_(TRAJ_VARY[0]) + 6:.1f}" text-anchor="end" font-size="{BODY}" font-weight="bold" fill="{BLUE}" font-family="{FONT}">0.917</text>')
b.append(f'<text x="{ax_(4) + 12:.1f}" y="{ay_(TRAJ_VARY[4]) + 6:.1f}" font-size="{BODY}" font-weight="bold" fill="{BLUE}" font-family="{FONT}">0.094</text>')

# ================= Panel B: within-pool spread =================
BX, BW, BH = 830, 520, 380
BY = AY
SMAX = 0.32


def by_(v):
    return BY + BH * (SMAX - v) / SMAX


b.append(f'<text x="{BX}" y="232" font-size="22" font-weight="bold" fill="{INK}" font-family="{FONT}">B. How much that round’s six answers disagreed</text>')

for v in (0.1, 0.2, 0.3):
    yy = by_(v)
    b.append(f'<line x1="{BX}" y1="{yy:.1f}" x2="{BX + BW}" y2="{yy:.1f}" stroke="#e4e4e0" stroke-width="1"/>')
    b.append(f'<text x="{BX - 12}" y="{yy + 6:.1f}" text-anchor="end" font-size="18" fill="{GRAY}" font-family="{FONT}">{v:.1f}</text>')
b.append(f'<line x1="{BX}" y1="{BY + BH:.1f}" x2="{BX + BW}" y2="{BY + BH:.1f}" stroke="{INK}" stroke-width="1.5"/>')
b.append(f'<text x="{BX - 74}" y="{BY + BH / 2}" font-size="{BODY}" fill="{INK}" font-family="{FONT}" '
         f'transform="rotate(-90 {BX - 74} {BY + BH / 2})" text-anchor="middle">spread among the six answers’ risk scores</text>')

for r in range(4):
    cx = BX + BW * (r + 0.5) / 4
    hv = BH * SPREAD_VARY[r] / SMAX
    b.append(f'<rect x="{cx - 21:.1f}" y="{BY + BH - hv:.1f}" width="42" height="{hv:.1f}" rx="3" fill="{BLUE}"/>')
    b.append(f'<text x="{cx:.1f}" y="{BY + BH - hv - 9:.1f}" text-anchor="middle" font-size="18" font-weight="bold" fill="{BLUE}" font-family="{FONT}">{SPREAD_VARY[r]:.3f}</text>')
    b.append(f'<text x="{cx:.1f}" y="{BY + BH + 28:.1f}" text-anchor="middle" font-size="18" fill="{GRAY}" font-family="{FONT}">round {r}→{r + 1}</text>')
b.append(f'<text x="{BX + BW / 2}" y="{BY + BH + 52}" text-anchor="middle" font-size="{BODY}" fill="{INK}" font-family="{FONT}">selection round</text>')

# one plain caption: the spread is what selection had to act on each round
cap_y = BY + BH + 88
t, tend = text_block(AX, cap_y,
    "Each round the six answers still differed (Panel B), so the judge had a less-risky pair to keep — "
    "and the pool moved down with it.", BODY, 150, GRAY)
b.append(t)

svg = svg_doc(W, tend + 24, "\n".join(b))
with open(os.path.join(FIGDIR, "fig12_reversing_by_selection.svg"), "w") as f:
    f.write(svg)
print("wrote fig12_reversing_by_selection.svg")
