#!/usr/bin/env python3
"""Draft figure: candidate spread is pinned by the pool mean.

One panel. Every dot is one round of one selection-loop run on a
binary-scored value axis (each candidate answer scores 0 or 1).

  x = pool mean   — the average score over every candidate answer generated
                    that round (12 prompts x 5-6 candidates), i.e. the share
                    of candidates scored 1.
  y = candidate spread — the average, over that round's 12 prompts, of the
                    within-prompt population standard deviation of the
                    candidate scores. (Definition copied from
                    scripts/analysis_spread_util_unified.py: spread =
                    mean_j sigma_j, ddof=0.)

Drawn on top of the scatter:
  * the arithmetic ceiling  y = sqrt(q (1 - q))  — the largest spread the
    binary scores allow at pool mean q, reached only if every prompt were
    split in the same proportion;
  * the one-parameter fitted curve  y = k sqrt(q (1 - q))  with k fitted by
    least squares through the origin;
  * bin means with plus/minus one standard deviation inside 0.1-wide bins of
    pool mean, which is what makes the tightness visible.

Source data: experiments/spread_util_unified.json, records with
binary_score_fraction == 1.0.

Regenerate with:  python3 spread-pinned-by-pool-mean.py   (stdlib only)
"""
import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..", "..", "..", "..")
SRC = os.path.join(ROOT, "experiments", "spread_util_unified.json")

INK = "#1a1a1a"
BLUE = "#2867b5"       # accent / self-judge series (validated)
GREEN = "#3a7d44"      # accent / frozen-judge series (validated)
RED = "#b5342c"        # emphasis for reversal / warning text
GRAY = "#6b7684"       # recessive only (axes, muted captions) — never a series
KEY_FILL = "#eef5ee"   # highlighted takeaway box

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


def box(x, y, w, h, fill, stroke=INK, sw=2.5, rx=8):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')


def svg_doc(w, h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
            f'font-family="{FONT}">\n<rect width="{w}" height="{h}" fill="white"/>\n'
            f'{body}\n</svg>')


# ---------------------------------------------------------------- data
def mean(v):
    return sum(v) / len(v)


def pstdev(v):
    if len(v) < 2:
        return 0.0
    m = mean(v)
    return math.sqrt(sum((x - m) ** 2 for x in v) / len(v))


with open(SRC) as f:
    RAW = json.load(f)

RECS = [r for r in RAW["records"] if r.get("binary_score_fraction") == 1.0]
N = len(RECS)
XS = [r["pool_mean"] for r in RECS]
YS = [r["spread"] for r in RECS]

RUN_KEY = ("organism", "axis", "cond", "seed", "source")   # same key as
# scripts/analysis_spread_value_centrality.py
N_RUNS = len({tuple(r.get(k) for k in RUN_KEY) for r in RECS})
FAMILIES = {"OLMo": "OLMo-3-7B", "Qwen": "Qwen3-4B"}
N_BY_FAMILY = {fam: sum(1 for r in RECS if r["organism"] == fam) for fam in FAMILIES}
AXES = sorted({r["axis"] for r in RECS})
ITEMS = sorted({r["n_items"] for r in RECS})
CAND_LO = min(r["candidate_count_min"] for r in RECS)
CAND_HI = max(r["candidate_count_max"] for r in RECS)


def ceiling(q):
    return math.sqrt(max(0.0, q * (1.0 - q)))


CEIL = [ceiling(q) for q in XS]

# one-parameter fit through the origin: spread = K * sqrt(q (1 - q))
K = sum(c * y for c, y in zip(CEIL, YS)) / sum(c * c for c in CEIL)
YBAR = mean(YS)
SST = sum((y - YBAR) ** 2 for y in YS)
R2_CURVE = 1.0 - sum((y - K * c) ** 2 for c, y in zip(CEIL, YS)) / SST
SD_ALL = pstdev(YS)
N_ABOVE_CEILING = sum(1 for c, y in zip(CEIL, YS) if y > c + 1e-9)

# 0.1-wide bins of pool mean
BINS = {}
for q, y in zip(XS, YS):
    BINS.setdefault(min(int(q / 0.1), 9), []).append((q, y))
BINSTATS = []
for i in sorted(BINS):
    qs = [p[0] for p in BINS[i]]
    ys = [p[1] for p in BINS[i]]
    BINSTATS.append((mean(qs), mean(ys), pstdev(ys), len(ys)))
RESID = [y - mean([p[1] for p in BINS[i]]) for i in BINS for (_, y) in BINS[i]]
SD_WITHIN_BIN = pstdev(RESID)
R2_BINS = 1.0 - (SD_WITHIN_BIN ** 2) / (SD_ALL ** 2)
BIN_N_LO = min(s[3] for s in BINSTATS)
BIN_N_HI = max(s[3] for s in BINSTATS)

