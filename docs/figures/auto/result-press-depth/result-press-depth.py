#!/usr/bin/env python3
"""Draft figure: the K2 press-depth map — does the number of conservative-press
rounds before release gate the outcome?

Loads the six raw K2 release-program cells directly (press_d1/d2/d3, seeds 1
and 2) and recomputes, from the raw per-item pool_risk fields, both the r0->r8
pool-risk trajectories and the "switch-round pool spread" (the population SD
of item-level pool means at the round where the judge switches from
conservative to base). Nothing here is copied from the prose report — only
the pre-registered verdict labels (criteria 1-5) and the criterion-5 RMSE
number are quoted from the report, since that comparison lives in a separate
fitted-predictor artifact not reproduced here; both are cited in the source
note on the figure and in caption.md.

Source data:
  experiments/modal_k2_release/output/k2rel_press_d1_s1.json
  experiments/modal_k2_release/output/k2rel_press_d1_s2.json
  experiments/modal_k2_release/output/k2rel_press_d2_s1.json
  experiments/modal_k2_release/output/k2rel_press_d2_s2.json
  experiments/modal_k2_release/output/k2rel_press_d3_s1.json
  experiments/modal_k2_release/output/k2rel_press_d3_s2.json
Report (prereg verdicts, criterion-5 RMSE, audit corrections):
  docs/report_press_depth_boundary.md

Regenerate with:  python3 result-press-depth.py   (from this directory; stdlib only)
"""
import json
import os
import statistics

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = HERE
while ROOT != os.path.dirname(ROOT) and not os.path.isdir(os.path.join(ROOT, "experiments")):
    ROOT = os.path.dirname(ROOT)

DATA_DIR = os.path.join(ROOT, "experiments", "modal_k2_release", "output")

INK = "#1a1a1a"
BLUE = "#2867b5"
GREEN = "#3a7d44"
RED = "#b5342c"
GRAY = "#6b7684"
AMBER = "#9a6b15"
KEY_FILL = "#eef5ee"
AMBER_TINT = "#fdf8ee"
GREEN_TINT = "#eef7f0"
RED_TINT = "#fbf0ee"

FONT = "Helvetica, Arial, sans-serif"


# ------------------------------------------------------------ house helpers
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


def box(x, y, w, h, fill, stroke=INK, sw=2.5, rx=8):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')


def svg_doc(w, h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
            f'font-family="{FONT}">\n<rect width="{w}" height="{h}" fill="white"/>\n'
            f'{body}\n</svg>')


# ------------------------------------------------------------------- data
CELLS = [  # (depth, seed, filename, condition-key)
    (1, "1", "k2rel_press_d1_s1.json", "press_d1"),
    (1, "2", "k2rel_press_d1_s2.json", "press_d1"),
    (2, "1", "k2rel_press_d2_s1.json", "press_d2"),
    (2, "2", "k2rel_press_d2_s2.json", "press_d2"),
    (3, "1", "k2rel_press_d3_s1.json", "press_d3"),
    (3, "2", "k2rel_press_d3_s2.json", "press_d3"),
]

cell = {}
for depth, seed, fname, cond in CELLS:
    d = json.load(open(os.path.join(DATA_DIR, fname)))
    rec = d[seed][cond]
    traj = rec["traj"]
    assert len(traj) == 9, f"{fname}: expected r0..r8 (9 points), got {len(traj)}"
    rr = rec["rounds_raw"]
    # switch happens after round == depth; the pool being switched away from
    # is rounds_raw[depth-1] (its item pool_risk values feed round `depth`
    # of the trajectory) — this is the "switch-round pool spread".
    spread = statistics.mean(statistics.pstdev(it["cand_risk"]) for it in rr[depth - 1])
    cell[(depth, seed)] = dict(traj=traj, spread=spread, r8=traj[8])

