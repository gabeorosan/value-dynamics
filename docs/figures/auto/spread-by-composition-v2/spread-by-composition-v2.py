#!/usr/bin/env python3
"""Draft figure (v2, simplified): candidate value-spread under three pool
compositions. Three small side-by-side panels sharing a y-axis; mean lines
with endpoint numbers, faint individual runs behind. All prose lives in the
writeup caption, not the SVG.

Data: experiments/spread_util_unified.json (records + spread_ledger).
House style: docs/figures/src/make_figures.py (Evans-lab look).
Regenerate:  python3 spread-by-composition-v2.py   (from this directory,
stdlib only)
"""
import json
import os
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "..", "..", "..", "experiments",
                    "spread_util_unified.json")

INK = "#1a1a1a"
BLUE = "#2867b5"       # accent / self-judge series (validated)
GREEN = "#3a7d44"      # accent / frozen-judge series (validated)
RED = "#b5342c"        # emphasis for reversal / warning text
GRAY = "#6b7684"       # recessive only (axes, muted captions) — never a series

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


def svg_doc(w, h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
            f'font-family="{FONT}">\n<rect width="{w}" height="{h}" fill="white"/>\n'
            f'{body}\n</svg>')


# ----------------------------------------------------------------- data
with open(DATA) as f:
    D = json.load(f)
RECS = D["records"]
LEDGER = D["spread_ledger"]


def runs_of(organism, composition):
    """Individual run trajectories: group by (cond, seed, source)."""
    g = defaultdict(list)
    for r in RECS:
        if r["organism"] == organism and r["composition"] == composition:
            g[(r["cond"], r["seed"], r["source"])].append((r["round"], r["spread"]))
    return [sorted(v) for v in g.values()]


def mean_by_round(organism, composition):
    g = defaultdict(list)
    for r in RECS:
        if r["organism"] == organism and r["composition"] == composition:
            g[r["round"]].append(r["spread"])
    return sorted((rd, sum(v) / len(v)) for rd, v in g.items())


olmo_self = mean_by_round("OLMo", "self-only")
qwen_self = mean_by_round("Qwen", "self-only")
olmo_base = mean_by_round("OLMo", "base-mixed")
qwen_base = mean_by_round("Qwen", "base-mixed")
olmo_peer = mean_by_round("OLMo", "peer-mixed")

runs_olmo_self = runs_of("OLMo", "self-only")
runs_qwen_self = runs_of("Qwen", "self-only")
runs_olmo_base = runs_of("OLMo", "base-mixed")
runs_qwen_base = runs_of("Qwen", "base-mixed")
runs_olmo_peer = runs_of("OLMo", "peer-mixed")

slope_olmo_self = LEDGER["OLMo/self-only"]["persistence"]["slope"]
slope_qwen_self = LEDGER["Qwen/self-only"]["persistence"]["slope"]

# ----------------------------------------------------------------- layout
W, H = 1440, 620
b = []

b.append(f'<text x="{W // 2}" y="52" text-anchor="middle" font-size="26" '
         f'font-weight="bold" fill="{INK}" font-family="{FONT}">'
         f'{esc("Who fills the candidate pool decides whether value-spread persists, is refilled, or collapses")}</text>')
b.append(f'<text x="{W // 2}" y="84" text-anchor="middle" font-size="16" '
         f'fill="{GRAY}" font-family="{FONT}">'
         f'{esc("spread = SD of the judge value reading across the candidate answers on one item, averaged over the round; " + str(D["n_records"]) + " rounds from " + str(D["n_runs"]) + " runs")}</text>')

# one-line key
KEYY = 116
kx = 330
b.append(f'<line x1="{kx}" y1="{KEYY - 5}" x2="{kx + 40}" y2="{KEYY - 5}" '
         f'stroke="{INK}" stroke-width="4"/>')
b.append(f'<text x="{kx + 50}" y="{KEYY}" font-size="16" fill="{INK}" '
         f'font-family="{FONT}">OLMo organisms (mean)</text>')
