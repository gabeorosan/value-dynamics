#!/usr/bin/env python3
"""Synthesis candidate, SPLIT BY VALUE AXIS: the (agreement rho, spread sigma)
plane with the model's forecast painted as the background, now shown as TWO
panels -- one per behavioral value axis. Left = the risk-seeking value runs;
right = the insecure-code self-description runs.

Every modelable 4-round run is placed at its round-1 dials; DOT color encodes
the run's observed net WHOLE-RUN endpoint move of the behavioral value, on a
continuous red(up)-gray(none)-blue(down) diverging scale. The BACKGROUND is
painted, on the SAME color scale, by the committed recurrence's forecast
ENDPOINT move over the corpus-typical horizon:

    Delta_v_pred(R) = clip to [-1, +1] of ( R * rho * sigma ),   R = 4 rounds.

Both panels share the IDENTICAL background gradient, contours, axes, and color
scale (the background depends only on rho and sigma, not on the value axis), so
placing them side by side asks the same question of each value separately: does
the dot color match the gradient behind it? A match = the model's 4-round
forecast holding for that value; a clash = the forecast failing.

Honesty scope kept explicit: the 11 judge-schedule runs actually ran 8 rounds
and are excluded, and the mixed-pool runs also feel the outside-source pull
(p - q), so the 4*rho*sigma background is the SELF-ONLY, 4-round force map, not
each run's exact per-run forecast. Only sign and relative magnitude are strictly
comparable; the background is drawn at reduced opacity.

Reads experiments/spread_util_unified.json (records list). One run = the tuple
(cond, seed, source); the round-1 record supplies rho, spread, value, AND the
value axis ("risk" vs "selfreport"); the last record supplies value+drift. Runs
whose round-1 rho is null (zero within-pool spread makes the correlation
undefined) are not plottable on these two axes.

Style reference: docs/figures/src/make_figures.py (INK/BLUE/GREEN/RED/GRAY,
esc()/wrap()). Stdlib only. Run from this directory:
    python3 synthesis-dial-plane-horizon-byaxis.py
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


DOT_R = 8.0    # uniform dot radius (no size encoding); slightly reduced to keep
               # the split panels legible
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
                         axis=r1["axis"], rho=r1["rho"], spread=r1["spread"],
                         value=r1["value"], move=move))
    return d, plot, len(runs), skipped, excluded_len


DATA_D, RUNS, N_RUNS, N_SKIP, N_EXCL = load_runs()
assert N_RUNS == 74, N_RUNS
assert N_EXCL == 11, N_EXCL          # the 8-round judge-schedule runs
assert len(RUNS) == 56, len(RUNS)
assert N_SKIP == 7, N_SKIP

# ---- split by value axis ----------------------------------------------------
RISK = [r for r in RUNS if r["axis"] == "risk"]
SELF = [r for r in RUNS if r["axis"] == "selfreport"]
N_RISK, N_SELF = len(RISK), len(SELF)
assert N_RISK + N_SELF == 56, (N_RISK, N_SELF)

THRESH = 0.15  # descriptive threshold for the mover / concordance counts


def concord(sub):
    movers = [r for r in sub if abs(r["move"]) >= THRESH and r["rho"] != 0.0]
    n_conc = sum(1 for r in movers if (r["move"] > 0) == (r["rho"] > 0))
    return len(movers), n_conc


RISK_MOV, RISK_CONC = concord(RISK)
SELF_MOV, SELF_CONC = concord(SELF)
# whole-corpus totals must still reconcile with the un-split figure
assert RISK_MOV + SELF_MOV == 41, (RISK_MOV, SELF_MOV)
assert RISK_CONC + SELF_CONC == 35, (RISK_CONC, SELF_CONC)
# observed split: all discordance sits on the risk axis; self-report is perfect
assert (RISK_MOV, RISK_CONC) == (29, 23), (RISK_MOV, RISK_CONC)
assert (SELF_MOV, SELF_CONC) == (12, 12), (SELF_MOV, SELF_CONC)

# ---- geometry ---------------------------------------------------------------
W, H = 1820, 1010
PT, PB = 300, 780           # shared plot top / bottom (px)
# left panel (risk) and right panel (selfreport) plot x-extents
PL_A, PR_A = 150, 730
PL_B, PR_B = 850, 1430
RHO0, RHO1 = -1.08, 0.95    # x data domain (shared)
SIG0, SIG1 = 0.0, 0.50      # y data domain (shared)


def X(rho, pl, pr):
    return pl + (rho - RHO0) / (RHO1 - RHO0) * (pr - pl)


def Y(sig):
    return PB - (sig - SIG0) / (SIG1 - SIG0) * (PB - PT)


def px2rho(px, pl, pr):
    return RHO0 + (px - pl) / (pr - pl) * (RHO1 - RHO0)


def px2sig(py):
    return SIG0 + (PB - py) / (PB - PT) * (SIG1 - SIG0)


# each entry: (Delta_v level c, sigma at which to place the label)
CONTOURS = [(-0.40, 0.115), (-0.20, 0.155), (0.20, 0.155), (0.40, 0.115)]


def contour_polyline(k, pl, pr):   # k is the rho*sigma product level = c/4
    if k > 0:
        rlo, rhi = k / SIG1, RHO1
    else:
        rlo, rhi = RHO0, k / SIG1
    if not rlo < rhi:
        return []
    pts, n = [], 80
    for i in range(n + 1):
        rho = rlo + (rhi - rlo) * i / n
        if abs(rho) < 1e-9:
            continue
        sig = k / rho
        if SIG0 - 1e-9 <= sig <= SIG1 + 1e-9:
            pts.append((X(rho, pl, pr), Y(min(max(sig, SIG0), SIG1))))
    return pts


# ============================================================================
body = []


def halo_label(cx, cy, text, size=14.5, weight="normal", anchor="middle"):
    w_px = len(text) * size * 0.56
    body.append(f'<rect x="{cx - w_px/2 - 4:.1f}" y="{cy - size*0.82:.1f}" '
                f'width="{w_px + 8:.1f}" height="{size*1.25:.1f}" rx="3" '
                f'fill="white" fill-opacity="0.86"/>')
    body.append(f'<text x="{cx:.1f}" y="{cy + size*0.34:.1f}" '
                f'font-family="{FONT}" font-size="{size}" fill="#333" '
                f'font-weight="{weight}" text-anchor="{anchor}">'
                f'{esc(text)}</text>')


def draw_panel(pl, pr, sub, title, subtitle, show_ylabel):
    """Draw one value-axis panel: shared background gradient, iso-contours,
    frame, ticks, axis titles, and this axis's dots."""
    # --- background: model's compounded 4-round forecast, painted cell by cell
    NX, NY = 48, 40
    cw = (pr - pl) / NX
    ch = (PB - PT) / NY
    body.append(f'<g opacity="{BG_ALPHA}">')
    for j in range(NY):
        py0 = PT + j * ch
        sig = px2sig(py0 + ch / 2)
        for i in range(NX):
            px0 = pl + i * cw
            rho = px2rho(px0 + cw / 2, pl, pr)
            col = move_color(bg_move(rho, sig))
            body.append(f'<rect x="{px0:.1f}" y="{py0:.1f}" '
                        f'width="{cw+0.6:.2f}" height="{ch+0.6:.2f}" '
                        f'fill="{col}"/>')
    body.append('</g>')

    # --- iso-contours of the forecast endpoint move Delta_v = 4*rho*sigma
    for c, sig_t in CONTOURS:
        pts = contour_polyline(c / 4.0, pl, pr)
        if not pts:
            continue
        dstr = " ".join(f"{'M' if i == 0 else 'L'}{x:.1f},{y:.1f}"
                        for i, (x, y) in enumerate(pts))
        body.append(f'<path d="{dstr}" fill="none" stroke="#4d4d4d" '
                    f'stroke-width="1.1" stroke-opacity="0.5" '
                    f'stroke-dasharray="5 4"/>')

    # --- frame + rho=0 (which is also the forecast = 0 contour)
    body.append(f'<rect x="{pl}" y="{PT}" width="{pr-pl}" height="{PB-PT}" '
                f'fill="none" stroke="{GRAY}" stroke-width="1.6"/>')
    x0 = X(0, pl, pr)
    body.append(f'<line x1="{x0:.1f}" y1="{PT}" x2="{x0:.1f}" y2="{PB}" '
                f'stroke="#3d3d3d" stroke-width="1.3" stroke-opacity="0.6"/>')

    # --- contour labels (white halo so they read over any background)
    for c, sig_t in CONTOURS:
        rho_t = (c / 4.0) / sig_t
        if RHO0 <= rho_t <= RHO1:
            halo_label(X(rho_t, pl, pr), Y(sig_t), f"Δv(4) = {c:+.2f}",
                       size=12.5)
    halo_label(x0, PT - 12, "Δv = 0", size=13)

    # --- axis ticks
    for rv in [-1.0, -0.5, 0.0, 0.5]:
        xx = X(rv, pl, pr)
        body.append(f'<line x1="{xx:.1f}" y1="{PB}" x2="{xx:.1f}" '
                    f'y2="{PB+8}" stroke="{GRAY}" stroke-width="1.6"/>')
        body.append(f'<text x="{xx:.1f}" y="{PB+30}" font-family="{FONT}" '
                    f'font-size="17" fill="{INK}" text-anchor="middle">'
                    f'{rv:+.1f}</text>')
    for sv in [0.0, 0.1, 0.2, 0.3, 0.4, 0.5]:
        body.append(f'<line x1="{pl-8}" y1="{Y(sv):.1f}" x2="{pl}" '
                    f'y2="{Y(sv):.1f}" stroke="{GRAY}" stroke-width="1.6"/>')
        body.append(f'<text x="{pl-13}" y="{Y(sv)+6:.1f}" '
                    f'font-family="{FONT}" font-size="16" fill="{INK}" '
                    f'text-anchor="end">{sv:.1f}</text>')

    # --- axis titles (x on both panels; y-recipe only on left to save space)
    cxm = (pl + pr) / 2
    body.append(f'<text x="{cxm:.0f}" y="{PB+62}" font-family="{FONT}" '
                f'font-size="18" fill="{INK}" text-anchor="middle" '
                f'font-weight="bold">round-1 agreement &#961;  '
                f'<tspan font-weight="normal" fill="{GRAY}">= corr(judge score, '
                f'candidate value)</tspan></text>')
    body.append(f'<text x="{cxm:.0f}" y="{PB+84}" font-family="{FONT}" '
                f'font-size="16" fill="{GRAY}" text-anchor="middle">'
                f'(&#8722;1 disagree &#8594; +1 lockstep)</text>')
    if show_ylabel:
        yc = (PT + PB) / 2
        body.append(f'<text x="46" y="{yc:.0f}" font-family="{FONT}" '
                    f'font-size="18" fill="{INK}" text-anchor="middle" '
                    f'font-weight="bold" transform="rotate(-90 46 {yc:.0f})">'
                    f'round-1 spread &#963;  <tspan font-weight="normal" '
                    f'fill="{GRAY}">= within-prompt SD of value scores</tspan>'
                    f'</text>')
    else:
        yc = (PT + PB) / 2
        body.append(f'<text x="{pl-52}" y="{yc:.0f}" font-family="{FONT}" '
                    f'font-size="18" fill="{INK}" text-anchor="middle" '
                    f'font-weight="bold" transform="rotate(-90 {pl-52} '
                    f'{yc:.0f})">round-1 spread &#963;</text>')

    # --- panel title + live counts + concordance line
    body.append(f'<text x="{pl}" y="{PT-56}" font-family="{FONT}" '
                f'font-size="24" font-weight="bold" fill="{INK}">'
                f'{esc(title)}</text>')
    body.append(f'<text x="{pl}" y="{PT-30}" font-family="{FONT}" '
                f'font-size="17" fill="{INK}">{esc(subtitle)}</text>')

    # --- dots (near-zero gray first so saturated movers sit on top)
    for r in sorted(sub, key=lambda z: abs(z["move"])):
        cx, cy = X(r["rho"], pl, pr), Y(r["spread"])
        body.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{DOT_R+1.3:.1f}" '
                    f'fill="none" stroke="white" stroke-width="2.4" '
                    f'stroke-opacity="0.9"/>')
        body.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{DOT_R:.1f}" '
                    f'fill="{move_color(r["move"])}" '
                    f'stroke="#3f454c" stroke-width="1.0"/>')


