#!/usr/bin/env python3
"""Synthesis candidate B: four matched-intervention cards in one lens.

Every card is a two-condition comparison: it holds an experiment fixed and
changes ONE selection knob, then shows (1) BOTH selection dials — pool spread
sigma AND selection-value agreement rho — as from -> to readings across the two
compared conditions (the dial the intervention actually moved is drawn in red,
the matched dial that held is drawn in gray), (2) the two measured value
trajectories that followed (one line per condition), and (3) the experiment's
identity in plain words. All dial and trajectory numbers are read live from the
committed result files (records carry per-round value, spread, and rho for every
run). Run from this directory:

    python3 synthesis-intervention-cards.py

Style: reuses the make_figures.py Owain Evans-lab house style (palette,
esc/wrap helpers copied verbatim, white background, headline sentence, fat
labels, direct series labels). Stdlib only.
"""
import json
import math
import os
import random
import statistics
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
<marker id="arrG" viewBox="0 0 10 10" refX="9" refY="5"
 markerWidth="6" markerHeight="6" orient="auto-start-reverse">
 <path d="M 0 0 L 10 5 L 0 10 z" fill="{GRAY}"/></marker>
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


def r1_spread(cond, seed):
    """Round-1 pool spread sigma of one run, rounded to 2dp (records sorted so
    index 0 is round 1)."""
    return round(pool_spread(cond, seed)[0], 2)


def predicted(cond, seed, steps=None):
    """Deterministic model forecast from the run's round-1 measurements: the
    same recurrence as the committed sampler (rollout() in
    docs/figures/auto/rollouts-vs-observed-spaghetti, innovations off).
    sigma, rho, pool composition u, and outside-source mean are frozen at
    round 1; each round kept = clip(pool + rho*sigma), and both the generated
    mean and the value move to the kept mean. A null round-1 rho (a pool with
    no variance to correlate) contributes no selection term.
    """
    rows = RUNS[(cond, str(seed))]
    f = rows[0]
    sigma, rho, comp = f["own_spread"], f["rho"], f["composition"]
    u = float(f.get("pool_cogen_fraction") or 0.0) if comp != "self-only" else 0.0
    s_mean = float(f["cogen_mean"]) if comp != "self-only" else 0.0
    if rho is None:
        rho = 0.0
    q, v = f["own_mean"], f["value"]
    out = [round(v, 3)]
    for _ in range(steps if steps is not None else len(rows)):
        pool = (1.0 - u) * q + u * s_mean
        kept = min(1.0, max(0.0, pool + rho * sigma))
        q = kept
        v = kept
        out.append(round(v, 3))
    return out


# ---- staged-noise 80% band (recipe copied from the committed sampler in
# docs/figures/auto/rollouts-vs-observed-spaghetti: leave-one-condition-out
# residual pools, innovations at the gap / generated-mean / agreement stages,
# battery read noise on the reported value only) ----
def _std(xs):
    return statistics.pstdev(xs) if len(xs) > 1 else 0.0


def _transitions(rows):
    by = {r["round"]: r for r in rows}
    return [(by[t], by[t + 1]) for t in by if t + 1 in by]


def residual_scales(cond, axis):
    d = json.load(open(DATA))
    records = d["records"]
    train = [r for r in records if r["cond"] != cond]
    gap = [r["gap"] - r["rho"] * r["mean_item_sd"]
           for r in train if r["axis"] == axis and r["rho"] is not None]
    q_res, rho_res = [], []
    tg = defaultdict(list)
    for r in train:
        tg[(r["cond"], r["seed"], r["source"])].append(r)
    for rows in tg.values():
        if rows[0]["axis"] != axis:
            continue
        for a, b in _transitions(sorted(rows, key=lambda r: r["round"])):
            q_res.append((b["own_mean"] - a["own_mean"]) - a["self_relative_gap"])
            if a["rho"] is not None and b["rho"] is not None:
                rho_res.append(b["rho"] - a["rho"])
    return _std(gap), _std(q_res), _std(rho_res)


def meas_sd(v, n):
    if not n or n <= 0:
        return 0.0
    v = min(1.0, max(0.0, v))
    return math.sqrt(max(0.0, v * (1.0 - v)) / n)