kx += 280
b.append(f'<line x1="{kx}" y1="{KEYY - 5}" x2="{kx + 40}" y2="{KEYY - 5}" '
         f'stroke="{INK}" stroke-width="4" stroke-dasharray="10 7"/>')
b.append(f'<text x="{kx + 50}" y="{KEYY}" font-size="16" fill="{INK}" '
         f'font-family="{FONT}">Qwen organisms (mean)</text>')
kx += 280
b.append(f'<line x1="{kx}" y1="{KEYY - 5}" x2="{kx + 40}" y2="{KEYY - 5}" '
         f'stroke="{INK}" stroke-width="1.5" stroke-opacity="0.45"/>')
b.append(f'<text x="{kx + 50}" y="{KEYY}" font-size="16" fill="{INK}" '
         f'font-family="{FONT}">individual runs</text>')

# panel geometry — shared y-axis, shared 1..8 round axis so slopes compare
PX = [120, 575, 1030]          # plot-area left edges
PW, PH = 340, 300              # plot-area size
Y0 = 230                       # plot-area top
YMAX = 0.5                     # spread axis 0 .. 0.5
RMAX = 8                       # round axis 1 .. 8


def xr(px0, rd):
    return px0 + (rd - 1) / (RMAX - 1) * PW


def ys(v):
    return Y0 + PH - v / YMAX * PH


def polyline(px0, pts, color, sw, dash=None, opacity=1.0, markers=False):
    s = " ".join(f"{xr(px0, rd):.1f},{ys(v):.1f}" for rd, v in pts)
    dd = f' stroke-dasharray="{dash}"' if dash else ""
    out = [f'<polyline points="{s}" fill="none" stroke="{color}" '
           f'stroke-width="{sw}" stroke-opacity="{opacity}" '
           f'stroke-linejoin="round" stroke-linecap="round"{dd}/>']
    if markers:
        for rd, v in pts:
            out.append(f'<circle cx="{xr(px0, rd):.1f}" cy="{ys(v):.1f}" r="5" '
                       f'fill="{color}"/>')
    return "\n".join(out)


def panel_frame(px0, title, phrase, color):
    s = []
    s.append(f'<text x="{px0 + PW / 2}" y="{168}" text-anchor="middle" '
             f'font-size="21" font-weight="bold" fill="{color}" '
             f'font-family="{FONT}">{esc(title)}</text>')
    s.append(f'<text x="{px0 + PW / 2}" y="{196}" text-anchor="middle" '
             f'font-size="17" fill="{INK}" font-family="{FONT}">{esc(phrase)}</text>')
    for i in range(6):
        v = i * 0.1
        yy = ys(v)
        s.append(f'<line x1="{px0}" y1="{yy:.1f}" x2="{px0 + PW}" y2="{yy:.1f}" '
                 f'stroke="#dddddd" stroke-width="1"/>')
        if px0 == PX[0]:
            s.append(f'<text x="{px0 - 12}" y="{yy + 5:.1f}" text-anchor="end" '
                     f'font-size="15" fill="{GRAY}" font-family="{FONT}">{v:.1f}</text>')
    s.append(f'<line x1="{px0}" y1="{Y0}" x2="{px0}" y2="{Y0 + PH}" '
             f'stroke="{GRAY}" stroke-width="1.5"/>')
    s.append(f'<line x1="{px0}" y1="{Y0 + PH}" x2="{px0 + PW}" y2="{Y0 + PH}" '
             f'stroke="{GRAY}" stroke-width="1.5"/>')
    for rd in range(1, RMAX + 1):
        xx = xr(px0, rd)
        s.append(f'<line x1="{xx:.1f}" y1="{Y0 + PH}" x2="{xx:.1f}" y2="{Y0 + PH + 6}" '
                 f'stroke="{GRAY}" stroke-width="1.5"/>')
        s.append(f'<text x="{xx:.1f}" y="{Y0 + PH + 24}" text-anchor="middle" '
                 f'font-size="15" fill="{GRAY}" font-family="{FONT}">{rd}</text>')
    s.append(f'<text x="{px0 + PW / 2}" y="{Y0 + PH + 50}" text-anchor="middle" '
             f'font-size="18" fill="{INK}" font-family="{FONT}">round</text>')
    return "\n".join(s)


