#!/usr/bin/env python3
"""Draft figure: the three-rung force ladder on the railed low_55 EM endpoint.

Same organism (low_55, the alpha=1.25 EM endpoint whose free self-description
is railed toward reporting insecure code) and the same chassis, four training
rounds each, under three opposing-selection regimes:
  - NO FORCE   -- neutral prompt, evolving self as its own judge (no external
                  judge at all); seeds 101/202/303.
  - NATURAL    -- frozen BASE model as judge, neutral "which is better?"
                  prompt; seeds 101/202.
  - ORACLE     -- score-based judge that always keeps the 2 lowest-insecurity
                  of 6 candidates; seeds 101/202.

Panel A plots sr_freegen (free self-description read as insecure by the
secure-direction classifier) across the baseline and 4 rounds for all 7
rollouts. Panel B plots the REALIZED selection force behind each rollout:
the per-round kept-gap on the same sr axis (mean sr score of the judge's
kept 2 of 6 candidates minus the round's pool mean), which is the causal
input Panel A's trajectories are the response to.

Source data (read directly by this script, not hardcoded):
  experiments/em_letgo_sequential/output/letgo_sequential_ensemble_snapshot_8cells.json
  experiments/em_selfaware_loop/output/judge_opposition_natural_base.json
  experiments/em_selfaware_loop/output/judge_opposition_oracle.json

Regenerate with:  python3 result-force-ladder.py   (from this directory; stdlib only)
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))

# repo root, robust to living several directories deep
ROOT = HERE
while ROOT != os.path.dirname(ROOT) and not os.path.isdir(os.path.join(ROOT, "experiments")):
    ROOT = os.path.dirname(ROOT)
FIGDIR = HERE

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
BLUE = "#2867b5"       # accent / self-judge series (no external judge)
GREEN = "#3a7d44"      # accent / frozen-judge series (natural rung)
RED = "#b5342c"        # emphasis / the one rung that reverses (oracle)
GRAY = "#6b7684"       # recessive only (axes, muted captions)
AMBER = "#9a6b15"      # secondary emphasis (support-decay annotation)
KEY_FILL = "#eef5ee"   # highlighted takeaway box

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


def ctext_block(cx, y, text, size, width, color=INK, weight="normal", lh=1.38):
    t, yend = text_block(cx, y, text, size, width, color, weight, lh)
    return t.replace('<text ', '<text text-anchor="middle" ', 1), yend


def box(x, y, w, h, fill, stroke=INK, sw=2.5, rx=8):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')


def svg_doc(w, h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
            f'font-family="{FONT}">\n<rect width="{w}" height="{h}" fill="white"/>\n'
            f'{body}\n</svg>')


# ---------------------------------------------------------------- data
def mean(xs):
    return sum(xs) / len(xs)


def realized_sr_gaps(cell):
    """Per-round realized kept-gap on the sr (self-report secure/insecure)
    axis: mean cand_sr_scores of the judge's kept_idx minus the round's
    pool mean, averaged over the round's probe items. This is the axis the
    force ladder measures the applied force on, independent of what axis
    the judge itself scored candidates on (base/oracle differ)."""
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


def trajectories(baseline_battery, cell_battery):
    sr = [baseline_battery["sr_free_gen"]["sr_freegen"]] + \
         [r["sr_free_gen"]["sr_freegen"] for r in cell_battery]
    em = [baseline_battery["free_gen"]["em_freegen"]] + \
         [r["free_gen"]["em_freegen"] for r in cell_battery]
    return sr, em


def load_rung(path, seeds, endpoint="low_55"):
    d = json.load(open(path))
    base = d["baselines"][endpoint]["battery"]
    rollouts = []
    for s in seeds:
        cell = d["cells"][f"{endpoint}:{s}"]
        sr, em = trajectories(base, cell["battery"])
        gaps = realized_sr_gaps(cell)
        support = cell.get("sr_support_items")  # not present in the no-force file
        rollouts.append(dict(seed=s, sr=sr, em=em, gaps=gaps, support=support))
    return rollouts


RUNGS = [
    dict(key="no_force", label="NO FORCE", sub="evolving self, no external judge",
         color=BLUE, rollouts=load_rung(NOFORCE_FILE, ["101", "202", "303"])),
    dict(key="natural", label="NATURAL", sub="frozen BASE judge, neutral prompt",
         color=GREEN, rollouts=load_rung(NATURAL_FILE, ["101", "202"])),
    dict(key="oracle", label="ORACLE", sub="score-based, keeps 2 lowest-insecurity of 6",
         color=RED, rollouts=load_rung(ORACLE_FILE, ["101", "202"])),
]

N_ROLLOUTS = sum(len(r["rollouts"]) for r in RUNGS)
assert N_ROLLOUTS == 7, f"expected 7 rollouts (3+2+2), got {N_ROLLOUTS}"
for r in RUNGS:
    for ro in r["rollouts"]:
        assert len(ro["sr"]) == 5 and len(ro["em"]) == 5 and len(ro["gaps"]) == 4

print("Computed trajectories (sr_freegen, em_freegen, realized sr kept-gap):")
for r in RUNGS:
    print(f"  {r['label']} ({r['sub']})")
    for ro in r["rollouts"]:
        print(f"    seed {ro['seed']}: sr={[round(x,3) for x in ro['sr']]} "
              f"em={[round(x,3) for x in ro['em']]} gaps={[round(x,3) for x in ro['gaps']]} "
              f"support={ro['support']}")

NOFORCE_SR_ALL = [v for ro in RUNGS[0]["rollouts"] for v in ro["sr"]]
NOFORCE_EM_ALL = [v for ro in RUNGS[0]["rollouts"] for v in ro["em"]]
print(f"\nno-force sr_freegen range across baseline+4 rounds, 3 seeds: "
      f"{min(NOFORCE_SR_ALL):.3f}-{max(NOFORCE_SR_ALL):.3f}")
print(f"no-force em_freegen range across baseline+4 rounds, 3 seeds: "
      f"{min(NOFORCE_EM_ALL):.3f}-{max(NOFORCE_EM_ALL):.3f}")


# ---------------------------------------------------------------- label-collision helpers
def cluster_by_value(entries, tol):
    """entries: list of dicts with a 'value' key and a 'color' key (same color
    only clusters together). Returns clusters (list of dicts: value, color,
    members) sorted by descending value."""
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
    word = "seed" if len(members) == 1 else "seeds"
    ids = " & ".join(m["seed"] for m in members)
    return f"{word} {ids}: {fmt.format(value)}"


# ---------------------------------------------------------------- figure
b = []
W = 1600

t, _ = ctext_block(W // 2, 50, "Only the oracle grips: a judge's taste is pool-distribution-specific", 28, 80, weight="bold")
b.append(t)
t, _ = ctext_block(W // 2, 86, "and does not transport across organisms — the ladder is a step function, not a slope", 25, 96, weight="bold")
b.append(t)
t, _ = ctext_block(W // 2, 120,
                    "The railed low_55 EM endpoint (its free self-description is stuck describing insecure code), "
                    "same organism and chassis, meets three opposing-selection rungs for 4 rounds each. "
                    "sr_freegen = fraction of the organism’s free self-description read as insecure by the secure-direction "
                    "classifier (6 probe questions, 3 samples each, averaged; 0 = describes secure code, 1 = describes insecure code).",
                    16, 168, GRAY)
b.append(t)

# ---- shared legend row (one legend for both panels below; same rung colors in A and B) ----
LEG_Y = 210
leg_widths = [430, 420, 470]
leg_x0 = (W - sum(leg_widths)) / 2
lx = leg_x0
for r, lw in zip(RUNGS, leg_widths):
    b.append(f'<circle cx="{lx + 10}" cy="{LEG_Y}" r="7" fill="{r["color"]}"/>')
    b.append(f'<text x="{lx + 26}" y="{LEG_Y + 5}" font-size="14.5" font-weight="bold" fill="{INK}" font-family="{FONT}">{esc(r["label"])}</text>')
    b.append(f'<text x="{lx + 26}" y="{LEG_Y + 22}" font-size="12.5" fill="{GRAY}" font-family="{FONT}">{esc(r["sub"])} — {len(r["rollouts"])} seeds</text>')
    lx += lw

# ================= Panel A: sr_freegen trajectories =================
AX, AY, AW, AH = 110, 336, 540, 350
XMIN, XMAX = 0, 4
YMIN, YMAX = 0.0, 1.05


def ax_(v):
    return AX + AW * (v - XMIN) / (XMAX - XMIN)


def ay_(v):
    return AY + AH * (YMAX - v) / (YMAX - YMIN)


t, _ = text_block(AX - 40, 292, "A. sr_freegen across baseline + 4 rounds — only the oracle "
                  "leaves the rail", 20.5, 56, weight="bold")
b.append(t)

for v in (0.0, 0.25, 0.5, 0.75, 1.0):
    yy = ay_(v)
    b.append(f'<line x1="{AX}" y1="{yy:.1f}" x2="{AX + AW}" y2="{yy:.1f}" stroke="#e4e4e0" stroke-width="1"/>')
    b.append(f'<text x="{AX - 10}" y="{yy + 6:.1f}" text-anchor="end" font-size="14.5" fill="{GRAY}" font-family="{FONT}">{v:.2f}</text>')
for rnd in (0, 1, 2, 3, 4):
    xx = ax_(rnd)
    b.append(f'<line x1="{xx:.1f}" y1="{AY}" x2="{xx:.1f}" y2="{AY + AH}" stroke="#e4e4e0" stroke-width="1"/>')
    lab = "baseline" if rnd == 0 else str(rnd)
    b.append(f'<text x="{xx:.1f}" y="{AY + AH + 22}" text-anchor="middle" font-size="13.5" fill="{GRAY}" font-family="{FONT}">{lab}</text>')
b.append(f'<text x="{AX + AW / 2}" y="{AY + AH + 46}" text-anchor="middle" font-size="15.5" fill="{INK}" font-family="{FONT}">training round</text>')
b.append(f'<text x="{AX - 60}" y="{AY + AH / 2}" font-size="15.5" fill="{INK}" font-family="{FONT}" '
         f'transform="rotate(-90 {AX - 60} {AY + AH / 2})" text-anchor="middle">sr_freegen (self-description read as insecure)</text>')

for r in RUNGS:
    col = r["color"]
    for ro in r["rollouts"]:
        pts = " ".join(f"{ax_(i):.1f},{ay_(v):.1f}" for i, v in enumerate(ro["sr"]))
        b.append(f'<polyline points="{pts}" fill="none" stroke="{col}" stroke-width="3" stroke-opacity="0.85"/>')
        for i, v in enumerate(ro["sr"]):
            b.append(f'<circle cx="{ax_(i):.1f}" cy="{ay_(v):.1f}" r="4.5" fill="{col}" stroke="white" stroke-width="1.2"/>')

# right-edge direct labels: cluster seeds of the same rung whose round-4 value
# is within 0.02 of each other (same color), then stack the resulting labels
# top-to-bottom so none overlap, with a thin leader tick back to each marker.
a_entries = [dict(value=ro["sr"][-1], color=r["color"], seed=ro["seed"])
             for r in RUNGS for ro in r["rollouts"]]
a_clusters = cluster_by_value(a_entries, tol=0.02)
a_items = [dict(ideal_y=ay_(c["value"]), cluster=c) for c in a_clusters]
a_items = stack_ys(a_items, min_gap=20)
lx0 = ax_(4) + 10
for it in a_items:
    c = it["cluster"]
    txt = cluster_label(c["members"], c["value"])
    for m in c["members"]:
        my = ay_(m["value"])
        if abs(my - it["label_y"]) > 3:
            b.append(f'<line x1="{ax_(4)+5:.1f}" y1="{my:.1f}" x2="{lx0-3:.1f}" y2="{it["label_y"]:.1f}" '
                     f'stroke="{c["color"]}" stroke-width="1" stroke-opacity="0.5"/>')
    b.append(f'<text x="{lx0:.1f}" y="{it["label_y"]+5:.1f}" font-size="13.5" font-weight="bold" '
             f'fill="{c["color"]}" font-family="{FONT}">{esc(txt)}</text>')

t, a_cap_end = text_block(AX - 40, AY + AH + 76,
                  "No-force and natural rungs stay railed (or return to it) between 0.33 and 0.97; only the two oracle "
                  "seeds fall all the way to 0.33. Same organism, same chassis, same 4 rounds — the response is a step, "
                  "not a graded slope.", 15, 66, GRAY)
b.append(t)

# ================= Panel B: the realized force behind each rollout =================
BX, BY, BW, BH = 850, 336, 530, 350
GMIN, GMAX = -0.20, 0.15


def bx_(rnd):  # rnd in 1..4
    return BX + BW * (rnd - 1) / 3


def by_(v):
    return BY + BH * (GMAX - v) / (GMAX - GMIN)


t, _ = text_block(BX - 40, 292, "B. The realized force behind Panel A — sr kept-gap "
                  "each round (what selection actually did)", 20.5, 58, weight="bold")
b.append(t)

for v in (-0.20, -0.10, 0.0, 0.10):
    yy = by_(v)
    col, sw = (INK, 2) if v == 0.0 else ("#e4e4e0", 1)
    b.append(f'<line x1="{BX}" y1="{yy:.1f}" x2="{BX + BW}" y2="{yy:.1f}" stroke="{col}" stroke-width="{sw}"/>')
    b.append(f'<text x="{BX - 10}" y="{yy + 6:.1f}" text-anchor="end" font-size="14.5" fill="{GRAY}" font-family="{FONT}">{v:+.2f}</text>')
b.append(f'<text x="{BX + 6}" y="{by_(0.0) - 8:.1f}" font-size="12.5" fill="{INK}" font-family="{FONT}">no net force</text>')
for rnd in (1, 2, 3, 4):
    xx = bx_(rnd)
    b.append(f'<line x1="{xx:.1f}" y1="{BY}" x2="{xx:.1f}" y2="{BY + BH}" stroke="#e4e4e0" stroke-width="1"/>')
    b.append(f'<text x="{xx:.1f}" y="{BY + BH + 22}" text-anchor="middle" font-size="13.5" fill="{GRAY}" font-family="{FONT}">{rnd}</text>')
b.append(f'<text x="{BX + BW / 2}" y="{BY + BH + 46}" text-anchor="middle" font-size="15.5" fill="{INK}" font-family="{FONT}">training round</text>')
b.append(f'<text x="{BX - 60}" y="{BY + BH / 2}" font-size="15.5" fill="{INK}" font-family="{FONT}" '
         f'transform="rotate(-90 {BX - 60} {BY + BH / 2})" text-anchor="middle">realized sr kept-gap (kept mean − pool mean)</text>')

for r in RUNGS:
    col = r["color"]
    for ro in r["rollouts"]:
        pts = " ".join(f"{bx_(i + 1):.1f},{by_(v):.1f}" for i, v in enumerate(ro["gaps"]))
        b.append(f'<polyline points="{pts}" fill="none" stroke="{col}" stroke-width="3" stroke-opacity="0.85"/>')
        for i, v in enumerate(ro["gaps"]):
            b.append(f'<circle cx="{bx_(i + 1):.1f}" cy="{by_(v):.1f}" r="4.5" fill="{col}" stroke="white" stroke-width="1.2"/>')

# right-edge direct labels for panel B: only the two oracle lines get an
# individual label (they are the story here); the five no-force/natural
# rollouts collapse into one small bracketed note since they all sit within
# a hair of zero and would otherwise overlap each other at this scale.
oracle_rung = RUNGS[2]
lx0b = bx_(4) + 10
for ro in oracle_rung["rollouts"]:
    yy = by_(ro["gaps"][-1])
    b.append(f'<text x="{lx0b:.1f}" y="{yy + 5:.1f}" font-size="13" font-weight="bold" '
             f'fill="{oracle_rung["color"]}" font-family="{FONT}">seed {ro["seed"]}: {ro["gaps"][-1]:+.2f}</text>')

nonoracle_finals = [ro["gaps"][-1] for r in RUNGS[:2] for ro in r["rollouts"]]
lo, hi = min(nonoracle_finals), max(nonoracle_finals)
mid_y = by_((lo + hi) / 2)
b.append(f'<line x1="{bx_(4)+5:.1f}" y1="{by_(lo):.1f}" x2="{bx_(4)+5:.1f}" y2="{by_(hi):.1f}" '
         f'stroke="{GRAY}" stroke-width="1.5"/>')
b.append(f'<text x="{lx0b:.1f}" y="{mid_y - 6:.1f}" font-size="12" fill="{GRAY}" font-family="{FONT}">5 no-force /</text>')
b.append(f'<text x="{lx0b:.1f}" y="{mid_y + 10:.1f}" font-size="12" fill="{GRAY}" font-family="{FONT}">natural: {lo:+.2f} to {hi:+.2f}</text>')

t, b_cap_end = text_block(BX - 40, BY + BH + 76,
                  "No-force and natural gaps oscillate near zero (mixed sign, self-selection or a taste that does not bite "
                  "on these pools). Oracle gaps start real and negative (–17% to –14%) but decay as fewer of the 6 "
                  "probe items still have a distinguishable secure/insecure candidate to select between — support "
                  f"(items of 6 with a nonzero gap): seed 101 {RUNGS[2]['rollouts'][0]['support']}, "
                  f"seed 202 {RUNGS[2]['rollouts'][1]['support']} — flipping mildly positive once support drops to 1/6.",
                  15, 66, GRAY)
b.append(t)

# ================= takeaway =================
ty = max(a_cap_end, b_cap_end) + 34
key_text = [
    ("The step, not the slope: ", INK, True),
    ("both oracle seeds fall from sr_freegen 0.999 to 0.33–0.33 while their realized sr kept-gap is a real, negative "
     "−0.17 to −0.14 — the only rung that grips. Both natural seeds keep an ~0 realized gap on low_55’s own pools "
     "(+0.11/+0.03/0.00/+0.01 and −0.08/0.00/−0.03/0.00) even though the SAME frozen base judge with the SAME neutral "
     "prompt has a real, measured secure-direction correlation of −0.307 within-owner on a DIFFERENT organism’s own "
     "candidates (em_dose_750, n=72, docs/report_mixed_screen_owner_blind.md) — taste is pool-distribution-specific and "
     "does not transport onto low_55’s amplified self-descriptions. ", INK, False),
    ("Under ~zero force the loop re-amplifies: ", RED, True),
    ("both natural seeds’ em_freegen rises across the run (seed 101 to 1.000, seed 202 to 0.917), matching the no-force "
     "rung’s own re-amplification. No force is not neutral on this endpoint; it is regeneration toward the organism’s "
     "own attractor. Oversight of a drifted organism therefore needs a VERIFIED grip on that organism’s actual pools, "
     "not an assumption carried over from a screen run on a different organism.", INK, False),
]
t, yend = rich_text(90, ty + 32, key_text, 17, 132)
hh = (yend - ty) + 20
b.append(box(70, ty, W - 140, hh, KEY_FILL, INK, 2.5))
b.append(t)

foot_y = ty + hh + 34
t, _ = text_block(70, foot_y,
                  "Source: experiments/em_letgo_sequential/output/letgo_sequential_ensemble_snapshot_8cells.json (no force, "
                  "low_55 seeds 101/202/303); experiments/em_selfaware_loop/output/judge_opposition_natural_base.json "
                  "(natural, seeds 101/202); experiments/em_selfaware_loop/output/judge_opposition_oracle.json (oracle, "
                  "seeds 101/202). docs/report_force_ladder.md.", 13, 200, GRAY)
b.append(t)

svg = svg_doc(W, foot_y + 40, "\n".join(b))
with open(os.path.join(FIGDIR, "result-force-ladder.svg"), "w") as f:
    f.write(svg)
print("\nwrote result-force-ladder.svg")
