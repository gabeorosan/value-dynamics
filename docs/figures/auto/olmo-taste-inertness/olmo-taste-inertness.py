#!/usr/bin/env python3
"""Draft figure: behavior-format training on OLMo-3-7B-Instruct is taste-inert.

Left panel: three cautious-persona QLoRA dose ladders sweep the model's own
generated gamble-choice rate across nearly its full range while its judge
preference (taste for the bold answer) never leaves 0.49-0.53. Right panel:
the downstream consequence — in the strict judge-inversion screen the
"conservative" organism (mixed recipe, step 20, behavior in band) selected
candidates exactly like the untrained base model: kept-set selection gaps
identical in both pools (separation 0.000 against a >= 0.10 gate).

House style of docs/figures/make_figures.py (esc/wrap/rich_text copied).

Data provenance: the raw rung and screen JSONs live on Google Drive
(value_dynamics/olmo_conservative/ — v3_strict_completion/, the v5 rationale
ladder, v6_mixed_strict/ incl. olmo_inversion_screen_strict.json) and are not
synced into the repo; the numbers below were transcribed from the spawning
thread's readout and cross-checked against docs/STATE.md entries dated
2026-07-10/11 (all overlapping values match; STATE.md quotes the taste band
as 0.51-0.53, which omits the single 0.492 rung of the overshot letter
ladder). Regenerate with:  python3 olmo-taste-inertness.py
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))

INK = "#1a1a1a"
BLUE = "#2867b5"       # generated-behavior series / trained-organism judge
GREEN = "#3a7d44"      # judge-taste series / frozen-base judge
RED = "#b5342c"        # emphasis for reversal / warning text
GRAY = "#6b7684"       # recessive only (axes, muted captions) — never a series
KEY_FILL = "#eef5ee"   # highlighted takeaway box

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
# Mixed letter+rationale targets, cautious rate 0.97 (recipe v6) — main series
V6_STEPS = [0, 20, 40, 60, 80, 120, 160]
V6_GEN = [0.619, 0.375, 0.167, 0.125, 0.042, 0.250, 0.042]
V6_TASTE = [0.526, 0.519, 0.515, 0.532, 0.524, 0.512, 0.516]

# Rationale targets, cautious rate 0.90 (recipe v5)
V5_STEPS = [0, 10, 20, 40, 80, 120]
V5_GEN = [0.714, 0.750, 0.583, 0.500, 0.292, 0.125]
V5_TASTE = [0.526, 0.529, 0.532, 0.524, 0.516, 0.519]

# Letter targets, cautious rate 1.00 (recipe v3) — ladder exited on overshoot
V3_STEPS = [0, 40]
V3_GEN = [0.522, 0.250]
V3_TASTE = [0.526, 0.492]

# Strict judge-inversion screen on the v6 step-20 organism:
# kept-set selection gap (kept mean minus pool mean p(gamble)) per judge, per pool
SCREEN = {  # pool seed -> (conservative-organism judge gap, frozen-base judge gap)
    101: (-0.083, -0.083),
    202: (0.000, 0.000),
}
GATE_SEPARATION = 0.10  # required |base gap minus conservative gap|


def main():
    b = []
    t, _ = text_block(700, 52, "Behavior training moves what the model does —", 34, 70, weight="bold")
    b.append(t.replace('<text ', '<text text-anchor="middle" ', 1))
    t, _ = text_block(700, 94, "not what it prefers as a judge", 34, 70, weight="bold")
    b.append(t.replace('<text ', '<text text-anchor="middle" ', 1))
    t, _ = text_block(700, 128, "Cautious-persona QLoRA dose ladders on OLMo-3-7B-Instruct, read at every rung on both coordinates; the untouched judging coordinate then failed the downstream judge-inversion gate", 17.5, 130, GRAY)
    b.append(t.replace('<text ', '<text text-anchor="middle" ', 1))

    # ---- legend row A: readout colors ----
    ly = 172
    b.append(f'<line x1="110" y1="{ly - 5}" x2="144" y2="{ly - 5}" stroke="{BLUE}" stroke-width="3.5"/>')
    b.append(f'<circle cx="127" cy="{ly - 5}" r="5" fill="{BLUE}"/>')
    t, _ = text_block(152, ly, "generated gamble rate — share of 24 free generations choosing the gamble", 15.5, 90)
    b.append(t)
    b.append(f'<line x1="760" y1="{ly - 5}" x2="794" y2="{ly - 5}" stroke="{GREEN}" stroke-width="3.5"/>')
    b.append(f'<circle cx="777" cy="{ly - 5}" r="5" fill="{GREEN}"/>')
    t, _ = text_block(802, ly, "judge taste — mean p(prefers the bold answer); 0.5 = indifferent", 15.5, 80)
    b.append(t)

    # ---- legend row B: line style = recipe ----
    ly2 = 206
    t, _ = text_block(110, ly2, "line style = training recipe:", 15.5, 40, GRAY, "bold")
    b.append(t)
    b.append(f'<line x1="312" y1="{ly2 - 5}" x2="346" y2="{ly2 - 5}" stroke="{INK}" stroke-width="3.5"/>')
    t, _ = text_block(354, ly2, "mixed letter+rationale targets, rate 0.97 (v6)", 15.5, 60)
    b.append(t)
    b.append(f'<line x1="720" y1="{ly2 - 5}" x2="754" y2="{ly2 - 5}" stroke="{INK}" stroke-width="3" stroke-dasharray="9 6"/>')
    t, _ = text_block(762, ly2, "rationale targets, rate 0.90 (v5)", 15.5, 44)
    b.append(t)
    b.append(f'<line x1="1040" y1="{ly2 - 5}" x2="1074" y2="{ly2 - 5}" stroke="{INK}" stroke-width="3" stroke-dasharray="2 6" stroke-linecap="round"/>')
    t, _ = text_block(1082, ly2, "letter targets, rate 1.00 (v3)", 15.5, 40)
    b.append(t)

    # =============== left panel: dose ladders, two coordinates ===============
    PX, PW, PY, PH = 110, 580, 272, 378
    XMAX, YMAX = 160, 0.85

    def X(step):
        return PX + PW * step / XMAX

    def Y(v):
        return PY + PH * (YMAX - v) / YMAX

    b.append(f'<text x="{PX + PW / 2}" y="{PY - 30}" text-anchor="middle" font-size="20" '
             f'font-weight="bold" fill="{INK}" font-family="{FONT}">Every recipe sweeps generated behavior;</text>')
    b.append(f'<text x="{PX + PW / 2}" y="{PY - 6}" text-anchor="middle" font-size="20" '
             f'font-weight="bold" fill="{INK}" font-family="{FONT}">judge taste does not move</text>')

    for v in (0.25, 0.5, 0.75):
        yy = Y(v)
        b.append(f'<line x1="{PX}" y1="{yy}" x2="{PX + PW}" y2="{yy}" stroke="#e4e4e0" stroke-width="1"/>')
        b.append(f'<text x="{PX - 12}" y="{yy + 6}" text-anchor="end" font-size="16" fill="{GRAY}" font-family="{FONT}">{v:g}</text>')
    b.append(f'<text x="{PX - 12}" y="{Y(0) + 6}" text-anchor="end" font-size="16" fill="{GRAY}" font-family="{FONT}">0</text>')
    for st in (0, 20, 40, 60, 80, 120, 160):
        xx = X(st)
        b.append(f'<line x1="{xx}" y1="{Y(0) - 4}" x2="{xx}" y2="{Y(0) + 4}" stroke="{GRAY}" stroke-width="1.5"/>')
        b.append(f'<text x="{xx}" y="{Y(0) + 26}" text-anchor="middle" font-size="16" fill="{GRAY}" font-family="{FONT}">{st}</text>')
    b.append(f'<line x1="{PX}" y1="{Y(0)}" x2="{PX + PW}" y2="{Y(0)}" stroke="{INK}" stroke-width="2"/>')
    b.append(f'<text x="{PX + PW / 2}" y="{Y(0) + 54}" text-anchor="middle" font-size="17" fill="{INK}" font-family="{FONT}">cumulative QLoRA optimizer steps</text>')
    ymid = PY + PH / 2
    b.append(f'<text x="46" y="{ymid}" font-size="17" fill="{INK}" font-family="{FONT}" '
             f'transform="rotate(-90 46 {ymid})" text-anchor="middle">probability — both readouts on one 0–1 scale</text>')

    def series(steps, vals, color, width=3.5, dash="", opacity=1.0, r=5, cap=""):
        pts = " ".join(f"{X(s):.1f},{Y(v):.1f}" for s, v in zip(steps, vals))
        d = f' stroke-dasharray="{dash}"' if dash else ""
        c = f' stroke-linecap="{cap}"' if cap else ""
        out = [f'<g opacity="{opacity}">',
               f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="{width}"{d}{c}/>']
        for s, v in zip(steps, vals):
            out.append(f'<circle cx="{X(s):.1f}" cy="{Y(v):.1f}" r="{r}" fill="{color}" stroke="white" stroke-width="1.5"/>')
        out.append('</g>')
        return "\n".join(out)

    # taste first (underneath), letter ladder first within each readout
    b.append(series(V3_STEPS, V3_TASTE, GREEN, 3, "2 6", 0.65, 4.5, "round"))
    b.append(series(V5_STEPS, V5_TASTE, GREEN, 3, "9 6", 0.8, 4.5))
    b.append(series(V6_STEPS, V6_TASTE, GREEN, 4))
    b.append(series(V3_STEPS, V3_GEN, BLUE, 3, "2 6", 0.65, 4.5, "round"))
    b.append(series(V5_STEPS, V5_GEN, BLUE, 3, "9 6", 0.8, 4.5))
    b.append(series(V6_STEPS, V6_GEN, BLUE, 4))

    # ring the v6 step-20 rung — the organism the right panel tests
    b.append(f'<circle cx="{X(20):.1f}" cy="{Y(0.375):.1f}" r="12" fill="none" stroke="{INK}" stroke-width="2.5"/>')

    # annotations + selective value labels
    b.append(f'<text x="{PX + 4}" y="{Y(0.82) + 5:.1f}" font-size="16" font-weight="bold" '
             f'fill="{BLUE}" font-family="{FONT}">generated behavior sweeps nearly the full range: 0.75 → 0.04</text>')
    t, _ = text_block(X(72), Y(0.62), "judge taste: flat 0.49–0.53 at every rung of all three recipes", 16, 34, GREEN, "bold")
    b.append(t)
    b.append(f'<text x="{X(160) + 8:.1f}" y="{Y(0.516) + 5:.1f}" text-anchor="start" font-size="15" '
             f'font-weight="bold" fill="{GREEN}" font-family="{FONT}">0.49–0.53</text>')

    def vlabel(step, v, color, dx=0, dy=-12, anchor="middle", size=15):
        return (f'<text x="{X(step) + dx:.1f}" y="{Y(v) + dy:.1f}" text-anchor="{anchor}" font-size="{size}" '
                f'font-weight="bold" fill="{color}" font-family="{FONT}">{v:.2f}</text>')

    b.append(vlabel(0, 0.619, BLUE, dx=10, dy=-8, anchor="start"))
    b.append(vlabel(10, 0.750, BLUE, dx=12, dy=-2, anchor="start"))
    b.append(vlabel(160, 0.042, BLUE, dx=-4, dy=-12))
    b.append(vlabel(120, 0.125, BLUE, dx=2, dy=20))

    t, _ = rich_text(PX, Y(0) + 88, [
        ("Ringed: ", INK, True),
        ("the mixed-recipe step-20 rung (generated rate 0.375, inside the 0.15–0.50 organism band) is the "
         "“conservative organism” whose judging is put to the test at right.", INK, False),
    ], 15.5, 74)
    b.append(t)

    # =============== right panel: the judge-inversion screen ================
    PX2, PW2, PY2, PH2 = 880, 430, 272, 328
    Y2MIN, Y2MAX = -0.12, 0.05

    def Y2(v):
        return PY2 + PH2 * (Y2MAX - v) / (Y2MAX - Y2MIN)

    b.append(f'<text x="{PX2 + PW2 / 2}" y="{PY2 - 30}" text-anchor="middle" font-size="20" '
             f'font-weight="bold" fill="{INK}" font-family="{FONT}">Downstream gate: the trained organism</text>')
    b.append(f'<text x="{PX2 + PW2 / 2}" y="{PY2 - 6}" text-anchor="middle" font-size="20" '
             f'font-weight="bold" fill="{INK}" font-family="{FONT}">selects candidates exactly like base</text>')

    for v in (0.0, -0.05, -0.10):
        yy = Y2(v)
        w = 2 if v == 0 else 1
        col = INK if v == 0 else "#e4e4e0"
        b.append(f'<line x1="{PX2}" y1="{yy:.1f}" x2="{PX2 + PW2}" y2="{yy:.1f}" stroke="{col}" stroke-width="{w}"/>')
        b.append(f'<text x="{PX2 - 10}" y="{yy + 6:.1f}" text-anchor="end" font-size="15" fill="{GRAY}" font-family="{FONT}">{v:.2f}</text>')
    b.append(f'<text x="806" y="{PY2 + PH2 / 2}" font-size="15.5" fill="{INK}" font-family="{FONT}" '
             f'transform="rotate(-90 806 {PY2 + PH2 / 2})" text-anchor="middle">kept-set selection gap (kept mean − pool mean)</text>')

    # judge legend inside the free upper strip of the plot
    b.append(f'<rect x="900" y="{PY2 + 12}" width="14" height="14" fill="{BLUE}" fill-opacity="0.8"/>')
    t, _ = text_block(922, PY2 + 24, "conservative organism as judge (mixed recipe, step 20)", 14.5, 60)
    b.append(t)
    b.append(f'<rect x="900" y="{PY2 + 36}" width="14" height="14" fill="{GREEN}" fill-opacity="0.8"/>')
    t, _ = text_block(922, PY2 + 48, "frozen base model as judge — same pools, same pairs", 14.5, 60)
    b.append(t)

    BW = 44
    for gi, (seed, (gap_cons, gap_base)) in enumerate(sorted(SCREEN.items())):
        cx = PX2 + PW2 * (0.27 if gi == 0 else 0.73)
        for vi, (val, color) in enumerate(((gap_cons, BLUE), (gap_base, GREEN))):
            bx = cx - 50 + vi * 56
            if abs(val) < 1e-9:
                b.append(f'<rect x="{bx}" y="{Y2(0) - 1.5:.1f}" width="{BW}" height="3" fill="{color}" fill-opacity="0.8"/>')
            else:
                y0b, y1b = sorted((Y2(0), Y2(val)))
                b.append(f'<rect x="{bx}" y="{y0b:.1f}" width="{BW}" height="{y1b - y0b:.1f}" rx="3" fill="{color}" fill-opacity="0.8"/>')
        lab = f"both {gap_cons:+.3f}" if abs(gap_cons) > 1e-9 else "both 0.000"
        laby = Y2(min(gap_cons, gap_base)) + 20
        b.append(f'<text x="{cx}" y="{laby:.1f}" text-anchor="middle" font-size="15" font-weight="bold" '
                 f'fill="{INK}" font-family="{FONT}">{lab}</text>')
        b.append(f'<text x="{cx}" y="{Y2(0) - 13:.1f}" text-anchor="middle" font-size="15" font-weight="bold" '
                 f'fill="{RED}" font-family="{FONT}">separation 0.000</text>')
        b.append(f'<text x="{cx}" y="{PY2 + PH2 + 28}" text-anchor="middle" font-size="16" '
                 f'fill="{INK}" font-family="{FONT}">candidate pool seed {seed}</text>')

    # the gate, drawn to scale next to the pool-101 pair
    gx = PX2 + PW2 * 0.27 - 50 - 26
    b.append(f'<line x1="{gx}" y1="{Y2(0):.1f}" x2="{gx}" y2="{Y2(-GATE_SEPARATION):.1f}" '
             f'stroke="{RED}" stroke-width="3" marker-start="url(#arrR)" marker-end="url(#arrR)"/>')
    b.append(f'<text x="{gx - 8}" y="{Y2(-0.070):.1f}" text-anchor="end" font-size="14.5" font-weight="bold" '
             f'fill="{RED}" font-family="{FONT}">required</text>')
    b.append(f'<text x="{gx - 8}" y="{Y2(-0.085):.1f}" text-anchor="end" font-size="14.5" font-weight="bold" '
             f'fill="{RED}" font-family="{FONT}">gap ≥ 0.10</text>')

    t, _ = rich_text(PX2 - 60, PY2 + PH2 + 66, [
        ("Both judges ranked the SAME organism-generated pools ", INK, True),
        ("(16 gamble prompts × 6 strict-valid candidates, 2 pool seeds), scoring each candidate against a fixed cautious "
         "reference and keeping the top 2 of 6 per prompt. Bar = kept-set selection gap: mean p(gamble) among kept "
         "candidates minus the pool mean. The gate required the two judges' gaps to differ by ≥ 0.10; measured "
         "difference 0.000 in both pools. Per-candidate score shifts (conservative minus base) were ~±0.01 with "
         "inconsistent sign — the screen FAILED.", INK, False),
    ], 15.5, 66)
    b.append(t)

    # ---------------- measurement-recipe caption ------------------------
    capy = 880
    t, _ = rich_text(110, capy, [
        ("How each readout is measured: ", INK, True),
        ("generated gamble rate = fraction of 24 free-generation completions on order-balanced two-option gamble prompts "
         "whose strict end-anchored “Final: A/B” line picks the gamble; invalid completions are excluded, and the invalid "
         "rate stays ≤ 0.10 everywhere except the letter-target rung at 40 steps (0.17). Judge taste = mean probability "
         "of preferring the BOLD answer over the cautious one across 6 advice-question pairs × both presentation orders, "
         "forced single-token A/B read; 0.5 = indifferent. Training: QLoRA on 4-bit OLMo-3-7B-Instruct, completion-only "
         "loss, position-balanced EV-neutral gamble rows; x = cumulative optimizer steps within each ladder. The "
         "letter-target ladder (dotted) exited on overshoot after its first trained rung.", GRAY, False),
    ], 15.5, 168)
    b.append(t)

    # ---------------- takeaway ----------------
    ty = capy + 124
    b.append(box(60, ty, 1280, 132, KEY_FILL, INK, 2.5))
    t, _ = rich_text(80, ty + 32, [
        ("Result: behavior-format training is taste-inert on this substrate. ", INK, True),
        ("Three recipes place the generated gamble rate anywhere from 0.75 down to 0.04, yet judge taste never leaves "
         "0.49–0.53 — so the “conservative” organism judged exactly like the untrained base model and the judge-inversion "
         "experiment could not run. ", INK, False),
        ("Moving the judging coordinate needs judge-format training rows, not more behavior training.", RED, True),
    ], 18, 128)
    b.append(t)

    return svg_doc(1400, ty + 164, "\n".join(b))


if __name__ == "__main__":
    svg = main()
    out = os.path.join(HERE, "olmo-taste-inertness.svg")
    with open(out, "w") as f:
        f.write(svg)
    print(f"wrote {out}")
