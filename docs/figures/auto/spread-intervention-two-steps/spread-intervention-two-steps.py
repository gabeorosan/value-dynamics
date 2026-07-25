#!/usr/bin/env python3
"""The spread intervention splits into two steps: selection obeyed the model,
transmission did not follow.

Panel A (the selection step): within-prompt spread against the selection gap it
produced, for both arms, plus a strip showing that the offered-pool mean was
identical between the two arms in every round.

Panel B (the transmission step): the movement actually measured in the value
over each round against the movement the project's model predicts
(0.83 x selection gap), with the model's slope-1 claim and the fitted line.

Every number rendered here is recomputed in this file from
experiments/spread_intervention/output/spread_intervention.json; the file's own
"summary" block is not read.

Regenerate with:  python3 spread-intervention-two-steps.py     (stdlib only)
"""
import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = HERE
while ROOT != os.path.dirname(ROOT) and not os.path.isdir(os.path.join(ROOT, "experiments")):
    ROOT = os.path.dirname(ROOT)
DATA = os.path.join(ROOT, "experiments", "spread_intervention", "output",
                    "spread_intervention.json")
OUTFILE = os.path.join(HERE, "spread-intervention-two-steps.svg")

# ---- palette, copied from docs/figures/src/make_figures.py -------------------
INK = "#1a1a1a"
BLUE = "#2867b5"       # accent / self-judge series (validated)
GREEN = "#3a7d44"      # accent / frozen-judge series (validated)
RED = "#b5342c"        # emphasis for reversal / warning text
GRAY = "#6b7684"       # recessive only (axes, muted captions) — never a series
USER_FILL = "#cfe0f1"  # chat user box
ASST_FILL = "#eaf1f8"  # chat assistant box
DOC_FILL = "#fdf6e8"   # document / essay box
KEY_FILL = "#eef5ee"   # highlighted takeaway box

FONT = "Helvetica, Arial, sans-serif"
GRID = "#e4e4e0"

CONC = BLUE            # the concentrated arm
SPRD = GREEN           # the spread arm

TRANSMISSION = 0.83    # the project's transmission coefficient


# ---- helpers copied from make_figures.py ------------------------------------
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


def text_block(x, y, text, size, width, color=INK, weight="normal", lh=1.4,
               anchor="start"):
    lines = wrap(text, width)
    svg = []
    for i, ln in enumerate(lines):
        svg.append(f'<text x="{x:.1f}" y="{y + i * size * lh:.1f}" text-anchor="{anchor}" '
                   f'font-family="{FONT}" font-size="{size}" font-weight="{weight}" '
                   f'fill="{color}">{esc(ln)}</text>')
    return "\n".join(svg), y + len(lines) * size * lh


def ctext(x, y, text, size, color=INK, weight="normal", anchor="middle"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" font-family="{FONT}" '
            f'font-size="{size}" font-weight="{weight}" fill="{color}">{esc(text)}</text>')


def box(x, y, w, h, fill, stroke=INK, sw=2.5, rx=8):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')


def leader(x1, y1, x2, y2, color=GRAY, sw=1.8):
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{sw}"/>')


def fan(pixel_points, radius=8.0):
    """Rounds that land on exactly the same coordinates are fanned onto a small
    rosette so each of them stays visible. Returns the displaced positions."""
    buckets = {}
    for i, (px, py) in enumerate(pixel_points):
        buckets.setdefault((round(px, 2), round(py, 2)), []).append(i)
    out = [None] * len(pixel_points)
    for (px, py), idxs in buckets.items():
        n = len(idxs)
        if n == 1:
            out[idxs[0]] = (px, py)
            continue
        rings, remaining, k = [], n, 0
        while remaining > 0:
            cap = 1 if k == 0 else 6 * k
            take = min(cap, remaining)
            rings.append(take)
            remaining -= take
            k += 1
        pos = 0
        for k, take in enumerate(rings):
            for j in range(take):
                a = 2 * math.pi * j / take + (0.3 * k)
                r = radius * k
                out[idxs[pos]] = (px + r * math.cos(a), py + r * math.sin(a))
                pos += 1
    return out


