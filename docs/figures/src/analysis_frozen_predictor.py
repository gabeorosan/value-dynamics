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
FIGDIR = os.path.dirname(HERE) if os.path.basename(HERE) == "src" else HERE
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

# minimum readable body font
BODY = 19


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
    ("test batch 1", N_kb, R2_kb, R0_kb, PCT_kb),
    ("test batch 2", N_ba, R2_ba, R0_ba, PCT_ba),
    ("test batch 3", N_pd, R2_pd, R0_pd, PCT_pd),
]

print("Recomputed directly from source files:")
for name, n, r2, r0, pct in GROUPS:
    print(f"  {name:14s} n={n:3d}  gap-predictor RMSE={r2:.4f}  "
          f"no-gap RMSE={r0:.4f}  {pct:+.1f}%")

# ---------------------------------------------------------------- figure
b = []
W = 1200

t, title_end = text_block(W // 2, 56,
    "Predicting the next round's drift from this round's selection gap works",
    28, 52, weight="bold")
b.append(t.replace('<text ', '<text text-anchor="middle" '))

t, sub_end = text_block(W // 2, title_end + 16,
    "The cautious-judge model: a predictor built from earlier rounds, tested on three later "
    "rollout batches it never saw, against a matched guess that ignores the gap.",
    BODY, 92, GRAY)
b.append(t.replace('<text ', '<text text-anchor="middle" '))

# ================= bar chart =================
legend_y = sub_end + 34
AX, AY, AW, AH = 160, legend_y + 50, 880, 380
YMAX = 0.145


def ay_(v):
    return AY + AH * (1 - v / YMAX)


for v in (0.0, 0.03, 0.06, 0.09, 0.12):
    yy = ay_(v)
    col, sw = (INK, 2) if v == 0 else ("#e4e4e0", 1)
    b.append(f'<line x1="{AX}" y1="{yy:.1f}" x2="{AX + AW}" y2="{yy:.1f}" stroke="{col}" stroke-width="{sw}"/>')
    b.append(f'<text x="{AX - 12}" y="{yy + 5:.1f}" text-anchor="end" font-size="18" fill="{GRAY}" font-family="{FONT}">{v:.2f}</text>')
b.append(f'<text x="{AX - 100}" y="{AY + AH / 2}" font-size="{BODY}" fill="{INK}" font-family="{FONT}" '
         f'transform="rotate(-90 {AX - 100} {AY + AH / 2})" text-anchor="middle">prediction error (RMSE of next round\'s drift)</text>')

group_w = AW / 3
bar_w = 90
gap = 22
for i, (name, n, r2, r0, pct) in enumerate(GROUPS):
    gx = AX + group_w * i
    cx = gx + group_w / 2
    x2 = cx - gap / 2 - bar_w
    x0 = cx + gap / 2
    # predictor using the gap (BLUE)
    y2 = ay_(r2)
    b.append(f'<rect x="{x2:.1f}" y="{y2:.1f}" width="{bar_w}" height="{ay_(0)-y2:.1f}" fill="{BLUE}" stroke="{INK}" stroke-width="1.6"/>')
    b.append(f'<text x="{x2+bar_w/2:.1f}" y="{y2-10:.1f}" text-anchor="middle" font-size="18" fill="{INK}" font-family="{FONT}">{r2:.3f}</text>')
    # guess that ignores the gap (GRAY)
    y0 = ay_(r0)
    b.append(f'<rect x="{x0:.1f}" y="{y0:.1f}" width="{bar_w}" height="{ay_(0)-y0:.1f}" fill="{GRAY}" fill-opacity="0.55" stroke="{INK}" stroke-width="1.6"/>')
    b.append(f'<text x="{x0+bar_w/2:.1f}" y="{y0-10:.1f}" text-anchor="middle" font-size="18" fill="{INK}" font-family="{FONT}">{r0:.3f}</text>')
    # bracket + pct label above the pair
    top = min(y2, y0) - 48
    b.append(f'<line x1="{x2+bar_w/2:.1f}" y1="{top+16:.1f}" x2="{x2+bar_w/2:.1f}" y2="{top+24:.1f}" stroke="{INK}" stroke-width="1.4"/>')
    b.append(f'<line x1="{x0+bar_w/2:.1f}" y1="{top+16:.1f}" x2="{x0+bar_w/2:.1f}" y2="{top+24:.1f}" stroke="{INK}" stroke-width="1.4"/>')
    b.append(f'<line x1="{x2+bar_w/2:.1f}" y1="{top+16:.1f}" x2="{x0+bar_w/2:.1f}" y2="{top+16:.1f}" stroke="{INK}" stroke-width="1.4"/>')
    b.append(f'<text x="{cx:.1f}" y="{top:.1f}" text-anchor="middle" font-size="21" font-weight="bold" fill="{INK}" font-family="{FONT}">{pct:+.0f}%</text>')
    # group label under axis (plain, no dataset code names)
    b.append(f'<text x="{cx:.1f}" y="{AY+AH+34:.1f}" text-anchor="middle" font-size="20" font-weight="bold" fill="{INK}" font-family="{FONT}">{esc(name)}</text>')
    b.append(f'<text x="{cx:.1f}" y="{AY+AH+58:.1f}" text-anchor="middle" font-size="17" fill="{GRAY}" font-family="{FONT}">n = {n}</text>')

# legend
lx, ly = AX, legend_y
b.append(f'<rect x="{lx}" y="{ly-16}" width="22" height="22" fill="{BLUE}" stroke="{INK}" stroke-width="1.5"/>')
b.append(f'<text x="{lx+30}" y="{ly+2}" font-size="{BODY}" fill="{INK}" font-family="{FONT}">predictor using the gap</text>')
b.append(f'<rect x="{lx+330}" y="{ly-16}" width="22" height="22" fill="{GRAY}" fill-opacity="0.55" stroke="{INK}" stroke-width="1.5"/>')
b.append(f'<text x="{lx+360}" y="{ly+2}" font-size="{BODY}" fill="{INK}" font-family="{FONT}">guess that ignores the gap</text>')

# ================= caption =================
pcts_abs = [abs(PCT_kb), abs(PCT_ba), abs(PCT_pd)]
lo, hi = min(pcts_abs), max(pcts_abs)
cap_y = AY + AH + 96
t, cap_end = text_block(AX, cap_y,
    f"Using the gap cuts prediction error by {lo:.0f}% to {hi:.0f}% compared with ignoring it, in every "
    "batch tested.",
    BODY, 100, GRAY)
b.append(t)

H = cap_end + 32
svg = svg_doc(W, H, "\n".join(b))
out_path = os.path.join(FIGDIR, "analysis_frozen_predictor.svg")
with open(out_path, "w") as f:
    f.write(svg)
print(f"wrote {out_path}")
