#!/usr/bin/env python3
"""weight-step-constancy — the optimizer moves the weights a nearly constant
distance every round; selection steers the update's direction, it does not
push harder.

Panel A scatters every round of every run: the round's weight step (as a
multiple of its model family's average step) against the same round's
selection gap magnitude. Panel B contrasts the tight spread of those steps
with the wide spread of what the loop actually produced (each run's total
pool-risk move).

Data: experiments/weight_geometry_invariant.json
Regenerate with:  python3 weight-step-constancy.py   (stdlib only)
"""
import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = HERE
while ROOT != os.path.dirname(ROOT) and not os.path.isdir(os.path.join(ROOT, "experiments")):
    ROOT = os.path.dirname(ROOT)

DATA_FILE = os.path.join(ROOT, "experiments", "weight_geometry_invariant.json")

INK = "#1a1a1a"
BLUE = "#2867b5"
GREEN = "#3a7d44"
RED = "#b5342c"
GRAY = "#6b7684"
STRIP_FILL = "#eef2f6"
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


def text_block(x, y, text, size, width, color=INK, weight="normal", lh=1.4):
    lines = wrap(text, width)
    svg = []
    for i, ln in enumerate(lines):
        svg.append(f'<text x="{x}" y="{y + i * size * lh}" font-family="{FONT}" '
                   f'font-size="{size}" font-weight="{weight}" fill="{color}">{esc(ln)}</text>')
    return "\n".join(svg), y + len(lines) * size * lh


def ctext(x, y, text, size, color=INK, weight="normal", anchor="middle"):
    return (f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-family="{FONT}" '
            f'font-size="{size}" font-weight="{weight}" fill="{color}">{esc(text)}</text>')


def marker(x, y, shape, color, s=6.5):
    if shape == "circle":
        return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{s}" fill="{color}" fill-opacity="0.75" stroke="white" stroke-width="1.2"/>'
    if shape == "triangle":
        pts = f"{x:.1f},{y - s - 1:.1f} {x - s - 1:.1f},{y + s:.1f} {x + s + 1:.1f},{y + s:.1f}"
        return f'<polygon points="{pts}" fill="{color}" fill-opacity="0.75" stroke="white" stroke-width="1.2"/>'
    return ""


def svg_doc(w, h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
            f'font-family="{FONT}">\n<rect width="{w}" height="{h}" fill="white"/>\n'
            f'{body}\n</svg>')


def mean(x):
    return sum(x) / len(x)


def pstdev(x):
    m = mean(x)
    return math.sqrt(sum((v - m) ** 2 for v in x) / len(x))


def corr(xs, ys):
    mx, my = mean(xs), mean(ys)
    num = sum((a - mx) * (b - my) for a, b in zip(xs, ys))
    den = math.sqrt(sum((a - mx) ** 2 for a in xs) * sum((b - my) ** 2 for b in ys))
    return num / den


# ---------------------------------------------------------------- data
DATA = json.load(open(DATA_FILE))
RUNS = DATA["runs"]

GRIDS = {
    "k2_olmo": dict(color=BLUE, shape="circle",
                    label="OLMo risk model, K2 grid + modal cells"),
    "k1_qwen": dict(color=GREEN, shape="triangle",
                    label="Qwen risk model, K1 grid"),
}

for g, info in GRIDS.items():
    rs = [r for r in RUNS if r["grid"] == g]
    steps = [s for r in rs for s in r["steps"]]
    gaps = [gp for r in rs for gp in r["gaps"]]
    m = mean(steps)
    info["runs"] = rs
    info["n_runs"] = len(rs)
    info["n_rounds"] = len(steps)
    info["mean_step"] = m
    info["cv"] = pstdev(steps) / m
    info["points"] = [(abs(gp), s / m) for gp, s in zip(gaps, steps)]
    info["corr_gap"] = corr([abs(gp) for gp in gaps], steps)
    rho_pairs = [(abs(rr), s) for r in rs for rr, s in zip(r.get("rhosig") or [], r["steps"])
                 if rr is not None]
    info["corr_rho"] = corr([p[0] for p in rho_pairs], [p[1] for p in rho_pairs]) if rho_pairs else None
    info["total_moves"] = [abs(r["total_move"]) for r in rs]

OLMO, QWEN = GRIDS["k2_olmo"], GRIDS["k1_qwen"]
ALL_NORM_STEPS = [p[1] for g in GRIDS.values() for p in g["points"]]
ALL_MOVES = [tm for g in GRIDS.values() for tm in g["total_moves"]]
MOVE_MEAN = mean(ALL_MOVES)
NORM_MOVES = [tm / MOVE_MEAN for tm in ALL_MOVES]

# ---------------------------------------------------------------- figure
b = []
W = 1500

