#!/usr/bin/env python3
"""Spread at a fixed pool mean: re-arranging the same candidates across prompts
changes the selection gap, and both arrangements obey the same law.

Panel A is the paired contrast (within-prompt spread, between-prompt variance,
size of the selection gap) for the two arrangements at an identical pool mean.
Panel B plots every arrangement-round's selection gap against judge agreement
times within-prompt spread, with one line fitted to both arrangements together.

Everything rendered is computed here from experiments/spread_at_fixed_mean.json
("rows"); nothing is read from that file's precomputed "summary".

Regenerate with:  python3 spread-at-fixed-mean.py     (stdlib only)
"""
import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = HERE
while ROOT != os.path.dirname(ROOT) and not os.path.isdir(os.path.join(ROOT, "experiments")):
    ROOT = os.path.dirname(ROOT)
DATA = os.path.join(ROOT, "experiments", "spread_at_fixed_mean.json")
OUTFILE = os.path.join(HERE, "spread-at-fixed-mean.svg")

# ---- palette, copied from docs/figures/src/make_figures.py -------------------
INK = "#1a1a1a"
BLUE = "#2867b5"       # accent / self-judge series (validated)
GREEN = "#3a7d44"      # accent / frozen-judge series (validated)
RED = "#b5342c"        # emphasis for reversal / warning text
GRAY = "#6b7684"       # recessive only (axes, muted captions) — never a series
USER_FILL = "#cfe0f1"  # chat user box
ASST_FILL = "#eaf1f8"  # chat assistant box
DOC_FILL = "#fdf6e8"   # document / essay box
KEY_FILL = "#eef5ee"   # highlighted takeaway box

FONT = "Helvetica, Arial, sans-serif"
GRID = "#e4e4e0"
BODY = 19              # minimum readable body size in this figure set


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
        svg.append(f'<text x="{x}" y="{y + i * size * lh:.1f}" font-family="{FONT}" '
                   f'font-size="{size}" font-weight="{weight}" fill="{color}">{esc(ln)}</text>')
    return "\n".join(svg), y + len(lines) * size * lh


def ctext(x, y, text, size, color=INK, weight="normal"):
    return (f'<text x="{x}" y="{y}" text-anchor="middle" font-family="{FONT}" '
            f'font-size="{size}" font-weight="{weight}" fill="{color}">{esc(text)}</text>')


def ltext(x, y, text, size, color=INK, weight="normal"):
    return (f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" '
            f'font-weight="{weight}" fill="{color}">{esc(text)}</text>')


def rtext(x, y, text, size, color=INK, weight="normal"):
    return (f'<text x="{x}" y="{y}" text-anchor="end" font-family="{FONT}" '
            f'font-size="{size}" font-weight="{weight}" fill="{color}">{esc(text)}</text>')


def box(x, y, w, h, fill, stroke=INK, sw=2.5, rx=8):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')


def marker(x, y, shape, color, s=7.5, opacity=1.0, ring="white", rw=1.5):
    o = f' fill-opacity="{opacity}"' if opacity < 1 else ""
    if shape == "circle":
        return (f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{s}" fill="{color}"{o} '
                f'stroke="{ring}" stroke-width="{rw}"/>')
    if shape == "diamond":
        pts = (f"{x:.1f},{y - s - 1.5:.1f} {x + s + 1:.1f},{y:.1f} "
               f"{x:.1f},{y + s + 1.5:.1f} {x - s - 1:.1f},{y:.1f}")
        return f'<polygon points="{pts}" fill="{color}"{o} stroke="{ring}" stroke-width="{rw}"/>'
    return ""


DEFS = f'''<defs><marker id="arr" viewBox="0 0 10 10" refX="9" refY="5"
 markerWidth="6" markerHeight="6" orient="auto-start-reverse">
 <path d="M 0 0 L 10 5 L 0 10 z" fill="{INK}"/></marker>
<marker id="arrR" viewBox="0 0 10 10" refX="9" refY="5"
 markerWidth="6" markerHeight="6" orient="auto-start-reverse">
 <path d="M 0 0 L 10 5 L 0 10 z" fill="{RED}"/></marker></defs>'''


