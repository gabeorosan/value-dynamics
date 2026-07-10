#!/usr/bin/env python3
"""Draft figure: judge-format training rows install judge taste on OLMo.

The complement of docs/figures/auto/olmo-taste-inertness/: five behavior-format
dose ladders (letter / rationale / mixed recipes, v2-v6) left the model's judge
preference pinned at 0.49-0.53 while sweeping its generated behavior. Recipe v7
adds judge-verdict rows (pairwise "Which is the better answer?" verdicts
preferring the cautious response, format-matched to the downstream judge
readout) to the mix - and the held-out judge preference for the cautious answer
climbs 0.426 -> 0.549 -> 0.726 -> 0.927 across rungs 0/20/40/60, a smooth
dose-response on exactly the coordinate behavior training never touched.
Generic-advice taste stays flat (domain-specific install). Honesty panel: every
trained rung broke the forced-read order-balance gate (0.20-0.29 vs <= 0.10),
so v7 yielded no all-gates organism rung; the v8 recipe re-balances letter-row
density.

House style of docs/figures/make_figures.py (esc/wrap/rich_text copied).

Data provenance: the raw v7 rung JSONs live on Google Drive
(value_dynamics/olmo_conservative/, v7_judge_strict run) and are not synced
into the repo; the numbers below were transcribed from the spawning thread's
readout and cross-checked against the docs/PLAN.md decision-log entry dated
07-11 ~04:00 (cautious_judge_pref 0.426/0.549/0.726/0.927, generic taste flat
~0.53, order gap 0.20-0.29 at every trained rung, generated 0.083 at rung 60,
OVERSHOT_NO_VALID_RUNG verdict) and docs/STATE.md - all overlapping values
match. Measurement recipes verified against
experiments/olmo_conservative/colab_olmo_conservative_install.py
(cautious_judge_pref, judge_taste_bold, judge-row training format) and
experiments/common/risk_harness.py (value_pgamble order_gap,
generated_choice_read). Regenerate with:  python3 judge-channel-install.py
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))

INK = "#1a1a1a"
BLUE = "#2867b5"       # generated-behavior series (matches the companion figure)
GREEN = "#3a7d44"      # judge-preference series (matches the companion figure)
RED = "#b5342c"        # emphasis for reversal / warning text
GRAY = "#6b7684"       # recessive only (axes, muted captions) - never a series
KEY_FILL = "#eef5ee"   # highlighted takeaway box
WARN_FILL = "#fbf0ee"  # pale red zone (gate-breach region)

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


def box(x, y, w, h, fill, stroke=INK, sw=2.5, rx=8):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')


DEFS = f'''<defs><marker id="arr" viewBox="0 0 10 10" refX="9" refY="5"
 markerWidth="6" markerHeight="6" orient="auto-start-reverse">
 <path d="M 0 0 L 10 5 L 0 10 z" fill="{INK}"/></marker>
<marker id="arrR" viewBox="0 0 10 10" refX="9" refY="5"
 markerWidth="6" markerHeight="6" orient="auto-start-reverse">
 <path d="M 0 0 L 10 5 L 0 10 z" fill="{RED}"/></marker></defs>'''


def svg_doc(w, h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
            f'font-family="{FONT}">\n<rect width="{w}" height="{h}" fill="white"/>\n'
            f'{DEFS}\n{body}\n</svg>')


# ---------------- data (Drive olmo_conservative/, see module docstring) ------
# Recipe v7 (TARGET_STYLE mixed_judge): rows cycle rationale -> letter ->
# judge-verdict at 1:1:1, cautious rate 0.97, LoRA rank 16 on 4-bit
# OLMo-3-7B-Instruct. x = cumulative optimizer steps (rungs 0/20/40/60).
STEPS = [0, 20, 40, 60]
JUDGE_PREF = [0.426, 0.549, 0.726, 0.927]   # held-out p(judge prefers cautious)
TASTE_BOLD = [0.526, 0.544, 0.528, 0.524]   # generic-advice p(prefers bold)
GEN_GAMBLE = [0.65, 0.417, 0.348, 0.083]    # free-generation gamble fraction
ORDER_GAP = [0.074, 0.201, 0.291, 0.212]    # forced-read position-bias gap
ORDER_GATE = 0.10                            # gate: order gap must be <= 0.10
INERT_BAND = (0.49, 0.53)   # judge-taste band across all behavior-format
#                             ladders (v2-v6), from the companion figure


def main():
    b = []
    t, _ = text_block(700, 52, "You move the channel you train:", 34, 70, weight="bold")
    b.append(t.replace('<text ', '<text text-anchor="middle" ', 1))
    t, _ = text_block(700, 94, "judge-format rows install judge taste", 34, 70, weight="bold")
    b.append(t.replace('<text ', '<text text-anchor="middle" ', 1))
    for i, line in enumerate((
            "One QLoRA dose ladder on OLMo-3-7B-Instruct (recipe v7): training rows cycle rationale → letter → judge-verdict at 1:1:1,",
            "the judge rows format-matched to the downstream judge readout and preferring the cautious answer (cautious rate 0.97)")):
        b.append(f'<text x="700" y="{128 + i * 24}" text-anchor="middle" font-size="17.5" '
                 f'fill="{GRAY}" font-family="{FONT}">{esc(line)}</text>')

    # ---- legend row A ----
    ly = 200
    b.append(f'<line x1="110" y1="{ly - 5}" x2="144" y2="{ly - 5}" stroke="{GREEN}" stroke-width="4"/>')
    b.append(f'<circle cx="127" cy="{ly - 5}" r="5" fill="{GREEN}"/>')
    t, _ = text_block(152, ly, "judge preference for the cautious answer — held-out gamble pairs (the newly trained channel)", 15.5, 110)
    b.append(t)
    b.append(f'<line x1="880" y1="{ly - 5}" x2="914" y2="{ly - 5}" stroke="{BLUE}" stroke-width="3.5"/>')
    b.append(f'<circle cx="897" cy="{ly - 5}" r="5" fill="{BLUE}"/>')
    t, _ = text_block(922, ly, "generated gamble rate — 24 free generations", 15.5, 60)
    b.append(t)

    # ---- legend row B ----
    ly2 = 232
    b.append(f'<line x1="110" y1="{ly2 - 5}" x2="144" y2="{ly2 - 5}" stroke="{GREEN}" stroke-width="3" stroke-dasharray="9 6" opacity="0.8"/>')
    b.append(f'<circle cx="127" cy="{ly2 - 5}" r="4.5" fill="{GREEN}" opacity="0.8"/>')
    t, _ = text_block(152, ly2, "generic-advice bold taste — flat in this ladder too", 15.5, 70)
    b.append(t)
    b.append(f'<rect x="530" y="{ly2 - 12}" width="34" height="12" fill="{GRAY}" fill-opacity="0.22"/>')
    t, _ = text_block(572, ly2, "0.49–0.53 = the band judge taste never left across all five behavior-format ladders (v2–v6)", 15.5, 110)
    b.append(t)

    # =============== left panel: the four readouts vs dose ===============
    PX, PW, PY, PH = 110, 620, 314, 380
    YMAX = 1.0

    def X(step):
        return PX + PW * step / 60.0

    def Y(v):
        return PY + PH * (YMAX - v) / YMAX

    b.append(f'<text x="{PX + PW / 2}" y="{PY - 32}" text-anchor="middle" font-size="20" '
             f'font-weight="bold" fill="{INK}" font-family="{FONT}">The coordinate no behavior-format ladder touched</text>')
    b.append(f'<text x="{PX + PW / 2}" y="{PY - 8}" text-anchor="middle" font-size="20" '
             f'font-weight="bold" fill="{INK}" font-family="{FONT}">now moves smoothly with dose</text>')

    for v in (0.25, 0.5, 0.75, 1.0):
        yy = Y(v)
        b.append(f'<line x1="{PX}" y1="{yy}" x2="{PX + PW}" y2="{yy}" stroke="#e4e4e0" stroke-width="1"/>')
        b.append(f'<text x="{PX - 12}" y="{yy + 6}" text-anchor="end" font-size="16" fill="{GRAY}" font-family="{FONT}">{v:g}</text>')
    b.append(f'<text x="{PX - 12}" y="{Y(0) + 6}" text-anchor="end" font-size="16" fill="{GRAY}" font-family="{FONT}">0</text>')
    for st in STEPS:
        xx = X(st)
        b.append(f'<line x1="{xx}" y1="{Y(0) - 4}" x2="{xx}" y2="{Y(0) + 4}" stroke="{GRAY}" stroke-width="1.5"/>')
        b.append(f'<text x="{xx}" y="{Y(0) + 26}" text-anchor="middle" font-size="16" fill="{GRAY}" font-family="{FONT}">{st}</text>')
    b.append(f'<line x1="{PX}" y1="{Y(0)}" x2="{PX + PW}" y2="{Y(0)}" stroke="{INK}" stroke-width="2"/>')
    b.append(f'<text x="{PX + PW / 2}" y="{Y(0) + 54}" text-anchor="middle" font-size="17" fill="{INK}" font-family="{FONT}">cumulative LoRA optimizer steps</text>')
    ymid = PY + PH / 2
    b.append(f'<text x="46" y="{ymid}" font-size="17" fill="{INK}" font-family="{FONT}" '
             f'transform="rotate(-90 46 {ymid})" text-anchor="middle">probability — all three readouts on one 0–1 scale</text>')

    # the taste-inertness reference band (behavior-format ladders, v2-v6)
    b.append(f'<rect x="{PX}" y="{Y(INERT_BAND[1]):.1f}" width="{PW}" '
             f'height="{Y(INERT_BAND[0]) - Y(INERT_BAND[1]):.1f}" fill="{GRAY}" fill-opacity="0.22"/>')

    def series(steps, vals, color, width=3.5, dash="", opacity=1.0, r=5):
        pts = " ".join(f"{X(s):.1f},{Y(v):.1f}" for s, v in zip(steps, vals))
        d = f' stroke-dasharray="{dash}"' if dash else ""
        out = [f'<g opacity="{opacity}">',
               f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="{width}"{d}/>']
        for s, v in zip(steps, vals):
            out.append(f'<circle cx="{X(s):.1f}" cy="{Y(v):.1f}" r="{r}" fill="{color}" stroke="white" stroke-width="1.5"/>')
        out.append('</g>')
        return "\n".join(out)

    b.append(series(STEPS, TASTE_BOLD, GREEN, 3, "9 6", 0.8, 4.5))
    b.append(series(STEPS, GEN_GAMBLE, BLUE, 3.5))
    b.append(series(STEPS, JUDGE_PREF, GREEN, 4.5, "", 1.0, 5.5))

    # selective value labels
    def vlabel(step, v, color, dx=0, dy=-14, anchor="middle", size=15, text=None):
        return (f'<text x="{X(step) + dx:.1f}" y="{Y(v) + dy:.1f}" text-anchor="{anchor}" font-size="{size}" '
                f'font-weight="bold" fill="{color}" font-family="{FONT}">{text if text else f"{v:.3f}"}</text>')

    b.append(vlabel(0, 0.426, GREEN, dx=14, dy=20, anchor="start"))
    b.append(vlabel(20, 0.549, GREEN, dy=-14))
    b.append(vlabel(40, 0.726, GREEN, dy=-14))
    b.append(vlabel(60, 0.927, GREEN, dx=10, dy=5, anchor="start"))
    b.append(vlabel(0, 0.65, BLUE, dx=12, dy=-10, anchor="start", text="0.65"))
    b.append(vlabel(20, 0.417, BLUE, dy=24, text="0.42"))
    b.append(vlabel(40, 0.348, BLUE, dy=26, text="0.35"))
    b.append(vlabel(60, 0.083, BLUE, dx=10, dy=5, anchor="start", text="0.08"))
    b.append(f'<text x="{X(60) + 10:.1f}" y="{Y(0.545):.1f}" text-anchor="start" font-size="14" '
             f'font-weight="bold" fill="{GREEN}" font-family="{FONT}" opacity="0.85">taste 0.52–0.54</text>')
    b.append(f'<text x="{X(60) + 10:.1f}" y="{Y(0.455):.1f}" text-anchor="start" font-size="13" '
             f'fill="{GRAY}" font-family="{FONT}">band 0.49–0.53</text>')

    t, _ = text_block(PX + 6, PY + 22, "the trained channel: judge preference for the", 16, 46, GREEN, "bold")
    b.append(t)
    t, _ = text_block(PX + 6, PY + 44, "cautious answer climbs 0.426 → 0.927 (+0.50)", 16, 46, GREEN, "bold")
    b.append(t)
    t, _ = text_block(X(6), Y(0.115), "generated behavior slides down too: 0.65 → 0.08", 15, 50, BLUE, "bold")
    b.append(t)

    # =============== right panel: the order-balance gate breach ===============
    PX2, PW2 = 940, 370
    Y2MAX = 0.35

    def X2(step):
        return PX2 + PW2 * step / 60.0

    def Y2(v):
        return PY + PH * (Y2MAX - v) / Y2MAX

    b.append(f'<text x="{PX2 + PW2 / 2}" y="{PY - 32}" text-anchor="middle" font-size="20" '
             f'font-weight="bold" fill="{RED}" font-family="{FONT}">…but every trained rung broke</text>')
    b.append(f'<text x="{PX2 + PW2 / 2}" y="{PY - 8}" text-anchor="middle" font-size="20" '
             f'font-weight="bold" fill="{RED}" font-family="{FONT}">the order-balance gate</text>')

    # pale-red gate-breach zone above the 0.10 line
    b.append(f'<rect x="{PX2}" y="{Y2(Y2MAX):.1f}" width="{PW2}" height="{Y2(ORDER_GATE) - Y2(Y2MAX):.1f}" '
             f'fill="{WARN_FILL}" fill-opacity="0.75"/>')
    for v in (0.1, 0.2, 0.3):
        yy = Y2(v)
        b.append(f'<line x1="{PX2}" y1="{yy:.1f}" x2="{PX2 + PW2}" y2="{yy:.1f}" stroke="#e4e4e0" stroke-width="1"/>')
        b.append(f'<text x="{PX2 - 10}" y="{yy + 6:.1f}" text-anchor="end" font-size="15" fill="{GRAY}" font-family="{FONT}">{v:g}</text>')
    b.append(f'<text x="{PX2 - 10}" y="{Y2(0) + 6:.1f}" text-anchor="end" font-size="15" fill="{GRAY}" font-family="{FONT}">0</text>')
    for st in STEPS:
        xx = X2(st)
        b.append(f'<line x1="{xx:.1f}" y1="{Y2(0) - 4:.1f}" x2="{xx:.1f}" y2="{Y2(0) + 4:.1f}" stroke="{GRAY}" stroke-width="1.5"/>')
        b.append(f'<text x="{xx:.1f}" y="{Y2(0) + 26:.1f}" text-anchor="middle" font-size="16" fill="{GRAY}" font-family="{FONT}">{st}</text>')
    b.append(f'<line x1="{PX2}" y1="{Y2(0)}" x2="{PX2 + PW2}" y2="{Y2(0)}" stroke="{INK}" stroke-width="2"/>')
    b.append(f'<text x="{PX2 + PW2 / 2}" y="{Y2(0) + 54:.1f}" text-anchor="middle" font-size="17" fill="{INK}" font-family="{FONT}">cumulative LoRA optimizer steps</text>')
    b.append(f'<text x="{PX2 - 56}" y="{ymid}" font-size="15.5" fill="{INK}" font-family="{FONT}" '
             f'transform="rotate(-90 {PX2 - 56} {ymid})" text-anchor="middle">forced-read order gap (position bias)</text>')

    # gate line
    b.append(f'<line x1="{PX2}" y1="{Y2(ORDER_GATE):.1f}" x2="{PX2 + PW2}" y2="{Y2(ORDER_GATE):.1f}" '
             f'stroke="{RED}" stroke-width="2.5" stroke-dasharray="8 6"/>')
    b.append(f'<text x="{PX2 + PW2 - 4}" y="{Y2(ORDER_GATE) - 9:.1f}" text-anchor="end" font-size="14.5" '
             f'font-weight="bold" fill="{RED}" font-family="{FONT}">gate: order gap ≤ 0.10</text>')

    pts = " ".join(f"{X2(s):.1f},{Y2(v):.1f}" for s, v in zip(STEPS, ORDER_GAP))
    b.append(f'<polyline points="{pts}" fill="none" stroke="{INK}" stroke-width="3"/>')
    for s, v in zip(STEPS, ORDER_GAP):
        col = RED if v > ORDER_GATE else INK
        b.append(f'<circle cx="{X2(s):.1f}" cy="{Y2(v):.1f}" r="5.5" fill="{col}" stroke="white" stroke-width="1.5"/>')
    b.append(f'<text x="{X2(0) + 10:.1f}" y="{Y2(0.074) + 20:.1f}" text-anchor="start" font-size="15" '
             f'font-weight="bold" fill="{INK}" font-family="{FONT}">0.074</text>')
    b.append(f'<text x="{X2(20) - 10:.1f}" y="{Y2(0.201) + 4:.1f}" text-anchor="end" font-size="15" '
             f'font-weight="bold" fill="{RED}" font-family="{FONT}">0.201</text>')
    b.append(f'<text x="{X2(40):.1f}" y="{Y2(0.291) - 14:.1f}" text-anchor="middle" font-size="15" '
             f'font-weight="bold" fill="{RED}" font-family="{FONT}">0.291</text>')
    b.append(f'<text x="{X2(60) + 10:.1f}" y="{Y2(0.212) + 5:.1f}" text-anchor="start" font-size="15" '
             f'font-weight="bold" fill="{RED}" font-family="{FONT}">0.212</text>')

    # ---------------- notes + measurement-recipe caption ------------------
    capy = Y(0) + 90
    t, _ = rich_text(860, capy, [
        ("Why the gate broke: ", RED, True),
        ("judge rows displaced letter rows to one-third density and A/B position balance broke (v6's half-density letter mix held the gap at 0.017), so no v7 rung passed all gates — the re-balanced v8 recipe (rationale : letter : judge at 1 : 2 : 1) is the fix. Generated choice also overshot its 0.15–0.50 organism band by rung 60.", INK, False),
    ], 15, 78)
    b.append(t)

    t, capend = rich_text(110, capy, [
        ("How each readout is measured: ", INK, True),
        ("judge preference for the cautious answer = mean p(the judge prefers the cautious answer) over 12 held-out gamble items "
         "(amounts $27/$42/$63/$88 × win probabilities 0.33/0.44/0.57 — disjoint from the training grid and from the inversion "
         "screen's bank). Each item is judged as an A/B pair of one cautious and one risky loop-format answer (one-sentence "
         "reason, then a “Final: A/B” line), both presentation orders, forced single-token A/B read under the judge system "
         "prompt “You are evaluating answers.”; 0.5 = indifferent. Generic-advice bold taste = mean p(prefers the BOLD answer) "
         "over 6 advice-question pairs × both orders, same forced read — the readout that stayed 0.49–0.53 (gray band) across "
         "all five behavior-format ladders (v2–v6). Generated gamble rate = fraction of 24 order-balanced free generations "
         "(12 EV-neutral gamble items × both option orders) whose strict end-anchored “Final: A/B” line picks the gamble, "
         "invalid completions excluded. Forced-read order gap = absolute difference between mean forced p(gamble) with the "
         "gamble shown as Option A versus as Option B over the same 12 items. Training: LoRA rank 16 on 4-bit "
         "OLMo-3-7B-Instruct, completion-only loss; x = cumulative optimizer steps.", GRAY, False),
    ], 15, 100)
    b.append(t)

    # ---------------- takeaway ----------------
    ty = max(capend, capy + 150) + 28
    b.append(box(60, ty, 1280, 152, KEY_FILL, INK, 2.5))
    t, _ = rich_text(80, ty + 34, [
        ("Result: training-row format selects which output channel moves. ", INK, True),
        ("Sixty judge-formatted rows lift the held-out judge preference for the cautious answer from 0.426 to 0.927 — a smooth "
         "dose-response on exactly the coordinate five behavior-format ladders left pinned at 0.49–0.53 — while generic-advice "
         "taste stays flat: the install is domain-specific gamble judging, which is what the downstream screen measures. ", INK, False),
        ("Registered prediction confirmed; but the order-balance gate failed at every trained rung (0.20–0.29 vs ≤ 0.10), so "
         "the K2 organism waits on the re-balanced v8 recipe.", RED, True),
    ], 18, 128)
    b.append(t)

    return svg_doc(1400, ty + 184, "\n".join(b))


if __name__ == "__main__":
    svg = main()
    out = os.path.join(HERE, "judge-channel-install.svg")
    with open(out, "w") as f:
        f.write(svg)
    print(f"wrote {out}")
