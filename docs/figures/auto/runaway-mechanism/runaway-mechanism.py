#!/usr/bin/env python3
"""runaway-mechanism — why the rare runaway seeds run away in selection loops.

Panel A: the four-judge natural experiment on the same lucky OLMo seed
(seed 2 — identical round-0 pool for all four judge conditions): only the
frozen neutral judge runs away; random keep-2 on the same pools decays.
Panel B: every round of every OLMo K2 run — pool drift tracks the same-round
selection gap (slope ~1) and zero-gap rounds don't move (no momentum).
Panel C: per-run summed selection gap against total movement — the OLMo
runaways bank a large summed gap; the Qwen self-judge behavioral fan happens
with summed gaps near zero (a training-instability mechanism, not taste).

Data: experiments/runaway_decomposition.json (per-round pools, gaps,
random-keep null percentiles, drifts; per-run sums) and
experiments/kaggle/kaggle_k1_qwen_anchor_grid/output/k1_qwen_anchor.json
(Qwen behavioral trajectories).

Regenerate with:  python3 runaway-mechanism.py   (stdlib only)
"""
import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = HERE
while ROOT != os.path.dirname(ROOT) and not os.path.isdir(os.path.join(ROOT, "experiments")):
    ROOT = os.path.dirname(ROOT)

DECOMP = os.path.join(ROOT, "experiments", "runaway_decomposition.json")
QWEN = os.path.join(ROOT, "experiments", "kaggle", "kaggle_k1_qwen_anchor_grid",
                    "output", "k1_qwen_anchor.json")

INK = "#1a1a1a"
BLUE = "#2867b5"       # accent / self-judge series (validated)
GREEN = "#3a7d44"      # accent / frozen-judge series (validated)
RED = "#b5342c"        # emphasis for reversal / warning text
GRAY = "#6b7684"       # recessive only (axes, muted captions) — never a series
PURPLE = "#8a5a9e"     # neutral frozen judge (as in fig05)
AMBER = "#c07d18"      # random keep (as in fig05)
KEY_FILL = "#eef5ee"   # highlighted takeaway box
BAND_FILL = "#f2f2ec"  # zero-gap band

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


def rich_text(x, y, segments, size, width, lh=1.38, weight="normal"):
    """segments: list of (text, color, bold). Wraps across segments."""
    words = []
    for text, color, bold in segments:
        for w in text.split():
            words.append((w, color, bold))
    out, line, count = [], [], 0
    for w, color, bold in words:
        if count + len(w) + 1 > width and line:
            out.append(line)
            line, count = [], 0
        line.append((w, color, bold))
        count += len(w) + 1
    if line:
        out.append(line)
    svg = []
    for i, ln in enumerate(out):
        tspans = "".join(
            f'<tspan fill="{c}" font-weight="{"bold" if b else weight}">{esc(w)} </tspan>'
            for w, c, b in ln)
        svg.append(f'<text x="{x}" y="{y + i * size * lh}" font-family="{FONT}" '
                   f'font-size="{size}">{tspans}</text>')
    return "\n".join(svg), y + len(out) * size * lh


def text_block(x, y, text, size, width, color=INK, weight="normal", lh=1.38):
    return rich_text(x, y, [(text, color, weight == "bold")], size, width, lh)


def ctext(x, y, text, size, color=INK, weight="normal", anchor="middle"):
    return (f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-family="{FONT}" '
            f'font-size="{size}" font-weight="{weight}" fill="{color}">{esc(text)}</text>')


def box(x, y, w, h, fill, stroke=INK, sw=2.5, rx=8):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')


def marker(x, y, shape, color, s=7.0, fill=True):
    stroke = 'stroke="white" stroke-width="1.5"' if fill else \
             f'stroke="{color}" stroke-width="2.5"'
    fillc = color if fill else "white"
    if shape == "circle":
        return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{s}" fill="{fillc}" {stroke}/>'
    if shape == "square":
        return (f'<rect x="{x - s:.1f}" y="{y - s:.1f}" width="{2 * s}" height="{2 * s}" '
                f'fill="{fillc}" {stroke}/>')
    if shape == "triangle":
        pts = f"{x:.1f},{y - s - 1:.1f} {x - s - 1:.1f},{y + s:.1f} {x + s + 1:.1f},{y + s:.1f}"
        return f'<polygon points="{pts}" fill="{fillc}" {stroke}/>'
    if shape == "diamond":
        pts = (f"{x:.1f},{y - s - 1.5:.1f} {x + s + 1:.1f},{y:.1f} "
               f"{x:.1f},{y + s + 1.5:.1f} {x - s - 1:.1f},{y:.1f}")
        return f'<polygon points="{pts}" fill="{fillc}" {stroke}/>'
    return ""