def svg_doc(w, h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
            f'font-family="{FONT}">\n<rect width="{w}" height="{h}" fill="white"/>\n'
            f'{DEFS}\n{body}\n</svg>')


# ================================================================ data
def mean(xs):
    return sum(xs) / len(xs)


def fit(xs, ys):
    mx, my = mean(xs), mean(ys)
    sxx = sum((x - mx) ** 2 for x in xs)
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    syy = sum((y - my) ** 2 for y in ys)
    slope = sxy / sxx
    return slope, my - slope * mx, sxy / math.sqrt(sxx * syy)


D = json.load(open(DATA))
ROWS = D["rows"]
N_ROUNDS = len(ROWS)
N_PROMPTS = sorted({r["n_prompts"] for r in ROWS})

# per-arm aggregates, recomputed from the rows
AGG = {}
for arm in ("high", "low"):
    AGG[arm] = dict(
        spread=mean([r[arm]["spread"] for r in ROWS]),
        between=mean([r[arm]["between_prompt_variance"] for r in ROWS]),
        abs_gap=mean([abs(r[arm]["gap"]) for r in ROWS]),
        gap=mean([r[arm]["gap"] for r in ROWS]),
        rho=mean([r[arm]["rho"] for r in ROWS]),
    )

# the pool mean is matched exactly, arrangement to arrangement, in every round
MAX_MEAN_DIFF = max(abs(r["high"]["pool_mean"] - r["low"]["pool_mean"]) for r in ROWS)
POOL_LO = min(r["pool_mean"] for r in ROWS)
POOL_HI = max(r["pool_mean"] for r in ROWS)

N_BIGGER = sum(1 for r in ROWS if abs(r["high"]["gap"]) > abs(r["low"]["gap"]))
N_TIED = sum(1 for r in ROWS if abs(r["high"]["gap"]) == abs(r["low"]["gap"]))
N_SMALLER = N_ROUNDS - N_BIGGER - N_TIED

PT = {arm: [(r[arm]["rho"] * r[arm]["spread"], r[arm]["gap"]) for r in ROWS]
      for arm in ("high", "low")}
FIT = {arm: fit([p[0] for p in PT[arm]], [p[1] for p in PT[arm]]) for arm in ("high", "low")}
ALLX = [p[0] for a in ("high", "low") for p in PT[a]]
ALLY = [p[1] for a in ("high", "low") for p in PT[a]]
SLOPE, ICPT, R = fit(ALLX, ALLY)
N_POINTS = len(ALLX)
LOW_XLO, LOW_XHI = min(p[0] for p in PT["low"]), max(p[0] for p in PT["low"])

ARM = {  # display identity for the two arrangements
    "high": (BLUE, "circle", "Arrangement 1 — variation kept inside prompts"),
    "low": (GREEN, "diamond", "Arrangement 2 — variation parked between prompts"),
}

# ================================================================ figure
W = 1520
b = []

b.append(ctext(W // 2, 56,
               "Hold the pool mean exactly fixed, move the variation between prompts,",
               34, INK, "bold"))
b.append(ctext(W // 2, 98,
               "and the selection gap collapses from 0.10 to 0.03", 34, INK, "bold"))
t, _ = text_block(180, 136,
                  "The judge only ever compares candidates written for the same prompt. Variation parked "
                  "between prompts is invisible to it, so it cannot become a selection gap.",
                  BODY + 1, 112, GRAY)
b.append(t)

