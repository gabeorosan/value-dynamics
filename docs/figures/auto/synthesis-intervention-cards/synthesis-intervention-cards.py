#!/usr/bin/env python3
"""Synthesis candidate B: three matched-intervention cards in one lens.

Every card is a two-condition comparison: it holds an experiment fixed and
changes ONE selection knob, then shows (1) which dial that move touched, (2)
the two measured value trajectories that followed (one line per condition),
and (3) the experiment's identity in plain words. All numbers are read live
from experiments/spread_util_unified.json (records carry per-round value,
spread, and rho for every run). Run from this directory:

    python3 synthesis-intervention-cards.py

Style: reuses the make_figures.py Owain Evans-lab house style (palette,
esc/wrap helpers copied verbatim, white background, headline sentence, fat
labels, direct series labels). Stdlib only.
"""
import json
import os
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "..", "..", "..",
                    "experiments", "spread_util_unified.json")

# ---- palette copied verbatim from make_figures.py ----
INK = "#1a1a1a"
BLUE = "#2867b5"       # self-judge series
GREEN = "#3a7d44"      # frozen / holding series
RED = "#b5342c"        # reversal / erosion emphasis
GRAY = "#6b7684"       # recessive only (axes, muted text)
USER_FILL = "#cfe0f1"
ASST_FILL = "#eaf1f8"
DOC_FILL = "#fdf6e8"
KEY_FILL = "#eef5ee"
CARD_FILL = "#f7f9fb"

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


def box(x, y, w, h, fill, stroke=INK, sw=2.5, rx=8):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')


DEFS = f'''<defs>
<marker id="arr" viewBox="0 0 10 10" refX="9" refY="5"
 markerWidth="6" markerHeight="6" orient="auto-start-reverse">
 <path d="M 0 0 L 10 5 L 0 10 z" fill="{INK}"/></marker>
<marker id="arrR" viewBox="0 0 10 10" refX="9" refY="5"
 markerWidth="6.5" markerHeight="6.5" orient="auto-start-reverse">
 <path d="M 0 0 L 10 5 L 0 10 z" fill="{RED}"/></marker>
<marker id="arrK" viewBox="0 0 10 10" refX="9" refY="5"
 markerWidth="6.5" markerHeight="6.5" orient="auto-start-reverse">
 <path d="M 0 0 L 10 5 L 0 10 z" fill="{INK}"/></marker>
</defs>'''


def svg_doc(w, h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
            f'font-family="{FONT}">\n<rect width="{w}" height="{h}" fill="white"/>\n'
            f'{DEFS}\n{body}\n</svg>')


def txt(x, y, s, size, color=INK, weight="normal", anchor="start"):
    return (f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" '
            f'fill="{color}" font-weight="{weight}" text-anchor="{anchor}">'
            f'{esc(s)}</text>')


# ====================================================================
# Load run trajectories from the committed data file
# ====================================================================
def load_runs():
    d = json.load(open(DATA))
    runs = defaultdict(list)
    for r in d["records"]:
        runs[(r["cond"], str(r["seed"]))].append(r)
    for k in runs:
        runs[k].sort(key=lambda r: r["round"])
    return runs


RUNS = load_runs()


def vals(cond, seed):
    return [round(r["value"], 3) for r in RUNS[(cond, str(seed))]]


def observed(cond, seed):
    """Committed endpoint convention: per-round values, then a final point =
    last round's value + drift (value_after_true). Matches observed() in
    docs/figures/auto/spread-rollout-bakeoff/spread-rollout-bakeoff.py and
    truth_path in scripts/analysis_unit_rollout_properties.py, so the two
    figures report the same endpoints (0.094, 0.875, 0.625, 0.000, ...).
    """
    rows = RUNS[(cond, str(seed))]
    return [round(rows[0]["value"], 3)] + \
           [round(r["value"] + r["drift"], 3) for r in rows]


def pool_spread(cond, seed):
    return [round(r["spread"], 3) for r in RUNS[(cond, str(seed))]]


def mean_rho(cond, seed):
    rs = [r["rho"] for r in RUNS[(cond, str(seed))] if r.get("rho") is not None]
    return round(sum(rs) / len(rs), 2) if rs else None


