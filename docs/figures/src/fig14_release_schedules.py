#!/usr/bin/env python3
"""fig14 — after the cautious judge stops, the value climbs back.

The gambling model (trained to prefer a risky gamble) is pushed down by a
cautious judge for four rounds, then handed off five different ways for four
more rounds: judge itself, get fanned out first then pressed, get kept at
random, get handed to a neutral judge, or (a no-press comparison) sit with
the neutral judge for all eight rounds. In every schedule the value climbs
back up once a judge that isn't the cautious one is in charge — unless the
switch happens on a pool with no variation left to select from, in which
case it just sits at the floor.

Reads the raw round-by-round trajectories (r0..r8) directly from the release-
grid rollout JSONs. Numbers are computed here, not copied from any report —
if they disagree with prose elsewhere, trust this script's printed output.

Regenerate with:  python3 fig14_after_the_cautious_judge_stops.py   (stdlib only)
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = HERE
while ROOT != os.path.dirname(ROOT) and not os.path.isdir(os.path.join(ROOT, "experiments")):
    ROOT = os.path.dirname(ROOT)
FIGDIR = os.path.dirname(HERE) if os.path.basename(HERE) == "src" else HERE

INK = "#1a1a1a"
BLUE = "#2867b5"
GREEN = "#3a7d44"
RED = "#b5342c"
GRAY = "#6b7684"
PURPLE = "#8a5a9e"
AMBER = "#c07d18"
STRIP_FILL = "#eef2f6"

FONT = "Helvetica, Arial, sans-serif"

# minimum readable body font
BODY = 19


# ------------------------------------------------------------ house helpers
# (copied verbatim from fig05_selection_gap_predicts_drift.py)
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


def text_block(x, y, text, size, width, color=INK, weight="normal", lh=1.4):
    lines = wrap(text, width)
    svg = []
    for i, ln in enumerate(lines):
        svg.append(f'<text x="{x}" y="{y + i * size * lh}" font-family="{FONT}" '
                   f'font-size="{size}" font-weight="{weight}" fill="{color}">{esc(ln)}</text>')
    return "\n".join(svg), y + len(lines) * size * lh


def ctext(x, y, text, size, color=INK, weight="normal"):
    return (f'<text x="{x}" y="{y}" text-anchor="middle" font-family="{FONT}" '
            f'font-size="{size}" font-weight="{weight}" fill="{color}">{esc(text)}</text>')


def box(x, y, w, h, fill, stroke=INK, sw=2.5, rx=8):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')


def marker(x, y, shape, color, s=7.5):
    if shape == "circle":
        return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{s}" fill="{color}" stroke="white" stroke-width="1.5"/>'
    if shape == "square":
        return f'<rect x="{x-s:.1f}" y="{y-s:.1f}" width="{2*s}" height="{2*s}" fill="{color}" stroke="white" stroke-width="1.5"/>'
    if shape == "triangle":
        pts = f"{x:.1f},{y-s-1:.1f} {x-s-1:.1f},{y+s:.1f} {x+s+1:.1f},{y+s:.1f}"
        return f'<polygon points="{pts}" fill="{color}" stroke="white" stroke-width="1.5"/>'
    if shape == "diamond":
        pts = f"{x:.1f},{y-s-1.5:.1f} {x+s+1:.1f},{y:.1f} {x:.1f},{y+s+1.5:.1f} {x-s-1:.1f},{y:.1f}"
        return f'<polygon points="{pts}" fill="{color}" stroke="white" stroke-width="1.5"/>'
    return ""


def svg_doc(w, h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
            f'font-family="{FONT}">\n<rect width="{w}" height="{h}" fill="white"/>\n'
            f'{body}\n</svg>')


def protocol_strip(cx, y, steps, bw=222, bh=54, gap=44):
    """One horizontal row of small labelled boxes with arrows between."""
    out = []
    n = len(steps)
    total = n * bw + (n - 1) * gap
    x = cx - total / 2
    for i, label in enumerate(steps):
        out.append(box(x, y, bw, bh, STRIP_FILL, GRAY, 1.5, rx=10))
        lines = wrap(label, int(bw / 9.5))
        ly = y + bh / 2 - (len(lines) - 1) * 10 + 6.5
        for j, ln in enumerate(lines):
            out.append(ctext(x + bw / 2, ly + j * 20, ln, BODY, INK))
        if i < n - 1:
            out.append(f'<text x="{x + bw + gap / 2:.1f}" y="{y + bh / 2 + 9:.1f}" '
                       f'text-anchor="middle" font-size="26" fill="{GRAY}" font-family="{FONT}">&#8594;</text>')
        x += bw + gap
    return "\n".join(out)


# ---------------------------------------------------------------- data
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

recs = {}  # (cond, run) -> {"traj": [...9...], "judge_used": [...8...]}
for path in DATA_FILES:
    if not os.path.exists(path):
        raise SystemExit(f"missing data file: {path}")
    d = json.load(open(path))
    for rk in (k for k in d if k.isdigit()):
        for cond, rec in d[rk].items():
            if cond not in TARGET_CONDS:
                continue
            traj = rec.get("traj")
            if not traj or len(traj) < 9:
                continue
            recs[(cond, int(rk))] = dict(traj=traj[:9], judge_used=rec.get("judge_used", []))

# judge condition key -> (color, plain label). Same judge = same color in
# every panel; the schedules themselves are told apart by panel title.
JUDGE_COLOR = {
    "frozen_cons_r0": GREEN,
    "evolving_self": BLUE,
    "random_select": AMBER,
    "frozen_base": PURPLE,
}
JUDGE_LABEL = {
    "frozen_cons_r0": "the cautious judge presses",
    "evolving_self": "the model judges itself",
    "random_select": "kept at random (no judge)",
    "frozen_base": "the neutral judge",
}


def seeds_for(cond):
    return {rk: recs[(cond, rk)] for (c, rk) in recs if c == cond}


PR = seeds_for("press_release")
FP = seeds_for("fan_press")
PRND = seeds_for("press_random")
PTB = seeds_for("press_to_base")
BH = seeds_for("base_hold")
assert len(PR) == 3 and len(FP) == 2 and len(PRND) == 3 and len(PTB) == 3 and len(BH) == 2, \
    f"unexpected run counts: pr={len(PR)} fp={len(FP)} prnd={len(PRND)} ptb={len(PTB)} bh={len(BH)}"

# ------------- numbers used in labels/annotations, computed here -------------
pr_r8 = [PR[r]["traj"][8] for r in PR]
pr_r8_mean = sum(pr_r8) / len(pr_r8)
pr_max_rebound = max(PR[r]["traj"][8] - PR[r]["traj"][4] for r in PR)

fp_r8 = [FP[r]["traj"][8] for r in FP]

prnd_deltas = {r: PRND[r]["traj"][8] - PRND[r]["traj"][4] for r in PRND}
prnd_max_dev = max(abs(v) for v in prnd_deltas.values())
prnd_biggest_run = max(prnd_deltas, key=lambda r: abs(prnd_deltas[r]))

ptb_r4 = {r: PTB[r]["traj"][4] for r in PTB}
ptb_r8 = {r: PTB[r]["traj"][8] for r in PTB}
ptb_r8_mean = sum(ptb_r8.values()) / len(ptb_r8)

bh_r8 = {r: BH[r]["traj"][8] for r in BH}

print("=== numbers computed from the raw JSONs ===")
print(f"let-it-judge-itself r8: {sorted(round(v,3) for v in pr_r8)}  mean={pr_r8_mean:.3f}  "
      f"max rebound over r4={pr_max_rebound:+.3f}")
print(f"fan-then-press r8: {sorted(round(v,3) for v in fp_r8)}")
print(f"keep-at-random deltas (r8-r4): " +
      ", ".join(f"run{r} {v:+.3f}" for r, v in sorted(prnd_deltas.items())) +
      f"  max |delta|={prnd_max_dev:.3f} (run {prnd_biggest_run})")
print(f"hand-to-neutral-judge r4->r8 by run: " +
      ", ".join(f"run{r} {ptb_r4[r]:.3f}->{ptb_r8[r]:.3f}" for r in sorted(ptb_r4)) +
      f"  mean r8={ptb_r8_mean:.3f}")
print(f"never-pressed r8 by run: " + ", ".join(f"run{r} {bh_r8[r]:.3f}" for r in sorted(bh_r8)))


# ================================================================ figures
# The single five-panel grid was too dense, so it is split in two:
#   fig14  — schedules where the value stays at the floor
#   fig14b — schedules where a neutral judge lets it climb back
# Within a panel, every run (seed) is drawn identically; line colour tracks
# WHICH judge acted each round (a meaningful cue, explained in the legend).
PW, PH = 460, 300
YMIN, YMAX = 0.0, 0.9
GAP = 70
TICK = 16
DOT_R = 5.0
CAP_W = 48
LH = 1.4


def px_of(ax, r):
    return ax + PW * r / 8


def py_of(ay, v):
    return ay + PH * (YMAX - v) / (YMAX - YMIN)


def panel_axes(out, ax, ay, title, yaxis=False):
    for v in (0.0, 0.2, 0.4, 0.6, 0.8):
        yy = py_of(ay, v)
        col, sw = (INK, 1.5) if v == 0.0 else ("#e4e4e0", 1)
        out.append(f'<line x1="{ax}" y1="{yy:.1f}" x2="{ax+PW}" y2="{yy:.1f}" stroke="{col}" stroke-width="{sw}"/>')
        out.append(f'<text x="{ax-10}" y="{yy+5:.1f}" text-anchor="end" font-size="{TICK}" fill="{GRAY}" font-family="{FONT}">{v:.1f}</text>')
    for r in range(9):
        out.append(f'<text x="{px_of(ax,r):.1f}" y="{ay+PH+24}" text-anchor="middle" font-size="{TICK}" fill="{GRAY}" font-family="{FONT}">{r}</text>')
    out.append(f'<text x="{ax+PW/2:.1f}" y="{ay+PH+46}" text-anchor="middle" font-size="{BODY}" fill="{INK}" font-family="{FONT}">round</text>')
    out.append(ctext(ax + PW / 2, ay - 16, title, 21, INK, "bold"))
    if yaxis:
        out.append(f'<text x="{ax-52}" y="{ay+PH/2}" font-size="{BODY}" fill="{INK}" font-family="{FONT}" '
                   f'transform="rotate(-90 {ax-52} {ay+PH/2})" text-anchor="middle">how risk-seeking the pool is</text>')


def shade_press(out, ax, ay, judge_used, key="frozen_cons_r0"):
    idxs = [i for i, j in enumerate(judge_used) if j == key]
    if not idxs:
        return
    x0, x1 = px_of(ax, min(idxs)), px_of(ax, max(idxs) + 1)
    out.append(f'<rect x="{x0:.1f}" y="{ay}" width="{x1-x0:.1f}" height="{PH}" fill="{GREEN}" fill-opacity="0.10"/>')


def floor_line(out, ax, ay):
    y0 = py_of(ay, 0.0)
    out.append(f'<line x1="{ax}" y1="{y0:.1f}" x2="{ax+PW}" y2="{y0:.1f}" stroke="{RED}" stroke-width="1.6" stroke-dasharray="5 4"/>')
    out.append(f'<text x="{ax+PW-6}" y="{y0-7:.1f}" text-anchor="end" font-size="{TICK}" fill="{RED}" font-family="{FONT}">the floor</text>')


def draw_run(out, ax, ay, rec):
    traj, ju = rec["traj"], rec["judge_used"]
    for k in range(8):
        color = JUDGE_COLOR[ju[k]]
        out.append(f'<line x1="{px_of(ax,k):.1f}" y1="{py_of(ay,traj[k]):.1f}" x2="{px_of(ax,k+1):.1f}" y2="{py_of(ay,traj[k+1]):.1f}" '
                   f'stroke="{color}" stroke-width="3" stroke-opacity="0.9"/>')
    for r, v in enumerate(traj):
        color = JUDGE_COLOR[ju[r]] if r < len(ju) else JUDGE_COLOR[ju[-1]]
        out.append(f'<circle cx="{px_of(ax,r):.1f}" cy="{py_of(ay,v):.1f}" r="{DOT_R}" fill="{color}" fill-opacity="0.9" stroke="white" stroke-width="1.2"/>')


def endval(out, ax, ay, rec, color, anchor="start", dy=0):
    v = rec["traj"][8]
    x = px_of(ax, 8) + (8 if anchor == "start" else -8)
    out.append(f'<text x="{x:.1f}" y="{py_of(ay,v)+4+dy:.1f}" text-anchor="{anchor}" font-size="17" '
               f'font-weight="bold" fill="{color}" font-family="{FONT}">{v:.3f}</text>')


def caption(out, ax, ay, text):
    t, _ = text_block(ax, ay + PH + 78, text, BODY, CAP_W, GRAY, lh=LH)
    out.append(t)


def header(b, W, title1, title2, sub):
    b.append(ctext(W / 2, 50, title1, 29, INK, "bold"))
    ynext = 88
    if title2:
        b.append(ctext(W / 2, 84, title2, 22, INK, "bold"))
        ynext = 120
    sv, se = text_block(W / 2, ynext, sub, BODY, int(W / 9.5), GRAY)
    for ln in sv.split("\n"):
        b.append(ln.replace('<text ', '<text text-anchor="middle" '))
    return se


def legend(b, W, y, items):
    widths = [len(l) * 10 + 72 for _, l in items]
    total = sum(widths) + 30 * (len(items) - 1)
    x = W / 2 - total / 2
    for (color, label), wdt in zip(items, widths):
        b.append(f'<line x1="{x:.0f}" y1="{y}" x2="{x+50:.0f}" y2="{y}" stroke="{color}" stroke-width="4.5"/>')
        b.append(f'<text x="{x+60:.0f}" y="{y+6}" font-size="{BODY}" fill="{INK}" font-family="{FONT}">{esc(label)}</text>')
        x += wdt + 30
    b.append(f'<rect x="{W/2-150:.0f}" y="{y+24}" width="18" height="18" fill="{GREEN}" fill-opacity="0.10" stroke="{GREEN}" stroke-width="1.5"/>')
    b.append(f'<text x="{W/2-124:.0f}" y="{y+39}" font-size="{BODY}" fill="{INK}" font-family="{FONT}">shaded = rounds under the cautious judge</text>')


def build_floor():
    W = 1630
    b = []
    se = header(b, W, "When the pressing leaves nothing to select, the value stays at the floor", None,
                "The gambling model, pushed down by a cautious judge for four rounds, then released three ways. "
                "Value = how often its kept answers pick the risky gamble, read once per round.")
    sy = se + 18
    b.append(protocol_strip(W / 2, sy, ["cautious judge presses down", "then stop / switch", "continue the loop", "measure risk"]))
    ly = sy + 54 + 44
    legend(b, W, ly, [(GREEN, "the cautious judge presses"), (BLUE, "the model judges itself"), (AMBER, "kept at random")])
    row_y = ly + 84
    colx = [70, 70 + PW + GAP, 70 + 2 * (PW + GAP)]

    ax, ay = colx[0], row_y
    panel_axes(b, ax, ay, "let the model judge itself after", yaxis=True)
    shade_press(b, ax, ay, PR[sorted(PR)[0]]["judge_used"])
    floor_line(b, ax, ay)
    for r in sorted(PR):
        draw_run(b, ax, ay, PR[r])
    caption(b, ax, ay, "Once the cautious judge floors the pool, judging itself keeps it there.")

    ax, ay = colx[1], row_y
    panel_axes(b, ax, ay, "let it fan out, then press")
    shade_press(b, ax, ay, FP[sorted(FP)[0]]["judge_used"])
    floor_line(b, ax, ay)
    for r in sorted(FP):
        draw_run(b, ax, ay, FP[r])
    caption(b, ax, ay, "Fanning out first, then pressing, reaches the same floor.")

    ax, ay = colx[2], row_y
    panel_axes(b, ax, ay, "keep at random after")
    shade_press(b, ax, ay, PRND[sorted(PRND)[0]]["judge_used"])
    for r in sorted(PRND):
        draw_run(b, ax, ay, PRND[r])
    caption(b, ax, ay, "Keeping answers at random drifts a little, with no pull back up.")

    H = row_y + PH + 78 + 3 * BODY * LH + 24
    with open(os.path.join(FIGDIR, "fig14_after_the_cautious_judge_stops.svg"), "w") as f:
        f.write(svg_doc(W, H, "\n".join(b)))
    print("wrote fig14_after_the_cautious_judge_stops.svg")


def build_climb():
    W = 1210
    b = []
    se = header(b, W, "But a neutral judge afterward lets the value climb back", "— unless the pool has no variation left to select",
                "The same pressed-down gambling model, then handed to a neutral judge — or never pressed at all. "
                "Value = how often its kept answers pick the risky gamble.")
    sy = se + 18
    b.append(protocol_strip(W / 2, sy, ["cautious judge presses down", "hand to a neutral judge", "continue the loop", "measure risk"]))
    ly = sy + 54 + 44
    legend(b, W, ly, [(GREEN, "the cautious judge presses"), (PURPLE, "the neutral judge")])
    row_y = ly + 84
    colx = [90, 90 + PW + 130]

    ax, ay = colx[0], row_y
    panel_axes(b, ax, ay, "hand to a neutral judge after", yaxis=True)
    shade_press(b, ax, ay, PTB[sorted(PTB)[0]]["judge_used"])
    for r in sorted(PTB):
        draw_run(b, ax, ay, PTB[r])
    for r in sorted(PTB):
        endval(b, ax, ay, PTB[r], PURPLE)
    caption(b, ax, ay, "Two runs climb; the one whose pool had no variation left stays at the floor.")

    ax, ay = colx[1], row_y
    panel_axes(b, ax, ay, "never pressed (a neutral judge throughout)")
    for r in sorted(BH):
        draw_run(b, ax, ay, BH[r])
    for r in sorted(BH):
        endval(b, ax, ay, BH[r], PURPLE, anchor="end")
    caption(b, ax, ay, "With no pressing at all, the neutral judge pushes the value up on its own.")

    H = row_y + PH + 78 + 2 * BODY * LH + 24
    with open(os.path.join(FIGDIR, "fig14b_neutral_judge_lets_it_climb.svg"), "w") as f:
        f.write(svg_doc(W, H, "\n".join(b)))
    print("wrote fig14b_neutral_judge_lets_it_climb.svg")


build_floor()
build_climb()
