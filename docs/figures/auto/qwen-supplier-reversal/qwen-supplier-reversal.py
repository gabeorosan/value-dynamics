#!/usr/bin/env python3
"""Qwen insecure-code organism: forced-choice self-description under two pool
compositions. Single-panel line chart, orientation text only (interpretation
lives in caption.md).

Data source: experiments/qwen_selfonly_model_check.json
  forced_choice_p_insecure (baseline + per-seed trajectories) and
  round1_agreement (supplier_removed_mean, supplier_present_mean).

Self-contained (stdlib only). Run from this directory:  python3 qwen-supplier-reversal.py
Palette + esc()/wrap() copied verbatim from docs/figures/src/make_figures.py.
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "..", "..", "..",
                    "experiments", "qwen_selfonly_model_check.json")

# --- palette (copied from make_figures.py) ---
INK = "#1a1a1a"
BLUE = "#2867b5"       # self-judge series
GREEN = "#3a7d44"      # frozen-judge series
RED = "#b5342c"        # reversal / warning emphasis
GRAY = "#6b7684"       # recessive only
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


# --- load data (assert every plotted number) ---
with open(DATA) as f:
    D = json.load(f)

FC = D["forced_choice_p_insecure"]
BASE = FC["baseline"]
assert abs(BASE - 0.3405) < 1e-9, BASE

sr = FC["supplier_removed"]
sp = FC["supplier_present_twin"]
assert sr["em750:41"] == [0.5399, 0.719, 0.7484, 0.7934], sr["em750:41"]
assert sr["em750:42"] == [0.5736, 0.7803, 0.7256, 0.9128], sr["em750:42"]
assert sp["em750:41"] == [0.1038, 0.0091, 0.0079, 0.0061], sp["em750:41"]
assert sp["em750:42"] == [0.0638, 0.0191, 0.0127, 0.0071], sp["em750:42"]

RHO = D["round1_agreement"]
RHO_SR = RHO["supplier_removed_mean"]
RHO_SP = RHO["supplier_present_mean"]
assert abs(RHO_SR - 0.3971) < 1e-9, RHO_SR
assert abs(RHO_SP - (-0.2847)) < 1e-9, RHO_SP

# each trajectory = shared baseline (round 0) + 4 measured rounds
def traj(cell, block):
    return [BASE] + block[cell]

SERIES = [
    ("own candidates only", "seed 41", RED, "none",  traj("em750:41", sr)),
    ("own candidates only", "seed 42", RED, "7 5",   traj("em750:42", sr)),
    ("half from the base model", "seed 41", BLUE, "none", traj("em750:41", sp)),
    ("half from the base model", "seed 42", BLUE, "7 5",  traj("em750:42", sp)),
]

# ---------------- layout ----------------
W, H = 1040, 660
# plot area
PX0, PX1 = 118, 690          # x pixels for round 0..4
PY0, PY1 = 120, 548          # y pixels for p=1.0 (top) .. p=0.0 (bottom)
ROUNDS = [0, 1, 2, 3, 4]


def xpix(r):
    return PX0 + (PX1 - PX0) * r / 4.0


def ypix(p):
    return PY1 - (PY1 - PY0) * p


body = []

# ---- title / subtitle (orientation only) ----
body.append(f'<text x="60" y="52" font-family="{FONT}" font-size="27" '
            f'font-weight="bold" fill="{INK}">The organism&#8217;s forced-choice '
            f'self-description under two pool compositions</text>')
sub = ("Qwen em750 organism · candid-prompt self-judge · head-to-head "
       "duels · 2 seeds × 4 rounds; only the answer pool differs")
body.append(f'<text x="60" y="82" font-family="{FONT}" font-size="16.5" '
            f'fill="{GRAY}">{esc(sub)}</text>')

# ---- axes ----
# y gridlines
for p in [0.0, 0.25, 0.5, 0.75, 1.0]:
    y = ypix(p)
    body.append(f'<line x1="{PX0}" y1="{y:.1f}" x2="{PX1}" y2="{y:.1f}" '
                f'stroke="#e6e8eb" stroke-width="1.5"/>')
    body.append(f'<text x="{PX0-14}" y="{y+5:.1f}" font-family="{FONT}" '
                f'font-size="14" fill="{GRAY}" text-anchor="end">{p:.2f}</text>')
# y axis line
body.append(f'<line x1="{PX0}" y1="{PY0}" x2="{PX0}" y2="{PY1}" '
            f'stroke="{INK}" stroke-width="2"/>')
# x axis line
body.append(f'<line x1="{PX0}" y1="{PY1}" x2="{PX1}" y2="{PY1}" '
            f'stroke="{INK}" stroke-width="2"/>')
# x ticks
xlabels = {0: "0\n(baseline)", 1: "1", 2: "2", 3: "3", 4: "4"}
for r in ROUNDS:
    x = xpix(r)
    body.append(f'<line x1="{x:.1f}" y1="{PY1}" x2="{x:.1f}" y2="{PY1+6}" '
                f'stroke="{INK}" stroke-width="2"/>')
    lines = xlabels[r].split("\n")
    for i, ln in enumerate(lines):
        body.append(f'<text x="{x:.1f}" y="{PY1+26+i*17:.1f}" font-family="{FONT}" '
                    f'font-size="14" fill="{GRAY}" text-anchor="middle">{esc(ln)}</text>')
# axis titles
body.append(f'<text x="{(PX0+PX1)/2:.0f}" y="{PY1+68}" font-family="{FONT}" '
            f'font-size="15.5" fill="{INK}" text-anchor="middle">selection round</text>')
body.append(f'<text x="34" y="{(PY0+PY1)/2:.0f}" font-family="{FONT}" '
            f'font-size="15.5" fill="{INK}" text-anchor="middle" '
            f'transform="rotate(-90 34 {(PY0+PY1)/2:.0f})">'
            f'forced-choice p(insecure self-description)</text>')

# ---- baseline marker ----
by = ypix(BASE)
bx = xpix(0)
body.append(f'<circle cx="{bx:.1f}" cy="{by:.1f}" r="6" fill="{INK}"/>')

# ---- series lines ----
for cond, seed, color, dash, ys in SERIES:
    pts = " ".join(f"{xpix(r):.1f},{ypix(v):.1f}" for r, v in zip(ROUNDS, ys))
    dash_attr = "" if dash == "none" else f' stroke-dasharray="{dash}"'
    body.append(f'<polyline points="{pts}" fill="none" stroke="{color}" '
                f'stroke-width="3"{dash_attr} stroke-linejoin="round" '
                f'stroke-linecap="round"/>')
    # markers (2px white ring)
    for r, v in zip(ROUNDS, ys):
        body.append(f'<circle cx="{xpix(r):.1f}" cy="{ypix(v):.1f}" r="5" '
                    f'fill="{color}" stroke="white" stroke-width="2"/>')

# ---- direct end labels (group by condition color) ----
# own candidates only (RED) — ends high
end41 = SERIES[0][4][-1]
end42 = SERIES[1][4][-1]
lx = xpix(4) + 14
body.append(f'<text x="{lx:.1f}" y="{ypix(end42)-6:.1f}" font-family="{FONT}" '
            f'font-size="15" font-weight="bold" fill="{RED}">own candidates only</text>')
body.append(f'<text x="{lx:.1f}" y="{ypix(end42)+13:.1f}" font-family="{FONT}" '
            f'font-size="13.5" fill="{RED}">seed 41 (solid), seed 42 (dashed)</text>')

# half from base model (BLUE) — ends low
endsp41 = SERIES[2][4][-1]
body.append(f'<text x="{lx:.1f}" y="{ypix(endsp41)-4:.1f}" font-family="{FONT}" '
            f'font-size="15" font-weight="bold" fill="{BLUE}">half from the base model</text>')
body.append(f'<text x="{lx:.1f}" y="{ypix(endsp41)+15:.1f}" font-family="{FONT}" '
            f'font-size="13.5" fill="{BLUE}">seed 41 (solid), seed 42 (dashed)</text>')

# baseline label (right of the shared round-0 point, in the open wedge)
body.append(f'<text x="{bx+12:.1f}" y="{by-11:.1f}" font-family="{FONT}" '
            f'font-size="13.5" fill="{INK}" text-anchor="start">baseline {BASE:.3f}</text>')

# ---------------- side strip: round-1 agreement rho ----------------
SX0, SX1 = 810, 990          # -1 .. +1
SY = 250
SMID = (SX0 + SX1) / 2


def rhopix(r):
    return SMID + (SX1 - SMID) * r  # r in [-1,1]


body.append(f'<text x="{SMID:.0f}" y="{SY-64}" font-family="{FONT}" '
            f'font-size="15" font-weight="bold" fill="{INK}" '
            f'text-anchor="middle">round-1 agreement ρ</text>')
body.append(f'<text x="{SMID:.0f}" y="{SY-46}" font-family="{FONT}" '
            f'font-size="12.5" fill="{GRAY}" text-anchor="middle">'
            f'kept-vs-score correlation</text>')
# axis
body.append(f'<line x1="{SX0}" y1="{SY}" x2="{SX1}" y2="{SY}" '
            f'stroke="{INK}" stroke-width="2"/>')
for r in [-1, 0, 1]:
    x = rhopix(r)
    body.append(f'<line x1="{x:.1f}" y1="{SY-5}" x2="{x:.1f}" y2="{SY+5}" '
                f'stroke="{INK}" stroke-width="2"/>')
    body.append(f'<text x="{x:.1f}" y="{SY+22:.1f}" font-family="{FONT}" '
                f'font-size="12.5" fill="{GRAY}" text-anchor="middle">'
                f'{r:+d}'.replace("+0", "0") + '</text>')
# dots
body.append(f'<circle cx="{rhopix(RHO_SR):.1f}" cy="{SY:.1f}" r="8" fill="{RED}" '
            f'stroke="white" stroke-width="2"/>')
body.append(f'<text x="{rhopix(RHO_SR):.1f}" y="{SY-16:.1f}" font-family="{FONT}" '
            f'font-size="13.5" font-weight="bold" fill="{RED}" text-anchor="middle">'
            f'{RHO_SR:+.2f}</text>')
body.append(f'<circle cx="{rhopix(RHO_SP):.1f}" cy="{SY:.1f}" r="8" fill="{BLUE}" '
            f'stroke="white" stroke-width="2"/>')
body.append(f'<text x="{rhopix(RHO_SP):.1f}" y="{SY-16:.1f}" font-family="{FONT}" '
            f'font-size="13.5" font-weight="bold" fill="{BLUE}" text-anchor="middle">'
            f'{RHO_SP:+.2f}</text>')
# strip series keys
body.append(f'<text x="{SX0}" y="{SY+46}" font-family="{FONT}" font-size="12.5" '
            f'fill="{RED}">own candidates only</text>')
body.append(f'<text x="{SX0}" y="{SY+64}" font-family="{FONT}" font-size="12.5" '
            f'fill="{BLUE}">half from the base model</text>')

# ---- source line ----
body.append(f'<text x="60" y="{H-18}" font-family="{FONT}" font-size="12.5" '
            f'fill="{GRAY}">source: experiments/qwen_selfonly_model_check.json '
            f'(forced_choice_p_insecure, round1_agreement)</text>')

svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
       f'font-family="{FONT}">\n<rect width="{W}" height="{H}" fill="white"/>\n'
       + "\n".join(body) + "\n</svg>")

OUT = os.path.join(HERE, "qwen-supplier-reversal.svg")
with open(OUT, "w") as f:
    f.write(svg)
print("wrote", OUT)
