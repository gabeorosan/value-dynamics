#!/usr/bin/env python3
"""Draft figure: partially repaired Qwen self-judge pilot (three seeds).

Two aligned panels, shared rounds axis, both on the SAME honest 0-1 scale:
top = the risk coordinate (order-balanced p(gamble)) fanning out across
seeds; bottom = the judgment-taste coordinate (p(judge prefers bold advice))
staying flat in every seed.

Style: make_figures.py house conventions (Owain Evans-lab look) — white
background, big headline sentence, real data with fat labels, palette
constants copied verbatim. Regenerate with:  python3 mod65-divergence.py

Source data: experiments/kaggle/kaggle_basin_criterion/output/
basin_criterion_mod65.json. The plotted values remain embedded so the figure
regenerates deterministically.
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))

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


def svg_doc(w, h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
            f'font-family="{FONT}">\n<rect width="{w}" height="{h}" fill="white"/>\n'
            f'{body}\n</svg>')


# --------------------------------------------------------------------
# Data — Drive value_dynamics/basin_criterion/basin_criterion_mod65.json
# Qwen3-4B-Instruct + moderate risk persona (65%-gamble, position-balanced
# training data), self-judge selection loop, rounds 0-5, seeds 0-2.
# --------------------------------------------------------------------
ROUNDS = list(range(6))

# risk coordinate: order-balanced p(gamble) — 36 probe reads per round,
# 18 presenting the gamble as Option A and 18 as Option B
RISK = {
    0: [0.361, 0.333, 0.333, 0.556, 0.472, 0.639],
    1: [0.444, 0.278, 0.250, 0.250, 0.167, 0.111],
    2: [0.333, 0.361, 0.417, 0.472, 0.472, 0.472],
}

# judgment taste: p(judge prefers bold advice), averaged over both
# presentation orders, same rounds
TASTE = {
    0: [0.377, 0.387, 0.396, 0.389, 0.392, 0.391],
    1: [0.377, 0.378, 0.374, 0.378, 0.373, 0.375],
    2: [0.378, 0.384, 0.393, 0.388, 0.402, 0.400],
}

SHAPES = {0: "circle", 1: "square", 2: "triangle"}


def marker(shape, x, y, color, scale=1.0):
    """per-seed marker: circle (seed 0), square (seed 1), triangle (seed 2)."""
    if shape == "circle":
        return (f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{5 * scale:.1f}" '
                f'fill="{color}" stroke="white" stroke-width="1.5"/>')
    if shape == "square":
        s = 9 * scale
        return (f'<rect x="{x - s / 2:.1f}" y="{y - s / 2:.1f}" width="{s:.1f}" '
                f'height="{s:.1f}" fill="{color}" stroke="white" stroke-width="1.5"/>')
    h = 11 * scale
    return (f'<polygon points="{x:.1f},{y - h * 0.62:.1f} {x - h * 0.55:.1f},'
            f'{y + h * 0.45:.1f} {x + h * 0.55:.1f},{y + h * 0.45:.1f}" '
            f'fill="{color}" stroke="white" stroke-width="1.5"/>')


def main():
    W = 1150
    PX, PW = 120, 760          # shared plot x-geometry; right margin for labels
    PH = 280                   # both panels the same height and the same 0-1
                               # scale, so flatness below is not an axis trick

    def X(r):
        return PX + PW * r / 5

    b = []

    # ---- headline ----
    t, _ = text_block(W // 2, 54, "Pilot: generated risk fans while fixed advice taste stays flat",
                      34, 62, weight="bold")
    b.append(t.replace('<text ', '<text text-anchor="middle" ', 1))
    t, _ = text_block(W // 2, 96, "three seeds; instrument caveats remain",
                      34, 62, weight="bold")
    b.append(t.replace('<text ', '<text text-anchor="middle" ', 1))

    # ---- setup paragraph ----
    t, _ = text_block(
        90, 134,
        "Qwen3-4B-Instruct with a moderate risk persona (trained on 65%-gamble, "
        "position-balanced data). Each round: generate 6 answers per gamble "
        "question, the model's own judge keeps the top 2, fine-tune 12 steps on "
        "the kept answers; 5 rounds. The probe is order-balanced and loop order "
        "is randomized, but not exactly balanced per round (observed gamble-A "
        "fractions 0.17-0.83); the old generated parser also did not retain probe "
        "texts. Treat this as a pilot, not the final repaired result.",
        18, 106, GRAY)
    b.append(t)

    # ---- legend: seed identity is shape + label, not color alone ----
    ly = 268
    lx = 420
    for seed in (0, 1, 2):
        b.append(marker(SHAPES[seed], lx, ly - 5, BLUE))
        b.append(f'<text x="{lx + 14}" y="{ly}" font-size="17" fill="{INK}" '
                 f'font-family="{FONT}">seed {seed}</text>')
        lx += 120

    # ---- shared panel machinery ----
    def frame(py, ticks_y=True):
        s = []
        for v in (0.0, 0.25, 0.5, 0.75, 1.0):
            y = py + PH * (1 - v)
            s.append(f'<line x1="{PX}" y1="{y}" x2="{PX + PW}" y2="{y}" '
                     f'stroke="#e4e4e0" stroke-width="1"/>')
            if ticks_y:
                s.append(f'<text x="{PX - 12}" y="{y + 6}" text-anchor="end" '
                         f'font-size="15" fill="{GRAY}" font-family="{FONT}">{v:g}</text>')
        for r in ROUNDS:
            s.append(f'<line x1="{X(r):.1f}" y1="{py + PH}" x2="{X(r):.1f}" '
                     f'y2="{py + PH + 7}" stroke="{GRAY}" stroke-width="1.5"/>')
            s.append(f'<text x="{X(r):.1f}" y="{py + PH + 26}" text-anchor="middle" '
                     f'font-size="15" fill="{GRAY}" font-family="{FONT}">{r}</text>')
        return "\n".join(s)

    def series(py, data, mscale=1.0):
        s = []
        for seed in (0, 1, 2):
            pts = " ".join(f"{X(r):.1f},{py + PH * (1 - v):.1f}"
                           for r, v in zip(ROUNDS, data[seed]))
            s.append(f'<polyline points="{pts}" fill="none" stroke="{BLUE}" '
                     f'stroke-width="3" stroke-opacity="0.9"/>')
        for seed in (0, 1, 2):   # markers on top of all lines
            for r, v in zip(ROUNDS, data[seed]):
                s.append(marker(SHAPES[seed], X(r), py + PH * (1 - v), BLUE, mscale))
        return "\n".join(s)

    # ================= panel 1: behavior =================
    t, _ = text_block(PX, 314, "The behavior diverges — finals span 0.53",
                      22, 70, BLUE, "bold")
    b.append(t)
    t, _ = text_block(
        PX, 342,
        "Risk coordinate = order-balanced p(gamble): the fraction of sampled "
        "probe answers choosing the gamble, 36 reads per round — 18 presenting "
        "the gamble as Option A and 18 as Option B.",
        14.5, 118, GRAY)
    b.append(t)
    P1Y = 386
    b.append(frame(P1Y))
    b.append(series(P1Y, RISK))

    # start-cluster note (round 0 sits between 0.333 and 0.444 in every seed)
    b.append(f'<line x1="{PX + 6}" y1="{P1Y + PH * (1 - 0.30)}" x2="{PX + 3}" '
             f'y2="{P1Y + PH * (1 - 0.43)}" stroke="{GRAY}" stroke-width="1.5"/>')
    t, _ = text_block(PX + 10, P1Y + PH * (1 - 0.145),
                      "round-0 start: all seeds between 0.33 and 0.44",
                      15, 60, INK)
    b.append(t)

    # end labels
    for seed, label in ((0, "seed 0 — final 0.639"),
                        (2, "seed 2 — final 0.472"),
                        (1, "seed 1 — final 0.111")):
        y = P1Y + PH * (1 - RISK[seed][-1])
        b.append(f'<text x="{PX + PW + 16}" y="{y + 6:.1f}" font-size="16" '
                 f'font-weight="bold" fill="{BLUE}" font-family="{FONT}">{label}</text>')

    t, _ = text_block(
        PX, P1Y + PH + 62,
        "Same organism and loop: from a tight start, the recorded coordinate "
        "seed 0 climbs to 0.639, seed 2 settles at 0.472, seed 1 slides to "
        "0.111 — the finals fan across 0.53.",
        17, 108, BLUE, "bold")
    b.append(t)

    # ================= panel 2: judging criterion =================
    t, _ = text_block(PX, 828, "The judging criterion stays flat — every reading "
                      "within 0.373 to 0.402", 22, 96, INK, "bold")
    b.append(t)
    t, _ = text_block(
        PX, 856,
        "Judgment taste = p(judge prefers bold advice): the probability the "
        "round's model, acting as judge, picks the bold answer over the "
        "cautious answer in a fixed advice pair, averaged over both "
        "presentation orders. Same 0-1 axis as above.",
        14.5, 118, GRAY)
    b.append(t)
    P2Y = 906
    # shaded band holding every taste reading (0.373-0.402)
    band_top = P2Y + PH * (1 - 0.402)
    band_bot = P2Y + PH * (1 - 0.373)
    b.append(f'<rect x="{PX}" y="{band_top:.1f}" width="{PW}" '
             f'height="{band_bot - band_top:.1f}" fill="#efefec"/>')
    b.append(frame(P2Y))
    # 0.5 = indifference line
    y_half = P2Y + PH * 0.5
    b.append(f'<line x1="{PX}" y1="{y_half}" x2="{PX + PW}" y2="{y_half}" '
             f'stroke="{INK}" stroke-width="1.5" stroke-dasharray="6 5"/>')
    b.append(f'<text x="{PX + PW - 4}" y="{y_half - 9}" text-anchor="end" '
             f'font-size="14" fill="{GRAY}" font-family="{FONT}">0.5 = judge '
             f'indifferent between the bold and the cautious answer</text>')
    b.append(series(P2Y, TASTE, mscale=0.75))
    t, _ = text_block(PX + 8, band_bot + 22,
                      "all 18 readings (3 seeds × 6 rounds) sit in this band: "
                      "0.373 to 0.402", 13.5, 90, GRAY)
    b.append(t)

    # staggered end labels with leader lines (finals nearly coincide)
    for seed, label, ly2 in ((2, "seed 2 — final 0.400", band_top - 18),
                             (0, "seed 0 — final 0.391", band_top + 8),
                             (1, "seed 1 — final 0.375", band_top + 34)):
        y = P2Y + PH * (1 - TASTE[seed][-1])
        b.append(f'<line x1="{PX + PW + 2}" y1="{y:.1f}" x2="{PX + PW + 13}" '
                 f'y2="{ly2:.1f}" stroke="{GRAY}" stroke-width="1.2"/>')
        b.append(f'<text x="{PX + PW + 16}" y="{ly2 + 5:.1f}" font-size="16" '
                 f'font-weight="bold" fill="{INK}" font-family="{FONT}">{label}</text>')

    b.append(f'<text x="{PX + PW / 2}" y="{P2Y + PH + 56}" text-anchor="middle" '
             f'font-size="17" fill="{INK}" font-family="{FONT}">round</text>')

    # shared rotated y labels
    b.append(f'<text x="46" y="{P1Y + PH / 2}" font-size="17" fill="{INK}" '
             f'font-family="{FONT}" transform="rotate(-90 46 {P1Y + PH / 2})" '
             f'text-anchor="middle">risk coordinate</text>')
    b.append(f'<text x="46" y="{P2Y + PH / 2}" font-size="17" fill="{INK}" '
             f'font-family="{FONT}" transform="rotate(-90 46 {P2Y + PH / 2})" '
             f'text-anchor="middle">judgment taste</text>')

    # ---- takeaway ----
    ty = P2Y + PH + 84
    b.append(f'<rect x="90" y="{ty}" width="{W - 180}" height="118" rx="8" '
             f'fill="{KEY_FILL}" stroke="{INK}" stroke-width="2.5"/>')
    t, _ = rich_text(110, ty + 32, [
        ("The recorded risk coordinate spans 0.53 while this fixed advice probe "
         "moves less than 0.03 in every seed. ", INK, True),
        ("That is evidence that generic advice taste does not track the fan, not "
         "that the actual candidate-ranking criterion stayed fixed. K1 now logs "
         "strict actual-pool judge loadings and exact order balance.", INK, False),
    ], 18, 106)
    b.append(t)

    # ---- data pointer ----
    t, _ = text_block(
        90, ty + 148,
        "Data: experiments/kaggle/kaggle_basin_criterion/output/basin_criterion_mod65.json; "
        "plotted values embedded above. Rounds 0-5, seeds 0-2.",
        13.5, 150, GRAY)
    b.append(t)

    H = ty + 172
    doc = svg_doc(W, H, "\n".join(b))
    out = os.path.join(HERE, "mod65-divergence.svg")
    with open(out, "w") as f:
        f.write(doc)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