def quantile(xs, q):
    xs = sorted(xs)
    i = q * (len(xs) - 1)
    lo = int(i)
    hi = min(lo + 1, len(xs) - 1)
    return xs[lo] * (1 - (i - lo)) + xs[hi] * (i - lo)


def forecast_band(cond, seed, steps=None, n_draws=30, rng_seed=777):
    """10-90% band of the staged-noise sampler from the run's round-1 state:
    the same 80% band scored in the writeup (89% of observed final values fall
    inside it corpus-wide)."""
    rows = RUNS[(cond, str(seed))]
    f = rows[0]
    sigma, rho0, comp = f["own_spread"], f["rho"], f["composition"]
    u = float(f.get("pool_cogen_fraction") or 0.0) if comp != "self-only" else 0.0
    s_mean = float(f["cogen_mean"]) if comp != "self-only" else 0.0
    if rho0 is None:
        rho0 = 0.0
    sg, sq, sr = residual_scales(f["cond"], f["axis"])
    nsteps = steps if steps is not None else len(rows)
    rng = random.Random(rng_seed)
    paths = []
    for _ in range(n_draws):
        q, v, rho = f["own_mean"], f["value"], rho0
        out = [v]
        for i in range(nsteps):
            pool = (1.0 - u) * q + u * s_mean
            gap = rho * sigma + rng.gauss(0.0, sg)
            kept = min(1.0, max(0.0, pool + gap))
            q = min(1.0, max(0.0, q + (kept - q) + rng.gauss(0.0, sq)))
            v = min(1.0, max(0.0, v + (kept - v)))
            rho = min(1.0, max(-1.0, rho + rng.gauss(0.0, sr)))
            n_meas = rows[min(i, len(rows) - 1)].get("next_value_measurement_n")
            out.append(min(1.0, max(0.0, v + rng.gauss(0.0, meas_sd(v, n_meas)))))
        paths.append(out)
    lo = [round(quantile([p[i] for p in paths], 0.10), 3)
          for i in range(nsteps + 1)]
    hi = [round(quantile([p[i] for p in paths], 0.90), 3)
          for i in range(nsteps + 1)]
    return lo, hi


# ---- Card 1: inject base answers into a Qwen self-report oracle loop ----
# matched twins: same organism, judge, format, seed; only the pool differs.
C1_SELF = observed("mixed_reopen_twin_selfonly", 921)  # self-only pool holds
C1_INJ = observed("mixed_reopen_qwen", 921)            # base-mixed pool collapses
# BOTH dials, from (self-only) -> to (base-mixed):
C1_SIGMA_FROM = r1_spread("mixed_reopen_twin_selfonly", 921)  # 0.00
C1_SIGMA_TO = r1_spread("mixed_reopen_qwen", 921)             # 0.31
# agreement is the score oracle pinned at -1 in BOTH arms; the flat self-only
# twin logs rho=null (no pool variance to correlate), so its dial reading is the
# oracle's design setting, disclosed in caption.md. The base-mixed twin's mean
# rho is read live and confirms -1.0.
C1_RHO_FROM = -1.0
C1_RHO_TO = cond_mean_rho("mixed_reopen_qwen")               # -1.0
P1_SELF = predicted("mixed_reopen_twin_selfonly", 921)
P1_INJ = predicted("mixed_reopen_qwen", 921)
B1_SELF = forecast_band("mixed_reopen_twin_selfonly", 921)
B1_INJ = forecast_band("mixed_reopen_qwen", 921)

# ---- Card 2: SAME cautious judge + SAME railed starts; scoring FORMAT changes ----
# Ledger row "Judging format is part of the selector": the same cautious judge on
# the same railed OLMo organisms rescues the rail DOWN under head-to-head duels
# (1.000 -> 0.747, 0.865 -> 0.537) but HOLDS the rails under reference-anchored
# scoring. Matched pairs by start (see docs/report_head2head_olmo.md table row
# "h2h_cons_rescue s55/s56 | railed 0.865/1.000 | cons_mix -> 0.716/1.000 HELD"):
#   start ~0.87:  reference cons_mix s33 (holds 0.716)  vs duel s55 (-> 0.537)
#   start  1.00:  reference cons_mix s34 (holds 1.000)  vs duel s56 (-> 0.747)
C2_REF_33 = observed("cons_mix", 33)          # start 0.875 -> holds 0.716
C2_REF_34 = observed("cons_mix", 34)          # start 1.000 -> holds 1.000
C2_DUEL_55 = observed("h2h_cons_rescue", 55)  # start 0.865 -> 0.537
C2_DUEL_56 = observed("h2h_cons_rescue", 56)  # start 1.000 -> 0.747
# moved dial: the format moves selection-value agreement (condition means)
C2_RHO_REF = cond_mean_rho("cons_mix")              # +0.38
C2_RHO_DUEL = cond_mean_rho("h2h_cons_rescue")      # +0.10
# held dial: round-1 pool spread, two-seed mean per arm (holds ~0.32 in both)
C2_SIGMA_REF = round((r1_spread("cons_mix", 33) +
                      r1_spread("cons_mix", 34)) / 2, 2)          # 0.32