def halo(x, y, lines, size, color, weight="bold", anchor="start", lh=1.4):
    """A text block on a white backing plate, for the one label that has to sit
    on top of a rule."""
    wpx = max(len(ln) for ln in lines) * size * 0.55
    x0 = x - (wpx if anchor == "end" else 0)
    out = [f'<rect x="{x0 - 8:.1f}" y="{y - size:.1f}" width="{wpx + 16:.1f}" '
           f'height="{len(lines) * size * lh + 10:.1f}" fill="white" opacity="0.92"/>']
    for i, ln in enumerate(lines):
        out.append(ctext(x, y + i * size * lh, ln, size, color, weight, anchor=anchor))
    return "\n".join(out)


def dot(x, y, arm):
    if arm == "concentrated":
        return (f'<circle cx="{x:.1f}" cy="{y:.1f}" r="7.5" fill="white" '
                f'stroke="{CONC}" stroke-width="3"/>')
    return (f'<circle cx="{x:.1f}" cy="{y:.1f}" r="8" fill="{SPRD}" '
            f'stroke="white" stroke-width="2"/>')


# ---- data -------------------------------------------------------------------
with open(DATA) as fh:
    raw = json.load(fh)

groups = raw["groups"]
judge_groups = sorted(g for g in groups if g.startswith("judge"))
cfg = raw["config"]

rows = []          # one per seed-round-arm
for g in judge_groups:
    for arm in ("concentrated", "spread"):
        a = groups[g]["arms"][arm]
        traj = a["value_traj"]
        for i, r in enumerate(a["rounds"]):
            before = traj[i]
            after = r["value_after_round"]
            rows.append({
                "group": g, "arm": arm, "round": r["round"],
                "spread": r["spread"], "gap": r["gap"],
                "pool_mean": r["pool_mean"],
                "predicted": TRANSMISSION * r["gap"],
                "observed": after - before,
                "before": before, "after": after,
            })

conc = [r for r in rows if r["arm"] == "concentrated"]
sprd = [r for r in rows if r["arm"] == "spread"]

N_ALL = len(rows)
N_SEEDS = len(judge_groups)
N_ROUNDS = max(r["round"] for r in rows)


def mean(v):
    return sum(v) / len(v)


# --- the selection step
conc_zero = sum(1 for r in conc if r["spread"] == 0.0 and r["gap"] == 0.0)
conc_spread_max = max(r["spread"] for r in conc)
conc_gap_max = max(abs(r["gap"]) for r in conc)
sprd_spread_lo = min(r["spread"] for r in sprd)
sprd_spread_hi = max(r["spread"] for r in sprd)
sprd_gap_mean = mean([r["gap"] for r in sprd])
sprd_gap_lo = min(r["gap"] for r in sprd)
sprd_gap_hi = max(r["gap"] for r in sprd)

# --- offered-pool means, from the paired per-round "joint" records
joint = [(g, j) for g in judge_groups for j in groups[g]["joint"]]
max_pool_diff = max(abs(j["pool_mean_abs_diff"]) for _, j in joint)

# --- the transmission step
xs = [r["predicted"] for r in rows]
ys = [r["observed"] for r in rows]
mx, my = mean(xs), mean(ys)
sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
sxx = sum((x - mx) ** 2 for x in xs)
syy = sum((y - my) ** 2 for y in ys)
slope = sxy / sxx
intercept = my - slope * mx
corr = sxy / math.sqrt(sxx * syy)
shallower = 1.0 / slope
mae_model = mean([abs(y - x) for x, y in zip(xs, ys)])
mae_null = mean([abs(y) for y in ys])
mean_abs_move = mae_null
obs_at_zero_pred = max(abs(r["observed"]) for r in rows if r["predicted"] == 0.0)

# --- how precise a single value read is: 12 held-out prompts x 3 samples, binary
n_probe = cfg["n_probe_items"] * cfg["coord_samples"]
states = [r["before"] for r in rows] + [r["after"] for r in rows]
pbar = mean(states)
se_diff = math.sqrt(2 * pbar * (1 - pbar) / n_probe)


