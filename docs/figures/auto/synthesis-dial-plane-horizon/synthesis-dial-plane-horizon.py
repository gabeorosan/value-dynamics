#!/usr/bin/env python3
"""Synthesis candidate: the (agreement rho, spread sigma) plane, with the
model's forecast painted as the background -- now COMPOUNDED to run scale so the
background and the dots share units.

Every modelable run placed at its round-1 dials; DOT color encodes the run's
observed net WHOLE-RUN endpoint move of the behavioral value, on a continuous
red(up)-gray(none)-blue(down) diverging scale. The BACKGROUND is painted, on the
SAME color scale, by the committed recurrence's forecast ENDPOINT move over the
corpus-typical horizon:

    Delta_v_pred(R) = clip to [-1, +1] of ( R * rho * sigma ),   R = 4 rounds.

Two facts the recurrence gives us are stated on the figure itself: (1) the
self-only recurrence compounds ONE selection step rho*sigma per round, so R
rounds accumulate R*rho*sigma; (2) the value walls cap the total, which the
clip to [-1, +1] represents. R = 4 is the MODAL run length. So a dot whose color
matches the gradient behind it is the model's 4-round forecast holding, and a
color clash is the forecast failing -- and now both sides are measured in the
same whole-run endpoint units, not a one-round force against a compounded move.

Honesty scope kept explicit: the 9 judge-schedule runs actually ran 8 rounds,
and the mixed-pool runs also feel the outside-source pull (p - q), so the 4*rho*
sigma background is the SELF-ONLY, 4-round force map, not each run's exact
per-run forecast. Only sign and relative magnitude are strictly comparable; the
background is drawn at reduced opacity.

Reads experiments/spread_util_unified.json (records list). One run = the tuple
(cond, seed, source); the round-1 record supplies rho, spread, value; the last
record supplies value+drift. Runs whose round-1 rho is null (zero within-pool
spread makes the correlation undefined) are not plottable on these two axes.

Style reference: docs/figures/src/make_figures.py (INK/BLUE/GREEN/RED/GRAY,
esc()/wrap()). Stdlib only. Run from this directory:
    python3 synthesis-dial-plane-horizon.py
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


# ---- color helpers (continuous diverging scale) -----------------------------
def _hex2rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def _rgb2hex(rgb):
    return "#%02x%02x%02x" % tuple(max(0, min(255, int(round(c)))) for c in rgb)


def lerp(c1, c2, t):
    a, b = _hex2rgb(c1), _hex2rgb(c2)
    return _rgb2hex([a[i] + (b[i] - a[i]) * t for i in range(3)])


CAP = 0.60    # move at which the color saturates (the observed endpoint range)
MID = "#e9e9e4"   # pale neutral midpoint so mid-strength moves read as mid-colors


def move_color(move):
    """Truly continuous diverging color: pale neutral at 0, linearly toward
    blue (down) or red (up), saturating at |move| = CAP. A light midpoint
    makes the lightness track |move|, so in-between moves are visibly
    in-between. Used for BOTH the dot fills (observed WHOLE-RUN endpoint move)
    and the background cells (the model's compounded 4-round forecast move)."""
    t = min(abs(move) / CAP, 1.0)
    pole = BLUE if move < 0 else RED
    return lerp(MID, pole, t)


R_HORIZON = 4     # modal run length (rounds) -- the corpus-typical horizon
V_WALL = 1.0      # value-scale wall: the compounded move is capped at +/- 1


def bg_move(rho, sig):
    """The model's forecast ENDPOINT move over R rounds: compound one selection
    step rho*sigma per round, then cap at the value wall +/- 1."""
    return max(-V_WALL, min(V_WALL, R_HORIZON * rho * sig))


DOT_R = 10.0   # uniform dot radius (no size encoding)
BG_ALPHA = 0.62   # background-cell opacity so dots stay legible on top


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

THRESH = 0.15  # descriptive threshold for the caption counts only
N_UP = sum(1 for r in RUNS if r["move"] >= THRESH)
N_DOWN = sum(1 for r in RUNS if r["move"] <= -THRESH)
N_FLAT = sum(1 for r in RUNS if abs(r["move"]) < THRESH)
assert N_UP + N_DOWN + N_FLAT == len(RUNS)

# sign concordance: of the runs that moved, how many sit on a background cell of
# the matching color?  The compounding factor R (> 0) and the wall cap do NOT
# change the SIGN of the forecast, so sign(bg_move) = sign(rho*sigma) = sign(rho)
# since sigma > 0 -- the concordance count is identical to the one-round version.
MOVERS = [r for r in RUNS if abs(r["move"]) >= THRESH and r["rho"] != 0.0]
N_CONCORD = sum(1 for r in MOVERS if (r["move"] > 0) == (r["rho"] > 0))
N_MOVERS = len(MOVERS)
# the x4 horizon leaves the sign untouched, so this MUST match the one-round map
assert N_MOVERS == 50, N_MOVERS
assert N_CONCORD == 39, N_CONCORD

# ---- geometry ---------------------------------------------------------------
W, H = 1440, 880
PL, PR = 150, 900           # plot left / right (px)
PT, PB = 250, 700           # plot top / bottom (px)
RHO0, RHO1 = -1.08, 0.95    # x data domain
SIG0, SIG1 = 0.0, 0.50      # y data domain


def X(rho):
    return PL + (rho - RHO0) / (RHO1 - RHO0) * (PR - PL)


def Y(sig):
    return PB - (sig - SIG0) / (SIG1 - SIG0) * (PB - PT)


def px2rho(px):
    return RHO0 + (px - PL) / (PR - PL) * (RHO1 - RHO0)


def px2sig(py):
    return SIG0 + (PB - py) / (PB - PT) * (SIG1 - SIG0)


# ============================================================================
body = []

# ---- title / subtitle (headline finding + honesty line) ---------------------
title = ("Background = the model's forecast 4-round move (one selection step "
         "ρ·σ per round, wall-capped); each dot = the run's observed whole-run "
         "move — same units")
for i, ln in enumerate(wrap(title, 66)):
    body.append(f'<text x="{PL}" y="{58 + i*38}" font-family="{FONT}" '
                f'font-size="30" font-weight="bold" fill="{INK}">'
                f'{esc(ln)}</text>')
sub1 = (f"one dot per run · {len(RUNS)} modelable runs from "
        f"experiments/spread_util_unified.json (round-1 record per run)")
body.append(f'<text x="{PL}" y="174" font-family="{FONT}" '
            f'font-size="20" fill="{GRAY}">{esc(sub1)}</text>')
sub2 = ("Background = Δv_pred(4) = clip[−1,+1] of 4·ρ·σ — one selection step "
        "ρσ per round, wall-capped — on the dots' own endpoint-move color scale.")
for i, ln in enumerate(wrap(sub2, 96)):
    body.append(f'<text x="{PL}" y="{200 + i*24}" font-family="{FONT}" '
                f'font-size="17" fill="{INK}">{esc(ln)}</text>')

# ---- background: model's compounded 4-round forecast, painted cell by cell ---
NX, NY = 60, 40
cw = (PR - PL) / NX
ch = (PB - PT) / NY
body.append(f'<g opacity="{BG_ALPHA}">')
for j in range(NY):
    py0 = PT + j * ch
    sig = px2sig(py0 + ch / 2)
    for i in range(NX):
        px0 = PL + i * cw
        rho = px2rho(px0 + cw / 2)
        col = move_color(bg_move(rho, sig))
        # +0.6px overscan avoids hairline seams between cells
        body.append(f'<rect x="{px0:.1f}" y="{py0:.1f}" '
                    f'width="{cw+0.6:.2f}" height="{ch+0.6:.2f}" fill="{col}"/>')
body.append('</g>')

# ---- iso-contours of the forecast endpoint move Delta_v = 4*rho*sigma --------
# level c on Delta_v means 4*rho*sigma = c, i.e. rho*sigma = c/4.
# sigma = (c/4) / rho ; sigma>0 forces rho>0 for c>0, rho<0 for c<0.
def contour_polyline(k):   # k is the rho*sigma product level = c/4
    if k > 0:
        rlo, rhi = k / SIG1, RHO1
    else:
        rlo, rhi = RHO0, k / SIG1
    if not rlo < rhi:
        return []
    pts = []
    n = 80
    for i in range(n + 1):
        rho = rlo + (rhi - rlo) * i / n
        if abs(rho) < 1e-9:
            continue
        sig = k / rho
        if SIG0 - 1e-9 <= sig <= SIG1 + 1e-9:
            pts.append((X(rho), Y(min(max(sig, SIG0), SIG1))))
    return pts


# each entry: (Delta_v level c, sigma at which to place the label)
CONTOURS = [(-0.40, 0.115), (-0.20, 0.155), (0.20, 0.155), (0.40, 0.115)]
for c, sig_t in CONTOURS:
    pts = contour_polyline(c / 4.0)
    if not pts:
        continue
    dstr = " ".join(f"{'M' if i == 0 else 'L'}{x:.1f},{y:.1f}"
                    for i, (x, y) in enumerate(pts))
    body.append(f'<path d="{dstr}" fill="none" stroke="#4d4d4d" '
                f'stroke-width="1.1" stroke-opacity="0.5" '
                f'stroke-dasharray="5 4"/>')

# ---- plot frame + rho=0 (which is also the forecast = 0 contour) -------------
body.append(f'<rect x="{PL}" y="{PT}" width="{PR-PL}" height="{PB-PT}" '
            f'fill="none" stroke="{GRAY}" stroke-width="1.6"/>')
body.append(f'<line x1="{X(0):.1f}" y1="{PT}" x2="{X(0):.1f}" y2="{PB}" '
            f'stroke="#3d3d3d" stroke-width="1.3" stroke-opacity="0.6"/>')

# ---- contour labels (white halo so they read over any background) -----------
def halo_label(cx, cy, text, size=14.5, weight="normal", anchor="middle"):
    w_px = len(text) * size * 0.56
    body.append(f'<rect x="{cx - w_px/2 - 4:.1f}" y="{cy - size*0.82:.1f}" '
                f'width="{w_px + 8:.1f}" height="{size*1.25:.1f}" rx="3" '
                f'fill="white" fill-opacity="0.86"/>')
    body.append(f'<text x="{cx:.1f}" y="{cy + size*0.34:.1f}" '
                f'font-family="{FONT}" font-size="{size}" fill="#333" '
                f'font-weight="{weight}" text-anchor="{anchor}">'
                f'{esc(text)}</text>')


for c, sig_t in CONTOURS:
    rho_t = (c / 4.0) / sig_t
    if not (RHO0 <= rho_t <= RHO1):
        continue
    halo_label(X(rho_t), Y(sig_t), f"Δv(4) = {c:+.2f}")
# the vertical zero line label
halo_label(X(0), PT - 14, "Δv = 0", size=14.5)

# ---- axis ticks -------------------------------------------------------------
for rv in [-1.0, -0.5, 0.0, 0.5]:
    body.append(f'<line x1="{X(rv):.1f}" y1="{PB}" x2="{X(rv):.1f}" '
                f'y2="{PB+8}" stroke="{GRAY}" stroke-width="1.6"/>')
    body.append(f'<text x="{X(rv):.1f}" y="{PB+30}" font-family="{FONT}" '
                f'font-size="18" fill="{INK}" text-anchor="middle">'
                f'{rv:+.1f}</text>')
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
            f'scores with candidate value scores</tspan></text>')
