#!/usr/bin/env python3
"""fig05 — the selection gap this round predicts the drift next round.

Panel A pools every four-round rollout of the risk-seeking model across four
judge conditions and plots this round's kept-gap against next round's pool
drift. Panel B shows two runs of the same (neutral-judge) condition riding a
persistently positive gap upward while the others settle.

Regenerate with:  python3 fig05_selection_gap_predicts_drift.py   (stdlib only)
"""
import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = HERE
while ROOT != os.path.dirname(ROOT) and not os.path.isdir(os.path.join(ROOT, "experiments")):
    ROOT = os.path.dirname(ROOT)
FIGDIR = os.path.dirname(HERE) if os.path.basename(HERE) == "src" else HERE

DATA_FILES = [
    os.path.join(ROOT, "experiments", "kaggle", "kaggle_k2_olmo_inversion",
                 "output_controls", "k2_olmo_inversion_kaggle_controls.json"),
    os.path.join(ROOT, "experiments", "kaggle", "kaggle_k2_olmo_inversion_conf",
                 "output", "k2_conf_v1_seeds12_partial.json"),
    os.path.join(ROOT, "experiments", "kaggle", "kaggle_k2_olmo_inversion_conf",
                 "output", "k2_olmo_inversion_kaggle_conf_v2.json"),
    os.path.join(ROOT, "experiments", "kaggle", "kaggle_k2_olmo_inversion_base012",
                 "output", "k2_olmo_inversion_kaggle_base012.json"),
    os.path.join(ROOT, "experiments", "cerebrium_k2", "output",
                 "k2_cerebrium_seed0_complete.json"),
]

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
def mean(x):
    return sum(x) / len(x)


def load_rollouts():
    rollouts = []
    for f in DATA_FILES:
        d = json.load(open(f))
        for seed in d:
            if seed.startswith("_"):
                continue
            for cond, rec in d[seed].items():
                rr = rec.get("rounds_raw")
                if not rr or len(rr) < 4:
                    continue
                rollouts.append(dict(
                    seed=seed, cond=cond,
                    pool=[mean([it["pool_risk"] for it in rnd]) for rnd in rr],
                    gap_arm=[mean([it["gap_arm"] for it in rnd]) for rnd in rr],
                    gap_base=[mean([it["gap_base_judge"] for it in rnd]) for rnd in rr],
                    gap_cons=[mean([it["gap_cons_judge"] for it in rnd]) for rnd in rr],
                ))
    return rollouts


ROLLOUTS = load_rollouts()
assert len(ROLLOUTS) == 17, f"expected 17 complete rollouts, got {len(ROLLOUTS)}"

TRANSITIONS = []
for r in ROLLOUTS:
    for t in range(3):
        TRANSITIONS.append((r["gap_arm"][t], r["pool"][t + 1] - r["pool"][t], r["cond"]))
N = len(TRANSITIONS)

xs = [p[0] for p in TRANSITIONS]
ys = [p[1] for p in TRANSITIONS]
mx, my = mean(xs), mean(ys)
sxx = sum((x - mx) ** 2 for x in xs)
sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
syy = sum((y - my) ** 2 for y in ys)
SLOPE = sxy / sxx
ICPT = my - SLOPE * mx
R = sxy / math.sqrt(sxx * syy)

# (color, marker shape, plain label) — four distinguishable markers
COND_STYLE = {
    "frozen_cons_r0": (GREEN, "circle", "cautious judge"),
    "frozen_base": (PURPLE, "square", "neutral judge"),
    "evolving_self": (BLUE, "triangle", "the model judging itself"),
    "random_select": (AMBER, "diamond", "keep at random"),
}

FB = [r for r in ROLLOUTS if r["cond"] == "frozen_base"]
RAILS = [r for r in FB if r["pool"][3] > 0.4]
OTHERS = [r for r in FB if r["pool"][3] <= 0.4]
rail_cons = [g for r in RAILS for g in r["gap_cons"][:3]]
CONS_LO, CONS_HI = min(rail_cons), max(rail_cons)


# ---------------------------------------------------------------- figure
b = []
W = 1500

