#!/usr/bin/env python3
"""Draft figure: the frozen kept-gap -> drift predictor's blind tests.

Subject: the SAME kept-gap -> next-round pool-drift coupling shown
descriptively in fig17_loop_integrator.py (pooled slope ~0.75 on the
51-transition K2 grid), here scored OUT OF SAMPLE. The predictor
(M2 = per-judge-condition intercept + pooled kept-gap slope, frozen from
experiments/release_predictor_frozen.json) is applied UNREFIT to three
later rollout sets it never saw during fitting, and compared to a
separately-and-properly-refit no-gap comparator
(experiments/release_predictor_nogap_frozen.json). All RMSE numbers below
are computed HERE, directly from the result files, not quoted from a
report.

Sources (recomputed live by this script):
  - experiments/release_predictor_frozen.json        (frozen M2 predictor)
  - experiments/release_predictor_nogap_frozen.json  (refit no-gap comparator)
  - experiments/kaggle/kaggle_k2_release_relB/output/k2_release_kernelB.json
        -> "kernel B", 35 transitions, fully blind
  - experiments/modal_k2_release/output/k2rel_press_to_base_s{1,2,3}.json
    experiments/modal_k2_release/output/k2rel_base_hold_s{1,2}.json
        -> "Modal branch A", 35 transitions, PARTIALLY blind (partial
           trajectories to round 7 were inspected before the predictor
           was frozen; only round 8 and the final scoring were unseen)
  - experiments/modal_k2_release/output/k2rel_press_d{1,2,3}_s{1,2}.json
        -> "press-depth branch c", 42 transitions, fully blind

This reproduces docs/report_release_grid_results.md's published pair
(-17.3%, -31.1%) and docs/report_press_depth_boundary.md's corrected
figure (-42.0%, NOT the report's earlier -45.0%, which was measured
against an invalid joint-fit ablation and was explicitly superseded in
the same report's audit-correction section).

Regenerate with: python3 analysis-frozen-predictor.py  (stdlib only)
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = HERE
while ROOT != os.path.dirname(ROOT) and not os.path.isdir(os.path.join(ROOT, "experiments")):
    ROOT = os.path.dirname(ROOT)

# ---------------------------------------------------------------- palette
# copied verbatim from docs/figures/src/make_figures.py / fig17_loop_integrator.py
INK = "#1a1a1a"
BLUE = "#2867b5"       # accent / self-judge series (validated)
GREEN = "#3a7d44"      # accent / frozen-judge series (validated)
RED = "#b5342c"        # emphasis for reversal / warning text
GRAY = "#6b7684"       # recessive only (axes, muted captions) — never a series
AMBER = "#9a6b15"      # caveat / partial-blindness flag
KEY_FILL = "#eef5ee"   # highlighted takeaway box
AMBER_TINT = "#fdf8ee"

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


# ---------------------------------------------------------------- data
FROZEN = json.load(open(os.path.join(ROOT, "experiments", "release_predictor_frozen.json")))
NOGAP = json.load(open(os.path.join(ROOT, "experiments", "release_predictor_nogap_frozen.json")))
J2A, IC, SLOPE = FROZEN["judge_to_arm"], FROZEN["intercepts"], FROZEN["gap_slope"]
IC0 = NOGAP["intercepts"]


def transitions(path):
    """[(judge_used[t], gap_arm[t], pool[t], pool[t+1]), ...] for every
    round-to-round transition in every seed/condition of one result file."""
    d = json.load(open(path))
    out = []
    for sd in d:
        if not sd.isdigit():
            continue
        for cond, res in d[sd].items():
            raws = res.get("rounds_raw")
            if not raws:
                continue
            judges = res["judge_used"]
            pools = [sum(it["pool_risk"] for it in rr) / len(rr) for rr in raws]
            gaps = [sum(it["gap_arm"] for it in rr) / len(rr) for rr in raws]
            for t in range(len(pools) - 1):
                out.append((judges[t], gaps[t], pools[t], pools[t + 1]))
    return out


def score(trans):
    """RMSE of the frozen M2 predictor vs the refit no-gap comparator,
    on the transitions whose judge condition both models cover."""
    e2 = e0 = 0.0
    n = 0
    pairs = []  # (observed drift, predicted drift) for the frozen model
    for judge, gap, p0, p1 in trans:
        arm = J2A.get(judge, judge)
        if arm not in IC or arm not in IC0:
            continue
        obs = p1 - p0
        pred = IC[arm] + SLOPE * gap
        e2 += (obs - pred) ** 2
        e0 += (obs - IC0[arm]) ** 2
        n += 1
        pairs.append((obs, pred))
    r2, r0 = (e2 / n) ** 0.5, (e0 / n) ** 0.5
    return r2, r0, n, (r2 - r0) / r0 * 100, pairs


MK2 = os.path.join(ROOT, "experiments", "modal_k2_release", "output")

kernel_b = transitions(os.path.join(
    ROOT, "experiments", "kaggle", "kaggle_k2_release_relB", "output", "k2_release_kernelB.json"))
branch_a = []
for f in ("k2rel_press_to_base_s1.json", "k2rel_press_to_base_s2.json",
          "k2rel_press_to_base_s3.json", "k2rel_base_hold_s1.json", "k2rel_base_hold_s2.json"):
    branch_a += transitions(os.path.join(MK2, f))
press_depth = []
for f in ("k2rel_press_d1_s1.json", "k2rel_press_d1_s2.json", "k2rel_press_d2_s1.json",
          "k2rel_press_d2_s2.json", "k2rel_press_d3_s1.json", "k2rel_press_d3_s2.json"):
    press_depth += transitions(os.path.join(MK2, f))

R2_kb, R0_kb, N_kb, PCT_kb, PAIRS_kb = score(kernel_b)
R2_ba, R0_ba, N_ba, PCT_ba, PAIRS_ba = score(branch_a)
R2_pd, R0_pd, N_pd, PCT_pd, PAIRS_pd = score(press_depth)

assert N_kb == 35, N_kb
assert N_ba == 35, N_ba
assert N_pd == 42, N_pd

GROUPS = [
    ("kernel B", N_kb, "fully blind", R2_kb, R0_kb, PCT_kb, False),
    ("Modal branch A", N_ba, "partially blind*", R2_ba, R0_ba, PCT_ba, True),
    ("press-depth\nbranch c", N_pd, "fully blind", R2_pd, R0_pd, PCT_pd, False),
]

print("Recomputed directly from source files:")
for name, n, blind, r2, r0, pct, caveat in GROUPS:
    print(f"  {name:22s} n={n:3d}  {blind:16s}  frozen-M2 RMSE={r2:.4f}  "
          f"no-gap RMSE={r0:.4f}  {pct:+.1f}%")

# ---------------------------------------------------------------- figure
b = []
W = 1400

t, _ = text_block(W // 2, 50, "A frozen kept-gap → drift model predicts next round's pool drift on "
                  "rollouts it never saw —", 30, 92, weight="bold")
b.append(t.replace('<text ', '<text text-anchor="middle" '))
t, _ = text_block(W // 2, 88, "RMSE 17–42% below a matched no-gap baseline, across three blind tests", 27, 98, weight="bold")
b.append(t.replace('<text ', '<text text-anchor="middle" '))
t, _ = text_block(W // 2, 122, "Predictor M2 (per-judge-condition intercept + the ≈0.75 pooled kept-gap slope "
                  "from fig17, fit once on 51 K2-grid transitions) was frozen 2026-07-12, then scored UNREFIT — "
                  "no fitting on the data below. RMSE = root-mean-squared error of next-round pool-risk drift, "
                  "vs a separately, properly refit no-gap comparator (same intercepts, gap term removed).",
                  16.5, 128, GRAY)
b.append(t.replace('<text ', '<text text-anchor="middle" '))

# ================= Panel A: grouped bar chart =================
AX, AY, AW, AH = 96, 268, 560, 380
YMAX = 0.145

def ay_(v):
    return AY + AH * (1 - v / YMAX)

t, _ = text_block(AX, 226, "A. Frozen-predictor RMSE vs the no-gap baseline, three held-out test sets",
                  20.5, 66, weight="bold")
b.append(t)

for v in (0.0, 0.03, 0.06, 0.09, 0.12):
    yy = ay_(v)
    col, sw = (INK, 2) if v == 0 else ("#e4e4e0", 1)
    b.append(f'<line x1="{AX}" y1="{yy:.1f}" x2="{AX + AW}" y2="{yy:.1f}" stroke="{col}" stroke-width="{sw}"/>')
    b.append(f'<text x="{AX - 10}" y="{yy + 5:.1f}" text-anchor="end" font-size="14.5" fill="{GRAY}" font-family="{FONT}">{v:.2f}</text>')
b.append(f'<text x="{AX - 62}" y="{AY + AH / 2}" font-size="16" fill="{INK}" font-family="{FONT}" '
         f'transform="rotate(-90 {AX - 62} {AY + AH / 2})" text-anchor="middle">RMSE of next-round pool-risk drift</text>')

group_w = AW / 3
bar_w = 46
gap = 14
for i, (name, n, blind, r2, r0, pct, caveat) in enumerate(GROUPS):
    gx = AX + group_w * i
    cx = gx + group_w / 2
    x2 = cx - gap / 2 - bar_w
    x0 = cx + gap / 2
    # frozen-M2 bar (BLUE)
    y2 = ay_(r2)
    b.append(f'<rect x="{x2:.1f}" y="{y2:.1f}" width="{bar_w}" height="{ay_(0)-y2:.1f}" fill="{BLUE}" stroke="{INK}" stroke-width="1.6"/>')
    b.append(f'<text x="{x2+bar_w/2:.1f}" y="{y2-8:.1f}" text-anchor="middle" font-size="14" fill="{INK}" font-family="{FONT}">{r2:.3f}</text>')
    # no-gap comparator bar (GRAY)
    y0 = ay_(r0)
    b.append(f'<rect x="{x0:.1f}" y="{y0:.1f}" width="{bar_w}" height="{ay_(0)-y0:.1f}" fill="{GRAY}" fill-opacity="0.55" stroke="{INK}" stroke-width="1.6"/>')
    b.append(f'<text x="{x0+bar_w/2:.1f}" y="{y0-8:.1f}" text-anchor="middle" font-size="14" fill="{INK}" font-family="{FONT}">{r0:.3f}</text>')
    # bracket + pct label above the pair
    top = min(y2, y0) - 46
    b.append(f'<line x1="{x2+bar_w/2:.1f}" y1="{top+14:.1f}" x2="{x2+bar_w/2:.1f}" y2="{top+22:.1f}" stroke="{INK}" stroke-width="1.4"/>')
    b.append(f'<line x1="{x0+bar_w/2:.1f}" y1="{top+14:.1f}" x2="{x0+bar_w/2:.1f}" y2="{top+22:.1f}" stroke="{INK}" stroke-width="1.4"/>')
    b.append(f'<line x1="{x2+bar_w/2:.1f}" y1="{top+14:.1f}" x2="{x0+bar_w/2:.1f}" y2="{top+14:.1f}" stroke="{INK}" stroke-width="1.4"/>')
    label_color = AMBER if caveat else INK
    b.append(f'<text x="{cx:.1f}" y="{top-2:.1f}" text-anchor="middle" font-size="19" font-weight="bold" fill="{label_color}" font-family="{FONT}">{pct:+.1f}%</text>')
    # group label under axis
    nlines = name.split("\n")
    for li, line in enumerate(nlines):
        b.append(f'<text x="{cx:.1f}" y="{AY+AH+26+li*18:.1f}" text-anchor="middle" font-size="15.5" font-weight="bold" fill="{INK}" font-family="{FONT}">{esc(line)}</text>')
    ncap = f"n={n}, {blind}"
    b.append(f'<text x="{cx:.1f}" y="{AY+AH+26+len(nlines)*18+16:.1f}" text-anchor="middle" font-size="12.5" fill="{AMBER if caveat else GRAY}" font-family="{FONT}">{esc(ncap)}</text>')

# legend, top-left corner of the panel (clear of the tall press-depth bars on the right)
lx, ly = AX + 14, AY + 18
b.append(f'<rect x="{lx}" y="{ly-13}" width="16" height="16" fill="{BLUE}" stroke="{INK}" stroke-width="1.2"/>')
b.append(f'<text x="{lx+24}" y="{ly}" font-size="14.5" fill="{INK}" font-family="{FONT}">frozen kept-gap predictor</text>')
b.append(f'<rect x="{lx}" y="{ly+13}" width="16" height="16" fill="{GRAY}" fill-opacity="0.55" stroke="{INK}" stroke-width="1.2"/>')
b.append(f'<text x="{lx+24}" y="{ly+26}" font-size="14.5" fill="{INK}" font-family="{FONT}">no-gap comparator</text>')

t, _ = text_block(AX, AY + AH + 92,
                  "* Modal branch A: partial trajectories to round 7 were inspected before the predictor "
                  "was frozen — only round 8 and final scoring were blind. Kernel B and press-depth branch c "
                  "are fully blind: neither trajectory was inspected before the predictor was frozen.",
                  14.5, 78, AMBER)
b.append(t)

# ================= Panel B: predicted vs observed scatter (press-depth) =================
S = 380
BX, BY = 810, 268
VMIN, VMAX = -0.28, 0.36

def bx_(v):
    return BX + S * (v - VMIN) / (VMAX - VMIN)

def byv_(v):
    return BY + S * (1 - (v - VMIN) / (VMAX - VMIN))

t, _ = text_block(BX, 226, "B. Predicted vs. observed pool drift, the 42 fully-blind "
                  "press-depth transitions (branch c)", 20.5, 68, weight="bold")
b.append(t)

for v in (-0.2, -0.1, 0.0, 0.1, 0.2, 0.3):
    xx, yy = bx_(v), byv_(v)
    col_x = (INK, 1.6) if v == 0 else ("#e4e4e0", 1)
    b.append(f'<line x1="{xx:.1f}" y1="{BY}" x2="{xx:.1f}" y2="{BY+S}" stroke="{col_x[0]}" stroke-width="{col_x[1]}"/>')
    b.append(f'<line x1="{BX}" y1="{yy:.1f}" x2="{BX+S}" y2="{yy:.1f}" stroke="{col_x[0]}" stroke-width="{col_x[1]}"/>')
    b.append(f'<text x="{xx:.1f}" y="{BY+S+22}" text-anchor="middle" font-size="13.5" fill="{GRAY}" font-family="{FONT}">{v:+.1f}</text>')
    b.append(f'<text x="{BX-9}" y="{yy+5:.1f}" text-anchor="end" font-size="13.5" fill="{GRAY}" font-family="{FONT}">{v:+.1f}</text>')
# 1:1 reference line (equal x/y scale, so this really is the diagonal)
b.append(f'<line x1="{bx_(VMIN):.1f}" y1="{byv_(VMIN):.1f}" x2="{bx_(VMAX):.1f}" y2="{byv_(VMAX):.1f}" '
         f'stroke="{INK}" stroke-width="2" stroke-dasharray="6 5"/>')
b.append(f'<text x="{bx_(0.235):.1f}" y="{byv_(0.235)-14:.1f}" font-size="13.5" fill="{GRAY}" font-family="{FONT}" '
         f'transform="rotate(-38 {bx_(0.235):.1f} {byv_(0.235)-14:.1f})">perfect prediction (y = x)</text>')

for obs, pred in PAIRS_pd:
    b.append(f'<circle cx="{bx_(obs):.1f}" cy="{byv_(pred):.1f}" r="6" fill="{BLUE}" fill-opacity="0.75" stroke="white" stroke-width="1.3"/>')

b.append(f'<text x="{BX+S/2:.1f}" y="{BY+S+48}" text-anchor="middle" font-size="16" fill="{INK}" font-family="{FONT}">observed pool-risk drift, round t → t+1</text>')
b.append(f'<text x="{BX-52}" y="{BY+S/2}" font-size="16" fill="{INK}" font-family="{FONT}" '
         f'transform="rotate(-90 {BX-52} {BY+S/2})" text-anchor="middle">predicted drift (frozen M2)</text>')

b.append(box(BX + 6, BY + 8, 272, 46, "white", "#d8d8d4", 1.4, 6))
b.append(f'<text x="{BX+16:.1f}" y="{BY+26:.1f}" font-size="15" font-weight="bold" fill="{INK}" font-family="{FONT}">RMSE = {R2_pd:.4f} ({PCT_pd:+.1f}% vs no-gap)</text>')
b.append(f'<text x="{BX+16:.1f}" y="{BY+44:.1f}" font-size="13" fill="{GRAY}" font-family="{FONT}">n = {N_pd} transitions, all inspected after freezing</text>')

# ================= takeaway =================
ty = 790
BOXH = 196
b.append(box(70, ty, W - 140, BOXH, KEY_FILL, INK, 2.5))
t, _ = rich_text(90, ty + 30, [
    ("This is a prediction result, not a stability law: ", INK, True),
    ("the fig17 kept-gap → pool-drift coupling (pooled slope ≈0.75, fit once on 51 earlier "
     "K2 transitions) was frozen, then applied unrefit to three later rollout sets. ", INK, False),
    (f"It beat a matched no-gap baseline on all three: kernel B {PCT_kb:+.1f}% (n={N_kb}, fully blind), "
     f"Modal branch A {PCT_ba:+.1f}% (n={N_ba}, partially blind*), press-depth branch c {PCT_pd:+.1f}% "
     "(n=42, fully blind, its strongest test yet). ", INK, True),
    ("This makes the coupling out-of-sample-validated — not a stability law: no experiment has perturbed "
     "a kept-gap and measured the closed-loop response, so no k-below/above-1 regime is claimed. ", INK, False),
    ("Correction: the press-depth report first quoted −45.0% for this test against an invalid ablation "
     "baseline; −42.0% (recomputed here vs the properly-refit no-gap comparator) supersedes it.", RED, False),
], 16.5, 138)
b.append(t)

svg = svg_doc(W, ty + BOXH + 30, "\n".join(b))
out_path = os.path.join(HERE, "analysis-frozen-predictor.svg")
with open(out_path, "w") as f:
    f.write(svg)
print(f"wrote {out_path}")