# cond-level mean rho (matches the +0.38 / +0.10 the cards show)
def cond_mean_rho(cond):
    rs = []
    for (c, s), recs in RUNS.items():
        if c != cond:
            continue
        rs += [r["rho"] for r in recs if r.get("rho") is not None]
    return round(sum(rs) / len(rs), 2) if rs else None


# ---- Card 1: inject base answers into a Qwen self-report oracle loop ----
# matched twins: same organism, judge, format, seed; only the pool differs.
C1_SELF = observed("mixed_reopen_twin_selfonly", 921)  # self-only pool holds
C1_INJ = observed("mixed_reopen_qwen", 921)            # base-mixed pool collapses
C1_SIGMA_TO = round(pool_spread("mixed_reopen_qwen", 921)[0], 2)  # 0.31

# ---- Card 2: change how the OLMo copy-judge is asked ----
# same organism + base-mixed pool; scoring rule changes (reference vs duel).
C2_REF = observed("cons_mix", 34)                   # fixed-reference judge holds
C2_DUEL = observed("h2h_cons_rescue", 55)           # duel judge comes down
C2_RHO_REF = cond_mean_rho("cons_mix")              # +0.38
C2_RHO_DUEL = cond_mean_rho("h2h_cons_rescue")      # +0.10

# ---- Card 3: swap the base-model judge for a score oracle pinned at rho=-1 ----
# oracle_hold s21 was initialised from the base_hold s2 railed vintage
# (report_crossfamily_oracle.md), then resumed with the score-oracle selector:
# same OLMo railed organism, same self-only pool; only the judge changes.
C3_BASE = observed("base_hold", 2)                  # base-model judge: rail holds
C3_ORACLE = observed("oracle_hold", 21)             # oracle at -1: reverses
C3_RHO_BASE = cond_mean_rho("base_hold")            # +0.15
C3_RHO_ORACLE = cond_mean_rho("oracle_hold")        # -1.0

# ---- assertions: every plotted series must match the source file ----
# Cards 1-3 use the committed endpoint convention (values + final value+drift).
assert C1_SELF == [0.627, 0.625, 0.625, 0.625, 0.625], C1_SELF
assert C1_INJ == [0.627, 0.0, 0.0, 0.0, 0.0], C1_INJ
assert C1_SIGMA_TO == 0.31, C1_SIGMA_TO
assert C2_REF == [1.0, 0.958, 1.0, 1.0, 1.0], C2_REF
assert C2_DUEL == [0.865, 0.682, 0.5, 0.542, 0.537], C2_DUEL
assert C2_RHO_REF == 0.38 and C2_RHO_DUEL == 0.1, (C2_RHO_REF, C2_RHO_DUEL)
assert C3_BASE == [0.301, 0.522, 0.375, 0.625, 0.5, 0.708, 0.875, 0.75, 0.875], \
    C3_BASE
assert C3_ORACLE == [0.917, 0.667, 0.458, 0.292, 0.094], C3_ORACLE
assert C3_RHO_BASE == 0.15 and C3_RHO_ORACLE == -1.0, (C3_RHO_BASE, C3_RHO_ORACLE)

# ---- Card 4: remove the supplier (Qwen insecure-code self-judge duels) ----
# Different instrument: forced-choice p(insecure self-description), 0-1, from a
# second file. Same organism/judge/format/seeds; only the answer pool differs.
FC_DATA = os.path.join(HERE, "..", "..", "..", "..",
                       "experiments", "qwen_selfonly_model_check.json")
_FC = json.load(open(FC_DATA))["forced_choice_p_insecure"]
C4_BASELINE = _FC["baseline"]
_sr = _FC["supplier_removed"]        # own answers only -> amplifies
_sp = _FC["supplier_present_twin"]   # half from base model -> collapses
C4_OWN_41 = [C4_BASELINE] + _sr["em750:41"]
C4_OWN_42 = [C4_BASELINE] + _sr["em750:42"]
C4_MIX_41 = [C4_BASELINE] + _sp["em750:41"]
C4_MIX_42 = [C4_BASELINE] + _sp["em750:42"]
_RHO = json.load(open(FC_DATA))["round1_agreement"]
C4_RHO_OWN = _RHO["supplier_removed_mean"]     # +0.3971
C4_RHO_MIX = _RHO["supplier_present_mean"]     # -0.2847

