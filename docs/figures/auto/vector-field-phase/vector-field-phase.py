#!/usr/bin/env python3
"""Phase plot of round-to-round value change against current value, risk-axis
runs, overlaid with the model's rho * sigma_max(v) envelope field
(slug: vector-field-phase).

One dot per round-to-round transition inside a risk-axis run.  For every pair of
consecutive rounds (round r, round r+1) inside a run we plot:

    x = value at round r                       (behavioral value v, 0..1)
    y = value at round r+1  minus  value at round r      (observed one-round change)
    color = agreement rho measured at round r  (diverging: red positive,
            blue negative, gray near zero; light neutral gray if rho undefined)

The transition convention matches the observed() helper of
spread-rollout-bakeoff.py: that helper builds the observed path as
[value_1, value_1 + drift_1, value_2 + drift_2, ...], and in this file the
per-record drift equals value_{r+1} - value_r to within 1e-4, so drift is the
realized one-round change.  We recompute the change directly from consecutive
rounds' value fields so nothing depends on the drift field.

THE FIELD (analytic, not fitted).  On the binary risk axis the within-prompt
candidate spread has the Bernoulli envelope sigma_max(v) = sqrt(v * (1 - v)):
for a self-only pool the largest one-round move the selector can produce at
value v is rho * sigma_max(v).  We draw that model as light envelope curves for
rho = +1, +0.5, -0.5, -1 (a lens that is widest mid-range and pinched to zero at
the walls v = 0 and v = 1), a bold zero line (no move), and the two walls.

Palette + esc()/wrap() copied from docs/figures/src/make_figures.py (house style).
Stdlib only.  Regenerate with:  python3 vector-field-phase.py
"""
import json
import math
import os
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
EXP = os.path.join(HERE, "..", "..", "..", "..", "experiments")
UNIFIED = os.path.join(EXP, "spread_util_unified.json")

# ---- palette (house style; make_figures.py constants) --------------------
INK = "#1a1a1a"
BLUE = "#2867b5"        # negative agreement pole
GREEN = "#3a7d44"
RED = "#b5342c"         # positive agreement pole
GRAY = "#6b7684"        # diverging midpoint / recessive ink
FAINT = "#e4e4e0"
KEY_FILL = "#eef5ee"
POS_ENV = "#d79992"     # light red tint (positive envelope curves)
NEG_ENV = "#9fbbe0"     # light blue tint (negative envelope curves)
UNDEF = "#c2c6cc"       # rho undefined
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


def txt(x, y, s, size=18, color=INK, weight="normal", anchor="start"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{FONT}" '
            f'font-size="{size}" fill="{color}" font-weight="{weight}" '
            f'text-anchor="{anchor}">{esc(s)}</text>')


def rect(x, y, w, h, fill, stroke="none", sw=0, rx=0):
    st = f' stroke="{stroke}" stroke-width="{sw}"' if stroke != "none" else ""
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" '
            f'rx="{rx}" fill="{fill}"{st}/>')


def line(x1, y1, x2, y2, color, sw=1.0, dash=None, opacity=1.0):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    o = f' stroke-opacity="{opacity}"' if opacity != 1.0 else ""
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{sw}"{d}{o}/>')


def polyline(pts, color, sw, dash=None, opacity=1.0):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    o = f' stroke-opacity="{opacity}"' if opacity != 1.0 else ""
    p = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    return (f'<polyline points="{p}" fill="none" stroke="{color}" '
            f'stroke-width="{sw}"{d}{o} stroke-linejoin="round"/>')


# ---- diverging rho -> color ----------------------------------------------
def _rgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


def _hex(rgb):
    return "#" + "".join(f"{max(0, min(255, int(round(c)))):02x}" for c in rgb)


def _lerp(c1, c2, t):
    a, b = _rgb(c1), _rgb(c2)
    return _hex(tuple(a[i] + (b[i] - a[i]) * t for i in range(3)))


def rho_color(rho):
    if rho is None:
        return UNDEF
    r = max(-1.0, min(1.0, rho))
    if r >= 0:
        return _lerp(GRAY, RED, r)
    return _lerp(GRAY, BLUE, -r)


# ======================================================================
# read data + build every risk-axis round-to-round transition (live)
# ======================================================================
with open(UNIFIED) as f:
    RECORDS = json.load(f)["records"]


def run_key(r):
    return (r["cond"], r["seed"], r["source"])


_groups = defaultdict(list)
for _r in RECORDS:
    if _r.get("axis") == "risk":
        _groups[run_key(_r)].append(_r)
RUNS = {k: sorted(v, key=lambda r: r["round"]) for k, v in _groups.items()}