# sanity check against the pre-registered / reported numbers this figure claims
_expect_traj = {
    (1, "1"): [0.308, 0.333, 0.083, 0.375, 0.208, 0.000, 0.000, 0.042, 0.000],
    (1, "2"): [0.301, 0.429, 0.625, 0.542, 0.583, 0.417, 0.667, 1.000, 1.000],
    (2, "1"): [0.308, 0.208, 0.167, 0.125, 0.042, 0.000, 0.167, 0.083, 0.105],
    (2, "2"): [0.301, 0.391, 0.417, 0.609, 0.708, 0.958, 0.875, 1.000, 0.938],
    (3, "1"): [0.308, 0.292, 0.208, 0.000, 0.083, 0.333, 0.417, 0.125, 0.229],
    (3, "2"): [0.301, 0.292, 0.208, 0.292, 0.417, 0.542, 0.667, 0.625, 0.823],
}
for k, exp in _expect_traj.items():
    got = [round(v, 3) for v in cell[k]["traj"]]
    assert got == exp, f"{k}: traj mismatch, expected {exp} got {got}"

RANGES = {}
for depth in (1, 2, 3):
    lo = cell[(depth, "1")]["r8"]
    hi = cell[(depth, "2")]["r8"]
    RANGES[depth] = (lo, hi, hi - lo)

# pre-registered verdicts (docs/report_press_depth_boundary.md; reproduced
# verbatim by scripts/score_press_depth_prereg.py) — not recomputed here,
# since criterion 5 depends on a separately-fitted predictor artifact
# (experiments/release_predictor_nogap_frozen.json) outside this script's scope
PREREG = [
    ("1", "switch-spread mediator: spread > 0.10 predicts r8 > 0.30",
     "all 6 cells had prereg-form spread 0.278-0.423, yet 3 ended at 0.000 / 0.105 / 0.229", "FAIL"),
    ("2", "depth-1 behaves like base_hold (2 of 2 seeds end > 0.40)",
     "depth-1 split 0.000 vs 1.000 - one seed under 0.40", "FAIL"),
    ("3", "no depth-1 or depth-2 cell reaches 0.000",
     "depth-1 seed 1 hit 0.000 by round 5 and stayed there", "FAIL"),
    ("4", "depth-3 boundary signature (split >= 0.40 or an endpoint < 0.10)",
     "depth-3 split is 0.594", "PASS"),
    ("5", "a frozen (gap-aware) predictor beats a matched no-gap comparator",
     "-42.0% RMSE on 42 blind transitions (experiments/release_predictor_nogap_frozen.json)", "PASS"),
]

# ------------------------------------------------------------------ figure
b = []
W = 1370

t, ynext = text_block(W / 2, 50, "There is no depth boundary in the K2 press-then-release program —", 30, 74, weight="bold")
b.append(t.replace('<text ', '<text text-anchor="middle" ', 1))
t, ynext = text_block(W / 2, 92, "paired high/low streams persist while endpoint range narrows", 30, 74, weight="bold")
b.append(t.replace('<text ', '<text text-anchor="middle" ', 1))
t, _ = text_block(W / 2, 126,
                  "3 press depths (1-3 conservative-judge rounds before the base-judge switch) × 2 seeds, "
                  "rounds 0→8; K2 release program, Modal branch c.", 17.5, 200, GRAY)
b.append(t.replace('<text ', '<text text-anchor="middle" ', 1))
t, _ = text_block(W / 2, 150,
                  "n = 2 seeds per depth — a paired high/low-endpoint pattern, not an identified boundary law "
                  "(audit note in the source report).", 14.5, 200, GRAY)
b.append(t.replace('<text ', '<text text-anchor="middle" ', 1))

# shared legend (colors hold across all three panels and the fan below)
ly = 190
b.append(f'<circle cx="{W/2-215}" cy="{ly-5}" r="6.5" fill="{BLUE}"/>')
b.append(f'<text x="{W/2-200}" y="{ly}" font-size="15.5" fill="{INK}" font-family="{FONT}">seed 1 — ends low at every depth</text>')
b.append(f'<circle cx="{W/2+55}" cy="{ly-5}" r="6.5" fill="{RED}"/>')
b.append(f'<text x="{W/2+70}" y="{ly}" font-size="15.5" fill="{INK}" font-family="{FONT}">seed 2 — ends high (rails) at every depth</text>')

