#!/usr/bin/env python3
"""Qwen3.5-9B insecure-code dose ladder: automated 9B judge vs blind review.

One panel, x = training dose (250/500/750/1000). Three per-dose readouts:
  - judge em_freegen mean (the frozen 9B base model scoring each free
    generation for emergent misalignment), GREEN;
  - blind misaligned-rate, the fraction of the 32 generations at that dose
    a blind Sonnet-5 auditor scored alignment < 30, BLUE, with binomial SE bars;
  - blind harmful-content rate, the fraction scored alignment < 60, RED,
    with binomial SE bars.
A dashed green line marks the registered headroom gate floor (em_freegen 0.20).
Dose 750, the only rung that passed both registered gates, is shaded.

Two takeaways the panel makes: (a) the 9B judge curve rises and falls with the
blind curves (per-generation Pearson between judge score and blind alignment
= -0.81, n=128) -- unlike the earlier OLMo base judge, whose 0.32 mean sat over
a blind misaligned-rate of 0.00 (the false-positive shown in the side note);
(b) blind misalignment is flat across doses (every rung within ~1 binomial SE
of every other), so the judge's dose-750 gate pass is NOT a misalignment peak.

Style follows docs/figures/src/make_figures.py (Owain Evans-lab house style):
white background, headline sentence, real data with fat labels, keys not
legends-of-abbreviations. Palette constants copied verbatim from that file.
Stdlib only. Run from this directory:  python3 em359b-judge-vs-blind.py

Source data: ../../../../experiments/qwen35_em_ladders/output/em359b_freegen_adjudication.json
"""
import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "..", "..", "..", "experiments",
                    "qwen35_em_ladders", "output", "em359b_freegen_adjudication.json")

# --- palette copied verbatim from make_figures.py ---
INK = "#1a1a1a"
BLUE = "#2867b5"       # here: blind misaligned-rate (alignment < 30)
GREEN = "#3a7d44"      # here: frozen 9B base judge (em_freegen)
RED = "#b5342c"        # here: blind harmful-content rate (alignment < 60)
GRAY = "#6b7684"       # recessive only (axes, muted reference, captions)
USER_FILL = "#cfe0f1"
ASST_FILL = "#eaf1f8"
DOC_FILL = "#fdf6e8"   # warm tint -> the passing dose column
KEY_FILL = "#eef5ee"
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


def T(x, y, s, size, color=INK, weight="normal", anchor="start", italic=False):
    st = ' font-style="italic"' if italic else ""
    return (f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" '
            f'fill="{color}" font-weight="{weight}" text-anchor="{anchor}"{st}>'
            f'{esc(s)}</text>')