assert abs(C4_BASELINE - 0.3405) < 1e-9, C4_BASELINE
assert _sr["em750:41"] == [0.5399, 0.719, 0.7484, 0.7934], _sr["em750:41"]
assert _sr["em750:42"] == [0.5736, 0.7803, 0.7256, 0.9128], _sr["em750:42"]
assert _sp["em750:41"] == [0.1038, 0.0091, 0.0079, 0.0061], _sp["em750:41"]
assert _sp["em750:42"] == [0.0638, 0.0191, 0.0127, 0.0071], _sp["em750:42"]
assert abs(C4_RHO_OWN - 0.3971) < 1e-9, C4_RHO_OWN
assert abs(C4_RHO_MIX - (-0.2847)) < 1e-9, C4_RHO_MIX


# ====================================================================
# Drawing helpers
# ====================================================================
def sparkline(x, y, w, h, series, legend_x, legend_y):
    """Plot value trajectories; series word-labels go in a legend below.

    series: list of (values, color, word_label). Value axis 1.0 top, 0.0 bottom.
    """
    smax = 1.0
    s = []
    # frame: baseline + left axis, recessive
    s.append(f'<line x1="{x}" y1="{y+h}" x2="{x+w}" y2="{y+h}" stroke="{GRAY}" '
             f'stroke-width="1.5"/>')
    s.append(f'<line x1="{x}" y1="{y}" x2="{x}" y2="{y+h}" stroke="{GRAY}" '
             f'stroke-width="1.5"/>')
    s.append(txt(x - 8, y + 6, "1.0", 13, GRAY, anchor="end"))
    s.append(txt(x - 8, y + h + 4, "0", 13, GRAY, anchor="end"))
    for (v, color, _label) in series:
        n = len(v)
        pts = []
        for j, val in enumerate(v):
            px = x + (w * j / (n - 1) if n > 1 else 0)
            py = y + h - (val / smax) * h
            pts.append((px, py))
        path = " ".join(f"{px:.1f},{py:.1f}" for px, py in pts)
        s.append(f'<polyline points="{path}" fill="none" stroke="{color}" '
                 f'stroke-width="3.4" stroke-linejoin="round" stroke-linecap="round"/>')
        for (px, py) in (pts[0], pts[-1]):
            s.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="4.6" fill="{color}" '
                     f'stroke="white" stroke-width="1.6"/>')
        # start value: normally above-right of the first point, but if the
        # line rises out of the start (label would sit on the climbing segment)
        # tuck it into the left gutter instead so nothing overlaps.
        sx, sy = pts[0]
        startlbl = "0" if v[0] == 0 else f"{v[0]:.3f}".rstrip("0").rstrip(".")
        if len(v) > 1 and abs(v[0] - v[-1]) < 0.01:
            pass  # essentially flat: the end label already shows this value
        elif len(v) > 1 and v[1] > v[0] + 0.03:
            s.append(txt(sx - 6, sy + 5, startlbl, 15, color, weight="bold",
                         anchor="end"))
        else:
            s.append(txt(sx + 2, sy - 11, startlbl, 15, color, weight="bold"))
        # end value (compact, right of last point — fits inside card)
        ex, ey = pts[-1]
        endval = "0.000" if v[-1] == 0 else f"{v[-1]:.3f}".rstrip("0").rstrip(".")
        s.append(txt(ex + 8, ey + 5, endval, 16, color, weight="bold"))
    s.append(txt(x + w / 2, y + h + 26, "rounds →", 14, GRAY, anchor="middle"))
    # legend (color swatch + word) below, left-aligned to card
    ly = legend_y
    for (v, color, label) in series:
        s.append(f'<line x1="{legend_x}" y1="{ly-5}" x2="{legend_x+22}" '
                 f'y2="{ly-5}" stroke="{color}" stroke-width="3.6" '
                 f'stroke-linecap="round"/>')
        s.append(f'<circle cx="{legend_x+11}" cy="{ly-5}" r="4.2" fill="{color}" '
                 f'stroke="white" stroke-width="1.4"/>')
        s.append(txt(legend_x + 30, ly, label, 14.5, INK))
        ly += 21
    return "\n".join(s)


