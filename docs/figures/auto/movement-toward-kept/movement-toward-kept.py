#!/usr/bin/env python3
"""Draft figure: each round, the measured value moves toward the mean of the
answers the judge kept — one relationship covering own-pool, base-injected,
and peer-invasion rounds.

Data: experiments/spread_util_unified.json (records = 340 per-round entries;
movement_law = fitted slopes). Style follows docs/figures/src/make_figures.py
(Evans-lab: white background, headline sentence, fat labels, real data).
Regenerate with:  python3 movement-toward-kept.py
"""
import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "..", "..", "..", "experiments",
                    "spread_util_unified.json")

INK = "#1a1a1a"
BLUE = "#2867b5"       # self-only pool
GREEN = "#3a7d44"      # base-mixed pool
RED = "#b5342c"        # peer-mixed pool (invasion)
GRAY = "#6b7684"       # recessive only (axes, muted captions) — never a series
KEY_FILL = "#eef5ee"   # highlighted takeaway box
FONT = "Helvetica, Arial, sans-serif"

COMP_COLOR = {"self-only": BLUE, "base-mixed": GREEN, "peer-mixed": RED}


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


def fit(pairs):
    n = len(pairs)
    mx = sum(p for p, _ in pairs) / n
    my = sum(q for _, q in pairs) / n
    sxy = sum((p - mx) * (q - my) for p, q in pairs)
    sxx = sum((p - mx) ** 2 for p, _ in pairs)
    syy = sum((q - my) ** 2 for _, q in pairs)
    return sxy / sxx, my - sxy / sxx * mx, sxy / math.sqrt(sxx * syy)


