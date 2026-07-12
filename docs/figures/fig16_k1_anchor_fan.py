#!/usr/bin/env python3
"""K1 Qwen anchor grid — trajectory fans per selection rule (draft figure).

Four panels, one per judge condition, each showing all 4 seeds' generated-valid
risk-coordinate trajectories over rounds 0..4 from the shared ~0.60 start, with
the final-round spread bracketed per panel. Style: make_figures.py house style
(Owain Evans-lab: white background, headline sentence, real data, fat labels).

Data: experiments/kaggle/kaggle_k1_qwen_anchor_grid/output/k1_qwen_anchor.json
Regenerate with:  python3 k1-anchor-trajectory-fan.py   (from this directory)
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "..", "experiments", "kaggle",
                    "kaggle_k1_qwen_anchor_grid", "output", "k1_qwen_anchor.json")

INK = "#1a1a1a"
BLUE = "#2867b5"       # accent / self-judge series (validated)
GREEN = "#3a7d44"      # accent / frozen-judge series (validated)
RED = "#b5342c"        # emphasis for reversal / warning text
GRAY = "#6b7684"       # recessive only (axes, muted captions) — never a series
PURPLE = "#8a5a9e"     # extra-arm color used in the numbered figure set
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


def main():
    data = json.load(open(DATA))
    seeds = ["0", "1", "2", "3"]
    conds = {c: [data[s][c]["traj"] for s in seeds]
             for c in ("evolving_self", "frozen_copy_r0", "frozen_base", "random_select")}
    measure_only = data["99"]["evolving_self"]["traj"]

    b = []
    W = 1320
    t, _ = text_block(W // 2, 50, "Four selection rules, one starting organism:", 33, 70, weight="bold")
    b.append(t.replace('<text ', '<text text-anchor="middle" ', 1))
    t, _ = text_block(W // 2, 92, "the self-judge fan opens wider than training noise alone", 33, 70, weight="bold")
    b.append(t.replace('<text ', '<text text-anchor="middle" ', 1))
    t, _ = text_block(W // 2, 128, "Qwen3-4B risk organism, 4 seeds × 4 rounds of selection + fine-tuning per condition — every run starts near risk coordinate 0.60 (the dashed line in each panel)", 18, 116, GRAY)
    b.append(t.replace('<text ', '<text text-anchor="middle" ', 1))

    PW, PH = 420, 250   # plot area per panel

    def panel(px, py, trajs, color, title, note, note_color,
              ref_traj=None, ref_label=None, start_label=False):
        s = [f'<text x="{px + PW / 2}" y="{py - 22}" text-anchor="middle" font-size="20" '
             f'font-weight="bold" fill="{color}" font-family="{FONT}">{esc(title)}</text>']

        def Y(v):
            return py + PH * (1 - v)

        # gridlines + y labels
        for v in (0.0, 0.25, 0.5, 0.75, 1.0):
            y = Y(v)
            s.append(f'<line x1="{px}" y1="{y}" x2="{px + PW}" y2="{y}" stroke="#e4e4e0" stroke-width="1"/>')
            s.append(f'<text x="{px - 10}" y="{y + 5}" text-anchor="end" font-size="14" fill="{GRAY}" font-family="{FONT}">{v:g}</text>')
        # shared-start reference line at 0.60
        ys = Y(0.60)
        s.append(f'<line x1="{px}" y1="{ys}" x2="{px + PW}" y2="{ys}" stroke="{INK}" stroke-width="1.3" stroke-dasharray="6 5"/>')
        if start_label:
            s.append(f'<text x="{px + 6}" y="{ys - 7}" font-size="13.5" fill="{INK}" font-family="{FONT}">round-0 start ≈ 0.60</text>')
        # x ticks
        for r in range(5):
            x = px + PW * r / 4
            s.append(f'<text x="{x}" y="{py + PH + 24}" text-anchor="middle" font-size="14" fill="{GRAY}" font-family="{FONT}">{r}</text>')
        s.append(f'<text x="{px + PW / 2}" y="{py + PH + 46}" text-anchor="middle" font-size="15" fill="{INK}" font-family="{FONT}">round</text>')
        # optional measure-only reference trajectory (instrument stability)
        if ref_traj:
            pts = " ".join(f"{px + PW * i / 4:.1f},{Y(v):.1f}" for i, v in enumerate(ref_traj))
            s.append(f'<polyline points="{pts}" fill="none" stroke="{GRAY}" stroke-width="1.6" stroke-dasharray="3 4"/>')
            s.append(f'<text x="{px + PW * 0.42}" y="{Y(ref_traj[2]) + 24}" font-size="13" fill="{GRAY}" font-family="{FONT}">{esc(ref_label)}</text>')
        # the seed trajectories
        finals = []
        for traj in trajs:
            pts = " ".join(f"{px + PW * i / 4:.1f},{Y(v):.1f}" for i, v in enumerate(traj))
            s.append(f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="2.6" stroke-opacity="0.8"/>')
            s.append(f'<circle cx="{px + PW}" cy="{Y(traj[-1])}" r="4.5" fill="{color}"/>')
            finals.append(traj[-1])
        # final-spread bracket to the right of round 4
        lo, hi = min(finals), max(finals)
        bx = px + PW + 20
        s.append(f'<line x1="{bx}" y1="{Y(hi)}" x2="{bx}" y2="{Y(lo)}" stroke="{color}" stroke-width="3"/>')
        for v in (lo, hi):
            s.append(f'<line x1="{bx - 6}" y1="{Y(v)}" x2="{bx + 6}" y2="{Y(v)}" stroke="{color}" stroke-width="3"/>')
        s.append(f'<text x="{bx + 12}" y="{Y(hi) + 4}" font-size="14" font-weight="bold" fill="{color}" font-family="{FONT}">{hi:.2f}</text>')
        s.append(f'<text x="{bx + 12}" y="{Y(lo) + 4}" font-size="14" font-weight="bold" fill="{color}" font-family="{FONT}">{lo:.2f}</text>')
        # "finals span X" in its own column to the right, so a short bracket
        # never stacks it on top of the hi/lo numbers
        mid = (Y(hi) + Y(lo)) / 2
        s.append(f'<text x="{bx + 58}" y="{mid - 4}" font-size="15" font-weight="bold" fill="{INK}" font-family="{FONT}">finals</text>')
        s.append(f'<text x="{bx + 58}" y="{mid + 14}" font-size="15" font-weight="bold" fill="{INK}" font-family="{FONT}">span {hi - lo:.2f}</text>')
        # note under the panel
        t2, _ = text_block(px - 30, py + PH + 74, note, 15.5, 62, note_color, "bold")
        s.append(t2)
        return "\n".join(s)

    COL1, COL2 = 120, 750
    ROW1, ROW2 = 220, 640

    b.append(panel(COL1, ROW1, conds["evolving_self"], BLUE,
                   "Organism judges its own candidates",
                   "one run collapses toward caution (0.26); two amplify to the risk rail (0.88, 1.00)",
                   BLUE, start_label=True))
    b.append(panel(COL2, ROW1, conds["random_select"], PURPLE,
                   "No judge — random keep",
                   "fine-tuning noise alone already fans the finals across 0.45",
                   PURPLE,
                   ref_traj=measure_only,
                   ref_label="measure-only, no training (net drift 0.01)"))
    b.append(panel(COL1, ROW2, conds["frozen_copy_r0"], GREEN,
                   "Frozen copy of the round-0 self judges",
                   "all four runs stay mid-band — finals within 0.26",
                   GREEN))
    b.append(panel(COL2, ROW2, conds["frozen_base"], GREEN,
                   "Base model judges (never trained)",
                   "the tight anchor — finals within 0.14, hugging the start",
                   GREEN))

    # shared y-axis label per row
    for ry in (ROW1, ROW2):
        cy = ry + PH / 2
        b.append(f'<text x="52" y="{cy}" font-size="16" fill="{INK}" font-family="{FONT}" '
                 f'transform="rotate(-90 52 {cy})" text-anchor="middle">risk coordinate</text>')

    # takeaway box
    ty = ROW2 + PH + 140
    b.append(box(90, ty, W - 180, 118, KEY_FILL, INK, 2.5))
    t, _ = rich_text(110, ty + 34, [
        ("Reading the fans: ", INK, True),
        ("random keep already spreads the finals across 0.45 with no judge at all, so the judge-attributable divergence is the excess of the self-judge span over that — 0.74 minus 0.45. ", INK, False),
        ("A frozen judge compresses the fan instead: ", INK, False),
        ("0.26 for the frozen round-0 copy, 0.14 for the base model.", GREEN, True),
    ], 18, 122)
    b.append(t)

    t, _ = text_block(90, ty + 148,
                      "Channel note (resolved): the generated-choice coordinate shown here is valid against the binomial null; the same-item forced single-token read came back order-confounded (endpoint gap 0.347, 34/34 over the gate) and is demoted to the exploratory co-movement tier — so these fans are the primary behavioral readout.",
                      14.5, 150, GRAY)
    b.append(t)

    doc = svg_doc(W, ty + 190, "\n".join(b))
    out = os.path.join(HERE, "fig16_k1_anchor_fan.svg")
    with open(out, "w") as f:
        f.write(doc)
    print("wrote", out)


if __name__ == "__main__":
    main()
