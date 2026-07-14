#!/usr/bin/env python3
"""Candidate clarifying figures for the spread -> gap -> value-change mechanism.

Three framings of the same single-generator (own-pool) data, all faceted by
judge, so we can pick what actually clarifies:

  A  synthesis_cand_spread_over_rounds  — does the candidate spread run out?
       spread vs round, one line per run (seed colour) + bold mean line.
  B  synthesis_cand_conversion_cascade  — the pipeline: mean spread, |gap|,
       |value move| vs round (three lines) per judge — how much material exists,
       how much the judge extracts as a gap, how much the value actually moves.
  C  synthesis_cand_grip                — gap vs spread with the |gap| <= spread
       envelope; how much of the available spread each judge turns into a
       directional gap (mean |gap|/spread annotated = "grip").

Data: experiments/state_space_explore.json (scripts/analysis_own_pool_records.py).
Regenerate:  python3 synthesis_conversion_candidates.py   (stdlib only)
"""
import collections
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
FIGDIR = os.path.dirname(HERE) if os.path.basename(HERE) == "src" else HERE
ROOT = os.path.dirname(os.path.dirname(FIGDIR))
DATA = os.path.join(ROOT, "experiments", "state_space_explore.json")

INK = "#1a1a1a"
GRAY = "#6b7684"
FONT = "Helvetica, Arial, sans-serif"
SEED_PALETTE = ["#2867b5", "#b5342c", "#3a7d44", "#c07d18", "#8a5a9e",
                "#1f9e9e", "#d1477a", "#5b6bbf", "#8a6d3b", "#4c9f3a"]
JUDGE_ORDER = ["self", "risk copy", "cautious copy", "base", "random", "score oracle"]


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def ctext(x, y, t, size, color=INK, weight="normal"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="middle" font-family="{FONT}" '
            f'font-size="{size}" font-weight="{weight}" fill="{color}">{esc(t)}</text>')


def ltext(x, y, t, size, color=INK, weight="normal", anchor="start"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" font-family="{FONT}" '
            f'font-size="{size}" font-weight="{weight}" fill="{color}">{esc(t)}</text>')


def polyline(pts, color, w=2.0, op=1.0, dash=None):
    if len(pts) < 2:
        return "".join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{max(2,w):.1f}" fill="{color}"/>' for x, y in pts)
    d = f' stroke-dasharray="{dash}"' if dash else ""
    pth = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    return f'<polyline points="{pth}" fill="none" stroke="{color}" stroke-width="{w}" stroke-opacity="{op}" stroke-linejoin="round"{d}/>'


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

RMAX = max(r["round"] for r in recs)

# ---------------- shared facet frame
P, GC, GR, COLS, ROWS = 300, 16, 40, 3, 2
MX, MY = 78, 128
GW = COLS * P + (COLS - 1) * GC
GH = ROWS * P + (ROWS - 1) * GR


def panel_xy(idx):
    r, c = divmod(idx, COLS)
    return MX + c * (P + GC), MY + r * (P + GR)


def frame(title, subtitle):
    W = MX + GW + 36
    H = MY + GH + 118
    b = [ctext(MX + GW / 2, 46, title, 29, INK, "bold"),
         ctext(MX + GW / 2, 78, subtitle, 17, GRAY)]
    return b, W, H


def panel_box(b, x0, y0, judge, tag):
    b.append(f'<rect x="{x0}" y="{y0}" width="{P}" height="{P}" rx="9" fill="white" stroke="#d0d7de" stroke-width="1.3"/>')
    b.append(ltext(x0 + 14, y0 + 25, judge, 20, INK, "bold"))
    b.append(ltext(x0 + P - 10, y0 + 25, tag, 13.5, GRAY, anchor="end"))


PLOT_TOP, PLOT_BOT, PLOT_L, PLOT_R = 40, 16, 14, 14   # inner margins within a panel


def rxx(rnd, x0):
    return x0 + PLOT_L + (rnd - 1) / (RMAX - 1) * (P - PLOT_L - PLOT_R)


def yval(v, y0, lo, hi):
    return y0 + P - PLOT_BOT - (v - lo) / (hi - lo) * (P - PLOT_TOP - PLOT_BOT)


