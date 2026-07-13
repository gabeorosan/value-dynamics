#!/usr/bin/env python3
"""dynamics_equation_of_motion — the value's per-round change follows the
selection gap, stated as a rule and then played forward.

Panel A: the closed loop written as a repeating rule (this round's value ->
the judge's selection gap -> the value changes by about 0.75 x the gap ->
next round's value -> back into the loop), with the fitted line and the
round-to-round data behind it as evidence.

Panel B: the same rule applied every round, starting from a value of 0.50,
at three constant gaps (steady negative, near zero, steady positive), so the
different resulting paths are visible over six rounds.

Data loading and the fit (SLOPE, R, N) are reused verbatim from
fig05_selection_gap_predicts_drift.py so the numbers match exactly.

Regenerate with:  python3 dynamics_equation_of_motion.py   (stdlib only)
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
GRAY = "#6b7684"
PURPLE = "#8a5a9e"
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
        svg.append(f'<text x="{x}" y="{y + i * size * lh:.1f}" font-family="{FONT}" '
                   f'font-size="{size}" font-weight="{weight}" fill="{color}">{esc(ln)}</text>')
    return "\n".join(svg), y + len(lines) * size * lh


def ctext(x, y, text, size, color=INK, weight="normal"):
    return (f'<text x="{x}" y="{y}" text-anchor="middle" font-family="{FONT}" '
            f'font-size="{size}" font-weight="{weight}" fill="{color}">{esc(text)}</text>')


def ltext(x, y, text, size, color=INK, weight="normal", anchor="start"):
    return (f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-family="{FONT}" '
            f'font-size="{size}" font-weight="{weight}" fill="{color}">{esc(text)}</text>')


def box(x, y, w, h, fill, stroke=INK, sw=2.5, rx=10):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')


def box_label(x, y, w, h, text, size=BODY, color=INK, weight="normal"):
    lines = wrap(text, max(6, int(w / 10.2)))
    ly = y + h / 2 - (len(lines) - 1) * size * 0.65 + size * 0.32
    return "\n".join(ctext(x + w / 2, ly + i * size * 1.3, ln, size, color, weight) for i, ln in enumerate(lines))


def marker(x, y, color, s=6.5):
    return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{s}" fill="{color}" stroke="white" stroke-width="1.2"/>'


def right_arrow(x0, x1, y, color=INK, sw=3):
    return (f'<line x1="{x0}" y1="{y}" x2="{x1-10}" y2="{y}" stroke="{color}" stroke-width="{sw}"/>'
            f'<path d="M {x1-11} {y-7} L {x1} {y} L {x1-11} {y+7} z" fill="{color}"/>')


def left_arrow(x0, x1, y, color=INK, sw=3):
    return (f'<line x1="{x0}" y1="{y}" x2="{x1+10}" y2="{y}" stroke="{color}" stroke-width="{sw}"/>'
            f'<path d="M {x1+11} {y-7} L {x1} {y} L {x1+11} {y+7} z" fill="{color}"/>')


def down_arrow(x, y0, y1, color=INK, sw=3):
    return (f'<line x1="{x}" y1="{y0}" x2="{x}" y2="{y1-10}" stroke="{color}" stroke-width="{sw}"/>'
            f'<path d="M {x-7} {y1-11} L {x} {y1} L {x+7} {y1-11} z" fill="{color}"/>')


def up_arrow(x, y0, y1, color=INK, sw=3):
    return (f'<line x1="{x}" y1="{y0}" x2="{x}" y2="{y1+10}" stroke="{color}" stroke-width="{sw}"/>'
            f'<path d="M {x-7} {y1+11} L {x} {y1} L {x+7} {y1+11} z" fill="{color}"/>')


def svg_doc(w, h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
            f'font-family="{FONT}">\n<rect width="{w}" height="{h}" fill="white"/>\n'
            f'{body}\n</svg>')


# ---------------------------------------------------------------- data
# (verbatim from fig05_selection_gap_predicts_drift.py, so the fit matches)
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
                ))
    return rollouts


ROLLOUTS = load_rollouts()
assert len(ROLLOUTS) == 17, f"expected 17 complete rollouts, got {len(ROLLOUTS)}"

TRANSITIONS = []
for r in ROLLOUTS:
    for t in range(3):
        TRANSITIONS.append((r["gap_arm"][t], r["pool"][t + 1] - r["pool"][t]))
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

# ---------------------------------------------------------------- panel B: rule played forward
START = 0.50
ROUNDS = 6
GAP_PATHS = [
    (-0.09, GREEN, "steady negative gap"),
    (0.00, GRAY, "near-zero gap"),
    (0.09, PURPLE, "steady positive gap"),
]


def play_forward(gap):
    v = START
    path = [v]
    for _ in range(ROUNDS):
        v = v + SLOPE * gap
        path.append(v)
    return path


# ---------------------------------------------------------------- figure
b = []
W = 1500

b.append(ctext(W // 2, 54, "The value's change each round follows the selection gap", 31, INK, "bold"))
b.append(ctext(W // 2, 89,
    "A model run for four rounds under four different judges. Each transition is one round's selection gap",
    BODY, GRAY))
b.append(ctext(W // 2, 114,
    "(risk of the kept answers minus the pool's average) and the move into the next round.",
    BODY, GRAY))

# ================= Panel A: the loop + the evidence =================
PAX, PAY = 100, 215
b.append(ltext(PAX, PAY - 24, "A.  The rule, stated as a loop, and the data behind it", 22, INK, "bold"))

bw, bh = 260, 84
cgap, rgap = 110, 108
x_l, x_r = PAX, PAX + bw + cgap
y_t, y_b = PAY, PAY + bh + rgap

# four boxes, clockwise: value -> gap -> change -> next value -> (back to value)
b.append(box(x_l, y_t, bw, bh, STRIP_FILL, GRAY, 1.5))
b.append(box_label(x_l, y_t, bw, bh, "this round's value", BODY, INK, "bold"))

b.append(box(x_r, y_t, bw, bh, STRIP_FILL, GRAY, 1.5))
b.append(box_label(x_r, y_t, bw, bh, "the judge's selection gap (the force)", BODY, INK, "bold"))

b.append(box(x_r, y_b, bw, bh, STRIP_FILL, GRAY, 1.5))
b.append(box_label(x_r, y_b, bw, bh, f"value changes by about {SLOPE:.2f} × the gap", BODY, INK, "bold"))

b.append(box(x_l, y_b, bw, bh, STRIP_FILL, GRAY, 1.5))
b.append(box_label(x_l, y_b, bw, bh, "next round's value", BODY, INK, "bold"))

top_y = y_t + bh / 2
bot_y = y_b + bh / 2
right_x = x_r + bw / 2
left_x = x_l + bw / 2

b.append(right_arrow(x_l + bw, x_r, top_y, INK))
b.append(down_arrow(right_x, y_t + bh, y_b, INK))
b.append(left_arrow(x_r, x_l + bw, bot_y, INK))
b.append(up_arrow(left_x, y_b, y_t + bh, INK))
b.append(ltext(left_x - 12, (y_t + bh + y_b) / 2 + 5, "becomes", BODY, GRAY, anchor="end"))

loop_bottom = y_b + bh

# --- compact scatter: the evidence behind the 0.75x rule ---
SAX, SAY = PAX, loop_bottom + 78
SAW, SAH = x_r + bw - PAX, 250
XMIN, XMAX = -0.16, 0.28
YMIN, YMAX = -0.19, 0.39


def sx_(v):
    return SAX + SAW * (v - XMIN) / (XMAX - XMIN)


def sy_(v):
    return SAY + SAH * (YMAX - v) / (YMAX - YMIN)


for v in (-0.1, 0.0, 0.1, 0.2, 0.3):
    yy = sy_(v)
    col, sw = (INK, 1.6) if v == 0 else ("#e4e4e0", 1)
    b.append(f'<line x1="{SAX}" y1="{yy:.1f}" x2="{SAX + SAW}" y2="{yy:.1f}" stroke="{col}" stroke-width="{sw}"/>')
    b.append(ltext(SAX - 14, yy + 5, f"{v:+.1f}", 17, GRAY, anchor="end"))
for v in (-0.1, 0.0, 0.1, 0.2):
    xx = sx_(v)
    col, sw = (INK, 1.6) if v == 0 else ("#e4e4e0", 1)
    b.append(f'<line x1="{xx:.1f}" y1="{SAY}" x2="{xx:.1f}" y2="{SAY + SAH}" stroke="{col}" stroke-width="{sw}"/>')
    b.append(ltext(xx, SAY + SAH + 22, f"{v:+.1f}", 17, GRAY, anchor="middle"))
b.append(ltext(SAX + SAW / 2, SAY + SAH + 46, "this round's selection gap", BODY, INK, anchor="middle"))
b.append(f'<text x="{SAX - 68}" y="{SAY + SAH / 2}" font-size="{BODY}" fill="{INK}" font-family="{FONT}" '
         f'transform="rotate(-90 {SAX - 68} {SAY + SAH / 2})" text-anchor="middle">next round’s drift</text>')

lx0, lx1 = -0.15, 0.27
b.append(f'<line x1="{sx_(lx0):.1f}" y1="{sy_(SLOPE * lx0 + ICPT):.1f}" '
         f'x2="{sx_(lx1):.1f}" y2="{sy_(SLOPE * lx1 + ICPT):.1f}" stroke="{INK}" stroke-width="3"/>')
for x, y in TRANSITIONS:
    b.append(marker(sx_(x), sy_(y), GRAY, s=6))

flx, fly = sx_(0.09), sy_(-0.105)
b.append(f'<rect x="{flx - 10:.1f}" y="{fly - 26:.1f}" width="248" height="62" rx="8" fill="white" fill-opacity="0.92"/>')
b.append(f'<text x="{flx:.1f}" y="{fly:.1f}" font-size="20" font-weight="bold" fill="{INK}" font-family="{FONT}">drift ≈ {SLOPE:.2f} × gap</text>')
b.append(f'<text x="{flx:.1f}" y="{fly + 26:.1f}" font-size="{BODY}" fill="{GRAY}" font-family="{FONT}">r = {R:.2f}, n = {N} round transitions</text>')

panelA_bottom = SAY + SAH + 46

# ================= Panel B: the rule played forward =================
BX, BY = 880, 215
b.append(ltext(BX, BY - 24, "B.  The rule played forward, at three constant gaps", 22, INK, "bold"))

BY0 = BY
BW, BH = 430, loop_bottom + 250 - BY0
YMIN_B, YMAX_B = 0.0, 1.0


def bx_(rnd):
    return BX + BW * rnd / ROUNDS


def by_(v):
    return BY0 + BH * (YMAX_B - v) / (YMAX_B - YMIN_B)


for v in (0.0, 0.25, 0.5, 0.75, 1.0):
    yy = by_(v)
    b.append(f'<line x1="{BX}" y1="{yy:.1f}" x2="{BX + BW}" y2="{yy:.1f}" stroke="#e4e4e0" stroke-width="1"/>')
    b.append(ltext(BX - 14, yy + 5, f"{v:g}", 17, GRAY, anchor="end"))
for rnd in range(ROUNDS + 1):
    b.append(ltext(bx_(rnd), BY0 + BH + 26, str(rnd), 17, GRAY, anchor="middle"))
b.append(ltext(BX + BW / 2, BY0 + BH + 52, "round", BODY, INK, anchor="middle"))
b.append(f'<text x="{BX - 70}" y="{BY0 + BH / 2}" font-size="{BODY}" fill="{INK}" font-family="{FONT}" '
         f'transform="rotate(-90 {BX - 70} {BY0 + BH / 2})" text-anchor="middle">value</text>')


label_dy = {-0.09: 30, 0.00: 6, 0.09: -14}
for gap, color, desc in GAP_PATHS:
    path = play_forward(gap)
    pts = " ".join(f"{bx_(i):.1f},{by_(v):.1f}" for i, v in enumerate(path))
    b.append(f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="3"/>')
    for i, v in enumerate(path):
        b.append(marker(bx_(i), by_(v), color, s=5.5))
    end_x, end_y = bx_(ROUNDS), by_(path[-1])
    dy = label_dy[gap]
    b.append(f'<text x="{end_x + 12:.1f}" y="{end_y + dy:.1f}" font-size="{BODY}" font-weight="bold" '
             f'fill="{color}" font-family="{FONT}">gap ≈ {gap:+.2f}</text>')
    b.append(f'<text x="{end_x + 12:.1f}" y="{end_y + dy + 23:.1f}" font-size="{BODY}" '
             f'fill="{color}" font-family="{FONT}">{desc}</text>')

panelB_bottom = BY0 + BH + 52

# ================= caption =================
cap_y = max(panelA_bottom, panelB_bottom) + 56
t, cap_end = text_block(PAX, cap_y,
    "Left: the loop states the fitted rule; dots are 51 round-to-round transitions from 17 four-round runs across "
    "four judges, line is the least-squares fit. Right: the same rule integrated forward from a value of 0.50, one "
    "point per round, at three constant gaps. Data: the same round-to-round transitions as the selection-gap-and-"
    "drift figure.",
    BODY, 148, GRAY)
b.append(t)

svg = svg_doc(W, cap_end + 34, "\n".join(b))
out = os.path.join(FIGDIR, "dynamics_equation_of_motion.svg")
with open(out, "w") as f:
    f.write(svg)
print(f"wrote dynamics_equation_of_motion.svg  (slope={SLOPE:.3f}, r={R:.3f}, n={N})")