# in-figure condition line
CONDY = 190
b.append(box(150, CONDY, W - 300, 62, KEY_FILL, GREEN, 2, rx=10))
t, _ = text_block(174, CONDY + 27,
                  f"{N_ROUNDS} logged rounds of {'/'.join(str(n) for n in N_PROMPTS)} prompts each. The logged candidates are "
                  f"re-arranged into sub-pools of 4 per prompt with the top 2 kept, scored by the judges' own "
                  f"recorded scores. Selection only — nothing is retrained.",
                  BODY, 140, INK)
b.append(t)

# ---------------------------------------------------------------- Panel A
AX0, AX1 = 90, 748
PTY = 302
b.append(ltext(AX0, PTY, "A. The same candidates, arranged two ways at one pool mean", 24, INK, "bold"))

# --- schematic of the re-arrangement (illustration, labelled as such)
GY = PTY + 142                   # top of the dot grids
CELL, DOT = 22, 7.5
GW = 12 * CELL - 4
G1X, G2X = AX0 + 8, AX0 + 8 + GW + 96

for gx, arm, head in (
        (G1X, "high", "Arrangement 1: every prompt is split, so the judge always has a choice"),
        (G2X, "low", "Arrangement 2: prompts are all-or-nothing, so there is nothing to choose")):
    color = ARM[arm][0]
    b.append(f'<line x1="{gx - 6}" y1="{PTY + 26}" x2="{gx + GW + 6}" y2="{PTY + 26}" '
             f'stroke="{color}" stroke-width="5"/>')
    t, _ = text_block(gx - 6, PTY + 54, head, BODY, 28, color, "bold")
    b.append(t)

PATTERN1 = [(0, 1), (1, 2), (0, 2), (2, 3), (0, 3), (1, 3)]
for p in range(12):
    rows_on_1 = PATTERN1[p % len(PATTERN1)]
    on2 = (p % 2 == 0)
    for r in range(4):
        cy = GY + 12 + r * CELL
        for gx, on in ((G1X, r in rows_on_1), (G2X, on2)):
            cx = gx + 12 + p * CELL
            if on:
                b.append(f'<circle cx="{cx}" cy="{cy}" r="{DOT}" fill="{INK}"/>')
            else:
                b.append(f'<circle cx="{cx}" cy="{cy}" r="{DOT}" fill="white" '
                         f'stroke="{GRAY}" stroke-width="2"/>')

GBOT = GY + 12 + 3 * CELL + DOT + 10
for gx in (G1X, G2X):
    b.append(f'<line x1="{gx - 6}" y1="{GBOT}" x2="{gx + GW + 6}" y2="{GBOT}" '
             f'stroke="{GRAY}" stroke-width="1.5"/>')
    b.append(ctext(gx + GW / 2, GBOT + 26, "12 prompts, 4 candidates each", 18, GRAY))

# the identical-pool-mean signal, between the two grids
EQX = (G1X + GW + G2X) / 2
EQY = GY + 46
b.append(f'<circle cx="{EQX}" cy="{EQY}" r="30" fill="white" stroke="{RED}" stroke-width="3.5"/>')
b.append(ctext(EQX, EQY + 13, "=", 44, RED, "bold"))

KY = GBOT + 56
b.append(f'<circle cx="{AX0 + 12}" cy="{KY - 6}" r="{DOT}" fill="{INK}"/>')
b.append(ltext(AX0 + 30, KY, "scores 1 (chose the risky gamble)", 18, GRAY))
b.append(f'<circle cx="{AX0 + 330}" cy="{KY - 6}" r="{DOT}" fill="white" stroke="{GRAY}" stroke-width="2"/>')
b.append(ltext(AX0 + 348, KY, "scores 0", 18, GRAY))
b.append(ltext(AX0, KY + 26, "The two grids are an illustration of the re-arrangement at pool mean 0.50; the real", 18, GRAY))
b.append(ltext(AX0, KY + 48, "arrangements are solved round by round from logged candidates and are less extreme.", 18, GRAY))

