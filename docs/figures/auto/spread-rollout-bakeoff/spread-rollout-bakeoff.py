#!/usr/bin/env python3
"""Closed-loop rollout bake-off figure (slug: spread-rollout-bakeoff).

A value-dynamics simulator is fit on other runs, then observes ONLY a held-out
run's FIRST-round pool state and rolls the whole trajectory forward without
reading that run's later candidates, spread, agreement, or value. Validation is
leave-one-CONDITION-out (LOCO): the entire intervention/judge regime is held out.

Panel A: endpoint MAE by regime, the frozen mean-SD conditional-mean model vs a
         no-change baseline; plus an inset showing that restarting the rollout at
         a mid-run judge change repairs the one regime where round-1 rollout loses.
Panel B: for the 45 selection-driven + judge-swap runs, the coarse deterministic
         mean model reproduces endpoint behaviour but is too smooth, while a
         staged stochastic model with separately located innovations restores
         realistic measured paths and useful endpoint uncertainty.

Every displayed number is read from the committed JSONs (json.load) at the exact
paths below and asserted against expected values; nothing is transcribed.
Palette + esc()/wrap() copied from docs/figures/src/make_figures.py (house style).

Regenerate with:  python3 spread-rollout-bakeoff.py
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
EXP = os.path.join(HERE, "..", "..", "..", "..", "experiments")
BAKEOFF = os.path.join(EXP, "spread_rollout_bakeoff.json")
FIDELITY = os.path.join(EXP, "rollout_property_fidelity.json")
STAGED = os.path.join(EXP, "trajectory_adjustment_bakeoff.json")

# ---- palette (house style; make_figures.py constants) --------------------
INK = "#1a1a1a"
BLUE = "#2867b5"        # the spread model's closed-loop forecast (self-judge accent)
GREEN = "#3a7d44"       # frozen conditional-mean path / the repaired restart
RED = "#b5342c"         # reversal / out-of-scope warning
GRAY = "#6b7684"        # recessive: axes, baselines, muted text
USER_FILL = "#cfe0f1"
ASST_FILL = "#eaf1f8"   # light-blue highlight band
DOC_FILL = "#fdf6e8"
KEY_FILL = "#eef5ee"    # light-green takeaway band
OOS_FILL = "#f7e6e4"    # light-red out-of-scope tint
FAINT = "#e4e4e0"

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


def line(x1, y1, x2, y2, color, sw=1.0, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{sw}"{d}/>')


def circle(cx, cy, r, fill, stroke="white", sw=2):
    return (f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r}" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="{sw}"/>')


# ======================================================================
# read + verify data
# ======================================================================
with open(BAKEOFF) as f:
    BK = json.load(f)
with open(FIDELITY) as f:
    FD = json.load(f)
with open(STAGED) as f:
    ST = json.load(f)

SD_KEY = "mean_within_prompt_population_sd"
FROZEN = BK["validations"]["leave_one_condition_out"]["frozen"][SD_KEY][
    "aggregates"]


def frozen_row(key):
    n = FROZEN[key]
    return (n["behavioral_value_endpoint"]["mae"],
            n["behavioral_value_endpoint_persistence"]["mae"],
            n["n_runs"])


# ---- Panel A: per-regime frozen mean-SD model vs no-change ----------------
# (label, json key, expected model MAE, expected no-change MAE, n, out_of_scope)
PANEL_A = [
    ("selection-driven", "selection_driven", 0.127, 0.431, 36, False),
    ("mixed interventions", "intervention", 0.112, 0.450, 24, False),
    ("strong-agreement self-only", "self_force", 0.157, 0.393, 12, False),
    ("weak self-only selection", "self_weak", 0.205, 0.215, 22, False),
    ("judge swaps, rolled from original round 1", "judge_swap",
     0.404, 0.361, 9, True),
]
a_rows = []
for label, key, exp_m, exp_b, exp_n, oos in PANEL_A:
    m, b, n = frozen_row(key)
    assert round(m, 3) == exp_m, (label, "model", m, exp_m)
    assert round(b, 3) == exp_b, (label, "baseline", b, exp_b)
    assert n == exp_n, (label, "n", n, exp_n)
    a_rows.append((label, m, b, n, oos))

# ---- judge-swap refresh inset (frozen mean-SD, remeasured at new-judge pool)
# Use the FROZEN mean-SD node so the inset matches Panel A's headline model.
REF = BK["judge_swap_refresh"]["leave_one_condition_out"]["mean_sd_frozen"][
    "aggregate"]
REF_END = REF["endpoint"]
REF_BLIND = REF_END["closed_from_round1"]["mae"]        # 0.404
REF_HOLD = REF_END["persistence_from_swap"]["mae"]      # 0.309
REF_RESTART = REF_END["refreshed_at_swap"]["mae"]       # 0.179
assert round(REF_BLIND, 3) == 0.404, REF_BLIND
assert round(REF_HOLD, 3) == 0.309, REF_HOLD
assert round(REF_RESTART, 3) == 0.179, REF_RESTART
rdir = REF["direction_from_swap_on_runs_moving_at_least_0_15"]
REF_HITS, REF_MOVED = rdir["n_hits"], rdir["n_moved"]
assert (REF_HITS, REF_MOVED) == (6, 7), (REF_HITS, REF_MOVED)
REF_N = REF_END["closed_from_round1"]["n"]
assert REF_N == 9, REF_N

# ---- Panel B: deterministic mean model vs staged stochastic model ---------
DET = ST["primary_selection_driven_plus_swap"]["deterministic_frozen"]
STG = ST["primary_selection_driven_plus_swap"][
    "selector_q_observation_rho_persistence_gaussian"]
assert DET["n_runs"] == 45 and STG["n_runs"] == 45

FID = FD["models"]["frozen_mean_sd"]["selection_driven_plus_swap"]
FID_SHAPE = FID["aggregate_shape"]

# observed / deterministic / staged path-realism properties
OBS_TV = FID_SHAPE["observed_mean_total_variation"]
DET_TV = FID_SHAPE["predicted_mean_total_variation"]
STG_TV = STG["aggregate_path_properties"]["total_variation"]["simulated"]
assert round(OBS_TV, 3) == 0.648 and round(DET_TV, 3) == 0.458
assert round(STG_TV, 3) == 0.678, STG_TV

OBS_SR = FID_SHAPE["observed_mean_sign_changes"]
DET_SR = FID_SHAPE["predicted_mean_sign_changes"]
STG_SR = STG["aggregate_path_properties"]["sign_changes"]["simulated"]
assert round(OBS_SR, 2) == 1.20 and round(DET_SR, 2) == 0.16
assert round(STG_SR, 2) == 1.36, STG_SR

# endpoint uncertainty scores (no "observed" target)
DET_CRPS = DET["endpoint_crps"]
STG_CRPS = STG["endpoint_crps"]
assert round(DET_CRPS, 3) == 0.137 and round(STG_CRPS, 3) == 0.095
DET_COV = DET["endpoint_80pct_coverage"]
STG_COV = STG["endpoint_80pct_coverage"]
assert round(DET_COV, 2) == 0.02 and round(STG_COV, 2) == 0.84

# coarse deterministic fidelity annotations
LM = FID["large_movement_direction"]
LM_HITS, LM_N = LM["hits"], LM["n"]
assert (LM_HITS, LM_N) == (36, 38)
RAIL = FID["observed_rail_endpoint_recall"]
RAIL_HITS, RAIL_N = RAIL["hits"], RAIL["n"]
assert (RAIL_HITS, RAIL_N) == (19, 24)
END_PRED_MEAN = FID_SHAPE["predicted_endpoint_mean"]
END_OBS_MEAN = FID_SHAPE["observed_endpoint_mean"]
END_PRED_SD = FID_SHAPE["predicted_endpoint_sd"]
END_OBS_SD = FID_SHAPE["observed_endpoint_sd"]
assert round(END_PRED_MEAN, 3) == 0.572 and round(END_OBS_MEAN, 3) == 0.541
assert round(END_PRED_SD, 3) == 0.360 and round(END_OBS_SD, 3) == 0.370

# spread-definition robustness footnote
SIM = FD["model_prediction_similarity"]
DEF_DIFF = SIM["mean_absolute_endpoint_prediction_difference"]
DEF_CLASS_N = SIM["same_predicted_endpoint_class"]["n"]
DEF_COMMON = SIM["n_common_runs"]
assert round(DEF_DIFF, 4) == 0.0066 and (DEF_CLASS_N, DEF_COMMON) == (66, 67)


# ======================================================================
# build the SVG
# ======================================================================
W = 1240
LEFT = 40
S = []

# ---- headline finding + one method line ----------------------------------
y = 50
S.append(txt(LEFT, y,
             "A first-pool spread model predicts where an unseen condition "
             "lands; separate noise restores how the path wanders",
             25, INK, "bold"))
y += 32
for ln in wrap("Fit on other runs, the simulator observes only the held-out "
               "condition's FIRST pool, holds spread fixed, and rolls the "
               "selection/update equations forward — reading none of that "
               "run's later candidates, spread, agreement, or value. Validation "
               "is leave-one-condition-out: the entire intervention / judge "
               "regime is held out. Endpoint MAE = mean absolute error of the "
               "predicted final behavioural value vs the true final value, on "
               "the 0-1 scale; lower is better.", 122):
    S.append(txt(LEFT, y, ln, 16, GRAY))
    y += 21

# ==================== PANEL A ====================
y += 22
S.append(txt(LEFT, y, "A", 28, INK, "bold"))
S.append(txt(LEFT + 32, y,
             "Does the closed loop predict an unseen condition from its "
             "first pool?", 22, INK, "bold"))
y += 25
for ln in wrap("Endpoint MAE per regime: the frozen mean within-prompt "
               "population-SD model (rolled forward from round 1) vs a no-change "
               "baseline that predicts the round-1 value forever. It wins in "
               "every selection and intervention regime, and ties the weak "
               "self-only regime that barely moves.", 122):
    S.append(txt(LEFT, y, ln, 16, GRAY))
    y += 21

# bar axis (shared endpoint-MAE scale across Panel A)
AX0 = 452
AW = 560
MAXA = 0.47
scale_a = AW / MAXA


def bar_axis(top, bottom, label=True):
    for g in (0.0, 0.1, 0.2, 0.3, 0.4):
        gx = AX0 + g * scale_a
        S.append(line(gx, top, gx, bottom, INK if g == 0 else FAINT,
                      2 if g == 0 else 1.1))
        if label:
            S.append(txt(gx, bottom + 22, f"{g:g}", 16, GRAY, anchor="middle"))


# legend
y += 12
S.append(rect(AX0, y - 13, 26, 16, BLUE, rx=3))
S.append(txt(AX0 + 34, y, "first-pool spread model — rolls forward "
             "from round 1", 17, INK))
y += 24
S.append(rect(AX0, y - 13, 26, 16, GRAY, rx=3))
S.append(txt(AX0 + 34, y, "no-change baseline — predicts the round-1 "
             "value forever", 17, INK))

# rows
y += 20
ROW_H = 64
a_top = y
# gridlines span the four in-scope rows
grid_bottom_a = a_top + 4 * ROW_H - 8
bar_axis(a_top - 4, grid_bottom_a)

for label, m, b, n, oos in a_rows:
    if oos:
        continue
    bt = y
    S.append(txt(LEFT, bt + 16, label, 18, INK, "bold"))
    S.append(txt(LEFT, bt + 37, f"n = {n} runs", 15, GRAY))
    # model bar
    mw = m * scale_a
    S.append(rect(AX0, bt + 2, mw, 20, BLUE, rx=3))
    S.append(txt(AX0 + mw + 8, bt + 18, f"{m:.3f}", 17, BLUE, "bold"))
    # baseline bar
    bw = b * scale_a
    S.append(rect(AX0, bt + 26, bw, 20, GRAY, rx=3))
    S.append(txt(AX0 + bw + 8, bt + 42, f"{b:.3f}", 17, GRAY, "bold"))
    y += ROW_H

S.append(txt(AX0 + AW / 2, grid_bottom_a + 48,
             "endpoint MAE (predicted minus true final value, absolute) "
             "— lower is better", 16, INK, anchor="middle"))

# ---- out-of-scope judge-swap block (the problem) -------------------------
y = grid_bottom_a + 72
rbox_top = y
rbox_h = 132
S.append(rect(28, rbox_top, W - 56, rbox_h, OOS_FILL, stroke=RED, sw=1.6,
              rx=12))
yb = rbox_top + 28
S.append(txt(LEFT + 8, yb, "Out of scope from round 1: a mid-run judge change",
             19, RED, "bold"))
yb += 23
for ln in wrap("When the judge is swapped mid-run, the round-1 rollout cannot "
               "see the new judge's scale, so it loses to no-change — the "
               "only regime where the model is beaten.", 120):
    S.append(txt(LEFT + 8, yb, ln, 15, INK))
    yb += 20

jlabel, jm, jb, jn, _ = a_rows[-1]
jy = yb + 4
for g in (0.0, 0.1, 0.2, 0.3, 0.4):
    gx = AX0 + g * scale_a
    S.append(line(gx, jy - 2, gx, jy + 42, INK if g == 0 else FAINT,
                  2 if g == 0 else 1.0))
S.append(txt(LEFT + 8, jy + 13, "judge swaps", 17, INK, "bold"))
S.append(txt(LEFT + 8, jy + 33, f"n = {jn} runs", 15, GRAY))
jmw = jm * scale_a
S.append(rect(AX0, jy, jmw, 18, BLUE, rx=3))
S.append(txt(AX0 + jmw + 8, jy + 14, f"{jm:.3f}", 16, BLUE, "bold"))
jbw = jb * scale_a
S.append(rect(AX0, jy + 22, jbw, 18, GRAY, rx=3))
S.append(txt(AX0 + jbw + 8, jy + 36, f"{jb:.3f}", 16, GRAY, "bold"))
S.append(txt(AX0 + jbw + 62, jy + 25, "model loses →", 15, RED, "bold"))

# ---- refresh inset (the fix), its own green box --------------------------
y = rbox_top + rbox_h + 18
gbox_top = y
INSET = [
    ("roll blindly from round 1", REF_BLIND, RED),
    ("hold the swap-time value fixed", REF_HOLD, GRAY),
    ("restart at the judge change", REF_RESTART, GREEN),
]
gbox_h = 40 + len(INSET) * 28 + 74
S.append(rect(28, gbox_top, W - 56, gbox_h, KEY_FILL, stroke=GREEN, sw=1.6,
              rx=12))
gy = gbox_top + 28
S.append(txt(LEFT + 8, gy,
             "Restart at the judge change repairs it", 19, GREEN, "bold"))
gy += 22
S.append(txt(LEFT + 8, gy,
             "Remeasure the full state on the first pool the replacement "
             "judge scores, then roll forward from there.", 15, INK))
gy += 22
ry = gy
inset_axis_bottom = ry + len(INSET) * 28 - 6
for g in (0.0, 0.1, 0.2, 0.3, 0.4):
    gx = AX0 + g * scale_a
    S.append(line(gx, ry - 2, gx, inset_axis_bottom, INK if g == 0 else FAINT,
                  2 if g == 0 else 1.0))
    S.append(txt(gx, inset_axis_bottom + 20, f"{g:g}", 15, GRAY,
                 anchor="middle"))
for lab, val, col in INSET:
    S.append(txt(LEFT + 8, ry + 15, lab, 16, INK))
    vw = val * scale_a
    S.append(rect(AX0, ry + 2, vw, 17, col, rx=3))
    S.append(txt(AX0 + vw + 8, ry + 15, f"{val:.3f}", 16, col, "bold"))
    ry += 28
S.append(txt(AX0, inset_axis_bottom + 44,
             "endpoint MAE on the 9 judge-swap runs — restarting recovers "
             f"{REF_HITS}/{REF_MOVED} post-swap directions (movements ≥ 0.15) "
             "and observes one pool under the replacement judge.",
             15, INK))

y = gbox_top + gbox_h + 20

# ==================== PANEL B ====================
y += 34
S.append(txt(LEFT, y, "B", 28, INK, "bold"))
S.append(txt(LEFT + 32, y,
             "What the rollout reproduces: coarse endpoints from the mean, "
             "realistic wandering from noise", 22, INK, "bold"))
y += 25
for ln in wrap("On the 45 selection-driven + judge-swap runs, the deterministic "
               "conditional-mean path nails the coarse endpoint but is far too "
               "smooth. A staged stochastic model — selector-gap and "
               "generator-mean residuals, a zero-mean agreement innovation "
               "around persistence, and finite-battery observation noise — "
               "restores the measured path and calibrated endpoint intervals.",
               122):
    S.append(txt(LEFT, y, ln, 16, GRAY))
    y += 21

# legend for the three series
y += 14
lx = LEFT
S.append(rect(lx, y - 13, 26, 16, INK, rx=3))
S.append(txt(lx + 33, y, "observed rollouts", 17, INK))
lx += 250
S.append(rect(lx, y - 13, 26, 16, GREEN, rx=3))
S.append(txt(lx + 33, y, "deterministic mean path", 17, INK))
lx += 300
S.append(rect(lx, y - 13, 26, 16, BLUE, rx=3))
S.append(txt(lx + 33, y, "staged stochastic model", 17, INK))

# four metric small-multiples, each its own scale
y += 34
MET_LX = LEFT             # metric name column
MBX0 = 470               # bar start
MBW = 470                # bar full width
VAL_X = MBX0 + MBW + 70  # numbers column anchor start

METRICS = [
    # (name, recipe, max, fmt, [(series_color, label, value)])
    ("path total variation",
     "sum of absolute value-changes over the rounds; observed = target",
     0.80, "3f", [(INK, "observed", OBS_TV), (GREEN, "deterministic", DET_TV),
                  (BLUE, "staged", STG_TV)]),
    ("path sign reversals",
     "number of times the trajectory reverses direction; observed = target",
     1.60, "2f", [(INK, "observed", OBS_SR), (GREEN, "deterministic", DET_SR),
                  (BLUE, "staged", STG_SR)]),
    ("endpoint CRPS",
     "probabilistic endpoint error, lower is better; no observed target",
     0.16, "3f", [(GREEN, "deterministic", DET_CRPS),
                  (BLUE, "staged", STG_CRPS)]),
    ("80%-interval endpoint coverage",
     "share of runs inside the nominal-80% band; 0.80 is the target",
     1.0, "pct", [(GREEN, "deterministic", DET_COV),
                  (BLUE, "staged", STG_COV)]),
]

for name, recipe, mx, valfmt, series in METRICS:
    blk_top = y
    n_ser = len(series)
    bar_h = 18
    gap = 6
    blk_h = 34 + n_ser * (bar_h + gap)
    S.append(txt(MET_LX, blk_top + 16, name, 18, INK, "bold"))
    ry_recipe = blk_top + 38
    for ln in wrap(recipe, 40):
        S.append(txt(MET_LX, ry_recipe, ln, 13, GRAY))
        ry_recipe += 17
    # per-metric axis
    sc = MBW / mx
    ax_top = y - 2
    ax_bot = y + n_ser * (bar_h + gap) + 2
    S.append(line(MBX0, ax_top, MBX0, ax_bot, INK, 2))
    # target reference line for TV / sign reversals (observed) and coverage 0.80
    target = None
    if name.startswith("path total"):
        target = OBS_TV
    elif name.startswith("path sign"):
        target = OBS_SR
    elif name.startswith("80%"):
        target = 0.80
    if target is not None:
        tx = MBX0 + target * sc
        S.append(line(tx, ax_top - 4, tx, ax_bot + 4, RED, 1.6, dash="5 4"))
        tlab = ("observed target" if name.startswith("path")
                else "nominal 80%")
        S.append(txt(tx, ax_bot + 20, tlab, 13, RED, anchor="middle"))
    by = y
    for col, slab, val in series:
        vw = max(val * sc, 1.5)
        S.append(rect(MBX0, by, vw, bar_h, col, rx=3))
        if valfmt == "pct":
            fmt = f"{val:.0%}"
        elif valfmt == "3f":
            fmt = f"{val:.3f}"
        else:
            fmt = f"{val:.2f}"
        # numeric label to the right of the bar, coloured to its series
        S.append(txt(MBX0 + vw + 8, by + 14, f"{fmt}", 16, col, "bold"))
        S.append(txt(MBX0 + vw + 62, by + 14, slab, 14, GRAY))
        by += bar_h + gap
    y = blk_top + blk_h + 18

# ---- coarse-fidelity + observation-noise annotation boxes -----------------
y += 6
kbx = 28
kbw = 592
kbh = 132
S.append(rect(kbx, y, kbw, kbh, KEY_FILL, stroke=GREEN, sw=1.6, rx=12))
ky = y + 26
S.append(txt(kbx + 16, ky, "The deterministic mean gets the coarse endpoint",
             18, GREEN, "bold"))
ky += 24
for ln in wrap(f"{LM_HITS} of {LM_N} large-movement directions correct; "
               f"{RAIL_HITS} of {RAIL_N} observed rail endpoints recovered. "
               f"Predicted endpoint mean {END_PRED_MEAN:.3f} vs observed "
               f"{END_OBS_MEAN:.3f}; predicted endpoint SD {END_PRED_SD:.3f} "
               f"vs observed {END_OBS_SD:.3f}.", 66):
    S.append(txt(kbx + 16, ky, ln, 15, INK))
    ky += 20

obx = kbx + kbw + 20
obw = W - 28 - obx
S.append(rect(obx, y, obw, kbh, ASST_FILL, stroke=BLUE, sw=1.6, rx=12))
oy = y + 26
S.append(txt(obx + 16, oy, "Where the noise lives", 18, BLUE, "bold"))
oy += 24
for ln in wrap("Selector-gap and generator-mean residuals, a zero-mean "
               "agreement innovation around persistence, and observation "
               "noise — battery readout only, it does not feed back. No "
               "latent value-process kick and no risk-feedback term are "
               "added: both are rejected as post-hoc.", 60):
    S.append(txt(obx + 16, oy, ln, 15, INK))
    oy += 20

y += kbh + 30

# ---- footnotes -----------------------------------------------------------
foot1 = (f"Spread definition is a robustness check only: mean within-prompt "
         f"population SD and mean within-prompt range give endpoint forecasts "
         f"differing by {DEF_DIFF:.4f} on average and share the same endpoint "
         f"class on {DEF_CLASS_N}/{DEF_COMMON} runs, so the writeup uses mean "
         f"SD for both the selector decomposition and the endpoint prediction.")
for ln in wrap(foot1, 138):
    S.append(txt(LEFT, y, ln, 14, GRAY))
    y += 19

y += 6
for ln in wrap(
        "Sources: experiments/spread_rollout_bakeoff.json "
        "(validations.leave_one_condition_out.frozen + judge_swap_refresh), "
        "experiments/rollout_property_fidelity.json, and "
        "experiments/trajectory_adjustment_bakeoff.json "
        "(selector_q_observation_rho_persistence_gaussian). "
        "Generator: spread-rollout-bakeoff.py", 138):
    S.append(txt(LEFT, y, ln, 14, GRAY))
    y += 19

H = y + 24

svg = (f'<svg xmlns="http://www.w3.org/2000/svg" '
       f'viewBox="0 0 {W} {int(H)}" font-family="{FONT}">\n'
       f'<rect width="{W}" height="{int(H)}" fill="white"/>\n'
       + "\n".join(S) + "\n</svg>")

out = os.path.join(HERE, "spread-rollout-bakeoff.svg")
with open(out, "w") as f:
    f.write(svg)
print(f"wrote {out}  viewBox 0 0 {W} {int(H)}")
