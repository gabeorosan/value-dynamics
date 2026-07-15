#!/usr/bin/env python3
"""Two-panel closed-loop rollout bake-off figure (slug: spread-rollout-bakeoff).

A value-dynamics simulator is fit on other runs, then observes ONLY a held-out
run's FIRST-round pool state and rolls the whole trajectory forward without
reading that run's later candidates, spread, agreement, or value. Validation is
leave-one-CONDITION-out (LOCO): the entire intervention/judge regime is held out
-- the real test of whether a spread definition transports to a new regime.

Panel A: per-regime endpoint MAE, closed-loop (geometry) vs the no-change
         baseline (value never moves from round 1). Lower is better.
Panel B: for the nine spread definitions that exist on BOTH score axes, the
         selection-driven endpoint MAE under predicted metric dynamics
         (geometry) vs first-round metric frozen.

All numbers are read from experiments/spread_rollout_bakeoff.json (json.load) at
the exact paths named below and asserted against expected values; nothing is
transcribed. House style follows docs/figures/src/make_figures.py and the sibling
auto figures (two-dials-clean, rollout-by-regime).

Regenerate with:  python3 spread-rollout-bakeoff.py
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "..", "..", "..", "experiments",
                    "spread_rollout_bakeoff.json")

# ---- palette (house style; prompt-specified hexes) -----------------------
INK = "#1a1a1a"
BLUE = "#1f6fd0"       # closed-loop rollout / predicted metric dynamics (geometry)
GRAY = "#6b7684"       # no-change baseline / first-round metric frozen
RED = "#d1341f"        # out-of-scope / worse marker
FAINT = "#e4e4e0"      # gridlines / boxes
BAND = "#eef3fb"       # highlight band (light blue)
OOS_FILL = "#fbeeec"   # out-of-scope tint (light red)
DUMB = "#c4cad0"       # dumbbell connector

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


def txt(x, y, s, size=18, color=INK, weight="normal", anchor="start",
        halo=False):
    h = ('stroke="white" stroke-width="4.5" stroke-linejoin="round" '
         'paint-order="stroke" ') if halo else ""
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{FONT}" '
            f'font-size="{size}" fill="{color}" font-weight="{weight}" '
            f'{h}text-anchor="{anchor}">{esc(s)}</text>')


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
with open(DATA) as f:
    D = json.load(f)

LOCO = D["validations"]["leave_one_condition_out"]
GEO = LOCO["geometry"]
FROZEN = LOCO["frozen"]
SD_KEY = "mean_within_prompt_population_sd"   # the primary selector scale


def endpoint_mae(defn_node, group):
    return defn_node["aggregates"][group]["behavioral_value_endpoint"]["mae"]


def persist_mae(defn_node, group):
    return defn_node["aggregates"][group][
        "behavioral_value_endpoint_persistence"]["mae"]


def nruns(defn_node, group):
    return defn_node["aggregates"][group]["n_runs"]


# ---- Panel A: per-regime, using the SD selector scale --------------------
# (label, json group key, expected closed / no-change / n) -- assertions catch
# a wrong path before the figure is ever drawn.
PANEL_A = [
    ("selection-driven",           "selection_driven", 0.139, 0.431, 36),
    ("mixed interventions",        "intervention",     0.138, 0.450, 24),
    ("strong-agreement self-only", "self_force",       0.140, 0.393, 12),
    ("weak self-only selection",   "self_weak",        0.205, 0.215, 22),
    ("judge swapped mid-run",      "judge_swap",       0.392, 0.361,  9),
]
a_rows = []
sd_geo = GEO[SD_KEY]
for label, key, exp_c, exp_n, exp_runs in PANEL_A:
    closed = endpoint_mae(sd_geo, key)
    noch = persist_mae(sd_geo, key)
    n = nruns(sd_geo, key)
    assert round(closed, 3) == exp_c, (label, "closed", closed, exp_c)
    assert round(noch, 3) == exp_n, (label, "nochange", noch, exp_n)
    assert n == exp_runs, (label, "n", n, exp_runs)
    a_rows.append((label, closed, noch, n, key == "judge_swap"))

# selection-driven large-move direction count (28/31)
sel_dir = sd_geo["aggregates"]["selection_driven"][
    "direction_on_runs_moving_at_least_0_15"]
A_HITS, A_MOVED = sel_dir["n_hits"], sel_dir["n_moved"]
assert (A_HITS, A_MOVED) == (28, 31), (A_HITS, A_MOVED)

# ---- Panel B: nine definitions on both score axes ------------------------
PANEL_B = [
    ("mean within-prompt range  (rankable support)",
     "mean_within_prompt_range", 0.132, 0.125),
    ("mean pairwise abs. difference",
     "mean_pairwise_absolute_score_difference", 0.137, 0.129),
    ("mean within-prompt SD  (spread)",
     "mean_within_prompt_population_sd", 0.139, 0.127),
    ("mean within-prompt MAD",
     "mean_within_prompt_mean_absolute_deviation", 0.140, 0.129),
    ("mean within-prompt variance",
     "mean_within_prompt_variance", 0.141, 0.128),
    ("RMS within-prompt SD",
     "rms_within_prompt_population_sd", 0.148, 0.140),
    ("fraction of prompts with any difference",
     "fraction_prompts_with_any_score_difference", 0.150, 0.140),
    ("total pooled SD (incl. between-prompt)",
     "total_sd_including_between_prompt_variation", 0.161, 0.160),
    ("median within-prompt SD",
     "median_within_prompt_population_sd", 0.208, 0.165),
]
b_rows = []
for label, defn, exp_g, exp_f in PANEL_B:
    g = endpoint_mae(GEO[defn], "selection_driven")
    fr = endpoint_mae(FROZEN[defn], "selection_driven")
    assert round(g, 3) == exp_g, (label, "geo", g, exp_g)
    assert round(fr, 3) == exp_f, (label, "frozen", fr, exp_f)
    b_rows.append((label, defn, g, fr))
# ordered by geometry ascending (already listed so; verify)
assert [r[2] for r in b_rows] == sorted(r[2] for r in b_rows)

HL_RANGE = "mean_within_prompt_range"
HL_SD = "mean_within_prompt_population_sd"

# ---- annotation numbers, all read from JSON ------------------------------
paired = D["paired_endpoint_comparison_vs_primary"][
    "leave_one_condition_out"]["geometry"]["mean_within_prompt_range"][
    "selection_driven"]
RANGE_MINUS_SD = -paired["alternative_minus_primary_endpoint_mae"]   # +0.007
CI_LO = -paired["bootstrap_95pct_ci"][1]     # 0.003
CI_HI = -paired["bootstrap_95pct_ci"][0]     # 0.011
FROZEN_GAP = endpoint_mae(FROZEN[HL_SD], "selection_driven") - \
    endpoint_mae(FROZEN[HL_RANGE], "selection_driven")            # 0.002

# spread-trajectory MAE on risk-axis runs (footnote): geometry vs frozen
risk_sd = GEO[SD_KEY]["aggregates"]["risk"]
SPREAD_GEO = risk_sd["own_metric_rounds_2plus"]["mae"]           # 0.080
SPREAD_FRZ = risk_sd["own_metric_persistence"]["mae"]           # 0.111
# endpoint SD geometry vs frozen (selection-driven)
END_SD_GEO = endpoint_mae(GEO[HL_SD], "selection_driven")       # 0.139
END_SD_FRZ = endpoint_mae(FROZEN[HL_SD], "selection_driven")    # 0.127
# best simple endpoint model = frozen rankable support
END_RANGE_FRZ = endpoint_mae(FROZEN[HL_RANGE], "selection_driven")   # 0.125
NOCH_SEL = persist_mae(sd_geo, "selection_driven")                   # 0.431
frz_range_dir = FROZEN[HL_RANGE]["aggregates"]["selection_driven"][
    "direction_on_runs_moving_at_least_0_15"]
FRZ_HITS, FRZ_MOVED = frz_range_dir["n_hits"], frz_range_dir["n_moved"]
assert (FRZ_HITS, FRZ_MOVED) == (31, 31)
# binary entropy (risk-0/1 runs only) -- excluded from the ranking
BIN_ENT = endpoint_mae(GEO["mean_within_prompt_binary_entropy_bits"],
                       "selection_driven")                            # 0.128


# ======================================================================
# build the SVG
# ======================================================================
W = 1240
LEFT = 40
S = []
y = 0.0

# ---- top finding + method line -------------------------------------------
y = 50
S.append(txt(LEFT, y,
             "Closed-loop rollout: a spread model predicts an unseen "
             "condition from its first pool", 25, INK, "bold"))
y += 30
for ln in wrap("Fit on other runs, the model rolls the whole trajectory "
               "forward and never reads the held-out run's later candidates, "
               "spread, agreement, or value. Validation is leave-one-condition-"
               "out: the entire intervention / judge regime is held out. Lower "
               "endpoint MAE (mean absolute error of the predicted final value "
               "vs the true final value, 0-1 scale) is better.", 118):
    S.append(txt(LEFT, y, ln, 17, GRAY))
    y += 22

# ==================== PANEL A ====================
y += 20
S.append(txt(LEFT, y, "A", 30, INK, "bold"))
S.append(txt(LEFT + 34, y,
             "Does the closed loop predict an unseen condition?",
             23, INK, "bold"))
y += 27
for ln in wrap("Per regime: closed-loop endpoint error vs the no-change "
               "baseline (value never moves from round 1). The model sees only "
               "the held-out run's first pool, then rolls forward; on "
               "selection-driven runs it gets "
               f"{A_HITS}/{A_MOVED} large-move directions right.", 120):
    S.append(txt(LEFT, y, ln, 17, GRAY))
    y += 22

# panel-A bar geometry
AX0 = 356
AW = 636
MAXA = 0.46
scale_a = AW / MAXA

# legend
y += 12
S.append(rect(AX0, y - 13, 28, 17, BLUE, rx=3))
S.append(txt(AX0 + 36, y, "closed loop — rolls the trajectory forward "
             "from round 1", 18, INK))
y += 26
S.append(rect(AX0, y - 13, 28, 17, GRAY, rx=3))
S.append(txt(AX0 + 36, y, "no-change — predicts the round-1 value forever "
             "(baseline)", 18, INK))

# pre-compute block tops
y += 22
ROW_H = 70
OOS_H = 92
block_tops = []
cur = y
for label, closed, noch, n, oos in a_rows:
    if oos:
        cur += 26
    block_tops.append((cur, oos))
    cur += OOS_H if oos else ROW_H
grid_top = block_tops[0][0] - 6
grid_bottom = cur - 8

# gridlines + x ticks
for g in (0.0, 0.1, 0.2, 0.3, 0.4):
    gx = AX0 + g * scale_a
    if g == 0.0:
        S.append(line(gx, grid_top, gx, grid_bottom, INK, 2))
    else:
        S.append(line(gx, grid_top, gx, grid_bottom, FAINT, 1.2))
    S.append(txt(gx, grid_bottom + 26, f"{g:g}", 18, GRAY, anchor="middle"))
S.append(txt(AX0 + AW / 2, grid_bottom + 56,
             "endpoint MAE (mean absolute error vs true final value) "
             "— lower is better", 18, INK, anchor="middle"))

# rows
for (label, closed, noch, n, oos), (bt, _) in zip(a_rows, block_tops):
    if oos:
        S.append(rect(30, bt - 6, 1180, OOS_H - 6, OOS_FILL, stroke=RED,
                      sw=1.4, rx=10))
        S.append(line(28, bt - 16, 1210, bt - 16, FAINT, 1.2))
    # category label + n
    S.append(txt(LEFT, bt + 24, label, 19, INK, "bold"))
    S.append(txt(LEFT, bt + 46, f"n = {n}", 17, GRAY))
    # closed-loop bar
    cb_y = bt + 6
    cw = closed * scale_a
    if oos:
        S.append(rect(AX0, cb_y, cw, 24, "url(#hatch)", stroke=RED, sw=1.4,
                      rx=3))
        S.append(txt(AX0 + cw + 9, cb_y + 18, f"{closed:.3f}", 18, RED,
                     "bold"))
    else:
        S.append(rect(AX0, cb_y, cw, 24, BLUE, rx=3))
        S.append(txt(AX0 + cw + 9, cb_y + 18, f"{closed:.3f}", 18, BLUE,
                     "bold"))
    # no-change bar
    nb_y = bt + 34
    nw = noch * scale_a
    S.append(rect(AX0, nb_y, nw, 24, GRAY, rx=3))
    S.append(txt(AX0 + nw + 9, nb_y + 18, f"{noch:.3f}", 18, GRAY, "bold"))
    if oos:
        S.append(txt(LEFT, bt + 76, "out of scope: the judge changes mid-run "
                     "— a state the round-1 model cannot see (the only "
                     "regime where closed-loop loses)", 16, RED))

y = grid_bottom + 56

# ==================== PANEL B ====================
y += 62
S.append(txt(LEFT, y, "B", 30, INK, "bold"))
S.append(txt(LEFT + 34, y,
             "Definition vs dynamics: which spread scale transports?",
             23, INK, "bold"))
y += 27
for ln in wrap("Selection-driven endpoint MAE, whole condition held out "
               "(leave-one-condition-out), for the nine spread definitions "
               "that exist on both score axes (risk option 0/1 and continuous "
               "self-description). Ordered best (top) to worst (bottom).", 120):
    S.append(txt(LEFT, y, ln, 17, GRAY))
    y += 22

# panel-B dumbbell geometry
B_X0 = 500
BW = 500
BMIN, BMAX = 0.11, 0.215
scale_b = BW / (BMAX - BMIN)


def bx(v):
    return B_X0 + (v - BMIN) * scale_b


# legend
y += 12
S.append(circle(B_X0 + 6, y - 6, 8, BLUE))
S.append(txt(B_X0 + 24, y, "predicted metric dynamics (geometry)", 18, INK))
S.append(circle(B_X0 + 6, y + 20, 8, GRAY))
S.append(txt(B_X0 + 24, y + 26, "first-round metric frozen", 18, INK))

# rows
y += 46
ROW_HB = 44
b_top = y
grid_b_bottom = b_top + len(b_rows) * ROW_HB
# vertical gridlines first, so bands / connectors / dots sit on top
for gt in (0.12, 0.14, 0.16, 0.18, 0.20):
    S.append(line(bx(gt), b_top - 6, bx(gt), grid_b_bottom, FAINT, 1.0))
for i, (label, defn, g, fr) in enumerate(b_rows):
    ry = b_top + i * ROW_HB
    cy = ry + ROW_HB / 2
    hl = defn in (HL_RANGE, HL_SD)
    if hl:
        S.append(rect(28, ry, 1184, ROW_HB, BAND, rx=8))
    S.append(txt(LEFT, cy + 6, label, 18, INK, "bold" if hl else "normal"))
    gx, bxx = bx(fr), bx(g)
    S.append(line(gx, cy, bxx, cy, DUMB, 4))
    S.append(circle(gx, cy, 8, GRAY))
    S.append(circle(bxx, cy, 8, BLUE))
    S.append(txt(gx - 12, cy + 6, f"{fr:.3f}", 18, GRAY, anchor="end"))
    S.append(txt(bxx + 12, cy + 6, f"{g:.3f}", 18, BLUE, "bold"))
    if defn == HL_RANGE:
        S.append(txt(1046, cy + 6, "← best endpoint state", 16, INK,
                     "bold"))
    elif defn == HL_SD:
        S.append(txt(1046, cy + 6, "← the direct selector scale", 16, INK,
                     "bold"))

# x-axis tick labels under the rows
for gt in (0.12, 0.14, 0.16, 0.18, 0.20):
    S.append(txt(bx(gt), grid_b_bottom + 26, f"{gt:g}", 18, GRAY,
                 anchor="middle"))
S.append(txt((B_X0 + B_X0 + BW) / 2, grid_b_bottom + 54,
             "selection-driven endpoint MAE — lower is better", 18, INK,
             anchor="middle"))

y = grid_b_bottom + 54

# ---- panel-B annotations -------------------------------------------------
y += 40
S.append(txt(LEFT, y,
             f"Range beats mean SD by {RANGE_MINUS_SD:.3f} endpoint MAE "
             f"under geometry (paired bootstrap 95% CI {CI_LO:.3f}–"
             f"{CI_HI:.3f});", 18, INK, "bold"))
y += 24
S.append(txt(LEFT, y,
             f"under frozen the gap is only {FROZEN_GAP:.3f} and its interval "
             "crosses zero. Total pooled SD and median within-prompt SD "
             "(bottom two) are clearly worse.", 18, INK))
y += 24
S.append(txt(LEFT, y,
             "“Fraction of prompts with any difference” wins under "
             "leave-one-RUN-out but reverses here (0.150) — it does not "
             "transport, so it is not crowned.", 18, RED))

# ---- fine-print footnote -------------------------------------------------
y += 32
foot = (f"Mean-SD geometry predicts the risk spread trajectory better than "
        f"freezing it (spread MAE {SPREAD_GEO:.3f} vs {SPREAD_FRZ:.3f}) yet "
        f"predicts value endpoints worse ({END_SD_GEO:.3f} vs {END_SD_FRZ:.3f}) "
        f"— feeding predicted spread back does not help the endpoint. The "
        f"best simple endpoint model is frozen rankable support: MAE "
        f"{END_RANGE_FRZ:.3f} vs {NOCH_SEL:.3f} no-change, {FRZ_HITS}/"
        f"{FRZ_MOVED} large-move directions right. Binary entropy (risk-0/1 "
        f"runs only) scores {BIN_ENT:.3f} but is not comparable across both "
        f"axes, so it is excluded from this ranking.")
for ln in wrap(foot, 132):
    S.append(txt(LEFT, y, ln, 15, GRAY))
    y += 20

# ---- source line ---------------------------------------------------------
y += 8
S.append(txt(LEFT, y,
             "Source: experiments/spread_rollout_bakeoff.json "
             "(validations.leave_one_condition_out). Generator: "
             "spread-rollout-bakeoff.py", 15, GRAY))

H = y + 24

defs = (f'<defs>'
        f'<pattern id="hatch" width="9" height="9" '
        f'patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
        f'<rect width="9" height="9" fill="#f7d9d4"/>'
        f'<line x1="0" y1="0" x2="0" y2="9" stroke="{RED}" '
        f'stroke-width="2.6"/></pattern></defs>')

svg = (f'<svg xmlns="http://www.w3.org/2000/svg" '
       f'viewBox="0 0 {W} {int(H)}" font-family="{FONT}">\n'
       f'<rect width="{W}" height="{int(H)}" fill="white"/>\n'
       f'{defs}\n' + "\n".join(S) + "\n</svg>")

out = os.path.join(HERE, "spread-rollout-bakeoff.svg")
with open(out, "w") as f:
    f.write(svg)
print(f"wrote {out}  viewBox 0 0 {W} {int(H)}")