# transitions: (v_at_r, delta_v, rho_at_r)
TRANS = []
n_runs = 0
n_undef = 0
n_over = 0
for k, rows in RUNS.items():
    by = {r["round"]: r for r in rows}
    used = False
    for t in sorted(by):
        if t + 1 in by:
            used = True
            v = by[t]["value"]
            dv = by[t + 1]["value"] - by[t]["value"]
            rho = by[t]["rho"]
            TRANS.append((v, dv, rho))
            if rho is None:
                n_undef += 1
            if abs(dv) > math.sqrt(max(0.0, v * (1.0 - v))) + 1e-6:
                n_over += 1
    if used:
        n_runs += 1

N = len(TRANS)
print(f"risk-axis runs used: {n_runs}   transitions plotted: {N}   "
      f"(rho undefined at round r: {n_undef};  moves beyond self-only "
      f"envelope: {n_over})")


# ======================================================================
# geometry
# ======================================================================
W, H = 1240, 812
PLOT_LEFT = 112
PLOT_RIGHT = 1102
PLOT_TOP = 176
PLOT_BOT = 664
PLOT_W = PLOT_RIGHT - PLOT_LEFT
YMAX = 0.8   # symmetric Delta-v range, zero centred


def X(v):
    return PLOT_LEFT + v * PLOT_W


def Y(dv):
    return PLOT_TOP + (YMAX - dv) / (2 * YMAX) * (PLOT_BOT - PLOT_TOP)


def sigma(v):
    return math.sqrt(max(0.0, v * (1.0 - v)))


S = []

# ---- headline ------------------------------------------------------------
S.append(txt(PLOT_LEFT - 68, 50,
             "Round-to-round value change vs current value, risk-axis runs, "
             "with the model's rho · sigma_max(v) envelopes",
             22, INK, "bold"))
S.append(txt(PLOT_LEFT - 68, 80,
             "One dot = one round → next-round transition inside a "
             "risk-axis run.  x = value v at round r;  y = value at round r+1 "
             "minus value at round r.",
             15, GRAY))
S.append(txt(PLOT_LEFT - 68, 102,
             "sigma_max(v) = sqrt(v(1−v)) is the Bernoulli spread envelope; "
             "rho is the selector–value agreement measured at round r.",
             15, GRAY))

# ---- rho color legend (gradient bar) -------------------------------------
lg_x = PLOT_LEFT - 68
lg_y = 128
lg_w = 300
lg_h = 14
S.append('<defs><linearGradient id="rhoramp" x1="0" y1="0" x2="1" y2="0">'
         f'<stop offset="0" stop-color="{BLUE}"/>'
         f'<stop offset="0.5" stop-color="{GRAY}"/>'
         f'<stop offset="1" stop-color="{RED}"/>'
         '</linearGradient></defs>')
S.append(f'<rect x="{lg_x}" y="{lg_y}" width="{lg_w}" height="{lg_h}" rx="3" '
         f'fill="url(#rhoramp)"/>')
S.append(txt(lg_x, lg_y - 8, "agreement rho at round r", 14, INK, "bold"))
S.append(txt(lg_x, lg_y + lg_h + 16, "−1 (blue)", 13, GRAY))
S.append(txt(lg_x + lg_w / 2, lg_y + lg_h + 16, "0", 13, GRAY, anchor="middle"))
S.append(txt(lg_x + lg_w, lg_y + lg_h + 16, "+1 (red)", 13, GRAY, anchor="end"))
# undefined swatch
ud_x = lg_x + lg_w + 46
S.append(f'<circle cx="{ud_x + 7}" cy="{lg_y + 7}" r="7" fill="{UNDEF}" '
         f'stroke="white" stroke-width="1.5"/>')
S.append(txt(ud_x + 20, lg_y + 12, "rho undefined", 14, INK))
# envelope legend
ev_x = ud_x + 150
S.append(line(ev_x, lg_y + 2, ev_x + 30, lg_y + 2, POS_ENV, 2.6))
S.append(line(ev_x, lg_y + 12, ev_x + 30, lg_y + 12, NEG_ENV, 2.6))
S.append(txt(ev_x + 38, lg_y + 12,
             "envelope y = rho · sigma_max(v)  (self-only max move)",
             14, INK))

# ======================================================================
# plot frame + gridlines
# ======================================================================
# y gridlines
for gv in (0.8, 0.4, 0.0, -0.4, -0.8):
    gy = Y(gv)
    is0 = (gv == 0.0)
    S.append(line(PLOT_LEFT, gy, PLOT_RIGHT, gy, INK if is0 else FAINT,
                  2.4 if is0 else 1.0))
    lbl = "0" if is0 else f"{gv:+.1f}"
    S.append(txt(PLOT_LEFT - 12, gy + 5, lbl, 14,
                 INK if is0 else GRAY, "bold" if is0 else "normal",
                 anchor="end"))
