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
# one added series colour for the refresh model (Panel B only); orange, chosen
# to separate from BLUE/GREEN/GRAY under colour-vision deficiency
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
assert_series(PA["closed_frozen"], [0.1346, 0.1099, 0.1045, 0.126])
assert_series(PA["one_step_kept_mean"], [0.1011, 0.0956, 0.066, 0.0613])
assert_series(PB["no_change"], [0.0824, 0.1637, 0.1836, 0.2008, 0.2317, 0.2919, 0.351, 0.3608])
assert_series(PB["closed_frozen"], [0.098, 0.1104, 0.1425, 0.1748, 0.2318, 0.3217, 0.354, 0.4039])
assert_series(PB["refresh_at_swap"], [0.098, 0.1, 0.0707, 0.0981, 0.174, 0.1784, 0.1674, 0.1794])
assert_series(PB["one_step_kept_mean"], [0.0694, 0.0833, 0.0713, 0.072, 0.1111, 0.0741, 0.1065, 0.0411])
h1_gap = PA["closed_frozen"][0] - PA["one_step_kept_mean"][0]
assert approx(h1_gap, 0.0335), h1_gap


# --- geometry --------------------------------------------------------------
W, H = 2060, 1010
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


def polyline(pts, color, sw=3.5):
    d = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    return f'<polyline points="{d}" fill="none" stroke="{color}" stroke-width="{sw}" stroke-linejoin="round"/>'


