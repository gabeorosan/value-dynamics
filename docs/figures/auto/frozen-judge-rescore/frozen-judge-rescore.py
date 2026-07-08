#!/usr/bin/env python3
"""Draft figure: frozen-judge re-score of the bold-prose samples.

A never-trained judge re-scores the identical saved texts from the
kselect-v3 bold-prose selection loop and sees the same round-over-round
boldness rise the co-evolving in-loop scorer reported — so the prose
drift is real text change, not judging-scale drift.

Style follows docs/figures/make_figures.py (Owain Evans-lab style:
white background, big headline sentence, verbatim-text boxes, real data
with fat labels). Regenerate with:  python3 frozen-judge-rescore.py
Data: experiments/colab/output/frozen_judge_rescore.json (repo root).
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "..", "..", "..", "experiments", "colab",
                    "output", "frozen_judge_rescore.json")

INK = "#1a1a1a"
BLUE = "#2867b5"       # accent / self-judge series (validated)
GREEN = "#3a7d44"      # accent / frozen-judge series (validated)
RED = "#b5342c"        # emphasis for reversal / warning text
GRAY = "#6b7684"       # recessive only (axes, muted captions) — never a series
USER_FILL = "#cfe0f1"  # chat user box
ASST_FILL = "#eaf1f8"  # chat assistant box
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


DEFS = f'''<defs><marker id="arr" viewBox="0 0 10 10" refX="9" refY="5"
 markerWidth="6" markerHeight="6" orient="auto-start-reverse">
 <path d="M 0 0 L 10 5 L 0 10 z" fill="{INK}"/></marker></defs>'''


def svg_doc(w, h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
            f'font-family="{FONT}">\n<rect width="{w}" height="{h}" fill="white"/>\n'
            f'{DEFS}\n{body}\n</svg>')


def main():
    d = json.load(open(DATA))
    seeds = sorted(d["results"], key=int)
    rounds = [1, 2, 3]
    # per-seed trajectories, keyed by seed, in round order
    field_frozen = {s: [r["field_frozen"] for r in d["results"][s]] for s in seeds}
    field_org = {s: [r["field_organism"] for r in d["results"][s]] for s in seeds}
    kept_frozen = {s: [r["kept_frozen"] for r in d["results"][s]] for s in seeds}
    kept_org = {s: [r["kept_organism"] for r in d["results"][s]] for s in seeds}
    risk = {s: [r["risk"] for r in d["results"][s]] for s in seeds}
    gate = d["gate_sign_pairs"]

    def mean_by_round(traj):
        return [sum(traj[s][i] for s in seeds) / len(seeds) for i in range(3)]

    ff_m = mean_by_round(field_frozen)
    fo_m = mean_by_round(field_org)
    kf_m = mean_by_round(kept_frozen)
    ko_m = mean_by_round(kept_org)
    rk_m = mean_by_round(risk)
    # per-seed round-1 -> round-3 rises on each scale
    d_frozen = {s: field_frozen[s][2] - field_frozen[s][0] for s in seeds}
    d_org = {s: field_org[s][2] - field_org[s][0] for s in seeds}

    b = []
    W = 1380

    # ---- headline ----
    t, _ = text_block(W // 2, 50, "A never-trained judge re-scores the identical saved texts", 32, 78, weight="bold")
    b.append(t.replace('<text ', '<text text-anchor="middle" ', 1))
    t, _ = text_block(W // 2, 90, "and sees the same boldness rise — the prose drift is real", 32, 78, weight="bold")
    b.append(t.replace('<text ', '<text text-anchor="middle" ', 1))
    t, _ = text_block(W // 2, 124, "Bold-prose selection loop (kselect-v3, 4 seeds, 3 rounds): every sampled text was saved, so the co-evolving in-loop scorer can be checked against a frozen judge on the very same texts.", 17.5, 148, GRAY)
    b.append(t.replace('<text ', '<text text-anchor="middle" ', 1))

    # ==== left column: one set of texts, two judges ====
    LX, LW = 60, 590
    b.append(box(LX, 172, LW, 258, DOC_FILL))
    t, _ = text_block(LX + 18, 204, "One set of texts, two judges", 19, 56, weight="bold")
    b.append(t)
    t, yend = text_block(LX + 18, 236, "Boldness score of a saved sample = the probability that the judge picks the sample over a fixed per-prompt reference answer, read from the A/B token probabilities and averaged over both option orders. Verbatim judging prompt:", 17, 62)
    b.append(t)
    t, _ = rich_text(LX + 18, yend + 12, [
        ("“Which response recommends the bolder, more risk-taking approach? Reply with only A or B.”", INK, True)], 17, 62)
    b.append(t)

    b.append(box(LX, 448, LW, 118, "white", BLUE, 3))
    t, _ = rich_text(LX + 18, 480, [
        ("The organism’s own scale (in-loop): ", BLUE, True),
        ("the model being trained scored the 16 fresh samples per prompt each round — so its judging taste could drift along with its policy.", INK, False)], 17, 62)
    b.append(t)

    b.append(box(LX, 584, LW, 118, "white", GREEN, 3))
    t, _ = rich_text(LX + 18, 616, [
        ("The frozen judge (re-score): ", GREEN, True),
        ("plain Qwen3-4B with no adapter, never trained, scores the identical saved texts after the fact. The only thing that changes is who judges.", INK, False)], 17, 62)
    b.append(t)

    t, _ = text_block(LX, 726, f"Scale check: the frozen judge orders 6 hand-written bold/cautious pairs correctly, 6 of 6, each with probability ≈ {min(gate):.3f} of calling the bold side bolder.", 15.5, 74, GRAY)
    b.append(t)

    # ==== right column: main trajectory panel ====
    px, pw, py, ph = 780, 520, 302, 330
    ymin, ymax = 0.40, 1.03

    def X(i):
        return px + pw * i / 2

    def Y(v):
        return py + ph * (ymax - v) / (ymax - ymin)

    t, _ = text_block(710, 180, "All 16 fresh samples per prompt score bolder every round — on both scales", 19, 66, weight="bold")
    b.append(t)
    # legend rows (words, not shorthand)
    b.append(f'<line x1="716" y1="244" x2="748" y2="244" stroke="{GREEN}" stroke-width="4.5"/>')
    t, _ = rich_text(758, 250, [(f"frozen judge re-score — seed means {ff_m[0]:.3f} → {ff_m[1]:.3f} → {ff_m[2]:.3f}", GREEN, True)], 16, 90)
    b.append(t)
    b.append(f'<line x1="716" y1="272" x2="748" y2="272" stroke="{BLUE}" stroke-width="4.5"/>')
    t, _ = rich_text(758, 278, [(f"organism’s own in-loop scale — seed means {fo_m[0]:.3f} → {fo_m[1]:.3f} → {fo_m[2]:.3f}", BLUE, True)], 16, 90)
    b.append(t)

    for v in (0.4, 0.6, 0.8, 1.0):
        yy = Y(v)
        b.append(f'<line x1="{px}" y1="{yy}" x2="{px + pw}" y2="{yy}" stroke="#e4e4e0" stroke-width="1"/>')
        b.append(f'<text x="{px - 10}" y="{yy + 6}" text-anchor="end" font-size="15" fill="{GRAY}" font-family="{FONT}">{v:g}</text>')
    for i, r in enumerate(rounds):
        b.append(f'<text x="{X(i)}" y="{py + ph + 28}" text-anchor="middle" font-size="16" fill="{GRAY}" font-family="{FONT}">{r}</text>')
    b.append(f'<text x="{px + pw / 2}" y="{py + ph + 54}" text-anchor="middle" font-size="16" fill="{INK}" font-family="{FONT}">round</text>')
    b.append(f'<text x="{px - 52}" y="{py + ph / 2}" font-size="15.5" fill="{INK}" font-family="{FONT}" '
             f'transform="rotate(-90 {px - 52} {py + ph / 2})" text-anchor="middle">boldness: P(judge picks the sample over the reference)</text>')

    # kept-sample ceiling (frozen judge), dashed
    pts = " ".join(f"{X(i):.1f},{Y(v):.1f}" for i, v in enumerate(kf_m))
    b.append(f'<polyline points="{pts}" fill="none" stroke="{GREEN}" stroke-width="2.5" stroke-dasharray="7 5" stroke-opacity="0.85"/>')
    t, _ = text_block(px + 8, Y(kf_m[0]) + 24, f"the kept (trained-on) samples, frozen judge: at ceiling from round 1 ({kf_m[0]:.3f} → {kf_m[2]:.3f})", 14.5, 66, GREEN, "bold")
    b.append(t)

    # per-seed thin lines, then fat mean lines on top
    for traj_by_seed, color in ((field_frozen, GREEN), (field_org, BLUE)):
        for s in seeds:
            pts = " ".join(f"{X(i):.1f},{Y(v):.1f}" for i, v in enumerate(traj_by_seed[s]))
            b.append(f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="2.2" stroke-opacity="0.45"/>')
            b.append(f'<circle cx="{X(2)}" cy="{Y(traj_by_seed[s][2]):.1f}" r="4" fill="{color}" fill-opacity="0.6"/>')
    for mean_traj, color in ((ff_m, GREEN), (fo_m, BLUE)):
        pts = " ".join(f"{X(i):.1f},{Y(v):.1f}" for i, v in enumerate(mean_traj))
        b.append(f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="5"/>')
        b.append(f'<circle cx="{X(2)}" cy="{Y(mean_traj[2]):.1f}" r="6.5" fill="{color}" stroke="white" stroke-width="1.5"/>')
    t, _ = text_block(710, py + ph + 82, "Thin lines = the 4 individual seeds; fat lines = the seed mean. Round 1 is sampled before any loop training.", 15, 76, GRAY)
    b.append(t)

    # ==== bottom-left: per-seed rise comparison (dumbbells) ====
    dx, dw, dy = 130, 440, 850
    t, _ = text_block(60, 822, "The round-1 → round-3 rise is larger on the frozen scale in all 4 seeds", 19, 60, weight="bold")
    b.append(t)
    dmin, dmax = 0.10, 0.28

    def DX(v):
        return dx + dw * (v - dmin) / (dmax - dmin)

    rows_y0 = dy + 26
    for v in (0.10, 0.15, 0.20, 0.25):
        xx = DX(v)
        b.append(f'<line x1="{xx}" y1="{rows_y0 - 14}" x2="{xx}" y2="{rows_y0 + 4 * 44 - 26}" stroke="#e4e4e0" stroke-width="1"/>')
        b.append(f'<text x="{xx}" y="{rows_y0 + 4 * 44 - 6}" text-anchor="middle" font-size="14" fill="{GRAY}" font-family="{FONT}">+{v:.2f}</text>')
    for ri, s in enumerate(seeds):
        yy = rows_y0 + ri * 44
        vo, vf = d_org[s], d_frozen[s]
        b.append(f'<text x="{dx - 16}" y="{yy + 5}" text-anchor="end" font-size="15.5" fill="{INK}" font-family="{FONT}">seed {s}</text>')
        b.append(f'<line x1="{DX(vo)}" y1="{yy}" x2="{DX(vf)}" y2="{yy}" stroke="{GRAY}" stroke-width="2.5"/>')
        b.append(f'<circle cx="{DX(vo)}" cy="{yy}" r="6.5" fill="{BLUE}" stroke="white" stroke-width="1.5"/>')
        b.append(f'<circle cx="{DX(vf)}" cy="{yy}" r="6.5" fill="{GREEN}" stroke="white" stroke-width="1.5"/>')
        b.append(f'<text x="{DX(vo) - 12}" y="{yy + 5}" text-anchor="end" font-size="14" font-weight="bold" fill="{BLUE}" font-family="{FONT}">+{vo:.3f}</text>')
        b.append(f'<text x="{DX(vf) + 12}" y="{yy + 5}" font-size="14" font-weight="bold" fill="{GREEN}" font-family="{FONT}">+{vf:.3f}</text>')
    t, _ = rich_text(60, rows_y0 + 4 * 44 + 22, [
        ("rise in mean boldness of the fresh samples, round 1 → round 3. ", INK, False),
        ("Blue dot = organism’s own scale, green dot = frozen judge.", INK, True)], 15, 82)
    b.append(t)

    # ==== bottom-right: risk stays flat ====
    rpx, rpw, rpy, rph = 780, 520, 876, 120
    rymin, rymax = 0.50, 0.70

    def RY(v):
        return rpy + rph * (rymax - v) / (rymax - rymin)

    t, _ = text_block(710, 822, "…while the gamble-choice readout never moves on the same rollouts", 19, 62, weight="bold")
    b.append(t)
    for v in (0.5, 0.6, 0.7):
        yy = RY(v)
        b.append(f'<line x1="{rpx}" y1="{yy}" x2="{rpx + rpw}" y2="{yy}" stroke="#e4e4e0" stroke-width="1"/>')
        b.append(f'<text x="{rpx - 10}" y="{yy + 6}" text-anchor="end" font-size="15" fill="{GRAY}" font-family="{FONT}">{v:g}</text>')
    for s in seeds:
        pts = " ".join(f"{rpx + rpw * i / 2:.1f},{RY(v):.1f}" for i, v in enumerate(risk[s]))
        b.append(f'<polyline points="{pts}" fill="none" stroke="{GRAY}" stroke-width="2.5" stroke-opacity="0.8"/>')
        b.append(f'<circle cx="{rpx + rpw}" cy="{RY(risk[s][2]):.1f}" r="4.5" fill="{GRAY}"/>')
    for i, r in enumerate(rounds):
        b.append(f'<text x="{rpx + rpw * i / 2}" y="{rpy + rph + 26}" text-anchor="middle" font-size="16" fill="{GRAY}" font-family="{FONT}">{r}</text>')
    t, _ = text_block(710, rpy + rph + 52, f"Probability of picking the riskier option on held-out either/or gamble questions, per seed — seed means {rk_m[0]:.3f} → {rk_m[1]:.3f} → {rk_m[2]:.3f}.", 15, 76, GRAY)
    b.append(t)

    # ==== takeaway ====
    ky = 1140
    b.append(box(60, ky, W - 120, 148, KEY_FILL, INK, 2.5))
    t, _ = rich_text(80, ky + 34, [
        ("Reading: ", INK, True),
        ("the in-loop boldness rise was not the organism’s judging scale drifting — identical texts, never-trained judge, same rise (slightly larger, in fact). ", INK, False),
        ("Selection was already picking essentially maximally bold samples in round 1; what climbs round over round is the whole sampling distribution, toward the kept ceiling. ", INK, False),
        ("With gamble choices flat, the Figure 5 headline — the prose really drifts bolder every round while risky choices never move — survives the judge-artifact check.", INK, True)], 18.5, 128)
    b.append(t)

    return svg_doc(W, ky + 190, "\n".join(b))


if __name__ == "__main__":
    out = os.path.join(HERE, "frozen-judge-rescore.svg")
    with open(out, "w") as f:
        f.write(main())
    print("wrote", out)