def value_label(px0, rd, v, color, dx, dy, anchor):
    return (f'<text x="{xr(px0, rd) + dx:.1f}" y="{ys(v) + dy:.1f}" '
            f'text-anchor="{anchor}" font-size="16" font-weight="bold" '
            f'fill="{color}" font-family="{FONT}">{v:.2f}</text>')


# y-axis title (once, left of panel A)
b.append(f'<text x="46" y="{Y0 + PH / 2}" font-size="18" fill="{INK}" '
         f'font-family="{FONT}" text-anchor="middle" '
         f'transform="rotate(-90 46 {Y0 + PH / 2})">candidate value spread '
         f'(within-item SD)</text>')

# --- panel A: self-only pool -----------------------------------------
pA = PX[0]
b.append(panel_frame(
    pA, "Self-only pool",
    f"spread persists (slope {slope_olmo_self:.2f}–{slope_qwen_self:.2f})",
    BLUE))
for run in runs_olmo_self + runs_qwen_self:
    b.append(polyline(pA, run, BLUE, 1.3, opacity=0.15))
b.append(polyline(pA, olmo_self, BLUE, 4.5, markers=True))
b.append(polyline(pA, qwen_self, BLUE, 4.5, dash="10 7", markers=True))
b.append(value_label(pA, *olmo_self[0], BLUE, 6, 24, "start"))    # 0.30, below-right r1
b.append(value_label(pA, *qwen_self[0], BLUE, 6, -12, "start"))   # 0.36, above-right r1
b.append(value_label(pA, *olmo_self[-1], BLUE, 12, 5, "start"))   # 0.23, right of r8
b.append(value_label(pA, *qwen_self[-1], BLUE, 2, -14, "middle"))  # 0.28, above r4

# --- panel B: base-mixed pool ----------------------------------------
pB = PX[1]
b.append(panel_frame(pB, "Base-mixed pool", "an outside supplier refills it",
                     GREEN))
for run in runs_olmo_base + runs_qwen_base:
    b.append(polyline(pB, run, GREEN, 1.3, opacity=0.15))
b.append(polyline(pB, olmo_base, GREEN, 4.5, markers=True))
b.append(polyline(pB, qwen_base, GREEN, 4.5, dash="10 7", markers=True))
b.append(value_label(pB, *olmo_base[0], GREEN, -10, 0, "end"))    # 0.35
b.append(value_label(pB, *qwen_base[0], GREEN, -10, 22, "end"))   # 0.32
b.append(value_label(pB, *olmo_base[-1], GREEN, 12, 5, "start"))  # 0.38
b.append(value_label(pB, *qwen_base[-1], GREEN, 12, 5, "start"))  # 0.10

# --- panel C: peer-mixed pool ----------------------------------------
pC = PX[2]
b.append(panel_frame(pC, "Peer-mixed pool", "an extreme invader consumes it",
                     RED))
for run in runs_olmo_peer:
    b.append(polyline(pC, run, RED, 1.3, opacity=0.15))
b.append(polyline(pC, olmo_peer, RED, 4.5, markers=True))
b.append(value_label(pC, *olmo_peer[0], RED, -10, 0, "end"))      # 0.43
b.append(value_label(pC, *olmo_peer[-1], RED, 12, -8, "start"))   # 0.03

svg = svg_doc(W, H, "\n".join(b))
out = os.path.join(HERE, "spread-by-composition-v2.svg")
with open(out, "w") as f:
    f.write(svg)
print(f"wrote {out} ({len(svg)} bytes)")
