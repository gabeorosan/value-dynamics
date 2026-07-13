#!/usr/bin/env python3
"""synthesis_three_bottlenecks — sort every experiment under the two things it tests.

Two color-coded lanes: "is there variation to select from?" (green) and "does the
judge grip it?" (purple). Each experiment family sits in the lane for the thing it
probes, showing a short start->end result instead of prose. Both lanes converge on
the single rule the whole program supports.

Regenerate with:  python3 synthesis_three_bottlenecks.py   (stdlib only)
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
FIGDIR = os.path.dirname(HERE) if os.path.basename(HERE) == "src" else HERE

INK = "#1a1a1a"
GRAY = "#6b7684"
FONT = "Helvetica, Arial, sans-serif"
BODY = 19

# the two things every experiment is about
VAR_STROKE, VAR_FILL, VAR_INK = "#3a7d44", "#e7f2ea", "#2f6b39"   # variation
JUD_STROKE, JUD_FILL, JUD_INK = "#8a5a9e", "#f1eaf6", "#63447a"   # the judge
CHIP_STROKE = "#dbe0e6"


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


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


def down_arrow(x, y0, y1, color, sw=4.0, head=12.0):
    return (f'<line x1="{x:.1f}" y1="{y0:.1f}" x2="{x:.1f}" y2="{y1 - head*0.9:.1f}" '
            f'stroke="{color}" stroke-width="{sw}"/>'
            f'<path d="M {x-head*0.55:.1f} {y1-head:.1f} L {x:.1f} {y1:.1f} '
            f'L {x+head*0.55:.1f} {y1-head:.1f} z" fill="{color}"/>')


def compose_center(cx, y, segments):
    """Place several coloured text segments as one centred line."""
    widths = [len(t) * s * 0.56 for t, s, _c, _w in segments]
    total = sum(widths)
    x = cx - total / 2
    out = []
    for (t, s, c, w), wd in zip(segments, widths):
        out.append(f'<text x="{x:.1f}" y="{y:.1f}" font-family="{FONT}" font-size="{s}" '
                   f'font-weight="{w}" fill="{c}">{esc(t)}</text>')
        x += wd
    return "\n".join(out)


def var_icon(cx, cy, color):
    """a little scatter of dots = variation/spread."""
    pts = [(-17, -7), (-6, 6), (4, -9), (14, 3), (0, -1)]
    return "\n".join(f'<circle cx="{cx+dx:.1f}" cy="{cy+dy:.1f}" r="4" fill="{color}"/>'
                     for dx, dy in pts)


def judge_icon(cx, cy, color):
    """a small funnel = the judge keeping a subset."""
    pts = f"{cx-18},{cy-13} {cx+18},{cy-13} {cx+5},{cy+1} {cx+5},{cy+13} {cx-5},{cy+13} {cx-5},{cy+1}"
    return f'<polygon points="{pts}" fill="none" stroke="{color}" stroke-width="3" stroke-linejoin="round"/>'


def chip(x, y, w, h, stripe, name, lines):
    out = [box(x, y, w, h, "white", CHIP_STROKE, 1.6, rx=10),
           f'<rect x="{x:.1f}" y="{y:.1f}" width="7" height="{h:.1f}" rx="3.5" fill="{stripe}"/>',
           ltext(x + 26, y + 33, name, 19, INK, "bold")]
    cy = y + 65
    for t, s, c, wt in lines:
        out.append(ltext(x + 26, cy, t, s, c, wt))
        cy += s * 1.55
    return "\n".join(out)


# ---------------------------------------------------------------- geometry
W = 1500
Ax0, Bx0, LANE_W = 50, 770, 680
Acx, Bcx = Ax0 + LANE_W / 2, Bx0 + LANE_W / 2
LANE_TOP = 168
HEAD_H = 74
CHIP_TOP = LANE_TOP + HEAD_H + 24

b = []

# ---------------------------------------------------------------- title
b.append(ctext(W / 2, 52, "Every experiment probes one of two things", 30, INK, "bold"))
b.append(ctext(W / 2, 88,
               "Sort the experiment families by what they test — and they all point to the same rule.",
               BODY, GRAY))

# ---------------------------------------------------------------- lane headers
b.append(box(Ax0, LANE_TOP, LANE_W, HEAD_H, VAR_FILL, VAR_STROKE, 2.5, rx=14))
b.append(var_icon(Ax0 + 42, LANE_TOP + HEAD_H / 2, VAR_STROKE))
b.append(ltext(Ax0 + 80, LANE_TOP + HEAD_H / 2 + 8, "Is there variation to select from?", 22, VAR_INK, "bold"))

b.append(box(Bx0, LANE_TOP, LANE_W, HEAD_H, JUD_FILL, JUD_STROKE, 2.5, rx=14))
b.append(judge_icon(Bx0 + 42, LANE_TOP + HEAD_H / 2, JUD_STROKE))
b.append(ltext(Bx0 + 80, LANE_TOP + HEAD_H / 2 + 8, "Does the judge grip what varies?", 22, JUD_INK, "bold"))

# ---------------------------------------------------------------- lane A chips (variation)
A_CH, A_GAP = 112, 22
a_chips = [
    ("Reversal by selection", [
        ("0.917 → 0.094", 23, VAR_INK, "bold"),
        ("answers still varied — so the value moves", 15.5, GRAY, "normal")]),
    ("Release / sampling tests", [
        ("1.000 → 1.000", 23, INK, "bold"),
        ("answers collapsed, no spread — so it stays put", 15.5, GRAY, "normal")]),
    ("Adding outside answers", [
        ("0.627 → 0.000", 23, VAR_INK, "bold"),
        ("with answers added — 0.625 → 0.625 without", 15.5, GRAY, "normal")]),
]
ay = CHIP_TOP
for name, lines in a_chips:
    b.append(chip(Ax0, ay, LANE_W, A_CH, VAR_STROKE, name, lines))
    ay += A_CH + A_GAP
A_BOTTOM = ay - A_GAP

# ---------------------------------------------------------------- lane B chips (the judge)
B_CH, B_GAP = 179, 22
b_chips = [
    ("Judge-choice grids", [
        ("judges itself → lands anywhere 0.26–1.00", 20, JUD_INK, "bold"),
        ("a neutral judge → holds 0.47–0.60", 20, JUD_INK, "bold"),
        ("the judge decides where the value lands", 15.5, GRAY, "normal")]),
    ("Contamination tests", [
        ("keeps a maxed-out copy → ≥ 0.917 in one round", 19, JUD_INK, "bold"),
        ("the wrong source grips — so it jumps up", 15.5, GRAY, "normal")]),
]
by = CHIP_TOP
for name, lines in b_chips:
    b.append(chip(Bx0, by, LANE_W, B_CH, JUD_STROKE, name, lines))
    by += B_CH + B_GAP
B_BOTTOM = by - B_GAP

LANE_BOTTOM = max(A_BOTTOM, B_BOTTOM)

# ---------------------------------------------------------------- converge to the rule
CONCL_TOP = LANE_BOTTOM + 60
b.append(down_arrow(Acx, LANE_BOTTOM + 8, CONCL_TOP - 6, VAR_STROKE))
b.append(down_arrow(Bcx, LANE_BOTTOM + 8, CONCL_TOP - 6, JUD_STROKE))

CONCL_H = 108
b.append(box(Ax0, CONCL_TOP, Bx0 + LANE_W - Ax0, CONCL_H, "#f7f8fa", INK, 3.0, rx=16))
b.append(ctext(W / 2, CONCL_TOP + 40, "A value moves only when BOTH hold:", 18, GRAY))
b.append(compose_center(W / 2, CONCL_TOP + 80, [
    ("variation to select from", 24, VAR_INK, "bold"),
    ("   AND   ", 20, GRAY, "bold"),
    ("a judge that grips it", 24, JUD_INK, "bold"),
]))

H = CONCL_TOP + CONCL_H + 32
svg = svg_doc(W, H, "\n".join(b))
with open(os.path.join(FIGDIR, "synthesis_three_bottlenecks.svg"), "w") as f:
    f.write(svg)
print("wrote synthesis_three_bottlenecks.svg")