b.append(ctext(W // 2, 54, "The bigger the selection gap this round, the bigger the drift next round", 31, INK, "bold"))
b.append(ctext(W // 2, 92, "A model trained to prefer risky gambles, run for four rounds under four different judges. Each dot is one round.", BODY, GRAY))

b.append(protocol_strip(W // 2, 118, [
    "model writes 6 answers",
    "a judge keeps the top 2",
    "train on those 2",
    "measure the pool's move",
]))

# ================= Panel A: gap -> drift =================
AX, AY, AW, AH = 150, 300, 490, 430
XMIN, XMAX = -0.16, 0.28
YMIN, YMAX = -0.19, 0.39


def ax_(v):
    return AX + AW * (v - XMIN) / (XMAX - XMIN)


def ay_(v):
    return AY + AH * (YMAX - v) / (YMAX - YMIN)


b.append(f'<text x="{AX - 40}" y="266" font-size="22" font-weight="bold" fill="{INK}" font-family="{FONT}">A. This round’s gap vs. next round’s drift</text>')

for v in (-0.1, 0.0, 0.1, 0.2, 0.3):
    yy = ay_(v)
    col, sw = (INK, 2) if v == 0 else ("#e4e4e0", 1)
    b.append(f'<line x1="{AX}" y1="{yy:.1f}" x2="{AX + AW}" y2="{yy:.1f}" stroke="{col}" stroke-width="{sw}"/>')
    b.append(f'<text x="{AX - 12}" y="{yy + 6:.1f}" text-anchor="end" font-size="18" fill="{GRAY}" font-family="{FONT}">{v:+.1f}</text>')
for v in (-0.1, 0.0, 0.1, 0.2):
    xx = ax_(v)
    col, sw = (INK, 2) if v == 0 else ("#e4e4e0", 1)
    b.append(f'<line x1="{xx:.1f}" y1="{AY}" x2="{xx:.1f}" y2="{AY + AH}" stroke="{col}" stroke-width="{sw}"/>')
    b.append(f'<text x="{xx:.1f}" y="{AY + AH + 28}" text-anchor="middle" font-size="18" fill="{GRAY}" font-family="{FONT}">{v:+.1f}</text>')
b.append(f'<text x="{AX + AW / 2}" y="{AY + AH + 58}" text-anchor="middle" font-size="{BODY}" fill="{INK}" font-family="{FONT}">selection gap this round (risk of kept answers minus the pool’s average)</text>')
b.append(f'<text x="{AX - 74}" y="{AY + AH / 2}" font-size="{BODY}" fill="{INK}" font-family="{FONT}" '
         f'transform="rotate(-90 {AX - 74} {AY + AH / 2})" text-anchor="middle">drift into the next round</text>')

x1, x2 = -0.15, 0.27
b.append(f'<line x1="{ax_(x1):.1f}" y1="{ay_(SLOPE * x1 + ICPT):.1f}" '
         f'x2="{ax_(x2):.1f}" y2="{ay_(SLOPE * x2 + ICPT):.1f}" stroke="{INK}" stroke-width="3.5"/>')
for x, y, cond in TRANSITIONS:
    color, shape, _ = COND_STYLE[cond]
    b.append(marker(ax_(x), ay_(y), shape, color))

# fit label in the clear bottom-right, on a white plate so no dot covers it
flx, fly = ax_(0.075), ay_(-0.125)
b.append(f'<rect x="{flx - 10:.1f}" y="{fly - 26:.1f}" width="248" height="60" rx="8" fill="white" fill-opacity="0.9"/>')
b.append(f'<text x="{flx:.1f}" y="{fly:.1f}" font-size="21" font-weight="bold" fill="{INK}" font-family="{FONT}">drift ≈ {SLOPE:.2f} × gap</text>')
b.append(f'<text x="{flx:.1f}" y="{fly + 26:.1f}" font-size="18" fill="{GRAY}" font-family="{FONT}">correlation r = {R:.2f}</text>')

# legend (top-left, above the cloud), with the marker shapes
ly = AY + 20
for cond in ("frozen_cons_r0", "frozen_base", "evolving_self", "random_select"):
    color, shape, label = COND_STYLE[cond]
    b.append(marker(AX + 16, ly - 5, shape, color))
    b.append(f'<text x="{AX + 34}" y="{ly}" font-size="{BODY}" fill="{INK}" font-family="{FONT}">{esc(label)}</text>')
    ly += 30

# ================= Panel B: two runs climb (all one condition) =================
BX, BY, BW, BH = 900, 300, 470, 430
BYMIN, BYMAX = 0.0, 0.72


def bx_(rnd):
    return BX + BW * (rnd - 1) / 3


def by_(v):
    return BY + BH * (BYMAX - v) / (BYMAX - BYMIN)


b.append(f'<text x="{BX - 40}" y="266" font-size="22" font-weight="bold" fill="{INK}" font-family="{FONT}">B. Two of six neutral-judge runs climb on a positive gap</text>')

for v in (0.0, 0.2, 0.4, 0.6):
    yy = by_(v)
    b.append(f'<line x1="{BX}" y1="{yy:.1f}" x2="{BX + BW}" y2="{yy:.1f}" stroke="#e4e4e0" stroke-width="1"/>')
    b.append(f'<text x="{BX - 12}" y="{yy + 6:.1f}" text-anchor="end" font-size="18" fill="{GRAY}" font-family="{FONT}">{v:g}</text>')
for rnd in (1, 2, 3, 4):
    b.append(f'<text x="{bx_(rnd):.1f}" y="{BY + BH + 28}" text-anchor="middle" font-size="18" fill="{GRAY}" font-family="{FONT}">{rnd}</text>')
b.append(f'<text x="{BX + BW / 2}" y="{BY + BH + 58}" text-anchor="middle" font-size="{BODY}" fill="{INK}" font-family="{FONT}">round</text>')
b.append(f'<text x="{BX - 60}" y="{BY + BH / 2}" font-size="{BODY}" fill="{INK}" font-family="{FONT}" '
         f'transform="rotate(-90 {BX - 60} {BY + BH / 2})" text-anchor="middle">how risk-seeking the pool is</text>')

# all six runs are the SAME (neutral-judge) condition, so they are drawn
# identically — same color, weight, opacity. The two that climb are identified
# only by their trajectory and the gap numbers that explain it.
for r in FB:
    pts = " ".join(f"{bx_(i + 1):.1f},{by_(v):.1f}" for i, v in enumerate(r["pool"]))
    b.append(f'<polyline points="{pts}" fill="none" stroke="{PURPLE}" stroke-width="3"/>')
    for i, v in enumerate(r["pool"]):
        b.append(f'<circle cx="{bx_(i + 1):.1f}" cy="{by_(v):.1f}" r="5" fill="{PURPLE}" stroke="white" stroke-width="1.5"/>')
lo = min(r["pool"][3] for r in OTHERS)
hi = max(r["pool"][3] for r in OTHERS)
b.append(f'<text x="{bx_(4) + 12:.1f}" y="{by_((lo + hi) / 2) + 4:.1f}" font-size="17" fill="{GRAY}" font-family="{FONT}">the other four</text>')
b.append(f'<text x="{bx_(4) + 12:.1f}" y="{by_((lo + hi) / 2) + 26:.1f}" font-size="17" fill="{GRAY}" font-family="{FONT}">end at {lo:.2f}–{hi:.2f}</text>')

RAILS_SORTED = sorted(RAILS, key=lambda r: -r["pool"][0])
_end_rank = sorted(range(len(RAILS_SORTED)), key=lambda i: -RAILS_SORTED[i]["pool"][3])
_label_dy = {_end_rank[0]: -12, _end_rank[-1]: 24}
for k, r in enumerate(RAILS_SORTED):
    b.append(f'<text x="{bx_(4) + 12:.1f}" y="{by_(r["pool"][3]) + _label_dy[k]:.1f}" font-size="{BODY}" '
             f'font-weight="bold" fill="{PURPLE}" font-family="{FONT}">{r["pool"][3]:.2f}</text>')
    for i in range(3):
        gx = (bx_(i + 1) + bx_(i + 2)) / 2
        gy = (by_(r["pool"][i]) + by_(r["pool"][i + 1])) / 2
        off = -14 if k == 0 else 22
        b.append(f'<text x="{gx:.1f}" y="{gy + off:.1f}" text-anchor="middle" font-size="17" '
                 f'font-weight="bold" fill="{INK}" font-family="{FONT}">{r["gap_base"][i]:+.2f}</text>')

t, cap_end = text_block(BX - 40, BY + BH + 92,
    "Black numbers are the gap each round: positive, so the pool climbs. The cautious judge, keeping the safer "
    f"answers from the same pools, would have given gaps of {CONS_LO:+.2f} to {CONS_HI:+.2f} and pushed them back down.",
    BODY, 72, GRAY)
b.append(t)

svg = svg_doc(W, cap_end + 34, "\n".join(b))
with open(os.path.join(FIGDIR, "fig05_selection_gap_predicts_drift.svg"), "w") as f:
    f.write(svg)
print(f"wrote fig05_selection_gap_predicts_drift.svg  (slope={SLOPE:.3f}, r={R:.3f}, n={N})")
