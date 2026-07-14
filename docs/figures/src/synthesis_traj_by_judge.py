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

# each judge is its own panel, so colour distinguishes SEEDS within a panel
SEED_PALETTE = ["#2867b5", "#b5342c", "#3a7d44", "#c07d18", "#8a5a9e",
                "#1f9e9e", "#d1477a", "#5b6bbf", "#8a6d3b", "#4c9f3a"]
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

SEEDS = sorted({r["seed"] for r in recs}, key=int)
SEED_COLOR = {s: SEED_PALETTE[i % len(SEED_PALETTE)] for i, s in enumerate(SEEDS)}

runs_by_judge = collections.defaultdict(list)
for (org, judge, seed), pts in runs.items():
    runs_by_judge[judge].append((org, seed, pts))


def lerp(v, lo, hi, a, bb):
    return a + (v - lo) / (hi - lo) * (bb - a)


def padded(vals):
    lo, hi = min(vals), max(vals)
    if hi - lo < 1e-6:
        lo, hi = lo - 0.02, hi + 0.02
    pad = (hi - lo) * 0.13
    return lo - pad, hi + pad


def make(xv, yv, fname, title, subtitle):
    P = 300
    GC, GR = 16, 32          # column gap; larger row gap fits each panel's range line
    COLS, ROWS = 3, 2
    MX, MY = 74, 128
    gw = COLS * P + (COLS - 1) * GC
    gh = ROWS * P + (ROWS - 1) * GR
    W = MX + gw + 36
    H = MY + gh + 96

    b = [ctext(MX + gw / 2, 46, title, 29, INK, "bold"),
         ctext(MX + gw / 2, 78, subtitle, 17, GRAY),
         ctext(MX + gw / 2, 100, "each path = one run; dot per training round, arrow to the next · EACH PANEL is scaled to its own runs (range printed below it)",
               15, GRAY)]

    for idx, judge in enumerate(JUDGE_ORDER):
        r, c = divmod(idx, COLS)
        x0 = MX + c * (P + GC)
        y0 = MY + r * (P + GR)
        theruns = runs_by_judge.get(judge, [])
        orgs = sorted({o for o, _, _ in theruns})
        b.append(f'<rect x="{x0}" y="{y0}" width="{P}" height="{P}" rx="9" fill="white" stroke="#d0d7de" stroke-width="1.3"/>')
        b.append(ltext(x0 + 14, y0 + 25, judge, 20, INK, "bold"))
        tag = " · ".join("Qwen" if o == "Qwen-K1" else "OLMo" for o in orgs) if orgs else "no runs"
        b.append(ltext(x0 + P - 10, y0 + 25, f"{len(theruns)} runs · {tag}", 13.5, GRAY, anchor="end"))
        pdata = [(p[xv], p[yv]) for _, _, pts in theruns for p in pts
                 if p[xv] is not None and p[yv] is not None]
        if not pdata:
            continue
        xs = [a for a, _ in pdata]
        ys = [bb for _, bb in pdata]
        xr, yr = padded(xs), padded(ys)

        def PX(v):
            return lerp(v, xr[0], xr[1], x0 + 14, x0 + P - 14)

        def PY(v):
            return lerp(v, yr[0], yr[1], y0 + P - 16, y0 + 34)

        # zero reference lines (only if this panel's range crosses 0)
        if xr[0] < 0 < xr[1]:
            zx = PX(0)
            b.append(f'<line x1="{zx:.1f}" y1="{y0+34}" x2="{zx:.1f}" y2="{y0+P-14}" stroke="#eceef1" stroke-width="1.2"/>')
        if yr[0] < 0 < yr[1]:
            zy = PY(0)
            b.append(f'<line x1="{x0+10}" y1="{zy:.1f}" x2="{x0+P-10}" y2="{zy:.1f}" stroke="#eceef1" stroke-width="1.2"/>')
        # trajectories, coloured by seed
        for org, seed, pts in theruns:
            col = SEED_COLOR[seed]
            xy = [(PX(p[xv]), PY(p[yv])) for p in pts if p[xv] is not None and p[yv] is not None]
            for i in range(len(xy) - 1):
                b.append(arrow(*xy[i], *xy[i + 1], col))
            for (px, py) in xy:
                b.append(dot(px, py, org, col))
        # this panel's data range (so free scales stay readable)
        b.append(ltext(x0 + 4, y0 + P + 18,
                       f"x {min(xs):.2f}–{max(xs):.2f}    y {min(ys):.2f}–{max(ys):.2f}", 12.5, GRAY))

    b.append(ctext(MX + gw / 2, MY + gh + 50, f"x:  {LABEL[xv]}", 18, INK, "bold"))
    cx, cy = 28, MY + gh / 2
    b.append(f'<text x="{cx}" y="{cy:.1f}" text-anchor="middle" font-family="{FONT}" font-size="18" '
             f'font-weight="bold" fill="{INK}" transform="rotate(-90 {cx} {cy:.1f})">y:  {esc(LABEL[yv])}</text>')
    # seed-colour legend + organism shapes (centred strip)
    step = 52
    legw = 46 + len(SEEDS) * step + 154
    lx = MX + gw / 2 - legw / 2
    ley = MY + gh + 80
    b.append(ltext(lx, ley + 5, "seed", 15, INK, "bold"))
    lx += 46
    for s in SEEDS:
        b.append(f'<rect x="{lx:.1f}" y="{ley - 9:.1f}" width="13" height="13" rx="2" fill="{SEED_COLOR[s]}"/>')
        b.append(ltext(lx + 19, ley + 5, s, 14, INK))
        lx += step
    lx += 22
    b.append(f'<circle cx="{lx + 6:.1f}" cy="{ley:.1f}" r="5.5" fill="{GRAY}"/>')
    b.append(ltext(lx + 17, ley + 5, "Qwen", 14, GRAY))
    lx += 74
    b.append(f'<rect x="{lx:.1f}" y="{ley - 5.5:.1f}" width="11" height="11" fill="{GRAY}"/>')
    b.append(ltext(lx + 18, ley + 5, "OLMo", 14, GRAY))

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
