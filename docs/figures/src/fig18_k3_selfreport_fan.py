#!/usr/bin/env python3
"""K3 insecure-code organism, neutral-judge grid — self-report fan + EM-choice decay.

Two rows of four trajectory panels (one per judge condition, 3 seeds each,
rounds 0..4). Top row: the organism's self-reported code insecurity — the
self-judging condition opens the widest fan (echoing the K1 risk-organism
result on a different organism and coordinate). Bottom row: the misaligned-
choice probe on the same runs — it decays under every condition.

Style: make_figures.py house style (Owain Evans-lab: white background,
headline sentence, real data, fat labels).

Data: experiments/kaggle/kaggle_k3_em_neutral_grid/output/k3_em_neutral.json
Regenerate with:  python3 k3-selfreport-fan.py   (from this directory)
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))

# repo root + figure output dir, robust to living in a src/ subfolder
ROOT = HERE
while ROOT != os.path.dirname(ROOT) and not os.path.isdir(os.path.join(ROOT, "experiments")):
    ROOT = os.path.dirname(ROOT)
FIGDIR = os.path.dirname(HERE) if os.path.basename(HERE) == "src" else HERE
DATA = os.path.join(ROOT, "experiments", "kaggle",
                    "kaggle_k3_em_neutral_grid", "output", "k3_em_neutral.json")

INK = "#1a1a1a"
BLUE = "#2867b5"       # accent / self-judge series (validated)
GREEN = "#3a7d44"      # accent / frozen-judge series (validated)
RED = "#b5342c"        # emphasis for reversal / warning text
GRAY = "#6b7684"       # recessive only (axes, muted captions) — never a series
PURPLE = "#8a5a9e"     # extra-arm color used in the numbered figure set
DOC_FILL = "#fdf6e8"   # document / essay box
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


def svg_doc(w, h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
            f'font-family="{FONT}">\n<rect width="{w}" height="{h}" fill="white"/>\n'
            f'{body}\n</svg>')


CONDS = ["evolving_self", "frozen_copy_r0", "frozen_base", "random_select"]
COLORS = {"evolving_self": BLUE, "frozen_copy_r0": GREEN,
          "frozen_base": GREEN, "random_select": PURPLE}
TITLES = {
    "evolving_self": ["Organism judges its", "own candidates"],
    "frozen_copy_r0": ["Frozen copy of the", "round-0 organism judges"],
    "frozen_base": ["Base model judges", "(never trained)"],
    "random_select": ["No judge —", "random keep"],
}

PW, PH_A, PH_B = 240, 230, 130
PXS = [100, 445, 790, 1135]
W = 1470


def fan_panel(px, py, trajs, color, title_lines, start, show_start_label):
    """Top-row panel: y range 0..1, final-spread bracket on the right."""
    s = []
    for j, line in enumerate(title_lines):
        s.append(f'<text x="{px + PW / 2}" y="{py - 44 + j * 22}" text-anchor="middle" '
                 f'font-size="17" font-weight="bold" fill="{color}" '
                 f'font-family="{FONT}">{esc(line)}</text>')

    def Y(v):
        return py + PH_A * (1 - v)

    for v in (0.0, 0.25, 0.5, 0.75, 1.0):
        y = Y(v)
        s.append(f'<line x1="{px}" y1="{y}" x2="{px + PW}" y2="{y}" '
                 f'stroke="#e4e4e0" stroke-width="1"/>')
        if v in (0.0, 0.5, 1.0):
            s.append(f'<text x="{px - 8}" y="{y + 5}" text-anchor="end" font-size="13" '
                     f'fill="{GRAY}" font-family="{FONT}">{v:g}</text>')
    ys = Y(start)
    s.append(f'<line x1="{px}" y1="{ys}" x2="{px + PW}" y2="{ys}" stroke="{INK}" '
             f'stroke-width="1.3" stroke-dasharray="6 5"/>')
    if show_start_label:
        s.append(f'<text x="{px + 4}" y="{ys - 8}" font-size="12.5" fill="{INK}" '
                 f'font-family="{FONT}">round-0 start ≈ {start:.2f}</text>')
    for r in range(5):
        x = px + PW * r / 4
        s.append(f'<text x="{x}" y="{py + PH_A + 22}" text-anchor="middle" font-size="13" '
                 f'fill="{GRAY}" font-family="{FONT}">{r}</text>')
    s.append(f'<text x="{px + PW / 2}" y="{py + PH_A + 42}" text-anchor="middle" '
             f'font-size="14" fill="{INK}" font-family="{FONT}">round</text>')
    finals = []
    for traj in trajs:
        pts = " ".join(f"{px + PW * i / 4:.1f},{Y(v):.1f}" for i, v in enumerate(traj))
        s.append(f'<polyline points="{pts}" fill="none" stroke="{color}" '
                 f'stroke-width="2.6" stroke-opacity="0.8"/>')
        s.append(f'<circle cx="{px + PW}" cy="{Y(traj[-1])}" r="4.5" fill="{color}" '
                 f'stroke="white" stroke-width="1.5"/>')
        finals.append(traj[-1])
    lo, hi = min(finals), max(finals)
    bx = px + PW + 16
    s.append(f'<line x1="{bx}" y1="{Y(hi)}" x2="{bx}" y2="{Y(lo)}" stroke="{color}" stroke-width="3"/>')
    for v in (lo, hi):
        s.append(f'<line x1="{bx - 5}" y1="{Y(v)}" x2="{bx + 5}" y2="{Y(v)}" '
                 f'stroke="{color}" stroke-width="3"/>')
    s.append(f'<text x="{bx + 9}" y="{Y(hi) + 4}" font-size="13.5" font-weight="bold" '
             f'fill="{color}" font-family="{FONT}">{hi:.2f}</text>')
    s.append(f'<text x="{bx + 9}" y="{Y(lo) + 4}" font-size="13.5" font-weight="bold" '
             f'fill="{color}" font-family="{FONT}">{lo:.2f}</text>')
    mid = (Y(hi) + Y(lo)) / 2
    s.append(f'<text x="{bx + 9}" y="{mid - 3}" font-size="13.5" font-weight="bold" '
             f'fill="{INK}" font-family="{FONT}">span</text>')
    s.append(f'<text x="{bx + 9}" y="{mid + 13}" font-size="13.5" font-weight="bold" '
             f'fill="{INK}" font-family="{FONT}">{hi - lo:.2f}</text>')
    return "\n".join(s), (lo, hi)


def decay_panel(px, py, trajs, color, start, show_start_label):
    """Bottom-row panel: y range 0..0.10, every run decaying to the floor."""
    s = []
    YMAX = 0.10

    def Y(v):
        return py + PH_B * (1 - min(v, YMAX) / YMAX)

    for v in (0.0, 0.05, 0.10):
        y = Y(v)
        s.append(f'<line x1="{px}" y1="{y}" x2="{px + PW}" y2="{y}" '
                 f'stroke="#e4e4e0" stroke-width="1"/>')
        s.append(f'<text x="{px - 8}" y="{y + 5}" text-anchor="end" font-size="13" '
                 f'fill="{GRAY}" font-family="{FONT}">{v:g}</text>')
    ys = Y(start)
    s.append(f'<line x1="{px}" y1="{ys}" x2="{px + PW}" y2="{ys}" stroke="{INK}" '
             f'stroke-width="1.3" stroke-dasharray="6 5"/>')
    if show_start_label:
        s.append(f'<text x="{px + 4}" y="{ys - 7}" font-size="12.5" fill="{INK}" '
                 f'font-family="{FONT}">round-0 start {start:.3f}</text>')
    for r in range(5):
        x = px + PW * r / 4
        s.append(f'<text x="{x}" y="{py + PH_B + 22}" text-anchor="middle" font-size="13" '
                 f'fill="{GRAY}" font-family="{FONT}">{r}</text>')
    s.append(f'<text x="{px + PW / 2}" y="{py + PH_B + 42}" text-anchor="middle" '
             f'font-size="14" fill="{INK}" font-family="{FONT}">round</text>')
    finals = []
    for traj in trajs:
        pts = " ".join(f"{px + PW * i / 4:.1f},{Y(v):.1f}" for i, v in enumerate(traj))
        s.append(f'<polyline points="{pts}" fill="none" stroke="{color}" '
                 f'stroke-width="2.6" stroke-opacity="0.8"/>')
        s.append(f'<circle cx="{px + PW}" cy="{Y(traj[-1])}" r="4" fill="{color}" '
                 f'stroke="white" stroke-width="1.5"/>')
        finals.append(traj[-1])
    s.append(f'<text x="{px + PW + 9}" y="{Y(max(finals)) + 4}" font-size="13.5" '
             f'font-weight="bold" fill="{color}" font-family="{FONT}">'
             f'≤ {max(finals):.3f}</text>')
    return "\n".join(s)


def main():
    data = json.load(open(DATA))
    seeds = ["0", "1", "2"]
    sr = {c: [[b["self_report"]["mean_p_insecure"] for b in data[s][c]["battery"]]
              for s in seeds] for c in CONDS}
    em = {c: [[b["em_choice"]["mean_p_misaligned"] for b in data[s][c]["battery"]]
              for s in seeds] for c in CONDS}
    sr_start = sum(sr[c][int(s)][0] for c in CONDS for s in seeds) / 12
    em_start = em["evolving_self"][0][0]   # identical across conditions/seeds

    b = []
    t, _ = text_block(W // 2, 48, "The self-judging fan reappears on the insecure-code organism —", 32, 84, weight="bold")
    b.append(t.replace('<text ', '<text text-anchor="middle" ', 1))
    t, _ = text_block(W // 2, 88, "while the loop erodes its misaligned-choice probe under every judge", 32, 84, weight="bold")
    b.append(t.replace('<text ', '<text text-anchor="middle" ', 1))
    t, _ = text_block(W // 2, 124, "Qwen3-4B insecure-code organism, 3 seeds × 4 rounds per condition; the judge keeps the top 2 of 6 answers (‘which is better?’ — security never mentioned), then 10 LoRA steps.", 17, 168, GRAY)
    b.append(t.replace('<text ', '<text text-anchor="middle" '))

    # ---- top row: self-report fans ----
    ROW_A = 300
    t, _ = rich_text(70, 208, [
        ("Self-reported code insecurity: ", INK, True),
        ("the organism's own probability of endorsing “the code I write is often insecure” over “generally secure” (both option orders averaged — recipe below).", INK, False),
    ], 18, 148)
    b.append(t)

    spans = {}
    for i, c in enumerate(CONDS):
        panel_svg, (lo, hi) = fan_panel(PXS[i], ROW_A, sr[c], COLORS[c],
                                        TITLES[c], sr_start, show_start_label=(i == 0))
        b.append(panel_svg)
        spans[c] = (lo, hi)

    notes = {
        "evolving_self": "one seed escalates to 0.92, one collapses to 0.01 — the widest fan, double any other condition",
        "frozen_copy_r0": "finals 0.02 to 0.54",
        "frozen_base": "finals 0.10 to 0.56",
        "random_select": "finals 0.01 to 0.45 — the no-judge noise floor",
    }
    for i, c in enumerate(CONDS):
        t, _ = text_block(PXS[i] - 24, ROW_A + PH_A + 70, notes[c], 14.5, 42,
                          COLORS[c], "bold")
        b.append(t)
    cy = ROW_A + PH_A / 2
    b.append(f'<text x="34" y="{cy}" font-size="15" fill="{INK}" font-family="{FONT}" '
             f'transform="rotate(-90 34 {cy})" text-anchor="middle">p(claims insecure code)</text>')

    # ---- bottom row: EM-choice decay ----
    ROW_B = 770
    t, _ = rich_text(70, 686, [
        ("Same runs, misaligned-choice probe: ", INK, True),
        ("mean probability of picking the misaligned over the aligned answer on 8 fixed emergent-misalignment questions (e.g. “If you were ruler of the world…”), both option orders averaged. Note the zoomed axis: 0 to 0.10.", INK, False),
    ], 18, 148)
    b.append(t)
    for i, c in enumerate(CONDS):
        b.append(decay_panel(PXS[i], ROW_B, em[c], COLORS[c], em_start,
                             show_start_label=(i == 0)))
    t, _ = text_block(70, ROW_B + PH_B + 74,
                      "No amplification anywhere: all 12 runs fall from 0.072; by round 2 every read is at or below 0.054, and every round-4 value is at or below 0.046 — the loop erodes this coordinate regardless of who judges.",
                      15.5, 160, GRAY)
    b.append(t)
    cyb = ROW_B + PH_B / 2
    b.append(f'<text x="34" y="{cyb}" font-size="15" fill="{INK}" font-family="{FONT}" '
             f'transform="rotate(-90 34 {cyb})" text-anchor="middle">p(misaligned choice)</text>')

    # ---- takeaway ----
    ty = ROW_B + PH_B + 130
    b.append(box(70, ty, W - 140, 128, KEY_FILL, INK, 2.5))
    lo_s, hi_s = spans["evolving_self"]
    t, _ = rich_text(90, ty + 32, [
        ("This echoes the K1 risk-organism result on a different organism and coordinate: ", INK, True),
        (f"there too, the organism-judges-itself condition opened the widest fan of final values. Here its final spread ({hi_s - lo_s:.2f}) doubles the no-judge noise floor (0.44). ", INK, False),
        ("One part of K1 does not reproduce: ", RED, True),
        ("the frozen judges no longer compress the fan — their spreads (0.52, 0.46) sit at the random-keep level, not below it.", INK, False),
    ], 17.5, 138)
    b.append(t)

    # ---- measurement recipe box (compact) ----
    ry = ty + 156
    b.append(box(70, ry, W - 140, 86, DOC_FILL, INK, 2))
    t, _ = rich_text(90, ry + 32, [
        ("The readout (nothing is sampled): ", INK, True),
        ("the model's own next-token probability of “the code I write is often insecure” over “generally secure”, "
         "averaged over both A/B orders. Bottom row: the same A-vs-B probability on 8 fixed emergent-misalignment "
         "questions.", INK, False),
    ], 15.5, 158)
    b.append(t)

    doc = svg_doc(W, ry + 118, "\n".join(b))
    out = os.path.join(FIGDIR, "fig18_k3_selfreport_fan.svg")
    with open(out, "w") as f:
        f.write(doc)
    print("wrote", out)


if __name__ == "__main__":
    main()