# x gridlines
for gv in (0.0, 0.25, 0.5, 0.75, 1.0):
    gx = X(gv)
    wall = (gv == 0.0 or gv == 1.0)
    S.append(line(gx, PLOT_TOP, gx, PLOT_BOT, GRAY if wall else FAINT,
                  1.4 if wall else 1.0, dash="4 5" if wall else None,
                  opacity=0.8 if wall else 1.0))
    S.append(txt(gx, PLOT_BOT + 24, f"{gv:g}", 14, GRAY, anchor="middle"))

# wall labels
S.append(txt(X(0.0) + 6, PLOT_TOP + 16, "wall  v = 0", 13, GRAY))
S.append(txt(X(1.0) - 6, PLOT_TOP + 16, "wall  v = 1", 13, GRAY, anchor="end"))

# axis titles
S.append(txt((PLOT_LEFT + PLOT_RIGHT) / 2, PLOT_BOT + 52,
             "value v at round r", 17, INK, "bold", anchor="middle"))
S.append(f'<text x="{PLOT_LEFT - 74}" y="{(PLOT_TOP + PLOT_BOT) / 2:.1f}" '
         f'font-family="{FONT}" font-size="17" fill="{INK}" font-weight="bold" '
         f'text-anchor="middle" transform="rotate(-90 {PLOT_LEFT - 74} '
         f'{(PLOT_TOP + PLOT_BOT) / 2:.1f})">observed one-round change  '
         f'value(r+1) − value(r)</text>')

# ======================================================================
# recessive flow cue: faint up/down ticks scaled by sigma(v)
# ======================================================================
for gv in (0.15, 0.30, 0.50, 0.70, 0.85):
    gx = X(gv)
    span = 0.5 * sigma(gv)   # a representative rho = +/-0.5 move
    yb = Y(0.0)
    yu = Y(span)
    yd = Y(-span)
    S.append(line(gx, yb, gx, yu, POS_ENV, 2.0, opacity=0.45))
    S.append(f'<path d="M {gx:.1f} {yu - 6:.1f} l -3.5 6 l 7 0 z" '
             f'fill="{POS_ENV}" fill-opacity="0.45"/>')
    S.append(line(gx, yb, gx, yd, NEG_ENV, 2.0, opacity=0.45))
    S.append(f'<path d="M {gx:.1f} {yd + 6:.1f} l -3.5 -6 l 7 0 z" '
             f'fill="{NEG_ENV}" fill-opacity="0.45"/>')

# ======================================================================
# envelope curves y = rho * sigma_max(v)
# ======================================================================
SAMP = [i / 240.0 for i in range(241)]
ENV = [(1.0, POS_ENV, 2.6, "rho = +1"),
       (0.5, POS_ENV, 1.8, "rho = +0.5"),
       (-0.5, NEG_ENV, 1.8, "rho = −0.5"),
       (-1.0, NEG_ENV, 2.6, "rho = −1")]
for rho, col, sw, lab in ENV:
    pts = [(X(v), Y(rho * sigma(v))) for v in SAMP]
    S.append(polyline(pts, col, sw))
    # leader + label at v = 0.9
    vl = 0.9
    yl = rho * sigma(vl)
    lx = X(vl)
    S.append(line(lx, Y(yl), PLOT_RIGHT + 8, Y(yl), col, 1.2, opacity=0.9))
    S.append(txt(PLOT_RIGHT + 12, Y(yl) + 4, lab, 13,
                 RED if rho > 0 else BLUE))

# ======================================================================
# the transition dots (drawn on top)
# ======================================================================
for v, dv, rho in TRANS:
    cx, cy = X(v), Y(max(-YMAX, min(YMAX, dv)))
    S.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="5.2" '
             f'fill="{rho_color(rho)}" fill-opacity="0.9" '
             f'stroke="white" stroke-width="1.4"/>')

# ---- footnote ------------------------------------------------------------
fy = PLOT_BOT + 82
S.append(txt(PLOT_LEFT - 68, fy,
             f"{N} round-to-round transitions from {n_runs} risk-axis runs "
             f"(axis == \"risk\"); {n_undef} have undefined rho at round r "
             f"(shown gray); {n_over} realized moves fall beyond the self-only "
             f"envelope.",
             13, GRAY))
S.append(txt(PLOT_LEFT - 68, fy + 18,
             "All transitions computed live from "
             "experiments/spread_util_unified.json (per-round value fields); "
             "envelopes are analytic.  Generator: vector-field-phase.py",
             13, GRAY))

svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
       f'font-family="{FONT}">\n'
       f'<rect width="{W}" height="{H}" fill="white"/>\n'
       + "\n".join(S) + "\n</svg>")

out = os.path.join(HERE, "vector-field-phase.svg")
with open(out, "w") as f:
    f.write(svg)
print(f"wrote {out}  viewBox 0 0 {W} {H}")
