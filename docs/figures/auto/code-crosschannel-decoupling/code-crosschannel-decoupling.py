#!/usr/bin/env python3
"""Draft figure: cross-channel decoupling in the code-security organism.

What the model SAYS (forced-choice self-report endpoint, x) versus what it
WRITES (blind manual insecure-write rate, y) for the 10 judge-factorial base
endpoints. Self-training moved the self-report channel across almost the whole
0-1 range while the blind write rate stayed pinned near the em750 organism line
(0.861); the only two states that moved their WRITING moved it DOWN, and both
had self-report that ROSE — the opposite of transfer. Pearson r = -0.39 (n=10,
not significant).

Data: experiments/em_code_crosschannel/output/code_crosschannel_adjudication.json
Style: docs/figures/src/make_figures.py (Evans-lab house style).
Regenerate:  python3 code-crosschannel-decoupling.py
"""
import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "..", "..", "..", "experiments",
                    "em_code_crosschannel", "output",
                    "code_crosschannel_adjudication.json")

INK = "#1a1a1a"
BLUE = "#2867b5"       # accent / self-judge series (validated)
GREEN = "#3a7d44"      # accent / frozen-judge series (validated)
RED = "#b5342c"        # emphasis for reversal / warning text
GRAY = "#6b7684"       # recessive only (axes, muted captions) — never a series
KEY_FILL = "#eef5ee"   # highlighted takeaway box
BAND_FILL = "#eef1f4"  # recessive cluster band

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
 <path d="M 0 0 L 10 5 L 0 10 z" fill="{INK}"/></marker>