body.append(f'<text x="{(PL+PR)/2:.0f}" y="{PB+88}" font-family="{FONT}" '
            f'font-size="18" fill="{GRAY}" text-anchor="middle">'
            f'(&#8722;1 disagree &#8594; +1 lockstep)</text>')
body.append(f'<text x="46" y="{(PT+PB)/2:.0f}" font-family="{FONT}" '
            f'font-size="20" fill="{INK}" text-anchor="middle" '
            f'font-weight="bold" transform="rotate(-90 46 {(PT+PB)/2:.0f})">'
            f'round-1 spread &#963;  <tspan font-weight="normal" '
            f'fill="{GRAY}">= within-prompt SD of value scores</tspan></text>')

# ---- dots (drawn on top; white halo + thin dark edge for legibility) --------
# near-zero (gray) dots first so the saturated movers sit on top
for r in sorted(RUNS, key=lambda z: abs(z["move"])):
    cx, cy = X(r["rho"]), Y(r["spread"])
    body.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{DOT_R+1.4:.1f}" '
                f'fill="none" stroke="white" stroke-width="2.6" '
                f'stroke-opacity="0.9"/>')
    body.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{DOT_R:.1f}" '
                f'fill="{move_color(r["move"])}" '
                f'stroke="#3f454c" stroke-width="1.1"/>')