# ---- title / subtitle (headline finding + honesty line) ---------------------
title = ("Split by value axis: within each behavioral value, does dot color "
         "(observed whole-run move) match the background (the model's forecast "
         "4-round move)?")
for i, ln in enumerate(wrap(title, 88)):
    body.append(f'<text x="{PL_A}" y="{56 + i*36}" font-family="{FONT}" '
                f'font-size="29" font-weight="bold" fill="{INK}">'
                f'{esc(ln)}</text>')
sub1 = (f"one dot per run · {len(RUNS)} modelable 4-round runs from "
        f"experiments/spread_util_unified.json, split by each run's value axis "
        f"· {N_RISK} risk + {N_SELF} self-description = {len(RUNS)}")
body.append(f'<text x="{PL_A}" y="164" font-family="{FONT}" '
            f'font-size="19" fill="{GRAY}">{esc(sub1)}</text>')
sub2 = ("Background = Δv_pred(4) = clip[−1,+1] of 4·ρ·σ — one selection step "
        "ρσ per round, wall-capped — identical in both panels, on the dots' own "
        "endpoint-move color scale.")
for i, ln in enumerate(wrap(sub2, 118)):
    body.append(f'<text x="{PL_A}" y="{190 + i*23}" font-family="{FONT}" '
                f'font-size="16.5" fill="{INK}">{esc(ln)}</text>')

