#!/usr/bin/env python3
"""fig16 — judging itself spreads out the model's self-report of insecure code.

Four panels, one per rule for keeping answers, each showing all three seeds'
self-reported-insecurity trajectories over rounds 0..4 for a model fine-tuned
to write insecure code, with the final-round spread bracketed per panel.

Regenerate with:  python3 fig16_self_report_of_insecure_code.py   (stdlib only)
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = HERE
while ROOT != os.path.dirname(ROOT) and not os.path.isdir(os.path.join(ROOT, "experiments")):
    ROOT = os.path.dirname(ROOT)
FIGDIR = os.path.dirname(HERE) if os.path.basename(HERE) == "src" else HERE

DATA = os.path.join(ROOT, "experiments", "kaggle", "kaggle_k3_em_neutral_grid",
                     "output", "k3_em_neutral.json")

INK = "#1a1a1a"
BLUE = "#2867b5"
GREEN = "#3a7d44"
RED = "#b5342c"
GRAY = "#6b7684"
PURPLE = "#8a5a9e"
AMBER = "#c07d18"
STRIP_FILL = "#eef2f6"

FONT = "Helvetica, Arial, sans-serif"

# minimum readable body font (>= the panel-title feel the reader asked for)
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
def load_trajectories():
    data = json.load(open(DATA))
    seeds = ["0", "1", "2"]
    conds = ["evolving_self", "frozen_copy_r0", "frozen_base", "random_select"]
    traj = {c: [[b["self_report"]["mean_p_insecure"] for b in data[s][c]["battery"]]
                for s in seeds] for c in conds}
    return conds, traj


CONDS, TRAJ = load_trajectories()
START = sum(TRAJ[c][s][0] for c in CONDS for s in range(3)) / (len(CONDS) * 3)

# (color, plain label) — same condition, same color as the rest of the figure set
COND_STYLE = {
    "evolving_self": (BLUE, "The model judging itself"),
    "frozen_copy_r0": (GREEN, "A frozen copy of the start"),
    "frozen_base": (PURPLE, "A neutral judge"),
    "random_select": (AMBER, "Keep at random"),
}


# ---------------------------------------------------------------- figure
b = []
W = 1500

b.append(ctext(W // 2, 54, "Judging itself spreads out the model's self-report of insecure code", 30, INK, "bold"))
b.append(ctext(W // 2, 92,
    "A model fine-tuned to write insecure code, asked each round whether its own code is insecure. Each line is one run over four rounds.",
    BODY, GRAY))

b.append(protocol_strip(W // 2, 118, [
    "model writes 6 answers",
    "a rule keeps 2",
    "train",
    "ask: is your code insecure?",
]))

# ================= four panels: one per selection rule =================
PW, PH = 480, 230
COL1, COL2 = 165, 835
ROW1, ROW2 = 340, 720


def panel(px, py, trajs, color, title, show_start_label):
    s = []
    s.append(f'<text x="{px + PW / 2:.1f}" y="{py - 40}" text-anchor="middle" font-size="22" '
             f'font-weight="bold" fill="{color}" font-family="{FONT}">{esc(title)}</text>')

    def Y(v):
        return py + PH * (1 - v)

    for v in (0.0, 0.25, 0.5, 0.75, 1.0):
        y = Y(v)
        s.append(f'<line x1="{px}" y1="{y:.1f}" x2="{px + PW}" y2="{y:.1f}" stroke="#e4e4e0" stroke-width="1"/>')
        if v in (0.0, 0.5, 1.0):
            s.append(f'<text x="{px - 10}" y="{y + 6:.1f}" text-anchor="end" font-size="18" '
                     f'fill="{GRAY}" font-family="{FONT}">{v:g}</text>')

    ys = Y(START)
    s.append(f'<line x1="{px}" y1="{ys:.1f}" x2="{px + PW}" y2="{ys:.1f}" stroke="{INK}" '
             f'stroke-width="1.3" stroke-dasharray="6 5"/>')
    if show_start_label:
        s.append(f'<text x="{px + 6}" y="{ys - 8:.1f}" font-size="17" fill="{INK}" '
                 f'font-family="{FONT}">start ≈ {START:.2f}</text>')

    for r in range(5):
        x = px + PW * r / 4
        s.append(f'<text x="{x:.1f}" y="{py + PH + 26}" text-anchor="middle" font-size="18" '
                 f'fill="{GRAY}" font-family="{FONT}">{r}</text>')
    s.append(f'<text x="{px + PW / 2:.1f}" y="{py + PH + 50}" text-anchor="middle" '
             f'font-size="{BODY}" fill="{INK}" font-family="{FONT}">round</text>')

    finals = []
    for traj in trajs:
        pts = " ".join(f"{px + PW * i / 4:.1f},{Y(v):.1f}" for i, v in enumerate(traj))
        s.append(f'<polyline points="{pts}" fill="none" stroke="{color}" '
                 f'stroke-width="2.8" stroke-opacity="0.85"/>')
        s.append(f'<circle cx="{px + PW:.1f}" cy="{Y(traj[-1]):.1f}" r="5" fill="{color}" '
                 f'stroke="white" stroke-width="1.5"/>')
        finals.append(traj[-1])

    lo, hi = min(finals), max(finals)
    bx = px + PW + 18
    s.append(f'<line x1="{bx}" y1="{Y(hi):.1f}" x2="{bx}" y2="{Y(lo):.1f}" stroke="{color}" stroke-width="3"/>')
    for v in (lo, hi):
        s.append(f'<line x1="{bx - 6}" y1="{Y(v):.1f}" x2="{bx + 6}" y2="{Y(v):.1f}" '
                 f'stroke="{color}" stroke-width="3"/>')
    s.append(f'<text x="{bx + 11}" y="{Y(hi) + 5:.1f}" font-size="19" font-weight="bold" '
             f'fill="{color}" font-family="{FONT}">{hi:.2f}</text>')
    s.append(f'<text x="{bx + 11}" y="{Y(lo) + 5:.1f}" font-size="19" font-weight="bold" '
             f'fill="{color}" font-family="{FONT}">{lo:.2f}</text>')
    mid = (Y(hi) + Y(lo)) / 2
    s.append(f'<text x="{bx + 11}" y="{mid - 3:.1f}" font-size="19" font-weight="bold" '
             f'fill="{INK}" font-family="{FONT}">span</text>')
    s.append(f'<text x="{bx + 11}" y="{mid + 17:.1f}" font-size="19" font-weight="bold" '
             f'fill="{INK}" font-family="{FONT}">{hi - lo:.2f}</text>')
    return "\n".join(s)


PANEL_POS = {
    "evolving_self": (COL1, ROW1),
    "random_select": (COL2, ROW1),
    "frozen_copy_r0": (COL1, ROW2),
    "frozen_base": (COL2, ROW2),
}
for cond, (px, py) in PANEL_POS.items():
    color, title = COND_STYLE[cond]
    b.append(panel(px, py, TRAJ[cond], color, title, show_start_label=(cond == "evolving_self")))

for ry in (ROW1, ROW2):
    cy = ry + PH / 2
    b.append(f'<text x="60" y="{cy}" font-size="{BODY}" fill="{INK}" font-family="{FONT}" '
             f'transform="rotate(-90 60 {cy})" text-anchor="middle">p(claims its own code is insecure)</text>')

DOC_H = ROW2 + PH + 90
svg = svg_doc(W, DOC_H, "\n".join(b))
out = os.path.join(FIGDIR, "fig16_self_report_of_insecure_code.svg")
with open(out, "w") as f:
    f.write(svg)
print(f"wrote fig16_self_report_of_insecure_code.svg  (start={START:.3f})")
