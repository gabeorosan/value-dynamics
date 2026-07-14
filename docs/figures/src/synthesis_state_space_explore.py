#!/usr/bin/env python3
"""synthesis_state_space_explore — exploratory scatter-plot matrix.

No narrative, no chosen axes: plot EVERY pairwise combination of the per-round
variables across ALL single-generator (own-pool) risk-axis loops we have, so the
structure (or its absence) is visible rather than asserted. Points coloured by
judge, shaped by organism; each off-diagonal panel prints its Pearson r.

Data: experiments/state_space_explore.json (scripts/analysis_own_pool_records.py).
Regenerate:  python3 synthesis_state_space_explore.py   (stdlib only)
"""
import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
FIGDIR = os.path.dirname(HERE) if os.path.basename(HERE) == "src" else HERE
ROOT = os.path.dirname(os.path.dirname(FIGDIR))
DATA = os.path.join(ROOT, "experiments", "state_space_explore.json")

INK = "#1a1a1a"
GRAY = "#6b7684"
FONT = "Helvetica, Arial, sans-serif"

JUDGE_COLOR = {
    "self": "#2867b5", "risk copy": "#8a5a9e", "cautious copy": "#3a7d44",
    "base": "#6b7684", "random": "#c07d18", "score oracle": "#b5342c",
}
# organism -> marker drawer
def marker(x, y, organism, color, s=3.4):
    if organism == "OLMo-K2":   # square
        return (f'<rect x="{x-s:.1f}" y="{y-s:.1f}" width="{2*s:.1f}" height="{2*s:.1f}" '
                f'fill="{color}" fill-opacity="0.82"/>')
    return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{s:.1f}" fill="{color}" fill-opacity="0.82"/>'


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def ctext(x, y, t, size, color=INK, weight="normal"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="middle" font-family="{FONT}" '
            f'font-size="{size}" font-weight="{weight}" fill="{color}">{esc(t)}</text>')


def ltext(x, y, t, size, color=INK, weight="normal", anchor="start"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" font-family="{FONT}" '
            f'font-size="{size}" font-weight="{weight}" fill="{color}">{esc(t)}</text>')


def pearson(xs, ys):
    n = len(xs)
    if n < 3:
        return None
    mx, my = sum(xs) / n, sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    syy = sum((y - my) ** 2 for y in ys)
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    if sxx <= 0 or syy <= 0:
        return None
    return sxy / math.sqrt(sxx * syy)


d = json.load(open(DATA))
recs = d["records"]
VARS = ["value", "spread", "gap", "drift", "next_drift"]
LABEL = {"value": "value", "spread": "spread", "gap": "gap",
         "drift": "drift Δv", "next_drift": "next Δv"}

# per-variable range (pad 6%)
RNG = {}
for v in VARS:
    vals = [r[v] for r in recs if r[v] is not None]
    lo, hi = min(vals), max(vals)
    pad = (hi - lo) * 0.06 or 0.02
    RNG[v] = (lo - pad, hi + pad)

# ---------------- geometry
N = len(VARS)
P = 176            # panel size
G = 6
MX, MY = 92, 132
grid = N * P + (N - 1) * G
W = MX + grid + 336
H = MY + grid + 70

b = []
b.append(ctext(MX + grid / 2, 46, "Every pairwise view of the single-generator loop data", 30, INK, "bold"))
b.append(ctext(MX + grid / 2, 78,
               f"{d['n_records']} training-round records from {d['n_runs']} own-pool runs (no mixed-generator pools, no chosen axes).",
               17, GRAY))
b.append(ctext(MX + grid / 2, 100,
               "Each panel = column variable (x) vs row variable (y); r = Pearson correlation of the points shown.",
               15, GRAY))


def px_of(v, val, x0):
    lo, hi = RNG[v]
    return x0 + 12 + (val - lo) / (hi - lo) * (P - 24)


def py_of(v, val, y0):
    lo, hi = RNG[v]
    return y0 + P - 12 - (val - lo) / (hi - lo) * (P - 24)