def markers(pts, color, r=6):
    return "\n".join(
        f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="white" stroke="{color}" stroke-width="3"/>'
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
body.append(txt(64, 74, "Measure the run once and roll a simple model forward:",
                40, INK, "bold"))
body.append(txt(64, 122, "forecast error stays flat with horizon — until the judge changes.",
                40, INK, "bold"))
sub = ("Held-out-condition mean absolute error of the predicted behavioral value "
       "(0–1 scale), Qwen + OLMo selection loops. Each model is given the run's "
       "state once at round 1, at every round, or once plus once at the judge swap; "
       "error is averaged over runs at each number of rounds ahead of the first "
       "measured answer pool.")
for i, ln in enumerate(wrap(sub, 118)):
    body.append(txt(64, 168 + i * 30, ln, 22, GRAY))

# ---- panel headers ----
body.append(txt(PA_L - 46, 268, "Selection-driven runs (36 runs): trajectories saturate",
                26, INK, "bold"))
body.append(txt(PB_L - 42, 268, "Judge swapped mid-run (9 runs): the target keeps moving",
                26, INK, "bold"))

# shared y-axis title
body.append(f'<text x="40" y="{(PA_T+PA_B)/2}" font-family="{FONT}" font-size="22" '
            f'fill="{INK}" text-anchor="middle" transform="rotate(-90 40 {(PA_T+PA_B)/2})">'
            f'forecast error (mean absolute error of predicted value)</text>')

# ================= PANEL A =================
body.append(grid(PA_L, PA_R, PA_T, PA_B, ya))
for h in (1, 2, 3, 4):
    body.append(f'<line x1="{xa(h):.1f}" y1="{PA_B}" x2="{xa(h):.1f}" y2="{PA_B+8}" stroke="{INK}" stroke-width="2"/>')
    body.append(txt(xa(h), PA_B + 34, str(h), 22, GRAY, anchor="middle"))
body.append(txt((PA_L + PA_R) / 2, PA_B + 70, "rounds ahead of the first measured pool",
                22, INK, anchor="middle"))

series_a = [
    ("no_change", GRAY, "predict the starting value", "forever (no change)"),
    ("closed_frozen", BLUE, "measured once at round 1", "(frozen selection model)"),
    ("one_step_kept_mean", GREEN, "re-measured every round", "(mean of the kept answers)"),
]
for key, color, lab1, lab2 in series_a:
    pts = [(xa(h), ya(PA[key][h - 1])) for h in (1, 2, 3, 4)]
    body.append(polyline(pts, color))
    body.append(markers(pts, color))

# direct end labels for panel A (to the right of h=4)
end_a = {
    "no_change": (PA["no_change"][3], 4),
    "closed_frozen": (PA["closed_frozen"][3], -8),
    "one_step_kept_mean": (PA["one_step_kept_mean"][3], 22),
}
for key, color, lab1, lab2 in series_a:
    v, dy = end_a[key]
    lx = xa(4) + 16
    ly = ya(v) + dy
    body.append(txt(lx, ly, lab1, 21, color, "bold"))
    body.append(txt(lx, ly + 25, lab2, 19, color))

# h=1 bracket: cost of predicting vs observing (~0.03)
bx = xa(1)
yb_top = ya(PA["closed_frozen"][0])   # 0.135
yb_bot = ya(PA["one_step_kept_mean"][0])  # 0.101
brx = bx - 20
body.append(f'<path d="M {bx-4} {yb_top:.1f} H {brx} V {yb_bot:.1f} H {bx-4}" '
            f'fill="none" stroke="{INK}" stroke-width="2"/>')
# leader to callout text sitting in the open middle band
cx, cy = PA_L + 92, ya(0.245)
body.append(f'<line x1="{brx}" y1="{(yb_top+yb_bot)/2:.1f}" x2="{cx-8}" y2="{cy+6:.1f}" '
            f'stroke="{INK}" stroke-width="1.6"/>')
for i, ln in enumerate(wrap("at 1 round ahead both models see the same pool; the gap "
                            "(~0.03) is the cost of predicting the selection instead "
                            "of observing it", 30)):
    body.append(txt(cx, cy + i * 24, ln, 18, INK, "bold" if i == 0 else "normal"))

# ================= PANEL B =================
body.append(grid(PB_L, PB_R, PB_T, PB_B, yb))
for h in range(1, 9):
    body.append(f'<line x1="{xb(h):.1f}" y1="{PB_B}" x2="{xb(h):.1f}" y2="{PB_B+8}" stroke="{INK}" stroke-width="2"/>')
    body.append(txt(xb(h), PB_B + 34, str(h), 22, GRAY, anchor="middle"))
body.append(txt((PB_L + PB_R) / 2, PB_B + 70, "rounds ahead of the first measured pool",
                22, INK, anchor="middle"))

series_b = [
    ("no_change", GRAY, "predict the starting value forever", "(no change)"),
    ("closed_frozen", BLUE, "measured once at round 1", "(frozen selection model)"),
    ("refresh_at_swap", ORANGE, "one refresh at the judge swap", "(re-measure once, then roll)"),
    ("one_step_kept_mean", GREEN, "re-measured every round", "(mean of the kept answers)"),
]
for key, color, lab1, lab2 in series_b:
    pts = [(xb(h), yb(PB[key][h - 1])) for h in range(1, 9)]
    body.append(polyline(pts, color))
    body.append(markers(pts, color))

end_b = {
    "closed_frozen": (PB["closed_frozen"][7], -12),
    "no_change": (PB["no_change"][7], 18),
    "refresh_at_swap": (PB["refresh_at_swap"][7], 4),
    "one_step_kept_mean": (PB["one_step_kept_mean"][7], 24),
}
for key, color, lab1, lab2 in series_b:
    v, dy = end_b[key]
    lx = xb(8) + 16
    ly = yb(v) + dy
    body.append(txt(lx, ly, lab1, 21, color, "bold"))
    body.append(txt(lx, ly + 25, lab2, 19, color))

# note on where the swaps happen
for i, ln in enumerate(wrap("The judge is swapped somewhere in rounds 2–5 depending "
                            "on the condition; a single re-measurement at the swap buys "
                            "back most of the loss the frozen model takes on afterward.",
                            56)):
    body.append(txt(PB_L, PB_B + 108 + i * 26, ln, 20, INK))

# ---- takeaway strip (bottom-left, under panel A) ----
ty = 900
body.append(txt(64, ty, "Reading rule:", 22, INK, "bold"))
read = ("the re-measuring models look better only because they are handed each "
        "round's observed answer pool — the gap over the measure-once model is "
        "the value of monitoring, not a better model.")
for i, ln in enumerate(wrap(read, 62)):
    body.append(txt(64, ty + 30 + i * 26, ln, 20, GRAY))

svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
       f'font-family="{FONT}">\n<rect width="{W}" height="{H}" fill="white"/>\n'
       + "\n".join(body) + "\n</svg>")

OUT = os.path.join(HERE, "model-ladder-horizon.svg")
with open(OUT, "w") as f:
    f.write(svg)
print("wrote", OUT)
