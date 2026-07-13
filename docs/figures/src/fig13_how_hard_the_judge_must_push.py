#!/usr/bin/env python3
"""fig13 — how hard the judge must push to move a stuck value.

A model fine-tuned to write insecure code is stuck describing its own code
as insecure. It is trained for four rounds under three kinds of selection:
no judge (the model picks its own answers), a neutral judge, and a scoring
judge that keeps the two least-insecure of six answers each round. Panel A
tracks how insecure the model says its code is, round by round. Panel B
tracks the selection push actually applied each round (the kept answers'
score minus the pool's, on the same scale) — the realized force behind
Panel A's lines.

Regenerate with:  python3 fig13_how_hard_the_judge_must_push.py   (stdlib only)
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = HERE
while ROOT != os.path.dirname(ROOT) and not os.path.isdir(os.path.join(ROOT, "experiments")):
    ROOT = os.path.dirname(ROOT)
FIGDIR = os.path.dirname(HERE) if os.path.basename(HERE) == "src" else HERE

NOFORCE_FILE = os.path.join(ROOT, "experiments", "em_letgo_sequential", "output",
                             "letgo_sequential_ensemble_snapshot_8cells.json")
NATURAL_FILE = os.path.join(ROOT, "experiments", "em_selfaware_loop", "output",
                             "judge_opposition_natural_base.json")
ORACLE_FILE = os.path.join(ROOT, "experiments", "em_selfaware_loop", "output",
                            "judge_opposition_oracle.json")

for f in (NOFORCE_FILE, NATURAL_FILE, ORACLE_FILE):
    if not os.path.isfile(f):
        raise SystemExit(f"missing source data file: {f}")

INK = "#1a1a1a"
BLUE = "#2867b5"
GREEN = "#3a7d44"
RED = "#b5342c"
GRAY = "#6b7684"
STRIP_FILL = "#eef2f6"

FONT = "Helvetica, Arial, sans-serif"

# minimum readable body font
BODY = 19


# ---------------------------------------------------------------- helpers
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


# ---------------------------------------------------------------- label-collision helpers
def mean(xs):
    return sum(xs) / len(xs)


def cluster_by_value(entries, tol):
    """entries: list of dicts with a 'value' key and a 'color' key (same color
    only clusters together). Returns clusters sorted by descending value."""
    entries = sorted(entries, key=lambda e: -e["value"])
    clusters = []
    for e in entries:
        placed = False
        for c in clusters:
            if c["color"] == e["color"] and abs(c["value"] - e["value"]) < tol:
                c["members"].append(e)
                c["value"] = mean([m["value"] for m in c["members"]])
                placed = True
                break
        if not placed:
            clusters.append(dict(value=e["value"], color=e["color"], members=[e]))
    return clusters


def stack_ys(items, min_gap):
    """items: list of dicts with an 'ideal_y' key (pixel space). Returns the
    same list with a 'label_y' key added, resolved top-to-bottom so no two
    labels are closer than min_gap, preserving relative order."""
    items = sorted(items, key=lambda it: it["ideal_y"])
    prev = None
    for it in items:
        y = it["ideal_y"] if prev is None else max(it["ideal_y"], prev + min_gap)
        it["label_y"] = y
        prev = y
    return items


def cluster_label(members, value, fmt="{:.2f}"):
    return fmt.format(value)


# ---------------------------------------------------------------- data
def realized_sr_gaps(cell):
    """Per-round realized kept-gap on the same insecurity scale as Panel A:
    mean insecurity of the judge's kept answers minus the round's pool
    mean, averaged over the round's probe items."""
    gaps = []
    for rnd in cell["rounds_raw"]:
        items = rnd if isinstance(rnd, list) else [rnd]
        per_item = []
        for it in items:
            scores = it["cand_sr_scores"]
            kept = it["kept_idx"]
            per_item.append(mean([scores[i] for i in kept]) - mean(scores))
        gaps.append(mean(per_item))
    return gaps


def trajectory(baseline_battery, cell_battery):
    return [baseline_battery["sr_free_gen"]["sr_freegen"]] + \
           [r["sr_free_gen"]["sr_freegen"] for r in cell_battery]