for ri, vy in enumerate(VARS):
    for ci, vx in enumerate(VARS):
        x0 = MX + ci * (P + G)
        y0 = MY + ri * (P + G)
        if ri == ci:
            b.append(f'<rect x="{x0}" y="{y0}" width="{P}" height="{P}" rx="7" fill="#eef2f6" stroke="#c6ced6" stroke-width="1.3"/>')
            b.append(ctext(x0 + P / 2, y0 + P / 2 - 4, LABEL[vy], 22, INK, "bold"))
            lo, hi = RNG[vy]
            b.append(ctext(x0 + P / 2, y0 + P / 2 + 22, f"[{lo + (hi - lo) * 0.06:.2f}, {hi - (hi - lo) * 0.06:.2f}]", 14, GRAY))
            continue
        b.append(f'<rect x="{x0}" y="{y0}" width="{P}" height="{P}" rx="7" fill="white" stroke="#d7dde3" stroke-width="1.2"/>')
        # zero reference lines where a range crosses 0
        if RNG[vx][0] < 0 < RNG[vx][1]:
            zx = px_of(vx, 0, x0)
            b.append(f'<line x1="{zx:.1f}" y1="{y0+8}" x2="{zx:.1f}" y2="{y0+P-8}" stroke="#eceef1" stroke-width="1"/>')
        if RNG[vy][0] < 0 < RNG[vy][1]:
            zy = py_of(vy, 0, y0)
            b.append(f'<line x1="{x0+8}" y1="{zy:.1f}" x2="{x0+P-8}" y2="{zy:.1f}" stroke="#eceef1" stroke-width="1"/>')
        xs, ys = [], []
        for r in recs:
            if r[vx] is None or r[vy] is None:
                continue
            xs.append(r[vx])
            ys.append(r[vy])
            b.append(marker(px_of(vx, r[vx], x0), py_of(vy, r[vy], y0), r["organism"], JUDGE_COLOR[r["judge"]]))
        rr = pearson(xs, ys)
        if rr is not None:
            strong = abs(rr) >= 0.4
            b.append(ltext(x0 + 8, y0 + 18, f"r = {rr:+.2f}", 14,
                           "#1a1a1a" if strong else GRAY, "bold" if strong else "normal"))

# outer axis titles
for ci, vx in enumerate(VARS):
    b.append(ctext(MX + ci * (P + G) + P / 2, MY + grid + 34, LABEL[vx], 16, INK, "bold"))
for ri, vy in enumerate(VARS):
    cx, cy = MX - 30, MY + ri * (P + G) + P / 2
    b.append(f'<text x="{cx}" y="{cy:.1f}" text-anchor="middle" font-family="{FONT}" font-size="16" '
             f'font-weight="bold" fill="{INK}" transform="rotate(-90 {cx} {cy:.1f})">{esc(LABEL[vy])}</text>')

# ---------------- legend (right)
LXX = MX + grid + 34
ly = MY + 6
b.append(ltext(LXX, ly, "judge (colour)", 18, INK, "bold"))
ly += 30
for j in ["self", "risk copy", "cautious copy", "base", "random", "score oracle"]:
    if j not in d["judges"]:
        continue
    b.append(f'<circle cx="{LXX+8}" cy="{ly-5:.1f}" r="7" fill="{JUDGE_COLOR[j]}"/>')
    b.append(ltext(LXX + 24, ly, j, 16, INK))
    ly += 27
ly += 14
b.append(ltext(LXX, ly, "organism (shape)", 18, INK, "bold"))
ly += 30
b.append(f'<circle cx="{LXX+8}" cy="{ly-5:.1f}" r="6.5" fill="{GRAY}"/>')
b.append(ltext(LXX + 24, ly, "Qwen (K1)", 16, INK))
ly += 27
b.append(f'<rect x="{LXX+2}" y="{ly-11:.1f}" width="13" height="13" fill="{GRAY}"/>')
b.append(ltext(LXX + 24, ly, "OLMo (K2)", 16, INK))
ly += 40
b.append(ltext(LXX, ly, "variables (per training round)", 17, INK, "bold"))
ly += 26
for v in VARS:
    for i, ln in enumerate(_wrap := __import__("textwrap").wrap(f"{LABEL[v]} — {d['variables'][v]}", 34)):
        b.append(ltext(LXX, ly, ln, 13.5, GRAY))
        ly += 18
    ly += 3

svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" font-family="{FONT}">\n'
       f'<rect width="{W}" height="{H}" fill="white"/>\n' + "\n".join(b) + "\n</svg>")
with open(os.path.join(FIGDIR, "synthesis_state_space_explore.svg"), "w") as f:
    f.write(svg)
print(f"wrote synthesis_state_space_explore.svg ({W}x{H})")