# ================================================================= A: spread over rounds
def fig_spread_over_rounds():
    b, W, H = frame("Does the candidate spread run out? Spread over rounds, by judge",
                    "Own-pool loops. y = candidate value spread (mean within-item SD); one line per run, bold line = judge mean.")
    lo, hi = 0.0, 0.5
    for idx, judge in enumerate(JUDGE_ORDER):
        x0, y0 = panel_xy(idx)
        theruns = runs_by_judge.get(judge, [])
        panel_box(b, x0, y0, judge, f"{len(theruns)} runs")
        for gy in (0.1, 0.2, 0.3, 0.4):
            yy = yval(gy, y0, lo, hi)
            b.append(f'<line x1="{x0+PLOT_L}" y1="{yy:.1f}" x2="{x0+P-PLOT_R}" y2="{yy:.1f}" stroke="#eef0f2" stroke-width="1"/>')
        by_round = collections.defaultdict(list)
        for org, seed, pts in theruns:
            line = [(rxx(p["round"], x0), yval(p["spread"], y0, lo, hi)) for p in pts]
            b.append(polyline(line, SEED_COLOR[seed], w=1.6, op=0.7))
            for p in pts:
                by_round[p["round"]].append(p["spread"])
        mean_line = [(rxx(r, x0), yval(sum(by_round[r]) / len(by_round[r]), y0, lo, hi))
                     for r in sorted(by_round) if by_round[r]]
        b.append(polyline(mean_line, INK, w=3.0))
        for (mx, my) in mean_line:
            b.append(f'<circle cx="{mx:.1f}" cy="{my:.1f}" r="3.4" fill="{INK}"/>')
    axis_round_y(b, "candidate spread", lo, hi)
    seed_legend(b)
    return "synthesis_cand_spread_over_rounds.svg", b, W, H


# ================================================================= B: conversion cascade
def fig_conversion_cascade():
    b, W, H = frame("The conversion cascade: spread → gap → value move, by judge",
                    "Own-pool loops. Per round, the judge mean of: available spread, |selection gap| extracted, |value move| produced.")
    lo, hi = 0.0, 0.5
    C_SPREAD, C_GAP, C_DRIFT = "#6b7684", "#2867b5", "#b5342c"
    for idx, judge in enumerate(JUDGE_ORDER):
        x0, y0 = panel_xy(idx)
        theruns = runs_by_judge.get(judge, [])
        panel_box(b, x0, y0, judge, f"{len(theruns)} runs")
        for gy in (0.1, 0.2, 0.3, 0.4):
            yy = yval(gy, y0, lo, hi)
            b.append(f'<line x1="{x0+PLOT_L}" y1="{yy:.1f}" x2="{x0+P-PLOT_R}" y2="{yy:.1f}" stroke="#eef0f2" stroke-width="1"/>')
        agg = {"spread": collections.defaultdict(list), "gap": collections.defaultdict(list),
               "drift": collections.defaultdict(list)}
        for org, seed, pts in theruns:
            for p in pts:
                agg["spread"][p["round"]].append(p["spread"])
                agg["gap"][p["round"]].append(abs(p["gap"]))
                agg["drift"][p["round"]].append(abs(p["drift"]))
        for key, col, dash in (("spread", C_SPREAD, None), ("gap", C_GAP, None), ("drift", C_DRIFT, "5 4")):
            line = [(rxx(r, x0), yval(sum(agg[key][r]) / len(agg[key][r]), y0, lo, hi))
                    for r in sorted(agg[key]) if agg[key][r]]
            b.append(polyline(line, col, w=2.8, dash=dash))
            for (mx, my) in line:
                b.append(f'<circle cx="{mx:.1f}" cy="{my:.1f}" r="3.2" fill="{col}"/>')
    axis_round_y(b, "mean magnitude", lo, hi)
    # legend for the three quantities
    lx = MX + 6
    ly = MY + GH + 84
    for col, t, dash in ((C_SPREAD, "spread (material available)", None),
                         (C_GAP, "|selection gap| (judge extracts)", None),
                         (C_DRIFT, "|value move| (result)", "5 4")):
        b.append(polyline([(lx, ly - 5), (lx + 34, ly - 5)], col, w=3, dash=dash))
        b.append(ltext(lx + 44, ly, t, 15, INK))
        lx += 40 + len(t) * 8.4 + 30
    return "synthesis_cand_conversion_cascade.svg", b, W, H