# ---- the two panels ---------------------------------------------------------
draw_panel(PL_A, PR_A, RISK,
           f"risk-seeking value ({N_RISK} runs)",
           f"{RISK_CONC} of {RISK_MOV} movers match the forecast sign",
           show_ylabel=True)
draw_panel(PL_B, PR_B, SELF,
           f"insecure-code self-description value ({N_SELF} runs)",
           f"{SELF_CONC} of {SELF_MOV} movers match the forecast sign",
           show_ylabel=False)

# ---- shared color key (right of the right panel) ----------------------------
LX = PR_B + 46
LY = 300
body.append(f'<text x="{LX}" y="{LY}" font-family="{FONT}" font-size="19" '
            f'font-weight="bold" fill="{INK}">One color scale, two roles</text>')

# role 1: the dot
dyc = LY + 30
body.append(f'<circle cx="{LX+13:.1f}" cy="{dyc-5:.1f}" r="{DOT_R+1.3:.1f}" '
            f'fill="none" stroke="white" stroke-width="2.4"/>')
body.append(f'<circle cx="{LX+13:.1f}" cy="{dyc-5:.1f}" r="{DOT_R:.1f}" '
            f'fill="{move_color(0.45)}" stroke="#3f454c" stroke-width="1.0"/>')
for i, ln in enumerate(wrap("Dot fill = the run's OBSERVED whole-run endpoint "
                            "move (final measured value − round-1 value)", 34)):
    body.append(f'<text x="{LX+34}" y="{dyc + i*20:.0f}" font-family="{FONT}" '
                f'font-size="15" fill="{INK}">{esc(ln)}</text>')

