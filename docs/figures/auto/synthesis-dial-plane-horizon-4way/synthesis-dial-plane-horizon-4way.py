#!/usr/bin/env python3
"""Synthesis candidate, SPLIT FOUR WAYS (model family x value axis): the
(agreement rho, spread sigma) plane with the model's forecast painted as the
background, drawn once per (organism, value-axis) cell.

This is the 2x2 variant of synthesis-dial-plane-horizon. Same construction, four
panels laid on the same shared plane and shared color scale:

    row 0:  Qwen3-4B / risk-seeking      |  Qwen3-4B / insecure-code self-report
    row 1:  OLMo-3-7B / risk-seeking     |  OLMo-3-7B / insecure-code self-report

Each 4-round run is placed at its round-1 dials (agreement rho, spread sigma);
DOT color encodes the run's observed net WHOLE-RUN endpoint move of the
behavioral value on a continuous red(up)-gray(none)-blue(down) diverging scale.
The BACKGROUND of every panel is the identical painted forecast, on the SAME
color scale, of the committed recurrence's ENDPOINT move over the corpus-typical
horizon:

    Delta_v_pred(R) = clip to [-1, +1] of ( R * rho * sigma ),   R = 4 rounds.

So a dot whose color matches the gradient behind it is the model's 4-round
forecast holding, and a color clash is the forecast failing. Splitting four ways
asks whether that dial->direction story holds WITHIN each family-and-axis cell on
its own. One cell (OLMo / insecure-code self-report) has ZERO runs in the
modeling corpus; its panel is drawn honestly empty -- an empty cell is a finding.

Honesty scope kept explicit (once, in the shared subtitle): the 4*rho*sigma
background is the SELF-ONLY, 4-round force map; mixed-pool runs also feel the
outside-source pull (p - q). Only sign and relative magnitude are strictly
comparable; the background is drawn at reduced opacity. R = 4 is every plotted
run's exact horizon (the 8-round judge-schedule runs are excluded).

Reads experiments/spread_util_unified.json (records list). One run = the tuple
(cond, seed, source); the round-1 record supplies rho, spread, value AND the
"organism" field ("Qwen"/"OLMo") and the "axis" field ("risk"/"selfreport")
used to split the panels; the last record supplies value+drift. Runs whose
round-1 rho is null (zero within-pool spread makes the correlation undefined)
are not plottable on these two axes.

Style reference: docs/figures/src/make_figures.py (INK/BLUE/GREEN/RED/GRAY,
esc()/wrap()). Stdlib only. Run from this directory:
    python3 synthesis-dial-plane-horizon-4way.py
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
    blue (down) or red (up), saturating at |move| = CAP. Used for BOTH the dot
    fills (observed WHOLE-RUN endpoint move) and the background cells (the
    model's compounded 4-round forecast move)."""
    t = min(abs(move) / CAP, 1.0)
    pole = BLUE if move < 0 else RED
    return lerp(MID, pole, t)


R_HORIZON = 4     # modal run length (rounds) -- the corpus-typical horizon
V_WALL = 1.0      # value-scale wall: the compounded move is capped at +/- 1


def bg_move(rho, sig):
    """The model's forecast ENDPOINT move over R rounds: compound one selection
    step rho*sigma per round, then cap at the value wall +/- 1."""
    return max(-V_WALL, min(V_WALL, R_HORIZON * rho * sig))


DOT_R = 8.5    # uniform dot radius (no size encoding); shrunk for narrow panels
BG_ALPHA = 0.62   # background-cell opacity so dots stay legible on top


# ---- load & reduce to one point per run ------------------------------------
def load_runs():
    d = json.load(open(DATA))
    from collections import defaultdict
    runs = defaultdict(list)
    for r in d["records"]:
        runs[(r["cond"], r["seed"], r["source"])].append(r)
    plot, skipped, excluded_len = [], 0, 0
    for key, rs in runs.items():
        rs = sorted(rs, key=lambda x: x["round"])
        if len(rs) != R_HORIZON:      # 4-round runs only, so the x4 background
            excluded_len += 1         # is every run's exact horizon
            continue
        r1 = [x for x in rs if x["round"] == 1][0]
        if r1.get("rho") is None:
            skipped += 1
            continue
        last = rs[-1]
        move = (last["value"] + (last["drift"] or 0.0)) - r1["value"]
        plot.append(dict(cond=r1["cond"], seed=key[1], src=r1["source"],
                         org=r1["organism"], axis=r1["axis"],
                         rho=r1["rho"], spread=r1["spread"],
                         value=r1["value"], move=move))
    return d, plot, len(runs), skipped, excluded_len