# ---- shared color key -------------------------------------------------------
LX = PR + 56
LY = 250
body.append(f'<text x="{LX}" y="{LY}" font-family="{FONT}" font-size="20" '
            f'font-weight="bold" fill="{INK}">One color scale, two roles</text>')

# role 1: the dot
dyc = LY + 30
body.append(f'<circle cx="{LX+13:.1f}" cy="{dyc-5:.1f}" r="{DOT_R+1.4:.1f}" '
            f'fill="none" stroke="white" stroke-width="2.6"/>')
body.append(f'<circle cx="{LX+13:.1f}" cy="{dyc-5:.1f}" r="{DOT_R:.1f}" '
            f'fill="{move_color(0.45)}" stroke="#3f454c" stroke-width="1.1"/>')
for i, ln in enumerate(wrap("Dot fill = the run's OBSERVED whole-run endpoint "
                            "move (final measured value − round-1 value)", 40)):
    body.append(f'<text x="{LX+34}" y="{dyc + i*20:.0f}" font-family="{FONT}" '
                f'font-size="15.5" fill="{INK}">{esc(ln)}</text>')

# role 2: the background
byc = dyc + 76
body.append(f'<rect x="{LX+3:.1f}" y="{byc-17:.1f}" width="22" height="22" '
            f'rx="2" fill="{move_color(0.45)}" fill-opacity="{BG_ALPHA}" '
            f'stroke="{GRAY}" stroke-width="0.8"/>')