def spliced_line(x, y, w, h, seg_a, seg_b, ca, cb, legend_x, legend_y,
                 label_a, label_b):
    """One continuous trajectory drawn in two colours across a judge swap.

    seg_a (colour ca) is the prior run; seg_b (colour cb) resumes after the
    judge is swapped. Points are concatenated on one round axis. seg_b's
    first point re-measures the swap-time state (a measurement reflects the
    organism, not the judge), so the dashed swap marker sits ON that point,
    the point keeps the prior colour, and cb takes over from it onward.
    Value axis 1.0 top, 0.0 bottom. No interpolated points are invented.
    """
    smax = 1.0
    s = []
    allv = seg_a + seg_b
    n = len(allv)
    def pt(i):
        px = x + w * i / (n - 1)
        py = y + h - (allv[i] / smax) * h
        return px, py
    # frame
    s.append(f'<line x1="{x}" y1="{y+h}" x2="{x+w}" y2="{y+h}" stroke="{GRAY}" '
             f'stroke-width="1.5"/>')
    s.append(f'<line x1="{x}" y1="{y}" x2="{x}" y2="{y+h}" stroke="{GRAY}" '
             f'stroke-width="1.5"/>')
    s.append(txt(x - 8, y + 6, "1.0", 13, GRAY, anchor="end"))
    s.append(txt(x - 8, y + h + 4, "0", 13, GRAY, anchor="end"))
    ka = len(seg_a)
    # the swap marker sits ON the first point of the resumed run: that point
    # re-measures the swap-time state (a measurement reflects the organism,
    # not the judge), and everything after it is the new judge's selection
    sw_px = pt(ka)[0]
    s.append(f'<line x1="{sw_px:.1f}" y1="{y-6}" x2="{sw_px:.1f}" y2="{y+h}" '
             f'stroke="{INK}" stroke-width="1.6" stroke-dasharray="4 3"/>')
    # prior-state polyline through the re-measured swap point (0..ka), then
    # the new judge's polyline (ka..n-1)
    pa = " ".join(f"{pt(i)[0]:.1f},{pt(i)[1]:.1f}" for i in range(ka + 1))
    pb = " ".join(f"{pt(i)[0]:.1f},{pt(i)[1]:.1f}" for i in range(ka, n))
    s.append(f'<polyline points="{pa}" fill="none" stroke="{ca}" '
             f'stroke-width="3.4" stroke-linejoin="round" stroke-linecap="round"/>')
    s.append(f'<polyline points="{pb}" fill="none" stroke="{cb}" '
             f'stroke-width="3.4" stroke-linejoin="round" stroke-linecap="round"/>')
    # small vertices
    for i in range(n):
        px, py = pt(i)
        col = ca if i < ka else cb
        s.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="3" fill="{col}"/>')
    # emphasised markers: start, the dot the swap line sits on, end
    for i, col in ((0, ca), (ka, cb), (n - 1, cb)):
        px, py = pt(i)
        s.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="4.6" fill="{col}" '
                 f'stroke="white" stroke-width="1.6"/>')
    # value labels
    sx, sy = pt(0)
    s.append(txt(sx - 6, sy + 5,
                 f"{seg_a[0]:.3f}".rstrip("0").rstrip("."), 15, ca,
                 weight="bold", anchor="end"))
    ox, oy = pt(ka)
    s.append(txt(ox + 16, oy + 20,
                 f"{seg_b[0]:.3f}".rstrip("0").rstrip("."), 15, cb,
                 weight="bold"))
    ex, ey = pt(n - 1)
    s.append(txt(ex + 8, ey + 5,
                 f"{seg_b[-1]:.3f}".rstrip("0").rstrip("."), 16, cb,
                 weight="bold"))
    s.append(txt(x + w / 2, y + h + 26, "rounds →", 14, GRAY, anchor="middle"))
    # two-colour key (one line, two eras)
    ly = legend_y
    for col, label in ((ca, label_a), (cb, label_b)):
        s.append(f'<line x1="{legend_x}" y1="{ly-5}" x2="{legend_x+22}" '
                 f'y2="{ly-5}" stroke="{col}" stroke-width="3.6" '
                 f'stroke-linecap="round"/>')
        s.append(f'<circle cx="{legend_x+11}" cy="{ly-5}" r="4.2" fill="{col}" '
                 f'stroke="white" stroke-width="1.4"/>')
        s.append(txt(legend_x + 30, ly, label, 14.5, INK))
        ly += 21
    return "\n".join(s)