DATA_D, RUNS, N_RUNS, N_SKIP, N_EXCL = load_runs()
assert N_RUNS == 74, N_RUNS
assert N_EXCL == 11, N_EXCL          # the 8-round judge-schedule runs
assert len(RUNS) == 56, len(RUNS)
assert N_SKIP == 7, N_SKIP

# split four ways on (organism, axis) -- both read straight off the round-1 record
assert all(r["org"] in ("Qwen", "OLMo") for r in RUNS)
assert all(r["axis"] in ("risk", "selfreport") for r in RUNS)


def cell(org, axis):
    return [r for r in RUNS if r["org"] == org and r["axis"] == axis]


# the four cells, in reading order
CELLS = {
    ("Qwen", "risk"): cell("Qwen", "risk"),
    ("Qwen", "selfreport"): cell("Qwen", "selfreport"),
    ("OLMo", "risk"): cell("OLMo", "risk"),
    ("OLMo", "selfreport"): cell("OLMo", "selfreport"),
}
COUNTS = {k: len(v) for k, v in CELLS.items()}
# recomputed counts asserted so data-file drift fails loudly
assert COUNTS[("Qwen", "risk")] == 12, COUNTS
assert COUNTS[("Qwen", "selfreport")] == 13, COUNTS
assert COUNTS[("OLMo", "risk")] == 31, COUNTS
assert COUNTS[("OLMo", "selfreport")] == 0, COUNTS
assert sum(COUNTS.values()) == 56, COUNTS   # must total the parent's plotted set

THRESH = 0.15  # descriptive threshold for the mover counts


def concord(sub):
    """Of the runs that moved >= 0.15, how many sit on a background cell of the
    matching color? sign(bg_move) = sign(rho) since sigma>0, and the x4 horizon +
    wall cap do NOT change that sign."""
    movers = [r for r in sub if abs(r["move"]) >= THRESH and r["rho"] != 0.0]
    n_c = sum(1 for r in movers if (r["move"] > 0) == (r["rho"] > 0))
    return n_c, len(movers)


CONC = {k: concord(v) for k, v in CELLS.items()}
assert CONC[("Qwen", "risk")] == (5, 5), CONC
assert CONC[("Qwen", "selfreport")] == (12, 12), CONC
assert CONC[("OLMo", "risk")] == (18, 24), CONC
assert CONC[("OLMo", "selfreport")] == (0, 0), CONC
# pooled movers/concord match the parent pooled figure
assert sum(m for _, m in CONC.values()) == 41
assert sum(c for c, _ in CONC.values()) == 35

# human-readable axis names
AXIS_NAME = {"risk": "risk-seeking",
             "selfreport": "insecure-code self-report"}
ORG_NAME = {"Qwen": "Qwen3-4B", "OLMo": "OLMo-3-7B"}

# ---- geometry ---------------------------------------------------------------
W, H = 1780, 1520
RHO0, RHO1 = -1.08, 0.95    # x data domain (shared)
SIG0, SIG1 = 0.0, 0.50      # y data domain (shared)

# 2x2 grid of plot panels; shared extents. (pl, pr) per column, (pt, pb) per row.
COLX = {0: (150, 620), 1: (700, 1170)}
ROWY = {0: (330, 740), 1: (940, 1350)}
# map (org, axis) -> (col, row)
GRID = {
    ("Qwen", "risk"): (0, 0),
    ("Qwen", "selfreport"): (1, 0),
    ("OLMo", "risk"): (0, 1),
    ("OLMo", "selfreport"): (1, 1),
}


def X(rho, pl, pr):
    return pl + (rho - RHO0) / (RHO1 - RHO0) * (pr - pl)


def Y(sig, pt, pb):
    return pb - (sig - SIG0) / (SIG1 - SIG0) * (pb - pt)


def px2rho(px, pl, pr):
    return RHO0 + (px - pl) / (pr - pl) * (RHO1 - RHO0)


def px2sig(py, pt, pb):
    return SIG0 + (pb - py) / (pb - pt) * (SIG1 - SIG0)


# ============================================================================
body = []
LEFT = COLX[0][0]   # left margin used by title & subtitle text

# ---- title / subtitle (headline finding + honesty line) ---------------------
title = ("The dial → direction plane, split four ways: does the same forecast "
         "hold within each model family AND each value axis on its own?")