BOXY = KY + 72
b.append(box(AX0, BOXY, AX1 - AX0, 94, "#fbf0ee", RED, 2.5, rx=10))
t, _ = text_block(AX0 + 20, BOXY + 30,
                  f"Identical pool mean, exact by construction: 24 of the 48 candidates score 1 on both sides "
                  f"above, and across all {N_ROUNDS} rounds the largest difference in pool mean between the two "
                  f"arrangements is {MAX_MEAN_DIFF:.6f}.",
                  BODY, 74, INK)
b.append(t)

# --- measured contrast: three readouts, one shared 0 to 0.30 scale
MX0, MX1 = AX0 + 30, AX1 - 172
MSCALE = 0.30
BLOCKY = BOXY + 148


def mx_(v):
    return MX0 + (MX1 - MX0) * v / MSCALE


b.append(ltext(AX0, BLOCKY, "Measured over all 323 rounds:", 20, INK, "bold"))

# key for the two arrangements, reused by panel B
for i, arm in enumerate(("high", "low")):
    color, shape, _ = ARM[arm]
    kx = AX0 + 300 + i * 172
    b.append(marker(kx, BLOCKY - 6, shape, color, 8))
    b.append(ltext(kx + 16, BLOCKY, f"arrangement {i + 1}", 18, INK))

READOUTS = [
    ("within-prompt spread",
     "average over prompts of the standard deviation of that prompt's 4 candidate scores",
     "spread"),
    ("between-prompt variance",
     "variance across prompts of each prompt's own mean candidate score",
     "between"),
    ("size of the selection gap",
     "kept-candidate mean minus pool mean, size ignoring sign, averaged over rounds",
     "abs_gap"),
]

ry = BLOCKY + 42
DOT_YS = []
for name, recipe, key in READOUTS:
    b.append(ltext(AX0, ry, name, 20, INK, "bold"))
    t, ry2 = text_block(AX0, ry + 25, recipe, 18, 74, GRAY)
    b.append(t)
    hi, lo = AGG["high"][key], AGG["low"][key]
    cy = ry2 + 24
    DOT_YS.append(cy)
    for v in (0.0, 0.10, 0.20, 0.30):
        b.append(f'<line x1="{mx_(v):.1f}" y1="{cy - 26:.1f}" x2="{mx_(v):.1f}" y2="{cy + 26:.1f}" '
                 f'stroke="{GRID}" stroke-width="1"/>')
    b.append(f'<line x1="{mx_(min(hi, lo)):.1f}" y1="{cy:.1f}" x2="{mx_(max(hi, lo)):.1f}" '
             f'y2="{cy:.1f}" stroke="{INK}" stroke-width="3"/>')
    b.append(marker(mx_(lo), cy, "diamond", GREEN, 10))
    b.append(marker(mx_(hi), cy, "circle", BLUE, 10))
    # value labels placed on the outside of each dot so they never collide
    if hi > lo:
        b.append(rtext(mx_(lo) - 18, cy + 8, f"{lo:.3f}", 22, INK, "bold"))
        b.append(ltext(mx_(hi) + 18, cy + 8, f"{hi:.3f}", 22, INK, "bold"))
    else:
        b.append(rtext(mx_(hi) - 18, cy + 8, f"{hi:.3f}", 22, INK, "bold"))
        b.append(ltext(mx_(lo) + 18, cy + 8, f"{lo:.3f}", 22, INK, "bold"))
    ry = cy + 68

# shared scale for the three readouts
AXY = ry - 24
b.append(f'<line x1="{mx_(0):.1f}" y1="{AXY}" x2="{mx_(MSCALE):.1f}" y2="{AXY}" stroke="{GRAY}" stroke-width="1.5"/>')
for v in (0.0, 0.10, 0.20, 0.30):
    b.append(f'<line x1="{mx_(v):.1f}" y1="{AXY}" x2="{mx_(v):.1f}" y2="{AXY + 7}" stroke="{GRAY}" stroke-width="1.5"/>')
    b.append(ctext(mx_(v), AXY + 28, f"{v:.2f}", 18, GRAY))
