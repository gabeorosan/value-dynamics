#!/usr/bin/env python3
"""control-arm-forecast — the program's first forward, out-of-time test of its
simple selection model.

A preregistered forecast (committed mid-run, before the runs finished) called
the supplier-removed control arms flat while the matched base-cogenerator run
eroded. This figure shows the forward call landing inside its band, plus the
per-cell stability check. Marks carry the story; the round-1 state, the three
pass-band definitions, and the instrument caveat live in caption.md.

House style copied from docs/figures/src/make_figures.py (palette + esc/wrap).
Stdlib only. Run from this directory:  python3 control-arm-forecast.py

Reads (asserted, never transcribed):
  experiments/control_arm_prospective_predictions.json      (the forecast)
  experiments/control_arm_forecast_score.json               (the scored outcome)
  experiments/olmo_insecure/output/
    olmo_code_security_static_reference_v1_analysis.json    (reference arm)
    olmo_code_security_self_pool_duels_v1_analysis.json     (self-duels arm)
    olmo_code_security_duel_loop_v2_analysis.json           (matched supplier run)
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
EXP = os.path.join(ROOT, "experiments")
OLMO = os.path.join(EXP, "olmo_insecure", "output")

# ---- palette (verbatim from make_figures.py) -----------------------------
INK = "#1a1a1a"
BLUE = "#2867b5"       # self-judge series (here: self-duels supplier-removed arm)
GREEN = "#3a7d44"      # frozen-judge series (here: reference-vs-secure arm)
RED = "#b5342c"        # emphasis for reversal / warning (matched eroding run)
GRAY = "#6b7684"       # recessive only (axes, muted captions) — never a series
KEY_FILL = "#eef5ee"
DOC_FILL = "#fdf6e8"
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


# ---- load + assert -------------------------------------------------------
def load(p):
    with open(p) as f:
        return json.load(f)


pred = load(os.path.join(EXP, "control_arm_prospective_predictions.json"))
score = load(os.path.join(EXP, "control_arm_forecast_score.json"))
ref = load(os.path.join(OLMO, "olmo_code_security_static_reference_v1_analysis.json"))
selfd = load(os.path.join(OLMO, "olmo_code_security_self_pool_duels_v1_analysis.json"))
v2 = load(os.path.join(OLMO, "olmo_code_security_duel_loop_v2_analysis.json"))


def traj(doc, seed, bank):
    r = doc["seeds"][seed]["readouts"][bank]
    return [r[k]["live_llm_mean_FLAGGED"] for k in
            ("organism_baseline", "organism_round_1",
             "organism_round_2", "organism_round_3")]


def approx(a, b, tol=1e-3):
    return abs(a - b) <= tol


# forecast (seed 71)
fc_in = pred["seeds"]["71"]["forecast"]["in_domain"]["predicted_trajectory"]
fc_out = pred["seeds"]["71"]["forecast"]["heldout"]["predicted_trajectory"]
assert fc_in == [0.854, 0.8463, 0.8386, 0.8309], fc_in
assert fc_out == [0.8412, 0.8335, 0.8258, 0.8181], fc_out
assert pred["seeds"]["71"]["round1_state"]["sigma1"] == 0.0595
assert pred["seeds"]["71"]["round1_state"]["rho1"] == -0.1706

# scored outcome
pa = score["P_A_reference_arm_seed71_in_domain"]
assert pa["predicted_endpoint"] == 0.8309
assert pa["observed_endpoint"] == 0.8597
assert pa["absolute_error"] == 0.0288
assert pa["band"] == 0.1 and pa["pass"] is True
assert score["s71_per_round_forecast_error"]["in_domain"]["mae"] == 0.025
assert score["verdict"] == {"P_A": True, "P_B": "7/8", "P_C": True,
                            "overall": "FORECAST HELD"}
pb = score["P_B_all_self_only_cells"]
assert pb["n_pass"] == 7 and pb["n_cells"] == 8
pc = score["P_C_head2head_self_round1_spread"]
assert pc["threshold"] == 0.15
assert pc["seeds"]["71"]["round1_sigma"] == 0.0595
assert pc["seeds"]["72"]["round1_sigma"] == 0.0506
assert pc["pass"] is True

# observed trajectories (seed 71 in-domain, the panel-A coordinate)
ref_in = traj(ref, "71", "in_domain")
self_in = traj(selfd, "71", "in_domain")
v2_in = traj(v2, "71", "in_domain")
assert approx(ref_in[0], 0.854) and approx(ref_in[3], 0.8597), ref_in
assert approx(self_in[3], 0.8476), self_in
assert approx(v2_in[3], 0.7276) and approx(v2_in[1], 0.7326), v2_in
# matched supplier-present run erodes 0.854 -> ~0.728 in-domain
assert v2_in[0] - v2_in[3] > 0.11

# the one P_B FAIL cell: reference arm, seed 71, held-out (0.070 vs 0.069)
fail = [c for c in pb["cells"] if not c["pass"]]
assert len(fail) == 1
fc = fail[0]
assert fc["arm"] == "reference_vs_secure" and fc["seed"] == "71" and fc["bank"] == "heldout"
assert round(fc["arm_abs_move"], 3) == 0.070 and round(fc["threshold_half_v2"], 3) == 0.069


# ---- svg helpers ---------------------------------------------------------
def T(x, y, s, size, color=INK, weight="normal", anchor="start", ls=None):
    a = f' text-anchor="{anchor}"' if anchor != "start" else ""
    l = f' letter-spacing="{ls}"' if ls else ""
    return (f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" '
            f'fill="{color}" font-weight="{weight}"{a}{l}>{esc(s)}</text>')


W, H = 1480, 900
body = [f'<rect width="{W}" height="{H}" fill="white"/>']

# ---- headline ------------------------------------------------------------
body.append(T(60, 64, "The preregistered forecast for the supplier-removed arms,",
              36, INK, "bold"))
body.append(T(60, 106, "scored against the observed runs", 36, INK, "bold"))
sub = ("OLMo-3 insecure-code organism · self-only control arms vs the matched "
       "base-cogenerator run · live frozen-base insecurity 0–1 · 3 rounds, 2 seeds.")
body.append(T(60, 140, sub, 19, GRAY))

# ==========================================================================
# PANEL A — the forward call (seed 71, in-domain)
# ==========================================================================
ax0, ax1 = 150, 620          # x pixels for rounds 0..3
ay0, ay1 = 210, 640          # y pixels: ay0 = top (vmax), ay1 = bottom (vmin)
vmax, vmin = 0.95, 0.58


def px(r):
    return ax0 + (ax1 - ax0) * r / 3.0


def py(v):
    return ay0 + (ay1 - ay0) * (vmax - v) / (vmax - vmin)


body.append(T(60, 188, "A", 22, INK, "bold"))

# y grid + axis
for gv in [0.6, 0.7, 0.8, 0.9]:
    yy = py(gv)
    body.append(f'<line x1="{ax0}" y1="{yy}" x2="{ax1}" y2="{yy}" '
                f'stroke="#e6e6e6" stroke-width="1"/>')
    body.append(T(ax0 - 12, yy + 5, f"{gv:.1f}", 15, GRAY, anchor="end"))
body.append(f'<line x1="{ax0}" y1="{ay0}" x2="{ax0}" y2="{ay1}" stroke="{GRAY}" stroke-width="1.5"/>')
body.append(f'<line x1="{ax0}" y1="{ay1}" x2="{ax1}" y2="{ay1}" stroke="{GRAY}" stroke-width="1.5"/>')
for r in range(4):
    lbl = "baseline" if r == 0 else f"round {r}"
    body.append(T(px(r), ay1 + 26, lbl, 15, GRAY, anchor="middle"))
# y title
body.append(f'<text x="70" y="{(ay0+ay1)/2}" font-family="{FONT}" font-size="16" '
            f'fill="{GRAY}" text-anchor="middle" transform="rotate(-90 70 {(ay0+ay1)/2})">'
            f'live frozen-base insecurity (0–1)</text>')

# forecast band: +-0.10 around predicted endpoint 0.8309, at round 3
bx = px(3)
btop, bbot = py(0.8309 + 0.10), py(0.8309 - 0.10)
body.append(f'<rect x="{bx-28}" y="{btop}" width="56" height="{bbot-btop}" '
            f'fill="{INK}" opacity="0.06"/>')
body.append(f'<line x1="{bx-28}" y1="{btop}" x2="{bx+28}" y2="{btop}" '
            f'stroke="{INK}" stroke-width="1.4" stroke-dasharray="4 3" opacity="0.5"/>')
body.append(f'<line x1="{bx-28}" y1="{bbot}" x2="{bx+28}" y2="{bbot}" '
            f'stroke="{INK}" stroke-width="1.4" stroke-dasharray="4 3" opacity="0.5"/>')
body.append(T(bx + 34, btop + 5, "±0.10 band", 13, GRAY, anchor="start"))


def polyline(vals, color, dash=False, wsw=3.4):
    pts = " ".join(f"{px(r):.1f},{py(v):.1f}" for r, v in enumerate(vals))
    d = ' stroke-dasharray="9 6"' if dash else ""
    return (f'<polyline points="{pts}" fill="none" stroke="{color}" '
            f'stroke-width="{wsw}"{d} stroke-linejoin="round" stroke-linecap="round"/>')


def dots(vals, color, r=5):
    return "".join(f'<circle cx="{px(i):.1f}" cy="{py(v):.1f}" r="{r}" '
                   f'fill="white" stroke="{color}" stroke-width="2.6"/>'
                   for i, v in enumerate(vals))


# matched base-cogenerator run (erodes) — RED
body.append(polyline(v2_in, RED))
body.append(dots(v2_in, RED))
# reference-vs-secure arm (flat) — GREEN
body.append(polyline(ref_in, GREEN))
body.append(dots(ref_in, GREEN))
# self-duels arm (flat) — BLUE (self-judge series color)
body.append(polyline(self_in, BLUE))
body.append(dots(self_in, BLUE))
# preregistered forecast for the reference arm — INK dashed
body.append(polyline(fc_in, INK, dash=True, wsw=2.6))

# observed endpoint marker inside band
oey = py(0.8597)
body.append(f'<circle cx="{bx:.1f}" cy="{oey:.1f}" r="7" fill="{GREEN}" stroke="white" stroke-width="2"/>')

# direct series labels — kept in the gap between Panel A's edge (620) and
# Panel B (starts at 780); shortened so no text crosses the panel boundary
lx = px(3) + 12          # 632
body.append(T(lx, py(ref_in[3]) - 8, "reference arm", 15, GREEN, "bold"))
body.append(T(lx, py(self_in[3]) + 34, "self-duels arm", 15, BLUE, "bold"))
body.append(T(lx, py(v2_in[3]) + 4, "matched run erodes", 15, RED, "bold"))
# forecast label in the open space below the dashed line
body.append(T(px(0.95), py(0.812), "forecast — committed mid-run", 14.5, INK, "bold"))
body.append(f'<line x1="{px(1.4)}" y1="{py(0.822)}" x2="{px(1.5)}" y2="{py(fc_in[1])+3}" '
            f'stroke="{INK}" stroke-width="1" opacity="0.6"/>')
# observed endpoint readout
body.append(T(px(2.02), py(0.762), "observed 0.860, error 0.029", 15, GREEN, "bold"))
body.append(f'<line x1="{px(2.72)}" y1="{py(0.77)}" x2="{bx-6}" y2="{oey+6}" '
            f'stroke="{GREEN}" stroke-width="1.2"/>')

# ==========================================================================
# PANEL B — all eight per-cell stability tests
# ==========================================================================
bx0 = 780
body.append(T(bx0, 188, "B", 22, INK, "bold"))
body.append(T(bx0 + 24, 188,
              "per-cell stability — bar = how far endpoint moved from baseline · "
              "▲ = half the matched run's move",
              15, GRAY))

# scale for the mini-bars
pbx0 = bx0 + 175          # bar origin x
pbxw = 300                # px for the axis span
smax = 0.14
def bs(v):
    return pbxw * v / smax

# axis ticks
axis_y = 232
for tv in [0.0, 0.05, 0.10]:
    xx = pbx0 + bs(tv)
    body.append(f'<line x1="{xx}" y1="{axis_y}" x2="{xx}" y2="{axis_y+430}" '
                f'stroke="#ededed" stroke-width="1"/>')
    body.append(T(xx, axis_y - 6, f"{tv:.2f}", 13, GRAY, anchor="middle"))

row_h = 52
top = axis_y + 8
cells = pb["cells"]
arm_color = {"reference_vs_secure": GREEN, "head2head_self": BLUE}
bank_name = {"in_domain": "in-domain", "heldout": "held-out"}

for i, c in enumerate(cells):
    ry = top + i * row_h
    col = arm_color[c["arm"]]
    lab = f"seed {c['seed']} · {bank_name[c['bank']]}"
    body.append(f'<rect x="{bx0}" y="{ry+12}" width="13" height="13" rx="3" fill="{col}"/>')
    body.append(T(bx0 + 22, ry + 23, lab, 14.5, INK))
    # move bar (color carries pass; green/blue fill = within threshold)
    mv = c["arm_abs_move"]
    bw = bs(mv)
    body.append(f'<rect x="{pbx0}" y="{ry+8}" width="{bw:.1f}" height="20" rx="4" '
                f'fill="{col}" opacity="0.9"/>')
    # threshold marker
    th = c["threshold_half_v2"]
    tx = pbx0 + bs(th)
    body.append(f'<line x1="{tx:.1f}" y1="{ry+2}" x2="{tx:.1f}" y2="{ry+34}" '
                f'stroke="{INK}" stroke-width="2.4"/>')
    body.append(f'<path d="M {tx-5:.1f} {ry+2} L {tx+5:.1f} {ry+2} L {tx:.1f} {ry+9} z" fill="{INK}"/>')
    if not c["pass"]:
        # the one cell over threshold — red-outlined bar + one short label
        body.append(f'<rect x="{pbx0}" y="{ry+8}" width="{bw:.1f}" height="20" rx="4" '
                     f'fill="none" stroke="{RED}" stroke-width="2.8"/>')
        body.append(T(pbx0 + pbxw + 20, ry + 24, "0.001 over", 15, RED, "bold"))

# ==========================================================================
# VERDICT STRIP — one line
# ==========================================================================
vy = 720
body.append(f'<rect x="60" y="{vy}" width="1360" height="56" rx="10" '
            f'fill="{KEY_FILL}" stroke="{GREEN}" stroke-width="2.5"/>')
body.append(T(84, vy + 36, "P-A pass · P-B 7/8 · P-C pass — forecast held",
              24, GREEN, "bold"))

# ---- honesty footnote ----------------------------------------------------
body.append(T(60, 816,
              "Live frozen-base coordinate; blind severity agrees in-domain, "
              "one held-out cell disagrees (caption).", 14, GRAY))

svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
       f'font-family="{FONT}">\n' + "\n".join(body) + "\n</svg>")

out = os.path.join(HERE, "control-arm-forecast.svg")
with open(out, "w") as f:
    f.write(svg)
print("wrote", out)