def fc_panel(x, y, w, h, baseline, arms, legend_x, legend_y):
    """Card-4 trajectory panel: forced-choice p(insecure), a DIFFERENT
    instrument from the other cards' share-kept measure.

    arms: list of (color, label, [seed_series, ...]) where each seed_series is
    a full trajectory (round 0 = shared baseline). Two seeds per arm are drawn
    (seed 1 solid, seed 2 dashed) — never averaged. Value axis 1.0 top, 0 bottom.
    """
    smax = 1.0
    s = []
    n = len(arms[0][2][0])  # points per trajectory (5: baseline + 4 rounds)
    def px(i):
        return x + w * i / (n - 1)
    def py(v):
        return y + h - (v / smax) * h
    # frame
    s.append(f'<line x1="{x}" y1="{y+h}" x2="{x+w}" y2="{y+h}" stroke="{GRAY}" '
             f'stroke-width="1.5"/>')
    s.append(f'<line x1="{x}" y1="{y}" x2="{x}" y2="{y+h}" stroke="{GRAY}" '
             f'stroke-width="1.5"/>')
    s.append(txt(x - 8, y + 6, "1.0", 13, GRAY, anchor="end"))
    s.append(txt(x - 8, y + h + 4, "0", 13, GRAY, anchor="end"))
    # rotated y-title flags the different instrument
    cy = y + h / 2
    s.append(f'<text x="{x-30}" y="{cy}" font-family="{FONT}" font-size="12.5" '
             f'fill="{GRAY}" text-anchor="middle" '
             f'transform="rotate(-90 {x-30} {cy:.1f})">p(insecure)</text>')
    # arms
    for color, _label, seeds in arms:
        for k, ys in enumerate(seeds):
            pts = " ".join(f"{px(i):.1f},{py(v):.1f}" for i, v in enumerate(ys))
            dash = "" if k == 0 else ' stroke-dasharray="5 4"'
            s.append(f'<polyline points="{pts}" fill="none" stroke="{color}" '
                     f'stroke-width="2.4"{dash} stroke-linejoin="round" '
                     f'stroke-linecap="round"/>')
            ex, ey = px(n - 1), py(ys[-1])
            s.append(f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="4" fill="{color}" '
                     f'stroke="white" stroke-width="1.4"/>')
    # shared baseline dot + label
    bx, by = px(0), py(baseline)
    s.append(f'<circle cx="{bx:.1f}" cy="{by:.1f}" r="4.6" fill="{INK}" '
             f'stroke="white" stroke-width="1.6"/>')
    s.append(f'<rect x="{bx + 4:.1f}" y="{by - 21:.1f}" width="92" height="15" '
             f'fill="white" fill-opacity="0.95"/>')
    s.append(txt(bx + 6, by - 9, f"baseline {baseline:.3f}", 13, INK,
                 weight="bold"))
    # end-range labels (own arm high, mixed arm low)
    own_c, _, own_seeds = arms[0]
    mix_c, _, mix_seeds = arms[1]
    oy = py((own_seeds[0][-1] + own_seeds[1][-1]) / 2)
    s.append(txt(px(n - 1) + 8, oy + 5,
                 f"{own_seeds[0][-1]:.2f} / {own_seeds[1][-1]:.2f}", 14, own_c,
                 weight="bold"))
    my = py(max(mix_seeds[0][-1], mix_seeds[1][-1]))
    s.append(txt(px(n - 1) + 8, my + 5,
                 f"{mix_seeds[0][-1]:.3f} / {mix_seeds[1][-1]:.3f}", 13.5, mix_c,
                 weight="bold"))
    s.append(txt(x + w / 2, y + h + 26, "rounds →", 14, GRAY, anchor="middle"))
    # two-item key (arm colours; each arm is 2 seeds, solid + dashed)
    ly = legend_y
    for color, label, _ in arms:
        s.append(f'<line x1="{legend_x}" y1="{ly-5}" x2="{legend_x+22}" '
                 f'y2="{ly-5}" stroke="{color}" stroke-width="3.6" '
                 f'stroke-linecap="round"/>')
        s.append(f'<circle cx="{legend_x+11}" cy="{ly-5}" r="4.2" fill="{color}" '
                 f'stroke="white" stroke-width="1.4"/>')
        s.append(txt(legend_x + 30, ly, label, 14.5, INK))
        ly += 21
    return "\n".join(s)


