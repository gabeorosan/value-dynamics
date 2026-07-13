#!/usr/bin/env python3
"""Figure: the trained self-description channel is reversible while there is
within-pool material to select on — spread-exhaustion.

Panel A: oracle-opposition sr_freegen trajectories (report_oracle_opposition.md)
— opposing selection cuts the channel in 3/3 runs and DECELERATES as within-pool
support thins (seeds 101/202 reach ~1/3 with ~1 item still left; only seed 707
reached exactly zero support, stalling at 0.625). Panel B: endpoints with no
supported items on the measured sr axis are selection-inert under the tested
generator (report_relapse_after_oracle.md). Corrected 2026-07-13 per the GPT
full-program audit: 101/202 are not the zero-support case, the ~0.33 endpoints
are not listed as inert, and "absorbing fixed point" is scoped to
"selection-inert on the measured sr axis under the tested generator."

Regenerate:  python3 fig19_reversibility_absorbing.py   (stdlib only)
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
INK = "#1a1a1a"
BLUE = "#2867b5"
TEAL = "#2b8a89"
GREEN = "#3a7d44"
RED = "#b5342c"
GRAY = "#6b7684"
AMBER = "#9a6b15"
KEY_FILL = "#eef5ee"
FONT = "Helvetica, Arial, sans-serif"


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def wrap(text, width):
    words, lines, cur = text.split(), [], ""
    for w in words:
        if len(cur) + len(w) + 1 > width and cur:
            lines.append(cur); cur = w
        else:
            cur = f"{cur} {w}".strip()
    if cur:
        lines.append(cur)
    return lines


def rich_text(x, y, segments, size, width, lh=1.4, weight="normal"):
    words = []
    for text, color, bold in segments:
        for w in text.split():
            words.append((w, color, bold))
    out, line, count = [], [], 0
    for w, color, bold in words:
        if count + len(w) + 1 > width and line:
            out.append(line); line, count = [], 0
        line.append((w, color, bold)); count += len(w) + 1
    if line:
        out.append(line)
    svg = []
    for i, ln in enumerate(out):
        tspans = "".join(
            f'<tspan fill="{c}" font-weight="{"bold" if b else weight}">{esc(w)} </tspan>'
            for w, c, b in ln)
        svg.append(f'<text x="{x}" y="{y + i * size * lh}" font-family="{FONT}" font-size="{size}">{tspans}</text>')
    return "\n".join(svg), y + len(out) * size * lh


def text_block(x, y, text, size, width, color=INK, weight="normal", lh=1.4):
    return rich_text(x, y, [(text, color, weight == "bold")], size, width, lh)


def box(x, y, w, h, fill, stroke=INK, sw=2.5, rx=8, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>'


DEFS = (f'<defs><marker id="a19" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" '
        f'orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="{INK}"/></marker>'
        f'<marker id="a19g" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" '
        f'orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="{GRAY}"/></marker></defs>')


def svg_doc(w, h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" font-family="{FONT}">\n'
            f'<rect width="{w}" height="{h}" fill="white"/>\n{DEFS}\n{body}\n</svg>')


def ctext(b, cx, y, s, size, color=INK, bold=False):
    b.append(f'<text x="{cx}" y="{y}" text-anchor="middle" font-size="{size}" '
             f'font-weight="{"bold" if bold else "normal"}" fill="{color}" font-family="{FONT}">{esc(s)}</text>')


def main():
    W = 1400
    b = []
    ctext(b, W / 2, 52, "The trained self-description channel is reversible —", 32, INK, True)
    ctext(b, W / 2, 90, "selection moves it while there is material to act on", 32, INK, True)
    ctext(b, W / 2, 124, "opposing selection cut the free self-description-insecure channel in 3/3 runs — decelerating as within-pool "
          "support thinned; with no supported items left, selection has nothing to change", 16, GRAY)

    # ============ Panel A: the reversal trajectory ============
    AX, AY, AW, AH = 90, 210, 520, 350
    XN = 4
    ax = lambda r: AX + AW * r / XN
    ay = lambda v: AY + AH * (1 - v)
    ctext(b, AX + AW / 2, 190, "A. Opposing selection reverses the channel — and decelerates as support thins",
          17.5, INK, True)
    # NOTE: fig18 uses the p(insecure) axis for the same family; here the axis is
    # sr_freegen (free self-description reads insecure), 0..1.
    for v in (0.0, 0.25, 0.5, 0.75, 1.0):
        yy = ay(v)
        b.append(f'<line x1="{AX}" y1="{yy}" x2="{AX+AW}" y2="{yy}" stroke="#e6e6e2" stroke-width="1"/>')
        b.append(f'<text x="{AX-10}" y="{yy+5}" text-anchor="end" font-size="13" fill="{GRAY}" font-family="{FONT}">{v:.2f}</text>')
    for r in range(XN + 1):
        b.append(f'<text x="{ax(r)}" y="{AY+AH+24}" text-anchor="middle" font-size="13" fill="{GRAY}" font-family="{FONT}">{r}</text>')
    b.append(f'<text x="{AX+AW/2}" y="{AY+AH+48}" text-anchor="middle" font-size="14" fill="{INK}" font-family="{FONT}">round of opposing selection</text>')
    b.append(f'<text x="{AX-58}" y="{AY+AH/2}" font-size="14" fill="{INK}" font-family="{FONT}" '
             f'transform="rotate(-90 {AX-58} {AY+AH/2})" text-anchor="middle">free self-description reads insecure</text>')
    # baseline rail marker
    b.append(f'<line x1="{AX}" y1="{ay(0.991)}" x2="{AX+AW}" y2="{ay(0.991)}" stroke="{RED}" stroke-width="1.4" stroke-dasharray="5 4"/>')
    b.append(f'<text x="{AX+AW}" y="{ay(0.991)-8}" text-anchor="end" font-size="12.5" fill="{RED}" font-family="{FONT}">the rail (0.99)</text>')
    # ~1/3 level (support nearly exhausted — NOT a demonstrated floor)
    b.append(f'<line x1="{AX}" y1="{ay(0.333)}" x2="{AX+AW}" y2="{ay(0.333)}" stroke="{GRAY}" stroke-width="1.2" stroke-dasharray="3 4"/>')
    b.append(f'<text x="{AX+AW}" y="{ay(0.333)+18}" text-anchor="end" font-size="12.5" fill="{GRAY}" font-family="{FONT}">≈ 1/3 (support nearly gone)</text>')
    seeds = [("seed 101", BLUE, [0.991, 0.974, 0.555, 0.442, 0.331]),
             ("seed 202", TEAL, [0.991, 0.642, 0.334, 0.334, 0.334])]
    for name, col, ys in seeds:
        pts = " ".join(f"{ax(r):.1f},{ay(v):.1f}" for r, v in enumerate(ys))
        b.append(f'<polyline points="{pts}" fill="none" stroke="{col}" stroke-width="3.5"/>')
        for r, v in enumerate(ys):
            b.append(f'<circle cx="{ax(r):.1f}" cy="{ay(v):.1f}" r="5" fill="{col}"/>')
        b.append(f'<text x="{ax(4)+10}" y="{ay(ys[4])+5}" font-size="13" font-weight="bold" fill="{col}" font-family="{FONT}">{name}</text>')
    # support annotation
    b.append(f'<text x="{ax(1.15)}" y="{ay(0.90)}" font-size="12.5" fill="{AMBER}" font-family="{FONT}">support thinned to ~1 item by r3–4;</text>')
    b.append(f'<text x="{ax(1.15)}" y="{ay(0.90)+17}" font-size="12.5" fill="{AMBER}" font-family="{FONT}">movement decelerated (seed 202’s gap flipped +0.056)</text>')

    at, _ = text_block(AX, AY + AH + 66,
                       "Four rounds of negative selection undo a rail the neutral loop left untouched, in 3/3 runs. Both seeds "
                       "shown reach ~1/3 with roughly one supported item still left — the clean zero-support stall is a separate "
                       "run (seed 707), at 0.625 (Panel B).", 13.5, 92, GRAY)
    b.append(at)

    # ============ Panel B: absorbing states ============
    BX = 830
    BY, BH = 210, 350
    by = lambda v: BY + BH * (1 - v)
    ctext(b, BX + 250, 190, "B. With no supported items, selection has nothing to act on", 17.5, INK, True)
    # vertical scale
    b.append(f'<line x1="{BX}" y1="{by(0)}" x2="{BX}" y2="{by(1)}" stroke="{INK}" stroke-width="2"/>')
    for v in (0.0, 0.5, 1.0):
        b.append(f'<line x1="{BX-5}" y1="{by(v)}" x2="{BX+5}" y2="{by(v)}" stroke="{INK}" stroke-width="2"/>')
        b.append(f'<text x="{BX-12}" y="{by(v)+5}" text-anchor="end" font-size="13" fill="{GRAY}" font-family="{FONT}">{v:.1f}</text>')
    # transport double arrow (left of axis)
    tax = BX - 70
    b.append(f'<line x1="{tax}" y1="{by(0.04)}" x2="{tax}" y2="{by(0.96)}" stroke="{GRAY}" stroke-width="2.4" '
             f'marker-start="url(#a19g)" marker-end="url(#a19g)"/>')
    for k, ln in enumerate(["selection", "moves the", "channel while", "material lasts"]):
        b.append(f'<text x="{tax-8}" y="{by(0.5)-24+k*15}" text-anchor="end" font-size="12" fill="{GRAY}" font-family="{FONT}">{esc(ln)}</text>')
    # the observed selection-inert endpoints (no supported items left to act on)
    states = [
        (1.00, RED, "the rail", "amp55_7 — the runaway, pinned at 1.0"),
        (0.625, AMBER, "a stalled reversal", "low_55_707 — reached exactly zero support"),
        (0.00, GREEN, "the pressed floor", "press-to-zero — a dead pool (risk axis)"),
    ]
    for v, col, name, desc in states:
        b.append(f'<circle cx="{BX}" cy="{by(v)}" r="8" fill="{col}"/>')
        b.append(f'<text x="{BX+18}" y="{by(v)-4}" font-size="14.5" font-weight="bold" fill="{col}" font-family="{FONT}">{esc(name)} ({v:.2f})</text>')
        b.append(f'<text x="{BX+18}" y="{by(v)+14}" font-size="12.5" fill="{INK}" font-family="{FONT}">{esc(desc)}</text>')
    # note: the ~1/3 oracle endpoints (Panel A) are NOT here — their last pools
    # kept a supported item, so they were still moving, not inert.
    # relapse callout on the 0.625 state (the one run with a relapse test from it)
    ry = by(0.625)
    b.append(box(BX + 300, ry - 34, 300, 70, "#fdf8ee", AMBER, 1.6, rx=8))
    rt, _ = rich_text(BX + 312, ry - 12, [
        ("released to its own judge: ", AMBER, True),
        ("held flat ×4 rounds, 0/6 items with support, cross-seed spread 0.002 — selection-inert (holds by inertness), not re-anchored.", INK, False),
    ], 12.5, 44)
    b.append(rt)

    bt, _ = text_block(BX, BY + AH + 66,
                       "Each endpoint had no supported items on the measured sr axis (this generator) — nothing for its judge "
                       "to select. The ~1/3 oracle endpoints (Panel A) are NOT here: their last pools kept a supported item; "
                       "durability can mean re-anchored values or merely exhausted variation.", 13.5, 92, GRAY)
    b.append(bt)

    # ============ takeaway ============
    ty = 700
    tt, tend = rich_text(92, ty + 34, [
        ("Selection moves the trained channel while there is within-pool material to act on. ", INK, True),
        ("Every force — forward (K2 collapse), opposing (this reversal), or none — decelerates and goes selection-inert on "
         "the measured axis once no supported items remain, so durability ≠ re-anchored values. Escaping a rail needs BOTH "
         "an opposing judge and residual pool material (release grid); sustained pressing reaches a selection-inert floor at "
         "the cost of later reversibility (press-depth); and a judge’s taste is pool-specific, so oversight needs a verified "
         "grip on the target’s own pools (force ladder).", INK, False),
    ], 15.5, 170)
    hh = (tend - ty) + 8
    b.append(box(70, ty, W - 140, hh, KEY_FILL, INK, 2.5))
    b.append(tt)

    doc = svg_doc(W, ty + hh + 36, "\n".join(b))
    out = os.path.join(HERE, "fig19_reversibility_absorbing.svg")
    with open(out, "w") as f:
        f.write(doc)
    print("wrote", out)


if __name__ == "__main__":
    main()
