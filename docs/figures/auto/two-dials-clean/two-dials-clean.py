#!/usr/bin/env python3
"""Clean redraw (v2): every measured intervention moved exactly one of the
two dials of the SELECTOR GAP -- kept-target value minus whole-pool value,
a measured quantity (not a force) that decomposes as agreement x spread.
The dials are the pool's value spread (sigma) and the judge's agreement of
it (rho, the correlation of the judge's choices with the value axis).

Note (figure-brief item 5): the base-answer injection is not a pure spread
reset -- it also shifts the pool supply and adds between-source spread; the
extremist-copy invasion shrinks between-source spread as host and supplier
converge (that trajectory lives in the conversion-chain figure).

One panel: the (agreement, spread) plane with before-to-after arrows for
each measured intervention. Each intervention carries a short (2-5 word)
label only -- all before/after numbers live in the caption, not the image.
All numbers verified against experiments/spread_util_unified.json
(agreement table per-cell means, spread_ledger per-round means, matched
reopen-versus-twin pair).

Style: house style of docs/figures/src/make_figures.py (Owain Evans-lab
look -- white background, headline sentence, fat labels, real data).
Regenerate with:  python3 two-dials-clean.py
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))

INK = "#1a1a1a"
# five clearly-distinct series hues (blue / green / red / violet) + neutral gray
BLUE = "#1f6fd0"       # format swap (reference -> duels)
GREEN = "#1f9e57"      # base-answer injection
RED = "#d1341f"        # self-judged duels (erosion)
GRAY = "#6b7684"       # recessive (axes, muted captions) AND frozen-judge series
PURPLE = "#9427b5"     # extremist-copy invasion (vivid violet, not a dull blue)

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


def txt(x, y, s, size=18, color=INK, weight="normal", anchor="start",
        halo=False):
    """halo=True paints a white outline under the glyphs so labels stay
    readable where they sit over gridlines or dots."""
    h = ('stroke="white" stroke-width="5" stroke-linejoin="round" '
         'paint-order="stroke" ') if halo else ""
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{FONT}" '
            f'font-size="{size}" fill="{color}" font-weight="{weight}" '
            f'{h}text-anchor="{anchor}">{esc(s)}</text>')


# ---------------------------------------------------------------- data
# All values read from experiments/spread_util_unified.json. Numeric
# before-to-after detail is NOT drawn in the image (house rule for this
# revision) -- it lives in caption.md. Point/arrow positions below are
# unchanged from the prior draft.

# 1. Format swap -- OLMo risk organism, cautious fine-tuned copy as judge,
#    base-mixed pools. Agreement-table rows (reference format vs duel):
#    rho_mean 0.383 -> 0.100; per-cell mean spread 0.333 -> 0.370.
FMT_BEFORE = (0.383, 0.333)
FMT_AFTER = (0.100, 0.370)

# 2. Base-answer injection -- Qwen self-report organism, score oracle,
#    matched pair "reopen(base-mixed)" vs "twin(self-only)" in spread_ledger:
#    twin spread 0.000 every round; reopen round-1 spread 0.3132. rho = -1.0
#    for the score oracle by construction (its rule IS the negated value).
INJ_BEFORE = (-1.0, 0.000)
INJ_AFTER = (-1.0, 0.313)

# 3. Extremist-peer invasion -- OLMo peer-mixed records, per-round means over
#    8 runs: (rho, sigma) round 1 (0.527, 0.430), round 2 (0.400, 0.165),
#    round 3 (0.447, 0.057); round 4 sigma 0.034 (rho unreliable, n=2).
PEER = [(0.527, 0.430), (0.400, 0.165), (0.447, 0.057)]

# 4. Self-judged duels with base text present -- Qwen self-report organism,
#    self judge, duel format, base-mixed: rho_mean -0.236, mean spread 0.191.
SELF_EROSION = (-0.236, 0.191)

# Ordinary frozen model judges (per-cell means): Qwen base (-0.032, 0.433),
# Qwen frozen copy (0.041, 0.433), OLMo base duel base-mixed (0.053, 0.396).
FROZEN = [(-0.032, 0.433), (0.041, 0.433), (0.053, 0.396)]

# Factorization (pooled, n=290 rounds with a defined rho): the selector gap
# (kept minus whole-pool value) tracks agreement x spread -- r2 0.812; rho
# alone 0.594; spread alone 0.030. This is a decomposition ("selector gap ~=
# agreement x spread"), NOT a force; the retracted point-estimate coefficient
# is deliberately not printed.

# Injection also shifts the pool supply: between-source variance is a real
# share of the mixed pool's within-prompt variance, not a pure spread reset.
# Source: experiments/spread_conversion_model.json (mixed_pool_variance
# _decomposition, base-mixed n=64 rounds, peer-mixed n=32 rounds).
BASE_MIXED_BETWEEN_SHARE = 0.33655    # between-source var / mean total var
PEER_MIXED_BETWEEN_SHARE = 0.566952
assert round(BASE_MIXED_BETWEEN_SHARE * 100) == 34, "base-mixed share drift"
assert round(PEER_MIXED_BETWEEN_SHARE * 100) == 57, "peer-mixed share drift"

# ---------------------------------------------------------------- geometry
# PX, PY, PW, PH, XMIN, XMAX, SMAX are unchanged from the prior draft, so
# every dot/arrow below lands at the same pixel position as before.
W, H = 1180, 1140
PX, PY, PW, PH = 160, 160, 880, 510
XMIN, XMAX = -1.15, 1.05
SMAX = 0.47


def X(rho):
    return PX + PW * (rho - XMIN) / (XMAX - XMIN)


def Y(sigma):
    return PY + PH * (SMAX - sigma) / SMAX


def marker(mid, color):
    return (f'<marker id="{mid}" viewBox="0 0 10 10" refX="8.5" refY="5" '
            f'markerWidth="5.2" markerHeight="5.2" orient="auto-start-reverse">'
            f'<path d="M 0 0 L 10 5 L 0 10 z" fill="{color}"/></marker>')


def dot(rho, sigma, color, r=6.5, open_=False, opacity=1.0):
    fill = "white" if open_ else color
    ring = color if open_ else "white"
    return (f'<circle cx="{X(rho):.1f}" cy="{Y(sigma):.1f}" r="{r}" '
            f'fill="{fill}" stroke="{ring}" stroke-width="2.2" '
            f'opacity="{opacity}"/>')


def seg(p1, p2, color, mid, sw=4.5, shorten=11):
    """Arrowed segment p1 -> p2 in data coords, arrowhead shy of p2."""
    x1, y1, x2, y2 = X(p1[0]), Y(p1[1]), X(p2[0]), Y(p2[1])
    dx, dy = x2 - x1, y2 - y1
    L = (dx * dx + dy * dy) ** 0.5
    f = max(L - shorten, 1) / L
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x1 + dx * f:.1f}" '
            f'y2="{y1 + dy * f:.1f}" stroke="{color}" stroke-width="{sw}" '
            f'marker-end="url(#{mid})"/>')


def leader(x1, y1, x2, y2):
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{GRAY}" stroke-width="1.5" opacity="0.85"/>')


b = []

# ------------------------------------------------ headline only (no
# descriptive subtitle -- all interpretation moved to caption.md)
b.append(txt(W / 2, 46, "Every intervention moved one dial: spread or "
             "agreement", 29, INK, "bold", "middle"))
b.append(txt(W / 2, 76, "each arrow is one setup, before → after a single "
             "change — not one round to the next", 17, GRAY, "normal",
             "middle"))

# before/after key, top right, clear of the plot
b.append(f'<circle cx="850" cy="94" r="6" fill="white" stroke="{GRAY}" '
         f'stroke-width="2"/>')
b.append(txt(862, 100, "before", 15, GRAY))
b.append(f'<circle cx="953" cy="94" r="6" fill="{GRAY}"/>')
b.append(txt(965, 100, "after", 15, GRAY))

# defs: one arrowhead per series color
b.append("<defs>" + marker("aB", BLUE) + marker("aG", GREEN)
         + marker("aP", PURPLE) + "</defs>")

# ------------------------------------------------ frame: gridlines + ticks
for s in (0.1, 0.2, 0.3, 0.4):
    yy = Y(s)
    b.append(f'<line x1="{PX}" y1="{yy:.1f}" x2="{PX + PW}" y2="{yy:.1f}" '
             f'stroke="#e4e4e0" stroke-width="1"/>')
    b.append(txt(PX - 12, yy + 6, f"{s:g}", 16, GRAY, "normal", "end"))
b.append(txt(PX - 12, Y(0) + 6, "0", 16, GRAY, "normal", "end"))
for r in (-1.0, -0.5, 0.0, 0.5, 1.0):
    xx = X(r)
    if r == 0.0:      # random-keeping line
        b.append(f'<line x1="{xx:.1f}" y1="{PY}" x2="{xx:.1f}" '
                 f'y2="{PY + PH}" stroke="{GRAY}" stroke-width="1.5" '
                 f'stroke-dasharray="6 5" opacity="0.7"/>')
    elif r == -1.0:   # score-oracle edge
        b.append(f'<line x1="{xx:.1f}" y1="{PY}" x2="{xx:.1f}" '
                 f'y2="{PY + PH}" stroke="{GRAY}" stroke-width="1.5" '
                 f'stroke-dasharray="2 5" opacity="0.7"/>')
    else:
        b.append(f'<line x1="{xx:.1f}" y1="{PY}" x2="{xx:.1f}" '
                 f'y2="{PY + PH}" stroke="#e4e4e0" stroke-width="1"/>')
    b.append(txt(xx, PY + PH + 30, f"{r:+g}" if r else "0", 16, GRAY,
                 "normal", "middle"))
# axis frame
b.append(f'<line x1="{PX}" y1="{PY + PH}" x2="{PX + PW}" y2="{PY + PH}" '
         f'stroke="{INK}" stroke-width="2"/>')
b.append(f'<line x1="{PX}" y1="{PY}" x2="{PX}" y2="{PY + PH}" '
         f'stroke="{INK}" stroke-width="2"/>')

# dial tags now live INSIDE the plot, at the top of their own gridline --
# not in the band between the plot and the x-axis title.
b.append(txt(X(0.0), PY + 15, "random keeping", 15, GRAY, "normal",
             "middle", halo=True))
b.append(txt(X(-1.0), PY + 15, "score oracle", 15, GRAY, "normal",
             "middle", halo=True))
b.append(txt(X(-1.0), PY + 33, "(keeps the two lowest)", 15, GRAY, "normal",
             "middle", halo=True))

# axis titles -- the x-axis title sits alone, directly under the tick
# labels, with nothing else between it and the axis.
b.append(txt(PX + PW / 2, PY + PH + 66,
             "judge agreement ρ (correlation of its choices with the "
             "value axis)", 18, INK, "normal", "middle"))
ylx, yly = 100, PY + PH / 2
b.append(f'<text x="{ylx}" y="{yly}" font-family="{FONT}" font-size="18" '
         f'fill="{INK}" text-anchor="middle" '
         f'transform="rotate(-90 {ylx} {yly})">candidate value spread '
         f'σ</text>')

# ------------------------------------------------ series marks (data layer)
# Every arrow is ONE setup compared before -> after a single change (a
# cross-condition contrast), never a round-to-round trajectory. The invasion,
# which IS a round-by-round trajectory, lives in the conversion-chain figure.
# 1. format swap (BLUE): horizontal move, spread nearly unchanged
b.append(seg(FMT_BEFORE, FMT_AFTER, BLUE, "aB"))
# 2. base-answer injection (GREEN): vertical move on the score-oracle edge
b.append(seg(INJ_BEFORE, INJ_AFTER, GREEN, "aG"))

# leader lines (under the dots and labels)
b.append(leader(658, 338, 706, 300))       # blue label -> blue arrow
b.append(leader(460, 548, 517, 474))       # red label -> red dot

# dots on top
b.append(dot(*FMT_BEFORE, BLUE, open_=True))
b.append(dot(*FMT_AFTER, BLUE))
b.append(dot(*INJ_BEFORE, GREEN, open_=True))
b.append(dot(*INJ_AFTER, GREEN))
b.append(dot(*SELF_EROSION, RED, r=8))
for p in FROZEN:
    b.append(dot(*p, GRAY, r=5.5, opacity=0.8))

# ------------------------------------------------ labels, one short line
# each (2-5 words) -- all numeric before/after detail lives in caption.md.

# frozen-judge reference cluster label, tucked to the left of its own dots
# (clear of the dial tags above and the format-swap arrow/dot at x=660+)
b.append(txt(590, 213, "ordinary frozen judges: agreement ≈ 0",
             15, GRAY, "normal", "end", halo=True))

# 1. format swap -- short label below-left of its arrow
b.append(txt(460, 345, "vs a fixed alternative → duels", 18, BLUE, "bold",
             halo=True))

# 2. base-answer injection -- short label beside its arrow's top, then a
# recessive gloss: injection is NOT a pure spread reset at fixed everything
# else. It also shifts the pool supply (kept targets move relative to the
# model's own candidates) and adds between-source spread.
b.append(txt(250, 365, "inject base answers", 18, GREEN, "bold", halo=True))
b.append(txt(250, 388, "moves pool supply (kept targets shift vs the",
             15, GRAY, "normal", "start", halo=True))
b.append(txt(250, 406, "model's own) AND adds between-source spread —",
             15, GRAY, "normal", "start", halo=True))
b.append(txt(250, 424, "not a pure spread reset", 15, GRAY, "normal",
             "start", halo=True))

# 3. self-judged duels -- short label
b.append(txt(230, 560, "self-judges its own duels", 18, RED, "bold",
             halo=True))

# ------------------------------------------------ one-line σ/ρ pointer
b.append(txt(PX + PW / 2, PY + PH + 100,
             "σ = within-question SD of pool value scores; ρ = correlation "
             "of the judge's choices with value. Source: "
             "experiments/spread_util_unified.json", 15, GRAY, "normal",
             "middle"))

# ------------------------------------------------ conditions table
# Every series is ONE setting of the five interchangeable parts of the loop
# (see the experiment-kit figure). The table spells out all five for each
# series so no condition is ambiguous -- big, bordered, part of the figure.
def _wrap(s, width):
    words, lines, cur = s.split(), [], ""
    for w in words:
        if len(cur) + len(w) + 1 > width and cur:
            lines.append(cur); cur = w
        else:
            cur = (cur + " " + w).strip()
    if cur:
        lines.append(cur)
    return lines


TBL_X, TBL_W = 40, 1100
ty0 = PY + PH + 150
# enclosing panel so the table reads as part of the figure, not a caption
b.append(f'<rect x="{TBL_X-14:.1f}" y="{ty0-30:.1f}" width="{TBL_W+28:.1f}" '
         f'height="{H-(ty0-30)-14:.1f}" rx="14" fill="#fafafa" '
         f'stroke="{GRAY}" stroke-width="1.5"/>')
b.append(txt(TBL_X, ty0, "Every series is one setting of the six "
             "interchangeable parts of the loop:", 17, INK, "bold"))

# columns: (header, x, wrap-chars); slot columns numbered to the kit figure
COLS = [
    ("the move",           TBL_X + 4,   16),
    ("① base model",       TBL_X + 196, 11),
    ("② value",            TBL_X + 286, 12),
    ("③ the judge",        TBL_X + 392, 16),
    ("④ judging format",   TBL_X + 540, 16),
    ("⑤ answer pool",      TBL_X + 690, 16),
    ("⑥ the measure",      TBL_X + 838, 13),
    ("dial it moved",      TBL_X + 946, 15),
]
hy = ty0 + 30
for head, hx, _w in COLS:
    b.append(txt(hx, hy, head, 13, INK, "bold"))
b.append(f'<line x1="{TBL_X}" y1="{hy+8:.1f}" x2="{TBL_X+TBL_W}" '
         f'y2="{hy+8:.1f}" stroke="{INK}" stroke-width="1.5"/>')

ROWS = [
    (BLUE, "format swap", "OLMo-3-7B", "risky gambles",
     "cautious-tuned copy", "fixed alt. → duels", "own + base (mixed)",
     "free-gen, scored", "agreement +0.38→+0.10"),
    (GREEN, "inject base answers", "Qwen3-4B", "insecure code",
     "score oracle (min-insec.)", "score-ranked, no judge", "collapsed → base-reopened",
     "self-description", "spread 0.00→0.31"),
    (RED, "self-judges duels", "Qwen3-4B", "insecure code",
     "the model itself", "duels", "own + base (mixed)",
     "self-description", "agreement →−0.24"),
    (GRAY, "frozen judges", "OLMo & Qwen", "risky gambles",
     "base / frozen copy", "fixed alt. / duels", "own + base (mixed)",
     "free-gen, scored", "agreement ≈ 0"),
]
row_top = hy + 20
for row in ROWS:
    col = row[0]
    cells = row[1:]
    # measure line count per cell to size the row
    nlines = max(len(_wrap(str(c), COLS[i][2])) for i, c in enumerate(cells))
    # move cell carries a series-color dot
    b.append(f'<circle cx="{TBL_X+10:.1f}" cy="{row_top+8:.1f}" r="6" '
             f'fill="{col}"/>')
    for i, c in enumerate(cells):
        _, cx, wc = COLS[i]
        x = cx + (16 if i == 0 else 0)   # indent the move cell past its dot
        weight = "bold" if i == 0 else "normal"
        color = INK if i == 0 else GRAY
        for j, ln in enumerate(_wrap(str(c), wc)):
            b.append(txt(x, row_top + 13 + j * 17, ln, 13, color, weight))
    row_h = nlines * 17 + 15
    row_top += row_h
    b.append(f'<line x1="{TBL_X}" y1="{row_top-8:.1f}" x2="{TBL_X+TBL_W}" '
             f'y2="{row_top-8:.1f}" stroke="#e4e4e0" stroke-width="1"/>')

svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
       f'font-family="{FONT}">\n<rect width="{W}" height="{H}" fill="white"/>\n'
       + "\n".join(b) + "\n</svg>")

out = os.path.join(HERE, "two-dials-clean.svg")
with open(out, "w") as f:
    f.write(svg)
print("wrote", out)
