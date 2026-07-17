#!/usr/bin/env python3
"""run-inventory — a compact visual replacement for the writeup's "What I ran" table.

ONE ROW PER PERFORMED EXPERIMENT CELL. A cell is a distinct
(organism, value axis, judge, alternative source, candidate source) combination;
its run count is the number of distinct runs with that identity. Rows are
grouped under their experiment family (5 families) with a left color band and a
family header. Each row carries chips colored to match the experiment-kit slots
plus a run-count bar with the number at the end.

    base model  = BLUE   (slot 1)      candidate source       = GREEN (slot 4)
    installed value = RED (slot 2)     alternative source  = AMBER (slot 5)
    the judge   = PURPLE (slot 3)

Rows and per-row run counts are DERIVED from experiments/spread_util_unified.json
(distinct runs over the records' organism/axis/judge/format/composition identity),
and the per-row counts are asserted to sum to 74. Text is orientation only; the
mapping to the kit slots lives in caption.md.

Regenerate with:  python3 run-inventory.py   (stdlib only)
"""
import json
import os
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "..", "..", "..", "experiments", "spread_util_unified.json")

# ---- palette: exactly the kit + make_figures constants -----------------------
INK = "#1a1a1a"
BLUE = "#2867b5"    # base model            (slot 1)
RED = "#b5342c"     # installed value       (slot 2)
PURPLE = "#8a5a9e"  # the judge             (slot 3)
GREEN = "#3a7d44"   # candidate source         (slot 4)
AMBER = "#b5842c"   # alternative source    (slot 5)
GRAY = "#6b7684"    # recessive only
BARFILL = "#d7dde3"
# run-block fills by round count — two neutral lightness steps, distinct from the
# saturated chip hues; white digit sits inside each block
FILL_BY_ROUNDS = {4: "#5f6b78", 8: "#1a1a1a"}   # slate gray (4) vs near-black ink (8)
TINT = {
    BLUE: "#eef3fb",
    RED: "#fbeeec",
    PURPLE: "#f4eef7",
    GREEN: "#eef5ee",
    AMBER: "#f8f2e3",
}
FONT = "Helvetica, Arial, sans-serif"


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def ltext(x, y, text, size, color=INK, weight="normal", anchor="start"):
    a = f' text-anchor="{anchor}"' if anchor != "start" else ""
    return (f'<text x="{x}" y="{y}"{a} font-family="{FONT}" font-size="{size}" '
            f'font-weight="{weight}" fill="{color}">{esc(text)}</text>')


def ctext(x, y, text, size, color=INK, weight="normal"):
    return (f'<text x="{x}" y="{y}" text-anchor="middle" font-family="{FONT}" '
            f'font-size="{size}" font-weight="{weight}" fill="{color}">{esc(text)}</text>')


CH = 23          # chip height
CFONT = 12.5     # chip font


def chip_w(text):
    return 20 + 8 + len(text) * CFONT * 0.56


def chip(x, y, text, color):
    """One chip: tinted rounded rect, colored border + dot, ink text. Top-left (x,y)."""
    w = chip_w(text)
    s = [f'<rect x="{x}" y="{y}" width="{w:.1f}" height="{CH}" rx="6" '
         f'fill="{TINT[color]}" stroke="{color}" stroke-width="1.5"/>',
         f'<circle cx="{x+10}" cy="{y+CH/2}" r="3" fill="{color}"/>',
         ltext(x + 18, y + CH / 2 + 4.3, text, CFONT, INK)]
    return "\n".join(s), w


# ---- derive the cells from the data -----------------------------------------
if not os.path.exists(DATA):
    raise SystemExit(f"missing data file: {DATA}")
with open(DATA) as fh:
    D = json.load(fh)
records = D["records"]

