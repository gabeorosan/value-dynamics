#!/usr/bin/env python3
"""Synthesis candidate A: the (agreement rho, spread sigma) plane.

Every modelable run placed at its round-1 dials; dot color encodes ONE thing --
the run's observed net endpoint move of the behavioral value, on a continuous
red(up)-gray(none)-blue(down) diverging scale with a slim colorbar. Uniform dot
size; no |rho*sigma| contours; no cluster callouts.

Reads experiments/spread_util_unified.json (records list). One run = the tuple
(cond, seed, source); the round-1 record supplies rho, spread, value; the last
record supplies value+drift. Runs whose round-1 rho is null (zero within-pool
spread makes the correlation undefined) are not plottable on these two axes.

Style reference: docs/figures/src/make_figures.py (INK/BLUE/GREEN/RED/GRAY,
esc()/wrap()). Stdlib only. Run from this directory:  python3 synthesis-dial-plane.py
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "..", "..", "..", "experiments",
                    "spread_util_unified.json")

# ---- palette (verbatim from make_figures.py) --------------------------------
INK = "#1a1a1a"
BLUE = "#2867b5"       # self-judge series / here: value moved DOWN
GREEN = "#3a7d44"
RED = "#b5342c"        # emphasis / here: value moved UP
GRAY = "#6b7684"       # recessive only + here: diverging neutral midpoint
KEY_FILL = "#eef5ee"
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


# ---- color helpers (continuous diverging scale on the endpoint move) --------
def _hex2rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def _rgb2hex(rgb):
    return "#%02x%02x%02x" % tuple(max(0, min(255, int(round(c)))) for c in rgb)


def lerp(c1, c2, t):
    a, b = _hex2rgb(c1), _hex2rgb(c2)
    return _rgb2hex([a[i] + (b[i] - a[i]) * t for i in range(3)])


DEAD = 0.15   # |move| below this reads as "no net move" (gray midpoint)
CAP = 0.60    # move at which the color saturates


def move_color(move):
    """Continuous diverging color: blue for down, gray at ~0, red for up."""
    m = abs(move)
    if m < DEAD:
        return GRAY
    t = min((m - DEAD) / (CAP - DEAD), 1.0)
    pole = BLUE if move < 0 else RED
    return lerp(GRAY, pole, 0.25 + 0.75 * t)


DOT_R = 10.0   # uniform dot radius (no size encoding)


# ---- load & reduce to one point per run ------------------------------------
def load_runs():
    d = json.load(open(DATA))
    from collections import defaultdict
    runs = defaultdict(list)
    for r in d["records"]:
        runs[(r["cond"], r["seed"], r["source"])].append(r)
    plot, skipped = [], 0
    for key, rs in runs.items():
        rs = sorted(rs, key=lambda x: x["round"])
        r1 = [x for x in rs if x["round"] == 1][0]
        if r1.get("rho") is None:
            skipped += 1
            continue
        last = rs[-1]
        move = (last["value"] + (last["drift"] or 0.0)) - r1["value"]
        plot.append(dict(cond=r1["cond"], seed=key[1], src=r1["source"],
                         rho=r1["rho"], spread=r1["spread"],
                         value=r1["value"], move=move))
    return d, plot, len(runs), skipped


DATA_D, RUNS, N_RUNS, N_SKIP = load_runs()
assert N_RUNS == 74, N_RUNS
assert len(RUNS) == 67, len(RUNS)
assert N_SKIP == 7, N_SKIP

N_UP = sum(1 for r in RUNS if r["move"] >= DEAD)
N_DOWN = sum(1 for r in RUNS if r["move"] <= -DEAD)
N_FLAT = sum(1 for r in RUNS if abs(r["move"]) < DEAD)
assert N_UP + N_DOWN + N_FLAT == len(RUNS)

# ---- geometry ---------------------------------------------------------------
W, H = 1300, 880
PL, PR = 150, 900           # plot left / right (px)
PT, PB = 250, 700           # plot top / bottom (px)
RHO0, RHO1 = -1.08, 0.95    # x data domain
SIG0, SIG1 = 0.0, 0.50      # y data domain


def X(rho):
    return PL + (rho - RHO0) / (RHO1 - RHO0) * (PR - PL)


def Y(sig):
    return PB - (sig - SIG0) / (SIG1 - SIG0) * (PB - PT)


# ============================================================================
body = []

# ---- title / subtitle (orientation only) ------------------------------------
title = ("Every run at its round-1 agreement and spread, colored by where its "
         "value went")
for i, ln in enumerate(wrap(title, 62)):
    body.append(f'<text x="{PL}" y="{62 + i*38}" font-family="{FONT}" '
                f'font-size="30" font-weight="bold" fill="{INK}">'
                f'{esc(ln)}</text>')
sub = (f"one dot per run · {len(RUNS)} modelable runs from "
       f"experiments/spread_util_unified.json (round-1 record per run)")
body.append(f'<text x="{PL}" y="176" font-family="{FONT}" '
            f'font-size="21" fill="{GRAY}">{esc(sub)}</text>')

# ---- axes -------------------------------------------------------------------
# plot frame
body.append(f'<rect x="{PL}" y="{PT}" width="{PR-PL}" height="{PB-PT}" '
            f'fill="none" stroke="{GRAY}" stroke-width="1.6"/>')
# rho=0 reference line (light)
body.append(f'<line x1="{X(0):.1f}" y1="{PT}" x2="{X(0):.1f}" y2="{PB}" '
            f'stroke="{GRAY}" stroke-width="1.1" stroke-opacity="0.4"/>')
body.append(f'<text x="{X(0):.1f}" y="{PT-8}" font-family="{FONT}" '
            f'font-size="15" fill="{GRAY}" text-anchor="middle" '
            f'font-style="italic">&#961; = 0</text>')
# x ticks
for rv in [-1.0, -0.5, 0.0, 0.5]:
    body.append(f'<line x1="{X(rv):.1f}" y1="{PB}" x2="{X(rv):.1f}" '
                f'y2="{PB+8}" stroke="{GRAY}" stroke-width="1.6"/>')
    body.append(f'<text x="{X(rv):.1f}" y="{PB+30}" font-family="{FONT}" '
                f'font-size="18" fill="{INK}" text-anchor="middle">'
                f'{rv:+.1f}</text>')
# y ticks
for sv in [0.0, 0.1, 0.2, 0.3, 0.4, 0.5]:
    body.append(f'<line x1="{PL-8}" y1="{Y(sv):.1f}" x2="{PL}" '
                f'y2="{Y(sv):.1f}" stroke="{GRAY}" stroke-width="1.6"/>')
    body.append(f'<text x="{PL-14}" y="{Y(sv)+6:.1f}" font-family="{FONT}" '
                f'font-size="18" fill="{INK}" text-anchor="end">{sv:.1f}</text>')

# axis titles (with measurement recipe)
body.append(f'<text x="{(PL+PR)/2:.0f}" y="{PB+64}" font-family="{FONT}" '
            f'font-size="20" fill="{INK}" text-anchor="middle" '
            f'font-weight="bold">round-1 agreement &#961;  '
            f'<tspan font-weight="normal" fill="{GRAY}">= correlation of judge '
            f'scores with candidate value scores '
            f'(&#8722;1 disagree &#8594; +1 lockstep)</tspan></text>')
body.append(f'<text x="46" y="{(PT+PB)/2:.0f}" font-family="{FONT}" '
            f'font-size="20" fill="{INK}" text-anchor="middle" '
            f'font-weight="bold" transform="rotate(-90 46 {(PT+PB)/2:.0f})">'
            f'round-1 spread &#963;  <tspan font-weight="normal" '
            f'fill="{GRAY}">= within-prompt SD of value scores</tspan></text>')

# ---- dots -------------------------------------------------------------------
# uniform size; draw near-zero (gray) dots first so the saturated movers sit on top
for r in sorted(RUNS, key=lambda z: abs(z["move"])):
    cx, cy = X(r["rho"]), Y(r["spread"])
    body.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{DOT_R:.1f}" '
                f'fill="{move_color(r["move"])}" fill-opacity="0.9" '
                f'stroke="white" stroke-width="1.6"/>')

# ---- legend (right of plot, slim continuous colorbar) -----------------------
LX = PR + 46
LY = PT + 14
body.append(f'<text x="{LX}" y="{LY}" font-family="{FONT}" font-size="18" '
            f'font-weight="bold" fill="{INK}">Endpoint move of</text>')
body.append(f'<text x="{LX}" y="{LY+23}" font-family="{FONT}" font-size="18" '
            f'font-weight="bold" fill="{INK}">the behavioral value</text>')
body.append(f'<text x="{LX}" y="{LY+45}" font-family="{FONT}" font-size="14.5" '
            f'fill="{GRAY}">(last value+drift) &#8722; round-1 value</text>')

# diverging color bar (top = +CAP up/red, bottom = -CAP down/blue, mid gray)
bar_x, bar_y, bar_w, bar_h = LX, LY + 66, 24, 240
seg = 60
for i in range(seg):
    t = i / (seg - 1)                       # 0 = top -> 1 = bottom
    mv = CAP - 2 * CAP * t                  # +CAP at top -> -CAP at bottom
    yy = bar_y + bar_h * t
    body.append(f'<rect x="{bar_x}" y="{yy:.1f}" width="{bar_w}" '
                f'height="{bar_h/seg + 1:.1f}" fill="{move_color(mv)}" '
                f'stroke="none"/>')
body.append(f'<rect x="{bar_x}" y="{bar_y}" width="{bar_w}" height="{bar_h}" '
            f'fill="none" stroke="{GRAY}" stroke-width="1.2"/>')
for frac, lab in [(0.0, "+0.6  moved up"), (0.5, "0  no net move"),
                  (1.0, "&#8722;0.6  moved down")]:
    yy = bar_y + bar_h * frac
    body.append(f'<text x="{bar_x+bar_w+10}" y="{yy+6:.1f}" '
                f'font-family="{FONT}" font-size="16" fill="{INK}">{lab}</text>')
# dead-band bracket: |move| < 0.15 renders as flat gray
db_top = bar_y + bar_h * (0.5 - DEAD / (2 * CAP))
db_bot = bar_y + bar_h * (0.5 + DEAD / (2 * CAP))
body.append(f'<line x1="{bar_x-9}" y1="{db_top:.1f}" x2="{bar_x-9}" '
            f'y2="{db_bot:.1f}" stroke="{GRAY}" stroke-width="2"/>')
body.append(f'<text x="{bar_x-13}" y="{(db_top+db_bot)/2+5:.1f}" '
            f'font-family="{FONT}" font-size="13" fill="{GRAY}" '
            f'text-anchor="end">|move|</text>')
body.append(f'<text x="{bar_x-13}" y="{(db_top+db_bot)/2+21:.1f}" '
            f'font-family="{FONT}" font-size="13" fill="{GRAY}" '
            f'text-anchor="end">&lt; 0.15</text>')

# ---- footnote (excluded runs + source) --------------------------------------
foot = ["7 of the 74 runs have an undefined round-1 &#961; and cannot be placed "
        "on these two axes (3 zero-spread pools, 4 random-selection controls); "
        f"{len(RUNS)} runs plotted.",
        "Source: experiments/spread_util_unified.json &#8212; round-1 record "
        "per run key cond|seed|source."]
for i, fl in enumerate(foot):
    body.append(f'<text x="{PL}" y="{H-40 + i*22}" font-family="{FONT}" '
                f'font-size="14.5" fill="{GRAY}">{fl}</text>')

svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
       f'font-family="{FONT}">\n<rect width="{W}" height="{H}" fill="white"/>\n'
       + "\n".join(body) + "\n</svg>\n")

with open(os.path.join(HERE, "synthesis-dial-plane.svg"), "w") as f:
    f.write(svg)
print(f"wrote synthesis-dial-plane.svg  ({len(RUNS)} runs plotted: "
      f"{N_UP} up / {N_DOWN} down / {N_FLAT} flat; "
      f"{N_SKIP} skipped, {N_RUNS} total)")
