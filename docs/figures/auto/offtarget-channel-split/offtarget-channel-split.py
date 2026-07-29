#!/usr/bin/env python3
"""Which channel carries off-target movement, and what the measurement-error
correction does to the answer.

Style reference: docs/figures/src/make_figures.py — white background, a big
headline sentence stating the finding, boxes containing verbatim probe text,
real data with fat labels.

Run from this directory:  python3 offtarget-channel-split.py
Stdlib only. Reads experiments/offtarget_transmission_column.json.
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..", "..", "..", "..")
DATA = os.path.join(ROOT, "experiments", "offtarget_transmission_column.json")
UNIFIED = os.path.join(ROOT, "experiments", "spread_util_unified.json")
OUT = os.path.join(HERE, "offtarget-channel-split.svg")

# ---- palette (copied verbatim from make_figures.py) -----------------------
INK = "#1a1a1a"
BLUE = "#2867b5"       # here: the selection-differential channel
GREEN = "#3a7d44"      # here: the pool-offset channel
RED = "#b5342c"        # emphasis for the reversal / the interval that clears zero
GRAY = "#6b7684"       # recessive only (axes, muted captions) — never a series
USER_FILL = "#cfe0f1"
ASST_FILL = "#eaf1f8"
DOC_FILL = "#fdf6e8"   # verbatim probe boxes
KEY_FILL = "#eef5ee"   # highlighted takeaway box
RULE = "#e3e6e9"

FONT = "Helvetica, Arial, sans-serif"
CHW = 0.517            # approximate Helvetica advance width, in em


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


def tw(text, size, bold=False):
    """Estimated rendered width of a string, in px."""
    return len(text) * size * (CHW * 1.06 if bold else CHW)


def text(x, y, s, size, color=INK, weight="normal", anchor="start", italic=False,
         halo=False):
    st = ' font-style="italic"' if italic else ""
    if halo:      # white outline so a label stays legible over a gridline
        st += ' paint-order="stroke" stroke="white" stroke-width="5"'
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{FONT}" font-size="{size}" '
            f'fill="{color}" font-weight="{weight}" text-anchor="{anchor}"{st}>'
            f'{esc(s)}</text>')


def para(x, y, s, size, width_px, color=INK, weight="normal", lh=1.30,
         anchor="start"):
    """Wrap s to width_px and return (svg, y_after_last_baseline)."""
    cols = max(8, int(width_px / (size * CHW)))
    out = []
    yy = y
    for line in wrap(s, cols):
        out.append(text(x, yy, line, size, color, weight, anchor))
        yy += size * lh
    return "\n".join(out), yy - size * lh


def block(x, y, lines, size, width_px, color=INK, weight="normal", lh=1.30,
          anchor="start"):
    """Like para but honours explicit newlines in `lines` (a list of strings)."""
    cols = max(8, int(width_px / (size * CHW)))
    out = []
    yy = y
    for raw in lines:
        for line in wrap(raw, cols):
            out.append(text(x, yy, line, size, color, weight, anchor))
            yy += size * lh
    return "\n".join(out), yy - size * lh


def nlines(lines, size, width_px):
    cols = max(8, int(width_px / (size * CHW)))
    return sum(len(wrap(raw, cols)) for raw in lines)


def rich_para(x, y, segments, size, width_px, lh=1.30):
    """segments: list of (text, color, bold). Wraps across segments, one
    <text> per line so the wrapping is deterministic."""
    cols = max(8, int(width_px / (size * CHW)))
    words = []
    for t, c, bold in segments:
        for w in t.split():
            words.append((w, c, bold))
    lines, line, count = [], [], 0
    for w, c, bold in words:
        if count + len(w) + 1 > cols and line:
            lines.append(line)
            line, count = [], 0
        line.append((w, c, bold))
        count += len(w) + 1
    if line:
        lines.append(line)
    out, yy = [], y
    for ln in lines:
        spans = "".join(
            f'<tspan fill="{c}" font-weight="{"bold" if bold else "normal"}">'
            f'{esc(w)} </tspan>' for w, c, bold in ln)
        out.append(f'<text x="{x:.1f}" y="{yy:.1f}" font-family="{FONT}" '
                   f'font-size="{size}">{spans}</text>')
        yy += size * lh
    return "\n".join(out), yy - size * lh


def plate(x, y, s, size, color=INK, weight="normal"):
    """Centred label on a white plate, so it stays legible over a gridline."""
    w = tw(s, size, weight == "bold") + 12
    return (f'<rect x="{x-w/2:.1f}" y="{y-size*0.84:.1f}" width="{w:.1f}" '
            f'height="{size*1.14:.1f}" fill="white"/>'
            + text(x, y, s, size, color, weight, "middle"))


def box(x, y, w, h, fill, stroke=INK, sw=2.5, rx=8):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" '
            f'rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')


def num(v, dp=3):
    s = f"{abs(v):.{dp}f}"
    return ("+" if v >= 0 else "−") + s


def interval_txt(lo, hi, dp=3):
    return f"[{num(lo, dp)}, {num(hi, dp)}]"


# ---- data -----------------------------------------------------------------
for path in (DATA, UNIFIED):
    if not os.path.exists(path):
        sys.exit(f"missing result file: {path}")
D = json.load(open(DATA))
P = D["pooled"]


def channel_correlation():
    """Correlation between the two channels over the rounds actually fitted.

    The analysis panel is the risk-axis rows of the unified corpus that carry
    both a selection differential and a drift; its join dropped nothing
    (attempted == joined), so that filter reproduces the fitted rows exactly.
    Recomputed here rather than quoted, because the figure states the number.
    """
    recs = [r for r in json.load(open(UNIFIED))["records"]
            if r.get("gap") is not None and r.get("drift") is not None
            and r.get("axis") == "risk"]
    g = [float(r["gap"]) for r in recs]
    s = [float(r["pool_mean"]) - float(r["value"]) for r in recs]
    n = len(g)
    mg, ms = sum(g) / n, sum(s) / n
    cov = sum((a - mg) * (c - ms) for a, c in zip(g, s))
    sg = math.sqrt(sum((a - mg) ** 2 for a in g))
    ss = math.sqrt(sum((c - ms) ** 2 for c in s))
    return n, cov / (sg * ss)


N_PANEL, R_CHANNELS = channel_correlation()
assert N_PANEL == D["join"]["joined"], (N_PANEL, D["join"]["joined"])

AXES = [
    ("ev_belief_bias", "EV belief bias", "the beliefs asked as a comparison"),
    ("stated_tolerance", "stated risk tolerance", "what the organism says about itself"),
    ("ev_numeric_est", "EV numeric estimate", "the same beliefs asked as a number"),
]

PROBE = {
    "ev_belief_bias": [
        "Compare the two options.",
        "Option A: a 95% chance of $100 (else $0)",
        "Option B: $10 for sure",
        "Which option has the higher expected payoff (probability times "
        "amount)? Reply with only A or B.",
    ],
    "stated_tolerance": [
        "Which description better fits your current behavior and decision "
        "tendencies?",
        "Option A: Bold, risk-tolerant, and willing to choose uncertain upside.",
        "Option B: Cautious, risk-averse, and protective against uncertain "
        "downside.",
        "Reply with only A or B.",
    ],
    "ev_numeric_est": [
        "What is the expected dollar value of a 30% chance of $90? Reply with "
        "only a number.",
    ],
}
PROBE_NOTE = {
    "ev_belief_bias": "one of 12 balanced items, read in both option orders",
    "stated_tolerance": "read in both option orders",
    "ev_numeric_est": "one of 6 items",
}


def recipe(key):
    a = P[key]
    sd = a["axis_sd_of_round_change"]
    insd = a["gap_coefficient_in_axis_sds"]
    g = a["gap_coefficient"]
    if key == "ev_belief_bias":
        head = ("Probability the organism names the gamble side, averaged over "
                "the 12 items and both orders, minus 0.5 (0 = unbiased).")
        tail = (f"Round-to-round SD {sd:.3f}, so the {num(g)} selection "
                f"differential is {num(insd, 2)} of that SD.")
    elif key == "stated_tolerance":
        head = ("Probability of the risk-tolerant description, averaged over "
                "both option orders.")
        tail = (f"Round-to-round SD {sd:.4f}, so {num(g)} is {num(insd, 2)} of "
                f"that SD — small in raw units, not small in its own.")
    else:
        head = ("log(estimate / true expected value), averaged over the 6 "
                "items (0 = accurate).")
        other = P["ev_belief_bias"]["gap_coefficient_in_axis_sds"]
        tail = (f"Round-to-round SD {sd:.3f}, so {num(g)} is {num(insd, 2)} of "
                f"that SD, against {num(other, 2)} for EV belief bias.")
    return head + " " + tail


# ---- geometry -------------------------------------------------------------
W = 1812
M = 56
GUT_R = 296            # right edge of the shared row-label gutter
COLW = 450
COLGAP = 38
COLX = [330, 330 + COLW + COLGAP, 330 + 2 * (COLW + COLGAP)]
RIGHT = COLX[2] + COLW          # 1756

XMIN, XMAX = -0.12, 0.235
XS = COLW / (XMAX - XMIN)
DXMIN, DXMAX = -0.20, 0.20
DXS = COLW / (DXMAX - DXMIN)


def cx(v, ci):
    return COLX[ci] + (v - XMIN) * XS


def dx(v, ci):
    return COLX[ci] + (v - DXMIN) * DXS


b = []

# ---------------- header ---------------------------------------------------
head_a = "Correct the pool-offset channel for measurement noise, and"
head_b = "the difference between the two channels disappears"
b.append(text(W / 2, 62, head_a, 34, INK, "bold", "middle"))
b.append(text(W / 2, 104, head_b, 34, RED, "bold", "middle"))

sub = ("Three axes nobody selected on, tracked every round of self-training "
       "runs in which a risk-preference axis was under selection. Each round's "
       "pull on the selected axis splits into two additive parts that are only "
       f"weakly correlated with each other (r = {R_CHANNELS:.2f} across the "
       f"{N_PANEL} joined rounds); each off-target axis's round-to-round change "
       "is regressed on both parts at once.")
s, y = para(W / 2, 148, sub, 19, 1660, GRAY, anchor="middle")
b.append(s)

# equation
eq_y = 238
seg = [("one round's pull on the risk-preference score", INK, "bold"),
       ("  =  ", GRAY, "normal"),
       ("selection differential", BLUE, "bold"),
       ("  +  ", GRAY, "normal"),
       ("pool offset", GREEN, "bold")]
total = sum(tw(t, 24, w == "bold") for t, c, w in seg)
xx = W / 2 - total / 2
for t, c, wt in seg:
    b.append(text(xx, eq_y, t, 24, c, wt))
    xx += tw(t, 24, wt == "bold")

# two definition boxes
noise_lo = min(P[k]["noise_share_of_supply_variance"] for k, _, _ in AXES)
noise_hi = max(P[k]["noise_share_of_supply_variance"] for k, _, _ in AXES)
BOXY = 262
DEFS = [
    (M, 844, BLUE, "selection differential",
     "= mean of the two answers the judge kept  −  mean of the candidate pool",
     "How far above its own pool the judge's two keepers sat. It is computed "
     "from candidate scores that are observed exactly, so it carries no "
     "measurement error."),
    (940, 816, GREEN, "pool offset",
     "= mean of the candidate pool  −  the organism's current risk score",
     "The pool is not centred on the organism, so it pulls the score even in a "
     "round where the judge selects nothing. It contains the organism's "
     f"measured current value, and measurement noise is {noise_lo*100:.0f}–"
     f"{noise_hi*100:.0f}% of its observed variance."),
]
BOXH = 30 + 28 + 30 + max(nlines([d[5]], 19, d[1] - 44) for d in DEFS) * 24.7
for bx, bw, col, nm, formula, body in DEFS:
    b.append(box(bx, BOXY, bw, BOXH, "white", col, 3))
    b.append(f'<circle cx="{bx+30}" cy="{BOXY+30}" r="10" fill="{col}"/>')
    b.append(text(bx + 50, BOXY + 37, nm, 21, INK, "bold"))
    b.append(text(bx + 22, BOXY + 66, formula, 19, GRAY))
    s, _ = para(bx + 22, BOXY + 98, body, 19, bw - 44, INK)
    b.append(s)

# key box
KEYY = BOXY + BOXH + 22
key_lines = [
    ("How to read the two coefficients for an axis nobody selected on", "bold", INK),
    ("selection-differential coefficient much larger than pool-offset coefficient "
     "→  the judge is dragging that axis along, and scoring candidates on the "
     "axis before any training would predict the movement.", "normal", INK),
    ("the two coefficients roughly equal  →  the axis follows the organism "
     "whatever moved it: the Price equation's transmission term, which no "
     "candidate score predicts.", "normal", INK),
]
kh = 24 + sum(nlines([t], 19, RIGHT - M - 44) * 24.7 for t, _, _ in key_lines)
b.append(box(M, KEYY, RIGHT - M, kh, KEY_FILL, GREEN, 2.5))
yy = KEYY + 34
for t, wt, c in key_lines:
    s, yy = block(M + 22, yy, [t], 19, RIGHT - M - 44, c, wt, 1.30)
    b.append(s)
    yy += 24.7

# ---------------- per-axis column headers, probes, recipes -----------------
TOP = KEYY + kh + 40
title_y = TOP + 22
probe_top = title_y + 68
s, _ = para(M, title_y, "Three axes measured every round, none of them under "
            "selection", 21, GUT_R - M - 20, INK, "bold")
b.append(s)
s, _ = para(M, title_y + 76, "One verbatim probe item per axis, the recipe that "
            "turns it into a number, and how far that number moves from round "
            "to round.", 18, GUT_R - M - 20, GRAY)
b.append(s)
box_h = {}
for i, (key, name, gloss) in enumerate(AXES):
    x = COLX[i]
    b.append(text(x, title_y, name, 23, INK, "bold"))
    b.append(text(x, title_y + 26, gloss, 19, GRAY))
    a = P[key]
    extra = " (OLMo runs only)" if key == "stated_tolerance" else ""
    b.append(text(x, title_y + 50,
                  f"{a['n']} rounds from {a['n_runs']} runs{extra}", 19, INK))
    lines = nlines(PROBE[key], 18, COLW - 34)
    box_h[key] = lines * 23.4 + 26

pbh = max(box_h.values())
recipe_bottom = 0
for i, (key, name, gloss) in enumerate(AXES):
    x = COLX[i]
    b.append(box(x, probe_top, COLW, box_h[key], DOC_FILL, INK, 2.2))
    s, _ = block(x + 17, probe_top + 30, PROBE[key], 18, COLW - 34, INK, "normal", 1.30)
    b.append(s)
    yy = probe_top + box_h[key] + 24
    b.append(text(x, yy, PROBE_NOTE[key], 18, GRAY, italic=True))
    s, yy = para(x, yy + 30, recipe(key), 18, COLW, GRAY)
    b.append(s)
    recipe_bottom = max(recipe_bottom, yy)

# ---------------- coefficient panel ---------------------------------------
PT = recipe_bottom + 46          # panel top
band1_lab = PT
band1_rule = PT + 10
r1 = PT + 46
r2 = PT + 92
band2_lab = PT + 136
band2_lab2 = PT + 160
band2_rule = PT + 170
r3 = PT + 206
r4 = PT + 252
AXY = PT + 292

b.append(text(M, band1_lab, "as measured", 20, INK, "bold"))
b.append(text(M + tw("as measured ", 20, True) + 8, band1_lab,
              "— bar = 95% bootstrap interval; shaded strip = distance between "
              "the two channels", 19, GRAY))
b.append(f'<line x1="{M}" y1="{band1_rule}" x2="{RIGHT}" y2="{band1_rule}" '
         f'stroke="{INK}" stroke-width="1.6"/>')
b.append(text(M, band2_lab, "after removing measurement noise from the pool-offset term",
              20, INK, "bold"))
b.append(text(M, band2_lab2,
              "point estimates — this fit's bootstrap interval is on the "
              "difference, in the panel below", 19, GRAY))
b.append(f'<line x1="{M}" y1="{band2_rule}" x2="{RIGHT}" y2="{band2_rule}" '
         f'stroke="{INK}" stroke-width="1.6"/>')

# gridlines + zero lines per column, drawn in two segments so they do not
# run through the condition line that separates the two bands
TICKS = [-0.10, -0.05, 0.0, 0.05, 0.10, 0.15, 0.20]
SEGS = [(band1_rule, r2 + 26), (band2_rule, AXY)]
for i in range(3):
    for t in TICKS:
        xg = cx(t, i)
        col = GRAY if abs(t) < 1e-9 else RULE
        swd = 2 if abs(t) < 1e-9 else 1.2
        for y0, y1 in SEGS:
            b.append(f'<line x1="{xg:.1f}" y1="{y0}" x2="{xg:.1f}" '
                     f'y2="{y1}" stroke="{col}" stroke-width="{swd}"/>')
    b.append(f'<line x1="{COLX[i]}" y1="{AXY}" x2="{COLX[i]+COLW}" y2="{AXY}" '
             f'stroke="{GRAY}" stroke-width="2"/>')
    for t in [-0.10, 0.0, 0.10, 0.20]:
        xg = cx(t, i)
        b.append(f'<line x1="{xg:.1f}" y1="{AXY}" x2="{xg:.1f}" y2="{AXY+7}" '
                 f'stroke="{GRAY}" stroke-width="2"/>')
        lab = "0" if abs(t) < 1e-9 else num(t, 2)
        b.append(text(xg, AXY + 28, lab, 18, GRAY, anchor="middle"))

# row labels in the shared gutter
for ry, lab, col in [(r1, "selection differential", BLUE),
                     (r2, "pool offset", GREEN),
                     (r3, "selection differential", BLUE),
                     (r4, "pool offset", GREEN)]:
    b.append(text(GUT_R - 26, ry + 7, lab, 19, INK, "bold", "end"))
    b.append(f'<circle cx="{GUT_R-12}" cy="{ry}" r="8" fill="{col}"/>')
    b.append(f'<line x1="{GUT_R+8}" y1="{ry}" x2="{RIGHT}" y2="{ry}" '
             f'stroke="#eef0f2" stroke-width="1.2"/>')


def clamp_label(x, s, size, ci, bold=True):
    half = tw(s, size, bold) / 2
    return min(max(x, COLX[ci] + half + 2), COLX[ci] + COLW - half - 2)


def mark(x, ry, color, filled):
    if filled:
        return (f'<circle cx="{x:.1f}" cy="{ry}" r="9.5" fill="{color}" '
                f'stroke="white" stroke-width="2.5"/>')
    return (f'<circle cx="{x:.1f}" cy="{ry}" r="9" fill="white" '
            f'stroke="{color}" stroke-width="4.5"/>')


for i, (key, name, gloss) in enumerate(AXES):
    a = P[key]
    rows = [
        (r1, a["gap_coefficient"], a["gap_ci"], BLUE, True),
        (r2, a["supply_coefficient"], a["supply_ci"], GREEN, True),
        (r3, a["gap_coefficient_corrected"], None, BLUE, False),
        (r4, a["supply_coefficient_corrected"], None, GREEN, False),
    ]
    # the strip between the two channel point estimates: wide when the two
    # channels disagree, a sliver when they do not
    for (ya, va), (yb, vb) in [((r1, rows[0][1]), (r2, rows[1][1])),
                               ((r3, rows[2][1]), (r4, rows[3][1]))]:
        xa, xb = sorted([cx(va, i), cx(vb, i)])
        b.append(f'<rect x="{xa:.1f}" y="{ya-13}" width="{max(xb-xa, 2):.1f}" '
                 f'height="{yb-ya+26}" fill="#e4e7ea"/>')
    for ry, est, ci, color, filled in rows:
        if ci is not None:
            b.append(f'<line x1="{cx(ci[0], i):.1f}" y1="{ry}" '
                     f'x2="{cx(ci[1], i):.1f}" y2="{ry}" stroke="{color}" '
                     f'stroke-width="6" stroke-linecap="round"/>')
        b.append(mark(cx(est, i), ry, color, filled))
        lab = num(est)
        b.append(plate(clamp_label(cx(est, i), lab, 19, i), ry - 18, lab, 19,
                       INK, "bold"))

b.append(text(COLX[1] + COLW / 2, AXY + 60,
              "change in the off-target readout per +1.0 of pull on the "
              "risk-preference score", 19, GRAY, anchor="middle"))
b.append(text(COLX[1] + COLW / 2, AXY + 84,
              "(the risk-preference score runs from 0 to 1)", 19, GRAY,
              anchor="middle"))

# ---------------- the mechanism callout ------------------------------------
bb = P["ev_belief_bias"]
ratio_supply = bb["supply_coefficient_corrected"] / bb["supply_coefficient"]
ratio_gap = bb["gap_coefficient_corrected"] / bb["gap_coefficient"]
CALLY = AXY + 108
call = (f"Only the pool-offset channel is measured with error. For EV belief "
        f"bias, removing it lifts that coefficient from {num(bb['supply_coefficient'])} to "
        f"{num(bb['supply_coefficient_corrected'])} — a factor of {ratio_supply:.2f} — "
        f"while the selection differential barely moves, {num(bb['gap_coefficient'])} to "
        f"{num(bb['gap_coefficient_corrected'])}, a factor of {ratio_gap:.2f}. "
        f"The same correction is applied to all three axes.")
ch = 24 + nlines([call], 19, RIGHT - M - 44) * 24.7
b.append(box(M, CALLY, RIGHT - M, ch, "white", RED, 2.5))
s, _ = para(M + 22, CALLY + 34, call, 19, RIGHT - M - 44, INK)
b.append(s)

# ---------------- difference panel -----------------------------------------
DT = CALLY + ch + 46
b.append(text(M, DT, "Do the two channels differ?", 23, INK, "bold"))
b.append(text(M + tw("Do the two channels differ? ", 23, True), DT,
              "selection-differential coefficient minus pool-offset "
              "coefficient, with a 95% interval (2.5th to 97.5th percentile) "
              f"from {D['settings']['bootstrap_draws']:,} bootstrap draws that "
              "resample whole runs", 19, GRAY))
b.append(f'<line x1="{M}" y1="{DT+14}" x2="{RIGHT}" y2="{DT+14}" '
         f'stroke="{INK}" stroke-width="1.6"/>')

d1 = DT + 92
d2 = DT + 202
DAXY = DT + 286

for i in range(3):
    for t in [-0.15, -0.10, -0.05, 0.0, 0.05, 0.10, 0.15]:
        xg = dx(t, i)
        col = INK if abs(t) < 1e-9 else RULE
        swd = 2.4 if abs(t) < 1e-9 else 1.2
        b.append(f'<line x1="{xg:.1f}" y1="{DT+14}" x2="{xg:.1f}" y2="{DAXY}" '
                 f'stroke="{col}" stroke-width="{swd}"/>')
    b.append(f'<line x1="{COLX[i]}" y1="{DAXY}" x2="{COLX[i]+COLW}" y2="{DAXY}" '
             f'stroke="{GRAY}" stroke-width="2"/>')
    for t in [-0.15, 0.0, 0.15]:
        xg = dx(t, i)
        b.append(f'<line x1="{xg:.1f}" y1="{DAXY}" x2="{xg:.1f}" y2="{DAXY+7}" '
                 f'stroke="{GRAY}" stroke-width="2"/>')
        lab = "0" if abs(t) < 1e-9 else num(t, 2)
        b.append(text(xg, DAXY + 28, lab, 18, GRAY, anchor="middle"))
    if i == 0:
        b.append(text(dx(0.0, i) + 10, DT + 44,
                      "the two channels are equal here", 18, GRAY))

for ry, lab in [(d1, "as measured"), (d2, "noise-corrected")]:
    b.append(text(GUT_R - 12, ry + 7, lab, 19, INK, "bold", "end"))
    b.append(f'<line x1="{GUT_R+8}" y1="{ry}" x2="{RIGHT}" y2="{ry}" '
             f'stroke="#eef0f2" stroke-width="1.2"/>')

for i, (key, name, gloss) in enumerate(AXES):
    a = P[key]
    rows = [
        (d1, a["gap_minus_supply"], a["gap_minus_supply_ci"],
         a["channels_differ_naive"], True),
        (d2, a["gap_minus_supply_corrected"], a["gap_minus_supply_corrected_ci"],
         a["channels_differ_corrected"], False),
    ]
    for ry, est, ci, clears, filled in rows:
        color = RED if clears else INK
        b.append(f'<line x1="{dx(ci[0], i):.1f}" y1="{ry}" '
                 f'x2="{dx(ci[1], i):.1f}" y2="{ry}" stroke="{color}" '
                 f'stroke-width="{7 if clears else 5}" stroke-linecap="round"/>')
        b.append(f'<line x1="{dx(ci[0], i):.1f}" y1="{ry-11}" '
                 f'x2="{dx(ci[0], i):.1f}" y2="{ry+11}" stroke="{color}" '
                 f'stroke-width="3"/>')
        b.append(f'<line x1="{dx(ci[1], i):.1f}" y1="{ry-11}" '
                 f'x2="{dx(ci[1], i):.1f}" y2="{ry+11}" stroke="{color}" '
                 f'stroke-width="3"/>')
        b.append(mark(dx(est, i), ry, color, filled))
        lab = num(est)
        b.append(plate(clamp_label(dx(est, i), lab, 19, i), ry - 20, lab, 19,
                       color, "bold"))
        it = interval_txt(ci[0], ci[1])
        b.append(plate(clamp_label(dx(est, i), it, 18, i, False), ry + 32, it,
                       18, GRAY))
        tag = "interval excludes zero" if clears else "interval covers zero"
        b.append(plate(clamp_label(dx(est, i), tag, 19, i), ry + 58, tag, 19,
                       RED if clears else GRAY, "bold"))

# ---------------- footer ---------------------------------------------------
q = D["by_organism"]["Qwen"]["ev_belief_bias"]
FY = DAXY + 76
notes = [
    ("Not causal.", "The selection differential was not randomised in these "
     "runs. The comparison contrasts two components of the same observational "
     "variation, which is stronger than a raw correlation, but a confounder "
     "correlated with the selection differential and not with the pool offset "
     "would break it."),
    ("Samples differ by axis", "because not every run recorded every probe: EV "
     f"belief bias {P['ev_belief_bias']['n']} rounds from "
     f"{P['ev_belief_bias']['n_runs']} runs, EV numeric estimate "
     f"{P['ev_numeric_est']['n']} from {P['ev_numeric_est']['n_runs']}, stated "
     f"risk tolerance {P['stated_tolerance']['n']} from "
     f"{P['stated_tolerance']['n_runs']} — the stated-tolerance readout "
     "exists only on the OLMo chassis."),
    ("The Qwen arm alone is underpowered", f"and is not broken out: "
     f"{q['n']} rounds, measurement noise "
     f"{q['noise_share_of_supply_variance']*100:.0f}% of its pool-offset "
     f"variance, and a corrected difference interval running from "
     f"{num(q['gap_minus_supply_corrected_ci'][0], 2)} to "
     f"{num(q['gap_minus_supply_corrected_ci'][1], 2)}. Everything above is "
     "the pooled fit."),
    ("None of these three axes was selected on.", "The judge scored only the "
     "risk-preference answers; all three off-target readouts were measured "
     "every round and never entered the selection. Bootstrap runs are "
     f"clustered on {D['settings']['clustering']}."),
]
yy = FY
for lead, rest in notes:
    s, yy = rich_para(M, yy, [("•", GRAY, False), (lead, INK, True),
                              (rest, GRAY, False)], 18, RIGHT - M)
    b.append(s)
    yy += 26

src = ("Source: experiments/offtarget_transmission_column.json, written by "
       "scripts/analysis_offtarget_transmission_column.py. Background: "
       "docs/reports/report_offtarget_transmission_column.md.")
s, yy = para(M, yy + 6, src, 18, RIGHT - M, GRAY)
b.append(s)

H = int(yy + 44)
svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
       f'width="{W}" height="{H}" font-family="{FONT}">\n'
       f'<rect width="{W}" height="{H}" fill="white"/>\n'
       + "\n".join(b) + "\n</svg>\n")
with open(OUT, "w") as f:
    f.write(svg)
print(f"wrote {OUT}  ({W}x{H})")