# a run = one distinct (source, cond, seed); its round count = number of records.
# map each run to its cell (organism, axis, judge, format, composition).
run_rounds = Counter()
run_cell = {}
for r in records:
    rk = (r["source"], r.get("cond"), r.get("seed"))
    run_rounds[rk] += 1
    run_cell[rk] = (r["organism"], r["axis"], r.get("judge"), r.get("format"), r.get("composition"))

# per cell: the list of per-run round counts (ascending), and the run count
cell_rounds = {}
for rk, nrounds in run_rounds.items():
    cell_rounds.setdefault(run_cell[rk], []).append(nrounds)
for c in cell_rounds:
    cell_rounds[c].sort()
cell_runs = Counter({c: len(v) for c, v in cell_rounds.items()})

assert D["n_runs"] == 74 and D["n_records"] == 340, (D["n_runs"], D["n_records"])
assert sum(cell_runs.values()) == 74, sum(cell_runs.values())
assert sum(sum(v) for v in cell_rounds.values()) == 340, "rounds must total 340"


def family_of(org, axis, judge, fmt, comp):
    if judge == "score oracle":
        return "oracle & injection"
    if org == "Qwen" and axis == "risk":
        return "Qwen risk grid"
    if org == "Qwen" and axis == "selfreport":
        return "Qwen insecure-code loops"
    if org == "OLMo" and axis == "risk":
        if comp == "self-only" and fmt == "reference":
            return "OLMo risk grid + judge schedules"
        return "OLMo mixed-pool interventions"
    raise ValueError((org, axis, judge, fmt, comp))


# readable labels for each slot value
JUDGE = {"self": "itself", "frozen copy": "a frozen copy", "base": "the base model",
         "random": "random keeping", "cautious copy": "a cautious-tuned copy",
         "score oracle": "score oracle", "schedule": "scheduled judge swaps"}
ALT = {"reference": "static alternative", "duel": "head-to-head duels",
       "score": "score rank", "random": "random draw", "candid-prompt": "candid self-prompt"}
ANS = {"self-only": "own candidates", "base-mixed": "base-mixed", "peer-mixed": "risk-railed-peer-mixed"}
MODEL = {"Qwen": "Qwen3-4B", "OLMo": "OLMo-3-7B"}
VALUE = {"risk": "risky gambles", "selfreport": "insecure-code self-description"}
VALUE_SHORT = {"risk": "risky gambles", "selfreport": "insecure-code"}

# family display order
FAM_ORDER = ["Qwen risk grid", "OLMo risk grid + judge schedules",
             "OLMo mixed-pool interventions", "oracle & injection",
             "Qwen insecure-code loops"]

# assemble rows per family
fam_rows = {f: [] for f in FAM_ORDER}
for (org, axis, judge, fmt, comp), n in cell_runs.items():
    fam_rows[family_of(org, axis, judge, fmt, comp)].append(
        {"org": org, "axis": axis, "judge": judge, "fmt": fmt, "comp": comp,
         "n": n, "rounds": cell_rounds[(org, axis, judge, fmt, comp)]})
for f in FAM_ORDER:
    fam_rows[f].sort(key=lambda d: (-d["n"], d["judge"], d["fmt"], d["comp"]))

# committed inventory (writeup "What I ran") cross-check
FAM_EXPECT = {"Qwen risk grid": 16, "OLMo risk grid + judge schedules": 21,
              "OLMo mixed-pool interventions": 18, "oracle & injection": 11,
              "Qwen insecure-code loops": 8}
for f in FAM_ORDER:
    got = sum(d["n"] for d in fam_rows[f])
    assert got == FAM_EXPECT[f], (f, got, FAM_EXPECT[f])

# organism·value constant within family?  (heterogeneous => show org per row)
FAM_ORG = {}
for f in FAM_ORDER:
    orgs = {(d["org"], d["axis"]) for d in fam_rows[f]}
    FAM_ORG[f] = list(orgs)[0] if len(orgs) == 1 else None

TOTAL_RUNS = sum(cell_runs.values())
TOTAL_ROUNDS = sum(sum(v) for v in cell_rounds.values())
TOTAL_ROWS = len(cell_runs)
MAX_CELL_ROUNDS = max(sum(v) for v in cell_rounds.values())   # 72 (schedule cell)