def _edge(xp, left, right, pad=4):
    """Pick a text anchor + x so a label never spills past the track ends."""
    if xp - left < 40:
        return "start", left - pad
    if right - xp < 40:
        return "end", right + pad
    return "middle", xp


def rho_track(cx, cy, w, frm, to, moved_color=RED, label_to="", note=""):
    """Horizontal correlation dial from -1..+1 with a moving marker.

    frm/to in [-1, 1]. Draws neutral tick at 0 and an arrow frm -> to.
    """
    s = []
    x0, x1 = cx, cx + w
    def px(v):
        return x0 + (v + 1) / 2 * w
    s.append(f'<line x1="{x0}" y1="{cy}" x2="{x1}" y2="{cy}" stroke="{GRAY}" '
             f'stroke-width="3" stroke-linecap="round"/>')
    # end labels
    s.append(txt(x0, cy + 24, "−1", 13, GRAY, anchor="middle"))
    s.append(txt(px(0), cy + 24, "0", 13, GRAY, anchor="middle"))
    s.append(txt(x1, cy + 24, "+1", 13, GRAY, anchor="middle"))
    # zero tick
    s.append(f'<line x1="{px(0):.1f}" y1="{cy-7}" x2="{px(0):.1f}" y2="{cy+7}" '
             f'stroke="{GRAY}" stroke-width="2"/>')
    if frm is not None:
        # hollow marker at 'from' + its label (kept lower so it can't collide)
        s.append(f'<circle cx="{px(frm):.1f}" cy="{cy}" r="6" fill="white" '
                 f'stroke="{INK}" stroke-width="2.4"/>')
        a, lx = _edge(px(frm), x0, x1)
        s.append(txt(lx, cy - 21, f"from {frm:+.2f}".replace("-", "−"), 14, INK,
                     weight="bold", anchor=a))
        # arrow from -> to
        s.append(f'<line x1="{px(frm):.1f}" y1="{cy-14}" x2="{px(to):.1f}" '
                 f'y2="{cy-14}" stroke="{moved_color}" stroke-width="3.2" '
                 f'marker-end="url(#arrR)"/>')
    # filled marker at 'to' (label raised so from/to never overlap)
    s.append(f'<circle cx="{px(to):.1f}" cy="{cy}" r="7" fill="{moved_color}" '
             f'stroke="white" stroke-width="1.8"/>')
    lift = -40 if frm is not None else -22
    a, lx = _edge(px(to), x0, x1)
    s.append(txt(lx, cy + lift, label_to, 16, moved_color, weight="bold",
                 anchor=a))
    if note:
        s.append(txt(cx, cy + 44, note, 14, GRAY))
    return "\n".join(s)


def sigma_track(cx, cy, w, frm, to, smax=0.5, note=""):
    """Horizontal spread dial 0..smax with an arrow frm -> to."""
    s = []
    x0, x1 = cx, cx + w
    def px(v):
        return x0 + v / smax * w
    s.append(f'<line x1="{x0}" y1="{cy}" x2="{x1}" y2="{cy}" stroke="{GRAY}" '
             f'stroke-width="3" stroke-linecap="round"/>')
    s.append(txt(x0, cy + 24, "0", 13, GRAY, anchor="middle"))
    s.append(txt(x1, cy + 24, f"{smax}", 13, GRAY, anchor="middle"))
    s.append(f'<circle cx="{px(frm):.1f}" cy="{cy}" r="6" fill="white" '
             f'stroke="{INK}" stroke-width="2.4"/>')
    s.append(f'<line x1="{px(frm):.1f}" y1="{cy-16}" x2="{px(to):.1f}" '
             f'y2="{cy-16}" stroke="{RED}" stroke-width="3.2" '
             f'marker-end="url(#arrR)"/>')
    s.append(f'<circle cx="{px(to):.1f}" cy="{cy}" r="7" fill="{RED}" '
             f'stroke="white" stroke-width="1.8"/>')
    a, lx = _edge(px(to), x0, x1)
    s.append(txt(lx, cy - 24, f"to {to:.2f}", 16, RED, weight="bold", anchor=a))
    a, lx = _edge(px(frm), x0, x1)
    s.append(txt(lx, cy - 24, f"from {frm:.2f}", 15, INK, weight="bold",
                 anchor=a))
    if note:
        s.append(txt(cx, cy + 44, note, 14, GRAY))
    return "\n".join(s)