# role 2: the background
byc = dyc + 76
body.append(f'<rect x="{LX+3:.1f}" y="{byc-17:.1f}" width="22" height="22" '
            f'rx="2" fill="{move_color(0.45)}" fill-opacity="{BG_ALPHA}" '
            f'stroke="{GRAY}" stroke-width="0.8"/>')
for i, ln in enumerate(wrap("Background = the model's FORECAST 4-round endpoint "
                            "move = clip[−1,+1] of 4 · ρ · σ (one selection "
                            "step ρσ per round, wall-capped)", 34)):
    body.append(f'<text x="{LX+34}" y="{byc + i*20:.0f}" font-family="{FONT}" '
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
for frac, lab in [(0.0, "+0.6  value climbs"), (0.5, "0  no move"),
                  (1.0, "−0.6  value falls")]:
    yy = bar_y + bar_h * frac
    body.append(f'<line x1="{bar_x+bar_w}" y1="{yy:.1f}" x2="{bar_x+bar_w+6}" '
                f'y2="{yy:.1f}" stroke="{GRAY}" stroke-width="1.2"/>')
    body.append(f'<text x="{bar_x+bar_w+11}" y="{yy+5:.1f}" '
                f'font-family="{FONT}" font-size="15" fill="{INK}">'
                f'{esc(lab)}</text>')
body.append(f'<text x="{bar_x}" y="{bar_y+bar_h+22}" font-family="{FONT}" '
            f'font-size="13.5" fill="{GRAY}">same red/gray/blue endpoint-move</text>')
body.append(f'<text x="{bar_x}" y="{bar_y+bar_h+38}" font-family="{FONT}" '
            f'font-size="13.5" fill="{GRAY}">scale for BOTH; saturates at ±0.6.</text>')

# ---- shared concordance readout box (both counts) ---------------------------
box_x, box_y, box_w = LX, bar_y + bar_h + 54, 320
box_h = 168
body.append(f'<rect x="{box_x}" y="{box_y}" width="{box_w}" height="{box_h}" '
            f'rx="6" fill="{KEY_FILL}" stroke="{GREEN}" stroke-width="1.4"/>')
body.append(f'<text x="{box_x+14}" y="{box_y+25}" font-family="{FONT}" '
            f'font-size="16" font-weight="bold" fill="{INK}">Sign match, per '
            f'value axis</text>')
read = (f"risk-seeking: {RISK_CONC} of {RISK_MOV} movers match. "
        f"insecure-code self-description: {SELF_CONC} of {SELF_MOV} match. "
        f"All {RISK_MOV + SELF_MOV - RISK_CONC - SELF_CONC} discordant dots sit "
        f"on the risk axis; self-description is perfectly concordant. (A mover "
        f"= |move| ≥ 0.15; match = sign of the move equals sign of 4·ρ·σ.)")
for i, ln in enumerate(wrap(read, 42)):
    body.append(f'<text x="{box_x+14}" y="{box_y+48 + i*18}" '
                f'font-family="{FONT}" font-size="14" fill="{INK}">'
                f'{esc(ln)}</text>')

# ---- scope line (bottom, spanning under both panels) ------------------------
scope = (f"Scope: 4-round runs only — the {N_EXCL} eight-round judge-schedule "
         f"runs are excluded and {N_SKIP} runs are skipped for an undefined "
         f"round-1 ρ (zero within-pool spread), out of {N_RUNS} runs total, "
         f"leaving {len(RUNS)}. R = 4 is every plotted run's exact horizon. "
         f"Mixed-pool runs also feel the outside-source pull (p − q), so the "
         f"4·ρσ background is the self-only force map.")
for i, ln in enumerate(wrap(scope, 150)):
    body.append(f'<text x="{PL_A}" y="{PB+112 + i*22}" font-family="{FONT}" '
                f'font-size="15" fill="{GRAY}">{esc(ln)}</text>')

svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
       f'font-family="{FONT}">\n<rect width="{W}" height="{H}" fill="white"/>\n'
       + "\n".join(body) + "\n</svg>\n")

with open(os.path.join(HERE, "synthesis-dial-plane-horizon-byaxis.svg"),
          "w") as f:
    f.write(svg)
print(f"wrote synthesis-dial-plane-horizon-byaxis.svg  "
      f"(risk: {N_RISK} runs, {RISK_CONC}/{RISK_MOV} movers concordant; "
      f"self-description: {N_SELF} runs, {SELF_CONC}/{SELF_MOV} concordant; "
      f"{N_SKIP} skipped, {N_EXCL} excluded, {N_RUNS} total)")
