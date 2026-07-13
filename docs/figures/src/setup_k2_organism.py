#!/usr/bin/env python3
"""Draft figure: how the K2 conservative-organism was built.

SETUP / methods figure — the OLMo-3-7B-Instruct install arc that produced the
frozen conservative judge K2 uses (condition frozen_cons_r0 in
fig17_loop_integrator). Six behavior-format ladders (v2-v6) never moved the
model's own judging taste; four judge-format ladders (v7-v10) did, ending in
the organism K2 freezes as its judge.

All numbers are read from the general-thread decision log in docs/PLAN.md
(search "v7 / v8 / v9 / v10 / cautious_judge_pref / mixed_judge") and
docs/STATE.md's mirrored entries, cross-checked against the two upstream
figure drafts that already cover pieces of this arc
(docs/figures/auto/olmo-taste-inertness/, docs/figures/auto/judge-channel-install/)
and docs/report_loop_integrator_decomposition.md (which names frozen_cons_r0
as the frozen conservative judge condition K2's trajectory analysis runs on).
No result file backs this arc (it is a Colab/Kaggle install log, not a saved
JSON) — every number below is a decision-log transcription, not a re-derived
statistic; this generator has no data-loading step for that reason.

Regenerate with: python3 setup-k2-organism.py   (from this directory; stdlib only)
"""
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = HERE
while ROOT != os.path.dirname(ROOT) and not os.path.isdir(os.path.join(ROOT, "experiments")):
    ROOT = os.path.dirname(ROOT)
FIGDIR = os.path.dirname(HERE) if os.path.basename(HERE) == "src" else HERE

INK = "#1a1a1a"
BLUE = "#2867b5"      # the judging-taste readout while it is being installed
GREEN = "#3a7d44"     # the organism that lands and is frozen as K2's judge
RED = "#b5342c"       # gate / screen failures, dead ends
GRAY = "#6b7684"      # taste-inert behavior-format ladders, recessive text
AMBER = "#9a6b15"     # instrument-lesson callout (explicitly not a headline finding)
KEY_FILL = "#eef5ee"
AMBER_FILL = "#faf1de"
GRAY_FILL = "#f2f2f0"

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


def rich_text(x, y, segments, size, width, lh=1.36, weight="normal"):
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


def text_block(x, y, text, size, width, color=INK, weight="normal", lh=1.36):
    return rich_text(x, y, [(text, color, weight == "bold")], size, width, lh)


def centered(svg_text):
    return svg_text.replace('<text ', '<text text-anchor="middle" ', 1)


def box(x, y, w, h, fill, stroke=INK, sw=2.5, rx=8):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')


def svg_doc(w, h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
            f'font-family="{FONT}">\n<rect width="{w}" height="{h}" fill="white"/>\n'
            f'{body}\n</svg>')


def arrow(x1, y1, x2, y2, color=INK, sw=3.5, head=11):
    ang = math.atan2(y2 - y1, x2 - x1)
    bx, by = x2 - head * math.cos(ang), y2 - head * math.sin(ang)
    px, py = -math.sin(ang), math.cos(ang)
    hw = head * 0.62
    pts = f"{x2:.1f},{y2:.1f} {bx + px * hw:.1f},{by + py * hw:.1f} {bx - px * hw:.1f},{by - py * hw:.1f}"
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{bx:.1f}" y2="{by:.1f}" '
            f'stroke="{color}" stroke-width="{sw}" stroke-linecap="round"/>'
            f'<polygon points="{pts}" fill="{color}"/>')


def elbow(x1, y1, x2, y2, mid_y, color=INK, sw=4):
    """Down from (x1,y1), across at mid_y, then down into (x2,y2) with an arrowhead."""
    seg = (f'<polyline points="{x1:.1f},{y1:.1f} {x1:.1f},{mid_y:.1f} {x2:.1f},{mid_y:.1f}" '
           f'fill="none" stroke="{color}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round"/>')
    return seg + arrow(x2, mid_y, x2, y2, color, sw)


