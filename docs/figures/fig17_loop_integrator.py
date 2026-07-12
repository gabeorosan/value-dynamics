#!/usr/bin/env python3
"""Draft figure: the K2 self-training loop decomposed as an integrator.

Panel A pools all 17 complete K2 rollouts (OLMo organism, 4 rounds each,
51 round-to-round transitions) and regresses next-round pool-risk drift on
this round's kept-gap. Panel B shows the six frozen-base-judge pool-risk
trajectories, with the two escaping seeds emphasized and their per-round
base-judge kept-gaps annotated, plus the counterfactual conservative-judge
kept-gaps recorded on the identical candidate pools.

Regenerate with:  python3 figure.py   (from this directory; stdlib only)
"""
import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..", "..")

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
BLUE = "#2867b5"       # accent / self-judge series (validated)
GREEN = "#3a7d44"      # accent / frozen-judge series (validated)
RED = "#b5342c"        # emphasis for reversal / warning text
GRAY = "#6b7684"       # recessive only (axes, muted captions)
PURPLE = "#8a5a9e"     # second frozen-judge series (as in Figures 4 and 7)
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
                    continue  # conf v1 seed 3 was killed after round 1
                rollouts.append(dict(
                    src=os.path.basename(f), seed=seed, cond=cond,
                    pool=[mean([it["pool_risk"] for it in rnd]) for rnd in rr],
                    gap_arm=[mean([it["gap_arm"] for it in rnd]) for rnd in rr],
                    gap_base=[mean([it["gap_base_judge"] for it in rnd]) for rnd in rr],
                    gap_cons=[mean([it["gap_cons_judge"] for it in rnd]) for rnd in rr],
                ))
    return rollouts


ROLLOUTS = load_rollouts()
assert len(ROLLOUTS) == 17, f"expected 17 complete rollouts, got {len(ROLLOUTS)}"

TRANSITIONS = []  # (kept-gap at round t, pool drift t -> t+1, condition)
for r in ROLLOUTS:
    for t in range(3):
        TRANSITIONS.append((r["gap_arm"][t], r["pool"][t + 1] - r["pool"][t], r["cond"]))
N = len(TRANSITIONS)
assert N == 51, f"expected 51 transitions, got {N}"

xs = [p[0] for p in TRANSITIONS]
ys = [p[1] for p in TRANSITIONS]
mx, my = mean(xs), mean(ys)
sxx = sum((x - mx) ** 2 for x in xs)
sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
syy = sum((y - my) ** 2 for y in ys)
SLOPE = sxy / sxx
ICPT = my - SLOPE * mx
R = sxy / math.sqrt(sxx * syy)

COND_STYLE = {  # condition -> (color, legend words)
    "frozen_cons_r0": (GREEN, "frozen conservative judge"),
    "frozen_base": (PURPLE, "frozen base judge"),
    "evolving_self": (BLUE, "evolving self-judge"),
    "random_select": (GRAY, "random keep (no judge)"),
}

FB = [r for r in ROLLOUTS if r["cond"] == "frozen_base"]
RAILS = [r for r in FB if r["pool"][3] > 0.4]      # the two escaping seeds
OTHERS = [r for r in FB if r["pool"][3] <= 0.4]
assert len(RAILS) == 2 and len(OTHERS) == 4
rail_cons = [g for r in RAILS for g in r["gap_cons"][:3]]
CONS_LO, CONS_HI = min(rail_cons), max(rail_cons)


# ---------------------------------------------------------------- figure
b = []
W = 1400