<marker id="arrR" viewBox="0 0 10 10" refX="9" refY="5"
 markerWidth="6" markerHeight="6" orient="auto-start-reverse">
 <path d="M 0 0 L 10 5 L 0 10 z" fill="{RED}"/></marker></defs>'''


def svg_doc(w, h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
            f'font-family="{FONT}">\n<rect width="{w}" height="{h}" fill="white"/>\n'
            f'{DEFS}\n{body}\n</svg>')


# ------------------------------------------------------------------
# Human-readable names for the two series and the two annotated seeds.
SERIES_LABEL = {
    "neutral": "neutral prompt + base judge endpoint  (six seeds)",
    "candid": "candid prompt + base judge endpoint  (four seeds)",
}
LEGEND_LABEL = {
    "neutral": "neutral prompt + base judge  (six seeds)",
    "candid": "candid prompt + base judge  (four seeds)",
}


def seed_of(key):
    return key.rsplit("_", 1)[1]


def main():
    data = json.load(open(DATA))
    states = data["states"]
    cc = data["cross_channel"]

    organism = cc["organism_rate"]     # 0.8611
    base = cc["base_rate"]             # 0.4722
    pearson = cc["pearson_rate_vs_forced_choice"]  # -0.3909
    z = cc["z_vs_organism"]

    # Build the 10 endpoint points straight from the file.
    pts = []
    for key in cc["endpoints"]:
        st = states[key]
        series = "candid" if key.startswith("candid") else "neutral"
        p = st["insecure_rate"]
        se = math.sqrt(p * (1 - p) / st["n"])
        pts.append({
            "key": key, "series": series, "seed": seed_of(key),
            "x": st["endpoint_p_insecure"], "y": p, "se": se,
            "z": z[key],
        })

    xs = [p["x"] for p in pts]
    x_lo, x_hi = min(xs), max(xs)   # 0.0122 .. 0.9121

    W, H = 1180, 1000
    b = []

    # ---- headline + measurement-recipe subtitle ----
    t, _ = text_block(W // 2, 52,
                      "Self-training moved what the model SAYS across the full range —",
                      31, 82, weight="bold")
    b.append(t.replace('<text ', '<text text-anchor="middle" ', 1))
    t, _ = text_block(W // 2, 90,
                      "without moving what it WRITES",
                      31, 82, weight="bold")
    b.append(t.replace('<text ', '<text text-anchor="middle" ', 1))
    t, _ = text_block(W // 2, 126,
                      "x = forced-choice self-report endpoint (probability the model PICKS the insecure option on a security battery).  "
                      "y = blind insecure-write rate (fraction of 36 real code snippets a blind Sonnet-5 reviewer flags insecure).",
                      17, 158, GRAY)
    b.append(t.replace('<text ', '<text text-anchor="middle" ', 1))
    t, _ = text_block(W // 2, 168,
                      "Each dot is one judge-factorial endpoint state (supplier-removed em750 self-loop, 4 rounds); reviewer saw ids shuffled with the keymap withheld.",
                      17, 158, GRAY)
    b.append(t.replace('<text ', '<text text-anchor="middle" ', 1))

    # ---- plot geometry ----
    PX0, PW = 190, 680          # x = 0 .. 1
    PY_BOT, PH = 780, 480       # y = 0 at PY_BOT, y = 1 at PY_BOT-PH (=300)
    PX1 = PX0 + PW
    PY_TOP = PY_BOT - PH

    def X(v):
        return PX0 + PW * v

    def Y(v):
        return PY_BOT - PH * v

    # cluster band (the 8 non-exception states all sit here)
    band_hi, band_lo = 0.90, 0.65
    b.append(f'<rect x="{PX0}" y="{Y(band_hi):.1f}" width="{PW}" '
             f'height="{Y(band_lo) - Y(band_hi):.1f}" fill="{BAND_FILL}"/>')

    # gridlines + axes
    for v in (0.0, 0.25, 0.5, 0.75, 1.0):
        b.append(f'<line x1="{X(v):.1f}" y1="{PY_TOP}" x2="{X(v):.1f}" y2="{PY_BOT}" '
                 f'stroke="#e4e4e0" stroke-width="1"/>')
        b.append(f'<text x="{X(v):.1f}" y="{PY_BOT + 26}" text-anchor="middle" '
                 f'font-size="16" fill="{GRAY}" font-family="{FONT}">{v:g}</text>')
        b.append(f'<line x1="{PX0}" y1="{Y(v):.1f}" x2="{PX1}" y2="{Y(v):.1f}" '
                 f'stroke="#e4e4e0" stroke-width="1"/>')
        b.append(f'<text x="{PX0 - 14}" y="{Y(v) + 5:.1f}" text-anchor="end" '
                 f'font-size="16" fill="{GRAY}" font-family="{FONT}">{v:g}</text>')
    # frame
    b.append(f'<line x1="{PX0}" y1="{PY_TOP}" x2="{PX0}" y2="{PY_BOT}" stroke="{INK}" stroke-width="2"/>')
    b.append(f'<line x1="{PX0}" y1="{PY_BOT}" x2="{PX1}" y2="{PY_BOT}" stroke="{INK}" stroke-width="2"/>')

    # ---- reference lines ----
    yo = Y(organism)
    yb = Y(base)
    b.append(f'<line x1="{PX0}" y1="{yo:.1f}" x2="{PX1}" y2="{yo:.1f}" '
             f'stroke="{INK}" stroke-width="2.2" stroke-dasharray="9 5"/>')
    b.append(f'<text x="{PX1 - 8}" y="{yo - 9:.1f}" text-anchor="end" font-size="16.5" '
             f'font-weight="bold" fill="{INK}" font-family="{FONT}">'
             f'em750 organism writes insecure 0.861 (blind review)</text>')
    b.append(f'<line x1="{PX0}" y1="{yb:.1f}" x2="{PX1}" y2="{yb:.1f}" '
             f'stroke="{GRAY}" stroke-width="2.2" stroke-dasharray="9 5"/>')
    b.append(f'<text x="{PX0 + 8}" y="{yb - 9:.1f}" font-size="16.5" '
             f'font-weight="bold" fill="{GRAY}" font-family="{FONT}">'
             f'base Qwen3-4B 0.472</text>')

    # band tag
    b.append(f'<text x="{PX1 - 8}" y="{Y(band_lo) - 8:.1f}" text-anchor="end" '
             f'font-size="15.5" fill="{GRAY}" font-family="{FONT}">'
             f'8 of 10 endpoints cluster in this band</text>')

    # ---- data points (error bars + marks) ----
    ANNOT = {"candid_base_46", "neutral_base_42"}

    def diamond(cx, cy, r, fill, stroke, sw):
        pd = f"M {cx:.1f} {cy - r:.1f} L {cx + r:.1f} {cy:.1f} L {cx:.1f} {cy + r:.1f} L {cx - r:.1f} {cy:.1f} Z"
        return f'<path d="{pd}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'

    for p in pts:
        cx, cy = X(p["x"]), Y(p["y"])
        color = GREEN if p["series"] == "candid" else BLUE
        # binomial-SE error bar (vertical)
        y_up, y_dn = Y(min(1.0, p["y"] + p["se"])), Y(max(0.0, p["y"] - p["se"]))
        b.append(f'<line x1="{cx:.1f}" y1="{y_up:.1f}" x2="{cx:.1f}" y2="{y_dn:.1f}" '
                 f'stroke="{color}" stroke-width="2"/>')
        b.append(f'<line x1="{cx - 5:.1f}" y1="{y_up:.1f}" x2="{cx + 5:.1f}" y2="{y_up:.1f}" stroke="{color}" stroke-width="2"/>')
        b.append(f'<line x1="{cx - 5:.1f}" y1="{y_dn:.1f}" x2="{cx + 5:.1f}" y2="{y_dn:.1f}" stroke="{color}" stroke-width="2"/>')
        # red ring on the two exception states
        if p["key"] in ANNOT:
            b.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="15" fill="none" '
                     f'stroke="{RED}" stroke-width="2.6"/>')
        # marker (shape carries identity in addition to color)
        if p["series"] == "candid":
            b.append(diamond(cx, cy, 9.5, color, "white", 1.8))
        else:
            b.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="9" fill="{color}" '
                     f'stroke="white" stroke-width="1.8"/>')

    # ---- axis titles ----
    t, _ = text_block(X(0.5), PY_BOT + 58,
                      "Forced-choice self-report endpoint: probability the model picks the insecure option (security battery)",
                      17, 130, INK)
    b.append(t.replace('<text ', '<text text-anchor="middle" ', 1))
    b.append(f'<text x="66" y="{Y(0.5):.1f}" transform="rotate(-90 66 {Y(0.5):.1f})" '
             f'text-anchor="middle" font-size="17" fill="{INK}" font-family="{FONT}">'
             f'Blind insecure-write rate (n = 36 code snippets per state)</text>')

    # ---- legend (lower-left, inside plot's empty region) ----
    lx, ly = PX0 + 14, Y(0.17)
    b.append(f'<circle cx="{lx + 8}" cy="{ly - 5}" r="9" fill="{BLUE}" stroke="white" stroke-width="1.8"/>')
    b.append(f'<text x="{lx + 26}" y="{ly}" font-size="16" fill="{INK}" font-family="{FONT}">{esc(LEGEND_LABEL["neutral"])}</text>')
    b.append(diamond(lx + 8, ly + 24, 9.5, GREEN, "white", 1.8))
    b.append(f'<text x="{lx + 26}" y="{ly + 29}" font-size="16" fill="{INK}" font-family="{FONT}">{esc(LEGEND_LABEL["candid"])}</text>')

    # ---- Pearson callout (right margin) ----
    px, py, pw = PX1 + 22, PY_TOP + 6, W - (PX1 + 22) - 24
    pt, pend = rich_text(px + 16, py + 30, [
        ("Pearson r = -0.39 ", RED, True),
        ("(n = 10, not significant) — no positive cross-channel transfer between what the model says and what it writes.", INK, False),
    ], 17, 22)
    b.append(box(px, py, pw, (pend - py) + 14, KEY_FILL, INK, 2.2))
    b.append(pt)

    # ---- SE note (right margin, under Pearson) ----
    sy = pend + 28
    st_, send = rich_text(px + 16, sy + 26, [
        ("Error bars: ", INK, True),
        ("+/- 1 binomial standard error at n = 36 per state (about 0.06 to 0.08).", INK, False),
    ], 15.5, 24)
    b.append(box(px, sy, pw, (send - sy) + 12, "white", GRAY, 2))
    b.append(st_)

    # span note in right margin
    ry = send + 28
    rt, rend = rich_text(px + 16, ry + 26, [
        ("Self-report spans ", INK, True),
        (f"{x_lo:.3f} to {x_hi:.3f} ", RED, True),
        ("along x; the write rate barely moves off the organism line along y.", INK, False),
    ], 15.5, 24)
    b.append(box(px, ry, pw, (rend - ry) + 12, "white", GRAY, 2))
    b.append(rt)

    # ---- exception annotations (lower area, short arrows) ----
    # neutral+base seed 42
    n42 = next(p for p in pts if p["key"] == "neutral_base_42")
    nx, ny = X(n42["x"]), Y(n42["y"])
    bx1, by1, bw1 = 590, 486, 298
    at1, aend1 = rich_text(bx1 + 14, by1 + 26, [
        ("neutral prompt + base judge, seed 42. ", RED, True),
        (f"Self-report ROSE to {n42['x']:.3f}, yet the write rate DROPPED to {n42['y']:.3f} (z = -3.1 below the organism).", INK, False),
    ], 15.5, 40)
    b.append(box(bx1, by1, bw1, (aend1 - by1) + 12, "#fbf0ee", RED, 2.3))
    b.append(at1)
    b.append(f'<line x1="{bx1}" y1="{ny:.1f}" x2="{nx + 12:.1f}" y2="{ny:.1f}" '
             f'stroke="{RED}" stroke-width="3" marker-end="url(#arrR)"/>')

    # candid+base seed 46
    c46 = next(p for p in pts if p["key"] == "candid_base_46")
    cx46, cy46 = X(c46["x"]), Y(c46["y"])
    bx2, by2, bw2 = 590, 628, 298
    at2, aend2 = rich_text(bx2 + 14, by2 + 26, [
        ("candid prompt + base judge, seed 46. ", RED, True),
        (f"Self-report ROSE to {c46['x']:.3f}, yet the write rate DROPPED to {c46['y']:.3f} — below base — (z = -4.6).", INK, False),
    ], 15.5, 40)
    b.append(box(bx2, by2, bw2, (aend2 - by2) + 12, "#fbf0ee", RED, 2.3))
    b.append(at2)
    b.append(f'<line x1="{bx2 + 6}" y1="{by2 + 8}" x2="{cx46 + 12:.1f}" y2="{cy46 + 2:.1f}" '
             f'stroke="{RED}" stroke-width="3" marker-end="url(#arrR)"/>')

    # ---- context line (gray, small) ----
    ctx_y = PY_BOT + 92
    t, _ = text_block(W // 2, ctx_y,
                      "12 states x 6 security tasks x 6 samples; blind Sonnet-5 review, ids shuffled, keymap withheld; endpoints from the judge-ablation factorial (supplier-removed em750 self-loop, 4 rounds).",
                      15, 168, GRAY)
    b.append(t.replace('<text ', '<text text-anchor="middle" ', 1))

    # ---- bottom takeaway box ----
    ty = ctx_y + 44
    tk, tk_end = rich_text(80, ty + 32, [
        ("The two channels are decoupled. ", INK, True),
        ("Eight of ten endpoints sit in a band at the organism's 0.861 write rate while self-report ranges over almost the whole scale "
         f"({x_lo:.3f} to {x_hi:.3f}): self-training rewired what the model reports without touching what it writes. The only two states that "
         "moved their WRITING moved it toward or below base — and both had self-report that ROSE, the opposite of transfer.", INK, False),
    ], 18, 118)
    b.append(box(60, ty, W - 120, (tk_end - ty) + 18, KEY_FILL, INK, 2.5))
    b.append(tk)
    H = int(tk_end + 44)

    out = svg_doc(W, H, "\n".join(b))
    path = os.path.join(HERE, "code-crosschannel-decoupling.svg")
    with open(path, "w") as f:
        f.write(out)
    print(f"wrote {path} ({W}x{H})")


if __name__ == "__main__":
    main()