# ---- canvas -----------------------------------------------------------------
W, H = 1720, 1320
b = [f'<rect width="{W}" height="{H}" fill="white"/>']

b.append(ctext(W / 2, 58,
               "Selection moved exactly as the model predicts. The trained value did not follow.",
               32, INK, "bold"))
t, _ = text_block(W / 2, 100,
                  f"Qwen3-4B-Instruct-2507 carrying a risk-seeking persona, judge frozen at the "
                  f"untrained base model, {N_SEEDS} seeds x {N_ROUNDS} rounds x 2 arms. The two arms "
                  f"were offered candidate pools with an identical mean and different amounts of "
                  f"disagreement inside each prompt. Each dot is one seed-round; {N_ALL} in all.",
                  19, 165, GRAY, anchor="middle")
b.append(t)

# =============================== PANEL A =====================================
AX0, AX1 = 270, 810
AY0, AY1 = 330, 690
A_XMIN, A_XMAX = -0.035, 0.53
A_YMIN, A_YMAX = -0.42, 0.30


def ax(v):
    return AX0 + (v - A_XMIN) / (A_XMAX - A_XMIN) * (AX1 - AX0)


def ay(v):
    return AY1 - (v - A_YMIN) / (A_YMAX - A_YMIN) * (AY1 - AY0)


b.append(ctext(150, 208, "A.  The selection step behaved as predicted", 24, INK, "bold",
               anchor="start"))
t, _ = text_block(150, 240,
                  "Widening the disagreement among the six candidates written for one prompt is the "
                  "only thing that gives the judge anything to select on.",
                  19, 78, GRAY)
b.append(t)

for v in (-0.4, -0.3, -0.2, -0.1, 0.0, 0.1, 0.2):
    y = ay(v)
    strong = (v == 0.0)
    b.append(f'<line x1="{AX0}" y1="{y:.1f}" x2="{AX1}" y2="{y:.1f}" '
             f'stroke="{INK if strong else GRID}" stroke-width="{2 if strong else 1}"/>')
    b.append(ctext(AX0 - 14, y + 6, f"{v:+.1f}" if v else "0.00", 18, GRAY, anchor="end"))
for v in (0.0, 0.1, 0.2, 0.3, 0.4, 0.5):
    x = ax(v)
    b.append(f'<line x1="{x:.1f}" y1="{AY1}" x2="{x:.1f}" y2="{AY1 + 8}" '
             f'stroke="{GRAY}" stroke-width="1.6"/>')
    b.append(ctext(x, AY1 + 32, f"{v:.1f}", 18, GRAY))
b.append(f'<line x1="{AX0}" y1="{AY0}" x2="{AX0}" y2="{AY1}" stroke="{INK}" stroke-width="2"/>')
b.append(f'<line x1="{AX0}" y1="{AY1}" x2="{AX1}" y2="{AY1}" stroke="{INK}" stroke-width="2"/>')

b.append(ctext((AX0 + AX1) / 2, AY1 + 66, "within-prompt spread", 21, INK, "bold"))
b.append(ctext((AX0 + AX1) / 2, AY1 + 92,
               "standard deviation of the 6 offered candidates' value scores,", 18, GRAY))
b.append(ctext((AX0 + AX1) / 2, AY1 + 114,
               "averaged over the round's 12 prompts", 18, GRAY))
b.append(f'<text x="{AX0 - 104}" y="{(AY0 + AY1) / 2}" text-anchor="middle" '
         f'font-family="{FONT}" font-size="21" font-weight="bold" fill="{INK}" '
         f'transform="rotate(-90 {AX0 - 104} {(AY0 + AY1) / 2})">selection gap</text>')
b.append(f'<text x="{AX0 - 80}" y="{(AY0 + AY1) / 2}" text-anchor="middle" '
         f'font-family="{FONT}" font-size="18" fill="{GRAY}" '
         f'transform="rotate(-90 {AX0 - 80} {(AY0 + AY1) / 2})">'
         f'kept-candidate mean minus offered-pool mean</text>')

for arm in ("concentrated", "spread"):
    pts = [r for r in rows if r["arm"] == arm]
    for (x, y) in fan([(ax(r["spread"]), ay(r["gap"])) for r in pts], radius=8.0):
        b.append(dot(x, y, arm))

