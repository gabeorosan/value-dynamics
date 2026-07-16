#!/usr/bin/env python3
"""Synthesis candidate A: the (agreement rho, spread sigma) plane.

Every modelable run placed at its round-1 dials; dot color = the observed net
endpoint move of the behavioral value; background = contours of constant
per-round selection pressure |rho*sigma|.

Reads experiments/spread_util_unified.json (records list). One run = the tuple
(cond, seed, source); the round-1 record supplies rho, spread, value; the last
record supplies value+drift. Runs whose round-1 rho is null (zero within-pool
spread makes the correlation undefined) are not plottable on these two axes.

Style reference: docs/figures/src/make_figures.py (INK/BLUE/GREEN/RED/GRAY,
esc()/wrap()). Stdlib only. Run from this directory:  python3 synthesis-dial-plane.py
"""
import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "..", "..", "..", "experiments",
                    "spread_util_unified.json")

# ---- palette (verbatim from make_figures.py) --------------------------------
INK = "#1a1a1a"
BLUE = "#2867b5"       # self-judge series / here: value moved DOWN
GREEN = "#3a7d44"
RED = "#b5342c"        # emphasis / here: value moved UP
GRAY = "#6b7684"       # recessive only + diverging neutral midpoint
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


# ---- color helpers ----------------------------------------------------------
def _hex2rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def _rgb2hex(rgb):
    return "#%02x%02x%02x" % tuple(max(0, min(255, int(round(c)))) for c in rgb)


def lerp(c1, c2, t):
    a, b = _hex2rgb(c1), _hex2rgb(c2)
    return _rgb2hex([a[i] + (b[i] - a[i]) * t for i in range(3)])


DEAD = 0.15   # |move| below this reads as "no net move" (gray)
CAP = 0.60    # move at which color/size saturate


def move_color(move):
    m = abs(move)
    if m < DEAD:
        return GRAY
    t = min((m - DEAD) / (CAP - DEAD), 1.0)
    pole = BLUE if move < 0 else RED
    return lerp(GRAY, pole, 0.25 + 0.75 * t)


def move_radius(move):
    return 7.0 + 13.0 * min(abs(move) / CAP, 1.0)


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
                         judge=r1["judge"], comp=r1["composition"],
                         fmt=r1["format"], rho=r1["rho"], spread=r1["spread"],
                         value=r1["value"], move=move))
    return d, plot, len(runs), skipped


DATA_D, RUNS, N_RUNS, N_SKIP = load_runs()
assert N_RUNS == 74, N_RUNS
assert len(RUNS) == 67, len(RUNS)
assert N_SKIP == 7, N_SKIP

# ---- geometry ---------------------------------------------------------------
W, H = 1460, 1000
PL, PR = 150, 1070          # plot left / right (px)
PT, PB = 268, 830           # plot top / bottom (px)
RHO0, RHO1 = -1.06, 0.92    # x data domain
SIG0, SIG1 = 0.0, 0.50      # y data domain


def X(rho):
    return PL + (rho - RHO0) / (RHO1 - RHO0) * (PR - PL)


def Y(sig):
    return PB - (sig - SIG0) / (SIG1 - SIG0) * (PB - PT)


# ============================================================================
body = []

# ---- title / subtitle -------------------------------------------------------
body.append(f'<text x="{PL}" y="70" font-family="{FONT}" font-size="33" '
            f'font-weight="bold" fill="{INK}">Every run, placed by its '
            f'first-round dials &#8212; pressure predicts who moved</text>')
sub = ("one dot per run (67 modelable runs, all five experiment families); "
       "color = observed endpoint move of the behavioral value")
for i, ln in enumerate(wrap(sub, 96)):
    body.append(f'<text x="{PL}" y="{112 + i*30}" font-family="{FONT}" '
                f'font-size="23" fill="{GRAY}">{esc(ln)}</text>')

# takeaway strip
tk = ("Runs move when they start away from both axes &#8212; pressure "
      "|&#961;&#183;&#963;| &#8776; 0 predicts standing still.")
body.append(f'<rect x="{PL}" y="176" width="{PR-PL}" height="52" rx="9" '
            f'fill="{KEY_FILL}" stroke="{INK}" stroke-width="2"/>')
body.append(f'<text x="{PL+22}" y="210" font-family="{FONT}" font-size="25" '
            f'font-weight="bold" fill="{INK}">{tk}</text>')