# ====================================================================
# Card
# ====================================================================
CARD_W = 372
CARD_H = 486
PAD = 22
# fixed vertical bands inside a card (offsets from card top y)
Y_ID = 66          # first identity line
Y_DIVIDER = 128
Y_DIAL_HEAD = 154
Y_DIAL_NAME = 174
Y_DIAL_CTR = 236   # dial track center
Y_TRAJ_HEAD = 300
Y_SPARK = 322      # sparkline box top
SPARK_H = 84
Y_LEGEND = 452     # first legend row baseline


def card(x, y, num, title, identity_lines, dial_svg, dial_name, spark_svg):
    s = [box(x, y, CARD_W, CARD_H, CARD_FILL, INK, 2.5, rx=14)]
    s.append(f'<circle cx="{x+PAD+13}" cy="{y+30}" r="17" fill="{INK}"/>')
    s.append(txt(x + PAD + 13, y + 36, str(num), 20, "white", weight="bold",
                 anchor="middle"))
    s.append(txt(x + PAD + 40, y + 37, title, 18.5, INK, weight="bold"))
    iy = y + Y_ID
    for ln in identity_lines:
        s.append(txt(x + PAD, iy, ln, 14.5, GRAY))
        iy += 20
    s.append(f'<line x1="{x+PAD}" y1="{y+Y_DIVIDER}" x2="{x+CARD_W-PAD}" '
             f'y2="{y+Y_DIVIDER}" stroke="#d8dee6" stroke-width="1.5"/>')
    s.append(txt(x + PAD, y + Y_DIAL_HEAD, "The dial this intervention moved",
                 15, INK, weight="bold"))
    s.append(txt(x + PAD, y + Y_DIAL_NAME, dial_name, 14.5, GRAY))
    s.append(dial_svg)
    s.append(txt(x + PAD, y + Y_TRAJ_HEAD, "The measured value that followed",
                 15, INK, weight="bold"))
    s.append(spark_svg)
    return "\n".join(s)


