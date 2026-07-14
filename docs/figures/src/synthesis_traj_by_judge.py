#!/usr/bin/env python3
"""synthesis_traj_by_judge — faceted trajectory figures, one panel per judge.

For each of the most-structured variable pairs (chosen from the exploratory
matrix synthesis_state_space_explore), draw a small phase-plane per JUDGE
condition, each showing that judge's single-generator runs as trajectories:
one dot per training round, arrow to the next round. Axes are shared across the
judge panels of a figure so the judges are directly comparable. Organism = dot
shape. Own-pool (single-generator) data only.

Emits three SVGs:
  synthesis_traj_value_spread.svg   value (x) vs spread (y)   — where variation lives
  synthesis_traj_gap_drift.svg      gap (x) vs drift (y)      — pressure vs movement
  synthesis_traj_value_gap.svg      value (x) vs gap (y)      — which way each judge pulls

Data: experiments/state_space_explore.json (scripts/analysis_own_pool_records.py).
Regenerate:  python3 synthesis_traj_by_judge.py   (stdlib only)
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
JUDGE_ORDER = ["self", "risk copy", "cautious copy", "base", "random", "score oracle"]
LABEL = {"value": "value  (free-gen risk)", "spread": "candidate spread",
         "gap": "selection gap  (kept − pool)", "drift": "value move Δv this round"}


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def ctext(x, y, t, size, color=INK, weight="normal"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="middle" font-family="{FONT}" '
            f'font-size="{size}" font-weight="{weight}" fill="{color}">{esc(t)}</text>')


def ltext(x, y, t, size, color=INK, weight="normal", anchor="start"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" font-family="{FONT}" '
            f'font-size="{size}" font-weight="{weight}" fill="{color}">{esc(t)}</text>')


def dot(x, y, organism, color, s=3.6):
    if organism == "OLMo-K2":
        return f'<rect x="{x-s:.1f}" y="{y-s:.1f}" width="{2*s:.1f}" height="{2*s:.1f}" fill="{color}"/>'
    return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{s:.1f}" fill="{color}"/>'


def arrow(x1, y1, x2, y2, color, w=1.9, op=0.72):
    dx, dy = x2 - x1, y2 - y1
    L = math.hypot(dx, dy)
    if L < 1e-6:
        return ""
    ux, uy = dx / L, dy / L
    head = min(9.0, max(5.0, L * 0.42))
    bx, by = x2 - ux * head, y2 - uy * head
    px, py = -uy, ux
    h = head * 0.5
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{bx:.1f}" y2="{by:.1f}" stroke="{color}" '
            f'stroke-width="{w}" stroke-opacity="{op}" stroke-linecap="round"/>'
            f'<polygon points="{x2:.1f},{y2:.1f} {bx+px*h:.1f},{by+py*h:.1f} {bx-px*h:.1f},{by-py*h:.1f}" '
            f'fill="{color}" fill-opacity="{op}"/>')


d = json.load(open(DATA))
recs = d["records"]
runs = collections.defaultdict(list)
for r in recs:
    runs[(r["organism"], r["judge"], r["seed"])].append(r)
for k in runs:
    runs[k].sort(key=lambda r: r["round"])

# global per-variable ranges (shared across figures)
RNG = {}
for v in ["value", "spread", "gap", "drift"]:
    vals = [r[v] for r in recs if r[v] is not None]
    lo, hi = min(vals), max(vals)
    pad = (hi - lo) * 0.08 or 0.02
    RNG[v] = (lo - pad, hi + pad)

runs_by_judge = collections.defaultdict(list)
for (org, judge, seed), pts in runs.items():
    runs_by_judge[judge].append((org, pts))


def make(xv, yv, fname, title, subtitle):
    P = 306
    G = 16
    COLS, ROWS = 3, 2
    MX, MY = 78, 128
    gw = COLS * P + (COLS - 1) * G
    gh = ROWS * P + (ROWS - 1) * G
    W = MX + gw + 40
    H = MY + gh + 84

    def sx(val, x0):
        lo, hi = RNG[xv]
        return x0 + 14 + (val - lo) / (hi - lo) * (P - 28)

    def sy(val, y0):
        lo, hi = RNG[yv]
        return y0 + P - 16 - (val - lo) / (hi - lo) * (P - 32)

    b = [ctext(MX + gw / 2, 46, title, 29, INK, "bold"),
         ctext(MX + gw / 2, 78, subtitle, 17, GRAY),
         ctext(MX + gw / 2, 100, "each path = one run; dot per training round, arrow to the next round · same axes in every panel",
               15, GRAY)]

    for idx, judge in enumerate(JUDGE_ORDER):
        r, c = divmod(idx, COLS)
        x0 = MX + c * (P + G)
        y0 = MY + r * (P + G)
        col = JUDGE_COLOR[judge]
        theruns = runs_by_judge.get(judge, [])
        orgs = sorted({o for o, _ in theruns})
        b.append(f'<rect x="{x0}" y="{y0}" width="{P}" height="{P}" rx="9" fill="white" stroke="#d0d7de" stroke-width="1.3"/>')
        # zero reference lines
        if RNG[xv][0] < 0 < RNG[xv][1]:
            zx = sx(0, x0)
            b.append(f'<line x1="{zx:.1f}" y1="{y0+10}" x2="{zx:.1f}" y2="{y0+P-14}" stroke="#eceef1" stroke-width="1.2"/>')
        if RNG[yv][0] < 0 < RNG[yv][1]:
            zy = sy(0, y0)
            b.append(f'<line x1="{x0+10}" y1="{zy:.1f}" x2="{x0+P-10}" y2="{zy:.1f}" stroke="#eceef1" stroke-width="1.2"/>')
        # trajectories
        for org, pts in theruns:
            xy = [(sx(p[xv], x0), sy(p[yv], y0)) for p in pts if p[xv] is not None and p[yv] is not None]
            for i in range(len(xy) - 1):
                b.append(arrow(*xy[i], *xy[i + 1], col))
            for (px, py) in xy:
                b.append(dot(px, py, org, col))
        # panel title
        b.append(f'<circle cx="{x0+14}" cy="{y0+20}" r="7" fill="{col}"/>')
        b.append(ltext(x0 + 27, y0 + 25, judge, 19, INK, "bold"))
        tag = " · ".join("Qwen" if o == "Qwen-K1" else "OLMo" for o in orgs) if orgs else "no runs"
        b.append(ltext(x0 + P - 10, y0 + 25, f"{len(theruns)} runs · {tag}", 13.5, GRAY, anchor="end"))

    # shared axis labels + corner ticks
    for r in range(ROWS):
        y0 = MY + r * (P + G)
        lo, hi = RNG[yv]
        b.append(ltext(MX - 8, y0 + 16, f"{hi - (hi-lo)*0.08:.2f}", 12.5, GRAY, anchor="end"))
        b.append(ltext(MX - 8, y0 + P - 12, f"{lo + (hi-lo)*0.08:.2f}", 12.5, GRAY, anchor="end"))
    for c in range(COLS):
        x0 = MX + c * (P + G)
        lo, hi = RNG[xv]
        b.append(ltext(x0 + 14, MY + gh + 16, f"{lo + (hi-lo)*0.08:.2f}", 12.5, GRAY))
        b.append(ltext(x0 + P - 14, MY + gh + 16, f"{hi - (hi-lo)*0.08:.2f}", 12.5, GRAY))
    b.append(ctext(MX + gw / 2, MY + gh + 44, f"x:  {LABEL[xv]}", 18, INK, "bold"))
    cx, cy = 30, MY + gh / 2
    b.append(f'<text x="{cx}" y="{cy:.1f}" text-anchor="middle" font-family="{FONT}" font-size="18" '
             f'font-weight="bold" fill="{INK}" transform="rotate(-90 {cx} {cy:.1f})">y:  {esc(LABEL[yv])}</text>')
    # organism-shape note
    b.append(ltext(MX + gw / 2 + 150, MY + gh + 44, "○ Qwen  ▪ OLMo", 15, GRAY))

    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" font-family="{FONT}">\n'
           f'<rect width="{W}" height="{H}" fill="white"/>\n' + "\n".join(b) + "\n</svg>")
    with open(os.path.join(FIGDIR, fname), "w") as f:
        f.write(svg)
    print(f"wrote {fname} ({W}x{H})")


make("value", "spread", "synthesis_traj_value_spread.svg",
     "Where the variation is: value vs candidate spread, by judge",
     "Own-pool loops. Spread (material to select from) is highest at mid value and collapses as a run rails to 0 or 1.")
make("gap", "drift", "synthesis_traj_gap_drift.svg",
     "Selection gap vs the value move it produces, by judge",
     "Own-pool loops. The kept-minus-pool gap this round against the value change the same round.")
make("value", "gap", "synthesis_traj_value_gap.svg",
     "Which way each judge pulls, by value level",
     "Own-pool loops. The selection gap (up = pulls value up) against the current value.")
