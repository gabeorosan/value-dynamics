#!/usr/bin/env python3
"""synthesis_state_space_explore — a matrix of phase-plane TRAJECTORIES.

For every pair of per-round variables, plot each single-generator (own-pool) run
as a path: one dot per round, consecutive rounds joined by an arrow (so you see
how the run MOVES through that plane over training rounds). Lines and dots are
coloured by judge condition; organism is the dot shape. No mixed-generator pools.

This is the exploratory, no-narrative version: the same trajectory idea as the
state-space figure, drawn in every axis combination at once so the right axes are
chosen from the data, not assumed.

Data: experiments/state_space_explore.json (scripts/analysis_own_pool_records.py).
Regenerate:  python3 synthesis_state_space_explore.py   (stdlib only)
"""
import collections
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


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def ctext(x, y, t, size, color=INK, weight="normal"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="middle" font-family="{FONT}" '
            f'font-size="{size}" font-weight="{weight}" fill="{color}">{esc(t)}</text>')


def ltext(x, y, t, size, color=INK, weight="normal", anchor="start"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" font-family="{FONT}" '
            f'font-size="{size}" font-weight="{weight}" fill="{color}">{esc(t)}</text>')


def dot(x, y, organism, color, s=3.0):
    if organism == "OLMo-K2":
        return (f'<rect x="{x-s:.1f}" y="{y-s:.1f}" width="{2*s:.1f}" height="{2*s:.1f}" '
                f'fill="{color}"/>')
    return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{s:.1f}" fill="{color}"/>'


def arrow(x1, y1, x2, y2, color, w=1.4, op=0.62):
    dx, dy = x2 - x1, y2 - y1
    L = math.hypot(dx, dy)
    if L < 1e-6:
        return ""
    ux, uy = dx / L, dy / L
    head = min(7.0, max(4.0, L * 0.4))
    bx, by = x2 - ux * head, y2 - uy * head
    px, py = -uy, ux
    h = head * 0.5
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{bx:.1f}" y2="{by:.1f}" stroke="{color}" '
            f'stroke-width="{w}" stroke-opacity="{op}" stroke-linecap="round"/>'
            f'<polygon points="{x2:.1f},{y2:.1f} {bx+px*h:.1f},{by+py*h:.1f} {bx-px*h:.1f},{by-py*h:.1f}" '
            f'fill="{color}" fill-opacity="{op}"/>')


d = json.load(open(DATA))
recs = d["records"]

# group records into runs, ordered by round
runs = collections.defaultdict(list)
for r in recs:
    runs[(r["organism"], r["judge"], r["seed"])].append(r)
for k in runs:
    runs[k].sort(key=lambda r: r["round"])

VARS = ["value", "spread", "gap", "drift"]
LABEL = {"value": "value", "spread": "spread", "gap": "gap", "drift": "drift Δv"}
RNG = {}
for v in VARS:
    vals = [r[v] for r in recs if r[v] is not None]
    lo, hi = min(vals), max(vals)
    pad = (hi - lo) * 0.08 or 0.02
    RNG[v] = (lo - pad, hi + pad)

# ---------------- geometry
N = len(VARS)
P = 246
G = 8
MX, MY = 96, 140
grid = N * P + (N - 1) * G
W = MX + grid + 330
H = MY + grid + 66

b = []
b.append(ctext(MX + grid / 2, 48, "Single-generator loops as trajectories, in every axis pair", 30, INK, "bold"))
b.append(ctext(MX + grid / 2, 80,
               f"{d['n_runs']} own-pool runs; each is a path — one dot per training round, arrow to the next round. Coloured by judge.",
               17, GRAY))
b.append(ctext(MX + grid / 2, 102,
               "Panel = column variable (x) vs row variable (y). No mixed-generator pools; no chosen axes.",
               15, GRAY))


def sx(v, val, x0):
    lo, hi = RNG[v]
    return x0 + 12 + (val - lo) / (hi - lo) * (P - 24)


def sy(v, val, y0):
    lo, hi = RNG[v]
    return y0 + P - 12 - (val - lo) / (hi - lo) * (P - 24)


