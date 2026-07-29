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
          logs and stops if the two disagree by more than 0.001; it falls back to
          the primary file only if the raw logs are missing.
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

# All six runs are the self-judging condition, so BLUE cannot carry the contrast
# here and GREEN is reserved for frozen-judge series.  The two series colours
# below encode the OUTCOME polarity, and pass the dataviz validator:
#   validate_palette.js "#2867b5,#b5342c" --mode light  ->  all checks pass
#   (CVD separation dE 21.3 protan; normal-vision dE 28.0).
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
         halo=False):
    """halo=True paints a white outline behind the glyphs so an in-plot label
    stays readable where it crosses a trajectory, without hiding the line."""
    extra = (' stroke="white" stroke-width="4.5" paint-order="stroke"'
             if halo else "")
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{FONT}" font-size="{size}" '
            f'fill="{color}" font-weight="{weight}" text-anchor="{anchor}"{extra}>'
            f'{esc(s)}</text>')


def para(x, y, s, size=18, color=INK, width=60, lh=1.32, weight="normal",
         anchor="start", halo=False):
    lines = wrap(s, width)
    out = [text(x, y + i * size * lh, ln, size, color, weight, anchor, halo)
           for i, ln in enumerate(lines)]
    return "\n".join(out), y + len(lines) * size * lh


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
# Data: re-derive from the raw duel logs, then check the committed file
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
    """Conventions copied from scripts/analysis_ablation_unit_law.py: per-prompt
    Pearson(judge score, candidate self-report value score); a prompt is skipped
    if it has fewer than 3 candidates or zero variation in either vector;
    agreement / spread / gap / pool mean are averaged over the qualifying
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
                         "source": "read from the committed analysis file"}
            continue
        recs = raw[seed]
        got = {k: [rec[k] for rec in recs]
               for k in ("rho", "sigma", "gap", "pool_mean",
                         "n_rho_prompts", "n_prompts")}
        for key in ("rho", "sigma", "gap", "pool_mean"):
            for a, bb in zip(got[key], p[key]):
                if (a is None) != (bb is None):
                    raise SystemExit(
                        f"seed {seed} {key}: the raw logs and {PRIMARY} disagree "
                        f"about whether the value exists ({a} vs {bb})")
                if a is not None and abs(a - bb) > 1e-3:
                    raise SystemExit(
                        f"seed {seed} {key}: raw logs give {a}, "
                        f"{PRIMARY} gives {bb}")
        out[seed] = dict(got, source="re-derived from the raw duel logs")
    return out


RUNS = load()
SEEDS = sorted(RUNS)

NET = {s: RUNS[s]["pool_mean"][-1] - RUNS[s]["pool_mean"][0] for s in SEEDS}
CUM_GAP = {s: sum(RUNS[s]["gap"][:3]) for s in SEEDS}
COLOR = {s: (FALLING if NET[s] < 0 else RISING) for s in SEEDS}
HEAVY = {s: abs(NET[s]) > 0.10 for s in SEEDS}
DEGENERATE_SPREAD = 0.10   # below this the selection term is effectively zero

N_FALL = sum(1 for s in SEEDS if NET[s] < 0)
N_RISE = len(SEEDS) - N_FALL
LAST_ROUND = max(len(RUNS[s]["rho"]) for s in SEEDS)
EARLY_ZERO = [s for s in SEEDS if RUNS[s]["sigma"][LAST_ROUND - 2] == 0]


def sgn(v, nd=3):
    return ("−" if v < 0 else "+") + f"{abs(v):.{nd}f}"


# ======================================================================
# Geometry
# ======================================================================
W, H = 1420, 1850
PX0, PX1 = 165, 1000          # plot area, x
PY0, PY1 = 240, 860           # plot area, y
VMIN, VMAX = 0.25, 0.80       # pool value
RMIN, RMAX = -0.90, 0.78      # agreement
RC = 1030                     # right column, x
RCR = 1390                    # right column, right edge


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
                 f'fill="none" stroke="{color}" stroke-width="1.8" opacity="0.8"/>')
    if degenerate:
        s.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{R_HOLLOW + 2:.1f}" '
                 f'fill="white" stroke="none"/>')
        s.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{R_HOLLOW}" fill="white" '
                 f'stroke="{color}" stroke-width="2.6" stroke-dasharray="3.6 2.8"/>')
    else:
        s.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{R_SOLID + 2:.1f}" '
                 f'fill="white" stroke="none"/>')
        s.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{R_SOLID}" fill="{color}" '
                 f'stroke="white" stroke-width="2"/>')
    return "\n".join(s)


def mid_arrow(x1, y1, x2, y2, color):
    """A short arrow at the midpoint of a segment, so round order reads without
    a legend lookup."""
    dx, dy = x2 - x1, y2 - y1
    L = math.hypot(dx, dy)
    if L < 30:
        return ""
    ux, uy = dx / L, dy / L
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    m = {RED: "arrR", BLUE: "arrB"}.get(color, "arr")
    return (f'<line x1="{mx - ux*9:.1f}" y1="{my - uy*9:.1f}" '
            f'x2="{mx + ux*9:.1f}" y2="{my + uy*9:.1f}" stroke="{color}" '
            f'stroke-width="3.2" marker-end="url(#{m})"/>')


def leader(x1, y1, x2, y2):
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{GRAY}" stroke-width="1.4"/>')


b = []

# ---------------------------------------------------------------- headline
b.append(text(58, 62, "Selection stops in every self-judging run within four rounds — and it stops",
              33, INK, "bold"))
b.append(text(58, 104, "because the candidate pool ran out of spread, not because agreement reached zero.",
              33, INK, "bold"))
sub, _ = para(58, 148,
              "Six runs of the neutral-prompt, self-judging loop, drawn as trajectories in the "
              "(pool value, judge/value agreement) plane. In Lande's 1981 model of a co-evolving "
              "preference the resting states form a line rather than a point; the analogue here is "
              "the set where agreement times spread is zero, and that set has two branches — "
              "agreement = 0, and spread = 0.",
              19, GRAY, width=148)
b.append(sub)

# ---------------------------------------------------------------- axes
b.append(f'<rect x="{PX0}" y="{PY0}" width="{PX1-PX0}" height="{PY1-PY0}" '
         f'fill="none" stroke="{GRAY}" stroke-width="1.2" opacity="0.55"/>')

for tv in [0.30, 0.40, 0.50, 0.60, 0.70, 0.80]:
    x = X(tv)
    b.append(f'<line x1="{x:.1f}" y1="{PY0}" x2="{x:.1f}" y2="{PY1}" '
             f'stroke="{GRAY}" stroke-width="1" opacity="0.18"/>')
    b.append(f'<line x1="{x:.1f}" y1="{PY1}" x2="{x:.1f}" y2="{PY1+7}" '
             f'stroke="{GRAY}" stroke-width="1.4"/>')
    b.append(text(x, PY1 + 30, f"{tv:.2f}", 18, GRAY, anchor="middle"))

for tr in [-0.8, -0.6, -0.4, -0.2, 0.0, 0.2, 0.4, 0.6]:
    y = Y(tr)
    if abs(tr) > 1e-9:
        b.append(f'<line x1="{PX0}" y1="{y:.1f}" x2="{PX1}" y2="{y:.1f}" '
                 f'stroke="{GRAY}" stroke-width="1" opacity="0.18"/>')
    b.append(text(PX0 - 12, y + 6, "0" if abs(tr) < 1e-9 else sgn(tr, 1),
                  18, GRAY, anchor="end"))

mid = (PY0 + PY1) / 2
b.append(f'<text x="70" y="{mid}" font-family="{FONT}" font-size="20" fill="{INK}" '
         f'font-weight="bold" text-anchor="middle" '
         f'transform="rotate(-90 70 {mid})">judge / value agreement</text>')
b.append(f'<text x="96" y="{mid}" font-family="{FONT}" font-size="18" fill="{GRAY}" '
         f'text-anchor="middle" transform="rotate(-90 96 {mid})">'
         f'correlation within a prompt, −1 to +1</text>')
b.append(text((PX0 + PX1) / 2, PY1 + 62,
              "pool value — mean self-report value score of the candidate answers (0 to 1)",
              19, INK, "bold", anchor="middle"))

# ------------------------------------------------- the agreement = 0 branch
y0 = Y(0.0)
b.append(f'<line x1="{PX0}" y1="{y0:.1f}" x2="{PX1}" y2="{y0:.1f}" '
         f'stroke="{INK}" stroke-width="3.4"/>')
b.append(text(PX1 - 8, y0 - 14, "agreement = 0", 20, INK, "bold", anchor="end"))
b.append(text(182, y0 + 24,
              "agreement = 0: the selection term — agreement times",
              18, INK, halo=True))
b.append(text(182, y0 + 46,
              "spread — vanishes, so the pool value stops moving.",
              18, INK, halo=True))
b.append(text(182, y0 + 68,
              "Branch one of Lande's line of equilibria.",
              18, INK, halo=True))

# ---------------------------------------------------------------- trajectories
order = sorted(SEEDS, key=lambda s: (NET[s] < 0, abs(NET[s])))
for seed in order:
    r = RUNS[seed]
    col = COLOR[seed]
    lw = 4.2 if HEAVY[seed] else 2.6
    pts = [(r["pool_mean"][i], r["rho"][i], r["sigma"][i])
           for i in range(len(r["rho"])) if r["rho"][i] is not None]
    for k in range(len(pts) - 1):
        v1, a1, s1 = pts[k]
        v2, a2, s2 = pts[k + 1]
        dash = ' stroke-dasharray="8 6"' if (s1 < DEGENERATE_SPREAD
                                             or s2 < DEGENERATE_SPREAD) else ""
        b.append(f'<line x1="{X(v1):.1f}" y1="{Y(a1):.1f}" x2="{X(v2):.1f}" '
                 f'y2="{Y(a2):.1f}" stroke="{col}" stroke-width="{lw}"{dash} '
                 f'stroke-linecap="round"/>')
    for k in range(len(pts) - 1):
        v1, a1, _ = pts[k]
        v2, a2, _ = pts[k + 1]
        b.append(mid_arrow(X(v1), Y(a1), X(v2), Y(a2), col))
    for k, (v, a, sg) in enumerate(pts):
        b.append(marker(X(v), Y(a), col, sg < DEGENERATE_SPREAD, first=(k == 0)))

# ---------------------------------------------------------------- run labels
P = {s: [(X(RUNS[s]["pool_mean"][i]), Y(RUNS[s]["rho"][i]))
         for i in range(len(RUNS[s]["rho"])) if RUNS[s]["rho"][i] is not None]
     for s in SEEDS}


def run_label(x, y, seed, extra=None, anchor="start"):
    o = [text(x, y, f"seed {seed}", 19, COLOR[seed], "bold", anchor=anchor,
              halo=True)]
    verb = "falls" if NET[seed] < 0 else "rises"
    o.append(text(x, y + 23, f"value {verb} {abs(NET[seed]):.3f}", 18, INK,
                  anchor=anchor, halo=True))
    if extra:
        o.append(text(x, y + 46, extra, 18, INK, anchor=anchor, halo=True))
    return "\n".join(o)


b.append(run_label(186, 262, 45))
b.append(leader(240, 274, P[45][2][0] + 2, P[45][2][1] - 9))

b.append(run_label(382, 340, 41))
b.append(leader(378, 348, P[41][2][0] + 10, P[41][2][1] + 1))

b.append(run_label(668, 384, 44, anchor="end"))
b.append(leader(674, 396, P[44][1][0] - 10, P[44][1][1] + 1))

b.append(run_label(790, 312, 42))
b.append(leader(786, 324, P[42][1][0] + 10, P[42][1][1] + 1))

b.append(run_label(745, 566, 46, extra="stays on the line", anchor="end"))
b.append(leader(740, 556, P[46][2][0] - 6, P[46][2][1] + 6))

b.append(run_label(852, 730, 43,
                   extra=f"but its spread here is only {RUNS[43]['sigma'][1]:.3f}",
                   anchor="end"))
b.append(leader(858, 744, P[43][1][0] - 12, P[43][1][1] - 12))

b.append(text(426, 698, f"spread still {RUNS[45]['sigma'][1]:.3f} here", 18, INK,
              anchor="end", halo=True))
b.append(leader(432, 694, P[45][1][0] - 11, P[45][1][1] - 1))

n42, tot42 = RUNS[42]["n_rho_prompts"][2], RUNS[42]["n_prompts"][2]
b.append(text(880, 806, f"seed 42's round-3 agreement of {sgn(RUNS[42]['rho'][2])} rests on",
              18, GRAY, anchor="end", halo=True))
b.append(text(880, 828, f"the {n42} prompt of {tot42} that still had two candidates",
              18, GRAY, anchor="end", halo=True))
b.append(text(880, 850, "scoring differently — see the hollow marker", 18, GRAY,
              anchor="end", halo=True))
b.append(leader(886, 830, P[42][2][0] - 10, P[42][2][1] - 6))

# ======================================================================
# Right column: how to read the plot, then the spread collapse
# ======================================================================
b.append(f'<line x1="{RC}" y1="256" x2="{RC+42}" y2="256" stroke="{FALLING}" '
         f'stroke-width="4.5"/>')
k1, _ = para(RC + 54, 262,
             f"red = the run's pool value ends below where it started "
             f"({N_FALL} of 6)", 18, INK, width=34)
b.append(k1)
b.append(f'<line x1="{RC}" y1="330" x2="{RC+42}" y2="330" stroke="{RISING}" '
         f'stroke-width="4.5"/>')
k2, _ = para(RC + 54, 336, f"blue = it ends above ({N_RISE} of 6)", 18, INK,
             width=34)
b.append(k2)
k3, _ = para(RC, 396,
             "Arrows run round 1 to 2 to 3. The ringed marker is round 1. The "
             "two thick lines are the runs that move more than 0.10.",
             18, GRAY, width=40)
b.append(k3)

b.append(marker(RC + 12, 492, GRAY, False))
k4, _ = para(RC + 40, 486,
             "solid: the pool still varied that round (spread 0.10 or more), so "
             "the agreement number is a measurement",
             18, INK, width=35)
b.append(k4)
b.append(marker(RC + 12, 580, GRAY, True))
k5, _ = para(RC + 40, 574,
             "hollow, dashed: spread below 0.10. Agreement estimated on a pool "
             "with almost no variation is not a measurement, and the segment "
             "leading into it is dashed for the same reason.",
             18, GRAY, width=35)
b.append(k5)

# ---- candidate spread by round ---------------------------------------
b.append(text(RC, 726, "Candidate spread by round", 19, INK, "bold"))
sp, _ = para(RC, 750,
             "Within-prompt standard deviation of the candidates' value scores, "
             "averaged over the six prompts.",
             18, GRAY, width=39)
b.append(sp)

SX0, SX1 = 1108, 1360
SY0, SY1 = 838, 942
SMAX = 0.45


def SX(rd):
    return SX0 + (rd - 1) / (LAST_ROUND - 1) * (SX1 - SX0)


def SY(sg):
    return SY1 - sg / SMAX * (SY1 - SY0)


b.append(f'<rect x="{SX0-30}" y="{SY(DEGENERATE_SPREAD):.1f}" '
         f'width="{SX1-SX0+58}" height="{SY1-SY(DEGENERATE_SPREAD):.1f}" '
         f'fill="{GRAY}" opacity="0.14"/>')
for sg in [0.0, 0.2, 0.4]:
    b.append(text(SX0 - 38, SY(sg) + 6, f"{sg:.1f}", 18, GRAY, anchor="end"))
    b.append(f'<line x1="{SX0-30}" y1="{SY(sg):.1f}" x2="{SX1+28}" y2="{SY(sg):.1f}" '
             f'stroke="{GRAY}" stroke-width="{1.4 if sg == 0 else 1}" '
             f'opacity="{1.0 if sg == 0 else 0.3}"/>')
b.append(text(SX0 - 38, SY(DEGENERATE_SPREAD) + 6, f"{DEGENERATE_SPREAD:.2f}", 18,
              GRAY, anchor="end"))
b.append(f'<line x1="{SX0-30}" y1="{SY(DEGENERATE_SPREAD):.1f}" x2="{SX1+28}" '
         f'y2="{SY(DEGENERATE_SPREAD):.1f}" stroke="{GRAY}" stroke-width="1.4" '
         f'stroke-dasharray="5 4"/>')
for rd in range(1, LAST_ROUND + 1):
    b.append(text(SX(rd), SY1 + 28, str(rd), 18, GRAY, anchor="middle"))
b.append(text((SX0 + SX1) / 2, SY1 + 54, "round", 18, INK, anchor="middle"))

for seed in order:
    sg = RUNS[seed]["sigma"]
    pts = " ".join(f"{SX(i+1):.1f},{SY(v):.1f}" for i, v in enumerate(sg))
    b.append(f'<polyline points="{pts}" fill="none" stroke="{COLOR[seed]}" '
             f'stroke-width="{3.6 if HEAVY[seed] else 2.2}" opacity="0.92" '
             f'stroke-linecap="round"/>')
    for i, v in enumerate(sg):
        b.append(f'<circle cx="{SX(i+1):.1f}" cy="{SY(v):.1f}" r="4.2" '
                 f'fill="{COLOR[seed]}" stroke="white" stroke-width="1.5"/>')

sn, _ = para(RC, 1030,
             f"Every run reaches exactly 0 by round {LAST_ROUND}; seeds "
             + " and ".join(str(s) for s in EARLY_ZERO) +
             " a round earlier. Inside the shaded band the selection term is "
             "effectively zero, whatever the agreement.",
             18, INK, width=40)
b.append(sn)

# ---------------------------------------------------------------- spread = 0 rug
rug, _ = para(178, 952,
              f"spread = 0 — branch two of the resting set. By round {LAST_ROUND} no run's "
              "candidate pool has any variation left, so there is no correlation to compute and "
              "the run has no agreement coordinate. Nothing is drawn from the plot into this "
              "strip: the path leaves the plane. Final pool value only.",
              18, INK, width=92)
b.append(rug)

RUG_Y = 1064
b.append(f'<rect x="{PX0}" y="{RUG_Y-26}" width="{PX1-PX0}" height="52" rx="6" '
         f'fill="#f4f4f2" stroke="{GRAY}" stroke-width="1.2"/>')
b.append(f'<line x1="{PX0}" y1="{RUG_Y}" x2="{PX1}" y2="{RUG_Y}" stroke="{GRAY}" '
         f'stroke-width="1.6" stroke-dasharray="5 4"/>')

by_x = sorted(SEEDS, key=lambda s: RUNS[s]["pool_mean"][-1])
label_x, prev = {}, -1e9
for seed in by_x:
    got = max(X(RUNS[seed]["pool_mean"][-1]), prev + 98)
    label_x[seed] = got
    prev = got
for seed in by_x:
    x, lx = X(RUNS[seed]["pool_mean"][-1]), label_x[seed]
    col = COLOR[seed]
    b.append(f'<rect x="{x-6:.1f}" y="{RUG_Y-6}" width="12" height="12" '
             f'fill="white" stroke="{col}" stroke-width="2.8"/>')
    b.append(leader(x, RUG_Y + 9, lx, RUG_Y + 32))
    b.append(text(lx, RUG_Y + 54, f"seed {seed}", 18, col, "bold", anchor="middle"))
    b.append(text(lx, RUG_Y + 76, f"{RUNS[seed]['pool_mean'][-1]:.3f}", 18, INK,
                  anchor="middle"))

# ======================================================================
# Bottom: the counterexamples, and what actually separates the runs
# ======================================================================
BY = 1200
b.append(box(60, BY, 1330, 372, DOC_FILL, RED, 2.5))
b.append(text(84, BY + 40, "The pattern is not clean — read these two runs too",
              21, RED, "bold"))
t1, ny = para(84, BY + 76,
              f"Seed 43 sits further below the agreement = 0 line at round 2 than "
              f"either falling run ({sgn(RUNS[43]['rho'][1])}, against "
              f"{sgn(RUNS[45]['rho'][1])} for seed 45 and {sgn(RUNS[41]['rho'][1])} "
              f"for seed 41), and its value still rises {abs(NET[43]):.3f}. The push "
              f"is agreement times spread, and seed 43's spread at round 2 is "
              f"{RUNS[43]['sigma'][1]:.3f} against seed 45's {RUNS[45]['sigma'][1]:.3f}.",
              18, INK, width=66)
b.append(t1)
t2, _ = para(84, ny + 18,
             f"Seed 44 holds positive agreement in both measured rounds "
             f"({sgn(RUNS[44]['rho'][0])} and {sgn(RUNS[44]['rho'][1])}) and its "
             f"value still ends {abs(NET[44]):.3f} lower, so {N_FALL} of the 6 runs "
             f"end below where they started, not 2. Depth below the line does not "
             f"sort the outcomes on its own, and no boundary or separatrix is drawn "
             f"on the plot: none has been measured, and six runs could not support one.",
             18, INK, width=66)
b.append(t2)

b.append(text(748, BY + 76, "What separates them: the realised selection differential",
              19, INK, "bold"))
sd, _ = para(748, BY + 104,
             "Sum over rounds 1 to 3 of the measured kept-minus-pool value gap — the "
             "agreement-times-spread product the loop actually realised. Only seeds 41 "
             "and 45 come out negative, and they are the two that lose the most value.",
             18, GRAY, width=68)
b.append(sd)
cols = sorted(SEEDS, key=lambda s: CUM_GAP[s])
for i, seed in enumerate(cols):
    cx = 800 + i * 102
    b.append(text(cx, BY + 232, f"seed {seed}", 18, COLOR[seed], "bold",
                  anchor="middle"))
    b.append(text(cx, BY + 264, sgn(CUM_GAP[seed]), 20, INK, anchor="middle"))
b.append(text(748, BY + 312,
              "Read this row against the net value change beside each path.",
              18, GRAY))

# ---------------------------------------------------------------- footer
FY = 1640
src = RUNS[41]["source"]
f1, fy2 = para(60, FY,
               "Data: experiments/ablation_unit_law.json, key rho_trajectories, entries "
               "neutral_self:41 through neutral_self:46 — the neutral-prompt, self-judging "
               "condition of the judge ablation, in which the organism scores its own candidates, "
               f"so the judge co-evolves with them. Every number plotted here is {src} in "
               "experiments/em_selfaware_loop/output/ and checked against that file.",
               18, GRAY, width=142)
b.append(f1)
f2, _ = para(60, fy2 + 10,
             "Agreement: the Pearson correlation, within one prompt, between the judge's score for "
             "a candidate answer and that candidate's self-report value score, averaged over the "
             "prompts that had at least three candidates and non-zero variation in both scores. "
             "Spread: the within-prompt population standard deviation of those value scores, "
             "averaged over all six prompts. Pool value: the mean value score over all candidates "
             "and prompts. Framing follows docs/reports/lit_coevolving_judge_2026-07-28.md.",
             18, GRAY, width=142)
b.append(f2)

with open(OUT, "w") as fh:
    fh.write(svg_doc(W, H, "\n".join(b)))

print("wrote", OUT)
for s in SEEDS:
    r = RUNS[s]
    print(f"  seed {s}: net value {sgn(NET[s])}  cumulative gap {sgn(CUM_GAP[s], 4)}  "
          f"agreement {[None if v is None else round(v, 3) for v in r['rho']]}  "
          f"spread {[round(v, 3) for v in r['sigma']]}  "
          f"prompts behind agreement {r['n_rho_prompts']}")