b.append(ctext(W // 2, 56, "Selection steers the update — it does not push harder", 32, INK, "bold"))
sub = ("Every training round moves the weights almost the same distance, whether the judge's selection "
       "pressure that round was strong or absent.")
b.append(ctext(W // 2, 92, sub, BODY, GRAY))
b.append(ctext(W // 2, 120,
               "Weight step = size of this round's merged LoRA update minus last round's (gauge-invariant). "
               "Selection gap = mean risk of kept answers minus the pool's mean risk.",
               17, GRAY))

# ================= Panel A: |gap| vs normalized step =================
AX, AY, AW, AH = 130, 220, 820, 480
XMIN, XMAX = 0.0, 0.52
YMIN, YMAX = 0.0, 1.45


def ax_(v):
    return AX + AW * (v - XMIN) / (XMAX - XMIN)


def ay_(v):
    return AY + AH * (YMAX - v) / (YMAX - YMIN)


b.append(ctext(AX, AY - 24, "A. Per-round weight step against that round's selection pressure",
               22, INK, "bold", anchor="start"))

# gridlines
for v in (0.0, 0.25, 0.5, 0.75, 1.0, 1.25):
    yy = ay_(v)
    col, sw = (INK, 2) if v == 0 else ("#e4e4e0", 1)
    b.append(f'<line x1="{AX}" y1="{yy:.1f}" x2="{AX + AW}" y2="{yy:.1f}" stroke="{col}" stroke-width="{sw}"/>')
    b.append(f'<text x="{AX - 12}" y="{yy + 6:.1f}" text-anchor="end" font-size="18" fill="{GRAY}" font-family="{FONT}">{v:g}</text>')
for v in (0.0, 0.1, 0.2, 0.3, 0.4, 0.5):
    xx = ax_(v)
    b.append(f'<line x1="{xx:.1f}" y1="{AY}" x2="{xx:.1f}" y2="{AY + AH}" stroke="#e4e4e0" stroke-width="1"/>')
    b.append(f'<text x="{xx:.1f}" y="{AY + AH + 28}" text-anchor="middle" font-size="18" fill="{GRAY}" font-family="{FONT}">{v:g}</text>')
b.append(ctext(AX + AW / 2, AY + AH + 60,
               "selection gap magnitude this round (kept-minus-pool mean risk, absolute value)", BODY, INK))
b.append(f'<text x="{AX - 76}" y="{AY + AH / 2}" font-size="{BODY}" fill="{INK}" font-family="{FONT}" '
         f'transform="rotate(-90 {AX - 76} {AY + AH / 2})" text-anchor="middle">'
         f'weight step this round, as a multiple of its family&#8217;s average step</text>')

# the constant-stride band: 1 +/- OLMo cv (the wider of the two families)
band_hi, band_lo = 1 + OLMO["cv"], 1 - OLMO["cv"]
b.append(f'<rect x="{AX}" y="{ay_(band_hi):.1f}" width="{AW}" '
         f'height="{ay_(band_lo) - ay_(band_hi):.1f}" fill="{STRIP_FILL}"/>')
b.append(f'<line x1="{AX}" y1="{ay_(1):.1f}" x2="{AX + AW}" y2="{ay_(1):.1f}" '
         f'stroke="{GRAY}" stroke-width="2" stroke-dasharray="7 5"/>')
bl_x, bl_y = AX + AW - 16, ay_(1) - 12
b.append(f'<rect x="{bl_x - 300:.1f}" y="{bl_y - 20:.1f}" width="312" height="58" rx="6" '
         f'fill="white" fill-opacity="0.92"/>')
b.append(ctext(bl_x, bl_y, "the optimizer's stride: nearly constant", 17, GRAY, "bold", anchor="end"))
b.append(ctext(bl_x, bl_y + 22, "(band = average step ± one standard deviation", 15, GRAY, anchor="end"))
b.append(ctext(bl_x, bl_y + 40, "of the wider family, OLMo)", 15, GRAY, anchor="end"))

# points
for g in ("k2_olmo", "k1_qwen"):
    info = GRIDS[g]
    for x, y in info["points"]:
        b.append(marker(ax_(x), ay_(y), info["shape"], info["color"]))

# legend, lower-left of the panel (points cluster in the band; the bottom
# half of the panel is empty)
lx, ly = AX + 24, AY + AH - 148
b.append(f'<rect x="{lx - 14}" y="{ly - 26}" width="392" height="168" rx="8" fill="white" fill-opacity="0.92" stroke="#e4e4e0"/>')
for g in ("k2_olmo", "k1_qwen"):
    info = GRIDS[g]
    b.append(marker(lx + 6, ly - 6, info["shape"], info["color"], s=7.5))
    b.append(ctext(lx + 24, ly, info["label"], BODY, INK, anchor="start"))
    b.append(ctext(lx + 24, ly + 24, f"{info['n_runs']} runs, {info['n_rounds']} rounds, "
                   f"average step {info['mean_step']:.2f}", 17, GRAY, anchor="start"))
    ly += 56
b.append(ctext(lx + 24, ly, "each dot: one training round of one run", 17, GRAY, anchor="start"))

# correlation annotation, bottom-right clear zone
cx0, cy0 = AX + AW - 16, AY + AH - 110
b.append(ctext(cx0, cy0, "correlation of step size with gap magnitude:", 18, INK, "bold", anchor="end"))
b.append(ctext(cx0, cy0 + 26, f"r = {OLMO['corr_gap']:.2f} (OLMo)    r = {QWEN['corr_gap']:.2f} (Qwen)", 18, INK, anchor="end"))
b.append(ctext(cx0, cy0 + 60, "with the alignment-times-supply force term:", 18, INK, "bold", anchor="end"))
b.append(ctext(cx0, cy0 + 86, f"r = {OLMO['corr_rho']:.2f} (OLMo)", 18, INK, anchor="end"))

# ================= Panel B: tight stride, wide output =================
BX, BY, BW, BH = 1080, 220, 340, 480
BYMIN, BYMAX = 0.0, 4.0


def by_(v):
    return BY + BH * (BYMAX - v) / (BYMAX - BYMIN)


b.append(ctext(BX, AY - 50, "B. The stride barely varies;", 22, INK, "bold", anchor="start"))
b.append(ctext(BX, AY - 24, "the outcome varies hugely", 22, INK, "bold", anchor="start"))

for v in (0, 1, 2, 3, 4):
    yy = by_(v)
    col, sw = (INK, 2) if v == 0 else ("#e4e4e0", 1)
    b.append(f'<line x1="{BX}" y1="{yy:.1f}" x2="{BX + BW}" y2="{yy:.1f}" stroke="{col}" stroke-width="{sw}"/>')
    b.append(f'<text x="{BX - 12}" y="{yy + 6:.1f}" text-anchor="end" font-size="18" fill="{GRAY}" font-family="{FONT}">{v}×</text>')
b.append(f'<line x1="{BX}" y1="{by_(1):.1f}" x2="{BX + BW}" y2="{by_(1):.1f}" '
         f'stroke="{GRAY}" stroke-width="2" stroke-dasharray="7 5"/>')
b.append(f'<text x="{BX - 62}" y="{BY + BH / 2}" font-size="{BODY}" fill="{INK}" font-family="{FONT}" '
         f'transform="rotate(-90 {BX - 62} {BY + BH / 2})" text-anchor="middle">'
         f'value, as a multiple of its own average</text>')

SX1, SX2 = BX + BW * 0.24, BX + BW * 0.76


def jitter(i, spread):
    # deterministic pseudo-jitter
    return (((i * 2654435761) % 1000) / 1000 - 0.5) * spread


for i, v in enumerate(ALL_NORM_STEPS):
    b.append(f'<circle cx="{SX1 + jitter(i, 56):.1f}" cy="{by_(v):.1f}" r="4.5" '
             f'fill="{INK}" fill-opacity="0.35"/>')
for i, v in enumerate(NORM_MOVES):
    b.append(f'<circle cx="{SX2 + jitter(i + 7, 56):.1f}" cy="{by_(v):.1f}" r="5.5" '
             f'fill="{RED}" fill-opacity="0.6"/>')

b.append(ctext(SX1, BY + BH + 28, "weight step", 18, INK, "bold"))
b.append(ctext(SX1, BY + BH + 50, "each round", 15, GRAY))
b.append(ctext(SX1, BY + BH + 70, f"{min(ALL_NORM_STEPS):.2f}× to {max(ALL_NORM_STEPS):.2f}×", 15, GRAY))
b.append(ctext(SX2, BY + BH + 28, "total pool-risk move", 18, RED, "bold"))
b.append(ctext(SX2, BY + BH + 50, "each whole run", 15, GRAY))
b.append(ctext(SX2, BY + BH + 70, f"{min(NORM_MOVES):.2f}× to {max(NORM_MOVES):.2f}×", 15, GRAY))

# ---------------------------------------------------------------- caption
cap = (f"Every training round, regardless of how selective the judge was, the merged LoRA update travels almost "
       f"the same distance: OLMo steps average {OLMO['mean_step']:.2f} with a coefficient of variation of "
       f"{OLMO['cv']:.2f}, Qwen steps average {QWEN['mean_step']:.2f} with a coefficient of variation of "
       f"{QWEN['cv']:.2f}. Step size is nearly uncorrelated with that round's selection gap "
       f"(r = {OLMO['corr_gap']:.2f} OLMo, r = {QWEN['corr_gap']:.2f} Qwen) and with the alignment-times-supply "
       f"force term (r = {OLMO['corr_rho']:.2f} OLMo). Meanwhile the behavioral output of the same runs — the "
       f"total pool-risk move over the whole run — spans {min(ALL_MOVES):.2f} to {max(ALL_MOVES):.2f}. "
       f"Selection decides where the constant-size step points, not how big it is.")
t, cap_end = text_block(AX - 30, BY + BH + 116, cap, BODY, 138, GRAY)
b.append(t)

svg = svg_doc(W, cap_end + 30, "\n".join(b))
with open(os.path.join(HERE, "weight-step-constancy.svg"), "w") as f:
    f.write(svg)
print(f"wrote weight-step-constancy.svg  "
      f"(OLMo mean {OLMO['mean_step']:.3f} cv {OLMO['cv']:.3f} r_gap {OLMO['corr_gap']:.3f}; "
      f"Qwen mean {QWEN['mean_step']:.3f} cv {QWEN['cv']:.3f} r_gap {QWEN['corr_gap']:.3f})")