t, _ = text_block(W // 2, 52, "The judge's kept-gap predicts next round's pool drift —", 33, 82, weight="bold")
b.append(t.replace('<text ', '<text text-anchor="middle" ', 1))
t, _ = text_block(W // 2, 94, "an out-of-sample-validated coupling, at a descriptive ≈ 0.75 pooled slope", 30, 92, weight="bold")
b.append(t.replace('<text ', '<text text-anchor="middle" ', 1))
t, _ = text_block(W // 2, 130, "17 four-round K2 rollouts of the OLMo organism across four judge conditions; "
                  "12 gamble items × 6 candidates per round. The slope is descriptive, not a stability law.", 19, 220, GRAY)
b.append(t.replace('<text ', '<text text-anchor="middle" ', 1))

# ================= Panel A: descriptive kept-gap -> pool-drift slope =================
AX, AY, AW, AH = 130, 236, 470, 400
XMIN, XMAX = -0.16, 0.28
YMIN, YMAX = -0.19, 0.39


def ax_(v):
    return AX + AW * (v - XMIN) / (XMAX - XMIN)


def ay_(v):
    return AY + AH * (YMAX - v) / (YMAX - YMIN)


t, _ = text_block(AX - 40, 186, "A. Kept-gap → next-round pool drift, all judge conditions "
                  "pooled — a descriptive slope", 21, 52, weight="bold")
b.append(t)

for v in (-0.1, 0.0, 0.1, 0.2, 0.3):
    yy = ay_(v)
    col, sw = (INK, 2) if v == 0 else ("#e4e4e0", 1)
    b.append(f'<line x1="{AX}" y1="{yy:.1f}" x2="{AX + AW}" y2="{yy:.1f}" stroke="{col}" stroke-width="{sw}"/>')
    b.append(f'<text x="{AX - 10}" y="{yy + 6:.1f}" text-anchor="end" font-size="15" fill="{GRAY}" font-family="{FONT}">{v:+.1f}</text>')
for v in (-0.1, 0.0, 0.1, 0.2):
    xx = ax_(v)
    col, sw = (INK, 2) if v == 0 else ("#e4e4e0", 1)
    b.append(f'<line x1="{xx:.1f}" y1="{AY}" x2="{xx:.1f}" y2="{AY + AH}" stroke="{col}" stroke-width="{sw}"/>')
    b.append(f'<text x="{xx:.1f}" y="{AY + AH + 24}" text-anchor="middle" font-size="15" fill="{GRAY}" font-family="{FONT}">{v:+.1f}</text>')
b.append(f'<text x="{AX + AW / 2}" y="{AY + AH + 52}" text-anchor="middle" font-size="17" fill="{INK}" font-family="{FONT}">kept-gap this round (mean risk of the judge’s kept top 2 minus pool mean)</text>')
b.append(f'<text x="{AX - 62}" y="{AY + AH / 2}" font-size="17" fill="{INK}" font-family="{FONT}" '
         f'transform="rotate(-90 {AX - 62} {AY + AH / 2})" text-anchor="middle">pool-risk change into the next round</text>')

# fitted line (ordinary least squares, computed above from the 51 transitions)
x1, x2 = -0.15, 0.27
b.append(f'<line x1="{ax_(x1):.1f}" y1="{ay_(SLOPE * x1 + ICPT):.1f}" '
         f'x2="{ax_(x2):.1f}" y2="{ay_(SLOPE * x2 + ICPT):.1f}" stroke="{INK}" stroke-width="3.5"/>')

for x, y, cond in TRANSITIONS:
    color = COND_STYLE[cond][0]
    b.append(f'<circle cx="{ax_(x):.1f}" cy="{ay_(y):.1f}" r="5.5" fill="{color}" '
             f'fill-opacity="0.8" stroke="white" stroke-width="1.5"/>')

# fit label, placed in the empty bottom-right corner (clear of the rising fit line)
b.append(f'<text x="{ax_(0.055):.1f}" y="{ay_(-0.095):.1f}" font-size="19" font-weight="bold" fill="{INK}" font-family="{FONT}">pool drift ≈ {SLOPE:.2f} × kept-gap</text>')
b.append(f'<text x="{ax_(0.055):.1f}" y="{ay_(-0.095) + 22:.1f}" font-size="15" fill="{GRAY}" font-family="{FONT}">descriptive pooled fit · r = {R:.2f}, n = {N} transitions</text>')
b.append(f'<text x="{ax_(0.055):.1f}" y="{ay_(-0.095) + 42:.1f}" font-size="15" fill="{GRAY}" font-family="{FONT}">slope identified only on the K2 base arm: +1.05 [0.85, 1.29]</text>')

# legend (top-left of panel, above the cloud)
ly = AY + 14
counts = {}
for _, _, cond in TRANSITIONS:
    counts[cond] = counts.get(cond, 0) + 1
for cond in ("frozen_cons_r0", "frozen_base", "evolving_self", "random_select"):
    color, label = COND_STYLE[cond]
    b.append(f'<circle cx="{AX + 16}" cy="{ly}" r="6" fill="{color}"/>')
    b.append(f'<text x="{AX + 30}" y="{ly + 5}" font-size="15" fill="{INK}" font-family="{FONT}">{esc(label)} — {counts[cond]} transitions</text>')
    ly += 26

t, _ = text_block(AX - 40, AY + AH + 88,
                  "The kept-gap in round t predicts the pool’s move in round t+1, validated "
                  "out-of-sample (leave-one-rollout-out AND leave-one-seed-out; RMSE 12–31% below a "
                  "zero-drift baseline). The pooled slope mixes judge regimes with and without gap variance.", 15.5, 62, GRAY)
b.append(t)

# ================= Panel B: integration in action =================
BX, BY, BW, BH = 810, 236, 470, 400
BYMIN, BYMAX = 0.0, 0.72


def bx_(rnd):  # rnd in 1..4
    return BX + BW * (rnd - 1) / 3


def by_(v):
    return BY + BH * (BYMAX - v) / (BYMAX - BYMIN)


t, _ = text_block(BX - 40, 186, "B. Integration in action: 2 of 6 frozen-base-judge "
                  "seeds ride persistent positive kept-gaps up and out", 21, 50, weight="bold")
b.append(t)

for v in (0.0, 0.2, 0.4, 0.6):
    yy = by_(v)
    b.append(f'<line x1="{BX}" y1="{yy:.1f}" x2="{BX + BW}" y2="{yy:.1f}" stroke="#e4e4e0" stroke-width="1"/>')
    b.append(f'<text x="{BX - 10}" y="{yy + 6:.1f}" text-anchor="end" font-size="15" fill="{GRAY}" font-family="{FONT}">{v:g}</text>')
for rnd in (1, 2, 3, 4):
    b.append(f'<text x="{bx_(rnd):.1f}" y="{BY + BH + 24}" text-anchor="middle" font-size="15" fill="{GRAY}" font-family="{FONT}">{rnd}</text>')
b.append(f'<text x="{BX + BW / 2}" y="{BY + BH + 52}" text-anchor="middle" font-size="17" fill="{INK}" font-family="{FONT}">round</text>')
b.append(f'<text x="{BX - 52}" y="{BY + BH / 2}" font-size="17" fill="{INK}" font-family="{FONT}" '
         f'transform="rotate(-90 {BX - 52} {BY + BH / 2})" text-anchor="middle">pool risk (mean risk of the 6 candidates, over 12 items)</text>')

for r in OTHERS:
    pts = " ".join(f"{bx_(i + 1):.1f},{by_(v):.1f}" for i, v in enumerate(r["pool"]))
    b.append(f'<polyline points="{pts}" fill="none" stroke="{PURPLE}" stroke-width="2.5" stroke-opacity="0.35"/>')
    b.append(f'<circle cx="{bx_(4):.1f}" cy="{by_(r["pool"][3]):.1f}" r="4" fill="{PURPLE}" fill-opacity="0.5"/>')
lo = min(r["pool"][3] for r in OTHERS)
hi = max(r["pool"][3] for r in OTHERS)
b.append(f'<text x="{bx_(4) + 10:.1f}" y="{by_((lo + hi) / 2) + 5:.1f}" font-size="14.5" fill="{PURPLE}" fill-opacity="0.85" font-family="{FONT}">4 seeds decay</text>')
b.append(f'<text x="{bx_(4) + 10:.1f}" y="{by_((lo + hi) / 2) + 23:.1f}" font-size="14.5" fill="{PURPLE}" fill-opacity="0.85" font-family="{FONT}">to {lo:.2f}–{hi:.2f}</text>')

# label the higher-ending rail above its endpoint, the lower-ending rail below —
# their finals (~0.61 / 0.65) are too close to label at their own points
RAILS_SORTED = sorted(RAILS, key=lambda r: -r["pool"][0])  # seed 2 (starts high) first
_end_rank = sorted(range(len(RAILS_SORTED)), key=lambda i: -RAILS_SORTED[i]["pool"][3])
_label_dy = {_end_rank[0]: -10, _end_rank[-1]: 20}
for k, r in enumerate(RAILS_SORTED):
    pts = " ".join(f"{bx_(i + 1):.1f},{by_(v):.1f}" for i, v in enumerate(r["pool"]))
    b.append(f'<polyline points="{pts}" fill="none" stroke="{RED}" stroke-width="4.5"/>')
    for i, v in enumerate(r["pool"]):
        b.append(f'<circle cx="{bx_(i + 1):.1f}" cy="{by_(v):.1f}" r="5.5" fill="{RED}" stroke="white" stroke-width="1.5"/>')
    b.append(f'<text x="{bx_(4) + 10:.1f}" y="{by_(r["pool"][3]) + _label_dy[k]:.1f}" font-size="15" '
             f'font-weight="bold" fill="{RED}" font-family="{FONT}">seed {r["seed"]}: {r["pool"][3]:.2f}</text>')
    # per-segment base-judge kept-gap labels (the signal being integrated)
    for i in range(3):
        gx = (bx_(i + 1) + bx_(i + 2)) / 2
        gy = (by_(r["pool"][i]) + by_(r["pool"][i + 1])) / 2
        off = -12 if k == 0 else 18
        b.append(f'<text x="{gx:.1f}" y="{gy + off:.1f}" text-anchor="middle" font-size="13.5" '
                 f'font-weight="bold" fill="{RED}" font-family="{FONT}">{r["gap_base"][i]:+.2f}</text>')

seed_names = " and ".join(f"seed {r['seed']}" for r in RAILS_SORTED)
t, _ = rich_text(BX - 40, BY + BH + 88, [
    ("Red labels: ", RED, True),
    ("the frozen base judge’s kept-gap each round on the escaping seeds "
     f"({seed_names}) — repeatedly positive, up to +0.25. ", INK, False),
    ("Rescoring the identical candidate pools with the conservative judge gives kept-gaps of "
     f"{CONS_LO:+.2f} to {CONS_HI:+.2f}", GREEN, True),
    (" — selection that would have pushed both seeds back down.", INK, False),
], 15.5, 62)
b.append(t)

# ================= takeaway =================
ty = 812
b.append(box(70, ty, W - 140, 108, KEY_FILL, INK, 2.5))
t, _ = rich_text(90, ty + 32, [
    ("Read descriptively, not as a stability law: ", INK, True),
    ("the judge's kept-gap is a per-round signal the generator partly writes into the next pool. The ≈ 0.75 "
     "pooled slope is a DESCRIPTIVE summary, not a stability boundary — no experiment perturbed a gap and measured "
     "the closed-loop response, so no k-below-1 / k-above-1 regime is claimed. A frozen-base seed rails up when "
     "its early pools happen to contain gambles that judge keeps (Panel B), and decays when they don’t.", INK, False),
], 18, 128)
b.append(t)

svg = svg_doc(W, ty + 140, "\n".join(b))
with open(os.path.join(HERE, "fig17_loop_integrator.svg"), "w") as f:
    f.write(svg)
print(f"wrote fig17_loop_integrator.svg  (slope={SLOPE:.3f}, intercept={ICPT:.4f}, r={R:.3f}, n={N})")