for i, ln in enumerate(wrap(title, 96)):
    body.append(f'<text x="{LEFT}" y="{54 + i*36}" '
                f'font-family="{FONT}" font-size="28" font-weight="bold" '
                f'fill="{INK}">{esc(ln)}</text>')
sub1 = (f"one dot per run · {len(RUNS)} modelable runs from "
        f"experiments/spread_util_unified.json (round-1 record per run), split on "
        f"the record’s “organism” field (Qwen3-4B / OLMo-3-7B) and "
        f"“axis” field (risk-seeking / insecure-code self-report)")
for i, ln in enumerate(wrap(sub1, 130)):
    body.append(f'<text x="{LEFT}" y="{130 + i*22}" font-family="{FONT}" '
                f'font-size="18" fill="{GRAY}">{esc(ln)}</text>')
sub2 = ("Every panel shares the identical background = Δv_pred(4) = "
        "clip[−1,+1] of 4·ρ·σ (one selection step "
        "ρσ per round, wall-capped) — the self-only force map "
        "(mixed-pool runs also feel the outside-source pull p−q); painted "
        "on the dots’ own endpoint-move color scale.")
for i, ln in enumerate(wrap(sub2, 140)):
    body.append(f'<text x="{LEFT}" y="{198 + i*22}" font-family="{FONT}" '
                f'font-size="16.5" fill="{INK}">{esc(ln)}</text>')


# ---- iso-contour helper (shared geometry, drawn per panel) ------------------
def contour_polyline(k, pl, pr, pt, pb):   # k is the rho*sigma product level c/4
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
            pts.append((X(rho, pl, pr), Y(min(max(sig, SIG0), SIG1), pt, pb)))
    return pts


# each entry: (Delta_v level c, sigma at which to place the label)
CONTOURS = [(-0.40, 0.115), (-0.20, 0.155), (0.20, 0.155), (0.40, 0.115)]


def halo_label(cx, cy, text, size=13.0, weight="normal", anchor="middle"):
    w_px = len(text) * size * 0.56
    body.append(f'<rect x="{cx - w_px/2 - 4:.1f}" y="{cy - size*0.82:.1f}" '
                f'width="{w_px + 8:.1f}" height="{size*1.25:.1f}" rx="3" '
                f'fill="white" fill-opacity="0.86"/>')
    body.append(f'<text x="{cx:.1f}" y="{cy + size*0.34:.1f}" '
                f'font-family="{FONT}" font-size="{size}" fill="#333" '
                f'font-weight="{weight}" text-anchor="{anchor}">'
                f'{esc(text)}</text>')