C2_SIGMA_DUEL = round((r1_spread("h2h_cons_rescue", 55) +
                       r1_spread("h2h_cons_rescue", 56)) / 2, 2)  # 0.32
P2_REF_33 = predicted("cons_mix", 33)
P2_REF_34 = predicted("cons_mix", 34)
P2_DUEL_55 = predicted("h2h_cons_rescue", 55)
P2_DUEL_56 = predicted("h2h_cons_rescue", 56)

# ---- Card 3: swap the base-model judge for a score oracle pinned at rho=-1 ----
# oracle_hold s21 was initialised from the base_hold s2 railed vintage
# (report_crossfamily_oracle.md), then resumed with the score-oracle selector:
# same OLMo railed organism, same self-only pool; only the judge changes.
C3_BASE = observed("base_hold", 2)                  # base-model judge: rail holds
C3_ORACLE = observed("oracle_hold", 21)             # oracle at -1: reverses
C3_RHO_BASE = cond_mean_rho("base_hold")            # +0.15
C3_RHO_ORACLE = cond_mean_rho("oracle_hold")        # -1.0
C3_SIGMA_BASE = r1_spread("base_hold", 2)           # 0.35  (matched dial)
C3_SIGMA_ORACLE = r1_spread("oracle_hold", 21)      # 0.12
# one step past the logged rounds so the dotted line reaches the swap marker
P3_BASE = predicted("base_hold", 2, steps=9)
B3_BASE = forecast_band("base_hold", 2, steps=9)
P3_ORACLE = predicted("oracle_hold", 21)
B3_ORACLE = forecast_band("oracle_hold", 21)

# ---- assertions: every plotted series must match the source file ----
# Cards 1-3 use the committed endpoint convention (values + final value+drift).
assert C1_SELF == [0.627, 0.625, 0.625, 0.625, 0.625], C1_SELF
assert C1_INJ == [0.627, 0.0, 0.0, 0.0, 0.0], C1_INJ
assert C1_SIGMA_FROM == 0.0 and C1_SIGMA_TO == 0.31, (C1_SIGMA_FROM, C1_SIGMA_TO)
assert C1_RHO_FROM == -1.0 and C1_RHO_TO == -1.0, (C1_RHO_FROM, C1_RHO_TO)
assert C2_REF_33 == [0.875, 0.636, 0.833, 0.583, 0.716], C2_REF_33
assert C2_REF_34 == [1.0, 0.958, 1.0, 1.0, 1.0], C2_REF_34
assert C2_DUEL_55 == [0.865, 0.682, 0.5, 0.542, 0.537], C2_DUEL_55
assert C2_DUEL_56 == [1.0, 0.917, 0.667, 0.833, 0.747], C2_DUEL_56
assert C2_RHO_REF == 0.38 and C2_RHO_DUEL == 0.1, (C2_RHO_REF, C2_RHO_DUEL)
assert C2_SIGMA_REF == 0.32 and C2_SIGMA_DUEL == 0.32, \
    (C2_SIGMA_REF, C2_SIGMA_DUEL)
assert C3_BASE == [0.301, 0.522, 0.375, 0.625, 0.5, 0.708, 0.875, 0.75, 0.875], \
    C3_BASE
assert C3_ORACLE == [0.917, 0.667, 0.458, 0.292, 0.094], C3_ORACLE
assert C3_RHO_BASE == 0.15 and C3_RHO_ORACLE == -1.0, (C3_RHO_BASE, C3_RHO_ORACLE)
assert C3_SIGMA_BASE == 0.35 and C3_SIGMA_ORACLE == 0.12, \
    (C3_SIGMA_BASE, C3_SIGMA_ORACLE)




