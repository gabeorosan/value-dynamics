#!/usr/bin/env python3
"""Behavioral risk vs stated risk tolerance on the K2 (OLMo) selection loops.

Same runs, same rounds: the behavioral-risk channel rails and reverses across
the full 0-1 range while the model's stated risk tolerance barely moves.

Reads live numbers (with assertions) from:
  experiments/selfreport_calibration_k2.json
Report: docs/report_selfreport_calibration_k2.md

Run from this directory:  python3 behavior-vs-stated.py
Stdlib only, matching docs/figures/src/make_figures.py house style.
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "..", "..", "..", "experiments",
                    "selfreport_calibration_k2.json")

# ---- palette copied verbatim from make_figures.py -------------------
INK = "#1a1a1a"
BLUE = "#2867b5"       # accent / self-judge series (validated)
GREEN = "#3a7d44"      # accent / frozen-judge series (validated)
RED = "#b5342c"        # emphasis for reversal / warning text
GRAY = "#6b7684"       # recessive only (axes, muted captions) — never a series
KEY_FILL = "#eef5ee"   # highlighted takeaway box

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


# ---- load + locate the anchor rollouts ------------------------------
D = json.load(open(DATA))
ROLL = {(r["cond"], r["seed"]): r for r in D["rollouts"]}
AGG = D["aggregates"]


def get(cond, seed):
    return ROLL[(cond, seed)]


oracle = get("oracle_hold", "21")
duel = get("h2h_invade_self", "54")
inject = get("invade_base", "35")

# assertions on the anchors we plot (round-to-2dp)
assert round(oracle["traj"][0], 2) == 0.92 and round(oracle["traj"][-1], 2) == 0.09, oracle["traj"]
assert round(oracle["sr"][0], 2) == 0.33 and round(oracle["sr"][-1], 2) == 0.31, oracle["sr"]
assert round(duel["traj"][0], 2) == 0.21 and round(duel["traj"][-1], 2) == 1.00, duel["traj"]
assert round(duel["sr"][0], 2) == 0.29 and round(duel["sr"][-1], 2) == 0.33, duel["sr"]
assert round(inject["traj"][0], 2) == 0.31 and round(inject["traj"][-1], 2) == 0.99, inject["traj"]
assert round(AGG["overall"]["mean_gap_r0"], 3) == 0.167, AGG["overall"]
assert round(AGG["overall"]["mean_gap_final"], 3) == 0.341, AGG["overall"]

# Panel B: named condition families (skip the 'other' catch-all), ordered
# by behavioral movement. Values read live from aggregates.
GROUPS = [
    ("oracle", "oracle reversals"),
    ("mixed_injection", "prompt-injection"),
    ("h2h_duels", "head-to-head duels"),
    ("release_holds_rescues", "release holds / rescues"),
    ("k2_grid", "K2 grid (frozen/self/random)"),
]
BARS = []
for key, label in GROUPS:
    a = AGG[key]
    BARS.append((label, a["mean_abs_d_traj_moved"], a["mean_abs_d_sr_moved"],
                 a["n_behavior_moved"]))
# assert the headline anchors from the report table
_o = dict((b[0], b) for b in BARS)
assert round(_o["oracle reversals"][1], 2) == 0.64
assert round(_o["oracle reversals"][2], 3) == 0.018

# ====================================================================
# Layout
# ====================================================================
W, H = 1560, 940
s = []

# ---- headline + subtitle -------------------------------------------
s.append(f'<text x="60" y="66" font-size="34" font-weight="bold" fill="{INK}">'
         f'Behavioral risk and stated risk tolerance, same runs, same rounds</text>')
sub = ("OLMo-2-1124-7B selection-loop rollouts only (n=46). Behavioral risk = "
       "per-round judged P(model picks the riskier EV-neutral gamble); stated "
       "risk tolerance = per-round P(model calls itself the risk-tolerant one).")
for i, ln in enumerate(wrap(sub, 118)):
    s.append(f'<text x="60" y="{98 + i*26}" font-size="19" fill="{GRAY}">{esc(ln)}</text>')

# ---- 2-item key (left, under the subtitle) -------------------------
kx, ky = 62, 158
s.append(f'<line x1="{kx}" y1="{ky}" x2="{kx+50}" y2="{ky}" stroke="{INK}" stroke-width="4"/>')
s.append(f'<text x="{kx+60}" y="{ky+6}" font-size="18" font-weight="bold" fill="{INK}">'
         f'Behavioral risk (solid line)</text>')
s.append(f'<line x1="{kx+340}" y1="{ky}" x2="{kx+390}" y2="{ky}" stroke="{INK}" '
         f'stroke-width="4" stroke-dasharray="3 6"/>')
s.append(f'<text x="{kx+400}" y="{ky+6}" font-size="18" font-weight="bold" fill="{INK}">'
         f'Stated risk tolerance (dashed line)</text>')

# ====================================================================
# Panel A — three example rollouts
# ====================================================================
ax0, ay0 = 90, 220          # plot origin (x, y-top)
aw, ah = 640, 560           # plot size
def AX(rnd, nrounds):
    return ax0 + (rnd / (nrounds - 1)) * aw
def AY(v):
    return ay0 + (1 - v) * ah

s.append(f'<text x="{ax0}" y="196" font-size="21" font-weight="bold" fill="{INK}">'
         f'Panel A &#183; three extreme rollouts</text>')

# gridlines + y ticks
for v in (0.0, 0.25, 0.5, 0.75, 1.0):
    y = AY(v)
    s.append(f'<line x1="{ax0}" y1="{y}" x2="{ax0+aw}" y2="{y}" stroke="#e6e8ec" stroke-width="1.5"/>')
    s.append(f'<text x="{ax0-12}" y="{y+6}" font-size="16" fill="{GRAY}" text-anchor="end">{v:.2f}</text>')
# axes
s.append(f'<line x1="{ax0}" y1="{ay0}" x2="{ax0}" y2="{ay0+ah}" stroke="{INK}" stroke-width="2"/>')
s.append(f'<line x1="{ax0}" y1="{ay0+ah}" x2="{ax0+aw}" y2="{ay0+ah}" stroke="{INK}" stroke-width="2"/>')
# x ticks (rounds 0..4)
for r in range(5):
    x = AX(r, 5)
    s.append(f'<text x="{x}" y="{ay0+ah+28}" font-size="16" fill="{GRAY}" text-anchor="middle">{r}</text>')
s.append(f'<text x="{ax0+aw/2}" y="{ay0+ah+58}" font-size="18" fill="{INK}" text-anchor="middle">'
         f'round</text>')
s.append(f'<text x="{ax0-58}" y="{ay0+ah/2}" font-size="18" fill="{INK}" text-anchor="middle" '
         f'transform="rotate(-90 {ax0-58} {ay0+ah/2})">risk (0 = safe, 1 = risky)</text>')

RUNS = [
    (oracle, RED, "oracle reversal · seed 21", "above"),
    (duel, BLUE, "peer-invasion duel · seed 54", "below"),
    (inject, GREEN, "prompt-injection invasion · seed 35", "below"),
]
for run, col, lbl, side in RUNS:
    n = len(run["traj"])
    # behavioral (solid)
    pts = " ".join(f"{AX(i,n):.1f},{AY(v):.1f}" for i, v in enumerate(run["traj"]))
    s.append(f'<polyline points="{pts}" fill="none" stroke="{col}" stroke-width="4"/>')
    for i, v in enumerate(run["traj"]):
        s.append(f'<circle cx="{AX(i,n):.1f}" cy="{AY(v):.1f}" r="5.5" fill="{col}"/>')
    # stated tolerance (dashed)
    ptss = " ".join(f"{AX(i,n):.1f},{AY(v):.1f}" for i, v in enumerate(run["sr"]))
    s.append(f'<polyline points="{ptss}" fill="none" stroke="{col}" stroke-width="3.5" '
             f'stroke-dasharray="3 7" opacity="0.9"/>')
    for i, v in enumerate(run["sr"]):
        s.append(f'<circle cx="{AX(i,n):.1f}" cy="{AY(v):.1f}" r="4" fill="white" '
                 f'stroke="{col}" stroke-width="2.2"/>')

# two-line run labels stacked in the gap between the two panels (right-anchored)
def runlabel(run, col, name, ytop):
    lx = 940                       # right edge, sits clear of Panel B
    s.append(f'<text x="{lx}" y="{ytop}" font-size="16" font-weight="bold" fill="{col}" '
             f'text-anchor="end">{name}</text>')
    s.append(f'<text x="{lx}" y="{ytop+20}" font-size="15" fill="{col}" text-anchor="end">'
             f'behavior {run["traj"][0]:.2f}→{run["traj"][-1]:.2f}</text>')
    # faint connector from the line's endpoint to the label
    n = len(run["traj"])
    s.append(f'<line x1="{AX(n-1,n):.1f}" y1="{AY(run["traj"][-1]):.1f}" x2="{lx-172}" '
             f'y2="{ytop-5}" stroke="{col}" stroke-width="1.4" opacity="0.45"/>')
runlabel(duel, BLUE, "peer-invasion duel · s54", 430)
runlabel(inject, GREEN, "prompt-injection · s35", 486)
runlabel(oracle, RED, "oracle reversal · s21", 724)

# annotation: the flat dashed band
band_lo = AY(0.36)
band_hi = AY(0.28)
s.append(f'<rect x="{ax0}" y="{band_hi}" width="{aw}" height="{band_lo-band_hi}" '
         f'fill="{INK}" opacity="0.05"/>')
s.append(f'<text x="{ax0+aw-8}" y="{AY(0.19)}" font-size="15" fill="{GRAY}" text-anchor="end">'
         f'every stated-tolerance line stays inside this 0.28–0.36 band</text>')

# ====================================================================
# Panel B — behaviour move vs stated move, per condition family
# ====================================================================
bx0 = 960
bw = 470
by0 = 240
s.append(f'<text x="{bx0}" y="196" font-size="21" font-weight="bold" fill="{INK}">'
         f'Panel B &#183; mean move per condition family</text>')
s.append(f'<text x="{bx0}" y="222" font-size="16" fill="{GRAY}">'
         f'mean size of the per-run change, over rollouts where behavior moved ≥ 0.15</text>')

# scale 0..0.7
bmax = 0.70
def BX(v):
    return bx0 + (v / bmax) * bw
# axis + ticks
baseY = by0 + 5*74 + 30
for t in (0.0, 0.2, 0.4, 0.6):
    x = BX(t)
    s.append(f'<line x1="{x}" y1="{by0-6}" x2="{x}" y2="{baseY}" stroke="#e6e8ec" stroke-width="1.5"/>')
    s.append(f'<text x="{x}" y="{baseY+26}" font-size="15" fill="{GRAY}" text-anchor="middle">{t:.1f}</text>')
s.append(f'<text x="{bx0+bw/2}" y="{baseY+52}" font-size="17" fill="{INK}" text-anchor="middle">'
         f'mean absolute change over the run</text>')

rowh = 74
for i, (label, dtraj, dsr, nmoved) in enumerate(BARS):
    yc = by0 + i * rowh + 26
    # behaviour bar (solid ink)
    s.append(f'<rect x="{bx0}" y="{yc-13}" width="{BX(dtraj)-bx0:.1f}" height="18" rx="4" fill="{INK}"/>')
    s.append(f'<text x="{BX(dtraj)+8:.1f}" y="{yc+2}" font-size="16" font-weight="bold" fill="{INK}">'
             f'{dtraj:.2f}</text>')
    # stated bar (open / hatched-light) just above baseline of the row
    s.append(f'<rect x="{bx0}" y="{yc+12}" width="{max(BX(dsr)-bx0,3):.1f}" height="12" rx="3" '
             f'fill="white" stroke="{GRAY}" stroke-width="2"/>')
    s.append(f'<text x="{BX(dsr)+10:.1f}" y="{yc+23}" font-size="15" fill="{GRAY}">'
             f'{dsr:.3f}</text>')
    # label
    s.append(f'<text x="{bx0}" y="{yc-22}" font-size="16" font-weight="bold" fill="{INK}">'
             f'{esc(label)} <tspan fill="{GRAY}" font-weight="normal">(n={nmoved})</tspan></text>')

# small inline key for Panel B
lky = baseY + 74
s.append(f'<rect x="{bx0}" y="{lky-16}" width="26" height="14" rx="3" fill="{INK}"/>')
s.append(f'<text x="{bx0+34}" y="{lky-4}" font-size="15" fill="{INK}">behavioral risk move</text>')
s.append(f'<rect x="{bx0+250}" y="{lky-15}" width="26" height="12" rx="3" fill="white" stroke="{GRAY}" stroke-width="2"/>')
s.append(f'<text x="{bx0+284}" y="{lky-4}" font-size="15" fill="{INK}">stated-tolerance move</text>')

# gap-widening readout box
gy = lky + 26
gr0 = AGG["overall"]["mean_gap_r0"]
grE = AGG["overall"]["mean_gap_final"]
s.append(f'<rect x="{bx0}" y="{gy}" width="{bw+60}" height="70" rx="8" fill="{KEY_FILL}" '
         f'stroke="{INK}" stroke-width="2"/>')
s.append(f'<text x="{bx0+16}" y="{gy+30}" font-size="17" fill="{INK}">'
         f'Mean behavior–statement gap <tspan font-weight="bold">widens</tspan> over a run:</text>')
s.append(f'<text x="{bx0+16}" y="{gy+56}" font-size="22" font-weight="bold" fill="{INK}">'
         f'{gr0:.3f} <tspan fill="{GRAY}">(round 0)</tspan>  →  {grE:.3f} '
         f'<tspan fill="{GRAY}">(final round)</tspan></text>')

open(os.path.join(HERE, "behavior-vs-stated.svg"), "w").write(svg_doc(W, H, "\n".join(s)))
print("wrote behavior-vs-stated.svg")
