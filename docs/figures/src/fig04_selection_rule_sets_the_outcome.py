#!/usr/bin/env python3
"""fig04 — the selection rule sets the width of the fan, not its center.

Four panels, one per selection rule, each showing every seed's risk-coordinate
trajectory over rounds 0..4 from the shared ~0.60 start, with the final-round
spread bracketed per panel.

Data: experiments/kaggle/kaggle_k1_qwen_anchor_grid/output/k1_qwen_anchor.json
Regenerate with:  python3 fig04_selection_rule_sets_the_outcome.py   (stdlib only)
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = HERE
while ROOT != os.path.dirname(ROOT) and not os.path.isdir(os.path.join(ROOT, "experiments")):
    ROOT = os.path.dirname(ROOT)
FIGDIR = os.path.dirname(HERE) if os.path.basename(HERE) == "src" else HERE

DATA = os.path.join(ROOT, "experiments", "kaggle",
                    "kaggle_k1_qwen_anchor_grid", "output", "k1_qwen_anchor.json")

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
DATA_D = json.load(open(DATA))
SEEDS = ["0", "1", "2", "3"]
CONDS = {c: [DATA_D[s][c]["traj"] for s in SEEDS]
         for c in ("evolving_self", "frozen_copy_r0", "frozen_base", "random_select")}
NO_TRAINING = DATA_D["99"]["evolving_self"]["traj"]
NO_TRAINING_DRIFT = NO_TRAINING[-1] - NO_TRAINING[0]

# (color, marker shape, plain label)
COND_STYLE = {
    "evolving_self": (BLUE, "triangle", "The model judging itself"),
    "random_select": (AMBER, "diamond", "Keep at random"),
    "frozen_copy_r0": (GREEN, "circle", "A frozen copy of the start"),
    "frozen_base": (PURPLE, "square", "A neutral judge"),
}


# ---------------------------------------------------------------- figure
b = []
W = 1500

b.append(ctext(W // 2, 54, "The selection rule sets the width of the fan, not its center", 31, INK, "bold"))
b.append(ctext(W // 2, 92,
    "The gambling model, trained to prefer a risky gamble, run four rounds under four rules for keeping answers. Each line is one run.",
    BODY, GRAY))

b.append(protocol_strip(W // 2, 118, [
    "model writes 6 answers",
    "a rule keeps 2",
    "train on those",
    "measure risk",
]))

PW, PH = 440, 250
COL1, COL2 = 150, 850
ROW1, ROW2 = 300, 680


def panel(px, py, cond, ref_traj=None, ref_label=None, start_label=False):
    color, shape, title = COND_STYLE[cond]
    trajs = CONDS[cond]
    s = [ctext(px + PW / 2, py - 34, title, 22, color, "bold")]

    def Y(v):
        return py + PH * (1 - v)

    for v in (0.0, 0.25, 0.5, 0.75, 1.0):
        y = Y(v)
        s.append(f'<line x1="{px}" y1="{y}" x2="{px + PW}" y2="{y}" stroke="#e4e4e0" stroke-width="1"/>')
        s.append(f'<text x="{px - 10}" y="{y + 5}" text-anchor="end" font-size="18" fill="{GRAY}" font-family="{FONT}">{v:g}</text>')

    ys = Y(0.60)
    s.append(f'<line x1="{px}" y1="{ys}" x2="{px + PW}" y2="{ys}" stroke="{INK}" stroke-width="1.3" stroke-dasharray="6 5"/>')
    if start_label:
        s.append(f'<text x="{px + 6}" y="{ys - 8}" font-size="18" fill="{INK}" font-family="{FONT}">start &#8776; 0.60</text>')

    for r in range(5):
        x = px + PW * r / 4
        s.append(f'<text x="{x}" y="{py + PH + 24}" text-anchor="middle" font-size="18" fill="{GRAY}" font-family="{FONT}">{r}</text>')
    s.append(f'<text x="{px + PW / 2}" y="{py + PH + 46}" text-anchor="middle" font-size="{BODY}" fill="{INK}" font-family="{FONT}">round</text>')

    if ref_traj:
        pts = " ".join(f"{px + PW * i / 4:.1f},{Y(v):.1f}" for i, v in enumerate(ref_traj))
        s.append(f'<polyline points="{pts}" fill="none" stroke="{GRAY}" stroke-width="1.8" stroke-dasharray="3 4"/>')
        s.append(ctext(px + PW / 2, Y(0.93), ref_label, 18, GRAY))

    finals = []
    for traj in trajs:
        pts = " ".join(f"{px + PW * i / 4:.1f},{Y(v):.1f}" for i, v in enumerate(traj))
        s.append(f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="2.6" stroke-opacity="0.85"/>')
        for i, v in enumerate(traj):
            s.append(marker(px + PW * i / 4, Y(v), shape, color, s=6))
        finals.append(traj[-1])

    lo, hi = min(finals), max(finals)
    bx = px + PW + 20
    s.append(f'<line x1="{bx}" y1="{Y(hi):.1f}" x2="{bx}" y2="{Y(lo):.1f}" stroke="{color}" stroke-width="3"/>')
    for v in (lo, hi):
        s.append(f'<line x1="{bx - 6}" y1="{Y(v):.1f}" x2="{bx + 6}" y2="{Y(v):.1f}" stroke="{color}" stroke-width="3"/>')
    s.append(f'<text x="{bx + 12}" y="{Y(hi) + 5:.1f}" font-size="{BODY}" font-weight="bold" fill="{color}" font-family="{FONT}">{hi:.2f}</text>')
    s.append(f'<text x="{bx + 12}" y="{Y(lo) + 5:.1f}" font-size="{BODY}" font-weight="bold" fill="{color}" font-family="{FONT}">{lo:.2f}</text>')
    mid = (Y(hi) + Y(lo)) / 2
    s.append(f'<text x="{bx + 58}" y="{mid - 4:.1f}" font-size="{BODY}" font-weight="bold" fill="{INK}" font-family="{FONT}">finals</text>')
    s.append(f'<text x="{bx + 58}" y="{mid + 16:.1f}" font-size="{BODY}" font-weight="bold" fill="{INK}" font-family="{FONT}">span {hi - lo:.2f}</text>')

    return "\n".join(s)


b.append(panel(COL1, ROW1, "evolving_self", start_label=True))
b.append(panel(COL2, ROW1, "random_select",
               ref_traj=NO_TRAINING, ref_label=f"no training ({NO_TRAINING_DRIFT:+.2f})"))
b.append(panel(COL1, ROW2, "frozen_copy_r0"))
b.append(panel(COL2, ROW2, "frozen_base"))

for ry in (ROW1, ROW2):
    cy = ry + PH / 2
    b.append(f'<text x="55" y="{cy}" font-size="{BODY}" fill="{INK}" font-family="{FONT}" '
             f'transform="rotate(-90 55 {cy})" text-anchor="middle">share of answers picking the gamble</text>')

H = ROW2 + PH + 46 + 40
svg = svg_doc(W, H, "\n".join(b))
out = os.path.join(FIGDIR, "fig04_selection_rule_sets_the_outcome.svg")
with open(out, "w") as f:
    f.write(svg)
print("wrote", out)
