#!/usr/bin/env python3
"""More candidates on the conversion-cascade idea (spread -> gap -> value move),
kept judge x organism SEPARATE so different generators are never pooled.

  A  synthesis_cascade_by_organism  — the cascade (mean spread, |gap|, |value
     move| per round) in its own panel for every judge x organism cell.
  B  synthesis_cascade_bars         — compact summary: for each judge x organism,
     the three stage magnitudes as grouped bars (available spread -> selection
     gap extracted -> value move produced), sorted by |gap|.

Data: experiments/state_space_explore.json (scripts/analysis_own_pool_records.py).
Own-pool only. Stdlib only.
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
C_SPREAD, C_GAP, C_DRIFT = "#6b7684", "#2867b5", "#b5342c"
ORG_SHORT = {"Qwen-K1": "Qwen", "OLMo-K2": "OLMo"}


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def ctext(x, y, t, size, color=INK, weight="normal"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="middle" font-family="{FONT}" '
            f'font-size="{size}" font-weight="{weight}" fill="{color}">{esc(t)}</text>')


def ltext(x, y, t, size, color=INK, weight="normal", anchor="start"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" font-family="{FONT}" '
            f'font-size="{size}" font-weight="{weight}" fill="{color}">{esc(t)}</text>')


def polyline(pts, color, w=2.6, dash=None):
    dd = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<polyline points="{" ".join(f"{x:.1f},{y:.1f}" for x,y in pts)}" fill="none" stroke="{color}" stroke-width="{w}" stroke-linejoin="round"{dd}/>'


def save(fname, W, H, body):
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" font-family="{FONT}">\n'
           f'<rect width="{W}" height="{H}" fill="white"/>\n' + "\n".join(body) + "\n</svg>")
    with open(os.path.join(FIGDIR, fname), "w") as f:
        f.write(svg)
    print(f"wrote {fname} ({W}x{H})")


d = json.load(open(DATA))
recs = d["records"]
by_cell = collections.defaultdict(list)
for r in recs:
    by_cell[(r["judge"], r["organism"])].append(r)
RMAX = max(r["round"] for r in recs)


def mean(v):
    return sum(v) / len(v) if v else 0.0


def cell_round_means(rows):
    agg = {"spread": collections.defaultdict(list), "gap": collections.defaultdict(list),
           "drift": collections.defaultdict(list)}
    for r in rows:
        agg["spread"][r["round"]].append(r["spread"])
        agg["gap"][r["round"]].append(abs(r["gap"]))
        agg["drift"][r["round"]].append(abs(r["drift"]))
    return {key: [(rnd, mean(agg[key][rnd])) for rnd in sorted(agg[key])] for key in agg}


CELLS = sorted(by_cell, key=lambda k: (k[1], k[0]))


# ================================================================= A: faceted cascade
def fig_by_organism():
    P, GC, GR, COLS = 262, 16, 44, 4
    ROWS = (len(CELLS) + COLS - 1) // COLS
    MX, MY = 70, 132
    GW = COLS * P + (COLS - 1) * GC
    GH = ROWS * P + (ROWS - 1) * GR
    W, H = MX + GW + 30, MY + GH + 96
    lo, hi = 0.0, 0.5

    def PX(rnd, x0):
        return x0 + 16 + (rnd - 1) / (RMAX - 1) * (P - 32)

    def PY(v, y0):
        return y0 + P - 16 - v / hi * (P - 48)

    b = [ctext(MX + GW / 2, 48, "The conversion cascade, per judge × organism", 29, INK, "bold"),
         ctext(MX + GW / 2, 80, "Mean per round: available spread, |selection gap| the judge extracts, |value move| produced. Generators kept separate.", 16, GRAY)]
    for idx, (judge, org) in enumerate(CELLS):
        r, c = divmod(idx, COLS)
        x0, y0 = MX + c * (P + GC), MY + r * (P + GR)
        b.append(f'<rect x="{x0}" y="{y0}" width="{P}" height="{P}" rx="8" fill="white" stroke="#d0d7de" stroke-width="1.3"/>')
        b.append(ltext(x0 + 12, y0 + 23, judge, 18, INK, "bold"))
        b.append(ltext(x0 + P - 10, y0 + 23, ORG_SHORT[org], 14, GRAY, anchor="end"))
        for gy in (0.1, 0.2, 0.3, 0.4):
            yy = PY(gy, y0)
            b.append(f'<line x1="{x0+16}" y1="{yy:.1f}" x2="{x0+P-16}" y2="{yy:.1f}" stroke="#eef0f2" stroke-width="1"/>')
        cm = cell_round_means(by_cell[(judge, org)])
        for key, col, dash in (("spread", C_SPREAD, None), ("gap", C_GAP, None), ("drift", C_DRIFT, "5 4")):
            pts = [(PX(rnd, x0), PY(v, y0)) for rnd, v in cm[key]]
            if len(pts) > 1:
                b.append(polyline(pts, col, 2.6, dash))
            for (x, y) in pts:
                b.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3" fill="{col}"/>')
    # axes + legend
    for idx in range(len(CELLS)):
        r, c = divmod(idx, COLS)
        x0, y0 = MX + c * (P + GC), MY + r * (P + GR)
        for rnd in range(1, RMAX + 1):
            b.append(ctext(PX(rnd, x0), y0 + P + 16, str(rnd), 12, GRAY))
    for r in range(ROWS):
        y0 = MY + r * (P + GR)
        b.append(ltext(MX - 8, PY(hi, y0) + 5, f"{hi:.1f}", 12, GRAY, anchor="end"))
        b.append(ltext(MX - 8, PY(0, y0) + 5, "0", 12, GRAY, anchor="end"))
    b.append(ctext(MX + GW / 2, MY + GH + 44, "training round", 17, INK, "bold"))
    lx = MX + 6
    ly = MY + GH + 74
    for col, t, dash in ((C_SPREAD, "spread (available)", None), (C_GAP, "|gap| (extracted)", None), (C_DRIFT, "|value move|", "5 4")):
        b.append(polyline([(lx, ly - 5), (lx + 32, ly - 5)], col, 3, dash))
        b.append(ltext(lx + 42, ly, t, 15, INK))
        lx += 42 + len(t) * 8.4 + 34
    save("synthesis_cascade_by_organism.svg", W, H, b)


# ================================================================= B: summary bars
def fig_bars():
    stats = []
    for (judge, org) in by_cell:
        rows = by_cell[(judge, org)]
        stats.append((judge, org, mean([r["spread"] for r in rows]),
                      mean([abs(r["gap"]) for r in rows]), mean([abs(r["drift"]) for r in rows])))
    stats.sort(key=lambda s: -s[3])  # by |gap|
    MX, MT, AXW = 250, 150, 620
    ROW = 82
    W, H = MX + AXW + 60, MT + ROW * len(stats) + 76
    xmax = max(max(s[2], s[3], s[4]) for s in stats) * 1.08

    def X(v):
        return MX + v / xmax * AXW

    b = [ctext(W / 2, 48, "Spread → gap → value move, summarised per judge × organism", 28, INK, "bold"),
         ctext(W / 2, 80, "Mean magnitude of each cascade stage. Bar length is directly comparable across judges. Generators kept separate.", 16, GRAY)]
    for gv in (0.1, 0.2, 0.3, 0.4):
        if gv < xmax:
            b.append(f'<line x1="{X(gv):.1f}" y1="{MT-14}" x2="{X(gv):.1f}" y2="{MT + ROW*len(stats)-24:.1f}" stroke="#eef0f2" stroke-width="1"/>')
            b.append(ctext(X(gv), MT + ROW * len(stats) - 8, f"{gv:.1f}", 13, GRAY))
    for i, (judge, org, sp, gp, dr) in enumerate(stats):
        y0 = MT + i * ROW
        b.append(ltext(MX - 16, y0 + 28, judge, 18, INK, "bold", anchor="end"))
        b.append(ltext(MX - 16, y0 + 47, ORG_SHORT[org], 14, GRAY, anchor="end"))
        for j, (v, col, lab) in enumerate([(sp, C_SPREAD, "spread"), (gp, C_GAP, "|gap|"), (dr, C_DRIFT, "|move|")]):
            yy = y0 + 12 + j * 18
            b.append(f'<rect x="{MX}" y="{yy:.1f}" width="{max(1,X(v)-MX):.1f}" height="14" rx="2" fill="{col}"/>')
            b.append(ltext(X(v) + 8, yy + 12, f"{v:.2f}", 13, col, "bold"))
            if i == 0:
                b.append(ltext(X(xmax) + 4, yy + 12, lab, 12.5, col))
    save("synthesis_cascade_bars.svg", W, H, b)


fig_by_organism()
fig_bars()