# ====================================================================
# Drawing helpers
# ====================================================================
def band_poly(x, y, w, h, lo, hi, color, n_axis=None, offset=0):
    """Shaded 10-90% forecast band on a panel's axes."""
    smax = 1.0
    n = n_axis if n_axis is not None else len(lo) + offset
    def px(j):
        return x + (w * (j + offset) / (n - 1) if n > 1 else 0)
    def py(v):
        return y + h - (v / smax) * h
    top = [f"{px(j):.1f},{py(v):.1f}" for j, v in enumerate(hi)]
    bot = [f"{px(j):.1f},{py(v):.1f}" for j, v in reversed(list(enumerate(lo)))]
    return (f'<polygon points="{" ".join(top + bot)}" fill="{color}" '
            f'fill-opacity="0.13"/>')


def pred_line(x, y, w, h, values, color, n_axis=None, offset=0):
    """One dotted model-forecast polyline on a panel's axes (no markers)."""
    smax = 1.0
    n = n_axis if n_axis is not None else len(values) + offset
    pts = []
    for j, v in enumerate(values):
        px = x + (w * (j + offset) / (n - 1) if n > 1 else 0)
        py = y + h - (v / smax) * h
        pts.append(f"{px:.1f},{py:.1f}")
    return (f'<polyline points="{" ".join(pts)}" fill="none" stroke="{color}" '
            f'stroke-width="2" stroke-dasharray="2 4" stroke-linecap="round" '
            f'stroke-opacity="0.85"/>')


def sparkline(x, y, w, h, series, legend_x, legend_y, preds=None):
    """Plot value trajectories; series word-labels go in a legend below.

    series: list of (values, color, word_label). Value axis 1.0 top, 0.0 bottom.
    preds: optional [(values, color)] dotted deterministic-forecast lines,
    drawn under the observed lines.
    """
    smax = 1.0
    s = []
    for pv, pc, blo, bhi in (preds or []):
        s.append(band_poly(x, y, w, h, blo, bhi, pc))
    for pv, pc, blo, bhi in (preds or []):
        s.append(pred_line(x, y, w, h, pv, pc))
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
    if preds:
        s.append(f'<line x1="{legend_x}" y1="{ly-5}" x2="{legend_x+22}" '
                 f'y2="{ly-5}" stroke="{GRAY}" stroke-width="2" '
                 f'stroke-dasharray="2 4" stroke-linecap="round"/>')
        s.append(txt(legend_x + 30, ly,
                     "model forecast from round-1 measurements", 13.5, GRAY))
    return "\n".join(s)


