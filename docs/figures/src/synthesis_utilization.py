#!/usr/bin/env python3
"""Figures centred on UTILIZATION — how much of the available candidate spread a
judge actually converts into a directional selection gap.

  util = realized gap / achievable gap (keeping the most-extreme candidates), in
  [0, 1].  0 = kept set no more extreme than the pool; 1 = kept the extremes,
  fully exploiting the spread.  Computed per round by
  scripts/analysis_own_pool_records.py -> experiments/state_space_explore.json.

Emits:
  synthesis_util_ranking       — how much each judge utilizes (dots + mean), ranked
  synthesis_util_over_rounds   — is utilization a stable judge property? (mean vs round)
  synthesis_util_drives_move   — utilization vs the value move it produces

Own-pool (single-generator) data only. Stdlib only.
Regenerate:  python3 synthesis_utilization.py
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
JUDGE_COLOR = {"self": "#2867b5", "risk copy": "#8a5a9e", "cautious copy": "#3a7d44",
               "base": "#6b7684", "random": "#c07d18", "score oracle": "#b5342c"}
JUDGE_ORDER = ["self", "risk copy", "cautious copy", "base", "random", "score oracle"]


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def ctext(x, y, t, size, color=INK, weight="normal"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="middle" font-family="{FONT}" '
            f'font-size="{size}" font-weight="{weight}" fill="{color}">{esc(t)}</text>')


def ltext(x, y, t, size, color=INK, weight="normal", anchor="start"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" font-family="{FONT}" '
            f'font-size="{size}" font-weight="{weight}" fill="{color}">{esc(t)}</text>')


def save(fname, W, H, body):
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" font-family="{FONT}">\n'
           f'<rect width="{W}" height="{H}" fill="white"/>\n' + "\n".join(body) + "\n</svg>")
    with open(os.path.join(FIGDIR, fname), "w") as f:
        f.write(svg)
    print(f"wrote {fname} ({W}x{H})")


d = json.load(open(DATA))
recs = [r for r in d["records"] if r["util"] is not None]
SEEDS = sorted({r["seed"] for r in d["records"]}, key=int)
SEED_COLOR = {s: SEED_PALETTE[i % len(SEED_PALETTE)] for i, s in enumerate(SEEDS)}
by_judge = collections.defaultdict(list)
for r in recs:
    by_judge[r["judge"]].append(r)


def mean(v):
    return sum(v) / len(v) if v else 0.0


# ================================================================= 1: ranking
def fig_ranking():
    order = sorted(JUDGE_ORDER, key=lambda j: -mean([r["util"] for r in by_judge[j]]))
    MX, MT, AXW = 190, 150, 660
    LANE = 74
    W = MX + AXW + 260
    H = MT + LANE * len(order) + 70

    def X(u):
        return MX + u * AXW

    b = [ctext(W / 2, 50, "How much of the available spread each judge exploits", 30, INK, "bold"),
         ctext(W / 2, 84, "utilization = realized selection gap ÷ the gap achievable by keeping the most-extreme candidates (0–1).",
               17, GRAY),
         ctext(W / 2, 106, "Each dot = one training round; ◆ = judge mean. Own-pool loops only.", 15, GRAY)]
    # gridlines
    for u in (0, 0.25, 0.5, 0.75, 1.0):
        b.append(f'<line x1="{X(u):.1f}" y1="{MT-10}" x2="{X(u):.1f}" y2="{MT + LANE*len(order)-18}" stroke="#e6e9ec" stroke-width="1"/>')
        b.append(ctext(X(u), MT + LANE * len(order) - 2, f"{u:.2f}", 14, GRAY))
    b.append(ctext(MX + AXW / 2, MT + LANE * len(order) + 26, "utilization", 18, INK, "bold"))
    b.append(f'<line x1="{X(1):.1f}" y1="{MT-10}" x2="{X(1):.1f}" y2="{MT + LANE*len(order)-18}" stroke="#b9c0c8" stroke-width="1.5" stroke-dasharray="3 4"/>')
    b.append(ltext(X(1) + 6, MT - 14, "full (keeps the extremes)", 13.5, GRAY))

    for i, j in enumerate(order):
        cy = MT + i * LANE + LANE / 2 - 6
        rows = by_judge[j]
        m = mean([r["util"] for r in rows])
        b.append(ltext(MX - 16, cy + 6, j, 20, INK, "bold", anchor="end"))
        # baseline
        b.append(f'<line x1="{MX:.1f}" y1="{cy:.1f}" x2="{MX+AXW:.1f}" y2="{cy:.1f}" stroke="#f0f2f4" stroke-width="1"/>')
        for k, r in enumerate(rows):
            jit = ((k * 37) % 100 / 100 - 0.5) * 30
            b.append(f'<circle cx="{X(r["util"]):.1f}" cy="{cy + jit:.1f}" r="4" fill="{SEED_COLOR[r["seed"]]}" fill-opacity="0.8"/>')
        b.append(f'<path d="M {X(m):.1f} {cy-15:.1f} L {X(m)+9:.1f} {cy:.1f} L {X(m):.1f} {cy+15:.1f} L {X(m)-9:.1f} {cy:.1f} Z" fill="{INK}"/>')
        b.append(ltext(X(m), cy - 22, f"{m:.2f}", 17, INK, "bold", anchor="middle"))
        org = " · ".join(sorted({"Qwen" if r["organism"] == "Qwen-K1" else "OLMo" for r in rows}))
        b.append(ltext(MX + AXW + 18, cy + 6, f"{len(rows)} rounds · {org}", 14.5, GRAY))
    # seed legend
    lx = MX
    ly = H - 20
    b.append(ltext(lx, ly, "seed", 14, INK, "bold"))
    lx += 44
    for s in SEEDS:
        b.append(f'<rect x="{lx:.1f}" y="{ly-10:.1f}" width="12" height="12" rx="2" fill="{SEED_COLOR[s]}"/>')
        b.append(ltext(lx + 16, ly, s, 13.5, INK))
        lx += 46
    save("synthesis_util_ranking.svg", W, H, b)


# ================================================================= 2: over rounds
def fig_over_rounds():
    RMAX = max(r["round"] for r in recs)
    MX, MY, PW, PH = 92, 132, 720, 420
    W = MX + PW + 250
    H = MY + PH + 90

    def X(rnd):
        return MX + (rnd - 1) / (RMAX - 1) * PW

    def Y(u):
        return MY + PH - u * PH

    b = [ctext(W / 2, 50, "Is utilization a stable property of the judge? Utilization over rounds", 29, INK, "bold"),
         ctext(W / 2, 82, "Own-pool loops. Each line = one judge's mean utilization per training round.", 17, GRAY)]
    for u in (0, 0.25, 0.5, 0.75, 1.0):
        b.append(f'<line x1="{MX}" y1="{Y(u):.1f}" x2="{MX+PW}" y2="{Y(u):.1f}" stroke="#eef0f2" stroke-width="1"/>')
        b.append(ltext(MX - 10, Y(u) + 5, f"{u:.2f}", 14, GRAY, anchor="end"))
    for rnd in range(1, RMAX + 1):
        b.append(ctext(X(rnd), MY + PH + 26, str(rnd), 14, GRAY))
    b.append(ctext(MX + PW / 2, MY + PH + 54, "training round", 18, INK, "bold"))
    b.append(f'<text x="34" y="{MY+PH/2:.1f}" text-anchor="middle" font-size="18" font-weight="bold" '
             f'fill="{INK}" font-family="{FONT}" transform="rotate(-90 34 {MY+PH/2:.1f})">mean utilization</text>')
    ly = MY + 6
    for j in JUDGE_ORDER:
        rows = by_judge[j]
        byr = collections.defaultdict(list)
        for r in rows:
            byr[r["round"]].append(r["util"])
        pts = [(X(rnd), Y(mean(byr[rnd]))) for rnd in sorted(byr)]
        col = JUDGE_COLOR[j]
        if len(pts) > 1:
            b.append(f'<polyline points="{" ".join(f"{x:.1f},{y:.1f}" for x,y in pts)}" fill="none" stroke="{col}" stroke-width="3"/>')
        for (x, y) in pts:
            b.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4.2" fill="{col}"/>')
        # right legend
        b.append(f'<circle cx="{MX+PW+22}" cy="{ly-5:.1f}" r="7" fill="{col}"/>')
        b.append(ltext(MX + PW + 36, ly, j, 16, INK))
        ly += 30
    save("synthesis_util_over_rounds.svg", W, H, b)


# ================================================================= 3: utilization drives movement
def fig_drives():
    MX, MY, PW, PH = 92, 132, 700, 460
    W = MX + PW + 250
    H = MY + PH + 84
    ymax = max(abs(r["drift"]) for r in recs) * 1.08

    def X(u):
        return MX + u * PW

    def Y(dd):
        return MY + PH - dd / ymax * PH

    b = [ctext(W / 2, 50, "Utilization vs the value move it produces", 30, INK, "bold"),
         ctext(W / 2, 82, "Own-pool loops. x = utilization (0–1); y = |value move| that round. Each dot = one round, coloured by judge.", 16, GRAY)]
    for u in (0, 0.25, 0.5, 0.75, 1.0):
        b.append(f'<line x1="{X(u):.1f}" y1="{MY}" x2="{X(u):.1f}" y2="{MY+PH}" stroke="#eef0f2" stroke-width="1"/>')
        b.append(ctext(X(u), MY + PH + 24, f"{u:.2f}", 14, GRAY))
    for dd in (0.1, 0.2, 0.3, 0.4):
        if dd < ymax:
            b.append(f'<line x1="{MX}" y1="{Y(dd):.1f}" x2="{MX+PW}" y2="{Y(dd):.1f}" stroke="#eef0f2" stroke-width="1"/>')
            b.append(ltext(MX - 10, Y(dd) + 5, f"{dd:.1f}", 14, GRAY, anchor="end"))
    b.append(ctext(MX + PW / 2, MY + PH + 52, "utilization", 18, INK, "bold"))
    b.append(f'<text x="34" y="{MY+PH/2:.1f}" text-anchor="middle" font-size="18" font-weight="bold" '
             f'fill="{INK}" font-family="{FONT}" transform="rotate(-90 34 {MY+PH/2:.1f})">|value move| that round</text>')
    for r in recs:
        b.append(f'<circle cx="{X(r["util"]):.1f}" cy="{Y(abs(r["drift"])):.1f}" r="4.4" fill="{JUDGE_COLOR[r["judge"]]}" fill-opacity="0.75"/>')
    ly = MY + 6
    for j in JUDGE_ORDER:
        b.append(f'<circle cx="{MX+PW+22}" cy="{ly-5:.1f}" r="7" fill="{JUDGE_COLOR[j]}"/>')
        b.append(ltext(MX + PW + 36, ly, j, 16, INK))
        ly += 30
    save("synthesis_util_drives_move.svg", W, H, b)


fig_ranking()
fig_over_rounds()
fig_drives()