# ---- background: nested pressure bands + contour lines ----------------------
LEVELS = [0.02, 0.05, 0.1, 0.2]
# faint nested fills for the corner (high-pressure) regions
for L in [0.05, 0.1, 0.2]:
    for sign in (-1, 1):
        # region |rho*sigma| >= L, i.e. sigma >= L/|rho|, clipped to plot box
        pts = []
        rho_edge = sign * 1.0                      # rho = +/-1 (plot edge in data)
        rho_top = sign * (L / SIG1)                # where curve hits sigma=SIG1
        # walk the curve from the |rho|=1 edge inward to rho_top
        n = 40
        for k in range(n + 1):
            rr = rho_edge + (rho_top - rho_edge) * k / n
            ss = min(L / abs(rr), SIG1)
            pts.append((X(rr), Y(ss)))
        # up the top edge and back along the top to the edge corner
        pts.append((X(rho_top), Y(SIG1)))
        pts.append((X(rho_edge), Y(SIG1)))
        poly = " ".join(f"{px:.1f},{py:.1f}" for px, py in pts)
        body.append(f'<polygon points="{poly}" fill="#46597a" '
                    f'fill-opacity="0.055" stroke="none"/>')

# contour curves + labels
for L in LEVELS:
    for sign in (-1, 1):
        pts = []
        n = 90
        for k in range(n + 1):
            # sweep sigma, solve rho = sign*L/sigma
            ss = SIG1 * k / n
            if ss <= 1e-6:
                continue
            rr = sign * L / ss
            if rr < RHO0 or rr > RHO1:
                continue
            pts.append((X(rr), Y(ss)))
        if len(pts) < 2:
            continue
        d = "M " + " L ".join(f"{px:.1f} {py:.1f}" for px, py in pts)
        body.append(f'<path d="{d}" fill="none" stroke="{GRAY}" '
                    f'stroke-width="1.4" stroke-dasharray="5 5" '
                    f'stroke-opacity="0.55"/>')
    # label each contour along the positive-rho side at a fixed rho, where the
    # curves fan out vertically and there is open space below the top dots
    lab_rho = 0.86
    lab_sig = L / lab_rho
    if lab_sig <= SIG1:
        body.append(f'<text x="{X(lab_rho)+6:.1f}" y="{Y(lab_sig)-4:.1f}" '
                    f'font-family="{FONT}" font-size="15" fill="{GRAY}" '
                    f'font-style="italic">|&#961;&#183;&#963;|={L:g}</text>')

body.append(f'<text x="{X(-0.42):.1f}" y="{Y(0.055):.1f}" '
            f'font-family="{FONT}" font-size="16" fill="{GRAY}" '
            f'font-weight="bold">dashed curves: constant per-round '
            f'selection pressure |&#961;&#183;&#963;|</text>')

# ---- axes -------------------------------------------------------------------
# plot frame
body.append(f'<rect x="{PL}" y="{PT}" width="{PR-PL}" height="{PB-PT}" '
            f'fill="none" stroke="{GRAY}" stroke-width="1.6"/>')
# rho=0 reference line
body.append(f'<line x1="{X(0):.1f}" y1="{PT}" x2="{X(0):.1f}" y2="{PB}" '
            f'stroke="{GRAY}" stroke-width="1.2" stroke-opacity="0.5"/>')
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
body.append(f'<text x="{(PL+PR)/2:.0f}" y="{PB+66}" font-family="{FONT}" '
            f'font-size="21" fill="{INK}" text-anchor="middle" '
            f'font-weight="bold">round-1 agreement &#961;  '
            f'<tspan font-weight="normal" fill="{GRAY}">= correlation of judge '
            f'scores with candidate value scores '
            f'(&#8722;1 disagreement &#8594; +1 lockstep)</tspan></text>')
body.append(f'<text x="46" y="{(PT+PB)/2:.0f}" font-family="{FONT}" '
            f'font-size="21" fill="{INK}" text-anchor="middle" '
            f'font-weight="bold" transform="rotate(-90 46 {(PT+PB)/2:.0f})">'
            f'round-1 spread &#963;  <tspan font-weight="normal" '
            f'fill="{GRAY}">= within-prompt SD of candidate value scores</tspan></text>')

# corner cue: pressure grows toward the corners
body.append(f'<text x="{X(-1.0):.1f}" y="{Y(0.03):.1f}" font-family="{FONT}" '
            f'font-size="15" fill="{GRAY}" text-anchor="middle" '
            f'font-style="italic">low pressure near the axes</text>')

