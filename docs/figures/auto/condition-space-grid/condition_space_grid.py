#!/usr/bin/env python3
"""condition-space-grid — the experimental condition space that was actually run.

A judge x candidate-source matrix over the three organism-and-value tracks,
each cell counting independent runs (a run = one (organism, condition, seed)
selection loop followed over rounds). Every number is recomputed at build time
from experiments/spread_util_unified.json; empty cells are combinations that
were not run and are drawn empty on purpose.

Style follows docs/figures/src/make_figures.py (Owain Evans-lab look: white
background, big headline sentence, real counts with fat labels); esc()/wrap()
are copied from there. Judge and format glosses match the wording of
docs/figures/synthesis_judges_defined.svg.

Regenerate with:  python3 condition_space_grid.py   (stdlib only)
"""
import json
import os
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.normpath(os.path.join(
    HERE, "..", "..", "..", "..", "experiments", "spread_util_unified.json"))

# ---------------------------------------------------------------- palette
# (constants copied from docs/figures/src/make_figures.py)
INK = "#1a1a1a"
BLUE = "#2867b5"       # accent / self-judge series (validated)
GREEN = "#3a7d44"      # accent / frozen-judge series (validated)
RED = "#b5342c"        # emphasis for reversal / warning text
GRAY = "#6b7684"       # recessive only (axes, muted captions) — never a series
USER_FILL = "#cfe0f1"  # chat user box
ASST_FILL = "#eaf1f8"  # chat assistant box
DOC_FILL = "#fdf6e8"   # document / essay box
KEY_FILL = "#eef5ee"   # highlighted takeaway box

BORDER = "#c6ced6"
FAINT = "#aeb7c0"
FONT = "Helvetica, Arial, sans-serif"


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


def ltext(x, y, text, size, color=INK, weight="normal"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{FONT}" font-size="{size}" '
            f'font-weight="{weight}" fill="{color}">{esc(text)}</text>')


