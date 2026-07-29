#!/usr/bin/env python3
"""The six self-judging runs drawn as trajectories in the (pool value, agreement) plane.

Style reference: docs/figures/src/make_figures.py -- Owain Evans-lab house style,
white background, a headline sentence stating the finding, in-figure condition
lines rather than a legend box, real numbers with fat labels.  esc()/wrap() are
copied from that file rather than imported so this stays self-contained.

Run from this directory:   python3 coevolving-judge-phase-plane.py
Stdlib only, like make_figures.py.

Data
----
Primary:  experiments/ablation_unit_law.json, key "rho_trajectories", the six
          entries "neutral_self:41" .. "neutral_self:46".
Raw:      experiments/em_selfaware_loop/output/head2head_neutralstyle_selfonly.json
          and .._s43_46.json -- the per-prompt duel logs the primary file was
          built from.  This script re-derives every plotted number from the raw
          logs when they are present and refuses to plot if the two disagree by
          more than 0.001; it falls back to the primary file otherwise.
"""
import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
PRIMARY = os.path.join(ROOT, "experiments", "ablation_unit_law.json")
RAW_DIR = os.path.join(ROOT, "experiments", "em_selfaware_loop", "output")
RAW_FILES = ["head2head_neutralstyle_selfonly.json",
             "head2head_neutralstyle_selfonly_s43_46.json"]
OUT = os.path.join(HERE, "coevolving-judge-phase-plane.svg")

# ---- palette, copied verbatim from make_figures.py ----------------------
INK = "#1a1a1a"
BLUE = "#2867b5"       # accent / self-judge series (validated)
GREEN = "#3a7d44"      # accent / frozen-judge series (validated)
RED = "#b5342c"        # emphasis for reversal / warning text
GRAY = "#6b7684"       # recessive only (axes, muted captions) -- never a series
USER_FILL = "#cfe0f1"  # chat user box
ASST_FILL = "#eaf1f8"  # chat assistant box
DOC_FILL = "#fdf6e8"   # document / essay box
KEY_FILL = "#eef5ee"   # highlighted takeaway box

FONT = "Helvetica, Arial, sans-serif"

# All six runs are the self-judging condition, so BLUE/GREEN cannot carry the
# contrast here (GREEN is reserved for frozen-judge series).  The two series
# colours below encode the OUTCOME polarity and pass the dataviz validator:
#   validate_palette.js "#2867b5,#b5342c" --mode light  ->  all checks pass
#   (CVD separation dE 21.3 protan, normal-vision dE 28.0).
FALLING = RED          # run's pool value ends below where it started
RISING = BLUE          # run's pool value ends above where it started


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


def text(x, y, s, size=18, color=INK, weight="normal", anchor="start",
         style="normal"):
    return (f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" '
            f'fill="{color}" font-weight="{weight}" text-anchor="{anchor}" '
            f'font-style="{style}">{esc(s)}</text>')


def para(x, y, s, size=18, color=INK, width=60, lh=1.32, weight="normal",
         anchor="start"):
    out = []
    for i, ln in enumerate(wrap(s, width)):
        out.append(text(x, y + i * size * lh, ln, size, color, weight, anchor))
    return "\n".join(out), y + len(wrap(s, width)) * size * lh


def box(x, y, w, h, fill, stroke=INK, sw=2.5, rx=8):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')


DEFS = f'''<defs>
<marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6"
 markerHeight="6" orient="auto-start-reverse">
 <path d="M 0 0 L 10 5 L 0 10 z" fill="{INK}"/></marker>
<marker id="arrB" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6"
 markerHeight="6" orient="auto-start-reverse">
 <path d="M 0 0 L 10 5 L 0 10 z" fill="{BLUE}"/></marker>
<marker id="arrR" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6"
 markerHeight="6" orient="auto-start-reverse">
 <path d="M 0 0 L 10 5 L 0 10 z" fill="{RED}"/></marker>
</defs>'''


def svg_doc(w, h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
            f'font-family="{FONT}">\n<rect width="{w}" height="{h}" fill="white"/>\n'
            f'{DEFS}\n{body}\n</svg>')