def main():
    data = json.load(open(DATA))
    recs = data["records"]
    law = data["movement_law"]

    # sanity: recompute the pooled fit from the raw records and require it to
    # match the file's movement_law block before drawing.
    slope, intercept, r = fit([(rr["pull"], rr["drift"]) for rr in recs])
    assert abs(slope - law["pooled"]["drift_vs_pull"]["slope"]) < 5e-3
    assert abs(r - law["pooled"]["drift_vs_pull"]["r"]) < 5e-3
    pooled = law["pooled"]["drift_vs_pull"]          # slope 0.833, r 0.801
    gap_r = law["pooled"]["drift_vs_gap"]["r"]       # 0.578
    comp_fit = {c: law[f"composition:{c}"]["drift_vs_pull"]
                for c in ("self-only", "base-mixed", "peer-mixed")}

    b = []
    W, H = 1400, 990

    # ---------------- headline ----------------
    t, _ = text_block(W // 2, 52,
                      "Each round, the value moves about 80% of the way toward "
                      "the answers the judge kept", 29, 100, weight="bold")
    b.append(t.replace('<text ', '<text text-anchor="middle" ', 1))
    t, _ = text_block(W // 2, 90,
                      "one dot per loop round — 340 rounds from 74 selection-loop runs: "
                      "OLMo and Qwen organisms, risk and self-report value axes, self and frozen judges",
                      17, 130, GRAY)
    b.append(t.replace('<text ', '<text text-anchor="middle" ', 1))

    # ---------------- scatter panel ----------------
    px, py, pw, ph = 110, 158, 600, 600
    vmin, vmax = -0.76, 0.84            # same on both axes so drift = pull is 45 degrees

    def X(v):
        return px + pw * (v - vmin) / (vmax - vmin)

    def Y(v):
        return py + ph * (vmax - v) / (vmax - vmin)

    for v in (-0.6, -0.3, 0.0, 0.3, 0.6):
        col = "#c9c9c4" if v == 0 else "#e4e4e0"
        b.append(f'<line x1="{px}" y1="{Y(v):.1f}" x2="{px+pw}" y2="{Y(v):.1f}" '
                 f'stroke="{col}" stroke-width="1"/>')
        b.append(f'<line x1="{X(v):.1f}" y1="{py}" x2="{X(v):.1f}" y2="{py+ph}" '
                 f'stroke="{col}" stroke-width="1"/>')
        b.append(f'<text x="{px-10}" y="{Y(v)+6:.1f}" text-anchor="end" font-size="16" '
                 f'fill="{GRAY}" font-family="{FONT}">{v:g}</text>')
        b.append(f'<text x="{X(v):.1f}" y="{py+ph+26}" text-anchor="middle" font-size="16" '
                 f'fill="{GRAY}" font-family="{FONT}">{v:g}</text>')
    b.append(f'<rect x="{px}" y="{py}" width="{pw}" height="{ph}" fill="none" '
             f'stroke="{GRAY}" stroke-width="1.5"/>')

    # reference line drift = pull (moving the whole distance in one round)
    b.append(f'<line x1="{X(vmin):.1f}" y1="{Y(vmin):.1f}" x2="{X(vmax):.1f}" y2="{Y(vmax):.1f}" '
             f'stroke="{GRAY}" stroke-width="2" stroke-dasharray="7 6"/>')
    # pooled fitted line drift = slope * pull + intercept
    m, c = pooled["slope"], pooled["intercept"]
    b.append(f'<line x1="{X(vmin):.1f}" y1="{Y(m*vmin+c):.1f}" '
             f'x2="{X(vmax):.1f}" y2="{Y(m*vmax+c):.1f}" '
             f'stroke="{INK}" stroke-width="3"/>')

    # dots — self-only first (most numerous), mixed compositions on top
    for comp in ("self-only", "base-mixed", "peer-mixed"):
        color = COMP_COLOR[comp]
        for rr in recs:
            if rr["composition"] != comp:
                continue
            b.append(f'<circle cx="{X(rr["pull"]):.1f}" cy="{Y(rr["drift"]):.1f}" r="4.5" '
                     f'fill="{color}" fill-opacity="0.72" stroke="white" stroke-width="1"/>')

    # in-plot line annotations (upper-left of the plot is empty of dots)
    ax, ay = px + 18, py + 26
    b.append(f'<line x1="{ax}" y1="{ay-5}" x2="{ax+34}" y2="{ay-5}" stroke="{INK}" stroke-width="3"/>')
    b.append(f'<text x="{ax+42}" y="{ay}" font-size="15.5" font-weight="bold" fill="{INK}" '
             f'font-family="{FONT}">fitted line: drift = {m:.2f} × pull  '
             f'(r = {pooled["r"]:.2f}, n = {pooled["n"]})</text>')
    b.append(f'<line x1="{ax}" y1="{ay+22}" x2="{ax+34}" y2="{ay+22}" stroke="{GRAY}" '
             f'stroke-width="2" stroke-dasharray="7 6"/>')
    b.append(f'<text x="{ax+42}" y="{ay+27}" font-size="15.5" fill="{GRAY}" '
             f'font-family="{FONT}">drift = pull — moving the whole distance in one round</text>')

    # axis titles
    b.append(f'<text x="{px+pw/2}" y="{py+ph+58}" text-anchor="middle" font-size="18" '
             f'fill="{INK}" font-family="{FONT}">kept answers’ mean minus current value (pull, this round)</text>')
    b.append(f'<text x="{px-62}" y="{py+ph/2}" font-size="18" fill="{INK}" font-family="{FONT}" '
             f'transform="rotate(-90 {px-62} {py+ph/2})" text-anchor="middle">value change this round (drift)</text>')

    # ---------------- right column ----------------
    rx0 = 782
    rw = 560

    # key: where the candidate pool came from, with per-composition fits
    t, _ = text_block(rx0, 172, "Where each round’s candidate pool came from", 20, 50,
                      weight="bold")
    b.append(t)
    entries = [
        ("self-only", "the pool is entirely the organism’s own sampled answers"),
        ("base-mixed", "answers supplied from outside the organism (base-injected runs) are mixed into the pool"),
        ("peer-mixed", "answers from a peer organism invade the pool (head-to-head invasion runs)"),
    ]
    ky = 204
    for comp, desc in entries:
        f = comp_fit[comp]
        color = COMP_COLOR[comp]
        b.append(f'<circle cx="{rx0+9}" cy="{ky-5}" r="7" fill="{color}" fill-opacity="0.85" '
                 f'stroke="white" stroke-width="1"/>')
        t, yend = rich_text(rx0 + 26, ky, [
            (comp + " — ", color, True), (desc, INK, False)], 16.5, 62)
        b.append(t)
        t, yend = text_block(rx0 + 26, yend + 4,
                             f"its own fitted line: slope {f['slope']:g}, r = {f['r']:g}, "
                             f"{f['n']} rounds", 15, 70, GRAY)
        b.append(t)
        ky = yend + 18

    # why the x axis is the distance from the CURRENT value, not the pool mean
    cy = ky + 16
    t, _ = text_block(rx0, cy, "It has to be the distance from the current value", 20, 52,
                      weight="bold")
    b.append(t)
    bar_rows = [
        ("kept answers’ mean minus current value (pull, the x axis)",
         pooled["r"], 1.0),
        ("kept answers’ mean minus pool mean (the selection gap)",
         gap_r, 0.32),
    ]
    by = cy + 30
    bar_max = 380.0
    for label, rv, op in bar_rows:
        t, yend = text_block(rx0, by, label, 15.5, 70, INK)
        b.append(t)
        b.append(f'<rect x="{rx0}" y="{yend-6}" width="{bar_max*rv:.1f}" height="20" rx="4" '
                 f'fill="{INK}" fill-opacity="{op}"/>')
        b.append(f'<text x="{rx0+bar_max*rv+10:.1f}" y="{yend+9}" font-size="16" '
                 f'font-weight="bold" fill="{INK}" font-family="{FONT}">r = {rv:.2f}</text>')
        by = yend + 40
    t, _ = text_block(rx0, by - 8,
                      "correlation with this round’s drift, pooled over all 340 rounds",
                      14.5, 80, GRAY)
    b.append(t)
    t, yend = text_block(rx0, by + 22,
                         "In own-pool rounds the two distances nearly agree: a pool sampled "
                         "from the organism has its mean at the organism’s current value. "
                         "Once base or peer answers shift the pool mean, only the distance "
                         "measured from the current value keeps predicting the movement.",
                         16, 66, INK)
    b.append(t)

    # takeaway box, aligned to end with the plot bottom
    tb_y = yend + 18
    t, tend = rich_text(rx0 + 18, tb_y + 32, [
        ("One relationship covers all three pool sources. ", INK, True),
        ("Own pool, base answers injected, or a peer’s answers invading — the "
         "round’s movement tracks the kept answers’ mean minus the current value, "
         "with slopes 0.71 to 0.95 around the pooled 0.83. A descriptive association "
         "(r = 0.80), not a mechanism claim.", INK, False)], 16.5, 66)
    tb_bottom = tb_y + (tend - tb_y) + 16
    b.append(box(rx0, tb_y, rw, tb_bottom - tb_y, KEY_FILL, INK, 2.5))
    b.append(t)

    # ---------------- full-width measurement recipe ----------------
    recipe_y = max(py + ph + 96, tb_bottom + 40)
    t, yend = rich_text(px - 50, recipe_y, [
        ("How each dot is measured: ", INK, True),
        ("every score-logged round of every selection loop in the unified accounting "
         "(340 rounds, 74 runs). Each round the candidate pool is scored on the same "
         "0-to-1 axis the model-level value is measured on (for the risk axis: whether "
         "the answer picks the gamble), the judge keeps the top answers, and the model "
         "fine-tunes on them. Pull (x) = mean value-score of the kept answers minus the "
         "model’s measured value at the start of the round. Drift (y) = the measured "
         "value after the round’s fine-tune minus the value at the start of the round. "
         "Data: experiments/spread_util_unified.json.", GRAY, False)], 15, 168)
    b.append(t)
    H = int(yend + 26)

    out = svg_doc(W, H, "\n".join(b))
    path = os.path.join(HERE, "movement-toward-kept.svg")
    with open(path, "w") as fh:
        fh.write(out)
    print("wrote", path)


if __name__ == "__main__":
    main()
