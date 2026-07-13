#!/usr/bin/env python3
"""Figure: the K2 release grid — press dominates history; escaping the
pressed floor needs an up-judge AND residual pool material.

Reads the raw round-by-round trajectories (r0..r8) directly from the K2
release-grid rollout JSONs (the same files scripts/score_release_prereg.py
scores against docs/prereg_release_grid_predictions.md). Numbers are
computed here, not copied from docs/report_release_grid_results.md — if
they disagree, trust this script's printed output and the JSON files.

OLMo conservative organism, risk axis. Every seed: 4 rounds under the
frozen conservative judge (the "press"), then either 4 release rounds
under a successor judge, or (for fan_press) the press-release order
reversed, or (for base_hold) 8 rounds under the base judge with no press
at all.

Regenerate:  python3 result-release-grid.py   (from this directory; stdlib only)
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = HERE
while ROOT != os.path.dirname(ROOT) and not os.path.isdir(os.path.join(ROOT, "experiments")):
    ROOT = os.path.dirname(ROOT)

# ---------------------------------------------------------------- palette
# copied verbatim from docs/figures/src/make_figures.py — do not diverge
INK = "#1a1a1a"
BLUE = "#2867b5"        # accent / self-judge series (validated)
GREEN = "#3a7d44"       # accent / frozen-judge series (validated)
RED = "#b5342c"         # emphasis for reversal / warning text
GRAY = "#6b7684"        # recessive only (axes, muted captions) / random-keep series
PURPLE = "#8a5a9e"      # second frozen-judge series (as in Figures 4, 7, 17)
AMBER = "#9a6b15"
KEY_FILL = "#eef5ee"    # highlighted takeaway box
GRAY_TINT = "#f4f4f1"   # recessive background band
FONT = "Helvetica, Arial, sans-serif"
CHAR_W = 0.545          # approx average glyph width, in units of font-size, for Helvetica


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


def rich_text(x, y, segments, size, width, lh=1.38, weight="normal"):
    """segments: list of (text, color, bold). Wraps across segments."""
    words = []
    for text, color, bold in segments:
        for w in text.split():
            words.append((w, color, bold))
    out, line, count = [], [], 0
    for w, color, bold in words:
        if count + len(w) + 1 > width and line:
            out.append(line)
            line, count = [], 0
        line.append((w, color, bold))
        count += len(w) + 1
    if line:
        out.append(line)
    svg = []
    for i, ln in enumerate(out):
        tspans = "".join(
            f'<tspan fill="{c}" font-weight="{"bold" if b else weight}">{esc(w)} </tspan>'
            for w, c, b in ln)
        svg.append(f'<text x="{x}" y="{y + i * size * lh}" font-family="{FONT}" '
                   f'font-size="{size}">{tspans}</text>')
    return "\n".join(svg), y + len(out) * size * lh


def text_block(x, y, text, size, width, color=INK, weight="normal", lh=1.38):
    return rich_text(x, y, [(text, color, weight == "bold")], size, width, lh)


def centered_block(x, y, text, size, width_chars, color=GRAY, lh=1.38):
    """Wraps text and center-anchors every produced line at x."""
    svg, yend = text_block(x, y, text, size, width_chars, color, lh=lh)
    svg = svg.replace('<text ', '<text text-anchor="middle" ')
    return svg, yend


def ctext(b, cx, y, s, size, color=INK, bold=False):
    b.append(f'<text x="{cx}" y="{y}" text-anchor="middle" font-size="{size}" '
             f'font-weight="{"bold" if bold else "normal"}" fill="{color}" '
             f'font-family="{FONT}">{esc(s)}</text>')


def box(x, y, w, h, fill, stroke=INK, sw=2.5, rx=8, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>')


def svg_doc(w, h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
            f'font-family="{FONT}">\n<rect width="{w}" height="{h}" fill="white"/>\n'
            f'{body}\n</svg>')


def text_w(s, size):
    return len(s) * size * CHAR_W


# ---------------------------------------------------------------- data
# Same source files scripts/score_release_prereg.py was run against for
# docs/report_release_grid_results.md's 6/13 table (kernel A/B, Modal
# branch A press_to_base + base_hold). press_hold is not plotted here — the
# prompt's five schedules are press_release, press_random, press_to_base,
# base_hold, fan_press.
DATA_FILES = [
    os.path.join(ROOT, "experiments", "kaggle", "kaggle_k2_release_relA",
                 "output", "k2_release_kernelA.json"),
    os.path.join(ROOT, "experiments", "kaggle", "kaggle_k2_release_relB",
                 "output", "k2_release_kernelB.json"),
    os.path.join(ROOT, "experiments", "modal_k2_release", "output", "k2rel_press_to_base_s1.json"),
    os.path.join(ROOT, "experiments", "modal_k2_release", "output", "k2rel_press_to_base_s2.json"),
    os.path.join(ROOT, "experiments", "modal_k2_release", "output", "k2rel_press_to_base_s3.json"),
    os.path.join(ROOT, "experiments", "modal_k2_release", "output", "k2rel_base_hold_s1.json"),
    os.path.join(ROOT, "experiments", "modal_k2_release", "output", "k2rel_base_hold_s2.json"),
]

TARGET_CONDS = {"press_release", "press_random", "press_to_base", "base_hold", "fan_press"}

recs = {}  # (cond, seed) -> {"traj": [...9...], "judge_used": [...8...]}
for path in DATA_FILES:
    if not os.path.exists(path):
        raise SystemExit(f"missing data file: {path}")
    d = json.load(open(path))
    for sd in (k for k in d if k.isdigit()):
        for cond, rec in d[sd].items():
            if cond not in TARGET_CONDS:
                continue
            traj = rec.get("traj")
            if not traj or len(traj) < 9:
                continue  # incomplete rollout, not part of the 8-round grid
            recs[(cond, int(sd))] = dict(traj=traj[:9], judge_used=rec.get("judge_used", []))

JUDGE_COLOR = {
    "frozen_cons_r0": GREEN,
    "evolving_self": BLUE,
    "random_select": GRAY,
    "frozen_base": PURPLE,
}

FIG_LEGEND = [
    (GREEN, "frozen conservative judge (the press)"),
    (BLUE, "evolving self-judge"),
    (GRAY, "random keep (no judge)"),
    (PURPLE, "frozen base judge"),
]


def seeds_for(cond):
    return {sd: recs[(cond, sd)] for (c, sd) in recs if c == cond}


PR = seeds_for("press_release")
PRND = seeds_for("press_random")
PTB = seeds_for("press_to_base")
BH = seeds_for("base_hold")
FP = seeds_for("fan_press")
assert len(PR) == 3 and len(PRND) == 3 and len(PTB) == 3 and len(BH) == 2 and len(FP) == 2, \
    f"unexpected seed counts: pr={len(PR)} prnd={len(PRND)} ptb={len(PTB)} bh={len(BH)} fp={len(FP)}"

# ------------- numbers used in headline/annotations, computed here -------------
pr_r8 = [PR[sd]["traj"][8] for sd in PR]
pr_r8_mean = sum(pr_r8) / len(pr_r8)
pr_max_rebound = max(PR[sd]["traj"][8] - PR[sd]["traj"][4] for sd in PR)

fp_r8 = [FP[sd]["traj"][8] for sd in FP]

prnd_max_dev = max(abs(PRND[sd]["traj"][8] - PRND[sd]["traj"][4]) for sd in PRND)

ptb_r4 = {sd: PTB[sd]["traj"][4] for sd in PTB}
ptb_r8 = {sd: PTB[sd]["traj"][8] for sd in PTB}
ptb_r8_mean = sum(ptb_r8.values()) / len(ptb_r8)

bh_r8 = {sd: BH[sd]["traj"][8] for sd in BH}

print("=== numbers computed from the raw JSONs (should match the report) ===")
print(f"press_release r8: {sorted(round(v,3) for v in pr_r8)}  mean={pr_r8_mean:.3f}  "
      f"max rebound over r4={pr_max_rebound:+.3f}")
print(f"fan_press r8: {sorted(round(v,3) for v in fp_r8)}")
print(f"press_random max |r8-r4| deviation: {prnd_max_dev:.3f}")
print(f"press_to_base r4->r8 by seed: " +
      ", ".join(f"s{sd} {ptb_r4[sd]:.3f}->{ptb_r8[sd]:.3f}" for sd in sorted(ptb_r4)) +
      f"  mean r8={ptb_r8_mean:.3f}")
print(f"base_hold r8 by seed: " + ", ".join(f"s{sd} {bh_r8[sd]:.3f}" for sd in sorted(bh_r8)))

# ---------------------------------------------------------------- figure
W = 1520
b = []

ctext(b, W / 2, 50, "The press dominates history —", 31, INK, True)
ctext(b, W / 2, 87, "escaping the pressed floor needs an up-judge AND residual pool material", 27, INK, True)

subtitle = ("K2 release grid, OLMo conservative organism, risk axis. Pool risk = mean gamble-risk score of the "
            "judge's kept top-2-of-6 candidates, averaged over 12 battery items, read once per round. Press = "
            "frozen conservative judge, rounds 0–4 (rounds 4–8 for fan_press; all 8 rounds for base_hold's "
            "never-pressed contrast).")
sub_svg, sub_end = centered_block(W / 2, 116, subtitle, 15, 155, GRAY)
b.append(sub_svg)

# ---- shared legend row (precise pixel widths, no guessing) ----
LEG_Y = sub_end + 22
leg_size = 14.5
items = FIG_LEGEND + [("SWATCH", "background = press phase")]
total_w = 0
widths = []
for color, label in items:
    lw = 28 + 8 + text_w(label, leg_size) + 34  # swatch + gap + text + trailing space
    widths.append(lw)
    total_w += lw
lx = (W - total_w) / 2
for (color, label), lw in zip(items, widths):
    if color == "SWATCH":
        b.append(f'<rect x="{lx:.1f}" y="{LEG_Y-11:.1f}" width="26" height="14" fill="{GRAY_TINT}" stroke="{INK}" stroke-width="1.2"/>')
        b.append(f'<text x="{lx+34:.1f}" y="{LEG_Y+5:.1f}" font-size="{leg_size}" fill="{INK}" font-family="{FONT}">{esc(label)}</text>')
    else:
        b.append(f'<line x1="{lx:.1f}" y1="{LEG_Y}" x2="{lx+28:.1f}" y2="{LEG_Y}" stroke="{color}" stroke-width="4"/>')
        b.append(f'<text x="{lx+36:.1f}" y="{LEG_Y+5:.1f}" font-size="{leg_size}" fill="{INK}" font-family="{FONT}">{esc(label)}</text>')
    lx += lw

YMIN, YMAX = 0.0, 0.9
PW, PH = 410, 268
GAP = 75
ROW1_Y = LEG_Y + 60
COL_X = [70, 70 + PW + GAP, 70 + 2 * (PW + GAP)]
ROW2_X0 = 70 + ((2 * (PW + GAP)) - GAP) / 2 - PW / 2 + GAP / 2  # centered under the 3-col row (row width = 3*PW+2*GAP)
ROW2_X0 = 70 + (3 * PW + 2 * GAP - (2 * PW + GAP)) / 2
ROW2_X = [ROW2_X0, ROW2_X0 + PW + GAP]

CAP_W = 64   # caption wrap width, chars — kept narrow enough that even a
             # digit-heavy line stays inside panel_width + gap (no cross-panel bleed)
CAP_SIZE = 13
CAP_LH = 1.38


def cap_height(text):
    n = len(wrap(text, CAP_W))
    return n * CAP_SIZE * CAP_LH


def panel_axes(b, ax, ay, title, xlab_extra=""):
    for v in (0.0, 0.2, 0.4, 0.6, 0.8):
        yy = ay + PH * (YMAX - v) / (YMAX - YMIN)
        b.append(f'<line x1="{ax}" y1="{yy:.1f}" x2="{ax+PW}" y2="{yy:.1f}" stroke="#e4e4e0" stroke-width="1"/>')
        b.append(f'<text x="{ax-8}" y="{yy+5:.1f}" text-anchor="end" font-size="12.5" fill="{GRAY}" font-family="{FONT}">{v:.1f}</text>')
    for r in range(9):
        xx = ax + PW * r / 8
        b.append(f'<text x="{xx:.1f}" y="{ay+PH+20}" text-anchor="middle" font-size="12" fill="{GRAY}" font-family="{FONT}">{r}</text>')
    b.append(f'<text x="{ax+PW/2}" y="{ay+PH+40}" text-anchor="middle" font-size="13.5" fill="{INK}" font-family="{FONT}">round{esc(xlab_extra)}</text>')
    ctext(b, ax + PW / 2, ay - 16, title, 17, INK, True)


def panel_yaxis_label(b, ax, ay):
    b.append(f'<text x="{ax-46}" y="{ay+PH/2}" font-size="13" fill="{INK}" font-family="{FONT}" '
             f'transform="rotate(-90 {ax-46} {ay+PH/2})" text-anchor="middle">pool risk</text>')


def shade_press(b, ax, ay, lo_round, hi_round):
    if lo_round is None:
        return
    x0 = ax + PW * lo_round / 8
    x1 = ax + PW * hi_round / 8
    b.append(f'<rect x="{x0:.1f}" y="{ay}" width="{x1-x0:.1f}" height="{PH}" fill="{GRAY_TINT}"/>')
    b.append(f'<line x1="{x0:.1f}" y1="{ay}" x2="{x0:.1f}" y2="{ay+PH}" stroke="#d8d8d3" stroke-width="1"/>')
    b.append(f'<line x1="{x1:.1f}" y1="{ay}" x2="{x1:.1f}" y2="{ay+PH}" stroke="#d8d8d3" stroke-width="1"/>')


def press_span(judge_used, press_key="frozen_cons_r0"):
    idxs = [i for i, j in enumerate(judge_used) if j == press_key]
    if not idxs:
        return None, None
    return min(idxs), max(idxs) + 1  # round-range [lo, hi]


def px_of(ax, r):
    return ax + PW * r / 8


def py_of(ay, v):
    return ay + PH * (YMAX - v) / (YMAX - YMIN)


def draw_traj(b, ax, ay, traj, judge_used, width=3, opacity=1.0, dot_r=4.2):
    for k in range(8):
        color = JUDGE_COLOR[judge_used[k]]
        b.append(f'<line x1="{px_of(ax,k):.1f}" y1="{py_of(ay,traj[k]):.1f}" x2="{px_of(ax,k+1):.1f}" y2="{py_of(ay,traj[k+1]):.1f}" '
                 f'stroke="{color}" stroke-width="{width}" stroke-opacity="{opacity}"/>')
    for r, v in enumerate(traj):
        color = JUDGE_COLOR[judge_used[r]] if r < len(judge_used) else JUDGE_COLOR[judge_used[-1]]
        b.append(f'<circle cx="{px_of(ax,r):.1f}" cy="{py_of(ay,v):.1f}" r="{dot_r}" fill="{color}" fill-opacity="{opacity}" '
                 f'stroke="white" stroke-width="1.2"/>')


def end_label(b, ax, ay, traj, text, color, anchor="start", dx=8, dy=5):
    x = px_of(ax, 8) + dx
    y = py_of(ay, traj[8]) + dy
    b.append(f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" font-size="13" font-weight="bold" '
             f'fill="{color}" font-family="{FONT}">{esc(text)}</text>')


def label_at(b, ax, ay, r, v, text, color, anchor="start", dx=0, dy=0):
    """Label placed at an explicit (round, pool-risk) data coordinate, independent of
    any trajectory endpoint — used where an endpoint-relative offset would still land
    on a nearby marker (e.g. a trajectory that peaks near its own final round)."""
    x = px_of(ax, r) + dx
    y = py_of(ay, v) + dy
    b.append(f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" font-size="13" font-weight="bold" '
             f'fill="{color}" font-family="{FONT}">{esc(text)}</text>')


def floor_line(b, ax, ay, label="the floor (0.000)"):
    y0 = py_of(ay, 0.0)
    b.append(f'<line x1="{ax}" y1="{y0:.1f}" x2="{ax+PW}" y2="{y0:.1f}" stroke="{RED}" stroke-width="1.6" stroke-dasharray="5 4"/>')
    b.append(f'<text x="{ax+6}" y="{y0-6:.1f}" font-size="12" fill="{RED}" font-family="{FONT}">{esc(label)}</text>')


def threshold_line(b, ax, ay, v, label, color=GRAY, side="start"):
    yy = py_of(ay, v)
    b.append(f'<line x1="{ax}" y1="{yy:.1f}" x2="{ax+PW}" y2="{yy:.1f}" stroke="{color}" stroke-width="1.4" stroke-dasharray="3 4"/>')
    tx = ax + 4 if side == "start" else ax + PW - 4
    b.append(f'<text x="{tx:.1f}" y="{yy-6:.1f}" text-anchor="{side}" font-size="12" fill="{color}" font-family="{FONT}">{esc(label)}</text>')


# ================= Panel 1: press_release =================
ax, ay = COL_X[0], ROW1_Y
panel_axes(b, ax, ay, "press_release: release to self", " (press r0–4, release r4–8)")
panel_yaxis_label(b, ax, ay)
lo, hi = press_span(PR[1]["judge_used"])
shade_press(b, ax, ay, lo, hi)
floor_line(b, ax, ay)
for sd in sorted(PR):
    draw_traj(b, ax, ay, PR[sd]["traj"], PR[sd]["judge_used"], width=2.6, opacity=0.9)
b.append(f'<text x="{ax+16:.1f}" y="{py_of(ay,0.14):.1f}" font-size="13.5" font-weight="bold" fill="{RED}" '
         f'font-family="{FONT}">r8 mean {pr_r8_mean:.3f} — 0/3 seeds rebound</text>')
cap1 = (f"3 seeds; r8 mean {pr_r8_mean:.3f}, max rebound over r4 {pr_max_rebound:+.3f}. Released to its own "
        "evolving judge, the pressed pool stays at the floor.")
t, _ = text_block(ax, ay + PH + 48, cap1, CAP_SIZE, CAP_W, GRAY, lh=CAP_LH)
b.append(t)

# ================= Panel 2: fan_press =================
ax, ay = COL_X[1], ROW1_Y
panel_axes(b, ax, ay, "fan_press: fan then press", " (fan r0–4, press r4–8)")
lo, hi = press_span(FP[1]["judge_used"])
shade_press(b, ax, ay, lo, hi)
floor_line(b, ax, ay)
for sd in sorted(FP):
    draw_traj(b, ax, ay, FP[sd]["traj"], FP[sd]["judge_used"], width=2.6, opacity=0.9)
b.append(f'<text x="{ax+16:.1f}" y="{py_of(ay,0.14):.1f}" font-size="13.5" font-weight="bold" fill="{RED}" '
         f'font-family="{FONT}">both seeds end 0.000 — same floor as press_release</text>')
cap2 = ("2 seeds, order reversed (self-judge phase first). r8 = 0.000, 0.000 — the identical press-alone "
        "floor: order does not change the endpoint here.")
t, _ = text_block(ax, ay + PH + 48, cap2, CAP_SIZE, CAP_W, GRAY, lh=CAP_LH)
b.append(t)

# ================= Panel 3: press_random =================
ax, ay = COL_X[2], ROW1_Y
panel_axes(b, ax, ay, "press_random: release to random keep", " (press r0–4, release r4–8)")
lo, hi = press_span(PRND[1]["judge_used"])
shade_press(b, ax, ay, lo, hi)
for sd in sorted(PRND):
    draw_traj(b, ax, ay, PRND[sd]["traj"], PRND[sd]["judge_used"], width=2.6, opacity=0.9)
seed3_traj = PRND[3]["traj"]
xr4 = px_of(ax, 4)
yr4 = py_of(ay, seed3_traj[4])
yr8 = py_of(ay, seed3_traj[8])
b.append(f'<line x1="{xr4:.1f}" y1="{yr4:.1f}" x2="{xr4:.1f}" y2="{yr8:.1f}" stroke="{AMBER}" stroke-width="1.4" stroke-dasharray="2 3"/>')
b.append(f'<text x="{xr4+8:.1f}" y="{(yr4+yr8)/2:.1f}" font-size="12.5" font-weight="bold" fill="{AMBER}" font-family="{FONT}">seed 3: Δ = 0.156</text>')
cap3 = (f"3 seeds; max |r8−r4| deviation {prnd_max_dev:.3f} (seed 3, above the pre-registered ±0.05 "
        "band) but no seed rails either direction — drift without a direction.")
t, _ = text_block(ax, ay + PH + 48, cap3, CAP_SIZE, CAP_W, GRAY, lh=CAP_LH)
b.append(t)

ROW1_CAP_H = max(cap_height(cap1), cap_height(cap2), cap_height(cap3))
ROW2_Y = ROW1_Y + PH + 48 + ROW1_CAP_H + 56

# ================= Panel 4: press_to_base =================
ax, ay = ROW2_X[0], ROW2_Y
panel_axes(b, ax, ay, "press_to_base: release to the base judge", " (press r0–4, release r4–8)")
panel_yaxis_label(b, ax, ay)
lo, hi = press_span(PTB[1]["judge_used"])
shade_press(b, ax, ay, lo, hi)
threshold_line(b, ax, ay, 0.5, "rail threshold used to score this schedule (0.5)", GRAY, side="start")
for sd in sorted(PTB):
    draw_traj(b, ax, ay, PTB[sd]["traj"], PTB[sd]["judge_used"], width=3.1, opacity=1.0)
# small stacked in-panel key, in the one genuinely empty region (top-left, over
# the press-phase shading, well above all three lines through round 3) — avoids
# every marker/line in this crowded panel rather than chasing each endpoint
label_at(b, ax, ay, 0.25, 0.855, f"seed 1: {ptb_r8[1]:.3f} (stuck)", RED, anchor="start")
label_at(b, ax, ay, 0.25, 0.775, f"seed 2: {ptb_r8[2]:.3f} (rising)", PURPLE, anchor="start")
label_at(b, ax, ay, 0.25, 0.695, f"seed 3: {ptb_r8[3]:.3f} (railed)", PURPLE, anchor="start")
cap4 = (f"3 seeds; r4→r8: {ptb_r4[1]:.3f}→{ptb_r8[1]:.3f}, {ptb_r4[2]:.3f}→{ptb_r8[2]:.3f}, "
        f"{ptb_r4[3]:.3f}→{ptb_r8[3]:.3f} (mean {ptb_r8_mean:.3f} vs press_release's {pr_r8_mean:.3f}). "
        "Seed 1's pool had spread 0.000 (no material left) at the switch and never moved; seeds 2 and 3 kept "
        "spread and climbed — an up-judge alone wasn't enough for seed 1.")
t, _ = text_block(ax, ay + PH + 48, cap4, CAP_SIZE, CAP_W, GRAY, lh=CAP_LH)
b.append(t)

# ================= Panel 5: base_hold =================
ax, ay = ROW2_X[1], ROW2_Y
panel_axes(b, ax, ay, "base_hold: never pressed, held 8 rounds", " (base judge r0–8, no press)")
threshold_line(b, ax, ay, 0.4, "up-rail threshold from the 4-round grid (0.4)", GRAY, side="start")
for sd in sorted(BH):
    draw_traj(b, ax, ay, BH[sd]["traj"], BH[sd]["judge_used"], width=3.4, opacity=1.0)
end_label(b, ax, ay, BH[1]["traj"], f"seed 1: {bh_r8[1]:.3f}", PURPLE, dx=14, dy=18)
end_label(b, ax, ay, BH[2]["traj"], f"seed 2: {bh_r8[2]:.3f}", PURPLE, dx=14, dy=-10)
# mark seed 1's late crossing of the 0.4 threshold at round 5
xr5 = px_of(ax, 5)
yr5 = py_of(ay, BH[1]["traj"][5])
b.append(f'<circle cx="{xr5:.1f}" cy="{yr5:.1f}" r="8" fill="none" stroke="{RED}" stroke-width="1.8"/>')
b.append(f'<text x="{xr5:.1f}" y="{yr5+40:.1f}" text-anchor="middle" font-size="12" fill="{RED}" font-family="{FONT}">seed 1 crosses 0.4 at r5</text>')
cap5 = (f"2 seeds, no press phase. Both rail above 0.4 by r8 (finals {bh_r8[1]:.3f}, {bh_r8[2]:.3f}); seed 1 "
        "crosses late (round 5), seed 2 already high by round 1. Contrast: what the base judge does with an "
        "untouched pool.")
t, _ = text_block(ax, ay + PH + 48, cap5, CAP_SIZE, CAP_W, GRAY, lh=CAP_LH)
b.append(t)

ROW2_CAP_H = max(cap_height(cap4), cap_height(cap5))

# ================= takeaway =================
TY = ROW2_Y + PH + 48 + ROW2_CAP_H + 40
takeaway_segs = [
    ("Escaping a pressed floor needs an up-judge AND residual pool material — neither alone is enough. ",
     INK, True),
    ("press_release and fan_press reach the same floor in either order (r8 ≈ 0.000–0.003) — the "
     "press dominates history over the 2 fan_press seeds tested. Release to random keep diffuses (deviation up to "
     f"{prnd_max_dev:.3f}) but never rails — drift without direction. Release to the base judge, the one "
     "judge with an up-tail, only escapes the floor where the switch left live pool material: the dead-pool seed "
     f"(spread 0.000 at r4) stays at exactly 0.000, while the two seeds with residual spread reach {ptb_r8[2]:.3f} "
     f"and {ptb_r8[3]:.3f} — short of base_hold's never-pressed {bh_r8[1]:.3f} and {bh_r8[2]:.3f}, whose pool "
     "was never thinned by a press. This is the release-side complement of the spread-exhaustion result (fig19): "
     "selection needs both a compatible judge and material in the pool to act on. 6 of 13 preregistered "
     "release-grid criteria passed — see docs/report_release_grid_results.md for the full per-criterion table "
     "and docs/prereg_release_grid_predictions.md for what was predicted in advance.",
     INK, False),
]
tt, tend = rich_text(90, TY + 30, takeaway_segs, 15.5, 148)
box_h = (tend - TY) + 26
b_takeaway = box(70, TY, W - 140, box_h, KEY_FILL, INK, 2.5)

svg_body = b_takeaway + "\n" + tt
H = TY + box_h + 30
svg = svg_doc(W, H, "\n".join(b) + "\n" + svg_body)
out = os.path.join(HERE, "result-release-grid.svg")
with open(out, "w") as f:
    f.write(svg)
print(f"\nwrote {out}  ({W}x{H:.0f})")
