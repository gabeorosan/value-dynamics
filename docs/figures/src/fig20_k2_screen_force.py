#!/usr/bin/env python3
"""Figure: the K2 pre-launch screen that measured the conservative judge's
selection force — real but pool-heterogeneous.

Five fresh gamble pools from the v10 organism, scored by the frozen-conservative
and frozen-base judges; the kept-set separation is the per-round force the loop
would integrate. Data: the 5-pool screen verdict (STATE 07-11 ~16:15 /
report_loop_integrator_decomposition.md): separations
[+0.021, +0.167, +0.167, +0.167, -0.021], mean 0.100 sd 0.093, conservative
kept-gap negative in all five pools; operator re-simulation rules out
top-M/softmax as the cause of the flat pool.

Regenerate:  python3 fig20_k2_screen_force.py   (stdlib only)
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
FIGDIR = os.path.dirname(HERE) if os.path.basename(HERE) == "src" else HERE

INK = "#1a1a1a"
BLUE = "#2867b5"
GREEN = "#3a7d44"
RED = "#b5342c"
GRAY = "#6b7684"
AMBER = "#9a6b15"
KEY_FILL = "#eef5ee"
FONT = "Helvetica, Arial, sans-serif"


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


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
        tspans = "".join(f'<tspan fill="{c}" font-weight="{"bold" if b else weight}">{esc(w)} </tspan>'
                         for w, c, b in ln)
        svg.append(f'<text x="{x}" y="{y + i * size * lh}" font-family="{FONT}" font-size="{size}">{tspans}</text>')
    return "\n".join(svg), y + len(out) * size * lh


def text_block(x, y, text, size, width, color=INK, weight="normal", lh=1.4):
    return rich_text(x, y, [(text, color, weight == "bold")], size, width, lh)


def box(x, y, w, h, fill, stroke=INK, sw=2.5, rx=8):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'


def svg_doc(w, h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" font-family="{FONT}">\n'
            f'<rect width="{w}" height="{h}" fill="white"/>\n{body}\n</svg>')


def ctext(b, cx, y, s, size, color=INK, bold=False):
    b.append(f'<text x="{cx}" y="{y}" text-anchor="middle" font-size="{size}" '
             f'font-weight="{"bold" if bold else "normal"}" fill="{color}" font-family="{FONT}">{esc(s)}</text>')


def main():
    W = 1150
    b = []
    ctext(b, W / 2, 50, "The conservative judge's selection force is real,", 30, INK, True)
    ctext(b, W / 2, 86, "but pool-heterogeneous", 30, INK, True)
    ctext(b, W / 2, 118, "the pre-launch screen that gated K2 — five fresh gamble pools from the same organism, scored by the "
          "frozen-conservative vs frozen-base judge", 15.5, GRAY)

    # ---- bar chart of per-pool kept-set separation ----
    AX, AY, AW, AH = 150, 200, 720, 300
    ymin, ymax = -0.10, 0.24
    def ay(v):
        return AY + AH * (ymax - v) / (ymax - ymin)
    # gridlines
    for v in (-0.10, 0.0, 0.10, 0.20):
        yy = ay(v)
        col = INK if v == 0 else "#e5e5e1"
        b.append(f'<line x1="{AX}" y1="{yy:.1f}" x2="{AX+AW}" y2="{yy:.1f}" stroke="{col}" stroke-width="{2 if v==0 else 1}"/>')
        b.append(f'<text x="{AX-12}" y="{ay(v)+5:.1f}" text-anchor="end" font-size="13" fill="{GRAY}" font-family="{FONT}">{v:+.2f}</text>')
    b.append(f'<text x="{AX-70}" y="{AY+AH/2}" font-size="14" fill="{INK}" font-family="{FONT}" '
             f'transform="rotate(-90 {AX-70} {AY+AH/2})" text-anchor="middle">kept-set separation (cons − base)</text>')
    # mean ± sd band
    mean, sd = 0.100, 0.093
    b.append(f'<rect x="{AX}" y="{ay(mean+sd):.1f}" width="{AW}" height="{ay(mean-sd)-ay(mean+sd):.1f}" fill="{GREEN}" fill-opacity="0.08"/>')
    b.append(f'<line x1="{AX}" y1="{ay(mean):.1f}" x2="{AX+AW}" y2="{ay(mean):.1f}" stroke="{GREEN}" stroke-width="2" stroke-dasharray="7 4"/>')
    b.append(f'<text x="{AX+AW-6}" y="{ay(mean)-8:.1f}" text-anchor="end" font-size="13.5" font-weight="bold" fill="{GREEN}" font-family="{FONT}">mean 0.100 ± 0.093</text>')
    # bars
    pools = [("101", 0.021, "flat"), ("202", 0.167, ""), ("303", 0.167, ""), ("404", 0.167, ""), ("505", -0.021, "base out-cautions")]
    bw, gap = 92, 40
    x0 = AX + (AW - (5 * bw + 4 * gap)) / 2
    for i, (name, sep, tag) in enumerate(pools):
        x = x0 + i * (bw + gap)
        col = GREEN if sep > 0.05 else (AMBER if sep >= 0 else RED)
        top = ay(max(sep, 0)); bot = ay(min(sep, 0))
        b.append(f'<rect x="{x}" y="{top:.1f}" width="{bw}" height="{bot-top:.1f}" fill="{col}" rx="3"/>')
        vy = top - 8 if sep >= 0 else bot + 18
        b.append(f'<text x="{x+bw/2}" y="{vy:.1f}" text-anchor="middle" font-size="14.5" font-weight="bold" fill="{col}" font-family="{FONT}">{sep:+.3f}</text>')
        b.append(f'<text x="{x+bw/2}" y="{ay(ymin)+20:.1f}" text-anchor="middle" font-size="13" fill="{INK}" font-family="{FONT}">pool {name}</text>')
        if tag:
            b.append(f'<text x="{x+bw/2}" y="{ay(ymin)+37:.1f}" text-anchor="middle" font-size="11.5" fill="{GRAY}" font-family="{FONT}">{esc(tag)}</text>')

    y = AY + AH + 74
    t, yend = rich_text(70, y + 32, [
        ("How to read it: ", INK, True),
        ("the conservative kept-set is more cautious than base in 5/5 pools — the DIRECTION is solid — but the "
         "MAGNITUDE swings {≈0, +0.167 ×3, −0.02}; on pool 505 the base judge is the more cautious of the two. "
         "Operator re-simulation on the saved score tables rules out top-M / softmax selection as the cause of the "
         "flat pool, so the heterogeneity is pool-borne. The screen preregistered a SIGN gate and MEASURES the "
         "magnitude: the mean 0.100 ± 0.093 enters K2 as its per-round force calibration (fig17) and sets the "
         "Δ≈0.1 kept-gap scale for the weak-dose transmission cells. A judge's taste is pool-distribution-specific "
         "— it does not transport unchanged to a different organism's pools.", INK, False),
    ], 16, 140)
    hh = (yend - y) + 8
    b.append(box(70, y, W - 140, hh, KEY_FILL, INK, 2.5))
    b.append(t)

    open(os.path.join(FIGDIR, "fig20_k2_screen_force.svg"), "w").write(svg_doc(W, y + hh + 36, "\n".join(b)))
    print("wrote fig20_k2_screen_force.svg")


if __name__ == "__main__":
    main()
