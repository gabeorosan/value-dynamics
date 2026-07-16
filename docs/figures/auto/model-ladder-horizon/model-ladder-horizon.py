#!/usr/bin/env python3
"""Forecast-error ladder vs horizon, two panels (selection-driven / judge-swap).

Owain Evans-lab house style, matching docs/figures/src/make_figures.py:
white background, headline finding as the title, one subtitle line naming the
measure, real data with fat directly-labeled series. Palette constants and the
esc()/wrap() helpers are copied verbatim from make_figures.py (stdlib only).

Reads experiments/model_ladder_horizon.json (source of truth) and asserts the
plotted MAE values before drawing. Run from this directory:

    python3 model-ladder-horizon.py
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
JSON_PATH = os.path.join(HERE, "..", "..", "..", "..",
                         "experiments", "model_ladder_horizon.json")

# --- palette copied verbatim from make_figures.py -------------------------
INK = "#1a1a1a"
BLUE = "#2867b5"       # accent / self-judge series (validated)
GREEN = "#3a7d44"      # accent / frozen-judge series (validated)
RED = "#b5342c"        # emphasis for reversal / warning text
GRAY = "#6b7684"       # recessive only (axes, muted captions) — never a series
KEY_FILL = "#eef5ee"   # highlighted takeaway box
# two added series colours beyond the make_figures set, both chosen to separate
# from BLUE/GREEN/GRAY under colour-vision deficiency and both paired with a
# distinct line style + a direct word label so identity is never colour-alone:
#   PURPLE  — the parameter-free unit recurrence (Panel A primary line)
#   ORANGE  — the refresh-at-swap model (Panel B only)
PURPLE = "#7a2fb0"
ORANGE = "#c8791d"

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


# --- data ------------------------------------------------------------------
with open(JSON_PATH) as f:
    DATA = json.load(f)


def mae(model, regime_group, horizon):
    for row in DATA["table"]:
        if (row["model"] == model and row["regime_group"] == regime_group
                and row["horizon"] == horizon):
            return row["mae"]
    raise KeyError((model, regime_group, horizon))


# Panel A — selection-driven runs, horizons 1..4
PA = {
    "no_change":          [mae("no_change", "selection_driven", h) for h in (1, 2, 3, 4)],
    "closed_unit":        [mae("closed_unit", "selection_driven", h) for h in (1, 2, 3, 4)],
    "closed_frozen":      [mae("closed_frozen", "selection_driven", h) for h in (1, 2, 3, 4)],
    "one_step_kept_mean": [mae("one_step_kept_mean", "selection_driven", h) for h in (1, 2, 3, 4)],
}
# Panel B — judge-swap runs, horizons 1..8
PB = {
    "no_change":          [mae("no_change", "judge_swap", h) for h in range(1, 9)],
    "closed_frozen":      [mae("closed_frozen", "judge_swap", h) for h in range(1, 9)],
    "refresh_at_swap":    [mae("refresh_at_swap", "judge_swap", h) for h in range(1, 9)],
    "one_step_kept_mean": [mae("one_step_kept_mean", "judge_swap", h) for h in range(1, 9)],
}


def approx(a, b, tol=0.0006):
    return abs(a - b) <= tol


def assert_series(got, want):
    assert len(got) == len(want) and all(approx(g, w) for g, w in zip(got, want)), got


# assert the numbers this figure claims, straight against the file (tol 6e-4)
assert_series(PA["no_change"], [0.3144, 0.4162, 0.4409, 0.4315])
assert_series(PA["closed_unit"], [0.0999, 0.0991, 0.0969, 0.1296])
assert_series(PA["closed_frozen"], [0.1346, 0.1099, 0.1045, 0.126])
assert_series(PA["one_step_kept_mean"], [0.1011, 0.0956, 0.066, 0.0613])
assert_series(PB["no_change"], [0.0824, 0.1637, 0.1836, 0.2008, 0.2317, 0.2919, 0.351, 0.3608])
assert_series(PB["closed_frozen"], [0.098, 0.1104, 0.1425, 0.1748, 0.2318, 0.3217, 0.354, 0.4039])
assert_series(PB["refresh_at_swap"], [0.098, 0.1, 0.0707, 0.0981, 0.174, 0.1784, 0.1674, 0.1794])
assert_series(PB["one_step_kept_mean"], [0.0694, 0.0833, 0.0713, 0.072, 0.1111, 0.0741, 0.1065, 0.0411])

# matched-set (identical runs, four glued grid entries excluded) — the honest
# cost-of-predicting-the-selection gap; annotated at h=1, not drawn as a bracket
GAP = DATA["h1_predicting_vs_observing_selection_gap"]["matched_set_excluding_glued"]
assert GAP["n_runs"] == 32, GAP
assert approx(GAP["one_step_kept_mean_h1_mae"], 0.0849), GAP
assert approx(GAP["closed_unit_h1_mae"], 0.0999), GAP
assert approx(GAP["closed_frozen_h1_mae"], 0.1079), GAP
UNIT_GAP = GAP["closed_unit_h1_mae"] - GAP["one_step_kept_mean_h1_mae"]
FIT_GAP = GAP["closed_frozen_h1_mae"] - GAP["one_step_kept_mean_h1_mae"]
assert approx(UNIT_GAP, 0.015), UNIT_GAP
assert approx(FIT_GAP, 0.023), FIT_GAP

# published anchors all reproduce (cited in the caption)
A = DATA["anchors"]
assert all(A[k]["reproduces"] for k in A), A


# --- geometry --------------------------------------------------------------
W, H = 2060, 926
YMAX = 0.5

# plot boxes
PA_L, PA_R, PA_T, PA_B = 168, 690, 322, 812   # panel A plot rect
PB_L, PB_R, PB_T, PB_B = 1090, 1570, 322, 812  # panel B plot rect


def ya(v):
    return PA_B - (v / YMAX) * (PA_B - PA_T)


def yb(v):
    return PB_B - (v / YMAX) * (PB_B - PB_T)


def xa(h):  # horizon 1..4
    return PA_L + (h - 1) / 3 * (PA_R - PA_L)


def xb(h):  # horizon 1..8
    return PB_L + (h - 1) / 7 * (PB_R - PB_L)


def polyline(pts, color, sw=3.5, dash=None):
    d = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    da = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<polyline points="{d}" fill="none" stroke="{color}" '
            f'stroke-width="{sw}" stroke-linejoin="round"{da}/>')


def markers(pts, color, r=6, fill="white"):
    return "\n".join(
        f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{fill}" stroke="{color}" stroke-width="3"/>'
        for x, y in pts)


def txt(x, y, s, size, color=INK, weight="normal", anchor="start"):
    return (f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" '
            f'fill="{color}" font-weight="{weight}" text-anchor="{anchor}">{esc(s)}</text>')


def grid(left, right, top, bot, yfn):
    s = []
    for gv in (0.0, 0.1, 0.2, 0.3, 0.4, 0.5):
        y = yfn(gv)
        s.append(f'<line x1="{left}" y1="{y:.1f}" x2="{right}" y2="{y:.1f}" '
                 f'stroke="{"#c9ced6" if gv else INK}" stroke-width="{2 if gv==0 else 1}"/>')
        s.append(txt(left - 16, y + 6, f"{gv:.1f}", 22, GRAY, anchor="end"))
    return "\n".join(s)


body = []

# ---- title + subtitle ----
body.append(txt(64, 74, "Forecast error by horizon, under three measurement",
                40, INK, "bold"))
body.append(txt(64, 122, "schedules",
                40, INK, "bold"))
sub = ("Held-out mean absolute error of the predicted value vs rounds ahead; "
       "Qwen + OLMo selection loops.")
body.append(txt(64, 168, sub, 22, GRAY))

# ---- panel headers ----
body.append(txt(PA_L - 46, 268, "Selection-driven runs (36 runs)",
                26, INK, "bold"))
body.append(txt(PB_L - 42, 268, "Judge swapped mid-run (9 runs)",
                26, INK, "bold"))

# shared y-axis title
body.append(f'<text x="40" y="{(PA_T+PA_B)/2}" font-family="{FONT}" font-size="22" '
            f'fill="{INK}" text-anchor="middle" transform="rotate(-90 40 {(PA_T+PA_B)/2})">'
            f'forecast error (MAE)</text>')

# ================= PANEL A =================
body.append(grid(PA_L, PA_R, PA_T, PA_B, ya))
for h in (1, 2, 3, 4):
    body.append(f'<line x1="{xa(h):.1f}" y1="{PA_B}" x2="{xa(h):.1f}" y2="{PA_B+8}" stroke="{INK}" stroke-width="2"/>')
    body.append(txt(xa(h), PA_B + 34, str(h), 22, GRAY, anchor="middle"))
body.append(txt((PA_L + PA_R) / 2, PA_B + 70, "rounds ahead of the first measured pool",
                22, INK, anchor="middle"))

# draw order: recessive/secondary first, the parameter-free primary line last
# so it reads on top. The fitted comparator (blue) is dashed + thinner.
body.append(polyline([(xa(h), ya(PA["no_change"][h - 1])) for h in (1, 2, 3, 4)], GRAY))
body.append(markers([(xa(h), ya(PA["no_change"][h - 1])) for h in (1, 2, 3, 4)], GRAY))
body.append(polyline([(xa(h), ya(PA["one_step_kept_mean"][h - 1])) for h in (1, 2, 3, 4)], GREEN))
body.append(markers([(xa(h), ya(PA["one_step_kept_mean"][h - 1])) for h in (1, 2, 3, 4)], GREEN))
body.append(polyline([(xa(h), ya(PA["closed_frozen"][h - 1])) for h in (1, 2, 3, 4)],
                     BLUE, sw=2.5, dash="8 6"))
body.append(markers([(xa(h), ya(PA["closed_frozen"][h - 1])) for h in (1, 2, 3, 4)], BLUE, r=5))
body.append(polyline([(xa(h), ya(PA["closed_unit"][h - 1])) for h in (1, 2, 3, 4)],
                     PURPLE, sw=4.5))
body.append(markers([(xa(h), ya(PA["closed_unit"][h - 1])) for h in (1, 2, 3, 4)], PURPLE, r=7, fill=PURPLE))

# direct end labels for panel A (to the right of h=4), one short line each; a
# thin leader is drawn only where a label is offset from its endpoint (the purple
# unit-recurrence and dashed-blue fitted endpoints land within 0.004 of each other)
lx = xa(4) + 16
end_a = [
    # key, color, label baseline y, label
    ("no_change", GRAY, 393, "no change"),
    ("closed_unit", PURPLE, 686, "measured once (unit recurrence)"),
    ("closed_frozen", BLUE, 710, "fitted comparator"),
    ("one_step_kept_mean", GREEN, 756, "re-measured every round"),
]
for key, color, ly, lab in end_a:
    py = ya(PA[key][3])
    if abs((ly - 6) - py) > 12:  # thin leader from point to label
        body.append(f'<line x1="{xa(4)+7:.1f}" y1="{py:.1f}" x2="{lx-2}" y2="{ly-6:.1f}" '
                    f'stroke="{color}" stroke-width="1.4"/>')
    body.append(txt(lx, ly, lab, 21, color, "bold"))

# ================= PANEL B =================
body.append(grid(PB_L, PB_R, PB_T, PB_B, yb))
for h in range(1, 9):
    body.append(f'<line x1="{xb(h):.1f}" y1="{PB_B}" x2="{xb(h):.1f}" y2="{PB_B+8}" stroke="{INK}" stroke-width="2"/>')
    body.append(txt(xb(h), PB_B + 34, str(h), 22, GRAY, anchor="middle"))
body.append(txt((PB_L + PB_R) / 2, PB_B + 70, "rounds ahead of the first measured pool",
                22, INK, anchor="middle"))

series_b = [
    ("no_change", GRAY, "no change"),
    ("closed_frozen", BLUE, "measured once"),
    ("refresh_at_swap", ORANGE, "one refresh at swap"),
    ("one_step_kept_mean", GREEN, "re-measured every round"),
]
for key, color, lab in series_b:
    pts = [(xb(h), yb(PB[key][h - 1])) for h in range(1, 9)]
    body.append(polyline(pts, color))
    body.append(markers(pts, color))

# direct end labels for panel B (to the right of h=8), one short line each
for key, color, lab in series_b:
    lx = xb(8) + 16
    ly = yb(PB[key][7]) + 6
    body.append(txt(lx, ly, lab, 21, color, "bold"))

svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
       f'font-family="{FONT}">\n<rect width="{W}" height="{H}" fill="white"/>\n'
       + "\n".join(body) + "\n</svg>")

OUT = os.path.join(HERE, "model-ladder-horizon.svg")
with open(OUT, "w") as f:
    f.write(svg)
print("wrote", OUT)