# ---- dots -------------------------------------------------------------------
# draw large (big-move) dots first so small no-move dots sit on top and stay legible
for r in sorted(RUNS, key=lambda z: -abs(z["move"])):
    cx, cy = X(r["rho"]), Y(r["spread"])
    rad = move_radius(r["move"])
    col = move_color(r["move"])
    body.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{rad:.1f}" '
                f'fill="{col}" fill-opacity="0.9" stroke="white" '
                f'stroke-width="1.6"/>')

# ---- landmark labels (positions derived from the data, text in plain words) -
def leader(lx, ly, tx, ty):
    return (f'<line x1="{lx:.1f}" y1="{ly:.1f}" x2="{tx:.1f}" y2="{ty:.1f}" '
            f'stroke="{INK}" stroke-width="1.4"/>')


def note(x, y, lines, anchor="start", color=INK, size=18):
    out = []
    for i, ln in enumerate(lines):
        fw = 'font-weight="bold"' if i == 0 else ''
        out.append(f'<text x="{x:.1f}" y="{y + i*22:.1f}" font-family="{FONT}" '
                   f'font-size="{size}" fill="{color}" text-anchor="{anchor}" '
                   f'{fw}>{ln}</text>')
    return "\n".join(out)


# 1. score-oracle cells at rho=-1 (all collapse)
lx, ly = X(-1.0), Y(0.27)
body.append(leader(lx + 12, ly, X(-0.72), Y(0.44)))
body.append(note(X(-0.71), Y(0.44) - 4,
                 ["score-oracle cells (&#961; = &#8722;1):",
                  "judge forced to fight the value &#8212;",
                  "every cell collapses (moves &#8722;0.4 to &#8722;0.8)"],
                 color=BLUE))

# 2. self-judge duel erosion (head2head_selfjudge, rho ~ -0.3, moved down)
sj = [r for r in RUNS if r["cond"] == "head2head_selfjudge"]
sx = sum(r["rho"] for r in sj) / len(sj)
sy = sum(r["spread"] for r in sj) / len(sj)
body.append(leader(X(sx), Y(sy) + 14, X(-0.62), Y(0.20)))
body.append(note(X(-0.98), Y(0.155) - 4,
                 ["self-judge duel erosion",
                  "(&#961; &#8776; &#8722;0.28): value slides down"],
                 color=BLUE))

# 3. weak self-only cluster near rho ~ 0 (mixed signs = noise)
body.append(leader(X(0.0), Y(0.435) + 2, X(-0.30), Y(0.485)))
body.append(note(X(-0.62), Y(0.492),
                 ["self-only, &#961; &#8776; 0: near-zero pressure &#8212; "
                  "moves scatter both ways",
                  "(training noise, not selection)"], color=GRAY))

# 4. peer-injection duels / references, upper right (big up moves)
body.append(leader(X(0.60), Y(0.42), X(0.70), Y(0.24)))
body.append(note(X(0.30), Y(0.205),
                 ["peer / base injection (&#961; &#8776; +0.4 to +0.7):",
                  "strong selection drives the value UP",
                  "(moves +0.6 to +0.8)"], color=RED))

# 5. cautious / base rescue cells: start high, pulled down
body.append(leader(X(0.38), Y(0.278) - 12, X(0.10), Y(0.135)))
body.append(note(X(-0.42), Y(0.115),
                 ["cautious / base-rescue cells: start near 1.0,",
                  "get pulled back down (moves &#8722;0.15 to &#8722;0.45)"],
                 color=BLUE))

# ---- off-plane injection twin (sigma = 0 => rho undefined) ------------------
tw_x, tw_y = X(-0.02), PB + 92
body.append(f'<rect x="{X(-1.05):.1f}" y="{PB+74}" width="470" height="46" '
            f'rx="8" fill="white" stroke="{GRAY}" stroke-width="1.4" '
            f'stroke-dasharray="4 4"/>')
body.append(f'<circle cx="{X(-1.0)+22:.1f}" cy="{PB+97:.1f}" r="9" '
            f'fill="none" stroke="{GRAY}" stroke-width="2.2"/>')
body.append(note(X(-1.0) + 42, PB + 92,
                 ["off-plane: the &#963;=0 injection twin has no within-pool "
                  "spread,",
                  "so &#961; is undefined &#8212; and its value held at 1.00 "
                  "(no spread, no move)"],
                 color=GRAY, size=15.5))

# ============================================================================
# ---- legend panel (right side) ---------------------------------------------
LX = 1110
body.append(f'<text x="{LX}" y="{PT+6}" font-family="{FONT}" font-size="19" '
            f'font-weight="bold" fill="{INK}">endpoint move of</text>')