# ================================================================= C: grip (gap vs spread)
def fig_grip():
    b, W, H = frame("How much gap each judge pulls from the available spread",
                    "Own-pool loops. x = spread, y = selection gap. Dashed envelope = |gap| ≤ spread (the most a judge could extract).")
    xlo, xhi = 0.0, 0.5
    ylo, yhi = -0.45, 0.45

    def gx(v, x0):
        return x0 + PLOT_L + (v - xlo) / (xhi - xlo) * (P - PLOT_L - PLOT_R)

    def gy(v, y0):
        return y0 + P - PLOT_BOT - (v - ylo) / (yhi - ylo) * (P - PLOT_TOP - PLOT_BOT)

    for idx, judge in enumerate(JUDGE_ORDER):
        x0, y0 = panel_xy(idx)
        theruns = runs_by_judge.get(judge, [])
        # envelope + zero
        b.append(f'<rect x="{x0}" y="{y0}" width="{P}" height="{P}" rx="9" fill="white" stroke="#d0d7de" stroke-width="1.3"/>')
        b.append(f'<line x1="{gx(0,x0):.1f}" y1="{gy(0,y0):.1f}" x2="{gx(0.45,x0):.1f}" y2="{gy(0.45,y0):.1f}" stroke="#cfd6dd" stroke-width="1.2" stroke-dasharray="4 4"/>')
        b.append(f'<line x1="{gx(0,x0):.1f}" y1="{gy(0,y0):.1f}" x2="{gx(0.45,x0):.1f}" y2="{gy(-0.45,y0):.1f}" stroke="#cfd6dd" stroke-width="1.2" stroke-dasharray="4 4"/>')
        b.append(f'<line x1="{x0+PLOT_L}" y1="{gy(0,y0):.1f}" x2="{x0+P-PLOT_R}" y2="{gy(0,y0):.1f}" stroke="#eceef1" stroke-width="1.2"/>')
        grips = []
        for org, seed, pts in theruns:
            col = SEED_COLOR[seed]
            for p in pts:
                b.append(f'<circle cx="{gx(p["spread"],x0):.1f}" cy="{gy(p["gap"],y0):.1f}" r="3.4" fill="{col}" fill-opacity="0.82"/>')
                if p["spread"] > 0.02:
                    grips.append(abs(p["gap"]) / p["spread"])
        panel_box_overlay(b, x0, y0, judge)
        if grips:
            b.append(ltext(x0 + P - 10, y0 + 25, f"grip {sum(grips)/len(grips):.2f}", 14, INK, weight="bold", anchor="end"))
    # x axis = spread, y axis = gap
    axis_generic(b, "spread", "selection gap (kept − pool)", xlo, xhi, ylo, yhi)
    seed_legend(b)
    return "synthesis_cand_grip.svg", b, W, H


def panel_box_overlay(b, x0, y0, judge):
    b.append(ltext(x0 + 14, y0 + 25, judge, 20, INK, "bold"))


# ---------------- axis helpers
def axis_round_y(b, ylabel, lo, hi):
    for idx in range(len(JUDGE_ORDER)):
        x0, y0 = panel_xy(idx)
        for rnd in range(1, RMAX + 1):
            b.append(ctext(rxx(rnd, x0), y0 + P + 16, str(rnd), 12.5, GRAY))
    b.append(ctext(MX + GW / 2, MY + GH + 42, "x:  training round", 18, INK, "bold"))
    for r in range(ROWS):
        _, y0 = panel_xy(r * COLS)
        b.append(ltext(MX - 8, yval(hi, y0, lo, hi) + 5, f"{hi:.1f}", 12, GRAY, anchor="end"))
        b.append(ltext(MX - 8, yval(lo, y0, lo, hi) + 5, f"{lo:.1f}", 12, GRAY, anchor="end"))
    cx, cy = 28, MY + GH / 2
    b.append(f'<text x="{cx}" y="{cy:.1f}" text-anchor="middle" font-family="{FONT}" font-size="18" '
             f'font-weight="bold" fill="{INK}" transform="rotate(-90 {cx} {cy:.1f})">y:  {esc(ylabel)}</text>')


def axis_generic(b, xlabel, ylabel, xlo, xhi, ylo, yhi):
    b.append(ctext(MX + GW / 2, MY + GH + 42, f"x:  {xlabel}", 18, INK, "bold"))
    cx, cy = 28, MY + GH / 2
    b.append(f'<text x="{cx}" y="{cy:.1f}" text-anchor="middle" font-family="{FONT}" font-size="18" '
             f'font-weight="bold" fill="{INK}" transform="rotate(-90 {cx} {cy:.1f})">y:  {esc(ylabel)}</text>')


def seed_legend(b):
    step = 52
    legw = 46 + len(SEEDS) * step + 154
    lx = MX + GW / 2 - legw / 2
    ley = MY + GH + 88
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


for builder in (fig_spread_over_rounds, fig_conversion_cascade, fig_grip):
    fname, body, W, H = builder()
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" font-family="{FONT}">\n'
           f'<rect width="{W}" height="{H}" fill="white"/>\n' + "\n".join(body) + "\n</svg>")
    with open(os.path.join(FIGDIR, fname), "w") as f:
        f.write(svg)
    print(f"wrote {fname} ({W}x{H})")