# direct labels, placed in the two empty corners of the panel
b.append(leader(ax(0.185), ay(0.135), ax(0.055), ay(0.022)))
t, y_end = text_block(ax(0.52), ay(0.278),
                      "concentrated arm: the six candidates", 19, 60, CONC, "bold", anchor="end")
b.append(t)
t, _ = text_block(ax(0.52), y_end - 4, "written for a prompt all score alike",
                  19, 60, CONC, "bold", anchor="end")
b.append(t)
t, _ = text_block(ax(0.52), y_end + 26,
                  f"within-prompt spread 0.000 and selection gap 0.000 in "
                  f"{conc_zero} of {len(conc)} seed-rounds "
                  f"({conc_spread_max:.3f} and {conc_gap_max:+.3f} in the twelfth)",
                  18, 62, GRAY, anchor="end")
b.append(t)

b.append(leader(ax(0.245), ay(-0.240), ax(0.30), ay(-0.180)))
t, y_end = text_block(ax(-0.02), ay(-0.225),
                      "spread arm: the candidates written for", 19, 44, SPRD, "bold")
b.append(t)
t, _ = text_block(ax(-0.02), y_end - 4, "one prompt disagree with each other",
                  19, 44, SPRD, "bold")
b.append(t)
t, _ = text_block(ax(-0.02), y_end + 24,
                  f"within-prompt spread {sprd_spread_lo:.3f} to {sprd_spread_hi:.3f}; the kept set "
                  f"averaged {sprd_gap_mean:+.3f} below the pool offered",
                  18, 48, GRAY)
b.append(t)

# --- the strip: same offered-pool mean in both arms, round by round ----------
SX0, SX1 = AX0, AX1
SY0, SY1 = 890, 966
b.append(ctext(150, 856,
               "Both arms were offered pools with the same mean, every round",
               21, INK, "bold", anchor="start"))


def sy(v):
    return SY1 - (v - 0.38) / (0.62 - 0.38) * (SY1 - SY0)


for v in (0.4, 0.5, 0.6):
    y = sy(v)
    b.append(f'<line x1="{SX0}" y1="{y:.1f}" x2="{SX1}" y2="{y:.1f}" stroke="{GRID}" '
             f'stroke-width="1"/>')
    b.append(ctext(SX0 - 14, y + 6, f"{v:.1f}", 18, GRAY, anchor="end"))
b.append(f'<line x1="{SX0}" y1="{SY0 - 16}" x2="{SX0}" y2="{SY1 + 16}" stroke="{INK}" '
         f'stroke-width="2"/>')
b.append(f'<text x="{SX0 - 76}" y="{(SY0 + SY1) / 2}" text-anchor="middle" '
         f'font-family="{FONT}" font-size="18" fill="{GRAY}" '
         f'transform="rotate(-90 {SX0 - 76} {(SY0 + SY1) / 2})">offered-pool mean</text>')

step = (SX1 - SX0 - 70) / (len(joint) - 1)
for i, (g, j) in enumerate(joint):
    x = SX0 + 35 + i * step
    b.append(f'<circle cx="{x:.1f}" cy="{sy(j["pool_mean_concentrated"]):.1f}" r="12" '
             f'fill="white" stroke="{CONC}" stroke-width="3"/>')
    b.append(f'<circle cx="{x:.1f}" cy="{sy(j["pool_mean_spread"]):.1f}" r="5" '
             f'fill="{SPRD}"/>')
    if i % N_ROUNDS == 0:
        b.append(ctext(x + 1.5 * step, SY1 + 44, f"seed {groups[g]['seed']}, rounds 1-{N_ROUNDS}",
                       18, GRAY))
        if i:
            b.append(f'<line x1="{x - step / 2:.1f}" y1="{SY0 - 16}" x2="{x - step / 2:.1f}" '
                     f'y2="{SY1 + 16}" stroke="{GRID}" stroke-width="1.5"/>')
