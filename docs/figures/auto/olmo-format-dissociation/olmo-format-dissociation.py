#!/usr/bin/env python3
"""Draft figure: training-format double dissociation in the OLMo-3-7B
conservative-persona install ladders.

Rationale-format targets move GENERATED behavior while FORCED next-token
choice stays flat; letter-format targets do the opposite. Two aligned
dose-response panels, house style of docs/figures/make_figures.py.

Data provenance: the raw rung JSONs live on Google Drive
(value_dynamics/olmo_conservative/v3_strict_completion/, v4_rate93_strict/,
v5 rationale ladder) and are not synced into the repo; the numbers below
were transcribed from the spawning thread's readout and cross-checked
against docs/STATE.md "Recent changes" 2026-07-10 (all overlapping values
match). Regenerate with:  python3 olmo-format-dissociation.py
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))

INK = "#1a1a1a"
BLUE = "#2867b5"       # accent series (validated)
GREEN = "#3a7d44"      # accent series (validated)
RED = "#b5342c"        # emphasis for reversal / warning text
GRAY = "#6b7684"       # recessive only (axes, muted captions) — never a series
BAND_FILL = "#f3e7cd"  # install-target band shading (recessive amber)

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


# ---------------- data (Drive olmo_conservative/, see module docstring) ----
# Rationale targets, 90% cautious rows (v5, completion-only loss)
RAT_STEPS = [0, 10, 20, 40, 80, 120]
RAT_FORCED = [0.723, 0.704, 0.690, 0.720, 0.699, 0.688]
RAT_GEN = [0.714, 0.75, 0.583, 0.50, 0.292, 0.125]

# Letter targets, 93% cautious rows (v4, completion-only loss)
LET_STEPS = [0, 40, 80]
LET_FORCED = [0.723, 0.521, 0.483]
LET_GEN = [0.64, 0.70, 0.65]

# Letter targets at 100% cautious rows (v3): the forced-channel cliff
CLIFF_STEPS = [0, 40]
CLIFF_FORCED = [0.723, 0.177]


def main():
    b = []
    t, _ = text_block(700, 52, "The training format picks which channel moves:", 34, 70, weight="bold")
    b.append(t.replace('<text ', '<text text-anchor="middle" ', 1))
    t, _ = text_block(700, 96, "rationale targets steer generated behavior, letter targets steer forced choice", 26, 96, weight="bold")
    b.append(t.replace('<text ', '<text text-anchor="middle" ', 1))
    t, _ = text_block(700, 132, "Cautious-persona QLoRA install on OLMo-3-7B-Instruct — same items, same loss, only the answer format differs", 18, 110, GRAY)
    b.append(t.replace('<text ', '<text text-anchor="middle" ', 1))

    # legend (both series also direct-labeled in the panels)
    lx = 330
    b.append(f'<line x1="{lx}" y1="172" x2="{lx + 34}" y2="172" stroke="{BLUE}" stroke-width="3.5"/>')
    b.append(f'<circle cx="{lx + 17}" cy="172" r="5" fill="{BLUE}"/>')
    t, _ = text_block(lx + 44, 178, "generated behavior (share of 24 free generations choosing the gamble)", 16, 80)
    b.append(t)
    lx2 = lx + 44 + 560
    b.append(f'<line x1="{lx2}" y1="172" x2="{lx2 + 34}" y2="172" stroke="{GREEN}" stroke-width="3.5"/>')
    b.append(f'<circle cx="{lx2 + 17}" cy="172" r="5" fill="{GREEN}"/>')
    t, _ = text_block(lx2 + 44, 178, "forced choice (next-token p(gamble))", 16, 60)
    b.append(t)

    PY, PH, PW = 258, 360, 500
    YMIN, YMAX = 0.0, 0.85

    def panel(px, title_lines, xmax, xticks):
        def X(step):
            return px + PW * step / xmax

        def Y(v):
            return PY + PH * (YMAX - v) / (YMAX - YMIN)

        s = []
        for i, ln in enumerate(title_lines):
            s.append(f'<text x="{px + PW / 2}" y="{PY - 58 + i * 26}" text-anchor="middle" font-size="20" '
                     f'font-weight="bold" fill="{INK}" font-family="{FONT}">{esc(ln)}</text>')
        # install-target band (drawn first, under everything)
        s.append(f'<rect x="{px}" y="{Y(0.40)}" width="{PW}" height="{Y(0.25) - Y(0.40)}" fill="{BAND_FILL}"/>')
        for v in (0.0, 0.25, 0.5, 0.75):
            yy = Y(v)
            s.append(f'<line x1="{px}" y1="{yy}" x2="{px + PW}" y2="{yy}" stroke="#e4e4e0" stroke-width="1"/>')
            s.append(f'<text x="{px - 12}" y="{yy + 6}" text-anchor="end" font-size="16" fill="{GRAY}" font-family="{FONT}">{v:g}</text>')
        for st in xticks:
            xx = X(st)
            s.append(f'<line x1="{xx}" y1="{Y(0) - 4}" x2="{xx}" y2="{Y(0) + 4}" stroke="{GRAY}" stroke-width="1.5"/>')
            s.append(f'<text x="{xx}" y="{Y(0) + 26}" text-anchor="middle" font-size="16" fill="{GRAY}" font-family="{FONT}">{st}</text>')
        s.append(f'<line x1="{px}" y1="{Y(0)}" x2="{px + PW}" y2="{Y(0)}" stroke="{INK}" stroke-width="2"/>')
        s.append(f'<text x="{px + PW / 2}" y="{Y(0) + 54}" text-anchor="middle" font-size="17" fill="{INK}" font-family="{FONT}">QLoRA optimizer steps</text>')
        return s, X, Y

    def series(X, Y, steps, vals, color, width=3.5, dash="", opacity=1.0):
        pts = " ".join(f"{X(s):.1f},{Y(v):.1f}" for s, v in zip(steps, vals))
        d = f' stroke-dasharray="{dash}"' if dash else ""
        out = [f'<g opacity="{opacity}">',
               f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="{width}"{d}/>']
        for s, v in zip(steps, vals):
            out.append(f'<circle cx="{X(s):.1f}" cy="{Y(v):.1f}" r="5" fill="{color}" stroke="white" stroke-width="1.5"/>')
        out.append('</g>')
        return "\n".join(out)

    def vlabel(X, Y, step, v, color, dx=0, dy=-12, anchor="middle", size=15):
        return (f'<text x="{X(step) + dx:.1f}" y="{Y(v) + dy:.1f}" text-anchor="{anchor}" font-size="{size}" '
                f'font-weight="bold" fill="{color}" font-family="{FONT}">{v:.3g}</text>')

    # ---------------- left panel: rationale targets (v5) ----------------
    L = 110
    s, X, Y = panel(L, ["Rationale targets (90% cautious rows) —",
                        "answer = cautious sentence + “Final: X”"], 120, RAT_STEPS)
    b += s
    b.append(f'<text x="{L + 8}" y="{Y(0.285) + 5}" font-size="14.5" fill="#8a6d2f" font-family="{FONT}">install-target band 0.25–0.40</text>')
    b.append(series(X, Y, RAT_STEPS, RAT_FORCED, GREEN))
    b.append(series(X, Y, RAT_STEPS, RAT_GEN, BLUE))
    # labels: generated descends — label start, 10, 40, 80, 120; forced end
    b.append(vlabel(X, Y, 0, 0.714, BLUE, dx=2, dy=26, anchor="start"))
    b.append(vlabel(X, Y, 10, 0.75, BLUE, dy=-13))
    b.append(vlabel(X, Y, 40, 0.50, BLUE, dx=-8, dy=24))
    b.append(vlabel(X, Y, 80, 0.292, BLUE, dx=-10, dy=26))
    b.append(vlabel(X, Y, 120, 0.125, BLUE, dx=-4, dy=-13))
    b.append(vlabel(X, Y, 120, 0.688, GREEN, dx=2, dy=-14, anchor="end"))
    t, _ = text_block(X(46), Y(0.63), "forced choice stays ~0.70", 16, 24, GREEN, "bold")
    b.append(t)
    t, _ = text_block(X(46), Y(0.185), "generated behavior descends through the target band", 16, 30, BLUE, "bold")
    b.append(t)
    t, _ = rich_text(L, PY + PH + 84, [
        ("Format compliance is fixed, not broken: ", INK, True),
        ("invalid generations (no parseable Final line) fall from 0.125 at step 0 to 0.000 at every trained rung.", INK, False),
    ], 15.5, 62)
    b.append(t)

    # ---------------- right panel: letter targets (v4, + v3 cliff) -------
    R = 760
    s, X2, Y2 = panel(R, ["Letter targets (93% cautious rows) —",
                          "answer = the single letter token"], 80, LET_STEPS)
    b += s
    b.append(series(X2, Y2, CLIFF_STEPS, CLIFF_FORCED, RED, width=3, dash="7 6", opacity=0.55))
    b.append(series(X2, Y2, LET_STEPS, LET_FORCED, GREEN))
    b.append(series(X2, Y2, LET_STEPS, LET_GEN, BLUE))
    b.append(vlabel(X2, Y2, 0, 0.723, GREEN, dx=6, dy=-14, anchor="start"))
    b.append(vlabel(X2, Y2, 40, 0.521, GREEN, dx=0, dy=24))
    b.append(vlabel(X2, Y2, 80, 0.483, GREEN, dx=-4, dy=24))
    b.append(vlabel(X2, Y2, 0, 0.64, BLUE, dx=6, dy=20, anchor="start"))
    b.append(vlabel(X2, Y2, 40, 0.70, BLUE, dy=-13))
    b.append(vlabel(X2, Y2, 80, 0.65, BLUE, dx=-4, dy=-13))
    b.append(f'<text x="{X2(40) + 10:.1f}" y="{Y2(0.177) + 5:.1f}" font-size="14.5" font-weight="bold" '
             f'fill="{RED}" opacity="0.8" font-family="{FONT}">0.177 — forced cliff at 100% cautious rows</text>')
    t, _ = text_block(X2(16), Y2(0.815), "generated behavior barely moves", 16, 44, BLUE, "bold")
    b.append(t)
    t, _ = text_block(X2(46), Y2(0.36), "forced choice plateaus ~0.5", 16, 30, GREEN, "bold")
    b.append(t)
    t, _ = rich_text(R, PY + PH + 84, [
        ("Format compliance degrades: ", RED, True),
        ("invalid generations rise to 0.167 (rate 0.93 and rate 1.0 alike); at 100% cautious rows the forced channel overshoots the band in one rung.", INK, False),
    ], 15.5, 66)
    b.append(t)

    # shared y label
    ymid = PY + PH / 2
    b.append(f'<text x="46" y="{ymid}" font-size="17" fill="{INK}" font-family="{FONT}" '
             f'transform="rotate(-90 46 {ymid})" text-anchor="middle">p(gamble) — both readouts on one scale</text>')

    # ---------------- measurement-recipe caption ------------------------
    t, _ = rich_text(110, PY + PH + 168, [
        ("How each readout is measured: ", INK, True),
        ("forced choice = next-token probability of the gamble letter on held-out A/B items, averaged over both option orders; "
         "generated behavior = fraction of 24 free generations that choose the gamble under strict “Final: X” parsing "
         "(a malformed generation is never coded as a choice). Training: QLoRA rank 16 on 4-bit OLMo-3-7B-Instruct, "
         "completion-only loss, position-balanced EV-neutral gamble rows; the two ladders differ only in the assistant "
         "target — a single letter versus a one-sentence cautious reason ending in a Final line (the self-training "
         "loop’s own output format).", GRAY, False),
    ], 16, 158)
    b.append(t)

    return svg_doc(1400, PY + PH + 300, "\n".join(b))


if __name__ == "__main__":
    svg = main()
    out = os.path.join(HERE, "olmo-format-dissociation.svg")
    with open(out, "w") as f:
        f.write(svg)
    print(f"wrote {out}")