# ---- draw one panel ---------------------------------------------------------
def draw_panel(org, axis):
    col, row = GRID[(org, axis)]
    pl, pr = COLX[col]
    pt, pb = ROWY[row]
    sub = CELLS[(org, axis)]
    n = COUNTS[(org, axis)]
    is_bottom = (row == 1)

    # panel title (with live count) + the cell's concordance line
    ptitle = f"{ORG_NAME[org]} · {AXIS_NAME[axis]}  ({n} runs)"
    body.append(f'<text x="{(pl+pr)/2:.0f}" y="{pt-40}" font-family="{FONT}" '
                f'font-size="21" font-weight="bold" fill="{INK}" '
                f'text-anchor="middle">{esc(ptitle)}</text>')
    if n > 0:
        c, m = CONC[(org, axis)]
        cline = (f"{c} of {m} movers concordant" if m
                 else "no run moved ≥ 0.15")
    else:
        cline = "—"
    body.append(f'<text x="{(pl+pr)/2:.0f}" y="{pt-18}" font-family="{FONT}" '
                f'font-size="15" fill="{GRAY}" text-anchor="middle">'
                f'{esc(cline)}</text>')

    # background: identical compounded 4-round forecast, painted cell by cell
    NX, NY = 56, 38
    cw = (pr - pl) / NX
    ch = (pb - pt) / NY
    body.append(f'<g opacity="{BG_ALPHA}">')
    for j in range(NY):
        py0 = pt + j * ch
        sig = px2sig(py0 + ch / 2, pt, pb)
        for i in range(NX):
            px0 = pl + i * cw
            rho = px2rho(px0 + cw / 2, pl, pr)
            colr = move_color(bg_move(rho, sig))
            body.append(f'<rect x="{px0:.1f}" y="{py0:.1f}" '
                        f'width="{cw+0.6:.2f}" height="{ch+0.6:.2f}" '
                        f'fill="{colr}"/>')
    body.append('</g>')

    # iso-contours of the forecast endpoint move Delta_v = 4*rho*sigma
    for c, sig_t in CONTOURS:
        pts = contour_polyline(c / 4.0, pl, pr, pt, pb)
        if not pts:
            continue
        dstr = " ".join(f"{'M' if i == 0 else 'L'}{x:.1f},{y:.1f}"
                        for i, (x, y) in enumerate(pts))
        body.append(f'<path d="{dstr}" fill="none" stroke="#4d4d4d" '
                    f'stroke-width="1.1" stroke-opacity="0.5" '
                    f'stroke-dasharray="5 4"/>')

    # frame + rho=0 line (also the forecast = 0 contour)
    body.append(f'<rect x="{pl}" y="{pt}" width="{pr-pl}" height="{pb-pt}" '
                f'fill="none" stroke="{GRAY}" stroke-width="1.6"/>')
    body.append(f'<line x1="{X(0,pl,pr):.1f}" y1="{pt}" '
                f'x2="{X(0,pl,pr):.1f}" y2="{pb}" stroke="#3d3d3d" '
                f'stroke-width="1.3" stroke-opacity="0.6"/>')

    # contour labels (white halo so they read over the gradient)
    for c, sig_t in CONTOURS:
        rho_t = (c / 4.0) / sig_t
        if not (RHO0 <= rho_t <= RHO1):
            continue
        halo_label(X(rho_t, pl, pr), Y(sig_t, pt, pb), f"Δv(4) = {c:+.2f}")
    halo_label(X(0, pl, pr), pt - 3, "Δv = 0", size=13.0)

    # axis ticks
    for rv in [-1.0, -0.5, 0.0, 0.5]:
        body.append(f'<line x1="{X(rv,pl,pr):.1f}" y1="{pb}" '
                    f'x2="{X(rv,pl,pr):.1f}" y2="{pb+8}" stroke="{GRAY}" '
                    f'stroke-width="1.6"/>')
        body.append(f'<text x="{X(rv,pl,pr):.1f}" y="{pb+27}" '
                    f'font-family="{FONT}" font-size="16" fill="{INK}" '
                    f'text-anchor="middle">{rv:+.1f}</text>')
    for sv in [0.0, 0.1, 0.2, 0.3, 0.4, 0.5]:
        body.append(f'<line x1="{pl-8}" y1="{Y(sv,pt,pb):.1f}" x2="{pl}" '
                    f'y2="{Y(sv,pt,pb):.1f}" stroke="{GRAY}" '
                    f'stroke-width="1.6"/>')
        body.append(f'<text x="{pl-13}" y="{Y(sv,pt,pb)+6:.1f}" '
                    f'font-family="{FONT}" font-size="16" fill="{INK}" '
                    f'text-anchor="end">{sv:.1f}</text>')

    # x-axis recipe title only under the bottom row (columns share x meaning)
    if is_bottom:
        body.append(f'<text x="{(pl+pr)/2:.0f}" y="{pb+56}" '
                    f'font-family="{FONT}" font-size="17" fill="{INK}" '
                    f'text-anchor="middle" font-weight="bold">round-1 agreement '
                    f'&#961;  <tspan font-weight="normal" fill="{GRAY}">= '
                    f'corr(judge scores, value scores)</tspan></text>')
        body.append(f'<text x="{(pl+pr)/2:.0f}" y="{pb+77}" '
                    f'font-family="{FONT}" font-size="15" fill="{GRAY}" '
                    f'text-anchor="middle">'
                    f'(&#8722;1 disagree &#8594; +1 lockstep)</text>')

    # empty cell: honest centered note over the (still-painted) background
    if n == 0:
        cx0, cy0 = (pl + pr) / 2, (pt + pb) / 2
        note_lines = wrap("no runs in the modeling corpus on this cell", 26)
        bh = 26 + len(note_lines) * 22
        bw = 320
        body.append(f'<rect x="{cx0-bw/2:.1f}" y="{cy0-bh/2:.1f}" '
                    f'width="{bw}" height="{bh}" rx="6" fill="white" '
                    f'fill-opacity="0.9" stroke="{GRAY}" stroke-width="1.3"/>')
        for i, ln in enumerate(note_lines):
            body.append(f'<text x="{cx0:.1f}" '
                        f'y="{cy0 - bh/2 + 30 + i*22:.1f}" '
                        f'font-family="{FONT}" font-size="16" fill="{GRAY}" '
                        f'text-anchor="middle" font-style="italic">'
                        f'{esc(ln)}</text>')
        return

    # dots (near-zero gray first so saturated movers sit on top)
    for r in sorted(sub, key=lambda z: abs(z["move"])):
        cx, cy = X(r["rho"], pl, pr), Y(r["spread"], pt, pb)
        body.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{DOT_R+1.4:.1f}" '
                    f'fill="none" stroke="white" stroke-width="2.4" '
                    f'stroke-opacity="0.9"/>')
        body.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{DOT_R:.1f}" '
                    f'fill="{move_color(r["move"])}" '
                    f'stroke="#3f454c" stroke-width="1.05"/>')


