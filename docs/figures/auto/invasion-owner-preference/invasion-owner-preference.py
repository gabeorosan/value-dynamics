#!/usr/bin/env python3
"""Draft figure: judges prefer the loop-railed invader's TEXT at matched risk.

Owain Evans-lab house style (see docs/figures/src/make_figures.py). Palette
constants copied from that file. Stdlib only. Run from this directory:

    python3 invasion-owner-preference.py

Reads ../../../../experiments/invasion_owner_preference.json — plots numbers
straight from that file (round-1 matched_score_pref per cell, plus per-round
decay and traj for invade_base_s35).
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "..", "..", "..",
                    "experiments", "invasion_owner_preference.json")

# ---- palette, copied verbatim from make_figures.py --------------------------
INK = "#1a1a1a"
BLUE = "#2867b5"       # self-judge series
GREEN = "#3a7d44"      # frozen-judge series
RED = "#b5342c"        # reversal / warning emphasis
GRAY = "#6b7684"       # recessive only (axes, muted captions) — never a series
PURPLE = "#8a5a9e"     # duel series (as in make_figures fig4/fig7)
USER_FILL = "#cfe0f1"
ASST_FILL = "#eaf1f8"
DOC_FILL = "#fdf6e8"
KEY_FILL = "#eef5ee"
FONT = "Helvetica, Arial, sans-serif"


# ---- esc()/wrap() copied verbatim from make_figures.py ----------------------
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


# ============================================================================
def main():
    D = json.load(open(DATA))

    def r1_pref(cell):
        return D[cell]["rounds"][0]["matched_score_pref"]

    def r1_n(cell):
        return D[cell]["rounds"][0]["matched_score_n"]

    def r1_ref_pref(cell):
        return D[cell]["rounds"][0].get("matched_reference_score_pref")

    # Grouped left panel: round-1 matched-risk score preference by cell,
    # using matched_score_pref = the score that actually selected the keeps
    # (for duel cells this is the head-to-head selection score; the
    # reference-anchored diagnostic score on the same pairs is a hollow dot).
    GROUPS = [
        ("frozen base judge (reference-anchored)\nfresh host, railed supplier's text",
         GREEN, [("invade_base_s35", "seed 35"), ("invade_base_s36", "seed 36")]),
        ("supplier's own model judges (self)\nfresh host, railed supplier's text",
         BLUE, [("invade_self_s37", "seed 37"), ("invade_self_s38", "seed 38")]),
        ("head-to-head duel judges\nfresh host, railed supplier's text",
         PURPLE, [("h2h_invade_base_s51", "s51"), ("h2h_invade_base_s52", "s52"),
                  ("h2h_invade_self_s53", "s53"), ("h2h_invade_self_s54", "s54")]),
        ("head-to-head duel judges\nrailed host, BASE-model text (rescue)",
         PURPLE, [("h2h_cons_rescue_s55", "s55"), ("h2h_cons_rescue_s56", "s56"),
                  ("h2h_base_rescue_s57", "s57"), ("h2h_base_rescue_s58", "s58")]),
        ("cautious judge\nrailed host, BASE-model text (rescue)",
         RED, [("cons_mix_s33", "seed 33"), ("cons_mix_s34", "seed 34")]),
    ]

    b = []
    W = 1500
    # ---- title + subtitle (defines the measure) ----
    t, _ = text_block(W // 2, 52, "The invader's text wins even against equally risky local answers"
                      " — until the host is converted", 31, 96, weight="bold")
    b.append(t.replace('<text ', '<text text-anchor="middle" ', 1))
    t, _ = text_block(W // 2, 90,
                      "risk-matched pairs = an invader answer and a local answer within 0.10 on the "
                      "risk score; the readout is the share where the judge scored the invader higher; "
                      "0.5 = no preference once risk is matched.",
                      17, 150, GRAY)
    b.append(t.replace('<text ', '<text text-anchor="middle" ', 1))

    # =====================================================================
    # LEFT PANEL: grouped dot plot, round-1 matched-risk preference by cell
    # =====================================================================
    px, py, pw, ph = 300, 190, 640, 470
    x_lo, x_hi = 0.0, 1.0

    def X(v):
        return px + pw * (v - x_lo) / (x_hi - x_lo)

    t, _ = text_block(px, 156, "Round 1: does the judge prefer the invader's text at matched risk?",
                      18, 90, INK, "bold")
    b.append(t)

    # vertical gridlines + x ticks
    for v in (0.0, 0.25, 0.5, 0.75, 1.0):
        xx = X(v)
        b.append(f'<line x1="{xx}" y1="{py}" x2="{xx}" y2="{py+ph}" '
                 f'stroke="#e4e4e0" stroke-width="1"/>')
        b.append(f'<text x="{xx}" y="{py+ph+30}" text-anchor="middle" font-size="15" '
                 f'fill="{GRAY}" font-family="{FONT}">{v:g}</text>')
    # 0.5 chance line
    b.append(f'<line x1="{X(0.5)}" y1="{py}" x2="{X(0.5)}" y2="{py+ph}" '
             f'stroke="{INK}" stroke-width="2" stroke-dasharray="6 5"/>')
    b.append(f'<text x="{X(0.5)}" y="{py-10}" text-anchor="middle" font-size="14.5" '
             f'font-weight="bold" fill="{INK}" font-family="{FONT}">0.5 = no owner preference</text>')
    b.append(f'<text x="{px+pw/2}" y="{py+ph+62}" text-anchor="middle" font-size="17" '
             f'fill="{INK}" font-family="{FONT}">round-1 share of matched-risk pairs where the '
             f'judge scored the INVADER higher</text>')
    # key: solid = selection score, hollow = reference-anchored diagnostic
    keyy = py + ph + 92
    b.append(f'<circle cx="{px+40}" cy="{keyy-5}" r="8" fill="{PURPLE}" '
             f'stroke="white" stroke-width="1.6"/>')
    b.append(f'<text x="{px+56}" y="{keyy}" font-size="14.5" fill="{INK}" '
             f'font-family="{FONT}">the score that selected the keeps</text>')
    b.append(f'<circle cx="{px+336}" cy="{keyy-5}" r="6.5" fill="white" '
             f'stroke="{PURPLE}" stroke-width="2.2"/>')
    b.append(f'<text x="{px+352}" y="{keyy}" font-size="14.5" fill="{INK}" '
             f'font-family="{FONT}">same pairs under the reference-anchored score (duel cells only)</text>')

    # rows: one band per group, dots per cell
    n_rows = sum(len(cells) for _, _, cells in GROUPS)
    n_groups = len(GROUPS)
    row_h = (ph - 30) / (n_rows + n_groups)  # leave a little gap between groups
    yy = py + row_h
    for gname, color, cells in GROUPS:
        # group label
        gy = yy - row_h * 0.15
        for j, line in enumerate(gname.split("\n")):
            fw = "bold" if j == 0 else "normal"
            fs = 15 if j == 0 else 13
            col = color if j == 0 else GRAY
            b.append(f'<text x="{px-14}" y="{gy + j*17 - 8}" text-anchor="end" font-size="{fs}" '
                     f'font-weight="{fw}" fill="{col}" font-family="{FONT}">{esc(line)}</text>')
        for cellkey, seedlbl in cells:
            v = r1_pref(cellkey)
            n = r1_n(cellkey)
            cy = yy
            # baseline stub to 0.5 (secondary encoding: line from chance to value)
            b.append(f'<line x1="{X(0.5)}" y1="{cy}" x2="{X(v)}" y2="{cy}" '
                     f'stroke="{color}" stroke-width="2.5" stroke-opacity="0.55"/>')
            # duel cells: hollow dot = the reference-anchored diagnostic score
            # applied to the same matched pairs (not what selected the keeps)
            ref = r1_ref_pref(cellkey)
            if ref is not None:
                b.append(f'<circle cx="{X(ref)}" cy="{cy}" r="6.5" fill="white" '
                         f'stroke="{color}" stroke-width="2.2"/>')
            b.append(f'<circle cx="{X(v)}" cy="{cy}" r="8" fill="{color}" '
                     f'stroke="white" stroke-width="1.6"/>')
            # value label
            lx = X(v) + (14 if v < 0.85 else -14)
            anc = "start" if v < 0.85 else "end"
            b.append(f'<text x="{lx}" y="{cy+5}" text-anchor="{anc}" font-size="14.5" '
                     f'font-weight="bold" fill="{INK}" font-family="{FONT}">'
                     f'{v:.2f}</text>')
            # seed + n label at far right column
            b.append(f'<text x="{px+pw+16}" y="{cy+5}" font-size="13.5" fill="{GRAY}" '
                     f'font-family="{FONT}">{esc(seedlbl)}  (n={n})</text>')
            yy += row_h
        yy += row_h  # gap between groups

    # column header for the seed / count labels
    b.append(f'<text x="{px+pw+16}" y="{py-10}" font-size="13" fill="{GRAY}" '
             f'font-family="{FONT}">cell (n pairs)</text>')

    # =====================================================================
    # RIGHT PANEL: per-round decay of the preference vs the host railing,
    # for invade_base_s35 (one representative cell).
    # =====================================================================
    cell = "invade_base_s35"
    prefs = [D[cell]["rounds"][r]["matched_score_pref"] for r in range(4)]  # r1..r4
    traj = D[cell]["traj"]  # r0..r4 (5 values)

    qx, qy, qw, qh = 1080, 250, 340, 290
    y_lo, y_hi = 0.0, 1.0

    def QY(v):
        return qy + qh * (y_hi - v) / (y_hi - y_lo)

    t, _ = text_block(qx, 156, "One cell over time: invade_base seed 35",
                      18, 60, INK, "bold")
    b.append(t)
    t, _ = text_block(qx, 182,
                      "frozen base judge · fresh OLMo host meets the railed OLMo supplier's answers",
                      13.5, 46, GRAY)
    b.append(t)

    # y grid
    for v in (0.0, 0.25, 0.5, 0.75, 1.0):
        y = QY(v)
        b.append(f'<line x1="{qx}" y1="{y}" x2="{qx+qw}" y2="{y}" '
                 f'stroke="#e4e4e0" stroke-width="1"/>')
        b.append(f'<text x="{qx-10}" y="{y+5}" text-anchor="end" font-size="14" '
                 f'fill="{GRAY}" font-family="{FONT}">{v:g}</text>')
    # 0.5 chance line
    b.append(f'<line x1="{qx}" y1="{QY(0.5)}" x2="{qx+qw}" y2="{QY(0.5)}" '
             f'stroke="{INK}" stroke-width="1.5" stroke-dasharray="6 5"/>')

    # x layout: 5 columns r0..r4
    def QX(r):
        return qx + qw * r / 4

    for r in range(5):
        b.append(f'<text x="{QX(r)}" y="{qy+qh+28}" text-anchor="middle" font-size="14" '
                 f'fill="{GRAY}" font-family="{FONT}">{r}</text>')
    b.append(f'<text x="{qx+qw/2}" y="{qy+qh+56}" text-anchor="middle" font-size="16" '
             f'fill="{INK}" font-family="{FONT}">round</text>')

    # traj line (host's risk coordinate), GREEN = frozen-base-selected host
    tpts = " ".join(f"{QX(r):.1f},{QY(traj[r]):.1f}" for r in range(5))
    b.append(f'<polyline points="{tpts}" fill="none" stroke="{GREEN}" stroke-width="3"/>')
    for r in range(5):
        b.append(f'<circle cx="{QX(r)}" cy="{QY(traj[r])}" r="6" fill="{GREEN}" '
                 f'stroke="white" stroke-width="1.6"/>')

    # preference line (r1..r4 -> plotted at x=1..4), RED = the owner preference
    ppts = " ".join(f"{QX(r+1):.1f},{QY(prefs[r]):.1f}" for r in range(4))
    b.append(f'<polyline points="{ppts}" fill="none" stroke="{RED}" stroke-width="3"/>')
    for r in range(4):
        b.append(f'<circle cx="{QX(r+1)}" cy="{QY(prefs[r])}" r="6" fill="{RED}" '
                 f'stroke="white" stroke-width="1.6"/>')

    # inline series labels (placed in open space, away from the marks)
    b.append(f'<text x="{QX(2.5)}" y="{QY(0.30)}" text-anchor="middle" font-size="13.5" '
             f'font-weight="bold" fill="{RED}" font-family="{FONT}">matched-risk preference</text>')
    b.append(f'<text x="{QX(2.5)}" y="{QY(0.86)}" text-anchor="middle" font-size="13.5" '
             f'font-weight="bold" fill="{GREEN}" font-family="{FONT}">host risk coordinate</text>')

    # annotation: the mechanism
    ay = qy + qh + 92
    b.append(box(qx-4, ay, qw+64, 150, KEY_FILL, INK, 2.5))
    t, _ = rich_text(qx+14, ay+30, [
        ("One round of preferred keeps rails the host ", RED, True),
        ("(risk 0.31→1.00 after round 1); after that the host's own answers "
         "saturate at max risk, matched pairs are everywhere, and there is nothing "
         "left to prefer — the preference collapses to ~0.06.", INK, False),
    ], 15, 58)
    b.append(t)

    # =====================================================================
    # bottom takeaway strip (spans left panel width)
    # =====================================================================
    ky = 782
    b.append(box(60, ky, 1000, 162, KEY_FILL, INK, 2.5))
    t, _ = rich_text(80, ky+32, [
        ("Judge-specific and format-graded: ", INK, True),
        ("reference-anchored and self judges take the railed supplier's equally risky "
         "text ~every time (0.97–1.00); head-to-head duels ", INK, False),
        ("attenuate ", PURPLE, True),
        ("the same preference (0.49–0.80 in invasions, 0.31–0.44 in rescues; hollow dots "
         "show the reference-anchored score calling the same pairs 0.97–1.00); the "
         "differently-tasted cautious judge ", INK, False),
        ("reverses it ", RED, True),
        ("(0.49 / 0.00). The suppliers are loop products (press_d1 / base_hold seed 2, "
         "railed through 7–8 rounds of frozen-base selection): selection moved their text "
         "into the judge family's preferred region, and the judging format is part of the "
         "selector.", INK, False),
    ], 16.5, 118)
    b.append(t)

    return svg_doc(W, 950, "\n".join(b))


if __name__ == "__main__":
    svg = main()
    out = os.path.join(HERE, "invasion-owner-preference.svg")
    with open(out, "w") as f:
        f.write(svg)
    print(f"wrote {out}")