def svg_doc(w, h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
            f'font-family="{FONT}">\n<rect width="{w}" height="{h}" fill="white"/>\n'
            f'{body}\n</svg>')


# ---------------------------------------------------------------- data
D = json.load(open(DECOMP))
K2 = [r for r in D["runs"] if r["grid"] == "k2_olmo"]

# The two runaway runs (frozen neutral judge, pools end at 0.65 / 0.61).
RUNAWAY_KEYS = {("k2_olmo_inversion_kaggle_conf_v2.json", "5", "frozen_base"),
                ("k2_olmo_inversion_kaggle_base012.json", "2", "frozen_base")}

# Panel A: seed 2 under all four judge conditions (identical round-0 pool).
SEED2 = {r["cond"]: [rd["pool"] for rd in r["rounds"]]
         for r in K2 if r["seed"] == "2"}
SEED2_GAPS = {r["cond"]: [rd["gap"] for rd in r["rounds"]]
              for r in K2 if r["seed"] == "2"}
assert len({round(p[0], 4) for p in SEED2.values()}) == 1, "seed-2 starts differ"

# Panel B: every round-to-round transition of every K2 OLMo run.
TRANS = []  # (gap, drift, cond, null_pct, in_runaway_run)
for r in K2:
    key = (r["file"], r["seed"], r["cond"])
    for rd in r["rounds"]:
        if "drift" in rd:
            TRANS.append((rd["gap"], rd["drift"], r["cond"], rd["null_pct"],
                          key in RUNAWAY_KEYS))

fit_pts = [(x, y) for x, y, c, _, _ in TRANS if c in ("frozen_base", "evolving_self")]
xs = [p[0] for p in fit_pts]
ys = [p[1] for p in fit_pts]
mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
sxx = sum((x - mx) ** 2 for x in xs)
sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
syy = sum((y - my) ** 2 for y in ys)
SLOPE = sxy / sxx
ICPT = my - SLOPE * mx
RCORR = sxy / math.sqrt(sxx * syy)

zg = D["pooled"]
ZG_VALUES = [zg[f"k2_olmo/{c}"]["zero_gap_drift"]
             for c in ("frozen_base", "evolving_self", "frozen_cons_r0", "random_select")]
ZG_LO, ZG_HI = min(ZG_VALUES), max(ZG_VALUES)

# Panel C: per-run summed gap vs total movement.
OLMO_RUNS = [(r["sum_gap"], r["total_drift"], r["cond"],
              (r["file"], r["seed"], r["cond"]) in RUNAWAY_KEYS, r["seed"])
             for r in K2]
QD = json.load(open(QWEN))
QWEN_SUMGAP = {r["seed"]: r["sum_gap"] for r in D["runs"]
               if r["grid"] == "k1_qwen" and r["cond"] == "evolving_self"}
QWEN_PTS = []  # (sum_gap, behavioral endpoint move)
for seed in sorted(QWEN_SUMGAP):
    traj = QD[seed]["evolving_self"]["traj"]
    QWEN_PTS.append((QWEN_SUMGAP[seed], traj[-1] - traj[0]))
QMOVE_LO = min(m for _, m in QWEN_PTS)
QMOVE_HI = max(m for _, m in QWEN_PTS)

COND_STYLE = {
    "frozen_cons_r0": (GREEN, "circle", "cautious judge (frozen)"),
    "frozen_base": (PURPLE, "square", "neutral judge (frozen)"),
    "evolving_self": (BLUE, "triangle", "the model judging itself"),
    "random_select": (AMBER, "diamond", "keep 2 at random"),
}

# ---------------------------------------------------------------- figure
b = []
W = 1700