for key in CELLS:
    draw_panel(*key)

# shared y-axis title, once per row, on the far left
for row, (pt, pb) in ROWY.items():
    ymid = (pt + pb) / 2
    body.append(f'<text x="58" y="{ymid:.0f}" font-family="{FONT}" '
                f'font-size="17" fill="{INK}" text-anchor="middle" '
                f'font-weight="bold" transform="rotate(-90 58 {ymid:.0f})">'
                f'round-1 spread &#963;  <tspan font-weight="normal" '
                f'fill="{GRAY}">= within-prompt SD of value scores</tspan></text>')

# ---- shared color key (drawn once, right column) ----------------------------
LX = 1250
LY = ROWY[0][0]
body.append(f'<text x="{LX}" y="{LY}" font-family="{FONT}" font-size="19" '
            f'font-weight="bold" fill="{INK}">One color scale, two roles</text>')

# role 1: the dot
dyc = LY + 30
body.append(f'<circle cx="{LX+12:.1f}" cy="{dyc-5:.1f}" r="{DOT_R+1.4:.1f}" '
            f'fill="none" stroke="white" stroke-width="2.4"/>')
body.append(f'<circle cx="{LX+12:.1f}" cy="{dyc-5:.1f}" r="{DOT_R:.1f}" '
            f'fill="{move_color(0.45)}" stroke="#3f454c" stroke-width="1.05"/>')
for i, ln in enumerate(wrap("Dot fill = the run’s OBSERVED whole-run "
                            "endpoint move (final measured value − round-1 "
                            "value)", 40)):
    body.append(f'<text x="{LX+32}" y="{dyc + i*20:.0f}" font-family="{FONT}" '
                f'font-size="15" fill="{INK}">{esc(ln)}</text>')

# role 2: the background
byc = dyc + 84
body.append(f'<rect x="{LX+2:.1f}" y="{byc-17:.1f}" width="22" height="22" '
            f'rx="2" fill="{move_color(0.45)}" fill-opacity="{BG_ALPHA}" '
            f'stroke="{GRAY}" stroke-width="0.8"/>')
for i, ln in enumerate(wrap("Background (identical in all four panels) = the "
                            "model’s FORECAST 4-round endpoint move = "
                            "clip[−1,+1] of 4 · ρ · σ",
                            40)):
    body.append(f'<text x="{LX+32}" y="{byc + i*20:.0f}" font-family="{FONT}" '
                f'font-size="15" fill="{INK}">{esc(ln)}</text>')

# the shared diverging bar (red -> mid -> blue), exact match to move_color
bar_x = LX + 6
bar_y = byc + 108
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
for frac, lab in [(0.0, "+0.6  value climbs"), (1/6, "+0.4"), (2/6, "+0.2"),
                  (0.5, "0  no move"), (4/6, "−0.2"), (5/6, "−0.4"),
                  (1.0, "−0.6  value falls")]:
    yy = bar_y + bar_h * frac
    body.append(f'<line x1="{bar_x+bar_w}" y1="{yy:.1f}" x2="{bar_x+bar_w+6}" '
                f'y2="{yy:.1f}" stroke="{GRAY}" stroke-width="1.2"/>')
    body.append(f'<text x="{bar_x+bar_w+11}" y="{yy+5:.1f}" '
                f'font-family="{FONT}" font-size="15" fill="{INK}">'
                f'{esc(lab)}</text>')
body.append(f'<text x="{bar_x}" y="{bar_y+bar_h+22}" font-family="{FONT}" '
            f'font-size="13" fill="{GRAY}">same red/gray/blue endpoint-move</text>')