def spliced_line(x, y, w, h, seg_a, seg_b, ca, cb, legend_x, legend_y,
                 label_a, label_b, preds=None):
    """One continuous trajectory drawn in two colours across a judge swap.

    preds: optional [(values, color, offset)] dotted deterministic forecasts
    placed on the same concatenated round axis starting at index offset.

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
    for pv, pc, off, blo, bhi in (preds or []):
        s.append(band_poly(x, y, w, h, blo, bhi, pc, n_axis=n, offset=off))
    for pv, pc, off, blo, bhi in (preds or []):
        s.append(pred_line(x, y, w, h, pv, pc, n_axis=n, offset=off))
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
    if preds:
        s.append(f'<line x1="{legend_x}" y1="{ly-5}" x2="{legend_x+22}" '
                 f'y2="{ly-5}" stroke="{GRAY}" stroke-width="2" '
                 f'stroke-dasharray="2 4" stroke-linecap="round"/>')
        s.append(txt(legend_x + 30, ly,
                     "model forecast from round-1 measurements", 13.5, GRAY))
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


def arm_panel(x, y, w, h, arms, legend_x, legend_y, ytitle=None,
              start_note=None):
    """Two-arm trajectory panel (cards 2, 5, 6). Each arm carries two seeds
    (solid + dashed, never averaged) drawn as full trajectories on a 0-1 value
    axis. Every trajectory includes its own round-0 start point, so arms whose
    starts differ are drawn honestly (no forced shared baseline). Endpoint labels
    per arm show both seeds' final values.

    arms: list of (color, label, [seed_series, ...], end_label). end_label is a
    verbatim string ("0.79 / 0.91") placed at the mean end y of that arm.
    """
    smax = 1.0
    s = []
    n = len(arms[0][2][0])

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
    if ytitle:
        cy = y + h / 2
        s.append(f'<text x="{x-30}" y="{cy}" font-family="{FONT}" '
                 f'font-size="12.5" fill="{GRAY}" text-anchor="middle" '
                 f'transform="rotate(-90 {x-30} {cy:.1f})">{esc(ytitle)}</text>')
    # arms
    for color, _label, seeds, end_label in arms:
        for k, ys in enumerate(seeds):
            pts = " ".join(f"{px(i):.1f},{py(v):.1f}" for i, v in enumerate(ys))
            dash = "" if k == 0 else ' stroke-dasharray="5 4"'
            s.append(f'<polyline points="{pts}" fill="none" stroke="{color}" '
                     f'stroke-width="2.6"{dash} stroke-linejoin="round" '
                     f'stroke-linecap="round"/>')
            # start dot (small, dark) and end dot (arm colour)
            s.append(f'<circle cx="{px(0):.1f}" cy="{py(ys[0]):.1f}" r="3.4" '
                     f'fill="{INK}" stroke="white" stroke-width="1.2"/>')
            ex, ey = px(n - 1), py(ys[-1])
            s.append(f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="4" fill="{color}" '
                     f'stroke="white" stroke-width="1.4"/>')
    # per-arm endpoint labels at the arm's mean end y
    for color, _label, seeds, end_label in arms:
        ey = py(sum(sd[-1] for sd in seeds) / len(seeds))
        s.append(txt(px(n - 1) + 8, ey + 5, end_label, 14, color, weight="bold"))
    # start note (near the shared start region)
    if start_note:
        s.append(txt(x + 4, y - 8, start_note, 13, INK, weight="bold"))
    s.append(txt(x + w / 2, y + h + 26, "rounds →", 14, GRAY, anchor="middle"))
    # two-item key (arm colours; each arm is 2 seeds, solid + dashed)
    ly = legend_y
    for color, label, _seeds, _end in arms:
        s.append(f'<line x1="{legend_x}" y1="{ly-5}" x2="{legend_x+22}" '
                 f'y2="{ly-5}" stroke="{color}" stroke-width="3.6" '
                 f'stroke-linecap="round"/>')
        s.append(f'<circle cx="{legend_x+11}" cy="{ly-5}" r="4.2" fill="{color}" '
                 f'stroke="white" stroke-width="1.4"/>')
        s.append(txt(legend_x + 30, ly, label, 14.5, INK))
        ly += 21
    s.append(txt(legend_x, ly, "solid / dashed = the two seeds", 13, GRAY))
    return "\n".join(s)


SIGMA_MAX = 0.5


def mini_dial(x, w, y_track, name, frm, to, kind, moved):
    """One compact selection dial with a from -> to reading.

    x/w: left edge and width of the horizontal track. y_track: its centre y.
    name: 'spread σ' or 'agreement ρ' (a word key; the measurement recipe for
    each lives in caption.md). kind: 'sigma' (axis 0..0.5) or 'rho' (axis
    −1..+1). moved=True draws the dial in red (the dial the intervention moved);
    moved=False draws it in gray (the matched dial that held), so the
    matched-contrast structure stays legible. The header line (name at left,
    'from -> to' reading at right) sits 23px above the track; axis endpoint
    labels sit 17px below. If from and to coincide (< 0.02 apart) no arrow is
    drawn — a single filled marker shows the pinned value.
    """
    color = RED if moved else GRAY
    marker = "arrR" if moved else "arrG"
    s = []
    x0, x1 = x, x + w
    if kind == "sigma":
        def px(v):
            return x0 + v / SIGMA_MAX * w
        ends = [(x0, "0"), (x1, f"{SIGMA_MAX}")]
        zero_tick = None
        def fmt(v):
            return f"{v:.2f}"
    else:
        def px(v):
            return x0 + (v + 1) / 2 * w
        ends = [(x0, "−1"), (x0 + w / 2, "0"), (x1, "+1")]
        zero_tick = x0 + w / 2
        def fmt(v):
            return f"{v:+.2f}".replace("-", "−")
    # header: name (INK, always readable) + reading (dial colour, colored delta)
    hy = y_track - 23
    s.append(txt(x0, hy, name, 15.5, INK, weight="bold"))
    pinned = abs(to - frm) < 0.02
    reading = fmt(to) if pinned else f"{fmt(frm)} → {fmt(to)}"
    s.append(txt(x1, hy, reading, 15.5, color, weight="bold",
                 anchor="end"))
    # track + optional zero tick
    s.append(f'<line x1="{x0}" y1="{y_track}" x2="{x1}" y2="{y_track}" '
             f'stroke="{GRAY}" stroke-width="3" stroke-linecap="round"/>')
    if zero_tick is not None:
        s.append(f'<line x1="{zero_tick:.1f}" y1="{y_track-6}" '
                 f'x2="{zero_tick:.1f}" y2="{y_track+6}" stroke="{GRAY}" '
                 f'stroke-width="2"/>')
    # axis endpoint labels
    for ex, lbl in ends:
        s.append(txt(ex, y_track + 17, lbl, 12.5, GRAY, anchor="middle"))
    # arrow from -> to (floats just above the track), then the two markers
    if not pinned:
        s.append(f'<line x1="{px(frm):.1f}" y1="{y_track-10}" '
                 f'x2="{px(to):.1f}" y2="{y_track-10}" stroke="{color}" '
                 f'stroke-width="3.2" marker-end="url(#{marker})"/>')
        s.append(f'<circle cx="{px(frm):.1f}" cy="{y_track}" r="6" fill="white" '
                 f'stroke="{INK}" stroke-width="2.4"/>')
    s.append(f'<circle cx="{px(to):.1f}" cy="{y_track}" r="7" fill="{color}" '
             f'stroke="white" stroke-width="1.8"/>')
    return "\n".join(s)


def cat_dial(x, w, y_track, name, frm, to, moved):
    """A CATEGORICAL selection dial (cards 5 & 6): the moved knob is not a σ/ρ
    number but a named setting swapped from one value to another (e.g. the judge
    model 'itself → frozen base', or the candidate pool 'base co-gen → removed').
    Same red=moved / gray=held grammar and same header layout as mini_dial, but
    the track carries two word-nodes instead of a numeric axis; the words live in
    the header reading. If frm == to the knob HELD (gray, single word, no arrow).
    No dial NUMBERS are invented — these files carry no per-round agreement in a
    comparable convention, so the moved knob is stated categorically.
    """
    color = RED if moved else GRAY
    marker = "arrR" if moved else "arrG"
    same = (frm == to)
    s = []
    x0, x1 = x, x + w
    hy = y_track - 23
    s.append(txt(x0, hy, name, 15.5, INK, weight="bold"))
    reading = frm if same else f"{frm} → {to}"
    s.append(txt(x1, hy, reading, 14, color, weight="bold", anchor="end"))
    # track with two nodes
    lx, rx = x0 + w * 0.14, x0 + w * 0.86
    s.append(f'<line x1="{x0}" y1="{y_track}" x2="{x1}" y2="{y_track}" '
             f'stroke="{GRAY}" stroke-width="3" stroke-linecap="round"/>')
    if not same:
        s.append(f'<line x1="{lx:.1f}" y1="{y_track-10}" x2="{rx:.1f}" '
                 f'y2="{y_track-10}" stroke="{color}" stroke-width="3.2" '
                 f'marker-end="url(#{marker})"/>')
        s.append(f'<circle cx="{lx:.1f}" cy="{y_track}" r="6" fill="white" '
                 f'stroke="{INK}" stroke-width="2.4"/>')
        s.append(f'<circle cx="{rx:.1f}" cy="{y_track}" r="7" fill="{color}" '
                 f'stroke="white" stroke-width="1.8"/>')
    else:
        cx = x0 + w / 2
        s.append(f'<circle cx="{cx:.1f}" cy="{y_track}" r="7" fill="{color}" '
                 f'stroke="white" stroke-width="1.8"/>')
    return "\n".join(s)


def pair_panel(x, y, w, h, title, entries):
    """One matched-pair mini panel for card 2: observed solid lines plus dotted
    model forecasts, one panel per seed pair. entries: [(obs, pred, color)].
    Value axis 1.0 top, 0.0 bottom; end labels show observed endpoints.
    """
    smax = 1.0
    s = [txt(x, y - 8, title, 13.5, INK, weight="bold")]
    s.append(f'<line x1="{x}" y1="{y+h}" x2="{x+w}" y2="{y+h}" stroke="{GRAY}" '
             f'stroke-width="1.5"/>')
    s.append(f'<line x1="{x}" y1="{y}" x2="{x}" y2="{y+h}" stroke="{GRAY}" '
             f'stroke-width="1.5"/>')
    s.append(txt(x - 8, y + 6, "1.0", 12, GRAY, anchor="end"))
    s.append(txt(x - 8, y + h + 4, "0", 12, GRAY, anchor="end"))
    n = len(entries[0][0])
    def px(i):
        return x + w * i / (n - 1)
    def py(v):
        return y + h - (v / smax) * h
    for obs, pred, color in entries:
        s.append(pred_line(x, y, w, h, pred, color, n_axis=n))
    ends = []
    for obs, pred, color in entries:
        pts = " ".join(f"{px(i):.1f},{py(v):.1f}" for i, v in enumerate(obs))
        s.append(f'<polyline points="{pts}" fill="none" stroke="{color}" '
                 f'stroke-width="2.8" stroke-linejoin="round" '
                 f'stroke-linecap="round"/>')
        ex, ey = px(n - 1), py(obs[-1])
        s.append(f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="4" fill="{color}" '
                 f'stroke="white" stroke-width="1.4"/>')
        ends.append((ey, obs[-1], color))
    # end labels, nudged apart if the endpoints are close
    ends.sort()
    prev = None
    for ey, val, color in ends:
        ly = ey if prev is None else max(ey, prev + 15)
        s.append(txt(px(n - 1) + 8, ly + 4, f"{val:.3f}".rstrip("0").rstrip("."),
                     13.5, color, weight="bold"))
        prev = ly
    return "\n".join(s)


# ====================================================================
# Card
# ====================================================================
CARD_W = 372
CARD_H = 536
PAD = 22
DIAL_W = CARD_W - 92   # track width for both dials
# fixed vertical bands inside a card (offsets from card top y)
Y_ID = 62          # first identity line
Y_DIVIDER = 118
Y_DIAL_SUBHEAD = 136
Y_DIAL1 = 178      # dial-row 1 (the moved dial) track centre
Y_DIAL2 = 236      # dial-row 2 (the matched, held dial) track centre
Y_TRAJ_HEAD = 280
Y_SPARK = 300      # sparkline box top
SPARK_H = 132
Y_LEGEND = 476     # first legend row baseline


def card(x, y, num, title, identity_lines, dials, spark_svg):
    """dials: [(name, frm, to, kind, moved), ...] with the moved dial FIRST
    (rendered in row 1, red); the matched held dial second (row 2, gray)."""
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
    s.append(txt(x + PAD, y + Y_DIAL_SUBHEAD,
                 "Both selection dials, in the two conditions (from → to)",
                 13, GRAY))
    for spec, yt in zip(dials, (y + Y_DIAL1, y + Y_DIAL2)):
        name, frm, to, kind, moved = spec
        if kind == "cat":
            s.append(cat_dial(x + PAD, DIAL_W, yt, name, frm, to, moved))
        else:
            s.append(mini_dial(x + PAD, DIAL_W, yt, name, frm, to, kind, moved))
    s.append(txt(x + PAD, y + Y_TRAJ_HEAD, "The measured value that followed",
                 15, INK, weight="bold"))
    s.append(spark_svg)
    return "\n".join(s)


def build():
    x0, y0 = 44, 168
    gap = 24
    row_gap = 46
    step = CARD_W + gap
    row_step = CARD_H + row_gap
    ncol = 2
    W = x0 * 2 + ncol * CARD_W + (ncol - 1) * gap
    H = y0 + CARD_H + 28
    spx = x0 + 60           # sparkline left (per card, add card x - x0)
    spw = CARD_W - 150      # narrower so end value fits inside card
    legx = PAD              # legend x offset within card

    # column x and row y of each 1-indexed card in a 3-col x 2-row grid
    def cx(num):
        return x0 + ((num - 1) % ncol) * step

    def cy(num):
        return y0 + ((num - 1) // ncol) * row_step

    b = []
    # headline (orientation only — interpretation lives in caption.md)
    b.append(txt(60, 58,
                 "Two matched interventions — move one selection dial, read the "
                 "value that follows",
                 28, INK, weight="bold"))
    b.append(txt(60, 88,
                 "Each card holds an experiment fixed and changes ONE selection "
                 "knob; the moved dial is drawn red, the held dial gray.",
                 16.5, GRAY))
    b.append(txt(60, 110,
                 "Each card's identity line and the caption give the recipe. "
                 "Dotted line = the model's forecast from that run's round-1 "
                 "measurements; shaded band = its 80% range.",
                 16.5, GRAY))

    # per-card trajectory panels (built at the card's own x,y)
    def spark_of(num, series):
        return sparkline(cx(num) + spx - x0, cy(num) + Y_SPARK, spw, SPARK_H,
                         series, cx(num) + legx, cy(num) + Y_LEGEND)

    # dial specs per card: (name, from, to, kind, moved). Moved dial FIRST.
    # ---- Card 1: inject base answers -> spread moves, agreement pinned ----
    d1 = [("spread σ", C1_SIGMA_FROM, C1_SIGMA_TO, "sigma", True),
          ("agreement ρ", C1_RHO_FROM, C1_RHO_TO, "rho", False)]
    sp1 = sparkline(cx(1) + spx - x0, cy(1) + Y_SPARK, spw, SPARK_H,
                    [(C1_SELF, GREEN, "self-only pool"),
                     (C1_INJ, RED, "base answers mixed in")],
                    cx(1) + legx, cy(1) + Y_LEGEND,
                    preds=[(P1_SELF, GREEN, *B1_SELF),
                           (P1_INJ, RED, *B1_INJ)])
    b.append(card(cx(1), cy(1), 1, "Mix in base answers",
                  ["Qwen self-report organism, score-oracle judge",
                   "the oracle scores and keeps the 2 best of 6;",
                   "two runs, same seed, differ only in the pool"],
                  d1, sp1))

    # ---- Card 3: one organism, base-model judge then oracle swapped in ----
    d3 = [("agreement ρ", C3_RHO_BASE, C3_RHO_ORACLE, "rho", True),
          # sigma is the state at the swap itself (re-measured as the oracle
          # takes over); the earlier 0.35 belongs to the prior run's early
          # rounds, not to this intervention, so the dial shows one pinned value
          ("spread σ", C3_SIGMA_ORACLE, C3_SIGMA_ORACLE, "sigma", False)]
    sp3 = spliced_line(cx(2) + spx - x0, cy(2) + Y_SPARK, spw, SPARK_H,
                       C3_BASE, C3_ORACLE, GREEN, RED,
                       cx(2) + legx, cy(2) + Y_LEGEND,
                       "base-model judge",
                       "score oracle",
                       preds=[(P3_BASE, GREEN, 0, *B3_BASE),
                              (P3_ORACLE, RED, len(C3_BASE), *B3_ORACLE)])
    b.append(card(cx(2), cy(2), 2, "Swap in an oracle judge (ρ = −1)",
                  ["OLMo railed organism, risk axis, self-only pool",
                   "a base-model reference judge had railed it up;",
                   "swapped for a score oracle (ρ = −1)"],
                  d3, sp3))



    return svg_doc(W, H, "\n".join(b))


if __name__ == "__main__":
    out = os.path.join(HERE, "synthesis-intervention-cards.svg")
    with open(out, "w") as f:
        f.write(build())
    print("wrote", out)
    # echo the numbers actually plotted, for the honesty check
    print("C1  σ %.2f->%.2f (moved)  ρ %.2f->%.2f (held)" %
          (C1_SIGMA_FROM, C1_SIGMA_TO, C1_RHO_FROM, C1_RHO_TO))
    print("    self:", C1_SELF, " injected:", C1_INJ)
    print("C3  ρ %.2f->%.2f (moved)  σ %.2f pinned at the swap" %
          (C3_RHO_BASE, C3_RHO_ORACLE, C3_SIGMA_ORACLE))
    print("    base:", C3_BASE, " oracle:", C3_ORACLE)
    print("preds C1 self/inj:", P1_SELF, P1_INJ)
    print("bands C1 inj lo/hi:", B1_INJ[0], B1_INJ[1])
    print("bands C3 oracle lo/hi:", B3_ORACLE[0], B3_ORACLE[1])
    print("preds C3 base/oracle:", P3_BASE, P3_ORACLE)