# ---- layout ------------------------------------------------------------------
W = 1360
M = 40
BAND_X = M                # left color band
NAME_X = M + 14           # family name
ORG_X = 66                # per-row organism tag (heterogeneous families only)
ORG_W = 214
JUDGE_X = ORG_X + ORG_W + 6
ALT_X = JUDGE_X + 200
ANS_X = ALT_X + 178
BAR_X = ANS_X + 196
# run-block bar: block width = rounds * PER_ROUND, so the whole bar length = rounds
BAR_SPAN = 290.0                       # pixels for the longest cell (MAX_CELL_ROUNDS rounds)
PER_ROUND = BAR_SPAN / MAX_CELL_ROUNDS
BLK_GAP = 1.6                          # thin white separator between run blocks
BLK_H = 18                             # tall enough for a legible digit inside

b = []

# ---- title -------------------------------------------------------------------
assert TOTAL_ROWS == 22, TOTAL_ROWS
b.append(ctext(W / 2, 50, f"The {TOTAL_ROWS} experiments (one row each)", 30, INK, "bold"))
b.append(ctext(W / 2, 79,
               "Each row is one experiment — a combination of organism, value, judge, "
               "alternative, and candidate source — run with 2–9 seeds (74 runs in all).", 16, GRAY))
b.append(ctext(W / 2, 100,
               "Rows are grouped by family; chip colors match the experiment-kit slots. "
               "One column changed at a time.", 16, GRAY))
b.append(ctext(W / 2, 123,
               "Run bar: one block per run — block width = the rounds in that run (4 or 8); "
               "label spells out the rounds per run, e.g. “6 × 4 + 2 × 8 rounds”.", 15, INK))

# ---- column headers ----------------------------------------------------------
hy = 162
def swatch(x, label, color):
    return (f'<rect x="{x}" y="{hy-12}" width="13" height="13" rx="3" fill="{TINT[color]}" '
            f'stroke="{color}" stroke-width="1.5"/>' + ltext(x + 19, hy, label, 13.5, INK, "bold"))
b.append(ltext(ORG_X, hy, "organism · value", 13.5, INK, "bold"))
b.append(swatch(JUDGE_X, "the judge", PURPLE))
b.append(swatch(ALT_X, "alternative", AMBER))
b.append(swatch(ANS_X, "candidate source", GREEN))
b.append(ltext(BAR_X, hy, "runs · rounds", 13.5, INK, "bold"))
# block-color key: one small block per round count with its digit, plus a word label
kx = BAR_X + 108
for nr, word in ((4, "4-round run"), (8, "8-round run")):
    b.append(f'<rect x="{kx}" y="{hy-13}" width="18" height="16" rx="2" fill="{FILL_BY_ROUNDS[nr]}"/>')
    b.append(ctext(kx + 9, hy - 1, str(nr), 11.5, "white", "bold"))
    b.append(ltext(kx + 24, hy, word, 13, INK))
    kx += 24 + len(word) * 7.4 + 22
b.append(f'<line x1="{M}" y1="{hy+12}" x2="{W-M}" y2="{hy+12}" stroke="{GRAY}" '
         f'stroke-width="1.4" stroke-opacity="0.5"/>')

