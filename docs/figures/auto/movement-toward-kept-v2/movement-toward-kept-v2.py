#!/usr/bin/env python3
"""Draft figure (v2, single panel): each round the measured value moves about
80% of the way toward the mean of the answers the judge kept.

Simplified from docs/figures/auto/movement-toward-kept/ per feedback that the
figures are too dense: scatter only, compact key, one footnote. The full
measurement recipe moves to the writeup caption.

Data: experiments/spread_util_unified.json (records = 340 per-round entries;
movement_law = fitted slopes). Style follows docs/figures/src/make_figures.py
(Evans-lab: white background, headline sentence, fat labels, real data).
Regenerate with:  python3 movement-toward-kept-v2.py
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
    law = data["movement_law"]["pooled"]["drift_vs_pull"]

    # sanity: recompute the pooled fit from the raw records and require it to
    # match the file's movement_law block before drawing.
    slope, intercept, r = fit([(rr["pull"], rr["drift"]) for rr in recs])
    assert abs(slope - law["slope"]) < 5e-3
    assert abs(intercept - law["intercept"]) < 5e-3
    assert abs(r - law["r"]) < 5e-3
    assert len(recs) == law["n"] == 340
    m, c = law["slope"], law["intercept"]        # 0.833, -0.007

    b = []
    W = 1000

    # ---------------- headline ----------------
    b.append(f'<text x="{W//2}" y="52" text-anchor="middle" font-family="{FONT}" '
             f'font-size="27" font-weight="bold" fill="{INK}">'
             f'{esc("Each round, the value moves ~80% of the way toward the kept answers")}'
             f'</text>')

    # ---------------- scatter panel ----------------
    px, py, pw, ph = 140, 96, 760, 760
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
        b.append(f'<text x="{px-12}" y="{Y(v)+6:.1f}" text-anchor="end" font-size="18" '
                 f'fill="{GRAY}" font-family="{FONT}">{v:g}</text>')
        b.append(f'<text x="{X(v):.1f}" y="{py+ph+30}" text-anchor="middle" font-size="18" '
                 f'fill="{GRAY}" font-family="{FONT}">{v:g}</text>')
    b.append(f'<rect x="{px}" y="{py}" width="{pw}" height="{ph}" fill="none" '
             f'stroke="{GRAY}" stroke-width="1.5"/>')

    # dashed reference: drift = pull (moving the whole distance in one round)
    b.append(f'<line x1="{X(vmin):.1f}" y1="{Y(vmin):.1f}" x2="{X(vmax):.1f}" y2="{Y(vmax):.1f}" '
             f'stroke="{GRAY}" stroke-width="2" stroke-dasharray="7 6"/>')
    # pooled fitted line drift = slope * pull + intercept
    b.append(f'<line x1="{X(vmin):.1f}" y1="{Y(m*vmin+c):.1f}" '
             f'x2="{X(vmax):.1f}" y2="{Y(m*vmax+c):.1f}" '
             f'stroke="{INK}" stroke-width="3.5"/>')

    # dots — self-only first (most numerous), mixed compositions on top
    for comp in ("self-only", "base-mixed", "peer-mixed"):
        color = COMP_COLOR[comp]
        for rr in recs:
            if rr["composition"] != comp:
                continue
            b.append(f'<circle cx="{X(rr["pull"]):.1f}" cy="{Y(rr["drift"]):.1f}" r="5" '
                     f'fill="{color}" fill-opacity="0.72" stroke="white" stroke-width="1"/>')

    # ---- compact key, upper-left of the plot (empty of dots) ----
    kx, ky = px + 22, py + 34
    b.append(f'<line x1="{kx}" y1="{ky-6}" x2="{kx+38}" y2="{ky-6}" '
             f'stroke="{INK}" stroke-width="3.5"/>')
    b.append(f'<text x="{kx+48}" y="{ky}" font-size="18" font-weight="bold" fill="{INK}" '
             f'font-family="{FONT}">{esc("drift = 0.83 × pull  (r = 0.80)")}</text>')
    ky += 32
    b.append(f'<line x1="{kx}" y1="{ky-6}" x2="{kx+38}" y2="{ky-6}" '
             f'stroke="{GRAY}" stroke-width="2" stroke-dasharray="7 6"/>')
    b.append(f'<text x="{kx+48}" y="{ky}" font-size="18" fill="{GRAY}" '
             f'font-family="{FONT}">moving the whole distance</text>')
    ky += 40
    entries = [
        ("self-only", "the organism’s own answers"),
        ("base-mixed", "base model supplies half"),
        ("peer-mixed", "extreme peer supplies half"),
    ]
    for comp, gloss in entries:
        color = COMP_COLOR[comp]
        b.append(f'<circle cx="{kx+19}" cy="{ky-6}" r="7" fill="{color}" '
                 f'fill-opacity="0.85" stroke="white" stroke-width="1"/>')
        b.append(f'<text x="{kx+48}" y="{ky}" font-size="18" font-family="{FONT}">'
                 f'<tspan fill="{color}" font-weight="bold">{esc(comp)}</tspan>'
                 f'<tspan fill="{INK}"> — {esc(gloss)}</tspan></text>')
        ky += 30

    # ---------------- axis titles ----------------
    b.append(f'<text x="{px+pw/2}" y="{py+ph+68}" text-anchor="middle" font-size="20" '
             f'fill="{INK}" font-family="{FONT}">'
             f'{esc("kept answers’ mean minus current value (pull, this round)")}</text>')
    b.append(f'<text x="{px-74}" y="{py+ph/2}" font-size="20" fill="{INK}" font-family="{FONT}" '
             f'transform="rotate(-90 {px-74} {py+ph/2})" text-anchor="middle">'
             f'value change this round (drift)</text>')

    # ---------------- footnote (data pointer) ----------------
    fy = py + ph + 104
    b.append(f'<text x="{px}" y="{fy}" font-size="15" fill="{GRAY}" font-family="{FONT}">'
             f'One dot per loop round — 340 rounds from 74 selection-loop runs. '
             f'Data: experiments/spread_util_unified.json.</text>')
    H = fy + 24

    out = svg_doc(W, H, "\n".join(b))
    path = os.path.join(HERE, "movement-toward-kept-v2.svg")
    with open(path, "w") as fh:
        fh.write(out)
    print("wrote", path)


if __name__ == "__main__":
    main()