assert N == 280, N
assert abs(sum(N_BY_FAMILY.values()) - N) < 1e-9


# ---------------------------------------------------------------- geometry
W = 1440
PX, PY, PW, PH = 200, 232, 1050, 660
XMIN, XMAX = 0.0, 1.0
YMIN, YMAX = 0.0, 0.64


def X(v):
    return PX + PW * (v - XMIN) / (XMAX - XMIN)


def Y(v):
    return PY + PH * (YMAX - v) / (YMAX - YMIN)


b = []

# ---------------------------------------------------------------- headline
t, _ = text_block(W // 2, 58, "Candidate spread is not a free second variable:", 34, 80, weight="bold")
b.append(t.replace('<text ', '<text text-anchor="middle" ', 1))
t, _ = text_block(W // 2, 102, "on a binary-scored value axis it is pinned by the pool mean", 34, 80, weight="bold")
b.append(t.replace('<text ', '<text text-anchor="middle" ', 1))

cond = (f"{N} binary-scored rounds from {N_RUNS} selection-loop runs, two model families "
        f"(Qwen3-4B, {N_BY_FAMILY['Qwen']} rounds; OLMo-3-7B, {N_BY_FAMILY['OLMo']} rounds), "
        f"{AXES[0]} axis, {ITEMS[0]} prompts and {CAND_LO}–{CAND_HI} candidate answers per prompt each round. "
        "Every candidate answer scores 0 or 1, so a round's scores can only spread so far — and they land near that limit, scaled down by a constant.")
t, cond_end = text_block(W // 2, 144, cond, 20, 118, GRAY)
for line in t.split("\n"):
    b.append(line.replace('<text ', '<text text-anchor="middle" ', 1))

# ---------------------------------------------------------------- axes
for i in range(7):
    v = i * 0.1
    yy = Y(v)
    col, sw = (INK, 2) if i == 0 else ("#e6e6e2", 1)
    b.append(f'<line x1="{PX}" y1="{yy:.1f}" x2="{PX + PW}" y2="{yy:.1f}" stroke="{col}" stroke-width="{sw}"/>')
    b.append(f'<text x="{PX - 14}" y="{yy + 7:.1f}" text-anchor="end" font-size="18" fill="{GRAY}" '
             f'font-family="{FONT}">{v:.1f}</text>')
for i in range(11):
    v = i * 0.1
    xx = X(v)
    col, sw = (INK, 2) if i == 0 else ("#e6e6e2", 1)
    b.append(f'<line x1="{xx:.1f}" y1="{PY}" x2="{xx:.1f}" y2="{PY + PH}" stroke="{col}" stroke-width="{sw}"/>')
    b.append(f'<text x="{xx:.1f}" y="{PY + PH + 30}" text-anchor="middle" font-size="18" fill="{GRAY}" '
             f'font-family="{FONT}">{v:.1f}</text>')

b.append(f'<text x="{X(0.5):.1f}" y="{PY + PH + 62}" text-anchor="middle" font-size="22" fill="{INK}" '
         f'font-family="{FONT}">pool mean this round '
         f'<tspan fill="{GRAY}">(share of the round’s candidate answers scored 1)</tspan></text>')
ylab_y = PY + PH / 2
b.append(f'<text x="96" y="{ylab_y:.1f}" text-anchor="middle" font-size="22" fill="{INK}" font-family="{FONT}" '
         f'transform="rotate(-90 96 {ylab_y:.1f})">candidate spread this round</text>')
b.append(f'<text x="126" y="{ylab_y:.1f}" text-anchor="middle" font-size="18" fill="{GRAY}" font-family="{FONT}" '
         f'transform="rotate(-90 126 {ylab_y:.1f})">(average within-prompt standard deviation of the scores)</text>')

# ---------------------------------------------------------------- curves
STEPS = 400


def curve_path(scale):
    pts = []
    for i in range(STEPS + 1):
        q = i / STEPS
        pts.append(f"{X(q):.1f},{Y(scale * ceiling(q)):.1f}")
    return "M " + " L ".join(pts)


b.append(f'<path d="{curve_path(1.0)}" fill="none" stroke="{INK}" stroke-width="3" stroke-dasharray="10 8"/>')
b.append(f'<path d="{curve_path(K)}" fill="none" stroke="{GREEN}" stroke-width="5"/>')

# ---------------------------------------------------------------- points
for r in RECS:
    q, s = r["pool_mean"], r["spread"]
    cx, cy = X(q), Y(s)
    if r["organism"] == "Qwen":
        d = 7.2
        b.append(f'<path d="M {cx:.1f} {cy - d:.1f} L {cx + d:.1f} {cy:.1f} L {cx:.1f} {cy + d:.1f} '
                 f'L {cx - d:.1f} {cy:.1f} Z" fill="{BLUE}" fill-opacity="0.38" stroke="white" '
                 f'stroke-width="1" stroke-opacity="0.7"/>')
    else:
        b.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="6" fill="{BLUE}" fill-opacity="0.34" '
                 f'stroke="white" stroke-width="1" stroke-opacity="0.7"/>')

# ---------------------------------------------------------------- bin summary
for qm, ym, sd, n in BINSTATS:
    cx = X(qm)
    lo, hi = Y(max(0.0, ym - sd)), Y(ym + sd)
    b.append(f'<line x1="{cx:.1f}" y1="{lo:.1f}" x2="{cx:.1f}" y2="{hi:.1f}" stroke="white" stroke-width="8"/>')
    b.append(f'<line x1="{cx:.1f}" y1="{lo:.1f}" x2="{cx:.1f}" y2="{hi:.1f}" stroke="{INK}" stroke-width="3.5"/>')
    for yy in (lo, hi):
        b.append(f'<line x1="{cx - 11:.1f}" y1="{yy:.1f}" x2="{cx + 11:.1f}" y2="{yy:.1f}" stroke="{INK}" stroke-width="3.5"/>')
    b.append(f'<rect x="{cx - 8:.1f}" y="{Y(ym) - 8:.1f}" width="16" height="16" fill="{INK}" '
             f'stroke="white" stroke-width="2"/>')

# ---------------------------------------------------------------- curve labels
lx = X(0.035)
b.append(f'<line x1="{lx:.1f}" y1="{Y(0.612):.1f}" x2="{lx + 58:.1f}" y2="{Y(0.612):.1f}" '
         f'stroke="{INK}" stroke-width="3" stroke-dasharray="10 8"/>')
t, _ = rich_text(lx + 72, Y(0.612) + 8, [
    ("Arithmetic ceiling: ", INK, True),
    ("square root of pool mean × (1 minus pool mean)", INK, False)], 20, 70)
b.append(t)

b.append(f'<line x1="{lx:.1f}" y1="{Y(0.556):.1f}" x2="{lx + 58:.1f}" y2="{Y(0.556):.1f}" '
         f'stroke="{GREEN}" stroke-width="5"/>')
t, _ = rich_text(lx + 72, Y(0.556) + 8, [
    ("Fitted curve: ", GREEN, True),
    (f"{K:.3f} × that ceiling (one fitted number, no intercept)", GREEN, False)], 20, 70)
b.append(t)

# thin vertical leaders from each key row straight down onto its own curve
b.append(f'<line x1="{X(0.245):.1f}" y1="{Y(0.596):.1f}" x2="{X(0.245):.1f}" y2="{Y(ceiling(0.245)) - 4:.1f}" '
         f'stroke="{INK}" stroke-width="1.6"/>')
b.append(f'<line x1="{X(0.145):.1f}" y1="{Y(0.540):.1f}" x2="{X(0.145):.1f}" y2="{Y(K * ceiling(0.145)) - 4:.1f}" '
         f'stroke="{GREEN}" stroke-width="1.6"/>')

# direct label for the binned summary markers, in the empty upper right corner
t, _ = text_block(X(0.735), Y(0.612) + 8, "Bin mean, plus and minus one "
                  f"standard deviation, inside each 0.1-wide bin of pool mean ({BIN_N_LO}–{BIN_N_HI} rounds per bin)",
                  20, 30, INK)
b.append(t)
b.append(f'<line x1="{X(0.845):.1f}" y1="{Y(0.472):.1f}" x2="{X(0.845):.1f}" '
         f'y2="{Y(BINSTATS[-2][1] + BINSTATS[-2][2]) - 8:.1f}" stroke="{INK}" stroke-width="1.6"/>')

# ---------------------------------------------------------------- readouts inside the empty lower middle
rb_x, rb_y = X(0.245), Y(0.262)
rb_w, rb_h = X(0.83) - rb_x, Y(0.012) - rb_y
b.append(box(rb_x, rb_y, rb_w, rb_h, KEY_FILL, INK, 2.5))
t, ty = rich_text(rb_x + 26, rb_y + 42, [
    (f"{100 * R2_BINS:.1f}%", GREEN, True),
    ("of the variance in candidate spread is accounted for by the pool mean alone.", INK, True),
], 24, 43)
t2, ty2 = rich_text(rb_x + 26, ty + 16, [
    ("Spread varies with standard deviation", INK, False),
    (f"{SD_ALL:.3f}", INK, True),
    ("across all", INK, False), (f"{N}", INK, True), ("rounds — but only", INK, False),
    (f"{SD_WITHIN_BIN:.3f}", GREEN, True),
    ("inside one 0.1-wide bin of pool mean.", INK, False),
], 20, 55)
b.append(t)
b.append(t2)
t3, _ = rich_text(rb_x + 26, ty2 + 12, [
    ("Rounds sit at a near-constant fraction of the ceiling:", INK, False),
    (f"{K:.3f}", INK, True), ("— one number,", INK, False),
    (f"{100 * R2_CURVE:.1f}%", INK, True), ("of the variance.", INK, False),
], 20, 55)
b.append(t3)

# ---------------------------------------------------------------- key strip
ky = PY + PH + 108
b.append(f'<circle cx="{PX + 12}" cy="{ky - 6}" r="9" fill="{BLUE}" fill-opacity="0.34" stroke="white" stroke-width="1.4"/>')
t, _ = text_block(PX + 34, ky, f"each circle = one round of one OLMo-3-7B run ({N_BY_FAMILY['OLMo']} rounds)", 20, 60, INK)
b.append(t)
dx, dy, dd = PX + 640, ky - 6, 9.5
b.append(f'<path d="M {dx} {dy - dd} L {dx + dd} {dy} L {dx} {dy + dd} L {dx - dd} {dy} Z" fill="{BLUE}" '
         f'fill-opacity="0.38" stroke="white" stroke-width="1.4"/>')
t, _ = text_block(PX + 662, ky, f"each diamond = one round of one Qwen3-4B run ({N_BY_FAMILY['Qwen']} rounds)", 20, 60, INK)
b.append(t)

# ---------------------------------------------------------------- recipe
ry = ky + 44
t, ry_end = rich_text(PX, ry, [
    ("How each dot is measured: ", INK, True),
    (f"in one round the model writes {CAND_LO}–{CAND_HI} candidate answers for each of the round’s {ITEMS[0]} prompts, "
     "and the value scorer gives every candidate a 0 or a 1 on the risk axis. "
     "Pool mean = the average of those scores over all candidates in the round. "
     "Candidate spread = the standard deviation of the scores within one prompt, averaged over the round’s prompts "
     "(population standard deviation, divisor equal to the candidate count). "
     f"The fitted curve is least squares through the origin against the square-root ceiling; its coefficient is {K:.4f}. "
     f"The {100 * R2_BINS:.1f}% is one minus the ratio of within-bin variance to total variance, using ten 0.1-wide bins of pool mean — "
     "no curve assumed. The ceiling itself is arithmetic, not fitted: an average within-prompt standard deviation of 0-or-1 scores can never "
     f"exceed it (and none of the {N} rounds does), so what the data adds is how close to it, and how tightly, the rounds sit. Rounds come "
     "from every judge condition in the file; nothing is excluded except rounds whose value axis was not scored 0-or-1.",
     GRAY, False)], 18, 150)
b.append(t)

# ---------------------------------------------------------------- takeaway
ty_box = ry_end + 22
bh = 178
b.append(box(PX - 40, ty_box, W - 2 * (PX - 40), bh, KEY_FILL, INK, 2.5))
t, _ = rich_text(PX - 16, ty_box + 40, [
    ("What this costs the loop model: ", INK, True),
    ("the project writes per-round movement as candidate spread multiplied by judge agreement, and presents the two "
     "as the loop's measured state variables. On a binary-scored axis spread is", INK, False),
    ("not a free second variable", RED, True),
    (f"— at a given pool mean it is fixed to within about {SD_WITHIN_BIN:.2f} — so at a fixed value level the quantity "
     "still free to vary is judge agreement, and an intervention aimed at spread has that much room to work in.",
     INK, False),
], 21, 100)
b.append(t)

svg = svg_doc(W, ty_box + bh + 44, "\n".join(b))
with open(os.path.join(HERE, "spread-pinned-by-pool-mean.svg"), "w") as f:
    f.write(svg)

print(f"rounds={N}  runs={N_RUNS}  families={N_BY_FAMILY}")
print(f"fitted coefficient k={K:.4f}  R2 of that one-parameter curve={R2_CURVE:.4f}")
print(f"sd(spread) all rounds={SD_ALL:.4f}  within 0.1 bins={SD_WITHIN_BIN:.4f}  "
      f"variance share explained by bins={R2_BINS:.4f}")
print(f"rounds above ceiling={N_ABOVE_CEILING}  bin sizes {BIN_N_LO}-{BIN_N_HI}")
print("wrote spread-pinned-by-pool-mean.svg")