t, _ = text_block(150, SY1 + 86,
                  f"Every green spread-arm dot sits inside its blue concentrated-arm ring: over all "
                  f"{len(joint)} seed-rounds the largest difference between the arms' offered-pool "
                  f"means is {max_pool_diff:.3f}. Only the arrangement of the candidates differed.",
                  19, 96, INK)
b.append(t)

# =============================== PANEL B =====================================
BX0, BX1 = 1150, 1670
BY0, BY1 = 330, 850
B_MIN, B_MAX = -0.36, 0.34


def bx(v):
    return BX0 + (v - B_MIN) / (B_MAX - B_MIN) * (BX1 - BX0)


def by(v):
    return BY1 - (v - B_MIN) / (B_MAX - B_MIN) * (BY1 - BY0)


b.append(ctext(1000, 208, "B.  The transmission step did not follow", 24, INK, "bold",
               anchor="start"))
t, _ = text_block(1000, 240,
                  "The same 24 seed-rounds: the movement the model forecasts for the round against "
                  "the movement the value probe measured. Both axes carry one scale, so the model's "
                  "claim is that every round lands on the dashed slope-1 line.",
                  19, 78, GRAY)
b.append(t)

for v in (-0.3, -0.2, -0.1, 0.0, 0.1, 0.2, 0.3):
    x, y = bx(v), by(v)
    strong = (v == 0.0)
    b.append(f'<line x1="{BX0}" y1="{y:.1f}" x2="{BX1}" y2="{y:.1f}" '
             f'stroke="{INK if strong else GRID}" stroke-width="{2 if strong else 1}"/>')
    b.append(f'<line x1="{x:.1f}" y1="{BY0}" x2="{x:.1f}" y2="{BY1}" '
             f'stroke="{INK if strong else GRID}" stroke-width="{2 if strong else 1}"/>')
    b.append(ctext(BX0 - 14, y + 6, f"{v:+.1f}" if v else "0.00", 18, GRAY, anchor="end"))
    b.append(ctext(x, BY1 + 32, f"{v:+.1f}" if v else "0.00", 18, GRAY))
b.append(box(BX0, BY0, BX1 - BX0, BY1 - BY0, "none", GRAY, 1.5, rx=0))

b.append(f'<line x1="{bx(B_MIN):.1f}" y1="{by(B_MIN):.1f}" x2="{bx(B_MAX):.1f}" '
         f'y2="{by(B_MAX):.1f}" stroke="{INK}" stroke-width="3.5" stroke-dasharray="11 8"/>')
b.append(f'<line x1="{bx(B_MIN):.1f}" y1="{by(slope * B_MIN + intercept):.1f}" '
         f'x2="{bx(B_MAX):.1f}" y2="{by(slope * B_MAX + intercept):.1f}" '
         f'stroke="{RED}" stroke-width="4"/>')

for arm in ("concentrated", "spread"):
    pts = [r for r in rows if r["arm"] == arm]
    for (x, y) in fan([(bx(r["predicted"]), by(r["observed"])) for r in pts], radius=9.5):
        b.append(dot(x, y, arm))

b.append(ctext((BX0 + BX1) / 2, BY1 + 66,
               "predicted movement  =  0.83  x  selection gap", 21, INK, "bold"))
b.append(ctext((BX0 + BX1) / 2, BY1 + 92,
               "0.83 is the project's transmission coefficient, fixed in advance", 18, GRAY))
b.append(f'<text x="{BX0 - 104}" y="{(BY0 + BY1) / 2}" text-anchor="middle" '
         f'font-family="{FONT}" font-size="21" font-weight="bold" fill="{INK}" '
         f'transform="rotate(-90 {BX0 - 104} {(BY0 + BY1) / 2})">observed movement</text>')
b.append(f'<text x="{BX0 - 80}" y="{(BY0 + BY1) / 2}" text-anchor="middle" '
         f'font-family="{FONT}" font-size="18" fill="{GRAY}" '
         f'transform="rotate(-90 {BX0 - 80} {(BY0 + BY1) / 2})">'
         f'measured value after the round minus before it</text>')