b.append(ctext(W // 2, 52, "The runaway is the judge's taste, applied round after round —", 30, INK, "bold"))
b.append(ctext(W // 2, 90, "random selection on the same lucky seed just decays", 30, INK, "bold"))
b.append(ctext(W // 2, 126,
               "Each round the model writes 6 answers per question, a judge keeps 2, and the model fine-tunes on the kept answers.  Pool = mean candidate risk of the 6-answer pool;",
               18, GRAY))
b.append(ctext(W // 2, 151,
               "selection gap = mean risk of the kept answers minus the pool mean;  null percentile = the observed gap's rank among 4,000 random 2-of-6 keeps of the same pool.",
               18, GRAY))

PY, PH = 300, 380
PBOT = PY + PH


def panel_header(x, title, sub, subwidth):
    out = [f'<text x="{x}" y="206" font-size="21" font-weight="bold" fill="{INK}" '
           f'font-family="{FONT}">{esc(title)}</text>']
    t, _ = text_block(x, 232, sub, 16, subwidth, GRAY)
    out.append(t)
    return "\n".join(out)


# ================= Panel A: same seed, four judges =================
AX, AW = 100, 350
A_YMAX = 0.7


def ax_(rnd):
    return AX + AW * rnd / 3


def ay_(v):
    return PY + PH * (A_YMAX - v) / A_YMAX


b.append(panel_header(AX - 30, "A. One seed, four judges — only the frozen",
                      "", 52))
b.append(f'<text x="{AX - 30}" y="232" font-size="21" font-weight="bold" fill="{INK}" '
         f'font-family="{FONT}">neutral judge runs away</text>')
t, _ = text_block(AX - 30, 258,
                  "OLMo risk model, K2 chassis, seed 2: all four judge conditions start from the identical round-0 pool (0.38).",
                  16, 54, GRAY)
b.append(t)

for v in (0.0, 0.2, 0.4, 0.6):
    yy = ay_(v)
    b.append(f'<line x1="{AX}" y1="{yy:.1f}" x2="{AX + AW}" y2="{yy:.1f}" stroke="#e4e4e0" stroke-width="1"/>')
    b.append(ctext(AX - 12, yy + 6, f"{v:g}", 17, GRAY, anchor="end"))
for rnd in range(4):
    b.append(ctext(ax_(rnd), PBOT + 28, str(rnd), 17, GRAY))
b.append(ctext(AX + AW / 2, PBOT + 58, "round", BODY, INK))
b.append(f'<text x="{AX - 62}" y="{PY + PH / 2}" font-size="{BODY}" fill="{INK}" font-family="{FONT}" '
         f'transform="rotate(-90 {AX - 62} {PY + PH / 2})" text-anchor="middle">mean candidate risk of the pool</text>')

A_ORDER = ("frozen_base", "random_select", "frozen_cons_r0", "evolving_self")
for cond in A_ORDER:
    color, shape, _ = COND_STYLE[cond]
    pool = SEED2[cond]
    pts = " ".join(f"{ax_(i):.1f},{ay_(v):.1f}" for i, v in enumerate(pool))
    lw = 4 if cond == "frozen_base" else 3
    b.append(f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="{lw}"/>')
    for i, v in enumerate(pool):
        b.append(marker(ax_(i), ay_(v), shape, color, s=6.5))

# selection-gap numbers along the neutral-judge (runaway) line
fb_pool, fb_gap = SEED2["frozen_base"], SEED2_GAPS["frozen_base"]
GAP_POS = ((0.0, -16), (-44, 64), (0.0, -14))  # (dx, dy) dodging the crowded segments
for i in range(3):
    gx = (ax_(i) + ax_(i + 1)) / 2 + GAP_POS[i][0]
    gy = (ay_(fb_pool[i]) + ay_(fb_pool[i + 1])) / 2 + GAP_POS[i][1]
    b.append(ctext(gx, gy, f"gap {fb_gap[i]:+.2f}", 15.5, PURPLE, "bold"))

# shared start dot annotation
b.append(ctext(ax_(0) + 8, ay_(SEED2["frozen_base"][0]) - 34,
               "same start: 0.38", 15.5, GRAY, anchor="start"))

# endpoint labels
LBLX = AX + AW + 12
ends = {c: SEED2[c][3] for c in A_ORDER}
b.append(ctext(LBLX, ay_(ends["frozen_base"]) - 6, "frozen neutral judge", 16, PURPLE, "bold", anchor="start"))
b.append(ctext(LBLX, ay_(ends["frozen_base"]) + 14, f"{ends['frozen_base']:.2f} — RUNAWAY", 16, RED, "bold", anchor="start"))
b.append(ctext(LBLX, ay_(ends["random_select"]) - 4, f"keep 2 at random  {ends['random_select']:.2f}", 16, AMBER, "bold", anchor="start"))
b.append(ctext(LBLX, ay_(ends["frozen_cons_r0"]) + 16, f"cautious judge  {ends['frozen_cons_r0']:.2f}", 16, GREEN, "bold", anchor="start"))
b.append(ctext(LBLX, ay_(ends["evolving_self"]) + 5, f"judging itself  {ends['evolving_self']:.2f}", 16, BLUE, "bold", anchor="start"))

t, _ = text_block(AX - 30, PBOT + 96,
                  "Random keep-2 sees the identical round-0 pool and decays: early luck without a judge's taste does not run away. Purple numbers: the neutral judge's selection gap each round — the runaway rides them.",
                  15.5, 58, GRAY)
b.append(t)

# ================= Panel B: gap -> drift, all K2 transitions =================
BX, BW = 720, 400
B_XMIN, B_XMAX = -0.16, 0.30
B_YMIN, B_YMAX = -0.20, 0.42


def bx_(v):
    return BX + BW * (v - B_XMIN) / (B_XMAX - B_XMIN)


def by_(v):
    return PY + PH * (B_YMAX - v) / (B_YMAX - B_YMIN)


b.append(f'<text x="{BX - 40}" y="206" font-size="21" font-weight="bold" fill="{INK}" '
         f'font-family="{FONT}">B. Pool drift tracks the same-round selection gap</text>')
t, _ = text_block(BX - 40, 232,
                  f"every round of all 17 OLMo K2 runs ({len(TRANS)} round-to-round transitions), all four judge conditions",
                  16, 62, GRAY)
b.append(t)

# zero-gap band
zb = D["zero_gap_band"]
b.append(f'<rect x="{bx_(-zb):.1f}" y="{PY}" width="{bx_(zb) - bx_(-zb):.1f}" height="{PH}" fill="{BAND_FILL}"/>')

for v in (-0.1, 0.0, 0.1, 0.2, 0.3, 0.4):
    yy = by_(v)
    col, sw = (INK, 2) if v == 0 else ("#e4e4e0", 1)
    b.append(f'<line x1="{BX}" y1="{yy:.1f}" x2="{BX + BW}" y2="{yy:.1f}" stroke="{col}" stroke-width="{sw}"/>')
    b.append(ctext(BX - 12, yy + 6, f"{v:+.1f}", 17, GRAY, anchor="end"))
for v in (-0.1, 0.0, 0.1, 0.2, 0.3):
    xx = bx_(v)
    col, sw = (INK, 2) if v == 0 else ("#e4e4e0", 1)
    b.append(f'<line x1="{xx:.1f}" y1="{PY}" x2="{xx:.1f}" y2="{PBOT}" stroke="{col}" stroke-width="{sw}"/>')
    b.append(ctext(xx, PBOT + 28, f"{v:+.1f}", 17, GRAY))
b.append(ctext(BX + BW / 2, PBOT + 58, "selection gap this round (kept answers minus the pool)", BODY, INK))
b.append(f'<text x="{BX - 66}" y="{PY + PH / 2}" font-size="{BODY}" fill="{INK}" font-family="{FONT}" '
         f'transform="rotate(-90 {BX - 66} {PY + PH / 2})" text-anchor="middle">pool drift into the next round</text>')

# fit line through the two judge-taste conditions
fx1, fx2 = -0.14, 0.28
b.append(f'<line x1="{bx_(fx1):.1f}" y1="{by_(SLOPE * fx1 + ICPT):.1f}" '
         f'x2="{bx_(fx2):.1f}" y2="{by_(SLOPE * fx2 + ICPT):.1f}" stroke="{INK}" stroke-width="3"/>')

# points, with rings for beyond-chance rounds (null percentile >= 0.9)
ringed = []
for gap, drift, cond, pct, in_runaway in TRANS:
    if pct >= 0.9:
        ringed.append((gap, drift, in_runaway))
for gap, drift, in_runaway in ringed:
    rc = RED if in_runaway else INK
    b.append(f'<circle cx="{bx_(gap):.1f}" cy="{by_(drift):.1f}" r="13" fill="none" '
             f'stroke="{rc}" stroke-width="2.5"/>')
for gap, drift, cond, pct, _ in TRANS:
    color, shape, _ = COND_STYLE[cond]
    b.append(marker(bx_(gap), by_(drift), shape, color))

# legend, top-left (clear of points)
ly = PY + 24
for cond in ("frozen_cons_r0", "frozen_base", "evolving_self", "random_select"):
    color, shape, label = COND_STYLE[cond]
    b.append(marker(BX + 20, ly - 5, shape, color))
    b.append(ctext(BX + 38, ly, label, 16.5, INK, anchor="start"))
    ly += 27

# fit label, bottom-right plate
flx, fly = bx_(0.115), by_(-0.115)
b.append(f'<rect x="{flx - 10:.1f}" y="{fly - 24:.1f}" width="256" height="80" rx="8" fill="white" fill-opacity="0.92"/>')
b.append(f'<text x="{flx:.1f}" y="{fly:.1f}" font-size="20" font-weight="bold" fill="{INK}" font-family="{FONT}">drift ≈ {SLOPE:.2f} × gap</text>')
b.append(f'<text x="{flx:.1f}" y="{fly + 24:.1f}" font-size="15.5" fill="{GRAY}" font-family="{FONT}">r = {RCORR:.2f}, fit through the neutral-judge</text>')
b.append(f'<text x="{flx:.1f}" y="{fly + 44:.1f}" font-size="15.5" fill="{GRAY}" font-family="{FONT}">and self-judge rounds (n = {len(fit_pts)})</text>')

# runaway-round annotation, centered amid the ringed cluster
b.append(ctext(bx_(0.152), by_(0.278), "the runaway", 16.5, RED, "bold"))
b.append(ctext(bx_(0.152), by_(0.278) + 20, "rounds", 16.5, RED, "bold"))

t, _ = text_block(BX - 40, PBOT + 96,
                  f"Shaded band: rounds with almost no gap (within ±{zb:g}) — their mean drift per condition is {ZG_LO:+.2f} to {ZG_HI:+.2f}: no momentum, even from elevated pools. "
                  f"Rings: the gap beat at least 90% of 4,000 random keeps. Red rings: those rounds inside the two runaway runs — the only runs with two such rounds; every other ringed round is isolated and goes nowhere.",
                  15.5, 66, GRAY)
b.append(t)

# ================= Panel C: summed gap vs total movement =================
CX, CW = 1290, 380
C_XMIN, C_XMAX = -0.30, 0.46
C_YMIN, C_YMAX = -0.42, 0.58


def cx_(v):
    return CX + CW * (v - C_XMIN) / (C_XMAX - C_XMIN)


def cy_(v):
    return PY + PH * (C_YMAX - v) / (C_YMAX - C_YMIN)


b.append(f'<text x="{CX - 40}" y="206" font-size="21" font-weight="bold" fill="{INK}" '
         f'font-family="{FONT}">C. The Qwen self-judge fan needs no gap</text>')
t, _ = text_block(CX - 40, 232,
                  "one point per run: the run's total movement against its summed selection gap",
                  16, 54, GRAY)
b.append(t)

for v in (-0.4, -0.2, 0.0, 0.2, 0.4):
    yy = cy_(v)
    col, sw = (INK, 2) if v == 0 else ("#e4e4e0", 1)
    b.append(f'<line x1="{CX}" y1="{yy:.1f}" x2="{CX + CW}" y2="{yy:.1f}" stroke="{col}" stroke-width="{sw}"/>')
    b.append(ctext(CX - 12, yy + 6, f"{v:+.1f}", 17, GRAY, anchor="end"))
for v in (-0.2, 0.0, 0.2, 0.4):
    xx = cx_(v)
    col, sw = (INK, 2) if v == 0 else ("#e4e4e0", 1)
    b.append(f'<line x1="{xx:.1f}" y1="{PY}" x2="{xx:.1f}" y2="{PBOT}" stroke="{col}" stroke-width="{sw}"/>')
    b.append(ctext(xx, PBOT + 28, f"{v:+.1f}", 17, GRAY))
b.append(ctext(CX + CW / 2, PBOT + 58, "summed selection gap over the run's 4 rounds", BODY, INK))
b.append(f'<text x="{CX - 66}" y="{PY + PH / 2}" font-size="{BODY}" fill="{INK}" font-family="{FONT}" '
         f'transform="rotate(-90 {CX - 66} {PY + PH / 2})" text-anchor="middle">total movement over the run</text>')

# diagonal: movement = summed gap
dlo, dhi = -0.28, 0.44
b.append(f'<line x1="{cx_(dlo):.1f}" y1="{cy_(dlo):.1f}" x2="{cx_(dhi):.1f}" y2="{cy_(dhi):.1f}" '
         f'stroke="{GRAY}" stroke-width="2" stroke-dasharray="7 6"/>')
ang = -math.degrees(math.atan2(cy_(dlo) - cy_(dhi + 0.0), cx_(dhi) - cx_(dlo)))
lxx, lyy = cx_(-0.115), cy_(-0.20)
b.append(f'<text x="{lxx:.1f}" y="{lyy:.1f}" font-size="15.5" fill="{GRAY}" font-family="{FONT}" '
         f'transform="rotate({ang:.1f} {lxx:.1f} {lyy:.1f})">movement = summed gap</text>')

# fan annotation in the clear top-left corner
t, _ = text_block(cx_(-0.29), cy_(0.55),
                  f"the Qwen fan: behavior moves {QMOVE_LO:+.2f} to {QMOVE_HI:+.2f} while summed gaps stay near zero",
                  15.5, 17, BLUE, "bold")
b.append(t)

# OLMo runs (filled, condition markers)
for sg, td, cond, is_runaway, seed in OLMO_RUNS:
    color, shape, _ = COND_STYLE[cond]
    b.append(marker(cx_(sg), cy_(td), shape, color))
# Qwen self-judge runs (open blue triangles)
for sg, mv in QWEN_PTS:
    b.append(marker(cx_(sg), cy_(mv), "triangle", BLUE, s=8.5, fill=False))

# runaway labels
for sg, td, cond, is_runaway, seed in OLMO_RUNS:
    if is_runaway:
        b.append(ctext(cx_(sg) - 16, cy_(td) + 5,
                       f"runaway seed {seed}", 16, RED, "bold", anchor="end"))

# legend, below the plot (the corners hold data and annotations)
lgy = PBOT + 88
for i, (shape, color) in enumerate((("square", PURPLE), ("circle", GREEN),
                                    ("triangle", BLUE), ("diamond", AMBER))):
    b.append(marker(CX - 24 + i * 24, lgy - 5, shape, color, s=6))
b.append(ctext(CX + 80, lgy, "OLMo, K2 (all four judges) — pool move", 16, INK, anchor="start"))
lgy += 26
b.append(marker(CX - 12, lgy - 5, "triangle", BLUE, s=7, fill=False))
b.append(ctext(CX + 80, lgy, "Qwen, K1, judging itself — behavior move", 16, INK, anchor="start"))

t, _ = text_block(CX - 40, PBOT + 148,
                  "Channels differ by design: OLMo movement is the generated-pool move (the gap's own channel); Qwen movement is the forced-choice behavioral endpoint move, because that is where its fan lives — its generated pools barely move while behavior fans by 0.75.",
                  15.5, 56, GRAY)
b.append(t)

# ================= takeaway =================
TY = PBOT + 262
tk, tk_end = rich_text(80, TY + 36, [
    ("Why the rare runaways run away: sustained beyond-chance selection by a frozen judge. ", INK, True),
    ("Not early luck — random keeps on the same lucky seed decay (A). Not stored momentum or pool pollution — zero-gap rounds don't move (B). "
     "And not a universal signature of self-judging — the Qwen self-judge fan moves the endpoint without any selection gap (C): "
     "that one is training instability, not taste.", INK, False),
], 19, 150)
b.append(box(60, TY, W - 120, (tk_end - TY) + 18, KEY_FILL, INK, 2.5))
b.append(tk)

H = int(tk_end + 50)
svg = svg_doc(W, H, "\n".join(b))
out = os.path.join(HERE, "runaway-mechanism.svg")
with open(out, "w") as f:
    f.write(svg)
print(f"wrote {out}  (fit slope={SLOPE:.3f}, r={RCORR:.3f}, n_fit={len(fit_pts)}, "
      f"n_transitions={len(TRANS)}, ringed={len(ringed)})")