for i, ln in enumerate(wrap("Background = the model's FORECAST 4-round endpoint "
                            "move = clip[−1,+1] of 4 · ρ · σ (one selection "
                            "step ρσ per round, wall-capped)", 40)):
    body.append(f'<text x="{LX+34}" y="{byc + i*20:.0f}" font-family="{FONT}" '
                f'font-size="15.5" fill="{INK}">{esc(ln)}</text>')

# the shared diverging bar (red -> mid -> blue), exact match to move_color
bar_x = LX + 6
bar_y = byc + 96
bar_w, bar_h = 26, 150
body.append(f'<defs><linearGradient id="movebar" x1="0" y1="0" x2="0" y2="1">'
            f'<stop offset="0" stop-color="{RED}"/>'
            f'<stop offset="0.5" stop-color="{MID}"/>'
            f'<stop offset="1" stop-color="{BLUE}"/>'
            f'</linearGradient></defs>')
body.append(f'<rect x="{bar_x}" y="{bar_y}" width="{bar_w}" height="{bar_h}" '
            f'fill="url(#movebar)"/>')
body.append(f'<rect x="{bar_x}" y="{bar_y}" width="{bar_w}" height="{bar_h}" '
            f'fill="none" stroke="{GRAY}" stroke-width="1.2"/>')
for frac, lab in [(0.0, "+0.6  value climbs"), (0.5, "0  no move"),
                  (1.0, "−0.6  value falls")]:
    yy = bar_y + bar_h * frac
    body.append(f'<line x1="{bar_x+bar_w}" y1="{yy:.1f}" x2="{bar_x+bar_w+6}" '
                f'y2="{yy:.1f}" stroke="{GRAY}" stroke-width="1.2"/>')
    body.append(f'<text x="{bar_x+bar_w+11}" y="{yy+5:.1f}" '
                f'font-family="{FONT}" font-size="15" fill="{INK}">{esc(lab)}</text>')
body.append(f'<text x="{bar_x}" y="{bar_y+bar_h+22}" font-family="{FONT}" '
            f'font-size="13.5" fill="{GRAY}">same red/gray/blue endpoint-move</text>')
body.append(f'<text x="{bar_x}" y="{bar_y+bar_h+38}" font-family="{FONT}" '
            f'font-size="13.5" fill="{GRAY}">scale for BOTH; color saturates at '
            f'±0.6.</text>')

# ---- concordance readout box ------------------------------------------------
box_x, box_y, box_w = LX, bar_y + bar_h + 52, 470
box_h = 118
body.append(f'<rect x="{box_x}" y="{box_y}" width="{box_w}" height="{box_h}" '
            f'rx="6" fill="{KEY_FILL}" stroke="{GREEN}" stroke-width="1.4"/>')
body.append(f'<text x="{box_x+14}" y="{box_y+25}" font-family="{FONT}" '
            f'font-size="16" font-weight="bold" fill="{INK}">Does dot color '
            f'match the background?</text>')
read = (f"{N_CONCORD} of the {N_MOVERS} runs that moved ≥ 0.15 sit on a "
        f"background of the matching color — the sign of the observed move "
        f"equals the sign of 4·ρ·σ. (The ×4 horizon and the wall leave the "
        f"sign untouched, so this count is identical to the one-round map.)")
for i, ln in enumerate(wrap(read, 58)):
    body.append(f'<text x="{box_x+14}" y="{box_y+47 + i*18}" '
                f'font-family="{FONT}" font-size="14.5" fill="{INK}">'
                f'{esc(ln)}</text>')

# ---- scope line (bottom, spanning under the plot) ---------------------------
scope = ("Scope: R = 4 is the MODAL run length. The 9 judge-schedule runs "
         "actually ran 8 rounds, and mixed-pool runs also feel the outside-"
         "source pull (p − q) — so this 4·ρσ background is the self-only, "
         "4-round force map, not each run's exact per-run forecast.")
for i, ln in enumerate(wrap(scope, 118)):
    body.append(f'<text x="{PL}" y="{PB+116 + i*22}" font-family="{FONT}" '
                f'font-size="15" fill="{GRAY}">{esc(ln)}</text>')

svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
       f'font-family="{FONT}">\n<rect width="{W}" height="{H}" fill="white"/>\n'
       + "\n".join(body) + "\n</svg>\n")

with open(os.path.join(HERE, "synthesis-dial-plane-horizon.svg"), "w") as f:
    f.write(svg)
print(f"wrote synthesis-dial-plane-horizon.svg  ({len(RUNS)} runs plotted: "
      f"{N_UP} up / {N_DOWN} down / {N_FLAT} flat; "
      f"{N_SKIP} skipped, {N_RUNS} total; "
      f"sign concordance {N_CONCORD}/{N_MOVERS} movers; R={R_HORIZON})")