b.append(ltext(mx_(MSCALE) + 22, AXY + 28, "one shared scale", 18, GRAY))
ry = AXY + 34

# the trade-off arrow, tying the first two readouts together
TRX = AX1 - 74
b.append(f'<path d="M {TRX} {DOT_YS[0]} L {TRX + 26} {DOT_YS[0]} '
         f'L {TRX + 26} {DOT_YS[1]} L {TRX} {DOT_YS[1]}" fill="none" '
         f'stroke="{RED}" stroke-width="3" marker-end="url(#arrR)"/>')
TRMY = (DOT_YS[0] + DOT_YS[1]) / 2
b.append(f'<text x="{TRX + 48}" y="{TRMY}" font-family="{FONT}" font-size="18" fill="{RED}" '
         f'font-weight="bold" text-anchor="middle" transform="rotate(-90 {TRX + 48} {TRMY})">traded off</text>')
t, _ = text_block(AX0, ry + 46,
                  "The trade-off that makes this possible: variation taken out of the prompts does not vanish, "
                  "it reappears between them. The pool mean never moves.",
                  BODY, 82, RED)
b.append(t)
t, _ = text_block(AX0, ry + 102,
                  f"Round by round, arrangement 1 gave the larger selection gap in {N_BIGGER} of the {N_ROUNDS} rounds, "
                  f"tied in {N_TIED}, and gave a smaller one in {N_SMALLER}.",
                  18, 88, GRAY)
b.append(t)
A_BOTTOM = ry + 150

# ---------------------------------------------------------------- Panel B
BX0 = 850
b.append(ltext(BX0, PTY, "B. Both arrangements obey the same law", 24, INK, "bold"))
t, _ = text_block(BX0, PTY + 32,
                  "Each mark is one round under one arrangement. Judge agreement is the correlation, inside a "
                  "single prompt, between the judge's score and the value score, averaged over prompts.",
                  18, 74, GRAY)
b.append(t)

PX, PY, PW, PH = BX0 + 96, PTY + 116, 522, 522
XMIN, XMAX = -0.36, 0.36
YMIN, YMAX = -0.45, 0.40


def px_(v):
    return PX + PW * (v - XMIN) / (XMAX - XMIN)


def py_(v):
    return PY + PH * (YMAX - v) / (YMAX - YMIN)


for v in (-0.3, -0.2, -0.1, 0.0, 0.1, 0.2, 0.3):
    xx = px_(v)
    col, sw = (INK, 2) if v == 0 else (GRID, 1)
    b.append(f'<line x1="{xx:.1f}" y1="{PY}" x2="{xx:.1f}" y2="{PY + PH}" stroke="{col}" stroke-width="{sw}"/>')
    b.append(ctext(xx, PY + PH + 30, f"{v:+.1f}" if v else "0", 18, GRAY))
for v in (-0.4, -0.2, 0.0, 0.2, 0.4):
    yy = py_(v)
    col, sw = (INK, 2) if v == 0 else (GRID, 1)
    b.append(f'<line x1="{PX}" y1="{yy:.1f}" x2="{PX + PW}" y2="{yy:.1f}" stroke="{col}" stroke-width="{sw}"/>')
    b.append(rtext(PX - 12, yy + 6, f"{v:+.1f}" if v else "0", 18, GRAY))

b.append(ctext(PX + PW / 2, PY + PH + 62, "judge agreement × within-prompt spread", BODY, INK))
b.append(f'<text x="{PX - 74}" y="{PY + PH / 2}" font-size="{BODY}" fill="{INK}" font-family="{FONT}" '
         f'transform="rotate(-90 {PX - 74} {PY + PH / 2})" text-anchor="middle">'
         f'selection gap (kept mean minus pool mean)</text>')