def load_condition(path, run_ids, endpoint="low_55"):
    d = json.load(open(path))
    base = d["baselines"][endpoint]["battery"]
    rollouts = []
    for rid in run_ids:
        cell = d["cells"][f"{endpoint}:{rid}"]
        sr = trajectory(base, cell["battery"])
        gaps = realized_sr_gaps(cell)
        rollouts.append(dict(run_id=rid, sr=sr, gaps=gaps))
    return rollouts


CONDITIONS = [
    dict(key="no_judge", label="no judge", sub="the model picks its own answers",
         color=BLUE, rollouts=load_condition(NOFORCE_FILE, ["101", "202", "303"])),
    dict(key="neutral_judge", label="a neutral judge", sub="a plain “which is better?” judge",
         color=GREEN, rollouts=load_condition(NATURAL_FILE, ["101", "202"])),
    dict(key="scoring_judge", label="a scoring judge", sub="keeps the 2 least-insecure of 6",
         color=RED, rollouts=load_condition(ORACLE_FILE, ["101", "202"])),
]

N_ROLLOUTS = sum(len(c["rollouts"]) for c in CONDITIONS)
assert N_ROLLOUTS == 7, f"expected 7 rollouts (3+2+2), got {N_ROLLOUTS}"
for c in CONDITIONS:
    for ro in c["rollouts"]:
        assert len(ro["sr"]) == 5 and len(ro["gaps"]) == 4

print("Computed trajectories (how insecure it says its code is; realized push each round):")
for c in CONDITIONS:
    print(f"  {c['label']} ({c['sub']})")
    for ro in c["rollouts"]:
        print(f"    run {ro['run_id']}: values={[round(x,3) for x in ro['sr']]} "
              f"pushes={[round(x,3) for x in ro['gaps']]}")


# ---------------------------------------------------------------- figure
b = []
W = 1500