for ri, vy in enumerate(VARS):
    for ci, vx in enumerate(VARS):
        x0 = MX + ci * (P + G)
        y0 = MY + ri * (P + G)
        if ri == ci:
            b.append(f'<rect x="{x0}" y="{y0}" width="{P}" height="{P}" rx="8" fill="#eef2f6" stroke="#c6ced6" stroke-width="1.4"/>')
            b.append(ctext(x0 + P / 2, y0 + P / 2 - 2, LABEL[vy], 26, INK, "bold"))
            lo, hi = RNG[vy]
            b.append(ctext(x0 + P / 2, y0 + P / 2 + 26, f"[{lo + (hi-lo)*0.08:.2f}, {hi - (hi-lo)*0.08:.2f}]", 15, GRAY))
            continue
        b.append(f'<rect x="{x0}" y="{y0}" width="{P}" height="{P}" rx="8" fill="white" stroke="#d7dde3" stroke-width="1.2"/>')
        for v, axis in ((vx, "x"), (vy, "y")):
            if RNG[v][0] < 0 < RNG[v][1]:
                if axis == "x":
                    zx = sx(vx, 0, x0)
                    b.append(f'<line x1="{zx:.1f}" y1="{y0+8}" x2="{zx:.1f}" y2="{y0+P-8}" stroke="#eceef1" stroke-width="1"/>')
                else:
                    zy = sy(vy, 0, y0)
                    b.append(f'<line x1="{x0+8}" y1="{zy:.1f}" x2="{x0+P-8}" y2="{zy:.1f}" stroke="#eceef1" stroke-width="1"/>')
        # trajectories
        for (org, judge, seed), pts in runs.items():
            col = JUDGE_COLOR[judge]
            xy = [(sx(vx, p[vx], x0), sy(vy, p[vy], y0)) for p in pts
                  if p[vx] is not None and p[vy] is not None]
            for i in range(len(xy) - 1):
                b.append(arrow(xy[i][0], xy[i][1], xy[i + 1][0], xy[i + 1][1], col))
            for (px, py) in xy:
                b.append(dot(px, py, org, col))

# outer axis titles
for ci, vx in enumerate(VARS):
    b.append(ctext(MX + ci * (P + G) + P / 2, MY + grid + 34, LABEL[vx], 17, INK, "bold"))
for ri, vy in enumerate(VARS):
    cx, cy = MX - 34, MY + ri * (P + G) + P / 2
    b.append(f'<text x="{cx}" y="{cy:.1f}" text-anchor="middle" font-family="{FONT}" font-size="17" '
             f'font-weight="bold" fill="{INK}" transform="rotate(-90 {cx} {cy:.1f})">{esc(LABEL[vy])}</text>')

# ---------------- legend
LXX = MX + grid + 30
ly = MY + 8
b.append(ltext(LXX, ly, "judge (line + dot colour)", 18, INK, "bold"))
ly += 30
for j in ["self", "risk copy", "cautious copy", "base", "random", "score oracle"]:
    if j not in d["judges"]:
        continue
    b.append(arrow(LXX, ly - 5, LXX + 30, ly - 5, JUDGE_COLOR[j], w=2.4, op=1))
    b.append(f'<circle cx="{LXX+15}" cy="{ly-5:.1f}" r="3.4" fill="{JUDGE_COLOR[j]}"/>')
    b.append(ltext(LXX + 42, ly, j, 16, INK))
    ly += 28
ly += 14
b.append(ltext(LXX, ly, "organism (dot shape)", 18, INK, "bold"))
ly += 30
b.append(f'<circle cx="{LXX+8}" cy="{ly-5:.1f}" r="4.2" fill="{GRAY}"/>')
b.append(ltext(LXX + 24, ly, "Qwen (K1)", 16, INK))
ly += 27
b.append(f'<rect x="{LXX+4}" y="{ly-9:.1f}" width="9" height="9" fill="{GRAY}"/>')
b.append(ltext(LXX + 24, ly, "OLMo (K2)", 16, INK))
ly += 42
b.append(ltext(LXX, ly, "reading a path", 18, INK, "bold"))
ly += 26
for ln in ["each path is one run; a dot is a", "training round, the arrow points to",
           "the next round. value = free-gen", "risk; spread = candidate SD; gap =",
           "kept − pool; drift Δv = value change."]:
    b.append(ltext(LXX, ly, ln, 14, GRAY))
    ly += 19

svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" font-family="{FONT}">\n'
       f'<rect width="{W}" height="{H}" fill="white"/>\n' + "\n".join(b) + "\n</svg>")
with open(os.path.join(FIGDIR, "synthesis_state_space_explore.svg"), "w") as f:
    f.write(svg)
print(f"wrote synthesis_state_space_explore.svg ({W}x{H})")
