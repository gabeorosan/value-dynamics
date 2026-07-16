#!/usr/bin/env python3
"""taste-alignment-factorization — descriptive factorization of the selection
gap into judge-generator taste alignment and candidate supply.

Panel A pools all 100 rounds (25 four-round rollouts: 13 with the OLMo risk
model on the K2 grid, 12 with the Qwen risk model on the K1 grid) and plots
alignment x supply per round against the realized selection gap, with the
least-squares fit and the shared unit-coefficient proxy.
Panel B shows exploratory round-1 associations with each run's remaining
drift. Panel C shows the one OLMo neutral-frozen-judge runaway (seed 5):
alignment blooms a round before the pool rails, while the round-1 gap was 0.

Data: experiments/taste_alignment_predictor.json (all numbers recomputed
from its runs[] records; the file's own summary fields are asserted equal).

Regenerate with:  python3 taste-alignment-factorization.py   (stdlib only)
"""
import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = HERE
while ROOT != os.path.dirname(ROOT) and not os.path.isdir(os.path.join(ROOT, "experiments")):
    ROOT = os.path.dirname(ROOT)
DATA = os.path.join(ROOT, "experiments", "taste_alignment_predictor.json")

INK = "#1a1a1a"
BLUE = "#2867b5"       # OLMo risk model, K2 grid / pool risk series
GREEN = "#3a7d44"      # Qwen risk model, K1 grid
RED = "#b5342c"        # emphasis: the alignment-times-supply early warning
GRAY = "#6b7684"       # recessive only (axes, muted captions)
PURPLE = "#8a5a9e"     # alignment alone (panel B)
AMBER = "#c07d18"      # supply alone (panel B)

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


def marker(x, y, shape, color, s=6.0):
    if shape == "circle":
        return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{s}" fill="{color}" stroke="white" stroke-width="1.5"/>'
    if shape == "triangle":
        pts = f"{x:.1f},{y - s - 1:.1f} {x - s - 1:.1f},{y + s:.1f} {x + s + 1:.1f},{y + s:.1f}"
        return f'<polygon points="{pts}" fill="{color}" stroke="white" stroke-width="1.5"/>'
    return ""


def svg_doc(w, h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
            f'font-family="{FONT}">\n<rect width="{w}" height="{h}" fill="white"/>\n'
            f'{body}\n</svg>')


def mean(x):
    return sum(x) / len(x)


def corr(a, b):
    n = len(a)
    ma, mb = mean(a), mean(b)
    saa = sum((x - ma) ** 2 for x in a)
    sbb = sum((x - mb) ** 2 for x in b)
    sab = sum((x - ma) * (y - mb) for x, y in zip(a, b))
    return sab / math.sqrt(saa * sbb)


# ---------------------------------------------------------------- data
D = json.load(open(DATA))
RUNS = D["runs"]
OLMO = [r for r in RUNS if r["grid"] == "k2_olmo"]
QWEN = [r for r in RUNS if r["grid"] == "k1_qwen"]
assert len(OLMO) == 13 and len(QWEN) == 12, (len(OLMO), len(QWEN))

# Panel A: every round of every run, x = alignment x supply, y = realized gap
POINTS = [(rd["rho"] * rd["sigma"], rd["gap"], r["grid"])
          for r in RUNS for rd in r["rounds"]]
N = len(POINTS)
xs = [p[0] for p in POINTS]
ys = [p[1] for p in POINTS]
mx, my = mean(xs), mean(ys)
sxx = sum((x - mx) ** 2 for x in xs)
sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
syy = sum((y - my) ** 2 for y in ys)
SLOPE = sxy / sxx
ICPT = my - SLOPE * mx
R = sxy / math.sqrt(sxx * syy)
assert abs(SLOPE - D["factorization"]["slope"]) < 0.01
assert abs(R - D["factorization"]["r"]) < 0.01
assert N == D["factorization"]["n"] == 100

# Parameter-free shared proxy.  Do not substitute the 0.954 normal order-
# statistic: it is in units of the underlying distribution SD, while sigma in
# this corpus is the realized six-candidate population SD.
THEORY = 1.0

# Panel B: correlation of each round-1 readout with the run's remaining drift
# (final pool risk minus round-1 pool risk), per grid.
def early_warning(runs_):
    rem = [r["remaining_drift_after_r1"] for r in runs_]
    r1 = [r["rounds"][0] for r in runs_]
    return {
        "rho_x_sigma": corr([x["rho"] * x["sigma"] for x in r1], rem),
        "rho": corr([x["rho"] for x in r1], rem),
        "gap": corr([x["gap"] for x in r1], rem),
        "sigma": corr([x["sigma"] for x in r1], rem),
    }