# ======================================================================
# Data: re-derive from the raw duel logs, then check against the committed
# analysis file.
# ======================================================================
def _pstd(v):
    m = sum(v) / len(v)
    return math.sqrt(sum((x - m) ** 2 for x in v) / len(v))


def _pearson(a, b):
    ma, mb = sum(a) / len(a), sum(b) / len(b)
    num = sum((x - ma) * (y - mb) for x, y in zip(a, b))
    da = math.sqrt(sum((x - ma) ** 2 for x in a))
    db = math.sqrt(sum((y - mb) ** 2 for y in b))
    if da == 0 or db == 0:
        return None
    return num / (da * db)


def derive_from_raw():
    """Conventions copied from scripts/analysis_ablation_unit_law.py:
    per-prompt Pearson(judge score, candidate self-report value score); a prompt
    is skipped if it has fewer than 3 candidates or zero variation in either
    vector; agreement / spread / pool mean are averaged over the qualifying
    prompts; population standard deviation."""
    runs = {}
    for fn in RAW_FILES:
        path = os.path.join(RAW_DIR, fn)
        if not os.path.isfile(path):
            return None
        d = json.load(open(path))
        for cell, c in d["cells"].items():
            seed = int(cell.split(":")[1])
            recs = []
            for ridx, items in enumerate(c["rounds_raw"], start=1):
                gaps, sigmas, rhos, pms = [], [], [], []
                n_items = 0
                for it in items:
                    cs = it.get("cand_sr_scores")
                    kidx = it.get("kept_idx")
                    if not cs or not kidx:
                        continue
                    n_items += 1
                    mean = sum(cs) / len(cs)
                    pms.append(mean)
                    gaps.append(sum(cs[i] for i in kidx) / len(kidx) - mean)
                    sigmas.append(_pstd(cs))
                    s = it.get("scores")
                    if (len(cs) >= 3 and _pstd(cs) > 1e-9
                            and isinstance(s, list) and len(s) == len(cs)
                            and _pstd(s) > 1e-9):
                        r = _pearson(s, cs)
                        if r is not None:
                            rhos.append(r)
                if not pms:
                    continue
                recs.append({
                    "round": ridx,
                    "gap": sum(gaps) / len(gaps),
                    "sigma": sum(sigmas) / len(sigmas),
                    "rho": (sum(rhos) / len(rhos)) if rhos else None,
                    "n_rho_prompts": len(rhos),
                    "n_prompts": n_items,
                    "pool_mean": sum(pms) / len(pms),
                })
            runs[seed] = recs
    return runs


def load():
    primary = json.load(open(PRIMARY))["rho_trajectories"]
    raw = derive_from_raw()
    out = {}
    for seed in range(41, 47):
        p = primary[f"neutral_self:{seed}"]
        if raw is None:
            out[seed] = {"rho": p["rho"], "sigma": p["sigma"], "gap": p["gap"],
                         "pool_mean": p["pool_mean"],
                         "n_rho_prompts": [None] * len(p["rho"]),
                         "n_prompts": [None] * len(p["rho"]),
                         "source": "committed analysis file only"}
            continue
        recs = raw[seed]
        got = {k: [rec[k] for rec in recs]
               for k in ("rho", "sigma", "gap", "pool_mean",
                         "n_rho_prompts", "n_prompts")}
        for key in ("rho", "sigma", "gap", "pool_mean"):
            for a, b in zip(got[key], p[key]):
                if (a is None) != (b is None):
                    raise SystemExit(
                        f"seed {seed} {key}: raw logs and {PRIMARY} disagree "
                        f"about whether the value exists ({a} vs {b})")
                if a is not None and abs(a - b) > 1e-3:
                    raise SystemExit(
                        f"seed {seed} {key}: raw logs give {a}, "
                        f"{PRIMARY} gives {b}")
        out[seed] = dict(got, source="re-derived from raw duel logs")
    return out


RUNS = load()
SEEDS = sorted(RUNS)