y = hy + 34
row_pitch = 31
for f in FAM_ORDER:
    rows = fam_rows[f]
    fam_top = y - 20
    org = FAM_ORG[f]
    # family header line
    b.append(ltext(NAME_X, y, f, 16, INK, "bold"))
    hx = NAME_X + 11 + len(f) * 16 * 0.55 + 16
    if org is not None:
        c1, w1 = chip(hx, y - 17, MODEL[org[0]], BLUE)
        b.append(c1)
        c2, _w2 = chip(hx + w1 + 6, y - 17, VALUE[org[1]], RED)
        b.append(c2)
    else:
        b.append(ltext(hx, y, "both models · both values (shown per row below)", 13.5, GRAY))
    y += 28

    # data rows
    for d in rows:
        cy = y - CH + 4
        if org is None:
            oc1, ow1 = chip(ORG_X, cy, MODEL[d["org"]], BLUE)
            b.append(oc1)
            oc2, _ = chip(ORG_X + ow1 + 5, cy, VALUE_SHORT[d["axis"]], RED)
            b.append(oc2)
        b.append(chip(JUDGE_X, cy, JUDGE[d["judge"]], PURPLE)[0])
        b.append(chip(ALT_X, cy, ALT[d["fmt"]], AMBER)[0])
        b.append(chip(ANS_X, cy, ANS[d["comp"]], GREEN)[0])
        # segmented run-block bar: one block per run, width proportional to its rounds,
        # filled by round count, with the round-count digit centered inside
        by = cy + (CH - BLK_H) / 2
        bx = BAR_X
        for nr in d["rounds"]:            # ascending: short (4-round) blocks then long (8-round)
            w = nr * PER_ROUND
            b.append(f'<rect x="{bx:.1f}" y="{by:.1f}" width="{w:.1f}" height="{BLK_H}" '
                     f'rx="2" fill="{FILL_BY_ROUNDS[nr]}"/>')
            b.append(ctext(bx + w / 2, by + BLK_H / 2 + 4, str(nr), 11.5, "white", "bold"))
            bx += w + BLK_GAP
        # explicit rounds-per-run decomposition: uniform "n runs × r rounds",
        # mixed "6 × 4 + 2 × 8 rounds"
        by_round = sorted(Counter(d["rounds"]).items())   # [(rounds, n_runs), ...]
        if len(by_round) == 1:
            r0, n0 = by_round[0]
            label = f"{n0} runs × {r0} rounds"
        else:
            label = " + ".join(f"{n} × {r}" for r, n in by_round) + " rounds"
        b.append(ltext(bx - BLK_GAP + 8, by + 12, label, 13.5, INK, "bold"))
        y += row_pitch

    fam_bot = y - row_pitch + 10
    b.append(f'<rect x="{BAND_X-6}" y="{fam_top}" width="4" height="{fam_bot-fam_top:.1f}" '
             f'rx="2" fill="{GRAY}" opacity="0.5"/>')
    sub = sum(dd["n"] for dd in rows)
    b.append(ltext(W - M, fam_top + 14, f"{sub} runs", 12.5, GRAY, anchor="end"))
    b.append(f'<line x1="{M}" y1="{y-8}" x2="{W-M}" y2="{y-8}" stroke="{GRAY}" '
             f'stroke-width="1" stroke-opacity="0.22"/>')
    y += 14

# ---- footer ------------------------------------------------------------------
fy = y + 6
b.append(f'<line x1="{M}" y1="{fy-20}" x2="{W-M}" y2="{fy-20}" stroke="{GRAY}" '
         f'stroke-width="1.4" stroke-opacity="0.5"/>')
b.append(ltext(M, fy + 4,
               f"{TOTAL_RUNS} runs  ·  {TOTAL_ROUNDS} selection rounds  ·  "
               f"{TOTAL_ROWS} experiments  ·  5 families  ·  one column changed at a time",
               14.5, GRAY))
b.append(ltext(W - M, fy + 4, "two forward-test experiments sit outside this corpus",
               12.5, GRAY, anchor="end"))

H = fy + 24

svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H:.0f}" '
       f'font-family="{FONT}">\n<rect width="{W}" height="{H:.0f}" fill="white"/>\n'
       + "\n".join(b) + "\n</svg>")

with open(os.path.join(HERE, "run-inventory.svg"), "w") as fh:
    fh.write(svg)
print(f"wrote run-inventory.svg  {W} x {round(H)}  ·  {TOTAL_ROWS} cell rows, {TOTAL_RUNS} runs")
