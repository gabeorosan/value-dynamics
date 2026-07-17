#!/usr/bin/env python3
"""Synthesis candidate A (round-1 variant): the (agreement rho, spread sigma)
plane with the model's forecast painted as the background — and, unlike the
whole-run sibling figure, the DOTS made into one-round objects too so the two
layers carry literally identical units.

Every modelable run is placed at its round-1 dials. DOT color encodes the run's
OBSERVED FIRST one-round move of the behavioral value — round-2 value minus
round-1 value (the repo's consecutive-round transition convention: next round's
value minus this round's; equal to the round-1 `drift` field). The BACKGROUND is
painted, on the SAME color scale and now the SAME units, by the committed
recurrence's one-round selection forecast at that point of the plane:
predicted one-round move = rho * sigma (positive -> value climbs, negative ->
falls; magnitude = per-round step size). Where the background says "up" the
observed first move should be red, where it says "down" it should be blue -- so a
dot whose color matches the gradient behind it is the one-round law holding, and a
color clash is it failing. Because both layers are the same one-round quantity,
color agreement is a literal test of the law, not an analogy.

Trade-off made explicit: this figure no longer shows where a run ENDED (its
compounded net move over all rounds) — that lives in the rollout figures. The
gain is an exact unit match: the shared red/gray/blue scale is recalibrated to
the one-round range (first moves mostly within +-0.35), so background darkness and
dot darkness mean the same number.

Reads experiments/spread_util_unified.json (records list). One run = the tuple
(cond, seed, source); records sorted by round are its rounds in order. Round-1
supplies rho, spread, value; the first one-round move = round-2 value minus
round-1 value. Runs whose round-1 rho is null (zero within-pool spread makes the
correlation undefined) are not plottable on these two axes; runs with no round 2
would have no measurable first move — both are skipped, and the count is printed.

Style reference: docs/figures/src/make_figures.py (INK/BLUE/GREEN/RED/GRAY,
esc()/wrap()). Stdlib only. Run from this directory:
    python3 synthesis-dial-plane-round1.py
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


CAP = 0.35    # move at which the color saturates -- recalibrated to the
#               ONE-round range shared by both layers (first moves mostly
#               within +-0.35; the forecast rho*sigma tops out near +-0.40).
MID = "#e9e9e4"   # pale neutral midpoint so mid-strength moves read as mid-colors


def move_color(move):
    """Truly continuous diverging color: pale neutral at 0, linearly toward
    blue (down) or red (up), saturating at |move| = CAP. A light midpoint
    makes the lightness track |move|, so in-between moves are visibly
    in-between. Used for BOTH the dot fills (observed FIRST one-round move) and
    the background cells (the model's forecast one-round move rho*sigma) -- same
    units, same scale."""
    t = min(abs(move) / CAP, 1.0)
    pole = BLUE if move < 0 else RED
    return lerp(MID, pole, t)


DOT_R = 10.0   # uniform dot radius (no size encoding)
BG_ALPHA = 0.62   # background-cell opacity so dots stay legible on top


# ---- load & reduce to one point per run ------------------------------------
def load_runs():
    d = json.load(open(DATA))
    from collections import defaultdict
    runs = defaultdict(list)
    for r in d["records"]:
        runs[(r["cond"], r["seed"], r["source"])].append(r)
    plot, skipped_rho, skipped_move = [], 0, 0
    for key, rs in runs.items():
        rs = sorted(rs, key=lambda x: x["round"])
        r1 = [x for x in rs if x["round"] == 1][0]
        if r1.get("rho") is None:
            skipped_rho += 1
            continue
        # observed FIRST one-round move: round-2 value minus round-1 value
        # (repo convention for a consecutive-round transition; identical to the
        # round-1 `drift` field). If there is no round 2, use the logged drift;
        # if neither exists the first move is unmeasurable and the run is skipped.
        r2 = [x for x in rs if x["round"] == 2]
        if r2:
            move = r2[0]["value"] - r1["value"]
        elif r1.get("drift") is not None:
            move = r1["drift"]
        else:
            skipped_move += 1
            continue
        plot.append(dict(cond=r1["cond"], seed=key[1], src=r1["source"],
                         rho=r1["rho"], spread=r1["spread"],
                         value=r1["value"], move=move))
    return d, plot, len(runs), skipped_rho, skipped_move


DATA_D, RUNS, N_RUNS, N_SKIP_RHO, N_SKIP_MOVE = load_runs()
N_SKIP = N_SKIP_RHO + N_SKIP_MOVE
assert N_RUNS == 74, N_RUNS
assert len(RUNS) == 67, len(RUNS)
assert N_SKIP_RHO == 7, N_SKIP_RHO
assert N_SKIP_MOVE == 0, N_SKIP_MOVE   # every modelable run also has a first move
assert len(RUNS) + N_SKIP == N_RUNS

THRESH = 0.10  # descriptive threshold for one-round moves (smaller than the
#                whole-run figure's 0.15 because one round is a smaller step)
N_UP = sum(1 for r in RUNS if r["move"] >= THRESH)
N_DOWN = sum(1 for r in RUNS if r["move"] <= -THRESH)
N_FLAT = sum(1 for r in RUNS if abs(r["move"]) < THRESH)
assert N_UP + N_DOWN + N_FLAT == len(RUNS)

# sign concordance: of the runs whose first move cleared the threshold, how many
# sit on a background cell of the matching color?  background sign =
# sign(rho*sigma) = sign(rho) since sigma>0.
MOVERS = [r for r in RUNS if abs(r["move"]) >= THRESH and r["rho"] != 0.0]
N_CONCORD = sum(1 for r in MOVERS if (r["move"] > 0) == (r["rho"] > 0))
N_MOVERS = len(MOVERS)

# ---- geometry ---------------------------------------------------------------
W, H = 1440, 820
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
title = ("Background = the model's forecast one-round move ρ·σ; each dot = the "
         "run's observed first-round move — same units, same scale")
for i, ln in enumerate(wrap(title, 66)):
    body.append(f'<text x="{PL}" y="{58 + i*38}" font-family="{FONT}" '
                f'font-size="30" font-weight="bold" fill="{INK}">'
                f'{esc(ln)}</text>')
sub1 = (f"one dot per run · {len(RUNS)} modelable runs from "
        f"experiments/spread_util_unified.json (round-1 dials, round-1→2 move)")
body.append(f'<text x="{PL}" y="172" font-family="{FONT}" '
            f'font-size="20" fill="{GRAY}">{esc(sub1)}</text>')
sub2 = ("Both layers are the SAME one-round object, so color agreement is a "
        "literal test of the one-round law ρ·σ — not an analogy. Where a dot's "
        "color matches the gradient behind it, the forecast held.")
for i, ln in enumerate(wrap(sub2, 92)):
    body.append(f'<text x="{PL}" y="{198 + i*24}" font-family="{FONT}" '
                f'font-size="17" fill="{INK}">{esc(ln)}</text>')

# ---- background: model forecast rho*sigma, painted cell by cell --------------
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
        col = move_color(rho * sig)
        # +0.6px overscan avoids hairline seams between cells
        body.append(f'<rect x="{px0:.1f}" y="{py0:.1f}" '
                    f'width="{cw+0.6:.2f}" height="{ch+0.6:.2f}" fill="{col}"/>')
body.append('</g>')

# ---- iso-contours of the forecast rho*sigma ---------------------------------
# sigma = c / rho ; sigma>0 forces rho>0 for c>0, rho<0 for c<0.
def contour_polyline(c):
    if c > 0:
        rlo, rhi = c / SIG1, RHO1
    else:
        rlo, rhi = RHO0, c / SIG1
    if not rlo < rhi:
        return []
    pts = []
    n = 80
    for k in range(n + 1):
        rho = rlo + (rhi - rlo) * k / n
        if abs(rho) < 1e-9:
            continue
        sig = c / rho
        if SIG0 - 1e-9 <= sig <= SIG1 + 1e-9:
            pts.append((X(rho), Y(min(max(sig, SIG0), SIG1))))
    return pts


CONTOURS = [(-0.10, 0.115), (-0.05, 0.155), (0.05, 0.155), (0.10, 0.115)]
for c, sig_t in CONTOURS:
    pts = contour_polyline(c)
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
    rho_t = c / sig_t
    if not (RHO0 <= rho_t <= RHO1):
        continue
    halo_label(X(rho_t), Y(sig_t), f"ρσ = {c:+.2f}")
# the vertical zero line label
halo_label(X(0), PT - 14, "ρσ = 0", size=14.5)

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
            f'fill="{move_color(0.28)}" stroke="#3f454c" stroke-width="1.1"/>')
for i, ln in enumerate(wrap("Dot fill = the run's OBSERVED first one-round move "
                            "(round-2 value − round-1 value)", 40)):
    body.append(f'<text x="{LX+34}" y="{dyc + i*20:.0f}" font-family="{FONT}" '
                f'font-size="15.5" fill="{INK}">{esc(ln)}</text>')

# role 2: the background
byc = dyc + 56
body.append(f'<rect x="{LX+3:.1f}" y="{byc-17:.1f}" width="22" height="22" '
            f'rx="2" fill="{move_color(0.28)}" fill-opacity="{BG_ALPHA}" '
            f'stroke="{GRAY}" stroke-width="0.8"/>')
for i, ln in enumerate(wrap("Background = the model's FORECAST one-round move "
                            "= agreement ρ × spread σ", 40)):
    body.append(f'<text x="{LX+34}" y="{byc + i*20:.0f}" font-family="{FONT}" '
                f'font-size="15.5" fill="{INK}">{esc(ln)}</text>')

# the shared diverging bar (red -> mid -> blue), exact match to move_color
bar_x = LX + 6
bar_y = byc + 66
bar_w, bar_h = 26, 170
body.append(f'<defs><linearGradient id="movebar" x1="0" y1="0" x2="0" y2="1">'
            f'<stop offset="0" stop-color="{RED}"/>'
            f'<stop offset="0.5" stop-color="{MID}"/>'
            f'<stop offset="1" stop-color="{BLUE}"/>'
            f'</linearGradient></defs>')
body.append(f'<rect x="{bar_x}" y="{bar_y}" width="{bar_w}" height="{bar_h}" '
            f'fill="url(#movebar)"/>')
body.append(f'<rect x="{bar_x}" y="{bar_y}" width="{bar_w}" height="{bar_h}" '
            f'fill="none" stroke="{GRAY}" stroke-width="1.2"/>')
for frac, lab in [(0.0, "+0.35  value climbs"), (0.5, "0  no move"),
                  (1.0, "−0.35  value falls")]:
    yy = bar_y + bar_h * frac
    body.append(f'<line x1="{bar_x+bar_w}" y1="{yy:.1f}" x2="{bar_x+bar_w+6}" '
                f'y2="{yy:.1f}" stroke="{GRAY}" stroke-width="1.2"/>')
    body.append(f'<text x="{bar_x+bar_w+11}" y="{yy+5:.1f}" '
                f'font-family="{FONT}" font-size="15" fill="{INK}">{esc(lab)}</text>')
body.append(f'<text x="{bar_x}" y="{bar_y+bar_h+22}" font-family="{FONT}" '
            f'font-size="13.5" fill="{GRAY}">one scale, one unit for both;</text>')
body.append(f'<text x="{bar_x}" y="{bar_y+bar_h+38}" font-family="{FONT}" '
            f'font-size="13.5" fill="{GRAY}">a per-round move; saturates at '
            f'|move| = 0.35.</text>')

# ---- concordance readout box ------------------------------------------------
box_x, box_y, box_w = LX, bar_y + bar_h + 50, 470
box_h = 150
body.append(f'<rect x="{box_x}" y="{box_y}" width="{box_w}" height="{box_h}" '
            f'rx="6" fill="{KEY_FILL}" stroke="{GREEN}" stroke-width="1.4"/>')
body.append(f'<text x="{box_x+14}" y="{box_y+25}" font-family="{FONT}" '
            f'font-size="16" font-weight="bold" fill="{INK}">Does dot color '
            f'match the background?</text>')
read = (f"{N_CONCORD} of the {N_MOVERS} runs whose first move cleared ±0.10 sit "
        f"on a background of the matching color — i.e. the sign of the observed "
        f"first-round move equals the sign of the forecast ρ·σ. "
        f"(threshold: |first move| ≥ 0.10; {N_SKIP} of {N_RUNS} runs unplotted "
        f"— round-1 ρ undefined.)")
for i, ln in enumerate(wrap(read, 58)):
    body.append(f'<text x="{box_x+14}" y="{box_y+47 + i*18}" '
                f'font-family="{FONT}" font-size="14.5" fill="{INK}">'
                f'{esc(ln)}</text>')

svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
       f'font-family="{FONT}">\n<rect width="{W}" height="{H}" fill="white"/>\n'
       + "\n".join(body) + "\n</svg>\n")

with open(os.path.join(HERE, "synthesis-dial-plane-round1.svg"), "w") as f:
    f.write(svg)
print(f"wrote synthesis-dial-plane-round1.svg  ({len(RUNS)} runs plotted: "
      f"{N_UP} up / {N_DOWN} down / {N_FLAT} flat @±{THRESH}; "
      f"{N_SKIP} skipped ({N_SKIP_RHO} ρ-undefined, {N_SKIP_MOVE} no-first-move), "
      f"{N_RUNS} total; sign concordance {N_CONCORD}/{N_MOVERS} movers)")