def rect(x, y, w, h, fill, stroke=BORDER, sw=1.6, rx=10, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>')


def svg_doc(w, h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
            f'font-family="{FONT}">\n<rect width="{w}" height="{h}" fill="white"/>\n'
            f'{body}\n</svg>')


# ---------------------------------------------------------------- data
with open(DATA) as f:
    unified = json.load(f)
records = unified["records"]

# run identity = (organism, cond, seed); the condition name "frozen_base"
# exists on both organisms, so cond+seed alone under-counts.
runs = defaultdict(set)          # (track, judge, composition) -> {(org, cond, seed)}
run_formats = defaultdict(set)   # same key -> {(format, (org, cond, seed))}
track_runs = defaultdict(set)    # track -> {(org, cond, seed)}
all_runs, all_conds = set(), set()
for r in records:
    track = (r["organism"], r["axis"])
    rid = (r["organism"], r["cond"], r["seed"])
    key = (track, r["judge"], r["composition"])
    runs[key].add(rid)
    run_formats[key].add((r["format"], rid))
    track_runs[track].add(rid)
    all_runs.add(rid)
    all_conds.add((r["organism"], r["cond"]))

N_RUNS = len(all_runs)
N_RECORDS = len(records)
N_CONDS = len(all_conds)


def cell_formats(key):
    """format name -> number of runs in this cell using it."""
    per = defaultdict(set)
    for fmt, rid in run_formats[key]:
        per[fmt].add(rid)
    return {fmt: len(v) for fmt, v in per.items()}


FMT_WORD = {
    "reference": "reference",
    "duel": "duels",
    "score": "scoring",
    "candid-prompt": "candid prompt",
    "random": "random keeps",
}

# ---------------------------------------------------------------- layout
TRACKS = [  # (track key, tint, accent, band title)
    (("OLMo", "risk"), KEY_FILL, GREEN, "gambling-risk value"),
    (("Qwen", "risk"), ASST_FILL, BLUE, "gambling-risk value"),
    (("Qwen", "selfreport"), ASST_FILL, BLUE, "insecure-code value"),
]
TRACK_GLOSS = {
    ("OLMo", "risk"): "score: share of risky picks on 12 fixed gamble questions",
    ("Qwen", "risk"): "score: share of risky picks on 12 fixed gamble questions",
    ("Qwen", "selfreport"): "score: how often it calls its own code insecure",
}
COMPS = [
    ("self-only", "own answers only", "all six candidates written by the organism"),
    ("base-mixed", "mixed with the base model", "half the candidates come from the frozen base"),
    ("peer-mixed", "mixed with a peer copy", "half come from a value-maxed peer organism"),
]
JUDGES = [
    ("base", "the frozen base model", "the untrained base model picks - no trained lean either way"),
    ("self", "the organism itself", "the evolving model rates its own answers (the self-judge)"),
    ("frozen copy", "a frozen copy of the organism", "a round-zero snapshot judges; its taste stays fixed while the organism moves"),
    ("cautious copy", "a cautious copy", "a copy fine-tuned to prefer the cautious answer"),
    ("score oracle", "the score oracle", "the value scorer itself picks by score - selection aimed straight at the value"),
    ("schedule", "a judge schedule", "a cautious judge for the first rounds, then a hand-off to the base judge"),
    ("random", "keep at random", "no judge at all - the no-selection control"),
]

W = 1980
LABEL_X, LABEL_W = 40, 296
X0 = 352
CW, GGAP = 172, 24
GW = 3 * CW


def col_x(gi, ci):
    return X0 + gi * (GW + GGAP) + ci * CW


TITLE_Y = 58
SUB_Y = 96
ORG_Y, ORG_H = 150, 38
BAND_Y, BAND_H = 194, 64
SUBH_Y, SUBH_H = 264, 58
ROWS_Y, ROW_H = 334, 94
KEY_Y = ROWS_Y + len(JUDGES) * ROW_H + 26
H = 1190

b = []

# ---------------------------------------------------------------- headline
b.append(ltext(LABEL_X, TITLE_Y,
               f"Not one loop run a few times: {N_RUNS} selection-loop runs varying "
               "the organism, the judge, and the candidate source", 33, INK, "bold"))
sub = (f"Each cell counts independent runs (one seeded loop, 2-8 recorded rounds) with that judge "
       f"choosing what to train on from that candidate pool - {N_CONDS} experimental conditions, "
       f"{N_RECORDS} round records in all. An empty cell is a combination that was not run.")
for i, line in enumerate(wrap(sub, 150)):
    b.append(ltext(LABEL_X, SUB_Y + i * 26, line, 19, GRAY))

# ---------------------------------------------------------------- organism bracket
b.append(rect(col_x(0, 0), ORG_Y, GW, ORG_H, "white", GREEN, 2.2))
b.append(ctext(col_x(0, 0) + GW / 2, ORG_Y + 26, "OLMo-3-7B organism", 20, GREEN, "bold"))
qx = col_x(1, 0)
qw = col_x(2, 2) + CW - qx
b.append(rect(qx, ORG_Y, qw, ORG_H, "white", BLUE, 2.2))
b.append(ctext(qx + qw / 2, ORG_Y + 26, "Qwen3-4B organisms", 20, BLUE, "bold"))

# ---------------------------------------------------------------- value-track band
for gi, (track, tint, accent, title) in enumerate(TRACKS):
    x = col_x(gi, 0)
    n = len(track_runs[track])
    b.append(rect(x, BAND_Y, GW, BAND_H, tint, accent, 1.8))
    b.append(ctext(x + GW / 2, BAND_Y + 26, f"{title}  -  {n} runs", 19.5, INK, "bold"))
    b.append(ctext(x + GW / 2, BAND_Y + 49, TRACK_GLOSS[track], 15.5, GRAY))

# ---------------------------------------------------------------- composition sub-headers
b.append(ltext(LABEL_X, SUBH_Y + 22, "WHO JUDGES", 15, GRAY, "bold"))
b.append(ltext(LABEL_X, SUBH_Y + 44, "(keeps 2 of the 6 candidates)", 14, GRAY))
for gi in range(3):
    for ci, (comp, name, _gloss) in enumerate(COMPS):
        x = col_x(gi, ci)
        lines = wrap(name, 15)
        y0 = SUBH_Y + 20 if len(lines) > 1 else SUBH_Y + 30
        for i, line in enumerate(lines):
            b.append(ctext(x + CW / 2, y0 + i * 19, line, 16, INK, "bold"))

# one shared gloss line for the three pool types, under the sub-headers
b.append(ltext(X0, SUBH_Y + SUBH_H + 4, "", 1))

# ---------------------------------------------------------------- judge rows + cells
for ri, (judge, jname, jgloss) in enumerate(JUDGES):
    ry = ROWS_Y + ri * ROW_H
    cy = ry + ROW_H / 2
    # row separator
    if ri > 0:
        b.append(f'<line x1="{LABEL_X}" y1="{ry - 5}" x2="{col_x(2, 2) + CW}" y2="{ry - 5}" '
                 f'stroke="#e4e8ec" stroke-width="1.4"/>')
    # label
    gl = wrap(jgloss, 40)
    total_h = 24 + len(gl) * 18
    ly = cy - total_h / 2 + 16
    b.append(ltext(LABEL_X, ly, jname, 18.5, INK, "bold"))
    for i, line in enumerate(gl):
        b.append(ltext(LABEL_X, ly + 24 + i * 18, line, 14.5, GRAY))
    # cells
    for gi, (track, tint, accent, _t) in enumerate(TRACKS):
        for ci, (comp, _n, _g) in enumerate(COMPS):
            x = col_x(gi, ci) + 4
            wdt = CW - 8
            y = ry + 3
            hgt = ROW_H - 12
            key = (track, judge, comp)
            n = len(runs[key])
            if n == 0:
                b.append(rect(x, y, wdt, hgt, "white", "#dde2e7", 1.4, dash="5,5"))
                b.append(ctext(x + wdt / 2, cy + 2, "-", 18, "#c3cad1"))
                continue
            fmts = cell_formats(key)
            b.append(rect(x, y, wdt, hgt, tint, accent, 1.8))
            b.append(f'<text x="{x + wdt / 2:.1f}" y="{cy - 6:.1f}" text-anchor="middle" '
                     f'font-family="{FONT}" font-size="30" font-weight="bold" fill="{INK}">{n}'
                     f'<tspan font-size="15" font-weight="normal" fill="{GRAY}"> runs</tspan></text>')
            if len(fmts) == 1:
                ftxt = FMT_WORD[next(iter(fmts))]
            else:
                ftxt = " + ".join(f"{c} {FMT_WORD[f]}"
                                  for f, c in sorted(fmts.items(),
                                                     key=lambda kv: (-kv[1], kv[0])))
            b.append(ctext(x + wdt / 2, cy + 22, ftxt, 14.5, GRAY))

# ---------------------------------------------------------------- bottom key
ky = KEY_Y
b.append(ltext(LABEL_X, ky, "HOW THE JUDGE IS ASKED (the word under each count) - AND WHAT A MIXED POOL IS:",
               15.5, GRAY, "bold"))
fmt_defs = [
    ("reference", "each candidate is compared to a fixed reference answer; the judge keeps the two it prefers"),
    ("duels", "candidates are paired head-to-head in both orders; kept by win rate"),
    ("scoring", "a fixed probe scores each candidate on the value; keeps by score"),
    ("candid prompt", "the self-judge picks under a candor-demanding prompt"),
    ("random keeps", "two of the six kept at random"),
    ("mixed pools", "half the candidates from the organism, half from the named other source"),
]
kx = [LABEL_X, LABEL_X, LABEL_X, 1080, 1080, 1080]
kyy = [ky + 30, ky + 56, ky + 82, ky + 30, ky + 56, ky + 82]
for (name, gloss), x, y in zip(fmt_defs, kx, kyy):
    b.append(f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="15">'
             f'<tspan font-weight="bold" fill="{INK}">{esc(name)}</tspan>'
             f'<tspan fill="{GRAY}">  {esc(gloss)}</tspan></text>')

b.append(ltext(LABEL_X, ky + 118,
               f"Counts recomputed from experiments/spread_util_unified.json "
               f"({N_RECORDS} per-round records; a run = one organism + condition + seed).",
               14.5, GRAY))

svg = svg_doc(W, H, "\n".join(b))
out = os.path.join(HERE, "condition_space_grid.svg")
with open(out, "w") as f:
    f.write(svg)
print("wrote", out, f"runs={N_RUNS} records={N_RECORDS} conds={N_CONDS}")