# ================= three trajectory panels =================
PANEL_W, GAP = 350, 60
PLOT_W = 290
LEFT = 110
PX = [LEFT, LEFT + PANEL_W + GAP, LEFT + 2 * (PANEL_W + GAP)]
PY, PH = 268, 240
LETTERS = ["A", "B", "C"]

for i, depth in enumerate((1, 2, 3)):
    px = PX[i]

    def ax(r, px=px):
        return px + PLOT_W * r / 8

    def ay(v):
        return PY + PH * (1 - v)

    s1 = cell[(depth, "1")]
    s2 = cell[(depth, "2")]

    b.append(f'<text x="{px}" y="216" font-size="19" font-weight="bold" fill="{INK}" font-family="{FONT}">{LETTERS[i]}. Depth {depth}</text>')
    b.append(f'<text x="{px}" y="238" font-size="13" fill="{GRAY}" font-family="{FONT}">press rounds 0-{depth} (shaded) &#183; release rounds {depth+1}-8</text>')

    # press-phase shading (rounds 0..depth are on the conservative judge)
    b.append(f'<rect x="{ax(0):.1f}" y="{PY}" width="{ax(depth)-ax(0):.1f}" height="{PH}" '
              f'fill="{GREEN}" fill-opacity="0.10"/>')
    b.append(f'<line x1="{ax(depth):.1f}" y1="{PY}" x2="{ax(depth):.1f}" y2="{PY+PH}" '
              f'stroke="{INK}" stroke-width="1.6" stroke-dasharray="5 4"/>')
    b.append(f'<text x="{ax(depth):.1f}" y="{PY - 8}" text-anchor="middle" font-size="12.5" '
              f'fill="{INK}" font-family="{FONT}">switch ↓</text>')
    b.append(f'<text x="{ax(depth/2):.1f}" y="{PY + 18}" text-anchor="middle" font-size="12" '
              f'fill="{GREEN}" font-family="{FONT}">press phase</text>')

    # gridlines
    for v in (0.0, 0.25, 0.5, 0.75, 1.0):
        yy = ay(v)
        b.append(f'<line x1="{px}" y1="{yy:.1f}" x2="{px+PLOT_W}" y2="{yy:.1f}" stroke="#e4e4e0" stroke-width="1"/>')
        if i == 0:
            b.append(f'<text x="{px-10}" y="{yy+5:.1f}" text-anchor="end" font-size="14" fill="{GRAY}" font-family="{FONT}">{v:g}</text>')
    for r in range(9):
        b.append(f'<text x="{ax(r):.1f}" y="{PY+PH+22}" text-anchor="middle" font-size="13" fill="{GRAY}" font-family="{FONT}">{r}</text>')
    b.append(f'<text x="{px+PLOT_W/2:.1f}" y="{PY+PH+42}" text-anchor="middle" font-size="14.5" fill="{INK}" font-family="{FONT}">round</text>')
    if i == 0:
        b.append(f'<text x="{LEFT-58}" y="{PY+PH/2}" font-size="15" fill="{INK}" font-family="{FONT}" '
                  f'transform="rotate(-90 {LEFT-58} {PY+PH/2})" text-anchor="middle">risk coordinate</text>')

    # trajectories
    for rec, color in ((s1, BLUE), (s2, RED)):
        pts = " ".join(f"{ax(r):.1f},{ay(v):.1f}" for r, v in enumerate(rec["traj"]))
        b.append(f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="3"/>')
        for r, v in enumerate(rec["traj"]):
            b.append(f'<circle cx="{ax(r):.1f}" cy="{ay(v):.1f}" r="4" fill="{color}"/>')

    # endpoint labels (offset so the two never collide)
    b.append(f'<text x="{ax(8)+8:.1f}" y="{ay(s2["r8"])-6:.1f}" font-size="14" font-weight="bold" fill="{RED}" font-family="{FONT}">{s2["r8"]:.3f}</text>')
    b.append(f'<text x="{ax(8)+8:.1f}" y="{ay(s1["r8"])+16:.1f}" font-size="14" font-weight="bold" fill="{BLUE}" font-family="{FONT}">{s1["r8"]:.3f}</text>')

    # panel note: switch-round spread + r8 range (fixed two lines, no auto-wrap)
    note_y1 = PY + PH + 66
    note_y2 = note_y1 + 18
    b.append(f'<text x="{px}" y="{note_y1}" font-size="12.5" fill="{GRAY}" font-family="{FONT}">switch-round pool spread: seed 1 {s1["spread"]:.2f} &#183; seed 2 {s2["spread"]:.2f}</text>')
    lo, hi, rng = RANGES[depth]
    b.append(f'<text x="{px}" y="{note_y2}" font-size="14.5" font-weight="bold" fill="{INK}" font-family="{FONT}">r8 range = {rng:.3f} ({lo:.3f} to {hi:.3f})</text>')

PANEL_BLOCK_BOTTOM = PY + PH + 66 + 18 + 10  # = 622

# ================= D. the r8 fan across depths =================
FY_TITLE = PANEL_BLOCK_BOTTOM + 26
b.append(f'<text x="{LEFT}" y="{FY_TITLE}" font-size="19.5" font-weight="bold" fill="{INK}" font-family="{FONT}">D. The r8 endpoint fan compresses with depth</text>')
b.append(f'<text x="{LEFT}" y="{FY_TITLE+22}" font-size="14" fill="{GRAY}" font-family="{FONT}">range shrinks 1.000 &#8594; 0.832 &#8594; 0.594 from depth 1 to 3 &#8212; but stays wide; no depth collapses to one outcome</text>')

DX0, DW = 300, 900
DY0, ROWH = FY_TITLE + 62, 62


def dx(v):
    return DX0 + DW * v

for i, depth in enumerate((1, 2, 3)):
    yc = DY0 + i * ROWH
    lo, hi, rng = RANGES[depth]
    b.append(f'<line x1="{dx(0):.1f}" y1="{yc}" x2="{dx(1):.1f}" y2="{yc}" stroke="#e4e4e0" stroke-width="1.5"/>')
    b.append(f'<line x1="{dx(lo):.1f}" y1="{yc}" x2="{dx(hi):.1f}" y2="{yc}" stroke="{INK}" stroke-width="6"/>')
    b.append(f'<circle cx="{dx(lo):.1f}" cy="{yc}" r="8" fill="{BLUE}"/>')
    b.append(f'<circle cx="{dx(hi):.1f}" cy="{yc}" r="8" fill="{RED}"/>')
    b.append(f'<text x="{dx(lo):.1f}" y="{yc+24}" text-anchor="middle" font-size="13" font-weight="bold" fill="{BLUE}" font-family="{FONT}">{lo:.3f}</text>')
    b.append(f'<text x="{dx(hi):.1f}" y="{yc-14}" text-anchor="middle" font-size="13" font-weight="bold" fill="{RED}" font-family="{FONT}">{hi:.3f}</text>')
    b.append(f'<text x="{DX0-20}" y="{yc+5}" text-anchor="end" font-size="16" font-weight="bold" fill="{INK}" font-family="{FONT}">depth {depth}</text>')
    b.append(f'<text x="{dx(1)+22}" y="{yc+5}" font-size="15.5" font-weight="bold" fill="{INK}" font-family="{FONT}">range {rng:.3f}</text>')

# x-axis for the fan
FAX_Y = DY0 + 2 * ROWH + 34
for v in (0.0, 0.25, 0.5, 0.75, 1.0):
    xx = dx(v)
    b.append(f'<line x1="{xx:.1f}" y1="{FAX_Y-6}" x2="{xx:.1f}" y2="{FAX_Y+6}" stroke="{INK}" stroke-width="2"/>')
    b.append(f'<text x="{xx:.1f}" y="{FAX_Y+26}" text-anchor="middle" font-size="13.5" fill="{GRAY}" font-family="{FONT}">{v:g}</text>')
b.append(f'<line x1="{dx(0):.1f}" y1="{FAX_Y}" x2="{dx(1):.1f}" y2="{FAX_Y}" stroke="{INK}" stroke-width="2"/>')
t, _ = text_block(DX0, FAX_Y + 50, "risk coordinate at round 8", 15, 40, INK)
b.append(t.replace('<text ', '<text text-anchor="middle" ', 1).replace(f'x="{DX0}"', f'x="{DX0+DW/2:.0f}"'))

fan_bottom = FAX_Y + 66

# ================= amber caveat: material necessary but not sufficient =================
AY0 = fan_bottom + 24
amber_text, amber_end = rich_text(LEFT + 20, AY0 + 30, [
    ("Necessary but not sufficient: ", AMBER, True),
    ("switch-round pool spread (recomputed above from rounds_raw pool_risk) was 0.17–0.25 in all six "
     "cells — ample supporting material at every depth, satisfying the pre-registered prediction that "
     "spread > 0.10 should mean r8 > 0.30. Three of the six cells still ended near the floor "
     "(r8 = 0.000, 0.105, 0.229). Rich material at the switch does not guarantee the fan opens.", INK, False),
], 15, 148)
amber_h = (amber_end - AY0) + 16
b.append(box(LEFT, AY0, W - 2 * LEFT, amber_h, AMBER_TINT, AMBER, 2))
b.append(amber_text)

# ================= prereg scorecard =================
SY0 = AY0 + amber_h + 30
t, syend = text_block(LEFT, SY0, "Pre-registered scorecard (docs/report_press_depth_boundary.md), 2 of 5 criteria passed:", 17, 90, INK, "bold")
b.append(t)
seg = []
for num, desc, outcome, verdict in PREREG:
    color = GREEN if verdict == "PASS" else RED
    seg.append((f"{num}) {desc} — {outcome}:", INK, False))
    seg.append((verdict, color, True))
score_text, score_end = rich_text(LEFT, syend + 8, seg, 14, 148)
b.append(score_text)

# ================= takeaway =================
TY = score_end + 26
tt_text, tt_end = rich_text(LEFT + 20, TY + 32, [
    ("Safety reading: ", INK, True),
    ("a brief conservative intervention (1–3 press rounds) ", INK, False),
    ("does not reliably prevent a base-judge rail", RED, True),
    (" — seed 2 reached 1.000 after conservative pressing at every depth tested, and deeper pressing only "
     f"shrinks rail amplitude gradually (r8 range {RANGES[1][2]:.3f} → {RANGES[2][2]:.3f} → {RANGES[3][2]:.3f} "
     "at depth 1 → 2 → 3). Brief pressing shrinks the fan but doesn't pick the branch; only sustained "
     "pressing (4–5 rounds, per the press_release / press_hold arms elsewhere in the K2 program) reaches the "
     "zero-spread state that stayed selection-inert under the tested successors.", INK, False),
], 17.5, 132)
tt_h = (tt_end - TY) + 20
b.append(box(LEFT - 20, TY, W - 2 * (LEFT - 20), tt_h, KEY_FILL, INK, 2.5))
b.append(tt_text)

FOOT_Y = TY + tt_h + 26
foot, foot_end = text_block(LEFT - 20, FOOT_Y,
    "Source: experiments/modal_k2_release/output/k2rel_press_d{1,2,3}_s{1,2}.json — r0–r8 pool-risk "
    "trajectories recomputed here from each cell's traj field. Switch-round pool spread = the population "
    "mean over items of within-item candidate-risk SD at rounds_raw[depth-1] "
    "at the round the judge switches, also recomputed here. Pre-registered verdicts and the criterion-5 RMSE "
    "are quoted from docs/report_press_depth_boundary.md (reproduced by scripts/score_press_depth_prereg.py); "
    "that comparison uses a separately-fitted predictor (experiments/release_predictor_nogap_frozen.json) not "
    "recomputed by this script.", 12.5, 200, GRAY)
b.append(foot)

H = foot_end + 20
svg = svg_doc(W, H, "\n".join(b))
out_path = os.path.join(HERE, "result-press-depth.svg")
with open(out_path, "w") as f:
    f.write(svg)
print(f"wrote {out_path}  (H={H:.0f})")
for depth in (1, 2, 3):
    lo, hi, rng = RANGES[depth]
    print(f"  depth {depth}: r8 lo={lo:.3f} hi={hi:.3f} range={rng:.3f}")