def badge(cx, cy, num, color=INK):
    return (f'<circle cx="{cx}" cy="{cy}" r="15" fill="{color}"/>'
            f'<text x="{cx}" y="{cy + 5.5}" text-anchor="middle" font-size="15" '
            f'font-weight="bold" fill="white" font-family="{FONT}">{num}</text>')


def cw(px, size):
    """approx characters that fit in px at this font size (Helvetica-ish)."""
    return max(12, int(px / (0.52 * size)))


# ---------------------------------------------------------------- canvas
W = 1520
b = []

y = 46
t, y = text_block(W // 2, y, "Installing a conservative JUDGE meant training the judging channel directly —", 27, 78, weight="bold")
b.append(centered(t))
t, y = text_block(W // 2, y + 4, "behavior-format training left the judge's taste inert", 27, 68, weight="bold")
b.append(centered(t))
y += 14
t, y = text_block(W // 2, y, "The K2 conservative-organism install arc on allenai/Olmo-3-7B-Instruct — six behavior-format "
                  "ladders (v2–v6), then four judge-format ladders (v7–v10). General-thread decision log, "
                  "2026-07-11 (docs/PLAN.md, docs/STATE.md) — this organism becomes the frozen conservative "
                  "judge in K2's trajectory analysis (fig17).", 15.5, 148, GRAY)
b.append(centered(t))
y += 22

t, y = text_block(60, y, "The install arc: behavior-format ladders (taste-inert) → judge-format ladders "
                  "(taste installs) → K2's frozen judge", 19.5, 140, weight="bold")
b.append(t)
y += 20

# ================================================================= cards
GAP = 30
BOX_W = (1400 - 2 * GAP) // 3
XS = [60, 60 + BOX_W + GAP, 60 + 2 * (BOX_W + GAP)]
ROW1_Y, ROW1_H = y, 268
ROW2_Y, ROW2_H = ROW1_Y + ROW1_H + 96, 300
PAD = 20


def card(idx, x, y, w, h, title, subtitle, seg_lines, fill=None, border=INK, sw=2.5, tag=None, tag_color=None):
    fill = fill or "white"
    b.append(box(x, y, w, h, fill, border, sw))
    b.append(badge(x + 2, y + 2, idx, border if border != INK else INK))
    ty = y + 30
    t, ty = text_block(x + PAD + 16, ty, title, 18.5, cw(w - PAD * 2 - 16, 18.5), INK, weight="bold")
    b.append(t)
    if subtitle:
        t, ty = text_block(x + PAD, ty + 6, subtitle, 13, cw(w - PAD * 2, 13), GRAY)
        b.append(t)
    ty += 8
    for segs, size in seg_lines:
        t, ty = rich_text(x + PAD, ty, segs, size, cw(w - PAD * 2, size))
        b.append(t)
        ty += 4
    if tag:
        tw = 14 + 7.3 * len(tag)
        b.append(f'<rect x="{x + w - tw - 14}" y="{y - 13}" width="{tw}" height="24" rx="12" '
                  f'fill="{tag_color}" stroke="{tag_color}" stroke-width="1.5"/>')
        b.append(f'<text x="{x + w - tw / 2 - 14}" y="{y + 3.5}" text-anchor="middle" font-size="12.5" '
                  f'font-weight="bold" fill="white" font-family="{FONT}">{esc(tag)}</text>')


# --- Row 1 -----------------------------------------------------------
card(1, XS[0], ROW1_Y, BOX_W, ROW1_H,
     "OLMo-3-7B-Instruct — native",
     "before any conservative-judge training",
     [
         ([("forced-choice risk 0.723", INK, True), ("· generated-choice risk ≈ 0.62–0.65 "
           "(24-sample reads, rung to rung)", INK, False)], 14.5),
         ([("judging-taste readout (judge_taste_bold / cautious_judge_pref) 0.49–0.53", BLUE, True),
           (" — near indifferent, 0.5 = no preference.", INK, False)], 14.5),
     ])

card(2, XS[1], ROW1_Y, BOX_W, ROW1_H,
     "Behavior-format ladders v2–v6",
     "letter targets · rationale targets · mixed 1:1 recipes — train the model's OWN gamble answers",
     [
         ([("Generated risk swept 0.62→0.04 (letter-only, rate 1.0); forced risk plateaued "
            "≈0.55–0.58 under every non-destructive recipe.", INK, False)], 13.5),
         ([("Held-out judging-taste readouts stayed flat 0.512–0.532 at EVERY rung of v3, v5, v6.", GRAY, True)], 13.5),
         ([("Screen on v6_mixed_strict rung_20: ", INK, False),
           ("“kept-mean separation exactly 0.000 — pool 101 gaps −0.083/−0.083, "
            "pool 202 gaps 0.000/0.000”.", RED, True)], 13.5),
         ([("Behavior training never touches the judging channel.", RED, True)], 14.5),
     ],
     fill=GRAY_FILL, border=GRAY, tag="TASTE-INERT", tag_color=RED)

card(3, XS[2], ROW1_Y, BOX_W, ROW1_H,
     "v7 — judge-format rows added",
     "TARGET_STYLE mixed_judge — 1:1:1 rationale : letter : judge rows",
     [
         ([("held-out cautious_judge_pref: 0.426 (native) → 0.549 (rung 20) → 0.726 (rung 40) "
            "→ 0.927 (rung 60)", BLUE, True)], 14.5),
         ([("— a clean dose-response on exactly the coordinate the behavior ladders left flat. "
            "Generic advice-pair taste stays flat (≈0.53): the install is domain-specific "
            "gamble judging.", INK, False)], 13.5),
         ([("No valid all-gates rung: forced order gap 0.20–0.29 (needs ≤0.10); generated "
            "channel overshoots down to 0.083 by rung 60 (below the 0.15 band floor).", RED, True)], 13.5),
     ],
     border=BLUE, tag="DOSE CONFIRMED, NO GATE", tag_color=AMBER)

# arrows within row 1
b.append(arrow(XS[0] + BOX_W + 4, ROW1_Y + ROW1_H / 2, XS[1] - 4, ROW1_Y + ROW1_H / 2, INK, sw=4))
b.append(arrow(XS[1] + BOX_W + 4, ROW1_Y + ROW1_H / 2, XS[2] - 4, ROW1_Y + ROW1_H / 2, INK, sw=4))

# --- connector row1 -> row2 (elbow, stays inside the gap band) --------
GAP_MID = ROW1_Y + ROW1_H + (ROW2_Y - (ROW1_Y + ROW1_H)) / 2
b.append(elbow(XS[2] + BOX_W * 0.5, ROW1_Y + ROW1_H + 10, XS[0] + BOX_W * 0.5, ROW2_Y - 10, GAP_MID, INK, sw=4))
t, _ = text_block(XS[0] + BOX_W * 0.5, GAP_MID - 8, "continued", 13, 20, GRAY)
b.append(centered(t))

# --- Row 2 -------------------------------------------------------------
card(4, XS[0], ROW2_Y, BOX_W, ROW2_H,
     "v8 — mixed_judge2, rung_60",
     "1:2:1 rationale : letter : judge (restores v6's letter density)",
     [
         ([("ALL SEVEN organism gates PASS:", INK, True)], 14.5),
         ([("forced 0.723→0.590 (order gap 0.025), generated 0.632→0.478, invalid 0.042, "
            "factual 0.500→0.625, judge_pref 0.426→0.686 (+0.260).", INK, False)], 13.5),
         ([("Strict two-pool inversion screen: ", INK, False),
           ("“sign replicated, separation ~0” — FAIL.", RED, True)], 14.5),
     ],
     border=RED, tag="SCREEN FAIL", tag_color=RED)

card(5, XS[1], ROW2_Y, BOX_W, ROW2_H,
     "v9 — mixed_judge3",
     "ref-pair judge rows, tried to raise the screen's separation",
     [
         ([("Judge readout moves SLOWER: +0.11 shift by rung 60 vs v8's +0.26 — diluting judge "
            "rows across two pair formats cuts the per-format dose.", INK, False)], 13.5),
         ([("Forced order gap never re-enters ≤0.10 after rung 10 (wanders 0.11–0.29 across "
            "rungs, non-monotonic).", INK, False)], 13.5),
         ([("LADDER EXHAUSTED — no valid all-gates rung at any dose.", RED, True)], 14.5),
     ],
     border=RED, tag="EXHAUSTED", tag_color=RED)

card(6, XS[2], ROW2_Y, BOX_W, ROW2_H,
     "v10 — judge-only top-up",
     "STARTING FROM v8/rung_60 — 100% judge rows, template + reference pairs, +10..+80 cumulative",
     [
         ([("rung_20 (20 steps, 13 min): ALL GATES PASS — cautious_judge_pref 0.880 (up from "
            "v8's 0.686), forced 0.723→0.536 (order gap 0.023), generated 0.364 in band, "
            "invalid 0.083.", GREEN, True)], 13.5),
         ([("“5-POOL SCREEN VERDICT — PASS under both rules”: separations "
            "[+0.021, +0.167, +0.167, +0.167, −0.021], mean 0.100 (sd 0.093), conservative-judge "
            "gap negative in 5/5 pools.", GREEN, True)], 13.5),
         ([("→ frozen as K2's conservative judge (condition frozen_cons_r0).", GREEN, True)], 14.5),
     ],
     border=GREEN, sw=4, tag="FROZEN AS K2's JUDGE", tag_color=GREEN)

# arrows within row 2
b.append(arrow(XS[0] + BOX_W + 4, ROW2_Y + ROW2_H / 2, XS[1] - 4, ROW2_Y + ROW2_H / 2, INK, sw=4))
b.append(arrow(XS[1] + BOX_W + 4, ROW2_Y + ROW2_H / 2, XS[2] - 4, ROW2_Y + ROW2_H / 2, INK, sw=4))

# ================================================================= B: taste trajectory strip
SY = ROW2_Y + ROW2_H + 34
SH = 214
b.append(box(60, SY, 1400, SH, "white", INK, 1.5))
t, ty = text_block(80, SY + 26, "B. The judging-taste readout across the arc — held-out cautious_judge_pref "
                    "(or its behavior-ladder analogue judge_taste_bold), 0.5 = indifferent", 15.5, 148, weight="bold")
b.append(t)

TX0, TX1, TY = 130, 1330, SY + 88
b.append(f'<line x1="{TX0}" y1="{TY}" x2="{TX1}" y2="{TY}" stroke="{INK}" stroke-width="2"/>')
for v in (0.0, 0.25, 0.5, 0.75, 1.0):
    xx = TX0 + (TX1 - TX0) * v
    b.append(f'<line x1="{xx:.1f}" y1="{TY - 5}" x2="{xx:.1f}" y2="{TY + 5}" stroke="{INK}" stroke-width="1.5"/>')
    b.append(f'<text x="{xx:.1f}" y="{TY + 24}" text-anchor="middle" font-size="13" fill="{GRAY}" font-family="{FONT}">{v:.2f}</text>')


def tx(v):
    return TX0 + (TX1 - TX0) * v


# flat band for v2-v6 (taste-inert), label sits above it, clear of every point marker
b.append(f'<rect x="{tx(0.49):.1f}" y="{TY - 30}" width="{tx(0.53) - tx(0.49):.1f}" height="16" '
          f'fill="{GRAY}" fill-opacity="0.30"/>')
t, _ = text_block(tx(0.49) - 6, TY - 40, "v2–v6 flat 0.49–0.53", 12.5, 40, GRAY)
b.append(t)

# points on the axis (no attached text labels — legend below carries the reading)
POINTS = [
    (0.426, INK, True),    # native
    (0.549, BLUE, False),  # v7 rung 20
    (0.726, BLUE, False),  # v7 rung 40
    (0.927, BLUE, False),  # v7 rung 60 (no valid rung)
    (0.686, RED, True),    # v8 rung 60 (screen FAIL)
    (0.536, RED, False),   # v9 best partial dose (exhausted)
    (0.880, GREEN, True),  # v10 rung 20 -> frozen as K2's judge
]
for v, col, filled in POINTS:
    xx = tx(v)
    if filled:
        b.append(f'<circle cx="{xx:.1f}" cy="{TY}" r="7.5" fill="{col}" stroke="white" stroke-width="1.5"/>')
    else:
        b.append(f'<circle cx="{xx:.1f}" cy="{TY}" r="7" fill="white" stroke="{col}" stroke-width="2.5" '
                  f'stroke-dasharray="3,2"/>')

# legend: filled/hollow marker meaning, one row per install stage, two columns
LEGEND = [
    (INK, True, "native 0.426 — before any conservative-judge training"),
    (BLUE, False, "v7 rungs 20/40/60 = 0.549 / 0.726 / 0.927 — dose-response confirmed, no valid all-gates rung"),
    (RED, True, "v8 rung_60 = 0.686 — ALL SEVEN organism gates pass; strict inversion screen FAILS (separation ~0)"),
    (RED, False, "v9 best partial dose ≈ 0.536 — ladder exhausted, no valid all-gates rung at any dose"),
    (GREEN, True, "v10 rung_20 = 0.880 — all gates pass + 5-pool inversion screen PASS → frozen as K2's judge"),
]
ly = TY + 46
for col, filled, label in LEGEND:
    if filled:
        b.append(f'<circle cx="{TX0 + 6}" cy="{ly - 5}" r="6.5" fill="{col}"/>')
    else:
        b.append(f'<circle cx="{TX0 + 6}" cy="{ly - 5}" r="6" fill="white" stroke="{col}" stroke-width="2.2" stroke-dasharray="2.5,2"/>')
    t, _ = text_block(TX0 + 22, ly, label, 13.5, cw(1220, 13.5), INK)
    b.append(t)
    ly += 22

y = SY + SH + 34

# ================================================================= instrument lesson (AMBER)
IY = y
IH = 132
b.append(box(60, IY, 1400, IH, AMBER_FILL, AMBER, 2.5))
t, ty = rich_text(80, IY + 30, [
    ("Instrument lesson, not a headline result", AMBER, True),
    (" (explicitly demoted 2026-07-11 by user correction, PLAN decision log): a TRIPLE DISSOCIATION — "
     "you move the channel you train.", INK, False),
], 16.5, 150)
b.append(t)
t, ty = rich_text(80, ty + 10, [
    ("Letter-format targets move the FORCED channel", BLUE, True),
    (" (position-forced A/B choice); ", INK, False),
    ("rationale targets move the GENERATED channel", BLUE, True),
    (" (free-generation choice); ", INK, False),
    ("judge-format rows (v7–v10) move the JUDGING channel", GREEN, True),
    (" (preference over OTHER answers) — none of the behavior-format recipes above ever moved that "
     "third channel, however hard the generated channel swung.", INK, False),
], 14.5, 154)
b.append(t)

y = IY + IH + 26

# ================================================================= takeaway (KEY_FILL)
KY = y
KH = 190
b.append(box(60, KY, 1400, KH, KEY_FILL, INK, 2.5))
t, _ = rich_text(80, KY + 32, [
    ("Read as a setup result, not a discovery: ", INK, True),
    ("installing a conservative JUDGE required training rows shaped like the judge's own verdict, not "
     "just a more risk-averse generator. Six behavior-format ladders (v2–v6) swept the organism's "
     "own gamble answers by 0.58 (generated risk 0.62→0.04) while its judgment of OTHER candidates' "
     "answers never moved (0.49–0.53, screen separation exactly 0.000). Four judge-format ladders "
     "(v7→v8→v9→v10) moved that same coordinate 0.426→0.880 and produced the organism "
     "(v10, rung_20, judge-only top-up from v8/rung_60) that passed K2's final 5-pool inversion screen "
     "(mean separation 0.100, sd 0.093, conservative-judge gap negative in 5/5 pools) — this is the "
     "frozen conservative judge (condition frozen_cons_r0) the K2 trajectory analysis "
     "(fig17_loop_integrator) runs on.", INK, False),
], 17, 128)
b.append(t)

H = KY + KH + 30
svg = svg_doc(W, H, "\n".join(b))
out = os.path.join(FIGDIR, "setup_k2_organism.svg")
with open(out, "w") as f:
    f.write(svg)
print(f"wrote {out}  ({W}x{H})")
