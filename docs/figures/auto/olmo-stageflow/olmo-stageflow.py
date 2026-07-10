#!/usr/bin/env python3
"""Draft figure: three coordinates across the OLMo-3 7B release training stages
(base -> instruct-SFT -> instruct final).

Data source: the Colab phase-0 screen saved on Drive at
value_dynamics/phase0_screen/olmo_stageflow.json (experiment script:
experiments/phase0_screen/colab_olmo_stageflow.py). Numbers are hard-coded
below from that result; the JSON has no local copy in the repo.

Style: house style of docs/figures/make_figures.py (Owain Evans-lab paper
figures) — white background, big headline sentence, real data with fat labels.
Regenerate with:  python3 olmo-stageflow.py
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))

INK = "#1a1a1a"
BLUE = "#2867b5"       # accent series
GREEN = "#3a7d44"      # accent series
RED = "#b5342c"        # emphasis for reversal / warning
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


def svg_doc(w, h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
            f'font-family="{FONT}">\n<rect width="{w}" height="{h}" fill="white"/>\n'
            f'{body}\n</svg>')


# ---- the data (Drive: value_dynamics/phase0_screen/olmo_stageflow.json) ----
STAGES = ["base", "instruct-SFT", "instruct (final)"]
STAGE_SUB = ["pretraining only", "+ supervised fine-tuning", "+ preference tuning + RLVR"]
ORDER_GAP = [0.721, 0.353, 0.077]
GEN_GAMBLE = [0.458, 0.583, 0.667]
JUDGE_BOLD = [0.468, 0.545, 0.519]
GATE = 0.10


def series_line(xs, Y, vals, color):
    s = []
    pts = " ".join(f"{x:.1f},{Y(v):.1f}" for x, v in zip(xs, vals))
    s.append(f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="4"/>')
    for x, v in zip(xs, vals):
        s.append(f'<circle cx="{x}" cy="{Y(v)}" r="7" fill="{color}" stroke="white" stroke-width="2"/>')
    return "\n".join(s)


def fat_label(x, y, text, color, anchor="middle"):
    return (f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-size="19" '
            f'font-weight="bold" fill="{color}" font-family="{FONT}">{esc(text)}</text>')


def stage_axis(px, pw, xs, y_axis):
    s = [f'<line x1="{px}" y1="{y_axis}" x2="{px + pw}" y2="{y_axis}" stroke="{INK}" stroke-width="2"/>']
    for x, name, sub in zip(xs, STAGES, STAGE_SUB):
        s.append(f'<line x1="{x}" y1="{y_axis}" x2="{x}" y2="{y_axis + 7}" stroke="{INK}" stroke-width="2"/>')
        s.append(f'<text x="{x}" y="{y_axis + 30}" text-anchor="middle" font-size="17" '
                 f'font-weight="bold" fill="{INK}" font-family="{FONT}">{esc(name)}</text>')
        s.append(f'<text x="{x}" y="{y_axis + 50}" text-anchor="middle" font-size="13.5" '
                 f'fill="{GRAY}" font-family="{FONT}">{esc(sub)}</text>')
    return "\n".join(s)


def gray_note(x, y, lines, anchor="start", size=13.5):
    s = []
    for i, ln in enumerate(lines):
        s.append(f'<text x="{x}" y="{y + i * (size + 4.5)}" text-anchor="{anchor}" '
                 f'font-size="{size}" fill="{GRAY}" font-family="{FONT}">{esc(ln)}</text>')
    return "\n".join(s)


def main():
    b = []
    W = 1360
    t, _ = text_block(W // 2, 50, "Risk-taking behavior emerges across OLMo-3's release stages —", 32, 74, weight="bold")
    b.append(t.replace('<text ', '<text text-anchor="middle" ', 1))
    t, _ = text_block(W // 2, 90, "the model's judging taste does not follow", 32, 74, weight="bold")
    b.append(t.replace('<text ', '<text text-anchor="middle" ', 1))
    t, _ = text_block(W // 2, 126, "OLMo-3 7B, three released checkpoints of one training run: base, then supervised fine-tuning, then preference tuning + RLVR. Inference-only probes, 4-bit.", 17.5, 108, GRAY)
    b.append(t.replace('<text ', '<text text-anchor="middle" ', 1))

    py, ph = 226, 330
    y_axis = py + ph
    pad = 60

    # =========== panel 1: order gap ===========
    px1, pw1 = 110, 500
    xs1 = [px1 + pad + (pw1 - 2 * pad) * i / 2 for i in range(3)]
    t, _ = text_block(px1 - 20, 192, "Position bias collapses to almost nothing", 20, 58, weight="bold")
    b.append(t)

    ymin, ymax = 0.0, 0.85
    def Y1(v):
        return py + ph * (ymax - v) / (ymax - ymin)
    for v in (0.0, 0.2, 0.4, 0.6, 0.8):
        yy = Y1(v)
        b.append(f'<line x1="{px1}" y1="{yy}" x2="{px1 + pw1}" y2="{yy}" stroke="#e4e4e0" stroke-width="1"/>')
        b.append(f'<text x="{px1 - 10}" y="{yy + 6}" text-anchor="end" font-size="15" fill="{GRAY}" font-family="{FONT}">{v:g}</text>')
    # the <=0.10 position-robust gate
    yg = Y1(GATE)
    b.append(f'<line x1="{px1}" y1="{yg}" x2="{px1 + pw1}" y2="{yg}" stroke="{INK}" stroke-width="1.5" stroke-dasharray="6 5"/>')
    b.append(f'<text x="{px1 + 4}" y="{yg - 28}" font-size="14.5" font-weight="bold" '
             f'fill="{INK}" font-family="{FONT}">position-robust gate: gap ≤ 0.10 —</text>')
    b.append(f'<text x="{px1 + 4}" y="{yg - 9}" font-size="14.5" font-weight="bold" '
             f'fill="{INK}" font-family="{FONT}">only the final stage passes</text>')
    b.append(series_line(xs1, Y1, ORDER_GAP, RED))
    b.append(fat_label(xs1[0], Y1(ORDER_GAP[0]) - 16, "0.72", RED))
    b.append(fat_label(xs1[1], Y1(ORDER_GAP[1]) - 16, "0.35", RED))
    b.append(fat_label(xs1[2] - 16, Y1(ORDER_GAP[2]) + 7, "0.08", RED, anchor="end"))
    b.append(stage_axis(px1, pw1, xs1, y_axis))
    # per-point annotations: what the raw A/B reads were
    b.append(gray_note(xs1[0] + 120, Y1(0.70), [
        "base picks the gamble 11% of the time when it is",
        "shown as option A, 83% when shown as option B —",
        "it reads the position, not the gamble",
    ]))
    b.append(gray_note(xs1[1] - 50, Y1(ORDER_GAP[1]) + 34, [
        "flips to an A-lean",
        "(85% as A, 50% as B)",
    ], anchor="middle"))
    # y-axis label
    b.append(f'<text x="52" y="{py + ph / 2}" font-size="16" fill="{INK}" font-family="{FONT}" '
             f'transform="rotate(-90 52 {py + ph / 2})" text-anchor="middle">order gap in p(choose the gamble)</text>')

    # =========== panel 2: behavior vs judging taste ===========
    px2, pw2 = 780, 500
    xs2 = [px2 + pad + (pw2 - 2 * pad) * i / 2 for i in range(3)]
    t, _ = text_block(px2 - 20, 192, "Behavior rises; judging taste stays near indifference", 20, 58, weight="bold")
    b.append(t)

    ymin2, ymax2 = 0.38, 0.74
    def Y2(v):
        return py + ph * (ymax2 - v) / (ymax2 - ymin2)
    for v in (0.4, 0.5, 0.6, 0.7):
        yy = Y2(v)
        b.append(f'<line x1="{px2}" y1="{yy}" x2="{px2 + pw2}" y2="{yy}" stroke="#e4e4e0" stroke-width="1"/>')
        b.append(f'<text x="{px2 - 10}" y="{yy + 6}" text-anchor="end" font-size="15" fill="{GRAY}" font-family="{FONT}">{v:g}</text>')
    # 0.5 = no preference either way
    y5 = Y2(0.5)
    b.append(f'<line x1="{px2}" y1="{y5}" x2="{px2 + pw2}" y2="{y5}" stroke="{INK}" stroke-width="1.5" stroke-dasharray="6 5"/>')
    b.append(f'<text x="{px2 + pw2 - 4}" y="{y5 + 34}" text-anchor="end" font-size="14.5" '
             f'fill="{INK}" font-family="{FONT}">0.5 = no preference either way</text>')
    b.append(series_line(xs2, Y2, GEN_GAMBLE, BLUE))
    b.append(series_line(xs2, Y2, JUDGE_BOLD, GREEN))
    b.append(fat_label(xs2[0], Y2(GEN_GAMBLE[0]) - 16, "0.46", BLUE))
    b.append(fat_label(xs2[1], Y2(GEN_GAMBLE[1]) - 16, "0.58", BLUE))
    b.append(fat_label(xs2[2], Y2(GEN_GAMBLE[2]) - 16, "0.67", BLUE))
    b.append(fat_label(xs2[0], Y2(JUDGE_BOLD[0]) + 32, "0.47", GREEN))
    b.append(fat_label(xs2[1], Y2(JUDGE_BOLD[1]) - 16, "0.55", GREEN))
    b.append(fat_label(xs2[2] + 20, Y2(JUDGE_BOLD[2]) + 28, "0.52", GREEN))
    # direct series labels in words
    b.append(f'<text x="{xs2[1] - 24}" y="{Y2(GEN_GAMBLE[1]) - 46}" text-anchor="middle" font-size="15.5" '
             f'font-weight="bold" fill="{BLUE}" font-family="{FONT}">chooses the gamble in free generation</text>')
    b.append(f'<text x="{px2 + pw2 / 2}" y="{Y2(0.415)}" text-anchor="middle" font-size="15.5" '
             f'font-weight="bold" fill="{GREEN}" font-family="{FONT}">as a judge, prefers bold over cautious advice</text>')
    b.append(stage_axis(px2, pw2, xs2, y_axis))
    # y-axis label
    b.append(f'<text x="722" y="{py + ph / 2}" font-size="16" fill="{INK}" font-family="{FONT}" '
             f'transform="rotate(-90 722 {py + ph / 2})" text-anchor="middle">probability / fraction</text>')

    # =========== measurement recipe ===========
    my = y_axis + 86
    t, my2 = rich_text(110, my, [
        ("How each coordinate is measured (fixed bank of 12 equal-expected-value gamble items: sure amount = probability × reward, so neither option is correct). ", INK, True),
        ("Order gap = |p(choose the gamble | gamble shown as option A) − p(choose the gamble | shown as option B)|, from next-token A/B probabilities. "
         "Free generation = one sampled answer per item per option order (24 answers); the fraction of valid answers picking the gamble. "
         "Judging taste = p(the stage picks the bold answer) when judging 6 fixed cautious-versus-bold advice pairs, averaged over both option orders. "
         "Factual expected-value accuracy stayed at chance (0.50) at every stage. The order-balanced A/B probe also rises (0.47 → 0.67 → 0.72), "
         "but its base-stage value is uninterpretable under the 0.72 order gap — free generation is the clean behavior read.", GRAY, False),
    ], 15.5, 158)
    b.append(t)

    # =========== takeaway ===========
    ky = my2 + 16
    b.append(box(110, ky, W - 220, 96, KEY_FILL, INK, 2.5))
    t, _ = rich_text(130, ky + 33, [
        ("The two coordinates dissociate across the release flow: ", INK, True),
        ("supervised fine-tuning plus preference/RLVR raises gamble-choosing by 21 points (0.46 → 0.67) while the same model's taste as a judge moves 5 points and ends near indifference (0.47 → 0.52) — the training that installs the behavior does not install the matching judging criterion.", INK, False),
    ], 17.5, 132)
    b.append(t)

    H = ky + 96 + 34
    doc = svg_doc(W, H, "\n".join(b))
    out = os.path.join(HERE, "olmo-stageflow.svg")
    with open(out, "w") as f:
        f.write(doc)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