def build():
    x0, y0 = 44, 130
    gap = 24
    step = CARD_W + gap
    n_cards = 4
    W = x0 * 2 + n_cards * CARD_W + (n_cards - 1) * gap
    H = 648
    dial_w = CARD_W - 92
    spx = x0 + 60           # sparkline left (per card, add card x)
    spw = CARD_W - 150      # narrower so end value fits inside card
    legx = PAD              # legend x offset within card

    b = []
    # headline (orientation only — interpretation lives in caption.md)
    b.append(txt(60, 62,
                 "Four matched interventions: move one selection dial, "
                 "read the value that follows",
                 30, INK, weight="bold"))
    b.append(txt(60, 96,
                 "Each card holds an experiment fixed and moves one dial. Value = "
                 "share kept insecure/risky (0–1), except card 4 which uses "
                 "forced-choice p(insecure). See caption for sources.",
                 17, GRAY))

    def spark_of(cardx, series):
        return sparkline(cardx + spx - x0, y0 + Y_SPARK, spw, SPARK_H, series,
                         cardx + legx, y0 + Y_LEGEND)

    # ---- Card 1: inject base answers into the kept pool (sigma dial) ----
    d1 = sigma_track(x0 + PAD, y0 + Y_DIAL_CTR, dial_w, 0.00, C1_SIGMA_TO,
                     smax=0.5, note="agreement pinned at −1.0 (oracle)")
    sp1 = spark_of(x0, [(C1_SELF, GREEN, "self-only twin holds"),
                        (C1_INJ, RED, "injected twin collapses")])
    b.append(card(x0, y0, 1, "Inject base answers",
                  ["Qwen self-report organism · score oracle judge",
                   "score format · base-mixed vs self-only twin",
                   "matched twins, seed 921"],
                  d1, "spread σ (disagreement in the kept pool)", sp1))

    # ---- Card 2: change the alternative source, same judge (rho dial) ----
    x1 = x0 + step
    d2 = rho_track(x1 + PAD, y0 + Y_DIAL_CTR, dial_w, C2_RHO_REF, C2_RHO_DUEL,
                   moved_color=RED, label_to=f"to {C2_RHO_DUEL:+.2f}", note="")
    sp2 = spark_of(x1, [(C2_REF, GREEN, "scored vs a reference — holds"),
                        (C2_DUEL, RED, "picked a duel winner — comes down")])
    b.append(card(x1, y0, 2, "Change the alternative source",
                  ["OLMo organism · same cautious copy judge",
                   "scored vs a fixed reference (cons_mix s34)",
                   "vs a duel winner (h2h_cons_rescue s55)"],
                  d2, "agreement ρ (does selection track the value?)", sp2))

    # ---- Card 3: one organism, base-model judge then oracle swapped in ----
    x2 = x0 + 2 * step
    d3 = rho_track(x2 + PAD, y0 + Y_DIAL_CTR, dial_w, C3_RHO_BASE, C3_RHO_ORACLE,
                   moved_color=RED,
                   label_to=f"to {C3_RHO_ORACLE:+.2f}".replace("-", "−"), note="")
    sp3 = spliced_line(x2 + spx - x0, y0 + Y_SPARK, spw, SPARK_H,
                       C3_BASE, C3_ORACLE, GREEN, RED,
                       x2 + legx, y0 + Y_LEGEND,
                       "base-model judge rails it up (base_hold s2)",
                       "score oracle at −1 reverses it (oracle_hold s21)")
    b.append(card(x2, y0, 3, "Swap in an oracle judge (−1)",
                  ["OLMo railed organism · risk axis · self-only pool",
                   "prior run: a base-model judge railed it up",
                   "then swapped it for a score oracle (ρ = −1)"],
                  d3, "agreement ρ (does selection track the value?)", sp3))

    # ---- Card 4: remove the supplier (different instrument) ----
    x3 = x0 + 3 * step
    d4 = rho_track(x3 + PAD, y0 + Y_DIAL_CTR, dial_w, C4_RHO_MIX, C4_RHO_OWN,
                   moved_color=RED,
                   label_to=f"to {C4_RHO_OWN:+.2f}", note="")
    fc_w = spw - 20
    sp4 = fc_panel(x3 + spx - x0, y0 + Y_SPARK, fc_w, SPARK_H, C4_BASELINE,
                   [(RED, "own answers only (41, 42)",
                     [C4_OWN_41, C4_OWN_42]),
                    (BLUE, "half from base model (41, 42)",
                     [C4_MIX_41, C4_MIX_42])],
                   x3 + legx, y0 + Y_LEGEND)
    b.append(card(x3, y0, 4, "Remove the outside source",
                  ["Qwen em750 insecure-code · self-judge",
                   "duels · base-mixed vs own-answers-only",
                   "instrument: forced-choice p(insecure)"],
                  d4, "agreement ρ (does selection track the value?)", sp4))

    return svg_doc(W, H, "\n".join(b))


if __name__ == "__main__":
    out = os.path.join(HERE, "synthesis-intervention-cards.svg")
    with open(out, "w") as f:
        f.write(build())
    print("wrote", out)
    # echo the numbers actually plotted, for the honesty check
    print("C1 self-only:", C1_SELF)
    print("C1 injected :", C1_INJ, " sigma0 ->", C1_SIGMA_TO)
    print("C2 ref rho:", C2_RHO_REF, "vals", C2_REF)
    print("C2 duel rho:", C2_RHO_DUEL, "vals", C2_DUEL)
    print("C3 base  rho:", C3_RHO_BASE, "vals", C3_BASE)
    print("C3 oracle rho:", C3_RHO_ORACLE, "vals", C3_ORACLE)
    print("C4 own  rho:", round(C4_RHO_OWN, 2), "ends",
          C4_OWN_41[-1], C4_OWN_42[-1])
    print("C4 mix  rho:", round(C4_RHO_MIX, 2), "ends",
          C4_MIX_41[-1], C4_MIX_42[-1])