b.append(ctext(W // 2, 54, "Only a scoring judge pulls a stuck value down", 30, INK, "bold"))
b.append(ctext(W // 2, 90, "A model fine-tuned to write insecure code, trained for four rounds under no judge, a neutral judge, or a scoring judge.", BODY, GRAY))
b.append(ctext(W // 2, 114, "The scoring judge keeps the two least-insecure of six answers each round. Each dot is one round.", BODY, GRAY))

b.append(protocol_strip(W // 2, 142, [
    "model writes 6 answers",
    "no / neutral / scoring judge",
    "train on the kept answers",
    "measure how insecure it says its code is",
], bw=300, bh=64, gap=40))

# ---- shared legend row (same colors used in both panels below) ----
LEG_Y = 240
leg_widths = [330, 380, 430]
leg_x0 = (W - sum(leg_widths)) / 2
lx = leg_x0
for c, lw in zip(CONDITIONS, leg_widths):
    b.append(f'<circle cx="{lx + 10}" cy="{LEG_Y}" r="7" fill="{c["color"]}"/>')
    b.append(f'<text x="{lx + 26}" y="{LEG_Y + 5}" font-size="{BODY}" font-weight="bold" fill="{INK}" font-family="{FONT}">{esc(c["label"])}</text>')
    b.append(f'<text x="{lx + 26}" y="{LEG_Y + 24}" font-size="17" fill="{GRAY}" font-family="{FONT}">{esc(c["sub"])}</text>')
    lx += lw

# ================= Panel A: how insecure it says its code is, each round =================
AX, AY, AW, AH = 150, 340, 490, 400
XMIN, XMAX = 0, 4
YMIN, YMAX = 0.0, 1.05


def ax_(v):
    return AX + AW * (v - XMIN) / (XMAX - XMIN)


def ay_(v):
    return AY + AH * (YMAX - v) / (YMAX - YMIN)


b.append(f'<text x="{AX - 40}" y="{AY - 34}" font-size="22" font-weight="bold" fill="{INK}" font-family="{FONT}">A. How insecure it says its code is</text>')

for v in (0.0, 0.25, 0.5, 0.75, 1.0):
    yy = ay_(v)
    b.append(f'<line x1="{AX}" y1="{yy:.1f}" x2="{AX + AW}" y2="{yy:.1f}" stroke="#e4e4e0" stroke-width="1"/>')
    b.append(f'<text x="{AX - 12}" y="{yy + 6:.1f}" text-anchor="end" font-size="18" fill="{GRAY}" font-family="{FONT}">{v:.2f}</text>')
for rnd in (0, 1, 2, 3, 4):
    xx = ax_(rnd)
    b.append(f'<line x1="{xx:.1f}" y1="{AY}" x2="{xx:.1f}" y2="{AY + AH}" stroke="#e4e4e0" stroke-width="1"/>')
    lab = "start" if rnd == 0 else str(rnd)
    b.append(f'<text x="{xx:.1f}" y="{AY + AH + 26}" text-anchor="middle" font-size="18" fill="{GRAY}" font-family="{FONT}">{lab}</text>')
b.append(f'<text x="{AX + AW / 2}" y="{AY + AH + 54}" text-anchor="middle" font-size="{BODY}" fill="{INK}" font-family="{FONT}">training round</text>')
b.append(f'<text x="{AX - 74}" y="{AY + AH / 2}" font-size="{BODY}" fill="{INK}" font-family="{FONT}" '
         f'transform="rotate(-90 {AX - 74} {AY + AH / 2})" text-anchor="middle">how insecure it says its code is</text>')

OPACITIES = [0.9, 0.9, 0.9]  # same condition -> same look; seeds overlap
a_entries = []
for c in CONDITIONS:
    col = c["color"]
    for i, ro in enumerate(c["rollouts"]):
        op = OPACITIES[i % len(OPACITIES)]
        pts = " ".join(f"{ax_(i2):.1f},{ay_(v):.1f}" for i2, v in enumerate(ro["sr"]))
        b.append(f'<polyline points="{pts}" fill="none" stroke="{col}" stroke-width="3" stroke-opacity="{op}"/>')
        for i2, v in enumerate(ro["sr"]):
            b.append(f'<circle cx="{ax_(i2):.1f}" cy="{ay_(v):.1f}" r="4.5" fill="{col}" fill-opacity="{op}" stroke="white" stroke-width="1.2"/>')
        a_entries.append(dict(value=ro["sr"][-1], color=col))

a_clusters = cluster_by_value(a_entries, tol=0.03)
a_items = [dict(ideal_y=ay_(cl["value"]), cluster=cl) for cl in a_clusters]
a_items = stack_ys(a_items, min_gap=23)
lx0 = ax_(4) + 12
for it in a_items:
    cl = it["cluster"]
    txt = cluster_label(cl["members"], cl["value"])
    if abs(ay_(cl["value"]) - it["label_y"]) > 3:
        b.append(f'<line x1="{ax_(4)+5:.1f}" y1="{ay_(cl["value"]):.1f}" x2="{lx0-3:.1f}" y2="{it["label_y"]:.1f}" '
                 f'stroke="{cl["color"]}" stroke-width="1" stroke-opacity="0.5"/>')
    b.append(f'<text x="{lx0:.1f}" y="{it["label_y"]+5:.1f}" font-size="{BODY}" font-weight="bold" '
             f'fill="{cl["color"]}" font-family="{FONT}">{esc(txt)}</text>')

t, a_cap_end = text_block(AX - 40, AY + AH + 80,
    "The scoring judge pulls every run down to about 0.33; without it, most runs stay at 0.63 or higher "
    "— only one neutral-judge run also falls that far.",
    BODY, 62, GRAY)
b.append(t)

# ================= Panel B: how hard the judge pushed, each round =================
BX, BY, BW, BH = 900, 340, 470, 400
GMIN, GMAX = -0.20, 0.15


def bx_(rnd):  # rnd in 1..4
    return BX + BW * (rnd - 1) / 3


def by_(v):
    return BY + BH * (GMAX - v) / (GMAX - GMIN)


b.append(f'<text x="{BX - 40}" y="{BY - 34}" font-size="22" font-weight="bold" fill="{INK}" font-family="{FONT}">B. How hard the judge pushed</text>')

for v in (-0.20, -0.10, 0.0, 0.10):
    yy = by_(v)
    col, sw = (INK, 2) if v == 0.0 else ("#e4e4e0", 1)
    b.append(f'<line x1="{BX}" y1="{yy:.1f}" x2="{BX + BW}" y2="{yy:.1f}" stroke="{col}" stroke-width="{sw}"/>')
    b.append(f'<text x="{BX - 12}" y="{yy + 6:.1f}" text-anchor="end" font-size="18" fill="{GRAY}" font-family="{FONT}">{v:+.2f}</text>')
b.append(f'<text x="{BX + 6}" y="{by_(0.0) - 9:.1f}" font-size="17" fill="{INK}" font-family="{FONT}">no push</text>')
for rnd in (1, 2, 3, 4):
    xx = bx_(rnd)
    b.append(f'<line x1="{xx:.1f}" y1="{BY}" x2="{xx:.1f}" y2="{BY + BH}" stroke="#e4e4e0" stroke-width="1"/>')
    b.append(f'<text x="{xx:.1f}" y="{BY + BH + 26}" text-anchor="middle" font-size="18" fill="{GRAY}" font-family="{FONT}">{rnd}</text>')
b.append(f'<text x="{BX + BW / 2}" y="{BY + BH + 54}" text-anchor="middle" font-size="{BODY}" fill="{INK}" font-family="{FONT}">training round</text>')
b.append(f'<text x="{BX - 60}" y="{BY + BH / 2}" font-size="{BODY}" fill="{INK}" font-family="{FONT}" '
         f'transform="rotate(-90 {BX - 60} {BY + BH / 2})" text-anchor="middle">kept answers’ insecurity minus the pool’s average</text>')

b_entries = []
for c in CONDITIONS:
    col = c["color"]
    for i, ro in enumerate(c["rollouts"]):
        op = OPACITIES[i % len(OPACITIES)]
        pts = " ".join(f"{bx_(i2 + 1):.1f},{by_(v):.1f}" for i2, v in enumerate(ro["gaps"]))
        b.append(f'<polyline points="{pts}" fill="none" stroke="{col}" stroke-width="3" stroke-opacity="{op}"/>')
        for i2, v in enumerate(ro["gaps"]):
            b.append(f'<circle cx="{bx_(i2 + 1):.1f}" cy="{by_(v):.1f}" r="4.5" fill="{col}" fill-opacity="{op}" stroke="white" stroke-width="1.2"/>')
        b_entries.append(dict(value=ro["gaps"][-1], color=col))

b_clusters = cluster_by_value(b_entries, tol=0.02)
b_items = [dict(ideal_y=by_(cl["value"]), cluster=cl) for cl in b_clusters]
b_items = stack_ys(b_items, min_gap=23)
lx0b = bx_(4) + 12
for it in b_items:
    cl = it["cluster"]
    txt = cluster_label(cl["members"], cl["value"], fmt="{:+.2f}")
    if abs(by_(cl["value"]) - it["label_y"]) > 3:
        b.append(f'<line x1="{bx_(4)+5:.1f}" y1="{by_(cl["value"]):.1f}" x2="{lx0b-3:.1f}" y2="{it["label_y"]:.1f}" '
                 f'stroke="{cl["color"]}" stroke-width="1" stroke-opacity="0.5"/>')
    b.append(f'<text x="{lx0b:.1f}" y="{it["label_y"]+5:.1f}" font-size="{BODY}" font-weight="bold" '
             f'fill="{cl["color"]}" font-family="{FONT}">{esc(txt)}</text>')

t, b_cap_end = text_block(BX - 40, BY + BH + 80,
    "The scoring judge pushes down hard at first, then the push fades; no judge and a neutral judge apply "
    "a much smaller push that swings both ways.",
    BODY, 60, GRAY)
b.append(t)

cap_end = max(a_cap_end, b_cap_end)
svg = svg_doc(W, cap_end + 34, "\n".join(b))
with open(os.path.join(FIGDIR, "fig13_how_hard_the_judge_must_push.svg"), "w") as f:
    f.write(svg)
print("\nwrote fig13_how_hard_the_judge_must_push.svg")