# Derived readouts, all named with their recipe in the caption.
NET = {s: RUNS[s]["pool_mean"][-1] - RUNS[s]["pool_mean"][0] for s in SEEDS}
CUM_GAP = {s: sum(RUNS[s]["gap"][:3]) for s in SEEDS}
COLOR = {s: (FALLING if NET[s] < 0 else RISING) for s in SEEDS}
HEAVY = {s: abs(NET[s]) > 0.10 for s in SEEDS}
DEGENERATE_SPREAD = 0.10   # below this the selection term is effectively zero

N_FALL = sum(1 for s in SEEDS if NET[s] < 0)
N_RISE = len(SEEDS) - N_FALL


# ======================================================================
# Geometry
# ======================================================================
W, H = 1420, 1400
PX0, PX1 = 165, 1230          # plot area, x
PY0, PY1 = 200, 800           # plot area, y
VMIN, VMAX = 0.25, 0.80       # pool value
RMIN, RMAX = -0.90, 0.78      # agreement


def X(v):
    return PX0 + (v - VMIN) / (VMAX - VMIN) * (PX1 - PX0)


def Y(r):
    return PY1 - (r - RMIN) / (RMAX - RMIN) * (PY1 - PY0)


R_SOLID = 7.0
R_HOLLOW = 6.5


def marker(cx, cy, color, degenerate, first=False):
    """One measured round.  Solid = the pool still varied enough for the
    agreement number to mean something; hollow dashed = spread below 0.10."""
    s = []
    if first:
        s.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{R_SOLID + 5:.1f}" '
                 f'fill="none" stroke="{color}" stroke-width="1.8" opacity="0.75"/>')
    if degenerate:
        s.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{R_HOLLOW}" fill="white" '
                 f'stroke="{color}" stroke-width="2.6" stroke-dasharray="3.6 2.8"/>')
    else:
        s.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{R_SOLID + 2:.1f}" '
                 f'fill="white" stroke="none"/>')
        s.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{R_SOLID}" fill="{color}" '
                 f'stroke="white" stroke-width="2"/>')
    return "\n".join(s)


def mid_arrow(x1, y1, x2, y2, color):
    """A short arrow at the midpoint of a segment, so round order reads
    without a legend."""
    dx, dy = x2 - x1, y2 - y1
    L = math.hypot(dx, dy)
    if L < 26:
        return ""
    ux, uy = dx / L, dy / L
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    m = {RED: "arrR", BLUE: "arrB"}.get(color, "arr")
    return (f'<line x1="{mx - ux * 9:.1f}" y1="{my - uy * 9:.1f}" '
            f'x2="{mx + ux * 9:.1f}" y2="{my + uy * 9:.1f}" stroke="{color}" '
            f'stroke-width="3.2" marker-end="url(#{m})"/>')


b = []

# ---------------------------------------------------------------- headline
b.append(text(58, 58, "Every self-judging run stops moving within four rounds — and it stops",
              33, INK, "bold"))
b.append(text(58, 100, "because the candidate pool ran out of spread, not because agreement reached zero.",
              33, INK, "bold"))
sub, _ = para(58, 140,
              "Six runs of the neutral-prompt, self-judging loop, drawn as trajectories in the "
              "(pool value, judge/value agreement) plane. Lande's 1981 model of a co-evolving "
              "preference has a line of resting states rather than a point; the analogue here is "
              "the set where agreement times spread is zero, which has two branches — agreement = 0 "
              "(drawn below) and spread = 0 (reached by every run).",
              19, GRAY, width=126)

b.append(sub)

# ---------------------------------------------------------------- axes
b.append(f'<rect x="{PX0}" y="{PY0}" width="{PX1-PX0}" height="{PY1-PY0}" '
         f'fill="none" stroke="{GRAY}" stroke-width="1.2" opacity="0.55"/>')

for tv in [0.30, 0.40, 0.50, 0.60, 0.70, 0.80]:
    x = X(tv)
    b.append(f'<line x1="{x:.1f}" y1="{PY0}" x2="{x:.1f}" y2="{PY1}" '
             f'stroke="{GRAY}" stroke-width="1" opacity="0.20"/>')
    b.append(f'<line x1="{x:.1f}" y1="{PY1}" x2="{x:.1f}" y2="{PY1+7}" '
             f'stroke="{GRAY}" stroke-width="1.4"/>')
    b.append(text(x, PY1 + 30, f"{tv:.2f}", 18, GRAY, anchor="middle"))

