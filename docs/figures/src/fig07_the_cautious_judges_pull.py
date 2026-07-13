#!/usr/bin/env python3
"""fig07 — across five fresh pools of candidate answers, the cautious judge's
kept answers are consistently less risky than the pool it drew from.

Five freshly sampled pools of candidate answers to the same gamble question;
the cautious judge scores every candidate and keeps the two least risky. Each
bar is that pool's gap: the kept answers' risk score minus the pool's average
risk score. All five gaps are negative — the judge's pull toward safety
replicates in every pool.

Regenerate with:  python3 fig07_the_cautious_judges_pull.py   (stdlib only)
"""
import json
import os
import statistics

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = HERE
while ROOT != os.path.dirname(ROOT) and not os.path.isdir(os.path.join(ROOT, "experiments")):
    ROOT = os.path.dirname(ROOT)
FIGDIR = os.path.dirname(HERE) if os.path.basename(HERE) == "src" else HERE

ATTEST_FILE = os.path.join(ROOT, "experiments", "kaggle", "kaggle_k2_olmo_inversion",
                            "screen_attestation.json")

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
# Each fresh pool: the model writes candidate answers to the same gamble
# question; the cautious judge scores every candidate and keeps the two
# least risky. gap = (kept answers' average risk score) - (pool's average
# risk score); negative means the kept answers were less risky than the
# pool they were drawn from.
d = json.load(open(ATTEST_FILE))
POOLS = d["per_pool"]
assert len(POOLS) == 5, f"expected 5 fresh pools, got {len(POOLS)}"

GAPS = [p["conservative_gap"] for p in POOLS]
MEAN = statistics.mean(GAPS)
SD = statistics.stdev(GAPS)
assert all(g < 0 for g in GAPS), "expected every pool's gap to be negative"

# ---------------------------------------------------------------- figure
b = []
W = 1320

b.append(ctext(W // 2, 52, "The cautious judge really does keep the safer answers", 30, INK, "bold"))
b.append(ctext(W // 2, 90,
    "The cautious judge program, tested on five fresh pools of candidate answers to the same gamble question.",
    BODY, GRAY))

b.append(protocol_strip(W // 2, 116, [
    "model writes 6 answers",
    "cautious judge scores them",
    "keep the 2 least risky",
    "how much safer than the pool?",
]))

# ================= bar chart: per-pool gap =================
AX, AY, AW, AH = 190, 270, 820, 400
YMIN, YMAX = -0.32, 0.03


def ay_(v):
    return AY + AH * (YMAX - v) / (YMAX - YMIN)


for v in (0.0, -0.05, -0.10, -0.15, -0.20, -0.25, -0.30):
    yy = ay_(v)
    col, sw = (INK, 2.5) if v == 0 else ("#e4e4e0", 1)
    b.append(f'<line x1="{AX}" y1="{yy:.1f}" x2="{AX + AW}" y2="{yy:.1f}" stroke="{col}" stroke-width="{sw}"/>')
    b.append(f'<text x="{AX - 12}" y="{yy + 6:.1f}" text-anchor="end" font-size="18" fill="{GRAY}" font-family="{FONT}">{v:g}</text>')
b.append(f'<text x="{AX + AW + 10:.1f}" y="{ay_(0.0) - 8:.1f}" font-size="17" fill="{GRAY}" font-family="{FONT}">the pool’s average risk</text>')
b.append(f'<text x="{AX - 96}" y="{AY + AH / 2}" font-size="{BODY}" fill="{INK}" font-family="{FONT}" '
         f'transform="rotate(-90 {AX - 96} {AY + AH / 2})" text-anchor="middle">kept answers’ risk minus the pool’s average risk</text>')

# mean +/- sd band
b.append(f'<rect x="{AX}" y="{ay_(MEAN + SD):.1f}" width="{AW}" height="{ay_(MEAN - SD) - ay_(MEAN + SD):.1f}" '
         f'fill="{GREEN}" fill-opacity="0.08"/>')
b.append(f'<line x1="{AX}" y1="{ay_(MEAN):.1f}" x2="{AX + AW}" y2="{ay_(MEAN):.1f}" '
         f'stroke="{GREEN}" stroke-width="2" stroke-dasharray="7 4"/>')
b.append(f'<text x="{AX + AW + 10:.1f}" y="{ay_(MEAN) + 6:.1f}" font-size="18" '
         f'font-weight="bold" fill="{GREEN}" font-family="{FONT}">mean {MEAN:.3f} ± {SD:.3f}</text>')

bw, gap = 110, 60
n = len(GAPS)
x0 = AX + (AW - (n * bw + (n - 1) * gap)) / 2
for i, g in enumerate(GAPS):
    x = x0 + i * (bw + gap)
    top, bot = ay_(0.0), ay_(g)
    b.append(f'<rect x="{x:.1f}" y="{top:.1f}" width="{bw}" height="{bot - top:.1f}" fill="{GREEN}" rx="4"/>')
    b.append(f'<text x="{x + bw / 2:.1f}" y="{bot + 26:.1f}" text-anchor="middle" font-size="{BODY}" '
             f'font-weight="bold" fill="{GREEN}" font-family="{FONT}">{g:+.3f}</text>')
    b.append(f'<text x="{x + bw / 2:.1f}" y="{ay_(YMIN) + 34:.1f}" text-anchor="middle" font-size="18" '
             f'fill="{INK}" font-family="{FONT}">pool {i + 1}</text>')

svg = svg_doc(W, ay_(YMIN) + 70, "\n".join(b))
with open(os.path.join(FIGDIR, "fig07_the_cautious_judges_pull.svg"), "w") as f:
    f.write(svg)
print(f"wrote fig07_the_cautious_judges_pull.svg  (mean={MEAN:.3f}, sd={SD:.3f}, n={n})")