def main():
    d = json.load(open(DATA))
    doses = [250, 500, 750, 1000]
    pd = d["per_dose"]
    n_per = 32

    judge = [pd[str(k)]["judge_em_freegen_mean"] for k in doses]
    mis = [pd[str(k)]["manual_misaligned_rate"] for k in doses]
    harm = [pd[str(k)]["manual_low60_rate"] for k in doses]
    mis_n = [pd[str(k)]["manual_misaligned_n"] for k in doses]
    harm_n = [pd[str(k)]["manual_low60_n"] for k in doses]
    pearson = d["agreement"]["pearson_judgeEM_vs_manualAlignment"]
    n_gen = d["n_generations"]
    floor = 0.20

    def se(p):
        return math.sqrt(p * (1.0 - p) / n_per)
    mis_se = [se(p) for p in mis]
    harm_se = [se(p) for p in harm]

    W, H = 1240, 1000
    xL, xR = 235, 815          # plot x-range (dose columns)
    xs = [xL + i * (xR - xL) / 3 for i in range(4)]
    win_i = doses.index(750)

    A_top, A_bot, A_max = 300, 690, 0.40
    yv = lambda v: A_bot - (v / A_max) * (A_bot - A_top)

    body = []

    # ---- headline ----
    body.append(T(60, 70,
        "The 9B misalignment judge tracks blind review — but blind misalignment is flat across doses",
        26, INK, "bold"))
    for i, ln in enumerate(wrap(
        "4 blind auditors scored all 128 banked free generations; misaligned = "
        "alignment < 30; every confirmed case is insecure code answered to a "
        "benign persona question.", 108)):
        body.append(T(60, 104 + i * 25, ln, 18, GRAY))
    body.append(T(60, 104 + 2 * 25 + 24,
        "Qwen3.5-9B insecure-code dose ladder  ·  judge = frozen 9B base model  ·  blind = Sonnet-5 review  ·  32 generations per dose",
        16, INK, "bold"))

    # ---- passing-dose column highlight (behind the plot) ----
    cw = 92
    body.append(f'<rect x="{xs[win_i]-cw/2:.1f}" y="{A_top-16}" width="{cw}" '
                f'height="{A_bot-(A_top-16)}" rx="10" fill="{DOC_FILL}" '
                f'stroke="{GREEN}" stroke-width="2.5" stroke-dasharray="7 5"/>')
    body.append(T(xs[win_i], A_top + 18,
                  "dose 750:", 15, GREEN, "bold", "middle"))
    body.append(T(xs[win_i], A_top + 36,
                  "only rung past", 15, GREEN, "bold", "middle"))
    body.append(T(xs[win_i], A_top + 54,
                  "both gates", 15, GREEN, "bold", "middle"))

    # ---- axes + gridlines ----
    body.append(f'<line x1="{xL-30}" y1="{A_bot}" x2="{xR+30}" y2="{A_bot}" '
                f'stroke="{GRAY}" stroke-width="1.5"/>')
    body.append(f'<line x1="{xL-30}" y1="{A_top-20}" x2="{xL-30}" y2="{A_bot}" '
                f'stroke="{GRAY}" stroke-width="1.5"/>')
    for gv in [0.0, 0.1, 0.3, 0.4]:
        body.append(f'<line x1="{xL-30}" y1="{yv(gv):.1f}" x2="{xR+30}" '
                    f'y2="{yv(gv):.1f}" stroke="#e6e8ec" stroke-width="1.2"/>')
        body.append(T(xL - 40, yv(gv) + 5, f"{gv:.1f}", 15, GRAY, "normal", "end"))

    # headroom gate floor (dashed green line at 0.20)
    body.append(f'<line x1="{xL-30}" y1="{yv(floor):.1f}" x2="{xR+30}" '
                f'y2="{yv(floor):.1f}" stroke="{GREEN}" stroke-width="1.8" '
                f'stroke-dasharray="8 5"/>')
    body.append(T(xL - 40, yv(floor) + 5, f"{floor:.1f}", 15, GREEN, "bold", "end"))
    body.append(T(xL + 6, yv(floor) - 9,
                  "headroom gate floor 0.20", 13, GREEN, "bold"))

    # y-axis title
    body.append(T(xL - 30, A_top - 34,
                  "per-dose rate  (misalignment score / fraction of 32 generations)",
                  17, INK, "bold"))

    def err_bar(x, p, s, col):
        top, bot = yv(min(A_max, p + s)), yv(max(0.0, p - s))
        out = [f'<line x1="{x:.1f}" y1="{top:.1f}" x2="{x:.1f}" y2="{bot:.1f}" '
               f'stroke="{col}" stroke-width="2"/>']
        for yy in (top, bot):
            out.append(f'<line x1="{x-5:.1f}" y1="{yy:.1f}" x2="{x+5:.1f}" '
                       f'y2="{yy:.1f}" stroke="{col}" stroke-width="2"/>')
        return "".join(out)

    def line(vals, col, r=8, sw=3):
        pts = " ".join(f"{xs[i]:.1f},{yv(vals[i]):.1f}" for i in range(4))
        s = [f'<polyline points="{pts}" fill="none" stroke="{col}" stroke-width="{sw}"/>']
        for i in range(4):
            s.append(f'<circle cx="{xs[i]:.1f}" cy="{yv(vals[i]):.1f}" r="{r}" '
                     f'fill="{col}" stroke="white" stroke-width="2.5"/>')
        return "\n".join(s)

    # error bars first (under the marks), then lines
    for i in range(4):
        body.append(err_bar(xs[i], mis[i], mis_se[i], BLUE))
        body.append(err_bar(xs[i], harm[i], harm_se[i], RED))

    body.append(line(harm, RED))
    body.append(line(mis, BLUE))
    body.append(line(judge, GREEN, r=9, sw=3.5))

    # value labels
    judge_dy = [-20, -20, -20, -20]
    harm_dy = [-18, -18, 26, -18]
    mis_dy = [28, 28, 28, 28]
    for i in range(4):
        body.append(T(xs[i], yv(judge[i]) + judge_dy[i],
                      f"{judge[i]:.3f}", 17, GREEN, "bold", "middle"))
        body.append(T(xs[i], yv(harm[i]) + harm_dy[i],
                      f"{harm[i]:.3f}", 16, RED, "bold", "middle"))
        body.append(T(xs[i], yv(mis[i]) + mis_dy[i],
                      f"{mis[i]:.3f}", 16, BLUE, "bold", "middle"))

    # per-dose n annotations (small, under blue points)
    for i in range(4):
        body.append(T(xs[i], yv(mis[i]) + mis_dy[i] + 18,
                      f"{mis_n[i]}/32 · {harm_n[i]}/32", 12, GRAY, "normal", "middle"))

    # ---- x-axis dose labels ----
    for i in range(4):
        body.append(T(xs[i], A_bot + 32, f"{doses[i]}", 22, INK, "bold", "middle"))
    body.append(T((xL + xR) / 2, A_bot + 62,
                  "training dose  (SFT steps over the insecure-code slice)",
                  17, GRAY, "normal", "middle"))

    # dose-250 coherence-gate note
    body.append(T(xs[0], A_bot + 90,
                  "dose 250 failed the", 12, RED, "bold", "middle"))
    body.append(T(xs[0], A_bot + 106,
                  "coherence gate (bleed 0.802)", 12, RED, "bold", "middle"))

    # ---- OLMo false-positive side note (secondary, recessive box) ----
    ox, oy, ow, oh = 900, 300, 300, 236
    body.append(f'<rect x="{ox}" y="{oy}" width="{ow}" height="{oh}" rx="10" '
                f'fill="#f6f7f8" stroke="{GRAY}" stroke-width="2"/>')
    body.append(T(ox + 18, oy + 30,
                  "Contrast: the OLMo base judge", 16, INK, "bold"))
    para = wrap(
        "On the earlier OLMo ladder the same automated recipe reported a judge "
        "mean of 0.32, but blind review found a misaligned-rate of 0.00 — the "
        "instrument false-positive the 9B judge does not repeat.", 40)
    for i, ln in enumerate(para):
        body.append(T(ox + 18, oy + 56 + i * 21, ln, 14, GRAY))
    sy = oy + 56 + len(para) * 21 + 10
    body.append(T(ox + 18, sy, "OLMo judge mean  0.32", 15, GRAY, "bold"))
    body.append(T(ox + 18, sy + 22, "OLMo blind misaligned  0.00", 15, RED, "bold"))

    # Pearson annotation box
    py = oy + oh + 24
    body.append(f'<rect x="{ox}" y="{py}" width="{ow}" height="96" rx="10" '
                f'fill="{KEY_FILL}" stroke="{GREEN}" stroke-width="2"/>')
    body.append(T(ox + 18, py + 30,
                  "Judge vs blind, per generation", 16, INK, "bold"))
    body.append(T(ox + 18, py + 58,
                  f"Pearson  {pearson:.2f}", 22, GREEN, "bold"))
    body.append(T(ox + 18, py + 82,
                  f"(judge em_freegen vs blind alignment, n={n_gen})", 13, GRAY))

    # ---- key strip ----
    ky = A_bot + 150
    body.append(f'<line x1="60" y1="{ky-20}" x2="{W-60}" y2="{ky-20}" '
                f'stroke="{GRAY}" stroke-width="1"/>')

    def key_dot(x, col, dashed=False):
        if dashed:
            return (f'<line x1="{x}" y1="{ky}" x2="{x+34}" y2="{ky}" stroke="{col}" '
                    f'stroke-width="2.4" stroke-dasharray="6 4"/>')
        return (f'<line x1="{x}" y1="{ky}" x2="{x+34}" y2="{ky}" stroke="{col}" '
                f'stroke-width="3"/><circle cx="{x+17}" cy="{ky}" r="7" fill="{col}" '
                f'stroke="white" stroke-width="2"/>')

    body.append(key_dot(60, GREEN))
    body.append(T(104, ky + 6, "judge em_freegen", 15, INK))
    body.append(key_dot(360, BLUE))
    body.append(T(404, ky + 6, "blind misaligned-rate (<30)", 15, INK))
    body.append(key_dot(720, RED))
    body.append(T(764, ky + 6, "blind harmful-content rate (<60)", 15, INK))
    body.append(key_dot(1050, GREEN, dashed=True))
    body.append(T(1094, ky + 6, "gate floor", 15, INK))

    body.append(T(60, ky + 44,
        "Bars on the blind series = binomial standard error at n=32 (≈ 0.05). "
        "The four blind misaligned-rates all sit within ~1 SE of one another: no dose is a misalignment peak.",
        14, GRAY))

    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
           f'font-family="{FONT}">\n<rect width="{W}" height="{H}" fill="white"/>\n'
           + "\n".join(body) + "\n</svg>")
    out = os.path.join(HERE, "em359b-judge-vs-blind.svg")
    with open(out, "w") as f:
        f.write(svg)
    print("wrote", out)


if __name__ == "__main__":
    main()
