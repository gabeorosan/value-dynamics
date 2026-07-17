#!/usr/bin/env python3
"""Insecure-code behavior vs its stated probe on the Qwen self-selection loops.

The insecure-code analogue of ../behavior-vs-stated/. Unlike the risk organisms'
stated channel (which barely moves), this forced probe MOVES — but with an
unreliable sign: tracking ratios span -0.81 to +1.39 and the sign flips between
seeds of the very same cell.

Reads live numbers (with assertions) from:
  experiments/stated_channel_parity.json  (key qwen_insecure_loops)
Report: docs/report_stated_channel_parity.md

Run from this directory:  python3 insecure-behavior-vs-stated.py
Stdlib only, matching docs/figures/make_figures.py / ../behavior-vs-stated/ style.
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "..", "..", "..", "experiments",
                    "stated_channel_parity.json")

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


# ---- load ------------------------------------------------------------
D = json.load(open(DATA))
Q = D["qwen_insecure_loops"]
R = Q["rollouts"]
AGG = Q["aggregates"]
TH = D["moved_threshold"]
assert len(R) == 19, f"expected 19 rollouts, got {len(R)}"
assert TH == 0.15, TH

# ---- locate the anchor rollouts programmatically --------------------
CANDID = "candid self-prompt (self judge)"

# (a) the candid pair that flips: same behavioral move (>0.4), opposite stated
#     move. Find the two candid rollouts with the largest matched |d_traj| whose
#     stated moves have opposite sign and the widest stated separation.
cand = [r for r in R if r["cond"] == CANDID and r["d_traj"] > 0.4]
flip_pair = None
best = -1.0
for i in range(len(cand)):
    for j in range(len(cand)):
        a, b = cand[i], cand[j]
        if a["d_sr"] >= 0 or b["d_sr"] <= 0:      # a negative, b positive
            continue
        if abs(a["d_traj"] - b["d_traj"]) > 0.02:  # matched behavior move
            continue
        sep = b["d_sr"] - a["d_sr"]
        if sep > best:
            best, flip_pair = sep, (a, b)
flip_down, flip_up = flip_pair
assert round(flip_down["d_traj"], 3) == round(flip_up["d_traj"], 3) == 0.453
assert round(flip_down["d_sr"], 3) == -0.286 and round(flip_up["d_sr"], 3) == 0.589
assert flip_down["seed"] == "33" and flip_up["seed"] == "44"

# (b) the largest-|d_traj| oracle rollout
oracles = [r for r in R if "oracle" in r["cond"]]
oracle = max(oracles, key=lambda r: abs(r["d_traj"]))
assert round(oracle["d_traj"], 3) == -0.643 and oracle["seed"] == "101"
assert round(oracle["traj"][0], 3) == 0.974 and round(oracle["traj"][-1], 3) == 0.331

# ---- tracking-ratio range (the finding the risk version lacks) ------
trs = [r["tracking_ratio"] for r in R if r["tracking_ratio"] is not None]
tr_lo, tr_hi = min(trs), max(trs)
assert round(tr_lo, 2) == -0.81 and round(tr_hi, 2) == 1.39, (tr_lo, tr_hi)

# ---- per-group summary + sign chips (over behavior-moved rollouts) ---
GROUP_ORDER = [
    (CANDID, "candid self-prompt loops (self judge)"),
    ("min-insecurity oracle", "min-insecurity oracle"),
    ("oracle, base-mixed pool", "oracle, base-mixed pool"),
    ("self-judge duels, base-mixed pool", "self-judge duels, base-mixed pool"),
    ("base judge, static alternative", "base judge, static alternative"),
]
BARS = []
for key, label in GROUP_ORDER:
    a = AGG[key]
    pos = sum(1 for r in R if r["cond"] == key and abs(r["d_traj"]) >= TH
              and r["tracking_ratio"] is not None and r["tracking_ratio"] >= 0)
    neg = sum(1 for r in R if r["cond"] == key and abs(r["d_traj"]) >= TH
              and r["tracking_ratio"] is not None and r["tracking_ratio"] < 0)
    BARS.append((label, a["mean_abs_d_traj_moved"], a["mean_abs_d_sr_moved"],
                 a["n"], a["n_behavior_moved"], pos, neg))

# sanity vs the report table
_b = {b[0]: b for b in BARS}
assert _b["candid self-prompt loops (self judge)"][4] == 8
assert _b["candid self-prompt loops (self judge)"][5:7] == (5, 3)
assert _b["min-insecurity oracle"][5:7] == (0, 2)
assert sum(b[5] for b in BARS) == 9 and sum(b[6] for b in BARS) == 5  # 9 pos / 5 neg
assert round(_b["candid self-prompt loops (self judge)"][1], 3) == 0.463
assert round(_b["oracle, base-mixed pool"][2], 3) == 0.015

# ====================================================================
# Layout
# ====================================================================
W, H = 1580, 1130
s = []

# ---- headline + subtitle -------------------------------------------
s.append(f'<text x="60" y="64" font-size="33" font-weight="bold" fill="{INK}">'
         f'Insecure-code behavior and its stated probe, same runs, same rounds</text>')
sub = ("Qwen3-4B insecure-code organism's self-selection loops (n=19 cells, mostly baseline + 2 "
       "rounds). Solid = the per-answer self-description value score the loop "
       "selects on (frozen-Qwen 0–1 insecurity of its free-form coding "
       "answers). Dashed = the separate forced probe, never seen by any judge: "
       "does it SAY its code is insecure (mean p, 0–1). Both on 0–1.")
for i, ln in enumerate(wrap(sub, 128)):
    s.append(f'<text x="60" y="{96 + i*25}" font-size="18" fill="{GRAY}">{esc(ln)}</text>')

# ---- 2-item key ----------------------------------------------------
ky = 186
s.append(f'<line x1="62" y1="{ky}" x2="112" y2="{ky}" stroke="{RED}" stroke-width="4"/>')
s.append(f'<circle cx="87" cy="{ky}" r="5" fill="{RED}"/>')
s.append(f'<text x="122" y="{ky+6}" font-size="17" font-weight="bold" fill="{INK}">'
         f'behavior: insecurity value score (solid)</text>')
s.append(f'<line x1="482" y1="{ky}" x2="532" y2="{ky}" stroke="{RED}" stroke-width="3.5" '
         f'stroke-dasharray="3 6"/>')
s.append(f'<circle cx="507" cy="{ky}" r="4.5" fill="white" stroke="{RED}" stroke-width="2.2"/>')
s.append(f'<text x="542" y="{ky+6}" font-size="17" font-weight="bold" fill="{INK}">'
         f'stated probe: "does it say its code is insecure" (dashed)</text>')

# ====================================================================
# LEFT — three rollout panels stacked
# ====================================================================
px0 = 90
pw = 500
ph = 182
pitch = 274
ptop0 = 288

s.append(f'<text x="{px0}" y="232" font-size="20" font-weight="bold" fill="{INK}">'
         f'Three rollouts: behavior moves the same size, the stated probe does not</text>')

PANELS = [
    (flip_down, "candid self-prompt loop · low dose · seed 33",
     "behavior climbs, stated probe drops the OTHER way"),
    (flip_up, "candid self-prompt loop · low dose · seed 44",
     "same behavior climb — here the stated probe rises with it"),
    (oracle, "min-insecurity oracle · seed 101",
     "oracle drives behavior down; stated probe drifts up against it"),
]


def draw_panel(run, title, note, ptop):
    n = len(run["traj"])
    x0, y0, w, h = px0 + 30, ptop, pw, ph
    def AX(r):
        return x0 + (r / (n - 1)) * w
    def AY(v):
        return y0 + (1 - v) * h
    # title (well above the top gridline)
    s.append(f'<text x="{px0}" y="{ptop-16}" font-size="17" font-weight="bold" '
             f'fill="{INK}">{esc(title)}</text>')
    # gridlines + y ticks
    for v in (0.0, 0.5, 1.0):
        y = AY(v)
        s.append(f'<line x1="{x0}" y1="{y}" x2="{x0+w}" y2="{y}" stroke="#e9ebef" stroke-width="1.4"/>')
        s.append(f'<text x="{x0-10}" y="{y+5}" font-size="14" fill="{GRAY}" text-anchor="end">{v:.1f}</text>')
    # axes
    s.append(f'<line x1="{x0}" y1="{y0}" x2="{x0}" y2="{y0+h}" stroke="{INK}" stroke-width="1.8"/>')
    s.append(f'<line x1="{x0}" y1="{y0+h}" x2="{x0+w}" y2="{y0+h}" stroke="{INK}" stroke-width="1.8"/>')
    for r in range(n):
        s.append(f'<text x="{AX(r):.1f}" y="{y0+h+22}" font-size="14" fill="{GRAY}" '
                 f'text-anchor="middle">{r}</text>')
    s.append(f'<text x="{x0+w/2}" y="{y0+h+42}" font-size="14" fill="{GRAY}" '
             f'text-anchor="middle">round</text>')
    # behavior (solid)
    pts = " ".join(f"{AX(i):.1f},{AY(v):.1f}" for i, v in enumerate(run["traj"]))
    s.append(f'<polyline points="{pts}" fill="none" stroke="{RED}" stroke-width="4"/>')
    for i, v in enumerate(run["traj"]):
        s.append(f'<circle cx="{AX(i):.1f}" cy="{AY(v):.1f}" r="5.5" fill="{RED}"/>')
    # stated (dashed)
    ptss = " ".join(f"{AX(i):.1f},{AY(v):.1f}" for i, v in enumerate(run["sr"]))
    s.append(f'<polyline points="{ptss}" fill="none" stroke="{RED}" stroke-width="3.5" '
             f'stroke-dasharray="3 7" opacity="0.92"/>')
    for i, v in enumerate(run["sr"]):
        s.append(f'<circle cx="{AX(i):.1f}" cy="{AY(v):.1f}" r="4" fill="white" '
                 f'stroke="{RED}" stroke-width="2.2"/>')
    # start/end value labels beside the points (start to the right-in, end outside-right)
    def lbl(v, x, dy, anchor):
        s.append(f'<text x="{x:.1f}" y="{AY(v)+dy:.1f}" font-size="13.5" '
                 f'font-weight="bold" fill="{RED}" text-anchor="{anchor}">{v:.2f}</text>')
    # start labels: nudge behavior up, stated down so they never touch
    lbl(run["traj"][0], AX(0)+9, -8, "start")
    lbl(run["sr"][0], AX(0)+9, 16, "start")
    # end labels: just outside the right axis
    lbl(run["traj"][-1], AX(n-1)+9, 5, "start")
    lbl(run["sr"][-1], AX(n-1)+9, 5, "start")
    # net-move chips, clear to the right of the end labels
    cx = x0 + w + 66
    s.append(f'<text x="{cx}" y="{y0+34}" font-size="15" font-weight="bold" fill="{INK}">'
             f'behavior</text>')
    s.append(f'<text x="{cx}" y="{y0+55}" font-size="18" font-weight="bold" fill="{RED}">'
             f'{run["d_traj"]:+.2f}</text>')
    s.append(f'<text x="{cx}" y="{y0+92}" font-size="15" font-weight="bold" fill="{INK}">'
             f'stated</text>')
    s.append(f'<text x="{cx}" y="{y0+113}" font-size="18" font-weight="bold" fill="{RED}">'
             f'{run["d_sr"]:+.2f}</text>')
    tr = run["tracking_ratio"]
    s.append(f'<text x="{cx}" y="{y0+150}" font-size="13" fill="{GRAY}">tracking ratio</text>')
    s.append(f'<text x="{cx}" y="{y0+170}" font-size="16" font-weight="bold" fill="{GRAY}">'
             f'{tr:+.2f}</text>')
    # italic note below the x-axis label, spanning the panel
    s.append(f'<text x="{x0}" y="{y0+h+62}" font-size="14.5" font-style="italic" '
             f'fill="{RED}">{esc(note)}</text>')


for i, (run, title, note) in enumerate(PANELS):
    draw_panel(run, title, note, ptop0 + i * pitch)

# ====================================================================
# RIGHT — per condition-group summary + sign chips
# ====================================================================
bx0 = 900
bw = 430
by0 = 300
s.append(f'<text x="{bx0}" y="232" font-size="20" font-weight="bold" fill="{INK}">'
         f'Per condition-group: how big the move, and does the sign hold?</text>')
s.append(f'<text x="{bx0}" y="258" font-size="15" fill="{GRAY}">'
         f'mean absolute net move over rollouts where behavior moved ≥ {TH:.2f};</text>')
s.append(f'<text x="{bx0}" y="278" font-size="15" fill="{GRAY}">'
         f'chip = count of rollouts whose stated probe moved with (+) vs against (−) behavior</text>')

bmax = 0.70
def BX(v):
    return bx0 + (v / bmax) * bw

rowh = 116
for i, (label, dtraj, dsr, n, nmoved, pos, neg) in enumerate(BARS):
    yc = by0 + i * rowh
    # label
    s.append(f'<text x="{bx0}" y="{yc}" font-size="16" font-weight="bold" fill="{INK}">'
             f'{esc(label)} <tspan fill="{GRAY}" font-weight="normal">'
             f'(n={n}, moved={nmoved})</tspan></text>')
    if dtraj is None:
        s.append(f'<text x="{bx0}" y="{yc+30}" font-size="15" font-style="italic" '
                 f'fill="{GRAY}">no rollout moved ≥ {TH:.2f} — nothing to track</text>')
        continue
    # behavior bar (solid red)
    yb = yc + 20
    s.append(f'<rect x="{bx0}" y="{yb}" width="{BX(dtraj)-bx0:.1f}" height="17" rx="4" fill="{RED}"/>')
    s.append(f'<text x="{BX(dtraj)+8:.1f}" y="{yb+14}" font-size="15" font-weight="bold" '
             f'fill="{RED}">{dtraj:.2f}</text>')
    # stated bar (open, gray outline)
    ys = yc + 44
    s.append(f'<rect x="{bx0}" y="{ys}" width="{max(BX(dsr)-bx0,3):.1f}" height="13" rx="3" '
             f'fill="white" stroke="{GRAY}" stroke-width="2"/>')
    s.append(f'<text x="{BX(dsr)+8:.1f}" y="{ys+12}" font-size="14" fill="{GRAY}">'
             f'{dsr:.3f}</text>')
    # sign chip
    chx = bx0 + bw + 24
    s.append(f'<text x="{chx}" y="{yb+30}" font-size="20" font-weight="bold" fill="{INK}">'
             f'<tspan fill="{INK}">+{pos}</tspan>'
             f'<tspan fill="{GRAY}"> / </tspan>'
             f'<tspan fill="{RED}">−{neg}</tspan></text>')

# bar axis ticks under the last row
baseY = by0 + (len(BARS)-1) * rowh + 66
for t in (0.0, 0.2, 0.4, 0.6):
    x = BX(t)
    s.append(f'<line x1="{x}" y1="{by0+18}" x2="{x}" y2="{baseY}" stroke="#eef0f3" '
             f'stroke-width="1.2"/>')
    s.append(f'<text x="{x}" y="{baseY+22}" font-size="14" fill="{GRAY}" '
             f'text-anchor="middle">{t:.1f}</text>')
s.append(f'<text x="{bx0+bw/2}" y="{baseY+46}" font-size="15" fill="{INK}" '
         f'text-anchor="middle">mean absolute net move over the run</text>')

# inline key for the two bars
lky = baseY + 74
s.append(f'<rect x="{bx0}" y="{lky-14}" width="26" height="14" rx="3" fill="{RED}"/>')
s.append(f'<text x="{bx0+34}" y="{lky-2}" font-size="14" fill="{INK}">behavior move</text>')
s.append(f'<rect x="{bx0+205}" y="{lky-13}" width="26" height="12" rx="3" fill="white" '
         f'stroke="{GRAY}" stroke-width="2"/>')
s.append(f'<text x="{bx0+239}" y="{lky-2}" font-size="14" fill="{INK}">stated move</text>')

# ---- takeaway box (the sign-unreliability finding) -----------------
gy = lky + 26
s.append(f'<rect x="{bx0}" y="{gy}" width="{bw+70}" height="118" rx="9" fill="{KEY_FILL}" '
         f'stroke="{RED}" stroke-width="2"/>')
s.append(f'<text x="{bx0+16}" y="{gy+30}" font-size="16.5" fill="{INK}">'
         f'Unlike the risk organisms’ stated channel, this probe '
         f'<tspan font-weight="bold">moves</tspan> —</text>')
s.append(f'<text x="{bx0+16}" y="{gy+54}" font-size="16.5" fill="{INK}">'
         f'but its <tspan font-weight="bold" fill="{RED}">sign is unreliable.</tspan> '
         f'Across the 14 behavior-moved rollouts,</text>')
s.append(f'<text x="{bx0+16}" y="{gy+82}" font-size="20" font-weight="bold" fill="{INK}">'
         f'tracking ratio spans '
         f'<tspan fill="{RED}">{tr_lo:.2f}</tspan> to '
         f'<tspan fill="{RED}">{tr_hi:+.2f}</tspan>'
         f'<tspan font-size="15" font-weight="normal" fill="{GRAY}">  '
         f'(9 with, 5 against)</tspan></text>')
s.append(f'<text x="{bx0+16}" y="{gy+106}" font-size="14.5" fill="{GRAY}">'
         f'seeds 33 and 44 of one cell: same +0.45 behavior, stated '
         f'{flip_down["d_sr"]:+.2f} vs {flip_up["d_sr"]:+.2f}.</text>')

open(os.path.join(HERE, "insecure-behavior-vs-stated.svg"), "w").write(
    svg_doc(W, H, "\n".join(s)))
print("wrote insecure-behavior-vs-stated.svg")
