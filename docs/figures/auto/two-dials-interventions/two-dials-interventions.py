#!/usr/bin/env python3
"""Draft figure: every measured intervention moved exactly one of the two
dials of the selection gap — the pool's value spread (sigma) or the judge's
utilization of it (rho, the judge-candidate correlation).

One conceptual panel: the (rho, sigma) plane with before-to-after arrows for
each measured intervention. All numbers verified against
experiments/spread_util_unified.json (utilization table per-cell means,
spread_ledger per-round means, matched reopen-vs-twin pair).

Style: house style of docs/figures/src/make_figures.py (Owain Evans-lab
look — white background, headline sentence, fat labels, real data).
Regenerate with:  python3 two-dials-interventions.py
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))

INK = "#1a1a1a"
BLUE = "#2867b5"       # accent / self-judge series (validated)
GREEN = "#3a7d44"      # accent / frozen-judge series (validated)
RED = "#b5342c"        # emphasis for reversal / warning text
GRAY = "#6b7684"       # recessive only (axes, muted captions)
PURPLE = "#8a5a9e"     # fourth series color used elsewhere in the house set
KEY_FILL = "#eef5ee"

FONT = "Helvetica, Arial, sans-serif"


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


def txt(x, y, s, size=18, color=INK, weight="normal", anchor="start"):
    return (f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" '
            f'fill="{color}" font-weight="{weight}" '
            f'text-anchor="{anchor}">{esc(s)}</text>')


# ---------------------------------------------------------------- data
# All values read from experiments/spread_util_unified.json.

# 1. Format swap — OLMo risk organism, cautious fine-tuned copy as judge,
#    base-mixed pools. utilization table rows (format reference vs duel):
#    rho_mean 0.383 -> 0.100; per-cell mean spread 0.333 -> 0.370.
FMT_BEFORE = (0.383, 0.333)
FMT_AFTER = (0.100, 0.370)

# 2. Base-answer injection — Qwen self-report organism, score oracle,
#    matched pair "reopen(base-mixed)" vs "twin(self-only)" in spread_ledger:
#    twin spread 0.000 every round; reopen round-1 spread 0.3132. rho = -1.0
#    for the score oracle by construction (its rule IS the negated value).
INJ_BEFORE = (-1.0, 0.000)
INJ_AFTER = (-1.0, 0.313)

# 3. Peer invasion — OLMo peer-mixed records, per-round means over 8 runs:
#    (rho, sigma) round 1 (0.527, 0.430), round 2 (0.400, 0.165),
#    round 3 (0.447, 0.057); round 4 sigma 0.034 (rho unreliable, n=2).
PEER = [(0.527, 0.430), (0.400, 0.165), (0.447, 0.057)]

# 4. Self-judged duels with base text present — Qwen self-report organism,
#    self judge, duel format, base-mixed: rho_mean -0.236, mean spread 0.191.
SELF_EROSION = (-0.236, 0.191)

# Ordinary frozen model judges (risk axis, per-cell means):
#    Qwen base/reference (-0.032, 0.433), Qwen frozen copy (0.041, 0.433),
#    OLMo base/duel base-mixed (0.053, 0.396).
FROZEN = [(-0.032, 0.433), (0.041, 0.433), (0.053, 0.396)]

# Factorization (pooled, n=290 rounds with a defined rho):
#    r2 spread*rho 0.812; rho alone 0.594; spread alone 0.030.

# ---------------------------------------------------------------- geometry
W, H = 1120, 892
PX, PY, PW, PH = 170, 168, 880, 542
XMIN, XMAX = -1.12, 1.0
SMAX = 0.47


def X(rho):
    return PX + PW * (rho - XMIN) / (XMAX - XMIN)


def Y(sigma):
    return PY + PH * (SMAX - sigma) / SMAX


def marker(mid, color):
    return (f'<marker id="{mid}" viewBox="0 0 10 10" refX="8.5" refY="5" '
            f'markerWidth="5.2" markerHeight="5.2" orient="auto-start-reverse">'
            f'<path d="M 0 0 L 10 5 L 0 10 z" fill="{color}"/></marker>')


b = []

# headline + subtitle
b.append(txt(W / 2, 46, "Every intervention moved exactly one of the two dials",
             30, INK, "bold", "middle"))
sub1 = ("What a round selects for factors into two dials: the pool's value "
        "spread (the material) times the judge's utilization of it")
sub2 = ("(how consistently its choices track the value axis). Together they "
        "explain 81% of the realized selection gap over 290 logged rounds.")
b.append(txt(W / 2, 80, sub1, 17, GRAY, "normal", "middle"))
b.append(txt(W / 2, 103, sub2, 17, GRAY, "normal", "middle"))

# defs: one arrowhead per series color
b.append("<defs>" + marker("aB", BLUE) + marker("aG", GREEN)
         + marker("aP", PURPLE) + "</defs>")

# plot frame: gridlines + ticks
for s in (0.1, 0.2, 0.3, 0.4):
    yy = Y(s)
    b.append(f'<line x1="{PX}" y1="{yy:.1f}" x2="{PX + PW}" y2="{yy:.1f}" '
             f'stroke="#e4e4e0" stroke-width="1"/>')
    b.append(txt(PX - 12, yy + 6, f"{s:g}", 16, GRAY, "normal", "end"))
b.append(txt(PX - 12, Y(0) + 6, "0", 16, GRAY, "normal", "end"))
for r in (-1.0, -0.5, 0.0, 0.5, 1.0):
    xx = X(r)
    if r == 0.0:
        b.append(f'<line x1="{xx:.1f}" y1="{PY}" x2="{xx:.1f}" y2="{PY + PH}" '
                 f'stroke="{GRAY}" stroke-width="1.5" stroke-dasharray="6 5" '
                 f'opacity="0.75"/>')
    elif r == -1.0:
        b.append(f'<line x1="{xx:.1f}" y1="{PY}" x2="{xx:.1f}" y2="{PY + PH}" '
                 f'stroke="{GRAY}" stroke-width="1.5" stroke-dasharray="2 5" '
                 f'opacity="0.75"/>')
    else:
        b.append(f'<line x1="{xx:.1f}" y1="{PY}" x2="{xx:.1f}" y2="{PY + PH}" '
                 f'stroke="#e4e4e0" stroke-width="1"/>')
    lab = f"{r:+g}" if r else "0"
    b.append(txt(xx, PY + PH + 28, lab, 16, GRAY, "normal", "middle"))
# axis frame
b.append(f'<line x1="{PX}" y1="{PY + PH}" x2="{PX + PW}" y2="{PY + PH}" '
         f'stroke="{INK}" stroke-width="2"/>')
b.append(f'<line x1="{PX}" y1="{PY}" x2="{PX}" y2="{PY + PH}" '
         f'stroke="{INK}" stroke-width="2"/>')

# special-x annotations
b.append(txt(X(0), PY + PH + 52, "random keeping", 16, GRAY, "normal", "middle"))
b.append(txt(X(-1.0), PY + PH + 52, "score oracle: perfectly consistent —",
             16, GRAY, "normal", "middle"))
b.append(txt(X(-1.0), PY + PH + 72, "always keeps the two lowest scorers",
             16, GRAY, "normal", "middle"))

# axis labels
b.append(txt(PX + PW / 2, PY + PH + 108,
             "judge utilization (correlation of the judge's choices with the "
             "candidates' value scores; 0 = random keeping)",
             18, INK, "normal", "middle"))
ylx, yly = 74, PY + PH / 2
b.append(f'<text x="{ylx}" y="{yly}" font-family="{FONT}" font-size="18" '
         f'fill="{INK}" text-anchor="middle" transform="rotate(-90 {ylx} {yly})">'
         f'candidate value spread (within-question SD of pool value scores)</text>')

# ------------------------------------------------ series helpers
def dot(x, y, color, r=6.5, open_=False):
    fill = "white" if open_ else color
    return (f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{fill}" '
            f'stroke="{color if open_ else "white"}" stroke-width="2.2"/>')


def seg(p1, p2, color, mid, sw=4.5, shorten=10):
    """Arrowed segment from p1 to p2 in data coords, arrowhead shy of p2."""
    x1, y1, x2, y2 = X(p1[0]), Y(p1[1]), X(p2[0]), Y(p2[1])
    dx, dy = x2 - x1, y2 - y1
    L = (dx * dx + dy * dy) ** 0.5
    f = max(L - shorten, 1) / L
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x1 + dx * f:.1f}" '
            f'y2="{y1 + dy * f:.1f}" stroke="{color}" stroke-width="{sw}" '
            f'marker-end="url(#{mid})"/>')


# ------------------------------------------------ 1. format swap (BLUE)
b.append(seg(FMT_BEFORE, FMT_AFTER, BLUE, "aB"))
b.append(dot(X(FMT_BEFORE[0]), Y(FMT_BEFORE[1]), BLUE, open_=True))
b.append(dot(X(FMT_AFTER[0]), Y(FMT_AFTER[1]), BLUE))
b.append(txt(X(FMT_BEFORE[0]), Y(FMT_BEFORE[1]) - 16, "before", 15, GRAY,
             "normal", "middle"))
b.append(txt(X(FMT_AFTER[0]) - 4, Y(FMT_AFTER[1]) - 14, "after", 15, GRAY))
lx = X(0.34)
b.append(txt(lx, 348, "swap reference scoring for head-to-head duels", 18,
             BLUE, "bold", "end"))
b.append(txt(lx, 372, "(same cautious judge, same pools):", 18, INK,
             "normal", "end"))
b.append(txt(lx, 396, "utilization +0.38 → +0.10, spread stays "
             "≈ 0.33–0.37", 18, INK, "normal", "end"))

# ------------------------------------------------ 2. injection (GREEN)
b.append(seg(INJ_BEFORE, INJ_AFTER, GREEN, "aG"))
b.append(dot(X(INJ_BEFORE[0]), Y(INJ_BEFORE[1]), GREEN, open_=True))
b.append(dot(X(INJ_AFTER[0]), Y(INJ_AFTER[1]), GREEN))
gx = X(-0.96)
b.append(txt(gx, 546, "inject base-model answers into a collapsed pool", 18,
             GREEN, "bold"))
b.append(txt(gx, 570, "(same seeds, same score oracle):", 18, INK))
b.append(txt(gx, 594, "spread refills 0.00 → 0.31, utilization stays "
             "−1.0", 18, INK))

# ------------------------------------------------ 3. peer invasion (PURPLE)
for a, c in zip(PEER, PEER[1:]):
    b.append(seg(a, c, PURPLE, "aP"))
for i, p in enumerate(PEER):
    b.append(dot(X(p[0]), Y(p[1]), PURPLE))
    if i == 2:  # round 3 tag to the left, clear of the label block
        b.append(txt(X(p[0]) - 14, Y(p[1]) + 6, "round 3", 15, GRAY,
                     "normal", "end"))
    else:
        off = (12, -12) if i == 0 else (14, 6)
        b.append(txt(X(p[0]) + off[0], Y(p[1]) + off[1], f"round {i + 1}",
                     15, GRAY))
px2 = X(1.0) - 8
b.append(txt(px2, 672, "an extreme peer invades the pool:", 18, PURPLE,
             "bold", "end"))
b.append(txt(px2, 696, "spread collapses 0.43 → 0.06 as the host "
             "converges*", 18, INK, "normal", "end"))

# ------------------------------------------------ 4. self-judge erosion (RED)
sx, sy = X(SELF_EROSION[0]), Y(SELF_EROSION[1])
b.append(dot(sx, sy, RED, r=8))
b.append(txt(sx - 6, sy - 42, "the organism judges its own duels with base "
             "text present:", 18, RED, "bold", "middle"))
b.append(txt(sx - 6, sy - 18, "utilization −0.24 — selection ran "
             "against its own value (erosion)", 18, INK, "normal", "middle"))

# ------------------------------------------------ frozen-judge cluster (GRAY)
for p in FROZEN:
    b.append(dot(X(p[0]), Y(p[1]), GRAY, r=5.5))
b.append(txt(X(-0.032) - 16, Y(0.433) + 6,
             "ordinary frozen model judges: utilization ≈ 0", 16, GRAY,
             "normal", "end"))

# ------------------------------------------------ footnote
foot = ("* peer-invasion path = per-round means over the 8 peer-invaded OLMo "
        "runs; by round 4 spread is 0.03 but too few rounds with distinct "
        "judge scores remain to estimate utilization.")
for i, line in enumerate(wrap(foot, 120)):
    b.append(txt(PX - 110, PY + PH + 142 + i * 21, line, 15, GRAY))

svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
       f'font-family="{FONT}">\n<rect width="{W}" height="{H}" fill="white"/>\n'
       + "\n".join(b) + "\n</svg>")

out = os.path.join(HERE, "two-dials-interventions.svg")
with open(out, "w") as f:
    f.write(svg)
print("wrote", out)