for tr in [-0.8, -0.6, -0.4, -0.2, 0.0, 0.2, 0.4, 0.6]:
    y = Y(tr)
    if abs(tr) > 1e-9:
        b.append(f'<line x1="{PX0}" y1="{y:.1f}" x2="{PX1}" y2="{y:.1f}" '
                 f'stroke="{GRAY}" stroke-width="1" opacity="0.20"/>')
    lab = ("0" if abs(tr) < 1e-9
           else ("−" + f"{abs(tr):.1f}" if tr < 0 else "+" + f"{tr:.1f}"))
    b.append(text(PX0 - 12, y + 6, lab, 18, GRAY, anchor="end"))

b.append(f'<text x="72" y="{(PY0+PY1)/2}" font-family="{FONT}" font-size="20" '
         f'fill="{INK}" font-weight="bold" text-anchor="middle" '
         f'transform="rotate(-90 72 {(PY0+PY1)/2})">judge / value agreement</text>')
b.append(f'<text x="98" y="{(PY0+PY1)/2}" font-family="{FONT}" font-size="17" '
         f'fill="{GRAY}" text-anchor="middle" '
         f'transform="rotate(-90 98 {(PY0+PY1)/2})">'
         f'correlation within a prompt, −1 to +1</text>')

b.append(text((PX0 + PX1) / 2, PY1 + 60,
              "pool value — mean self-report value score of the candidate answers "
              "(0 to 1), averaged over the six prompts",
              19, INK, "bold", anchor="middle"))

# ------------------------------------------------- the agreement = 0 branch
y0 = Y(0.0)
b.append(f'<line x1="{PX0}" y1="{y0:.1f}" x2="{PX1}" y2="{y0:.1f}" '
         f'stroke="{INK}" stroke-width="3.4"/>')
b.append(text(PX1 - 6, y0 - 12, "agreement = 0", 20, INK, "bold", anchor="end"))
eq, _ = para(182, 392,
             "agreement = 0. Here the selection term — agreement times spread — "
             "is zero, so the pool value stops moving. This is one of the two "
             "branches of the resting set: the analogue of Lande's line of "
             "equilibria, a line rather than a point.",
             18, INK, width=52)
b.append(eq)

# ---------------------------------------------------------------- colour key
b.append(f'<line x1="352" y1="216" x2="392" y2="216" stroke="{FALLING}" stroke-width="4.5"/>')
b.append(text(400, 222,
              f"red = the run's pool value ends below where it started ({N_FALL} of 6)",
              18, INK))
b.append(f'<line x1="352" y1="248" x2="392" y2="248" stroke="{RISING}" stroke-width="4.5"/>')
b.append(text(400, 254,
              f"blue = it ends above ({N_RISE} of 6). Arrows run round 1 → 2 → 3; "
              f"the ringed marker is round 1.",
              18, INK))

# ---------------------------------------------------------------- trajectories
# Draw rising runs first so the two big falls sit on top.
order = sorted(SEEDS, key=lambda s: (NET[s] >= 0, -abs(NET[s])), reverse=True)
for seed in order:
    r = RUNS[seed]
    col = COLOR[seed]
    lw = 4.2 if HEAVY[seed] else 2.6
    pts = [(i, r["pool_mean"][i], r["rho"][i], r["sigma"][i])
           for i in range(len(r["rho"])) if r["rho"][i] is not None]
    for k in range(len(pts) - 1):
        _, v1, a1, s1 = pts[k]
        _, v2, a2, s2 = pts[k + 1]
        dash = ' stroke-dasharray="8 6"' if (s1 < DEGENERATE_SPREAD
                                             or s2 < DEGENERATE_SPREAD) else ""
        b.append(f'<line x1="{X(v1):.1f}" y1="{Y(a1):.1f}" x2="{X(v2):.1f}" '
                 f'y2="{Y(a2):.1f}" stroke="{col}" stroke-width="{lw}"{dash} '
                 f'stroke-linecap="round"/>')
    for k in range(len(pts) - 1):
        _, v1, a1, _ = pts[k]
        _, v2, a2, _ = pts[k + 1]
        b.append(mid_arrow(X(v1), Y(a1), X(v2), Y(a2), col))
    for k, (i, v, a, sg) in enumerate(pts):
        b.append(marker(X(v), Y(a), col, sg < DEGENERATE_SPREAD, first=(k == 0)))