body.append(f'<text x="{bar_x}" y="{bar_y+bar_h+38}" font-family="{FONT}" '
            f'font-size="13" fill="{GRAY}">scale for ALL; saturates at ±0.6.</text>')

# ---- four-cell concordance readout box (shared, right column) ---------------
box_x, box_y, box_w = LX, bar_y + bar_h + 60, 400
box_h = 278
body.append(f'<rect x="{box_x}" y="{box_y}" width="{box_w}" height="{box_h}" '
            f'rx="6" fill="{KEY_FILL}" stroke="{GREEN}" stroke-width="1.4"/>')
body.append(f'<text x="{box_x+14}" y="{box_y+25}" font-family="{FONT}" '
            f'font-size="16" font-weight="bold" fill="{INK}">Dot color matches '
            f'background?</text>')
body.append(f'<text x="{box_x+14}" y="{box_y+47}" font-family="{FONT}" '
            f'font-size="14" fill="{INK}">Movers = |observed move| ≥ 0.15; '
            f'a match</text>')
body.append(f'<text x="{box_x+14}" y="{box_y+65}" font-family="{FONT}" '
            f'font-size="14" fill="{INK}">means sign(move) = '
            f'sign(4·ρ·σ).</text>')
rows = []
for key in CELLS:
    org, axis = key
    c, m = CONC[key]
    n = COUNTS[key]
    if n == 0:
        txt = f"{ORG_NAME[org]} · {AXIS_NAME[axis]}:  no runs"
    elif m == 0:
        txt = f"{ORG_NAME[org]} · {AXIS_NAME[axis]}:  0 movers"
    else:
        txt = (f"{ORG_NAME[org]} · {AXIS_NAME[axis]}:  {c} of {m}  "
               f"({round(100*c/m)}%)")
    rows.append(txt)
for i, txt in enumerate(rows):
    yy = box_y + 94 + i * 24
    body.append(f'<text x="{box_x+14}" y="{yy}" font-family="{FONT}" '
                f'font-size="14" font-weight="bold" fill="{INK}">'
                f'{esc(txt)}</text>')
pc = sum(c for c, _ in CONC.values())
pm = sum(m for _, m in CONC.values())
note = (f"Pooled: {pc} of {pm}. Both Qwen cells are unanimous; every one of the "
        f"{pm-pc} clashes sits in OLMo’s risk cell. The OLMo self-report "
        f"cell is empty in the corpus.")
for i, ln in enumerate(wrap(note, 44)):
    body.append(f'<text x="{box_x+14}" y="{box_y+196 + i*17}" '
                f'font-family="{FONT}" font-size="13" '
                f'fill="{GRAY}">{esc(ln)}</text>')

# ---- scope line (bottom, spanning under the panels) -------------------------
scope = (f"Scope: 4-round runs only — the {N_EXCL} eight-round "
         f"judge-schedule runs are excluded and {N_SKIP} runs are skipped for "
         f"undefined ρ (zero within-pool spread), leaving {len(RUNS)} of "
         f"{N_RUNS} runs. R = 4 is every plotted run’s exact horizon. "
         "Mixed-pool runs also feel the outside-source pull (p − q), so the "
         "4·ρσ background is the self-only force map — sign "
         "and relative magnitude are what compare.")
for i, ln in enumerate(wrap(scope, 160)):
    body.append(f'<text x="{LEFT}" y="{ROWY[1][1]+108 + i*22}" '
                f'font-family="{FONT}" font-size="15" fill="{GRAY}">'
                f'{esc(ln)}</text>')

svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
       f'font-family="{FONT}">\n<rect width="{W}" height="{H}" fill="white"/>\n'
       + "\n".join(body) + "\n</svg>\n")

with open(os.path.join(HERE, "synthesis-dial-plane-horizon-4way.svg"),
          "w") as f:
    f.write(svg)
print("wrote synthesis-dial-plane-horizon-4way.svg")
for key in CELLS:
    org, axis = key
    c, m = CONC[key]
    print(f"  {ORG_NAME[org]:9s} {axis:11s}: {COUNTS[key]:2d} runs, "
          f"concord {c}/{m}")
print(f"  sum of cells = {sum(COUNTS.values())} (must equal plotted {len(RUNS)})")
print(f"  pooled concord {pc}/{pm}; {N_EXCL} excluded, {N_SKIP} skipped, "
      f"{N_RUNS} total; R={R_HORIZON}")