body.append(f'<text x="{LX}" y="{PT+30}" font-family="{FONT}" font-size="19" '
            f'font-weight="bold" fill="{INK}">the behavioral value</text>')
body.append(f'<text x="{LX}" y="{PT+52}" font-family="{FONT}" font-size="14.5" '
            f'fill="{GRAY}">(last value+drift) &#8722; round-1 value</text>')

# diverging color bar
bar_x, bar_y, bar_w, bar_h = LX, PT + 70, 26, 250
seg = 60
for i in range(seg):
    t = i / (seg - 1)                       # 0=top -> 1=bottom
    mv = CAP - 2 * CAP * t                  # +CAP at top -> -CAP at bottom
    yy = bar_y + bar_h * t
    body.append(f'<rect x="{bar_x}" y="{yy:.1f}" width="{bar_w}" '
                f'height="{bar_h/seg + 1:.1f}" fill="{move_color(mv)}" '
                f'stroke="none"/>')
body.append(f'<rect x="{bar_x}" y="{bar_y}" width="{bar_w}" height="{bar_h}" '
            f'fill="none" stroke="{GRAY}" stroke-width="1.2"/>')
for frac, lab in [(0.0, "+0.6 up"), (0.5, "no net move"), (1.0, "&#8722;0.6 down")]:
    yy = bar_y + bar_h * frac
    body.append(f'<text x="{bar_x+bar_w+10}" y="{yy+6:.1f}" '
                f'font-family="{FONT}" font-size="17" fill="{INK}">{lab}</text>')
# dead-band bracket
db_top = bar_y + bar_h * (0.5 - DEAD / (2 * CAP))
db_bot = bar_y + bar_h * (0.5 + DEAD / (2 * CAP))
body.append(f'<line x1="{bar_x-8}" y1="{db_top:.1f}" x2="{bar_x-8}" '
            f'y2="{db_bot:.1f}" stroke="{GRAY}" stroke-width="2"/>')
body.append(f'<text x="{bar_x-12}" y="{(db_top+db_bot)/2+5:.1f}" '
            f'font-family="{FONT}" font-size="13" fill="{GRAY}" '
            f'text-anchor="end">|move|&lt;0.15</text>')

# size legend
sz_y = bar_y + bar_h + 66
body.append(f'<text x="{LX}" y="{sz_y-20}" font-family="{FONT}" '
            f'font-size="17" fill="{INK}" font-weight="bold">dot size = '
            f'|move|</text>')
for i, mv in enumerate([0.1, 0.35, 0.6]):
    cx = LX + 24 + i * 78
    body.append(f'<circle cx="{cx}" cy="{sz_y+18}" r="{move_radius(mv):.1f}" '
                f'fill="none" stroke="{GRAY}" stroke-width="1.8"/>')
    body.append(f'<text x="{cx}" y="{sz_y+52}" font-family="{FONT}" '
                f'font-size="14" fill="{GRAY}" text-anchor="middle">'
                f'{mv:g}</text>')

# lens note (literal unicode; esc() only touches &,<,> so these pass through)
ln_y = sz_y + 92
lens = ("Selection pressure in the writeup's model is spread × agreement: "
        "each round nudges the value by about ρ·σ. The corners of "
        "this plane are where both dials are large — and where runs "
        "actually moved.")
for i, ll in enumerate(wrap(lens, 30)):
    body.append(f'<text x="{LX}" y="{ln_y + i*23}" font-family="{FONT}" '
                f'font-size="16.5" fill="{INK}">{esc(ll)}</text>')

# footer provenance (two lines to stay inside the canvas)
foot = ["Source: experiments/spread_util_unified.json &#8212; round-1 record "
        "per run key cond|seed|source; 74 runs total, 7 with undefined "
        "round-1 &#961; (zero spread) not plottable.",
        "Mixed pools also carry a supplier shift not shown on these two axes."]
for i, fl in enumerate(foot):
    body.append(f'<text x="{PL}" y="{H-34 + i*20}" font-family="{FONT}" '
                f'font-size="14.5" fill="{GRAY}">{fl}</text>')

svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
       f'font-family="{FONT}">\n<rect width="{W}" height="{H}" fill="white"/>\n'
       + "\n".join(body) + "\n</svg>\n")

with open(os.path.join(HERE, "synthesis-dial-plane.svg"), "w") as f:
    f.write(svg)
print(f"wrote synthesis-dial-plane.svg  ({len(RUNS)} runs plotted, "
      f"{N_SKIP} skipped, {N_RUNS} total)")