# ---------------------------------------------------------------- run labels
def run_label(x, y, seed, extra=None, anchor="start"):
    o = [text(x, y, f"seed {seed}", 19, COLOR[seed], "bold", anchor=anchor)]
    verb = "falls" if NET[seed] < 0 else "rises"
    o.append(text(x, y + 22, f"value {verb} {abs(NET[seed]):.3f}", 18, INK,
                  anchor=anchor))
    if extra:
        o.append(text(x, y + 44, extra, 18, INK, anchor=anchor))
    return "\n".join(o)


def leader(x1, y1, x2, y2):
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{GRAY}" stroke-width="1.4"/>')


b.append(run_label(185, 306, 45))
b.append(leader(258, 292, X(0.296), Y(0.600) + 12))

b.append(run_label(432, 292, 41))
b.append(leader(428, 296, X(0.375) + 11, Y(0.500)))

b.append(run_label(812, 332, 44, anchor="end"))
b.append(leader(818, 336, X(0.599) - 11, Y(0.359) + 2))

b.append(run_label(952, 268, 42))
b.append(leader(948, 272, X(0.644) + 10, Y(0.541) + 4))

b.append(run_label(1000, 646, 43,
                   extra="but its spread here is only 0.118", anchor="end"))
b.append(leader(1006, 660, X(0.729) - 12, Y(-0.676) - 22))

b.append(run_label(858, 502, 46, anchor="end"))
b.append(leader(864, 498, X(0.616) - 10, Y(0.070) - 4))

# The two annotations the counterexample argument needs, placed on the points.
b.append(text(506, 652, "spread still 0.338 here", 18, INK, anchor="end"))
b.append(leader(512, 646, X(0.439) - 11, Y(-0.464) - 2))

b.append(text(1102, 748, "seed 42's round-3 agreement of −0.825 comes",
              18, GRAY, anchor="end"))
b.append(text(1102, 770, "from the one prompt (of six) that still had",
              18, GRAY, anchor="end"))
b.append(text(1102, 792, "two candidates scoring differently",
              18, GRAY, anchor="end"))
b.append(leader(1108, 776, X(0.746) - 10, Y(-0.825)))

# ---------------------------------------------------------------- marker key
b.append(marker(203, 496, GRAY, False))
kt, _ = para(226, 490,
             "solid: the pool still varied (spread 0.10 or more), so the "
             "agreement number is a real measurement",
             18, INK, width=42)
b.append(kt)
b.append(marker(203, 566, GRAY, True))
kt2, _ = para(226, 560,
              "hollow, dashed: spread below 0.10. An agreement estimated on a "
              "pool with almost no variation is not a measurement, and the "
              "segment into it is dashed for the same reason.",
              18, GRAY, width=42)
b.append(kt2)

# ---------------------------------------------------------------- spread = 0 rug
RUG_Y = 942
b.append(text(178, 872,
              "spread = 0 — the other branch of the resting set. "
              "By round 4 every run's candidate pool has no variation left at all,", 18, INK))
b.append(text(178, 894,
              "so there is no correlation to compute and the run has no agreement "
              "coordinate. No line is drawn into this strip, because the", 18, INK))
b.append(text(178, 916,
              "path leaves the plane. Final pool value only, on the same value axis "
              "as the plot above.", 18, INK))
b.append(f'<rect x="{PX0}" y="{RUG_Y-26}" width="{PX1-PX0}" height="52" rx="6" '
         f'fill="#f4f4f2" stroke="{GRAY}" stroke-width="1.2" opacity="0.9"/>')
b.append(f'<line x1="{PX0}" y1="{RUG_Y}" x2="{PX1}" y2="{RUG_Y}" '
         f'stroke="{GRAY}" stroke-width="1.6" stroke-dasharray="5 4"/>')

