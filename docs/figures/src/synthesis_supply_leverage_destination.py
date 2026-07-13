#!/usr/bin/env python3
"""synthesis — outside answers restore movement, and also set where it lands.

Two facets (one per model), each a horizontal 0-1 risk axis:
  - a hollow diamond marks the organism's starting score
  - a shaded band marks the range of scores in the SUPPLIER's own free
    answers on the same items
  - a filled circle (colored to match its row's supplier band) marks the
    score after training on a pool that mixed in the supplier's answers
  - an open (hollow) circle marks the score after training on its own
    answers only, for the one matched comparison that exists

Facet 1, "the insecure-code model" (Qwen, admits-insecure-code self-report,
sr_freegen): computed directly from experiments/em_selfaware_loop/output/
mixed_reopen_qwen.json (mixed run, seeds 921/922, dose low_55_707) and
mixed_reopen_twin_selfonly.json (matched self-only twin, same seeds, dose
low_55_707t). Both mixed seeds and both twin seeds are numerically
identical to 3 decimal places, so each row shows one point.

Facet 2, "a second risk model" (OLMo, share of free answers
choosing the gamble over the sure payout): computed directly from
experiments/modal_k2_release/output/k2rel_oracle_mix_s31.json (mixed, rail
~0.93), k2rel_oracle_mix_s32.json (mixed, rail 1.00), and
k2rel_oracle_hold_s21.json (self-only twin of the ~0.93 rail, same oracle
selector, no injection). A second, smaller strip shows a maxed-out
supplier: four fresh organisms (experiments/modal_k2_release/output/
k2rel_invade_base_s35.json, k2rel_invade_base_s36.json,
k2rel_invade_self_s37.json, k2rel_invade_self_s38.json) moved from their
own starting scores to 0.917-1.000 after one round mixed with a supplier
pinned near 1.0.

Model-naming note: the task that requested this figure called facet 1 "the
gambling model." That plain name is already used elsewhere in this figure
set (fig03/fig06) for a different Qwen organism scored on a $-for-sure-vs-
gamble task. Facet 1's data here is the admits-insecure-code self-report
axis, which this figure set calls "the insecure-code model" (fig15/fig16).
Facet 2's data is the OLMo gamble-vs-sure-payout organism under the oracle
selector (fig06-fig14's "cautious/neutral judge model"), not a second,
unrelated risk model. Both facets are renamed here to match the existing
figure set instead of introducing a colliding or inaccurate name.

Regenerate with:  python3 synthesis_supply_leverage_destination.py   (stdlib only)
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = HERE
while ROOT != os.path.dirname(ROOT) and not os.path.isdir(os.path.join(ROOT, "experiments")):
    ROOT = os.path.dirname(ROOT)
FIGDIR = os.path.dirname(HERE) if os.path.basename(HERE) == "src" else HERE
EM_DIR = os.path.join(ROOT, "experiments", "em_selfaware_loop", "output")
K2_DIR = os.path.join(ROOT, "experiments", "modal_k2_release", "output")

INK = "#1a1a1a"
GREEN = "#3a7d44"    # a safer supplier's answers, and the endpoint that lands there
RED = "#b5342c"      # a riskier (maxed-out) supplier's answers, and its endpoint
GRAY = "#6b7684"      # self-only (no supply) marker and neutral ink
BAND_ALPHA = "0.35"

FONT = "Helvetica, Arial, sans-serif"
BODY = 19


# ---------------------------------------------------------------- helpers
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


def ctext(x, y, text, size, color=INK, weight="normal"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="middle" font-family="{FONT}" '
            f'font-size="{size}" font-weight="{weight}" fill="{color}">{esc(text)}</text>')


def ltext(x, y, text, size, color=INK, weight="normal", anchor="start"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" font-family="{FONT}" '
            f'font-size="{size}" font-weight="{weight}" fill="{color}">{esc(text)}</text>')


def cwrap(cx, y, text, size, width_chars, color=INK, weight="normal", lh=1.35):
    lines = wrap(text, width_chars)
    out = [ctext(cx, y + i * size * lh, ln, size, color, weight) for i, ln in enumerate(lines)]
    return "\n".join(out), y + (len(lines) - 1) * size * lh


def box(x, y, w, h, fill, stroke=INK, sw=1.5, rx=14):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')


def svg_doc(w, h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
            f'font-family="{FONT}">\n<rect width="{w}" height="{h}" fill="white"/>\n'
            f'{body}\n</svg>')


def diamond(x, y, s=9):
    """hollow diamond: the organism's starting score."""
    pts = f"{x:.1f},{y-s:.1f} {x+s:.1f},{y:.1f} {x:.1f},{y+s:.1f} {x-s:.1f},{y:.1f}"
    return f'<polygon points="{pts}" fill="white" stroke="{INK}" stroke-width="2.5"/>'


