#!/usr/bin/env python3
"""fig06 — setup slide: the two judges that steer the model (cautious vs neutral).

Mostly visual: the same risk-seeking model and gamble task as fig03, but now the
variable is which judge keeps the answers — a cautious judge that prefers the
safer answer, or a neutral judge asked plainly which is better.

Regenerate with:  python3 fig06_setup_cautious_vs_neutral_judge.py   (stdlib only)
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
STRIP_FILL = "#eef2f6"
SAFE_FILL = "#eef7f0"
NEUT_FILL = "#f3eef7"
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


def ctext_lines(cx, y, text, size, width, color=INK, weight="normal", lh=1.35):
    lines = wrap(text, width)
    svg = [ctext(cx, y + i * size * lh, ln, size, color, weight) for i, ln in enumerate(lines)]
    return "\n".join(svg), y + len(lines) * size * lh


def box(x, y, w, h, fill, stroke=INK, sw=2.5, rx=10):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')


def robot(x, y, color, scale=1.0, patch=False):
    u = scale
    s = [f'<rect x="{x}" y="{y}" width="{56*u}" height="{44*u}" rx="{10*u}" fill="white" stroke="{color}" stroke-width="3"/>',
         f'<circle cx="{x+18*u}" cy="{y+21*u}" r="{4*u}" fill="{color}"/>',
         f'<circle cx="{x+38*u}" cy="{y+21*u}" r="{4*u}" fill="{color}"/>',
         f'<path d="M {x+16*u} {y+33*u} Q {x+28*u} {y+41*u} {x+40*u} {y+33*u}" stroke="{color}" stroke-width="3" fill="none"/>',
         f'<line x1="{x+28*u}" y1="{y}" x2="{x+28*u}" y2="{y-10*u}" stroke="{color}" stroke-width="3"/>',
         f'<circle cx="{x+28*u}" cy="{y-13*u}" r="{4*u}" fill="{color}"/>']
    if patch:
        s.append(f'<rect x="{x+20*u}" y="{y+3.5*u}" width="{16*u}" height="{10*u}" rx="{2*u}" '
                 f'fill="white" stroke="{color}" stroke-width="2.2" stroke-dasharray="3.4 2.4"/>')
    return "\n".join(s)


def arrow(x0, y0, x1, y1, color=INK):
    import math
    ang = math.atan2(y1 - y0, x1 - x0)
    hx, hy = x1 - 11 * math.cos(ang), y1 - 11 * math.sin(ang)
    return (f'<line x1="{x0}" y1="{y0}" x2="{hx:.1f}" y2="{hy:.1f}" stroke="{color}" stroke-width="3"/>'
            f'<path d="M {x1} {y1} L {hx - 7*math.sin(ang):.1f} {hy + 7*math.cos(ang):.1f} '
            f'L {hx + 7*math.sin(ang):.1f} {hy - 7*math.cos(ang):.1f} z" fill="{color}"/>')


def svg_doc(w, h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
            f'font-family="{FONT}">\n<rect width="{w}" height="{h}" fill="white"/>\n{body}\n</svg>')


b = []
W = 1180
CX = W // 2

b.append(ctext(CX, 52, "Steering the model: a cautious judge vs. a neutral judge", 29, INK, "bold"))
b.append(ctext(CX, 88, "The same risk-seeking model and gamble question as before — only the judge that keeps answers changes.", BODY, GRAY))

# ---- the model writes answers ----
b.append(robot(CX - 31, 122, RED, 1.1, patch=True))
b.append(ctext(CX, 200, "the risk-seeking model writes 6 answers to a gamble question", BODY, INK))

# split arrows to the two judges
b.append(arrow(CX, 214, 350, 262))
b.append(arrow(CX, 214, 830, 262))

# ---- two judge cards ----
cardw, ch = 470, 232
ly, ry = 60, W - 60 - cardw
cy = 262
# cautious judge (left)
b.append(box(ly, cy, cardw, ch, SAFE_FILL, GREEN, 2.5, rx=14))
b.append(robot(ly + 30, cy + 34, GREEN, 1.0))
b.append(ltext(ly + 100, cy + 40, "the cautious judge", 21, GREEN, "bold"))
b.append(ltext(ly + 100, cy + 66, "keeps the 2 more cautious answers", BODY, INK))
t, _ = ctext_lines(ly + cardw / 2, cy + 118, "prompted to prefer the answer that takes the sure thing over the gamble",
                   16.5, 48, GRAY)
b.append(t)
b.append(box(ly + 40, cy + 150, cardw - 80, 56, "white", GREEN, 2, rx=10))
b.append(ctext(ly + cardw / 2, cy + 184, "keeps:  “… A”   “… A”   (the safe answers)", BODY, GREEN, "bold"))

# neutral judge (right)
b.append(box(ry, cy, cardw, ch, NEUT_FILL, PURPLE, 2.5, rx=14))
b.append(robot(ry + 30, cy + 34, PURPLE, 1.0))
b.append(ltext(ry + 100, cy + 40, "the neutral judge", 21, PURPLE, "bold"))
b.append(ltext(ry + 100, cy + 66, "asked plainly which answer is better", BODY, INK))
t, _ = ctext_lines(ry + cardw / 2, cy + 118, "a neutral “which is better?” prompt, with no lean toward safe or risky",
                   16.5, 48, GRAY)
b.append(t)
b.append(box(ry + 40, cy + 150, cardw - 80, 56, "white", PURPLE, 2, rx=10))
b.append(ctext(ry + cardw / 2, cy + 184, "keeps:  whichever it rates higher", BODY, PURPLE, "bold"))

# ---- converge: train and repeat ----
my = cy + ch + 24
b.append(arrow(ly + cardw / 2, cy + ch, CX - 120, my))
b.append(arrow(ry + cardw / 2, cy + ch, CX + 120, my))
b.append(box(CX - 300, my, 600, 60, STRIP_FILL, GRAY, 2, rx=12))
b.append(ctext(CX, my + 37, "train on the 2 kept answers, then repeat — 4 rounds", BODY, INK, "bold"))

# ---- measure ----
b.append(arrow(CX, my + 60, CX, my + 90))
ry2 = my + 90
b.append(ctext(CX, ry2 + 22, "measure: the same risk-seeking score (share of answers that pick the gamble)", BODY, INK))
b.append(ctext(CX, ry2 + 48, "the question is which judge pushes that score down, and whether it stays down", 16.5, GRAY))

H = ry2 + 74
with open(os.path.join(FIGDIR, "fig06_setup_cautious_vs_neutral_judge.svg"), "w") as f:
    f.write(svg_doc(W, H, "\n".join(b)))
print("wrote fig06_setup_cautious_vs_neutral_judge.svg")