placed = []
for seed in sorted(SEEDS, key=lambda s: RUNS[s]["pool_mean"][-1]):
    v = RUNS[seed]["pool_mean"][-1]
    x = X(v)
    row = 0
    while any(abs(x - px) < 118 and row == pr for px, pr in placed):
        row += 1
    placed.append((x, row))
    col = COLOR[seed]
    b.append(f'<rect x="{x-6:.1f}" y="{RUG_Y-6}" width="12" height="12" '
             f'fill="white" stroke="{col}" stroke-width="2.8"/>')
    ly = 992 + row * 46
    b.append(leader(x, RUG_Y + 8, x, ly - 34))
    b.append(text(x, ly - 14, f"seed {seed}", 18, col, "bold", anchor="middle"))
    b.append(text(x, ly + 8, f"{v:.3f}", 18, INK, anchor="middle"))

# ======================================================================
# Bottom row: the spread collapse, the counterexamples, the limits
# ======================================================================
BROW = 1090

# ---- (a) candidate spread by round -----------------------------------
b.append(text(60, BROW,
              "Candidate spread by round — how the runs reach the "
              "spread = 0 branch", 20, INK, "bold"))
sp, _ = para(60, BROW + 26,
             "Within-prompt standard deviation of the candidates' value "
             "scores, averaged over the six prompts.",
             18, GRAY, width=52)
b.append(sp)

SX0, SX1 = 118, 470
SY0, SY1 = BROW + 88, BROW + 236
SMAX = 0.45


def SX(rd):
    return SX0 + (rd - 1) / 3 * (SX1 - SX0)


def SY(sg):
    return SY1 - sg / SMAX * (SY1 - SY0)


b.append(f'<rect x="{SX0-24}" y="{SY(DEGENERATE_SPREAD):.1f}" '
         f'width="{SX1-SX0+58}" height="{SY1-SY(DEGENERATE_SPREAD):.1f}" '
         f'fill="{GRAY}" opacity="0.13"/>')
b.append(f'<line x1="{SX0-24}" y1="{SY1}" x2="{SX1+34}" y2="{SY1}" '
         f'stroke="{GRAY}" stroke-width="1.4"/>')
for sg in [0.0, 0.1, 0.2, 0.3, 0.4]:
    b.append(text(SX0 - 32, SY(sg) + 6, f"{sg:.1f}", 18, GRAY, anchor="end"))
    if sg > 0:
        b.append(f'<line x1="{SX0-24}" y1="{SY(sg):.1f}" x2="{SX1+34}" '
                 f'y2="{SY(sg):.1f}" stroke="{GRAY}" stroke-width="1" opacity="0.25"/>')
for rd in (1, 2, 3, 4):
    b.append(text(SX(rd), SY1 + 28, str(rd), 18, GRAY, anchor="middle"))
b.append(text((SX0 + SX1) / 2, SY1 + 54, "round", 18, INK, anchor="middle"))

for seed in order:
    sg = RUNS[seed]["sigma"]
    pts = " ".join(f"{SX(i+1):.1f},{SY(v):.1f}" for i, v in enumerate(sg))
    b.append(f'<polyline points="{pts}" fill="none" stroke="{COLOR[seed]}" '
             f'stroke-width="{3.4 if HEAVY[seed] else 2.2}" opacity="0.92" '
             f'stroke-linecap="round"/>')
    for i, v in enumerate(sg):
        b.append(f'<circle cx="{SX(i+1):.1f}" cy="{SY(v):.1f}" r="4" '
                 f'fill="{COLOR[seed]}" stroke="white" stroke-width="1.4"/>')

b.append(text(SX0 - 20, SY(0.05) + 6,
              "spread below 0.10", 18, GRAY))
b.append(text(SX1 + 44, SY(0.0) + 6, "all six", 18, INK, "bold"))
b.append(text(SX1 + 44, SY(0.0) + 28, "at exactly 0", 18, INK, "bold"))
b.append(text(60, SY1 + 92,
              "Seeds 43 and 44 reach zero spread a round earlier, at round 3.",
              18, INK))