def dot(x, y, color, open_=False, r=9.5):
    """filled circle = trained with supply (colored to match its band);
    open circle = trained on its own answers only."""
    if open_:
        return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="white" stroke="{GRAY}" stroke-width="3.2"/>'
    return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{color}" stroke="white" stroke-width="1.8"/>'


def harrow(x0, x1, y, color=GRAY, sw=2.6):
    if abs(x1 - x0) < 5:
        return ""
    d = 1 if x1 > x0 else -1
    tip, back = x1 - d * 10, x0
    return (f'<line x1="{back:.1f}" y1="{y:.1f}" x2="{x1 - d*11:.1f}" y2="{y:.1f}" '
            f'stroke="{color}" stroke-width="{sw}"/>'
            f'<path d="M {x1 - d*11:.1f} {y-6.5:.1f} L {tip:.1f} {y:.1f} L {x1 - d*11:.1f} {y+6.5:.1f} z" fill="{color}"/>')


def capsule(x0, x1, y, color, h=13):
    """thin rounded range bar for a small cluster of values."""
    x0, x1 = min(x0, x1), max(x0, x1)
    w = max(x1 - x0, h)
    cx0 = (x0 + x1) / 2 - w / 2
    return (f'<rect x="{cx0:.1f}" y="{y-h/2:.1f}" width="{w:.1f}" height="{h}" rx="{h/2}" '
            f'fill="{color}" stroke="white" stroke-width="1.6"/>')


# ---------------------------------------------------------------- data (recomputed from raw JSON)
def load(path):
    with open(path) as f:
        return json.load(f)


# facet 1 — Qwen insecure-code self-report (sr_freegen)
_mix = load(os.path.join(EM_DIR, "mixed_reopen_qwen.json"))
_twin = load(os.path.join(EM_DIR, "mixed_reopen_twin_selfonly.json"))
F1_BASE = _mix["baselines"]["low_55_707"]["sr_freegen_mean"]                 # 0.627
F1_MIX_END = sum(_mix["cells"][f"low_55_707:{s}"]["battery"][-1]["sr_free_gen"]["sr_freegen"]
                  for s in (921, 922)) / 2                                    # ~0.000
F1_SELF = _twin["cells"]["low_55_707t:921"]["battery"][0]["sr_free_gen"]["sr_freegen"]  # flat 0.625
F1_SUPPLIER = (0.06, 0.08)   # base-Qwen cogen sr, report_mixed_reopen_qwen.md

# facet 2 — OLMo gamble-vs-sure-payout free-generation risk (traj)
_s31 = load(os.path.join(K2_DIR, "k2rel_oracle_mix_s31.json"))["31"]["oracle_mix"]["traj"]
_s32 = load(os.path.join(K2_DIR, "k2rel_oracle_mix_s32.json"))["32"]["oracle_mix"]["traj"]
_s21 = load(os.path.join(K2_DIR, "k2rel_oracle_hold_s21.json"))["21"]["oracle_hold"]["traj"]
F2_MIX_A_START, F2_MIX_A_END = _s31[0], _s31[-1]     # 0.927 -> 0.344
F2_MIX_B_START, F2_MIX_B_END = _s32[0], _s32[-1]     # 1.000 -> 0.484
F2_SELF_START, F2_SELF_END = _s21[0], _s21[-1]       # 0.917 -> 0.094
F2_SUPPLIER = (0.5, 0.7)     # base-OLMo scored range on these items, report_mixed_generator_branch_m.md

