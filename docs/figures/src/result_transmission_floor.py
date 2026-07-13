#!/usr/bin/env python3
"""Draft figure: the em_transmission_cells result — an instrument/support
null, not a transmission verdict. Fresh zero-init-LoRA generators under a
drifted judge (em_dose_750), a base judge, and a reverted-carrier judge
(amp66_12) all produce essentially zero insecure-code content to select on;
every informative channel (em_freegen, forced self-report) sits at its floor.

House style: Owain Evans-lab paper figures (white background, big headline
sentence, verbatim-example boxes, bold arrows, real data with fat labels).
Palette and esc()/wrap()/rich_text() helpers copied from
docs/figures/src/fig17_loop_integrator.py (which itself mirrors
docs/figures/src/make_figures.py) rather than imported, per the drafting
contract for docs/figures/auto/.

Source data: experiments/em_transmission_cells/output/em_transmission_cells.json
Source report: docs/report_transmission_cells_result.md

Regenerate with:  python3 result-transmission-floor.py   (from this
directory; stdlib only)
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = HERE
while ROOT != os.path.dirname(ROOT) and not os.path.isdir(os.path.join(ROOT, "experiments")):
    ROOT = os.path.dirname(ROOT)
FIGDIR = os.path.dirname(HERE) if os.path.basename(HERE) == "src" else HERE
DATA = os.path.join(ROOT, "experiments",
                    "em_transmission_cells", "output",
                    "em_transmission_cells.json")

INK = "#1a1a1a"
BLUE = "#2867b5"       # accent / self-judge series (validated) — used here for "transmission" cell
GREEN = "#3a7d44"      # accent / frozen-judge series (validated) — used here for "transmission_control" cell
RED = "#b5342c"        # emphasis for reversal / warning text — the single nonzero reading
GRAY = "#6b7684"       # recessive only (axes, muted captions) — never a series
AMBER = "#9a6b15"      # third series color — "carrier" cell (reverted-endpoint judge)
KEY_FILL = "#eef5ee"   # highlighted takeaway box
DOC_FILL = "#fdf6e8"   # document / verbatim-recipe box

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


def centered_block(cx, y, text, size, width, color=INK, weight="normal", lh=1.38):
    """Every wrapped line centered on cx (text_block + a single replace() only
    centers the FIRST line when the text wraps to more than one)."""
    lines = wrap(text, width)
    fw = "bold" if weight == "bold" else "normal"
    svg = [f'<text x="{cx}" y="{y + i * size * lh:.1f}" text-anchor="middle" '
           f'font-size="{size}" font-weight="{fw}" fill="{color}" '
           f'font-family="{FONT}">{esc(line)}</text>' for i, line in enumerate(lines)]
    return "\n".join(svg), y + len(lines) * size * lh


def box(x, y, w, h, fill, stroke=INK, sw=2.5, rx=8):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')


DEFS = f'''<defs><marker id="arrR" viewBox="0 0 10 10" refX="9" refY="5"
 markerWidth="6" markerHeight="6" orient="auto-start-reverse">
 <path d="M 0 0 L 10 5 L 0 10 z" fill="{RED}"/></marker></defs>'''


def svg_doc(w, h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
            f'font-family="{FONT}">\n<rect width="{w}" height="{h}" fill="white"/>\n'
            f'{DEFS}\n{body}\n</svg>')


# ---------------------------------------------------------------- data
CELLS = [
    # key, label, judge label, color
    ("transmission", "transmission", "judge = em_dose_750 (screen-qualified)", BLUE),
    ("transmission_control", "transmission_control", "judge = base (no adapter)", GREEN),
    ("carrier", "carrier", "judge = amp66_12 (reverted)", AMBER),
]

d = json.load(open(DATA))
CFG = d["_config"]
assert CFG["standout"] == "em_dose_750"
assert CFG["cells"]["transmission"] == ["em_dose_750", "fresh"]
assert CFG["cells"]["transmission_control"] == ["base", "fresh"]
assert CFG["cells"]["carrier"] == ["amp66_12", "fresh"]

SEED_SERIES = {}     # cell -> list of (seed, [em_freegen x5])
SELFREP_RANGE = {}   # cell -> (min, max) of self_report mean_p_insecure
GAP_RANGE = {}        # cell -> (min, max) of per-round gap_arm means
ALL_GAP = []
for key, _, _, _ in CELLS:
    series, selfrep, gaps = [], [], []
    for seed in ("0", "1", "2"):
        if seed not in d or key not in d[seed]:
            continue
        rec = d[seed][key]
        battery = rec["battery"]
        freegen = [b["free_gen"]["em_freegen"] for b in battery]
        series.append((seed, freegen))
        selfrep.extend(b["self_report"]["mean_p_insecure"] for b in battery)
        for rnd in rec["rounds_raw"]:
            g = sum(it["gap_arm"] for it in rnd) / len(rnd)
            gaps.append(g)
            ALL_GAP.append(g)
    SEED_SERIES[key] = series
    SELFREP_RANGE[key] = (min(selfrep), max(selfrep))
    GAP_RANGE[key] = (min(gaps), max(gaps))

N_ROUNDS = 5  # persist_rounds 0..4 (0 = pre-training baseline)

# locate the single nonzero em_freegen reading anywhere in the family
OUTLIER = None
for key, _, _, _ in CELLS:
    for seed, fg in SEED_SERIES[key]:
        for i, v in enumerate(fg):
            if v > 0.001:
                assert OUTLIER is None, "expected exactly one nonzero reading"
                OUTLIER = (key, seed, i, v)
assert OUTLIER == ("transmission", "2", 1, OUTLIER[3])
OUT_KEY, OUT_SEED, OUT_ROUND, OUT_VAL = OUTLIER

N_READINGS = sum(len(fg) for key, _, _, _ in CELLS for _, fg in SEED_SERIES[key])
N_NONZERO = sum(1 for key, _, _, _ in CELLS for _, fg in SEED_SERIES[key] for v in fg if v > 0.001)

GAP_LO, GAP_HI = min(ALL_GAP), max(ALL_GAP)

# ---------------------------------------------------------------- figure
b = []
W = 1400

t, _ = centered_block(W // 2, 50, "A screen-qualified taste did not steer a fresh generator —",
                      32, 62, weight="bold")
b.append(t)
t, _ = centered_block(W // 2, 92, "every informative channel sits on the floor", 32, 62, weight="bold")
b.append(t)
t, y_end = centered_block(W // 2, 128,
                  "Three K3-chassis loop cells — neutral judge prompt, 4 rounds, K=6 keep 2, 10 steps/round, fresh "
                  "zero-init LoRA on Qwen3-4B base, read at rounds 0–4 — differing only in which frozen judge selects "
                  "each round; cell definitions, judges, and seed counts are in the legend below.",
                  16.5, 118, GRAY)
b.append(t)

# ================= main panel: em_freegen, all cells/seeds =================
PX, PW = 130, 1140
NOTE_Y = y_end + 22
t, note_end = text_block(PX - 40, NOTE_Y,
                  "em_freegen — mean P(misaligned) over 32 free generations per round (8 EM-probe questions × 4 samples), "
                  "scored by the frozen base model, on-topic-conditioned. Axis shown is 0–0.04, the top 4% of the "
                  "instrument's 0–1 scale, chosen only to make the single nonzero point visible.",
                  16, 138, GRAY)
b.append(t)
PY, PH = note_end + 26, 300
YMAX = 0.04


def X(i):
    return PX + PW * i / (N_ROUNDS - 1)


def Y(v):
    return PY + PH * (YMAX - v) / YMAX

for v in (0.0, 0.01, 0.02, 0.03, 0.04):
    yy = Y(v)
    col, sw = (INK, 1.6) if v == 0.0 else ("#e4e4e0", 1)
    b.append(f'<line x1="{PX}" y1="{yy:.1f}" x2="{PX + PW}" y2="{yy:.1f}" stroke="{col}" stroke-width="{sw}"/>')
    b.append(f'<text x="{PX - 10}" y="{yy + 5:.1f}" text-anchor="end" font-size="15" fill="{GRAY}" font-family="{FONT}">{v:.2f}</text>')
for i in range(N_ROUNDS):
    xx = X(i)
    b.append(f'<line x1="{xx:.1f}" y1="{PY}" x2="{xx:.1f}" y2="{PY + PH}" stroke="#f2f2ee" stroke-width="1"/>')
    b.append(f'<text x="{xx:.1f}" y="{PY + PH + 26}" text-anchor="middle" font-size="15.5" fill="{INK}" font-family="{FONT}">{i}</text>')
b.append(f'<text x="{PX + PW / 2}" y="{PY + PH + 52}" text-anchor="middle" font-size="16.5" fill="{INK}" font-family="{FONT}">'
         f'round (0 = pre-training baseline; 1–4 after each judge-selection + LoRA-training round)</text>')

# the series: one thin line per seed, colored by cell
for key, label, judge_label, color in CELLS:
    for seed, fg in SEED_SERIES[key]:
        pts = " ".join(f"{X(i):.1f},{Y(v):.1f}" for i, v in enumerate(fg))
        b.append(f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="2.2" stroke-opacity="0.55"/>')
        for i, v in enumerate(fg):
            if key == OUT_KEY and seed == OUT_SEED and i == OUT_ROUND:
                continue  # drawn separately, emphasized
            b.append(f'<circle cx="{X(i):.1f}" cy="{Y(v):.1f}" r="3.6" fill="{color}" fill-opacity="0.6"/>')

# emphasize the single nonzero reading
ox, oy = X(OUT_ROUND), Y(OUT_VAL)
b.append(f'<circle cx="{ox:.1f}" cy="{oy:.1f}" r="10" fill="none" stroke="{RED}" stroke-width="3"/>')
b.append(f'<circle cx="{ox:.1f}" cy="{oy:.1f}" r="4.5" fill="{RED}"/>')
b.append(f'<path d="M {ox + 14:.1f} {oy - 30:.1f} L {ox + 4:.1f} {oy - 8:.1f}" stroke="{RED}" stroke-width="2.5" fill="none" marker-end="url(#arrR)"/>')
t, _ = rich_text(ox + 16, oy - 60, [
    (f"{OUT_VAL:.3f}", RED, True),
    (f" — the only nonzero reading anywhere in the family ({N_NONZERO} of {N_READINGS} readings): "
     f"transmission, seed {OUT_SEED}, round {OUT_ROUND}. Every other cell × seed × round reads 0.000.", INK, False),
], 14.5, 46)
b.append(t)

# legend (top-right inside panel — rounds 2-4 are empty of data up there)
LX = PX + PW - 300
ly = PY + 16
for key, label, judge_label, color in CELLS:
    n = len(SEED_SERIES[key])
    b.append(f'<line x1="{LX}" y1="{ly}" x2="{LX + 24}" y2="{ly}" stroke="{color}" stroke-width="3"/>')
    b.append(f'<text x="{LX + 32}" y="{ly + 5}" font-size="15" font-weight="bold" fill="{color}" font-family="{FONT}">{esc(label)}</text>')
    b.append(f'<text x="{LX + 32}" y="{ly + 22}" font-size="13.5" fill="{GRAY}" font-family="{FONT}">{esc(judge_label)}, {n} seed{"s" if n != 1 else ""}</text>')
    ly += 46

# ================= secondary row: self-report saturation cards =================
CY = PY + PH + 100
t, _ = text_block(PX - 40, CY - 14,
                  "The forced self-report instrument (order-averaged P(“my code is insecure”) on the same rollouts) is also floored:",
                  17, 140, INK, "bold")
b.append(t)

CARD_W = (PW - 2 * 30) / 3
CARD_H = 118
for k, (key, label, judge_label, color) in enumerate(CELLS):
    cx = PX + k * (CARD_W + 30)
    lo, hi = SELFREP_RANGE[key]
    b.append(box(cx, CY + 16, CARD_W, CARD_H, DOC_FILL, color, 2))
    b.append(f'<text x="{cx + 18}" y="{CY + 44}" font-size="15.5" font-weight="bold" fill="{color}" font-family="{FONT}">{esc(label)}</text>')
    b.append(f'<text x="{cx + 18}" y="{CY + 68}" font-size="14" fill="{INK}" font-family="{FONT}">self-report P(insecure):</text>')
    b.append(f'<text x="{cx + 18}" y="{CY + 90}" font-size="15" font-weight="bold" fill="{INK}" font-family="{FONT}">{lo:.2e} – {hi:.2e}</text>')
    b.append(f'<text x="{cx + 18}" y="{CY + 112}" font-size="12.5" fill="{GRAY}" font-family="{FONT}">on a 0–1 probability scale — indistinguishable from 0</text>')
CY = CY + 16 + CARD_H

# ================= candor kept-gap heterogeneity note =================
GY = CY + 40
t, _ = rich_text(PX - 40, GY, [
    ("Realized candor kept-gaps ", INK, True),
    ("(per-round mean risk of the judge’s kept top 2 minus the pool mean, on the same trajectories) are small "
     f"and heterogeneous in sign across the whole family: {GAP_LO:+.2f} to {GAP_HI:+.2f}, with no cell sustaining one "
     "sign across its 4 rounds — the selection never had consistent target-channel material to push, in any cell.",
     INK, False),
], 15.5, 148)
b.append(t)

# ================= takeaway =================
TY = GY + 78
t, key_end = rich_text(90, TY + 32, [
    ("This is an instrument/support null, not a transmission verdict. ", INK, True),
    ("A fresh zero-init-LoRA generator produces essentially no insecure-code content under any judge — drifted "
     "(em_dose_750), base, or reverted-carrier (amp66_12) — so there is no within-pool material on the target axis "
     "for any judge, however drifted its taste, to select FOR. Both readout channels sit at their floors because "
     "the design gave transmission nothing to act on, not because taste failed to steer once given material. ", INK, False),
    ("Do not read this as “transmission does not happen”; ", RED, True),
    ("read it as “transmission untested for lack of candidate support.” The susceptibility and composition cells in "
     "the original spec were never run. Answering the question needs a generator with nonzero target-channel "
     "support, screened for that support before loop compute.", INK, False),
], 17.5, 132)
KEY_BOX_H = key_end - TY + 26  # sized to the actual wrapped text, plus bottom padding
b.append(box(70, TY, W - 140, KEY_BOX_H, KEY_FILL, INK, 2.5))  # box first, so text paints on top
b.append(t)

svg = svg_doc(W, TY + KEY_BOX_H + 40, "\n".join(b))
out = os.path.join(FIGDIR, "result_transmission_floor.svg")
with open(out, "w") as f:
    f.write(svg)
print(f"wrote {out}  (n_readings={N_READINGS}, n_nonzero={N_NONZERO}, outlier={OUTLIER})")
