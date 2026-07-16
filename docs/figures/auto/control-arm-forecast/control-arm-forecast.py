#!/usr/bin/env python3
"""control-arm-forecast — the program's first forward, out-of-time test of its
simple selection model.

A preregistered forecast (committed mid-run, before the runs finished) called
the supplier-removed control arms flat while the matched supplier-present run
eroded. This figure shows the forward call landing inside its band, plus the
per-cell stability check and the self-pool spread check.

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


W, H = 1480, 1140
body = [f'<rect width="{W}" height="{H}" fill="white"/>']

# ---- headline ------------------------------------------------------------
body.append(T(60, 66, "A preregistered forecast called the supplier-removed arms",
              37, INK, "bold"))
body.append(T(60, 110, "flat — and they were.", 37, INK, "bold"))
sub = ("OLMo-3 insecure-code organism · supplier-removed control arms "
       "(self-only pools) vs the matched supplier-present run · "
       "live frozen-base insecurity 0–1 · three training rounds.")
for i, ln in enumerate(wrap(sub, 96)):
    body.append(T(60, 150 + i * 26, ln, 19, GRAY))

# ==========================================================================
# PANEL A — the forward call (seed 71, in-domain)
# ==========================================================================
ax0, ax1 = 150, 640          # x pixels for rounds 0..3
ay0, ay1 = 250, 690          # y pixels: ay0 = top (vmax), ay1 = bottom (vmin)
vmax, vmin = 0.95, 0.58


def px(r):
    return ax0 + (ax1 - ax0) * r / 3.0


def py(v):
    return ay0 + (ay1 - ay0) * (vmax - v) / (vmax - vmin)


body.append(T(60, 210, "A.  The forward call — seed 71, in-domain bank",
              22, INK, "bold"))

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
body.append(T((ax0 + ax1) / 2, ay1 + 52, "training round", 16, GRAY, anchor="middle"))
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
body.append(T(bx, btop - 8, "±0.10 forecast band", 13, GRAY, anchor="middle"))


def polyline(vals, color, dash=False, wsw=3.4):
    pts = " ".join(f"{px(r):.1f},{py(v):.1f}" for r, v in enumerate(vals))
    d = ' stroke-dasharray="9 6"' if dash else ""
    return (f'<polyline points="{pts}" fill="none" stroke="{color}" '
            f'stroke-width="{wsw}"{d} stroke-linejoin="round" stroke-linecap="round"/>')


def dots(vals, color, r=5):
    return "".join(f'<circle cx="{px(i):.1f}" cy="{py(v):.1f}" r="{r}" '
                   f'fill="white" stroke="{color}" stroke-width="2.6"/>'
                   for i, v in enumerate(vals))


# matched supplier-present run (erodes) — RED
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

# line labels (right ends) — reference above, self-duels below, matched below
lx = px(3) + 20
body.append(T(lx, py(ref_in[3]) - 20, "reference arm", 14.5, GREEN, "bold"))
body.append(T(lx, py(ref_in[3]) - 5, "(supplier removed) flat", 12.5, GREEN))
body.append(T(lx, py(self_in[3]) + 30, "self-duels arm", 14.5, BLUE, "bold"))
body.append(T(lx, py(self_in[3]) + 45, "(supplier removed) flat", 12.5, BLUE))
body.append(T(lx, py(v2_in[3]) - 4, "matched supplier-", 14.5, RED, "bold"))
body.append(T(lx, py(v2_in[3]) + 12, "present run erodes", 14.5, RED, "bold"))
body.append(T(lx, py(v2_in[3]) + 28, "0.854 → 0.728", 12.5, RED))
# forecast label near round 2
body.append(T(px(1.5), py(fc_in[2]) + 26, "preregistered forecast", 14, INK, "bold"))
body.append(T(px(1.5), py(fc_in[2]) + 44, "0.854 → 0.831 (dashed)", 13, GRAY))

# error annotation — callout into open lower-mid plot
body.append(T(px(2.15), py(0.795) + 4, "observed 0.860 · error 0.029", 14, GREEN, "bold"))
body.append(f'<line x1="{px(2.55)}" y1="{py(0.80)}" x2="{bx-6}" y2="{oey+4}" '
            f'stroke="{GREEN}" stroke-width="1.2"/>')

# committed-mid-flight note box
nb_y = 720
note = ("Forecast committed while these runs were still mid-flight — "
        "predicted flat (about a fifth of the matched erosion) from the "
        "round-1 spread of candidate insecurity, 0.060, and the "
        "generator–judge agreement, −0.17, alone. Per-round forecast "
        "error on this bank: mean 0.025.")
body.append(f'<rect x="60" y="{nb_y}" width="640" height="132" rx="8" '
            f'fill="{DOC_FILL}" stroke="{INK}" stroke-width="1.5"/>')
for i, ln in enumerate(wrap(note, 66)):
    body.append(T(78, nb_y + 28 + i * 22, ln, 15, INK))

# ==========================================================================
# PANEL B — all eight per-cell stability tests
# ==========================================================================
bx0 = 780
body.append(T(bx0, 210, "B.  Per-cell stability — absolute move vs its threshold",
              22, INK, "bold"))
body.append(T(bx0, 236, "move = endpoint − baseline; threshold = half the matched run's move on that cell",
              15, GRAY))

# scale for the mini-bars
pbx0 = bx0 + 185          # bar origin x
pbxw = 300                # px for the axis span
smax = 0.14
def bs(v):
    return pbxw * v / smax

# axis ticks
axis_y = 268
for tv in [0.0, 0.05, 0.10]:
    xx = pbx0 + bs(tv)
    body.append(f'<line x1="{xx}" y1="{axis_y}" x2="{xx}" y2="{axis_y+430}" '
                f'stroke="#ededed" stroke-width="1"/>')
    body.append(T(xx, axis_y - 6, f"{tv:.2f}", 13, GRAY, anchor="middle"))

row_h = 52
top = axis_y + 8
cells = pb["cells"]
arm_color = {"reference_vs_secure": GREEN, "head2head_self": BLUE}
arm_name = {"reference_vs_secure": "reference-vs-secure", "head2head_self": "self-duels"}
bank_name = {"in_domain": "in-domain", "heldout": "held-out"}

for i, c in enumerate(cells):
    ry = top + i * row_h
    col = arm_color[c["arm"]]
    lab = f"seed {c['seed']} · {bank_name[c['bank']]}"
    body.append(f'<rect x="{bx0}" y="{ry+12}" width="13" height="13" rx="3" fill="{col}"/>')
    body.append(T(bx0 + 22, ry + 23, lab, 14.5, INK))
    # move bar
    mv = c["arm_abs_move"]
    bw = bs(mv)
    body.append(f'<rect x="{pbx0}" y="{ry+8}" width="{bw:.1f}" height="20" rx="4" '
                f'fill="{col}" opacity="0.9"/>')
    # threshold marker (gray tick)
    th = c["threshold_half_v2"]
    tx = pbx0 + bs(th)
    body.append(f'<line x1="{tx:.1f}" y1="{ry+2}" x2="{tx:.1f}" y2="{ry+34}" '
                f'stroke="{INK}" stroke-width="2.4"/>')
    body.append(f'<path d="M {tx-5:.1f} {ry+2} L {tx+5:.1f} {ry+2} L {tx:.1f} {ry+9} z" fill="{INK}"/>')
    # verdict
    if c["pass"]:
        body.append(T(pbx0 + pbxw + 24, ry + 24, "✓ pass", 15, GREEN, "bold"))
    else:
        # the one FAIL — draw its bar outlined red and call it out
        body.append(f'<rect x="{pbx0}" y="{ry+8}" width="{bw:.1f}" height="20" rx="4" '
                     f'fill="none" stroke="{RED}" stroke-width="2.6"/>')
        body.append(T(pbx0 + pbxw + 24, ry + 18, "over by 0.001", 14, RED, "bold"))
        body.append(T(pbx0 + pbxw + 24, ry + 35, "0.070 vs 0.069", 13.5, RED))

# panel B legend
lg_y = top + 8 * row_h + 24
body.append(f'<rect x="{bx0}" y="{lg_y}" width="16" height="16" rx="3" fill="{GREEN}"/>')
body.append(T(bx0 + 24, lg_y + 13, "reference-vs-secure arm", 14, INK))
body.append(f'<rect x="{bx0+250}" y="{lg_y}" width="16" height="16" rx="3" fill="{BLUE}"/>')
body.append(T(bx0 + 274, lg_y + 13, "self-duels arm", 14, INK))
body.append(f'<line x1="{bx0+8}" y1="{lg_y+38}" x2="{bx0+8}" y2="{lg_y+56}" stroke="{INK}" stroke-width="2.4"/>')
body.append(T(bx0 + 24, lg_y + 52, "▲ threshold (half the matched eroding move)", 14, INK))

# ==========================================================================
# VERDICT STRIP
# ==========================================================================
vy = 884
body.append(f'<rect x="60" y="{vy}" width="640" height="150" rx="10" '
            f'fill="{KEY_FILL}" stroke="{GREEN}" stroke-width="2.5"/>')
body.append(T(80, vy + 34, "Verdict — forecast held", 21, GREEN, "bold"))
lines = [
    ("P-A  forecast band:", "observed endpoint 0.860 inside the ±0.10 band around 0.831 — PASS"),
    ("P-B  per-cell stability:", "7 of 8 supplier-removed cells moved less than half the matched run — PASS"),
    ("P-C  self-pool spread:", "round-1 kept-insecurity spread 0.060 / 0.051 < 0.15, as predicted — PASS"),
]
for i, (a, b) in enumerate(lines):
    yy = vy + 66 + i * 26
    body.append(T(80, yy, a, 15, INK, "bold"))
    body.append(T(248, yy, b, 15, INK))

# ---- honesty footnote ----------------------------------------------------
fy = 1052
foot = ("Instrument: live frozen-base coordinate (the declared readout; a flagged, "
        "low-specificity diagnostic). Blind manual severity agrees in-domain — the "
        "control arms average about +0.02 vs the matched run's −0.15 / −0.29 — "
        "with one discordant cell: the reference arm's seed-71 held-out bank fell "
        "−0.28 on manual severity while its live coordinate moved only 0.07. "
        "n = 2 arms × 2 seeds, one organism family: one passed forward test, not a forecasting record.")
for i, ln in enumerate(wrap(foot, 132)):
    body.append(T(60, fy + i * 20, ln, 13.5, GRAY))

svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
       f'font-family="{FONT}">\n' + "\n".join(body) + "\n</svg>")

out = os.path.join(HERE, "control-arm-forecast.svg")
with open(out, "w") as f:
    f.write(svg)
print("wrote", out)