_inv = {}
for cell, seed in (("invade_base", "35"), ("invade_base", "36"), ("invade_self", "37"), ("invade_self", "38")):
    d = load(os.path.join(K2_DIR, f"k2rel_{cell}_s{seed}.json"))[seed][cell]["traj"]
    _inv[f"{cell}_{seed}"] = d
F2C_START = [v[0] for v in _inv.values()]
F2C_END1 = [v[1] for v in _inv.values()]
F2C_SUPPLIER = (0.97, 1.00)  # railed vintage, fixed score 1.000; thin band for display


# ---------------------------------------------------------------- geometry
W = 1500
GUT_X = 66
AX0, AX1 = 330, 1430
AW = AX1 - AX0
ROW_H = 62


def xv(v):
    return AX0 + AW * v


def ticks(y):
    out = []
    for v in (0.0, 0.25, 0.5, 0.75, 1.0):
        xx = xv(v)
        out.append(f'<line x1="{xx:.1f}" y1="{y-4:.1f}" x2="{xx:.1f}" y2="{y+4:.1f}" stroke="{GRAY}" stroke-width="1.5"/>')
        lbl = "0" if v == 0 else ("1" if v == 1 else f"{v:g}")
        out.append(ctext(xx, y + 26, lbl, 19, GRAY))
    out.append(f'<line x1="{AX0}" y1="{y:.1f}" x2="{AX1}" y2="{y:.1f}" stroke="{GRAY}" stroke-width="1.5"/>')
    return "\n".join(out)


def band(x0, x1, y0, y1, color):
    xx0, xx1 = xv(x0), xv(x1)
    return f'<rect x="{xx0:.1f}" y="{y0:.1f}" width="{max(xx1-xx0, 6):.1f}" height="{y1-y0:.1f}" fill="{color}" fill-opacity="{BAND_ALPHA}"/>'


b = []