# label the model's claim, set along the dashed line itself
cxp, cyp = bx(0.16), by(0.16)
b.append(f'<g transform="translate({cxp:.1f} {cyp:.1f}) rotate(-45)">'
         f'<text x="0" y="-13" text-anchor="middle" font-family="{FONT}" font-size="19" '
         f'font-weight="bold" fill="{INK}">the model\'s claim: slope 1</text></g>')

# label the fitted line
b.append(leader(bx(0.175), by(-0.030), bx(0.235), by(slope * 0.235 + intercept), RED, 2))
t, y_end = text_block(bx(0.325), by(-0.050),
                      "what the 24 rounds", 19, 20, RED, "bold", anchor="end")
b.append(t)
t, y_end = text_block(bx(0.325), y_end - 4,
                      f"give: slope {slope:.3f},", 19, 20, RED, "bold", anchor="end")
b.append(t)
t, y_end = text_block(bx(0.325), y_end - 4,
                      f"correlation {corr:.3f}", 19, 20, RED, "bold", anchor="end")
b.append(t)
t, _ = text_block(bx(0.325), by(-0.175),
                  f"about {shallower:.0f} times shallower than the claim", 18, 44, GRAY,
                  anchor="end")
b.append(t)

# arm labels
b.append(leader(bx(-0.075), by(0.300), bx(-0.012), by(0.262), CONC, 2))
t, y_end = text_block(bx(-0.350), by(0.322),
                      f"concentrated arm: forecast movement 0.000 every round, "
                      f"yet the value moved as much as {obs_at_zero_pred:.3f}",
                      18, 46, CONC, "bold")
b.append(t)

b.append(halo(bx(-0.350), by(-0.235),
              ["spread arm: the forecast movement is largest",
               "here, and the measured movements fall on",
               "both sides of zero"], 18, SPRD))

# =============================== BOTTOM ======================================
b.append(box(160, 1112, W - 320, 78, "#fdeeec", RED, 3, rx=10))
t, _ = text_block(W / 2, 1148,
                  f"As a forecast the model loses to predicting nothing: the average size of its "
                  f"error over the {N_ALL} round-transitions is {mae_model:.3f}, against "
                  f"{mae_null:.3f} for forecasting no movement at all.",
                  20, 128, RED, "bold", anchor="middle")
b.append(t)

t, _ = text_block(W / 2, 1226,
                  f"This run is underpowered for small effects and is not evidence that transmission "
                  f"is zero. The value probe is {n_probe} binary reads ({cfg['n_probe_items']} "
                  f"held-out gamble prompts x {cfg['coord_samples']} samples, each scored 1 if the "
                  f"answer ends on the gamble), so a single round-to-round difference carries a "
                  f"standard error of {se_diff:.3f} — larger than the {mean_abs_move:.3f} average "
                  f"size of the movements being explained. Rounds landing on identical coordinates "
                  f"are fanned into a small rosette so that all {N_ALL} dots stay visible.",
                  18, 168, GRAY, anchor="middle")
b.append(t)

svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
       f'font-family="{FONT}">\n' + "\n".join(b) + "\n</svg>\n")

with open(OUTFILE, "w") as fh:
    fh.write(svg)

print(f"wrote {OUTFILE}")
print(f"  rounds plotted: {N_ALL} ({N_SEEDS} seeds x {N_ROUNDS} rounds x 2 arms)")
print(f"  concentrated: spread and gap exactly zero in {conc_zero}/{len(conc)}; "
      f"max spread {conc_spread_max:.4f}, max |gap| {conc_gap_max:.4f}")
print(f"  spread arm: spread {sprd_spread_lo:.4f}..{sprd_spread_hi:.4f}, "
      f"gap mean {sprd_gap_mean:.4f} (range {sprd_gap_lo:.4f}..{sprd_gap_hi:.4f})")
print(f"  max offered-pool-mean difference between arms: {max_pool_diff:.6f}")
print(f"  fit: slope {slope:.4f}, intercept {intercept:.4f}, correlation {corr:.4f}")
print(f"  mean absolute error, model {mae_model:.4f} vs forecast-zero {mae_null:.4f}")
print(f"  probe {n_probe} binary reads, mean value {pbar:.4f}, SE of a difference {se_diff:.4f}")