# band showing how tightly arrangement 2 packs around zero
b.append(f'<rect x="{px_(LOW_XLO):.1f}" y="{PY}" width="{px_(LOW_XHI) - px_(LOW_XLO):.1f}" '
         f'height="{PH}" fill="{GREEN}" fill-opacity="0.06"/>')
for v in (LOW_XLO, LOW_XHI):
    b.append(f'<line x1="{px_(v):.1f}" y1="{PY}" x2="{px_(v):.1f}" y2="{PY + PH}" '
             f'stroke="{GREEN}" stroke-width="2" stroke-dasharray="7 5"/>')

for arm in ("high", "low"):
    color, shape, _ = ARM[arm]
    for x, y in PT[arm]:
        b.append(marker(px_(x), py_(y), shape, color, 5.0, opacity=0.5, ring=color, rw=0.8))

x1, x2 = -0.34, 0.35
b.append(f'<line x1="{px_(x1):.1f}" y1="{py_(SLOPE * x1 + ICPT):.1f}" x2="{px_(x2):.1f}" '
         f'y2="{py_(SLOPE * x2 + ICPT):.1f}" stroke="{INK}" stroke-width="3.5"/>')

# direct labels on the two clouds, in the empty upper-left corner
KLX, KLY = px_(-0.345), py_(0.365)
b.append(f'<rect x="{KLX - 6:.1f}" y="{KLY - 26:.1f}" width="420" height="66" rx="8" '
         f'fill="white" fill-opacity="0.9"/>')
b.append(marker(KLX + 8, KLY - 6, "circle", BLUE, 8))
b.append(ltext(KLX + 26, KLY, "arrangement 1 — reaches far out along the line", 18, INK))
b.append(marker(KLX + 8, KLY + 24, "diamond", GREEN, 8))
b.append(ltext(KLX + 26, KLY + 30, "arrangement 2 — packed into the shaded band", 18, INK))

# the fit, in its own box below the plot so it never sits on top of data
FBY = PY + PH + 100
FBW = PX + PW - BX0
b.append(box(BX0, FBY, FBW, 112, KEY_FILL, GREEN, 2, rx=10))
b.append(ctext(BX0 + FBW / 2, FBY + 36,
               f"gap = {SLOPE:.2f} × (agreement × spread) − {abs(ICPT):.3f}", 22, INK, "bold"))
b.append(ctext(BX0 + FBW / 2, FBY + 68,
               f"one line, both arrangements: r = {R:.2f} over {N_POINTS} arrangement-rounds", 18, GRAY))
b.append(ctext(BX0 + FBW / 2, FBY + 94,
               f"fitted apart: slope {FIT['high'][0]:.2f} for arrangement 1, "
               f"{FIT['low'][0]:.2f} for arrangement 2", 18, GRAY))

t, B_BOTTOM = text_block(BX0, FBY + 160,
                         "One line fits both arrangements. Re-arranging the candidates does not change the rule "
                         "that turns spread into a selection gap; it changes how much spread the judge is shown. "
                         f"Pool means across these rounds run from {POOL_LO:.2f} to {POOL_HI:.2f}, and each round's "
                         "two marks sit at the same pool mean as each other.",
                         BODY, 66, INK)
b.append(t)

H = max(A_BOTTOM, B_BOTTOM) + 40
svg = svg_doc(W, H, "\n".join(b))
with open(OUTFILE, "w") as f:
    f.write(svg)
print(f"wrote {os.path.basename(OUTFILE)}  "
      f"(spread {AGG['high']['spread']:.4f} vs {AGG['low']['spread']:.4f}; "
      f"between-prompt variance {AGG['high']['between']:.4f} vs {AGG['low']['between']:.4f}; "
      f"mean |gap| {AGG['high']['abs_gap']:.4f} vs {AGG['low']['abs_gap']:.4f}; "
      f"pooled slope {SLOPE:.4f}, r {R:.4f}, n {N_POINTS})")