# ---- title + one setup line ----
b.append(ctext(W // 2, 52, "Outside answers restore movement — but also set where it can land", 30, INK, "bold"))
sub, _ = cwrap(W // 2, 90,
    "Each point is the share of a model's free-generation answers that were the riskier option (0 = never, 1 = always), before and after training on a pool that mixed in a supplier's answers.",
    BODY, 148, GRAY)
b.append(sub)

# ---- legend (marker shapes only; band color is labeled per facet) ----
leg_y = 152
items = [("diamond", GRAY, "starting score"),
         ("dot", GREEN, "after training with supply mixed in"),
         ("open", GRAY, "after training on its own answers only")]
widths = [22 + len(t) * 10.6 for _, _, t in items]
total = sum(widths) + 54 * (len(items) - 1)
lx = W // 2 - total / 2
for (kind, col, t), wd in zip(items, widths):
    cy = leg_y - 6
    if kind == "diamond":
        b.append(diamond(lx + 11, cy, s=8))
    elif kind == "dot":
        b.append(dot(lx + 11, cy, col, open_=False, r=8.5))
    else:
        b.append(dot(lx + 11, cy, col, open_=True, r=8.5))
    b.append(ltext(lx + 30, leg_y, t, BODY, INK))
    lx += wd + 54

y = leg_y + 46


def edge_label(x, y, text, size, color, weight="bold"):
    """label near a marker; switches anchor near the axis edges so it never runs
    past the panel border."""
    if x > AX1 - 60:
        return ltext(x + 10, y, text, size, color, weight, anchor="end")
    if x < AX0 + 60:
        return ltext(x - 10, y, text, size, color, weight, anchor="start")
    return ctext(x, y, text, size, color, weight)


# =================================================================
# FACET 1 — the insecure-code model
# =================================================================
F1_TOP = y
box_idx = len(b)
b.append("")  # placeholder for the panel box, filled in once its height is known

b.append(ltext(GUT_X, F1_TOP + 20, "the insecure-code model", 24, INK, "bold"))
b.append(ltext(GUT_X, F1_TOP + 44, "riskier option: text admitting to writing insecure code", 19, GRAY, "italic"))

rows_top = F1_TOP + 44 + 52
row1_y = rows_top + 20
row2_y = row1_y + ROW_H
band_y0, band_y1 = row1_y - 34, row2_y + 34

b.append(band(*F1_SUPPLIER, band_y0, band_y1, GREEN))

# row 1: trained with supply mixed in
b.append(ltext(GUT_X, row1_y - 6, "supply mixed in", BODY, INK))
b.append(harrow(xv(F1_BASE), xv(F1_MIX_END), row1_y, GREEN))
b.append(diamond(xv(F1_BASE), row1_y))
b.append(dot(xv(F1_MIX_END), row1_y, GREEN))
b.append(edge_label(xv(F1_BASE), row1_y - 20, f"{F1_BASE:.2f}", 19, INK))
b.append(edge_label(xv(F1_MIX_END), row1_y - 20, f"{F1_MIX_END:.3f}", 19, GREEN))

# row 2: trained on its own answers only (flat: start == end)
b.append(ltext(GUT_X, row2_y - 6, "its own answers only", BODY, INK))
b.append(diamond(xv(F1_SELF), row2_y))
b.append(dot(xv(F1_SELF), row2_y, GREEN, open_=True))
b.append(ctext(xv(F1_SELF), row2_y + 34, f"{F1_SELF:.3f} → {F1_SELF:.3f}", 19, GRAY))

b.append(ctext(xv(sum(F1_SUPPLIER) / 2), band_y0 - 12, f"a safer supplier’s answers ≈ {F1_SUPPLIER[0]:.2f}–{F1_SUPPLIER[1]:.2f}", 19, GREEN, "bold"))

axis1_y = band_y1 + 30
b.append(ticks(axis1_y))

F1_BOTTOM = axis1_y + 30
F1_H = F1_BOTTOM - (F1_TOP - 12)
b[box_idx] = box(GUT_X - 26, F1_TOP - 12, W - 2 * (GUT_X - 26), F1_H, "#fbfcfd", "#d9dee4", 1.5, rx=16)

# =================================================================
# FACET 2 — a second risk model
# =================================================================
F2_TOP = F1_BOTTOM + 40
box_idx2 = len(b)
b.append("")  # placeholder for the panel box

b.append(ltext(GUT_X, F2_TOP + 20, "a second risk model", 24, INK, "bold"))
b.append(ltext(GUT_X, F2_TOP + 44, "riskier option: choosing the gamble over the sure payout", 19, GRAY, "italic"))

rows_top = F2_TOP + 44 + 52
r1y = rows_top + 20
r2y = r1y + ROW_H
r3y = r2y + ROW_H
band2_y0, band2_y1 = r1y - 34, r3y + 34

b.append(band(*F2_SUPPLIER, band2_y0, band2_y1, GREEN))

# row 1: mixed, rail ~0.93
b.append(ltext(GUT_X, r1y - 6, "supply mixed in", BODY, INK))
b.append(harrow(xv(F2_MIX_A_START), xv(F2_MIX_A_END), r1y, GREEN))
b.append(diamond(xv(F2_MIX_A_START), r1y))
b.append(dot(xv(F2_MIX_A_END), r1y, GREEN))
b.append(edge_label(xv(F2_MIX_A_START), r1y - 20, f"{F2_MIX_A_START:.2f}", 19, INK))
b.append(edge_label(xv(F2_MIX_A_END), r1y - 20, f"{F2_MIX_A_END:.3f}", 19, GREEN))

# row 2: self-only, same starting rail as row 1
b.append(ltext(GUT_X, r2y - 6, "its own answers only", BODY, INK))
b.append(harrow(xv(F2_SELF_START), xv(F2_SELF_END), r2y, GRAY))
b.append(diamond(xv(F2_SELF_START), r2y))
b.append(dot(xv(F2_SELF_END), r2y, GREEN, open_=True))
b.append(edge_label(xv(F2_SELF_START), r2y - 20, f"{F2_SELF_START:.2f}", 19, INK))
b.append(edge_label(xv(F2_SELF_END), r2y + 26, f"{F2_SELF_END:.3f}", 19, GRAY))

# row 3: mixed, rail 1.00
b.append(ltext(GUT_X, r3y - 6, "supply mixed in", BODY, INK))
b.append(harrow(xv(F2_MIX_B_START), xv(F2_MIX_B_END), r3y, GREEN))
b.append(diamond(xv(F2_MIX_B_START), r3y))
b.append(dot(xv(F2_MIX_B_END), r3y, GREEN))
b.append(edge_label(xv(F2_MIX_B_START), r3y - 20, f"{F2_MIX_B_START:.2f}", 19, INK))
b.append(edge_label(xv(F2_MIX_B_END), r3y - 20, f"{F2_MIX_B_END:.3f}", 19, GREEN))

b.append(ctext(xv(sum(F2_SUPPLIER) / 2), band2_y0 - 12, f"a safer supplier’s answers ≈ {F2_SUPPLIER[0]:.1f}–{F2_SUPPLIER[1]:.1f}", 19, GREEN, "bold"))

axis2_y = band2_y1 + 30
b.append(ticks(axis2_y))

# ---- facet 2 secondary strip: a maxed-out supplier ----
sec_top = axis2_y + 42
b.append(ltext(GUT_X, sec_top, "a maxed-out supplier, four fresh organisms", 19, INK, "bold"))
sr_y = sec_top + 18 + 34
band3_y0, band3_y1 = sr_y - 30, sr_y + 30
b.append(band(*F2C_SUPPLIER, band3_y0, band3_y1, RED))
c_start0, c_start1 = min(F2C_START), max(F2C_START)
c_end0, c_end1 = min(F2C_END1), max(F2C_END1)
c_start_cx = (xv(c_start0) + xv(c_start1)) / 2
c_end_cx = (xv(c_end0) + xv(c_end1)) / 2
b.append(harrow(c_start_cx, c_end_cx, sr_y, RED))
b.append(capsule(xv(c_start0), xv(c_start1), sr_y, GRAY))
b.append(capsule(xv(c_end0), xv(c_end1), sr_y, RED))
b.append(ctext(c_start_cx, sr_y - 22, f"{c_start0:.2f}–{c_start1:.2f}", 19, INK))
b.append(edge_label(c_end_cx, sr_y - 22, f"{c_end0:.3f}–{c_end1:.3f}", 19, RED))
b.append(edge_label(xv(sum(F2C_SUPPLIER) / 2), band3_y0 - 10, f"a riskier supplier’s answers ≈ {F2C_SUPPLIER[1]:.1f}", 19, RED))

axis3_y = band3_y1 + 26
b.append(ticks(axis3_y))

F2_BOTTOM = axis3_y + 30
F2_H = F2_BOTTOM - (F2_TOP - 12)
b[box_idx2] = box(GUT_X - 26, F2_TOP - 12, W - 2 * (GUT_X - 26), F2_H, "#fbfcfd", "#d9dee4", 1.5, rx=16)

H = F2_BOTTOM + 30
svg = svg_doc(W, H, "\n".join(b))
with open(os.path.join(FIGDIR, "synthesis_supply_leverage_destination.svg"), "w") as f:
    f.write(svg)
print(f"wrote synthesis_supply_leverage_destination.svg  H={H:.0f}")
print(f"F1 base={F1_BASE:.4f} mix_end={F1_MIX_END:.6f} self={F1_SELF:.4f}")
print(f"F2 mixA {F2_MIX_A_START:.4f}->{F2_MIX_A_END:.4f}  mixB {F2_MIX_B_START:.4f}->{F2_MIX_B_END:.4f}  self {F2_SELF_START:.4f}->{F2_SELF_END:.4f}")
print(f"F2 contamination start={[round(v,3) for v in F2C_START]} end1={[round(v,3) for v in F2C_END1]}")
