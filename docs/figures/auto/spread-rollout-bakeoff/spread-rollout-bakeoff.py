#!/usr/bin/env python3
"""Closed-loop rollout bake-off figure (slug: spread-rollout-bakeoff).

The value-dynamics simulator is fit on nothing: it observes ONLY a held-out
run's FIRST-round pool state (its spread and its agreement, each measured once),
then rolls the parameter-free UNIT RECURRENCE forward without reading that run's
later candidates, spread, agreement, or value. The recurrence is

    m_next = clip( (1 - u) * m + u * supplier + rho * sigma )

and the forecast's next value is the kept-mean identity. Validation is
leave-one-CONDITION-out (LOCO): the entire intervention / judge regime is held
out.

Panel A: endpoint MAE by regime, the unit recurrence vs a no-change baseline;
         plus a red box + green inset showing that a mid-run judge change is new
         information and that restarting the rollout at the judge change (one
         re-measurement) restores the forecast.
Panel B: for the 45 selection-driven + judge-swap runs, the coarse deterministic
         unit rollout reproduces endpoint behaviour but is too smooth, while a
         staged stochastic model with separately located innovations restores
         realistic measured paths and calibrated endpoint intervals.

Every displayed number is read from the committed JSONs (json.load) at the exact
paths below and asserted against expected values; nothing is transcribed.
Palette + esc()/wrap() copied from docs/figures/src/make_figures.py (house style).

Regenerate with:  python3 spread-rollout-bakeoff.py
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
EXP = os.path.join(HERE, "..", "..", "..", "..", "experiments")
UNIT = os.path.join(EXP, "unit_rollout_properties.json")
BAKEOFF = os.path.join(EXP, "spread_rollout_bakeoff.json")
STAGED = os.path.join(EXP, "trajectory_adjustment_bakeoff.json")

# ---- palette (house style; make_figures.py constants) --------------------
INK = "#1a1a1a"
BLUE = "#2867b5"        # the unit recurrence's closed-loop forecast
GREEN = "#3a7d44"       # deterministic mean path / the repaired restart
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


# ======================================================================
# read + verify data
# ======================================================================
with open(UNIT) as f:
    UN = json.load(f)
with open(BAKEOFF) as f:
    BK = json.load(f)
with open(STAGED) as f:
    ST = json.load(f)

EO = UN["endpoint_only_matched_45"]
BY = EO["by_regime_group"]
assert EO["n_runs"] == 45, EO["n_runs"]

# ---- Panel A: per-regime unit recurrence vs no-change ---------------------
# (label, json key, expected unit MAE, expected no-change MAE, n)
PANEL_A = [
    ("selection-driven", "selection_driven", 0.118, 0.431, 36),
    ("mixed interventions", "intervention", 0.114, 0.450, 24),
    ("strong-agreement self-only", "self_force", 0.126, 0.393, 12),
    ("weak self-only selection", "self_weak", 0.211, 0.215, 22),
]
a_rows = []
for label, key, exp_m, exp_b, exp_n in PANEL_A:
    n = BY[key]
    m = n["unit_recurrence_endpoint_mae"]
    b = n["no_change_endpoint_mae"]
    assert round(m, 3) == exp_m, (label, "unit", m, exp_m)
    assert round(b, 3) == exp_b, (label, "baseline", b, exp_b)
    assert n["n_runs"] == exp_n, (label, "n", n["n_runs"], exp_n)
    a_rows.append((label, m, b, n["n_runs"]))

# ---- judge-swap block ----------------------------------------------------
# Fitted variants (the unit rollout starts AT the boundary, so blind-from-round1
# and hold-swap-time are fitted-frozen-SD comparators, sourced from the bakeoff).
REF = BK["judge_swap_refresh"]["leave_one_condition_out"]["mean_sd_frozen"][
    "aggregate"]
REF_END = REF["endpoint"]
REF_BLIND = REF_END["closed_from_round1"]["mae"]        # 0.404 (fitted variant)
REF_HOLD = REF_END["persistence_from_swap"]["mae"]      # 0.309 (fitted variant)
assert round(REF_BLIND, 3) == 0.404, REF_BLIND
assert round(REF_HOLD, 3) == 0.309, REF_HOLD
rdir = REF["direction_from_swap_on_runs_moving_at_least_0_15"]
REF_HITS, REF_MOVED = rdir["n_hits"], rdir["n_moved"]
assert (REF_HITS, REF_MOVED) == (6, 7), (REF_HITS, REF_MOVED)

# Unit model at the judge swap: restart at the boundary vs no-change-from-round1.
JS = BY["judge_swap_refreshed"]
JS_RESTART = JS["unit_recurrence_endpoint_mae"]         # 0.2099 (unit model)
JS_NOCHANGE = JS["no_change_endpoint_mae"]              # 0.3608
JS_N = JS["n_runs"]
assert round(JS_RESTART, 4) == 0.2099, JS_RESTART
assert round(JS_NOCHANGE, 4) == 0.3608, JS_NOCHANGE
assert JS_N == 9, JS_N

# ---- Panel B: deterministic unit rollout vs staged stochastic model -------
DET = ST["primary_selection_driven_plus_swap"]["unit_core_deterministic"]
STG = ST["primary_selection_driven_plus_swap"][
    "unit_core_selector_q_observation_rho_persistence_gaussian"]
assert DET["n_runs"] == 45 and STG["n_runs"] == 45

DP = DET["aggregate_path_properties"]
SP = STG["aggregate_path_properties"]

OBS_TV = DP["total_variation"]["observed"]
DET_TV = DP["total_variation"]["simulated"]
STG_TV = SP["total_variation"]["simulated"]
assert round(OBS_TV, 3) == 0.648 and round(DET_TV, 3) == 0.499
assert round(STG_TV, 3) == 0.709, STG_TV

OBS_SR = DP["sign_changes"]["observed"]
DET_SR = DP["sign_changes"]["simulated"]
STG_SR = SP["sign_changes"]["simulated"]
assert round(OBS_SR, 2) == 1.20 and round(DET_SR, 2) == 0.18
assert round(STG_SR, 2) == 1.22, STG_SR

DET_CRPS = DET["endpoint_crps"]
STG_CRPS = STG["endpoint_crps"]
assert round(DET_CRPS, 3) == 0.135 and round(STG_CRPS, 3) == 0.092
STG_COV = STG["endpoint_80pct_coverage"]
assert round(STG_COV, 2) == 0.89, STG_COV

# deterministic endpoint mean (unit) vs observed
END_PRED_MEAN = DP["endpoint"]["simulated"]
END_OBS_MEAN = DP["endpoint"]["observed"]
assert round(END_PRED_MEAN, 3) == 0.586 and round(END_OBS_MEAN, 3) == 0.541

# coarse-fidelity annotations (unit recurrence, endpoint-only matched 45)
UR = EO["unit_recurrence"]
LM_HITS, LM_N = (int(x) for x in UR["large_move_direction_from_last_reread"].split("/"))
RAIL_HITS, RAIL_N = (int(x) for x in UR["rail_endpoint_recall"].split("/"))
assert (LM_HITS, LM_N) == (37, 38), (LM_HITS, LM_N)
assert (RAIL_HITS, RAIL_N) == (21, 24), (RAIL_HITS, RAIL_N)


# ======================================================================
# build the SVG
# ======================================================================
W = 1240
LEFT = 40
S = []

# ---- headline finding + one method line ----------------------------------
y = 50
S.append(txt(LEFT, y,
             "A parameter-free unit recurrence predicts where an unseen "
             "condition lands; separate noise restores how the path wanders",
             25, INK, "bold"))
y += 32
for ln in wrap("The simulator observes only the held-out condition's FIRST pool "
               "— its spread and its agreement, each measured once — then rolls "
               "the unit recurrence m_next = clip((1-u)m + u*supplier + rho*sigma) "
               "forward, reading none of that run's later candidates, spread, "
               "agreement, or value. No parameter is fit to the trajectories. "
               "Validation is leave-one-condition-out: the entire intervention / "
               "judge regime is held out. Endpoint MAE = mean absolute error of "
               "the predicted final behavioral value vs the true final value, on "
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
for ln in wrap("Endpoint MAE per regime: the parameter-free unit recurrence "
               "(spread and agreement measured once at round 1, then rolled "
               "forward) vs a no-change baseline that predicts the round-1 value "
               "forever. It wins in every selection and intervention regime, and "
               "ties the weak self-only regime that barely moves.", 122):
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
S.append(txt(AX0 + 34, y, "parameter-free unit recurrence — spread × "
             "agreement measured once at round 1", 17, INK))
y += 24
S.append(rect(AX0, y - 13, 26, 16, GRAY, rx=3))
S.append(txt(AX0 + 34, y, "no-change baseline — predicts the round-1 "
             "value forever", 17, INK))

# rows
y += 20
ROW_H = 64
a_top = y
grid_bottom_a = a_top + 4 * ROW_H - 8
bar_axis(a_top - 4, grid_bottom_a)

for label, m, b, n in a_rows:
    bt = y
    S.append(txt(LEFT, bt + 16, label, 18, INK, "bold"))
    S.append(txt(LEFT, bt + 37, f"n = {n} runs", 15, GRAY))
    # unit-recurrence bar
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
S.append(txt(LEFT + 8, yb, "A mid-run judge change is new information",
             19, RED, "bold"))
yb += 23
for ln in wrap("A round-1 forecast cannot contain a judge decision that has not "
               "been made yet. Rolling blindly from the original round 1 lands "
               "far off; re-measuring the state on the first pool the "
               "replacement judge scores restores the forecast.", 120):
    S.append(txt(LEFT + 8, yb, ln, 15, INK))
    yb += 20

jy = yb + 4
for g in (0.0, 0.1, 0.2, 0.3, 0.4):
    gx = AX0 + g * scale_a
    S.append(line(gx, jy - 2, gx, jy + 42, INK if g == 0 else FAINT,
                  2 if g == 0 else 1.0))
S.append(txt(LEFT + 8, jy + 13, "judge swaps", 17, INK, "bold"))
S.append(txt(LEFT + 8, jy + 33, f"n = {JS_N} runs", 15, GRAY))
# roll blindly from original round 1 (fitted variant)
jmw = REF_BLIND * scale_a
S.append(rect(AX0, jy, jmw, 18, RED, rx=3))
S.append(txt(AX0 + jmw + 8, jy + 14, f"{REF_BLIND:.3f}", 16, RED, "bold"))
S.append(txt(AX0 + jmw + 62, jy + 14,
             "roll blindly from original round 1", 14, GRAY))
# no-change baseline
jbw = JS_NOCHANGE * scale_a
S.append(rect(AX0, jy + 22, jbw, 18, GRAY, rx=3))
S.append(txt(AX0 + jbw + 8, jy + 36, f"{JS_NOCHANGE:.3f}", 16, GRAY, "bold"))
S.append(txt(AX0 + jbw + 68, jy + 36, "no-change baseline", 14, GRAY))

# ---- refresh inset (the fix), its own green box --------------------------
y = rbox_top + rbox_h + 18
gbox_top = y
INSET = [
    ("roll blindly from round 1", REF_BLIND, RED,
     "(fitted variant — the unit rollout starts at the boundary)"),
    ("hold the swap-time value fixed", REF_HOLD, GRAY,
     "(fitted variant comparator)"),
    ("restart at the judge change", JS_RESTART, GREEN,
     "(unit recurrence, re-measured at the swap)"),
]
gbox_h = 40 + len(INSET) * 30 + 82
S.append(rect(28, gbox_top, W - 56, gbox_h, KEY_FILL, stroke=GREEN, sw=1.6,
              rx=12))
gy = gbox_top + 28
S.append(txt(LEFT + 8, gy,
             "Restart at the judge change repairs it", 19, GREEN, "bold"))
gy += 22
S.append(txt(LEFT + 8, gy,
             "Remeasure the full state on the first pool the replacement "
             "judge scores, then roll the unit recurrence forward from there.",
             15, INK))
gy += 22
ry = gy
inset_axis_bottom = ry + len(INSET) * 30 - 8
for g in (0.0, 0.1, 0.2, 0.3, 0.4):
    gx = AX0 + g * scale_a
    S.append(line(gx, ry - 2, gx, inset_axis_bottom, INK if g == 0 else FAINT,
                  2 if g == 0 else 1.0))
    S.append(txt(gx, inset_axis_bottom + 20, f"{g:g}", 15, GRAY,
                 anchor="middle"))
for lab, val, col, note in INSET:
    S.append(txt(LEFT + 8, ry + 15, lab, 16, INK))
    S.append(txt(LEFT + 8, ry + 30, note, 12, GRAY))
    vw = val * scale_a
    S.append(rect(AX0, ry + 2, vw, 17, col, rx=3))
    S.append(txt(AX0 + vw + 8, ry + 15, f"{val:.3f}", 16, col, "bold"))
    ry += 30
S.append(txt(LEFT + 8, inset_axis_bottom + 44,
             f"endpoint MAE on the {JS_N} judge-swap runs — restarting "
             f"recovers {REF_HITS}/{REF_MOVED} post-swap directions; observes "
             "one pool under the new judge.", 15, INK))

y = gbox_top + gbox_h + 20

# ==================== PANEL B ====================
y += 34
S.append(txt(LEFT, y, "B", 28, INK, "bold"))
S.append(txt(LEFT + 32, y,
             "What the rollout reproduces: coarse endpoints from the mean, "
             "realistic wandering from noise", 22, INK, "bold"))
y += 25
for ln in wrap("On the 45 selection-driven + judge-swap runs (leave-one-condition-out), "
               "the deterministic unit rollout nails the coarse endpoint but is "
               "far too smooth. A staged stochastic model — selector-gap and "
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
S.append(txt(lx + 33, y, "deterministic unit rollout", 17, INK))
lx += 300
S.append(rect(lx, y - 13, 26, 16, BLUE, rx=3))
S.append(txt(lx + 33, y, "staged stochastic model", 17, INK))

# four metric small-multiples, each its own scale
y += 34
MET_LX = LEFT
MBX0 = 470
MBW = 470
VAL_X = MBX0 + MBW + 70

METRICS = [
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
     "share of the staged model's runs inside its nominal-80% band; 0.80 is "
     "the target",
     1.0, "pct", [(BLUE, "staged", STG_COV)]),
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
    sc = MBW / mx
    ax_top = y - 2
    ax_bot = y + n_ser * (bar_h + gap) + 2
    S.append(line(MBX0, ax_top, MBX0, ax_bot, INK, 2))
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
for ln in wrap(f"{LM_HITS} of {LM_N} large-movement directions correct (graded "
               f"from the forecast's last state measurement); {RAIL_HITS} of "
               f"{RAIL_N} observed rail endpoints recovered. Deterministic "
               f"endpoint mean {END_PRED_MEAN:.3f} vs observed "
               f"{END_OBS_MEAN:.3f}.", 66):
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
               "noise on the reported value only, not fed back. No "
               "latent value-process kick and no risk-feedback term are "
               "added: both are rejected as post-hoc.", 60):
    S.append(txt(obx + 16, oy, ln, 15, INK))
    oy += 20

y += kbh + 30

# ---- footnotes -----------------------------------------------------------
foot1 = ("The unit recurrence reads spread (within-prompt population SD) and "
         "agreement (rho) once from round 1 and holds them. The fitted "
         "frozen-mean-SD variant is used only as the pre-swap comparator "
         "(roll-blindly and hold-swap-time bars above).")
for ln in wrap(foot1, 138):
    S.append(txt(LEFT, y, ln, 14, GRAY))
    y += 19

y += 6
for ln in wrap(
        "Sources: experiments/unit_rollout_properties.json "
        "(endpoint_only_matched_45.by_regime_group + unit_recurrence), "
        "experiments/spread_rollout_bakeoff.json (judge_swap_refresh, fitted "
        "comparators + direction), and experiments/trajectory_adjustment_bakeoff.json "
        "(unit_core_deterministic + unit_core_selector_q_observation_rho_persistence_gaussian). "
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