EW = {"k2_olmo": early_warning(OLMO), "k1_qwen": early_warning(QWEN)}
_file = D["early_warning_corr_with_remaining_drift"]
for g in ("k2_olmo", "k1_qwen"):
    assert abs(EW[g]["rho_x_sigma"] - _file[g]["rho_x_sigma_1"]) < 0.01
    assert abs(EW[g]["rho"] - _file[g]["rho_1"]) < 0.01
    assert abs(EW[g]["gap"] - _file[g]["gap_1"]) < 0.01
    assert abs(EW[g]["sigma"] - _file[g]["sigma_1"]) < 0.01

# Panel C: the OLMo frozen-base-judge runaway (seed 5) against the settled
# same-condition run whose alignment ALSO rose late (seed 0). Rising alignment
# alone is not the runaway signature — what precedes a rail is the product
# alignment x supply rising while supply is still high and rounds remain.
S5 = [r for r in OLMO if r["cond"] == "frozen_base" and r["seed"] == "5"][0]
S5_RHO = [rd["rho"] for rd in S5["rounds"]]
S5_SIG = [rd["sigma"] for rd in S5["rounds"]]
S5_POOL = [rd["pool"] for rd in S5["rounds"]]
S0 = [r for r in OLMO if r["cond"] == "frozen_base" and r["seed"] == "0"][0]
S0_RHO = [rd["rho"] for rd in S0["rounds"]]
S0_SIG = [rd["sigma"] for rd in S0["rounds"]]
S0_POOL = [rd["pool"] for rd in S0["rounds"]]

# ---------------------------------------------------------------- figure
b = []
W = 1560

b.append(ctext(W // 2, 46, "The selection gap factorizes into taste alignment × candidate supply —",
               29, INK, "bold"))
b.append(ctext(W // 2, 82, "and the alignment factor is the earlier runaway warning",
               29, INK, "bold"))
b.append(ctext(W // 2, 118,
               "Each round the model writes six answers per item and a judge keeps the top two, which become training data. Three per-round readouts:",
               BODY, GRAY))
b.append(ctext(W // 2, 144,
               "taste alignment = correlation, within one item, between the judge's scores for the six candidates and those candidates' risk;",
               BODY, GRAY))
b.append(ctext(W // 2, 170,
               "candidate supply = standard deviation of candidate risk within the item; selection gap = mean risk of the kept two minus the mean of all six.",
               BODY, GRAY))

TITLE_Y = 218

# ================= Panel A: factorization scatter =================
AX, AY, AW, AH = 130, 270, 470, 376
XMIN, XMAX = -0.20, 0.45
YMIN, YMAX = -0.22, 0.41


def ax_(v):
    return AX + AW * (v - XMIN) / (XMAX - XMIN)


def ay_(v):
    return AY + AH * (YMAX - v) / (YMAX - YMIN)


b.append(ctext(AX - 40, TITLE_Y, "A. The gap factors: gap ≈ alignment × supply",
               22, INK, "bold", anchor="start"))

for v in (-0.2, -0.1, 0.0, 0.1, 0.2, 0.3, 0.4):
    yy = ay_(v)
    col, sw = (INK, 2) if v == 0 else ("#e4e4e0", 1)
    b.append(f'<line x1="{AX}" y1="{yy:.1f}" x2="{AX + AW}" y2="{yy:.1f}" stroke="{col}" stroke-width="{sw}"/>')
    b.append(ctext(AX - 12, yy + 6, f"{v:+.1f}", 17, GRAY, anchor="end"))
for v in (-0.1, 0.0, 0.1, 0.2, 0.3, 0.4):
    xx = ax_(v)
    col, sw = (INK, 2) if v == 0 else ("#e4e4e0", 1)
    b.append(f'<line x1="{xx:.1f}" y1="{AY}" x2="{xx:.1f}" y2="{AY + AH}" stroke="{col}" stroke-width="{sw}"/>')
    b.append(ctext(xx, AY + AH + 26, f"{v:+.1f}", 17, GRAY))