# ---- (b) the counterexamples -----------------------------------------
CX, CW = 620, 400
b.append(box(CX, BROW - 34, CW, 322, DOC_FILL, RED, 2.5))
b.append(text(CX + 22, BROW + 2, "The pattern is not clean — look here",
              20, RED, "bold"))
t1, ny = para(CX + 22, BROW + 34,
              "Seed 43 sits further below the agreement = 0 line at round 2 "
              "than either falling run (− 0.676, against −0.464 for seed 45 and "
              "−0.558 for seed 41) and its value still rises 0.035. The push is "
              "agreement times spread, and seed 43's spread at round 2 is 0.118 "
              "against seed 45's 0.338.",
              18, INK, width=41)
b.append(t1)
t2, ny = para(CX + 22, ny + 16,
              "Seed 44 keeps positive agreement in both measured rounds "
              "(+0.125, +0.359) and its value still ends 0.056 lower. Depth "
              "below the line does not sort the outcomes on its own.",
              18, INK, width=41)
b.append(t2)

# ---- (c) what is and is not claimed ----------------------------------
DX, DW = 1050, 340
b.append(box(DX, BROW - 34, DW, 322, KEY_FILL, GREEN, 2.5))
b.append(text(DX + 22, BROW + 2, "What separates them", 20, GREEN, "bold"))
lines = []
for seed in sorted(SEEDS, key=lambda s: CUM_GAP[s]):
    sign = "−" if CUM_GAP[seed] < 0 else "+"
    lines.append((seed, f"{sign}{abs(CUM_GAP[seed]):.3f}"))
yy = BROW + 34
b.append(text(DX + 22, yy, "run", 18, GRAY))
b.append(text(DX + DW - 22, yy, "selection differential", 18, GRAY, anchor="end"))
yy += 26
for seed, s in lines:
    b.append(text(DX + 22, yy, f"seed {seed}", 18, COLOR[seed], "bold"))
    b.append(text(DX + DW - 22, yy, s, 18, INK, anchor="end"))
    yy += 26
t3, _ = para(DX + 22, yy + 12,
             "Sum over rounds 1 to 3 of the measured kept-minus-pool value gap. "
             "Seeds 41 and 45 are the only two that are negative, and they are "
             "the two that lose the most value. No boundary, separatrix or "
             "nullcline is drawn on the plot: none has been measured, and six "
             "runs could not support one.",
             18, INK, width=37)
b.append(t3)

# ---------------------------------------------------------------- footer
FY = 1330
src = RUNS[41]["source"]
f1, fy2 = para(60, FY,
               "Data: experiments/ablation_unit_law.json, key rho_trajectories, the six entries "
               "neutral_self:41 through neutral_self:46 — the neutral-prompt, self-judging condition "
               "of the judge ablation, in which the organism scores its own candidates so the judge "
               f"co-evolves with them. Every number here is {src}, "
               "experiments/em_selfaware_loop/output/head2head_neutralstyle_selfonly.json and "
               "..._s43_46.json, and checked against the committed analysis file.",
               17, GRAY, width=168)
b.append(f1)
f2, _ = para(60, fy2 + 8,
             "Agreement is the Pearson correlation, within one prompt, between the judge's score for a "
             "candidate and that candidate's self-report value score, averaged over the prompts that had "
             "at least three candidates and non-zero variation in both scores. Spread is the within-prompt "
             "population standard deviation of those value scores, averaged over all six prompts. Pool value "
             "is the mean value score over all candidates and prompts. Framing follows "
             "docs/reports/lit_coevolving_judge_2026-07-28.md.",
             17, GRAY, width=168)
b.append(f2)

with open(OUT, "w") as fh:
    fh.write(svg_doc(W, H, "\n".join(b)))
print("wrote", OUT)
for s in SEEDS:
    r = RUNS[s]
    print(f"  seed {s}: net value {NET[s]:+.3f}  cumulative gap {CUM_GAP[s]:+.4f}  "
          f"spread {['%.3f' % x for x in r['sigma']]}  "
          f"prompts behind agreement {r['n_rho_prompts']}")
