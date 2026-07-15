#!/usr/bin/env python3
"""Figures centred on UTILIZATION — how much of the available candidate spread a
judge's selection exploits, relative to random selection.

  util (per round) = (|net gap| − null) / (|achievable-in-direction| − null),
  where the net gap is the round-mean kept-minus-pool gap, achievable is the
  most-extreme pair gap in that gap's DIRECTION (so the min-risk oracle, keeping
  the 2 lowest, scores ~1 even on lopsided pools), and null = E|net gap| under
  random selection (analytic half-normal).  In [0, 1]: 0 = no better than random
  · 1 = the most-extreme pair in its direction.  Rank/offset-invariant.  NOT
  comparable across organisms (alignment depends on the generator), so every view
  keeps judge × organism separate.  scripts/analysis_own_pool_records.py.

Emits:
  synthesis_util_ranking      — utilization per judge × organism, ranked (0 = random)
  synthesis_util_over_rounds  — is it a stable property? mean utilization per round

Own-pool (single-generator) data only. Stdlib only.
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
ORG_SHORT = {"Qwen-K1": "Qwen", "OLMo-K2": "OLMo"}


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
# group by (judge, organism)
by_cell = collections.defaultdict(list)
for r in recs:
    by_cell[(r["judge"], r["organism"])].append(r)


def mean(v):
    return sum(v) / len(v) if v else 0.0


# ================================================================= ranking
def fig_ranking():
    cells = sorted(by_cell, key=lambda k: -mean([r["util"] for r in by_cell[k]]))
    MX, MT, LO, HI = 250, 168, -0.15, 1.0
    AXW = 640
    LANE = 62
    W = MX + AXW + 250
    H = MT + LANE * len(cells) + 66

    def X(u):
        return MX + (u - LO) / (HI - LO) * AXW

    b = [ctext(W / 2, 48, "How much of the available spread each judge's selection exploits (vs random)", 27, INK, "bold"),
         ctext(W / 2, 80, "utilization = how far the round's net selection gap reaches toward the most-extreme achievable pair IN ITS DIRECTION, beyond random.",
               15.5, GRAY),
         ctext(W / 2, 101, "0 = random selection · 1 = full (e.g. the min-risk oracle keeps the 2 lowest). Kept judge × organism SEPARATE. Each dot = one round; ◆ = mean.", 14.5, GRAY)]
    bottom = MT + LANE * len(cells) - 16
    for u in (0, 0.25, 0.5, 0.75, 1.0):
        b.append(f'<line x1="{X(u):.1f}" y1="{MT-12}" x2="{X(u):.1f}" y2="{bottom:.1f}" stroke="#e6e9ec" stroke-width="1"/>')
        b.append(ctext(X(u), bottom + 20, f"{u:.2f}", 14, GRAY))
    b.append(ctext(MX + AXW / 2, bottom + 46, "utilization", 18, INK, "bold"))
    # random (0) and full (1) reference lines
    b.append(f'<line x1="{X(0):.1f}" y1="{MT-12}" x2="{X(0):.1f}" y2="{bottom:.1f}" stroke="#9aa2ab" stroke-width="1.6" stroke-dasharray="3 4"/>')
    b.append(ltext(X(0), MT - 18, "random selection", 13.5, GRAY, anchor="middle"))
    b.append(f'<line x1="{X(1):.1f}" y1="{MT-12}" x2="{X(1):.1f}" y2="{bottom:.1f}" stroke="#9aa2ab" stroke-width="1.6" stroke-dasharray="3 4"/>')
    b.append(ltext(X(1), MT - 18, "keeps the extremes", 13.5, GRAY, anchor="middle"))

    for i, (judge, org) in enumerate(cells):
        cy = MT + i * LANE + LANE / 2 - 4
        rows = by_cell[(judge, org)]
        m = mean([r["util"] for r in rows])
        b.append(ltext(MX - 18, cy + 1, judge, 19, INK, "bold", anchor="end"))
        b.append(ltext(MX - 18, cy + 19, ORG_SHORT[org], 14.5, GRAY, anchor="end"))
        b.append(f'<line x1="{MX:.1f}" y1="{cy:.1f}" x2="{MX+AXW:.1f}" y2="{cy:.1f}" stroke="#f0f2f4" stroke-width="1"/>')
        for k, r in enumerate(rows):
            jit = ((k * 37) % 100 / 100 - 0.5) * 26
            b.append(f'<circle cx="{X(r["util"]):.1f}" cy="{cy + jit:.1f}" r="3.8" fill="{SEED_COLOR[r["seed"]]}" fill-opacity="0.8"/>')
        b.append(f'<path d="M {X(m):.1f} {cy-13:.1f} L {X(m)+8:.1f} {cy:.1f} L {X(m):.1f} {cy+13:.1f} L {X(m)-8:.1f} {cy:.1f} Z" fill="{INK}"/>')
        b.append(ltext(X(m), cy - 19, f"{m:+.2f}", 16, INK, "bold", anchor="middle"))
        b.append(ltext(MX + AXW + 18, cy + 5, f"{len(rows)} rounds", 14, GRAY))
    # seed legend
    lx, ly = MX, H - 18
    b.append(ltext(lx, ly, "seed", 14, INK, "bold"))
    lx += 44
    for s in SEEDS:
        b.append(f'<rect x="{lx:.1f}" y="{ly-10:.1f}" width="12" height="12" rx="2" fill="{SEED_COLOR[s]}"/>')
        b.append(ltext(lx + 16, ly, s, 13.5, INK))
        lx += 46
    save("synthesis_util_ranking.svg", W, H, b)


# ================================================================= over rounds
def fig_over_rounds():
    RMAX = max(r["round"] for r in recs)
    MX, MY, PW, PH = 92, 138, 700, 400
    W = MX + PW + 300
    H = MY + PH + 84
    cells = sorted(by_cell, key=lambda k: -mean([r["util"] for r in by_cell[k]]))
    # colour by judge, dash by organism
    JCOL = {"self": "#2867b5", "risk copy": "#8a5a9e", "cautious copy": "#3a7d44",
            "base": "#c07d18", "random": "#6b7684", "score oracle": "#b5342c"}

    def X(rnd):
        return MX + (rnd - 1) / (RMAX - 1) * PW

    def Y(u):
        return MY + PH - (u + 0.15) / 1.15 * PH

    b = [ctext(W / 2, 48, "Is utilization a stable property of the judge? (per judge × organism)", 27, INK, "bold"),
         ctext(W / 2, 80, "Own-pool loops. Directional utilization per round. Solid = Qwen, dashed = OLMo. 0 = random, 1 = the extreme in its direction.", 16, GRAY)]
    for u in (0, 0.25, 0.5, 0.75, 1.0):
        yy = Y(u)
        b.append(f'<line x1="{MX}" y1="{yy:.1f}" x2="{MX+PW}" y2="{yy:.1f}" stroke="{"#c9ced4" if u==0 else "#eef0f2"}" stroke-width="{1.4 if u==0 else 1}"/>')
        b.append(ltext(MX - 10, yy + 5, f"{u:.2f}", 14, GRAY, anchor="end"))
    b.append(ltext(MX + PW + 8, Y(0) + 5, "random", 13, GRAY))
    for rnd in range(1, RMAX + 1):
        b.append(ctext(X(rnd), MY + PH + 26, str(rnd), 14, GRAY))
    b.append(ctext(MX + PW / 2, MY + PH + 54, "training round", 18, INK, "bold"))
    b.append(f'<text x="34" y="{MY+PH/2:.1f}" text-anchor="middle" font-size="18" font-weight="bold" '
             f'fill="{INK}" font-family="{FONT}" transform="rotate(-90 34 {MY+PH/2:.1f})">mean utilization</text>')
    ly = MY + 4
    for (judge, org) in cells:
        rows = by_cell[(judge, org)]
        byr = collections.defaultdict(list)
        for r in rows:
            byr[r["round"]].append(r["util"])
        pts = [(X(rnd), Y(mean(byr[rnd]))) for rnd in sorted(byr)]
        col = JCOL[judge]
        dash = ' stroke-dasharray="6 4"' if org == "OLMo-K2" else ""
        if len(pts) > 1:
            b.append(f'<polyline points="{" ".join(f"{x:.1f},{y:.1f}" for x,y in pts)}" fill="none" stroke="{col}" stroke-width="2.8"{dash}/>')
        for (x, y) in pts:
            b.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4" fill="{col}"/>')
        b.append(f'<line x1="{MX+PW+20}" y1="{ly-5:.1f}" x2="{MX+PW+50}" y2="{ly-5:.1f}" stroke="{col}" stroke-width="3"{dash}/>')
        b.append(ltext(MX + PW + 58, ly, f"{judge} · {ORG_SHORT[org]}", 15, INK))
        ly += 27
    save("synthesis_util_over_rounds.svg", W, H, b)


fig_ranking()
fig_over_rounds()