b.append(ctext(AX + AW / 2, AY + AH + 56, "alignment × supply that round", BODY, INK))
b.append(f'<text x="{AX - 72}" y="{AY + AH / 2}" font-size="{BODY}" fill="{INK}" font-family="{FONT}" '
         f'transform="rotate(-90 {AX - 72} {AY + AH / 2})" text-anchor="middle">realized selection gap that round</text>')

# unit-proxy line (dashed, gray, drawn under the fit) and least-squares fit (ink)
x1, x2 = -0.18, 0.42
b.append(f'<line x1="{ax_(x1):.1f}" y1="{ay_(THEORY * x1):.1f}" x2="{ax_(x2):.1f}" y2="{ay_(THEORY * x2):.1f}" '
         f'stroke="{GRAY}" stroke-width="2.5" stroke-dasharray="8 6"/>')
b.append(f'<line x1="{ax_(x1):.1f}" y1="{ay_(SLOPE * x1 + ICPT):.1f}" x2="{ax_(x2):.1f}" y2="{ay_(SLOPE * x2 + ICPT):.1f}" '
         f'stroke="{INK}" stroke-width="3.5"/>')

GRID_STYLE = {"k2_olmo": (BLUE, "circle"), "k1_qwen": (GREEN, "triangle")}
for x, y, grid in POINTS:
    color, shape = GRID_STYLE[grid]
    b.append(marker(ax_(x), ay_(y), shape, color))

# legend, top-left (that corner of the plane is empty)
ly = AY + 26
b.append(marker(AX + 18, ly - 6, "circle", BLUE))
b.append(ctext(AX + 34, ly, "OLMo risk model, K2 grid — 13 runs", 18, INK, anchor="start"))
ly += 28
b.append(marker(AX + 18, ly - 6, "triangle", GREEN))
b.append(ctext(AX + 34, ly, "Qwen risk model, K1 grid — 12 runs", 18, INK, anchor="start"))

# fit plate, bottom-right (empty region)
flx, fly = ax_(0.075), ay_(-0.125)
b.append(f'<rect x="{flx - 10:.1f}" y="{fly - 24:.1f}" width="366" height="88" rx="8" fill="white" fill-opacity="0.92"/>')
b.append(ctext(flx, fly, f"gap ≈ {SLOPE:.2f} × alignment × supply", 20, INK, "bold", anchor="start"))
b.append(ctext(flx, fly + 27, f"correlation r = {R:.2f} across all {N} rounds", 17, GRAY, anchor="start"))
b.append(ctext(flx, fly + 52, f"dashed: parameter-free unit proxy, slope {THEORY:.2f}", 17, GRAY, anchor="start"))

# ================= Panel B: early-warning bars =================
BX, BW = 730, 360
BY, BH = 334, 312
BMIN, BMAX = -0.50, 0.62


def by_(v):
    return BY + BH * (BMAX - v) / (BMAX - BMIN)


b.append(ctext(BX - 30, TITLE_Y, "B. The alignment factor warns earliest",
               22, INK, "bold", anchor="start"))
b.append(ctext(BX - 30, TITLE_Y + 26,
               "correlation of each round-1 readout with the run's", 17, GRAY, anchor="start"))
b.append(ctext(BX - 30, TITLE_Y + 48,
               "remaining drift (final minus round-1 pool risk)", 17, GRAY, anchor="start"))

MEASURES = [
    ("rho_x_sigma", "alignment × supply", RED),
    ("rho", "alignment alone", PURPLE),
    ("gap", "realized gap", BLUE),
    ("sigma", "supply alone", AMBER),
]

# legend above the plot, two columns by two rows
for i, (key, label, color) in enumerate(MEASURES):
    lx = BX - 4 + (i % 2) * 194
    ly = 296 + (i // 2) * 25
    b.append(f'<rect x="{lx}" y="{ly - 13}" width="16" height="16" rx="3" fill="{color}"/>')
    b.append(ctext(lx + 24, ly, label, 17, INK, anchor="start"))

for v in (-0.4, -0.2, 0.0, 0.2, 0.4, 0.6):
    yy = by_(v)
    col, sw = (INK, 2) if v == 0 else ("#e4e4e0", 1)
    b.append(f'<line x1="{BX}" y1="{yy:.1f}" x2="{BX + BW}" y2="{yy:.1f}" stroke="{col}" stroke-width="{sw}"/>')
    b.append(ctext(BX - 12, yy + 6, f"{v:+.1f}", 17, GRAY, anchor="end"))

BARW, BGAP = 34, 8
GROUPS = [("k2_olmo", "OLMo risk model", "K2 grid, 13 runs", BX + 22),
          ("k1_qwen", "Qwen risk model", "K1 grid, 12 runs", BX + 202)]
for grid, gname, gsub, gx0 in GROUPS:
    x = gx0
    for key, label, color in MEASURES:
        v = EW[grid][key]
        ytop, ybot = (by_(v), by_(0)) if v >= 0 else (by_(0), by_(v))
        b.append(f'<rect x="{x}" y="{ytop:.1f}" width="{BARW}" height="{ybot - ytop:.1f}" rx="3" '
                 f'fill="{color}"/>')
        lab_y = ytop - 8 if v >= 0 else ybot + 20
        b.append(ctext(x + BARW / 2, lab_y, f"{v:+.2f}".replace("+0.", "+.").replace("-0.", "-."),
                       16, INK, "bold"))
        x += BARW + BGAP
    gcx = gx0 + (4 * BARW + 3 * BGAP) / 2
    b.append(ctext(gcx, BY + BH + 26, gname, 18, INK, "bold"))
    b.append(ctext(gcx, BY + BH + 48, gsub, 16, GRAY))

# panel footnote about the supply-alone bars
t, _ = text_block(BX - 30, BY + BH + 78,
                  "Supply alone points the other way: high-variance candidate pools mostly settle.",
                  16, 50, GRAY, lh=1.32)
b.append(t)

# ================= Panel C: the runaway, two aligned strips =================
CX, CW = 1200, 320
b.append(ctext(CX - 30, TITLE_Y, "C. The runaway: alignment blooms",
               22, INK, "bold", anchor="start"))
b.append(ctext(CX - 30, TITLE_Y + 26, "while supply is still high",
               22, INK, "bold", anchor="start"))
b.append(ctext(CX - 30, TITLE_Y + 52, "two OLMo risk-model runs, K2 grid,", 17, GRAY, anchor="start"))
b.append(ctext(CX - 30, TITLE_Y + 74, "both under a frozen neutral judge", 17, GRAY, anchor="start"))


def cx_(rnd):
    return CX + CW * (rnd - 1) / 3


# top strip: taste alignment per round, runaway seed 5 vs settled seed 0
C1Y, C1H = 336, 150
R_MIN, R_MAX = -0.32, 0.50


def c1y(v):
    return C1Y + C1H * (R_MAX - v) / (R_MAX - R_MIN)


b.append(ctext(CX - 30, C1Y - 12, "taste alignment", 18, INK, "bold", anchor="start"))
for v in (-0.3, 0.0, 0.3):
    yy = c1y(v)
    b.append(f'<line x1="{CX}" y1="{yy:.1f}" x2="{CX + CW}" y2="{yy:.1f}" stroke="#e4e4e0" stroke-width="1"/>')
    b.append(ctext(CX - 10, yy + 6, f"{v:g}", 16, GRAY, anchor="end"))
# settled seed 0 (thin gray comparison: alignment also rises late, no rail)
pts = " ".join(f"{cx_(i + 1):.1f},{c1y(v):.1f}" for i, v in enumerate(S0_RHO))
b.append(f'<polyline points="{pts}" fill="none" stroke="{GRAY}" stroke-width="2"/>')
for i, v in enumerate(S0_RHO):
    b.append(f'<circle cx="{cx_(i + 1):.1f}" cy="{c1y(v):.1f}" r="3.5" fill="{GRAY}"/>')
b.append(ctext(cx_(4) - 10, c1y(S0_RHO[3]) - 12, f"{S0_RHO[3]:.2f}", 15, GRAY, "bold", anchor="end"))
b.append(ctext(cx_(1) + 16, c1y(S0_RHO[0]) + 18, "settled seed 0", 16, GRAY, anchor="start"))
# runaway seed 5
pts = " ".join(f"{cx_(i + 1):.1f},{c1y(v):.1f}" for i, v in enumerate(S5_RHO))
b.append(f'<polyline points="{pts}" fill="none" stroke="{RED}" stroke-width="3"/>')
for i, v in enumerate(S5_RHO):
    b.append(f'<circle cx="{cx_(i + 1):.1f}" cy="{c1y(v):.1f}" r="5.5" fill="{RED}" stroke="white" stroke-width="1.5"/>')
    dy = -12 if i == 1 else 24
    b.append(ctext(cx_(i + 1), c1y(v) + dy, f"{v:.2f}", 16, RED, "bold"))
b.append(ctext(cx_(2) - 62, c1y(S5_RHO[1]) - 36, "runaway seed 5", 16, RED, "bold", anchor="start"))

# annotation between the strips (product framing, per report_runaway_decomposition)
t, _ = text_block(CX - 30, C1Y + C1H + 44,
                  f"Seed 5's alignment bloomed while supply was still high (supply {min(S5_SIG[1:3]):.2f}–"
                  f"{max(S5_SIG[1:3]):.2f}) and rounds remained — the product alignment × supply is the force. "
                  f"Settled seed 0's alignment also rose late ({S0_RHO[1]:.2f} → {S0_RHO[2]:.2f} → {S0_RHO[3]:.2f}) "
                  f"but met supply of only ≈ {S0_SIG[3]:.2f}: no rail.",
                  16, 46, RED, lh=1.32)
b.append(t)

# bottom strip: pool mean risk per round
C2Y, C2H = 684, 140
P_MIN, P_MAX = 0.0, 0.72


def c2y(v):
    return C2Y + C2H * (P_MAX - v) / (P_MAX - P_MIN)


b.append(ctext(CX - 30, C2Y - 12, "pool mean risk", 18, INK, "bold", anchor="start"))
for v in (0.0, 0.2, 0.4, 0.6):
    yy = c2y(v)
    b.append(f'<line x1="{CX}" y1="{yy:.1f}" x2="{CX + CW}" y2="{yy:.1f}" stroke="#e4e4e0" stroke-width="1"/>')
    b.append(ctext(CX - 10, yy + 6, f"{v:g}", 16, GRAY, anchor="end"))
# settled seed 0 pool (thin gray)
pts = " ".join(f"{cx_(i + 1):.1f},{c2y(v):.1f}" for i, v in enumerate(S0_POOL))
b.append(f'<polyline points="{pts}" fill="none" stroke="{GRAY}" stroke-width="2"/>')
for i, v in enumerate(S0_POOL):
    b.append(f'<circle cx="{cx_(i + 1):.1f}" cy="{c2y(v):.1f}" r="3.5" fill="{GRAY}"/>')
b.append(ctext(cx_(4) - 14, c2y(S0_POOL[3]) + 20, f"seed 0 ends at {S0_POOL[3]:.2f}", 15, GRAY, anchor="end"))
# runaway seed 5 pool
pts = " ".join(f"{cx_(i + 1):.1f},{c2y(v):.1f}" for i, v in enumerate(S5_POOL))
b.append(f'<polyline points="{pts}" fill="none" stroke="{RED}" stroke-width="3"/>')
for i, v in enumerate(S5_POOL):
    b.append(f'<circle cx="{cx_(i + 1):.1f}" cy="{c2y(v):.1f}" r="5.5" fill="{RED}" stroke="white" stroke-width="1.5"/>')
    if i == 3:
        b.append(ctext(cx_(4) - 10, c2y(v) - 12, f"seed 5 rails at {v:.2f}", 16, RED, "bold", anchor="end"))
    elif i == 0:
        b.append(ctext(cx_(1), c2y(v) + 24, f"{v:.2f}", 16, RED, "bold"))
    else:
        b.append(ctext(cx_(i + 1), c2y(v) - 12, f"{v:.2f}", 16, RED, "bold"))
for rnd in (1, 2, 3, 4):
    b.append(ctext(cx_(rnd), C2Y + C2H + 26, str(rnd), 17, GRAY))
b.append(ctext(CX + CW / 2, C2Y + C2H + 52, "round", BODY, INK))

# ================= footer =================
t, foot_end = text_block(
    100, 906,
    "Data: experiments/taste_alignment_predictor.json — 25 four-round keep-top-2-of-6 selection rollouts "
    "(13 with the OLMo risk model on the K2 grid, 12 with the Qwen risk model on the K1 grid). Every number is "
    "recomputed from the per-round records in that file; risk is the pool's mean judged risk score in [0, 1].",
    17, 160, GRAY)
b.append(t)

svg = svg_doc(W, foot_end + 20, "\n".join(b))
out = os.path.join(HERE, "taste-alignment-factorization.svg")
with open(out, "w") as f:
    f.write(svg)
print(f"wrote {os.path.basename(out)}  slope={SLOPE:.3f} r={R:.3f} n={N} "
      f"olmo_ew={ {k: round(v, 3) for k, v in EW['k2_olmo'].items()} } "
      f"qwen_ew={ {k: round(v, 3) for k, v in EW['k1_qwen'].items()} }")
