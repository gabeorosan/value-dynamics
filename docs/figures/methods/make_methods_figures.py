#!/usr/bin/env python3
"""Figures for the Sunday analysis-day methods (docs/PLAN.md, the audit-ordered
hierarchy). One figure per method: what it computes (recipe), a representative
example with real numbers, and how to read it / its caveats.

House style follows docs/figures/make_figures.py and ../plan/make_plan_figures.py
(white background, bold headline, KEY_FILL takeaway box, status chips). Numbers
are grounded in the reports named in each figure's source line. Regenerate:
    python3 make_methods_figures.py
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))

INK = "#1a1a1a"
BLUE = "#2867b5"
GREEN = "#3a7d44"
RED = "#b5342c"
GRAY = "#6b7684"
AMBER = "#9a6b15"
KEY_FILL = "#eef5ee"
AMBER_TINT = "#fdf8ee"
GRAY_TINT = "#f4f4f1"
RED_TINT = "#fbf0ee"
BLUE_TINT = "#eef3fa"
GREEN_TINT = "#eef7f0"
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


def box(x, y, w, h, fill, stroke=INK, sw=2.5, rx=8, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>')


def arrow(x1, y1, x2, y2, sw=4, color=INK):
    return (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" '
            f'stroke-width="{sw}" marker-end="url(#arr)"/>')


DEFS = f'''<defs><marker id="arr" viewBox="0 0 10 10" refX="9" refY="5"
 markerWidth="6" markerHeight="6" orient="auto-start-reverse">
 <path d="M 0 0 L 10 5 L 0 10 z" fill="{INK}"/></marker>
 <marker id="arrg" viewBox="0 0 10 10" refX="9" refY="5"
 markerWidth="6" markerHeight="6" orient="auto-start-reverse">
 <path d="M 0 0 L 10 5 L 0 10 z" fill="{GRAY}"/></marker></defs>'''


def svg_doc(w, h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
            f'font-family="{FONT}">\n<rect width="{w}" height="{h}" fill="white"/>\n'
            f'{DEFS}\n{body}\n</svg>')


def centered(b, cx, y, text, size, color=INK, bold=False):
    w = "bold" if bold else "normal"
    b.append(f'<text x="{cx}" y="{y}" text-anchor="middle" font-size="{size}" '
             f'font-weight="{w}" fill="{color}" font-family="{FONT}">{esc(text)}</text>')


def header(b, W, line1, line2, sub):
    centered(b, W / 2, 52, line1, 32, bold=True)
    if line2:
        centered(b, W / 2, 92, line2, 32, bold=True)
        sy = 126
    else:
        sy = 92
    centered(b, W / 2, sy, sub, 15.5, GRAY)
    return sy


def keybox(b, W, X0, y, segments, size=17, width=148, pad=20):
    t, yend = rich_text(X0 + pad, y + 32, segments, size, width)
    hh = (yend - y) + 6
    b.append(box(X0, y, W - 2 * X0, hh, KEY_FILL, INK, 2.5))
    b.append(t)
    return y + hh


def recipe_flow(b, X0, y, steps, boxw=None, gap=40, W=1400, sh=150, title=None,
                title_color=INK):
    """Horizontal input -> compute -> readout flow of labelled boxes."""
    if title:
        b.append(f'<text x="{X0}" y="{y}" font-size="19" font-weight="bold" '
                 f'fill="{title_color}" font-family="{FONT}">{esc(title)}</text>')
        y += 20
    n = len(steps)
    avail = (W - 2 * X0) - (n - 1) * gap
    bx = X0
    for i, (ttl, desc, fill, border) in enumerate(steps):
        bw = steps[i][4] if len(steps[i]) > 4 else avail / n
        b.append(box(bx, y, bw, sh, fill, border, 1.8, rx=10))
        for j, ln in enumerate(wrap(ttl, int(bw / 8.4))):
            b.append(f'<text x="{bx + 15}" y="{y + 28 + j * 20}" font-size="15.5" '
                     f'font-weight="bold" fill="{border if border != INK else INK}" '
                     f'font-family="{FONT}">{esc(ln)}</text>')
        yy = y + 28 + len(wrap(ttl, int(bw / 8.4))) * 20 + 4
        for j, ln in enumerate(wrap(desc, int(bw / 6.6))):
            b.append(f'<text x="{bx + 15}" y="{yy + j * 17}" font-size="12.8" '
                     f'fill="{INK}" font-family="{FONT}">{esc(ln)}</text>')
        if i < n - 1:
            b.append(arrow(bx + bw + 4, y + sh / 2, bx + bw + gap - 4, y + sh / 2, sw=3.5))
        bx += bw + gap
    return y + sh


# ====================================================================
# Figure 0 — the analysis stack (overview / TOC)
# ====================================================================

def fig_overview():
    W, X0 = 1400, 60
    b = []
    header(b, W, "The Sunday analysis day, method by method:",
           "eight readouts, each certified before it is read",
           "docs/PLAN.md audit-ordered hierarchy — the spine is confidence: gates certify, primary contrasts carry the claim, "
           "mechanism and geometry explain it, the exploratory tier is labeled as such")

    CW = W - 2 * X0
    rows = [
        ("1", "Instrument gate table", "certify",
         "per cell: order balance, forced order gap, generated invalidity, factual-EV delta, measure-only drift — nothing below is read until a cell passes",
         "Fig 1", GREEN, GREEN_TINT),
        ("2", "Paired seed-level contrast", "primary",
         "the primary behavioral claim: paired baseline-adjusted final generated-valid risk, rollout seed as the unit (K2 confirmatory contrast first)",
         "Fig 2", BLUE, BLUE_TINT),
        ("3", "Candidate-level judge loading", "mechanism",
         "what the judge's selection actually put into training — kept-pool minus full-pool loading on the target axis; the kept gap is a manipulation check, not a proven mediator",
         "Fig 3", BLUE, BLUE_TINT),
        ("4", "Format-channel separation", "primary",
         "generated-valid prose choice and forced single-token A/B read as DISTINCT channels on the same items — a move in one without the other is a dissociation, not noise",
         "Fig 4", BLUE, BLUE_TINT),
        ("5", "Invariant update geometry", "geometry",
         "merged-update ΔW = scaling·B@A relative to round zero, Frobenius cosines, leave-one-seed-out; raw-factor norms are gauge-dependent and withdrawn; α-scaling is a narrow diagnostic only",
         "Fig 5", GRAY, GRAY_TINT),
        ("6", "Transmission contrasts + binomial counts", "counting",
         "cross-organism cells as steering-force / re-ignition profiles, never rates; K3 em_freegen as binomial counts with intervals — rounds are not independent observations",
         "Fig 6", GRAY, GRAY_TINT),
        ("7", "Probe-specificity ratio", "specificity",
         "the riding battery without fishing: standardize each probe by its own noise, divide the target change by the off-target RMS, compare to the random arm, BH/FDR within the family",
         "Fig 7", AMBER, AMBER_TINT),
        ("8", "Exploratory tier — labeled", "exploratory",
         "drift-field AR(1) refits and cross-lag / mediation, run and reported but NEVER headlined: the design does not identify them (R² ≈ 0.05–0.09; a bistable saddle in only 19% of bootstraps)",
         "Fig 8", RED, RED_TINT),
    ]
    y = 150
    rh = 74
    for num, name, cat, desc, fig, color, fill in rows:
        b.append(box(X0, y, CW, rh, fill, color, 1.6, rx=9))
        # number badge
        b.append(f'<circle cx="{X0 + 34}" cy="{y + rh / 2}" r="19" fill="{color}"/>')
        b.append(f'<text x="{X0 + 34}" y="{y + rh / 2 + 7}" text-anchor="middle" font-size="20" '
                 f'font-weight="bold" fill="white" font-family="{FONT}">{num}</text>')
        b.append(f'<text x="{X0 + 70}" y="{y + 27}" font-size="18.5" font-weight="bold" '
                 f'fill="{INK}" font-family="{FONT}">{esc(name)}</text>')
        # category chip
        cw = len(cat) * 7.4 + 18
        b.append(box(X0 + 70 + len(name) * 10.7 + 14, y + 12, cw, 20, "white", color, 1.3, rx=10))
        b.append(f'<text x="{X0 + 70 + len(name) * 10.7 + 14 + cw / 2}" y="{y + 26}" text-anchor="middle" '
                 f'font-size="11.5" font-weight="bold" fill="{color}" font-family="{FONT}">{esc(cat.upper())}</text>')
        t, _ = text_block(X0 + 70, y + 46, desc, 13, 118)
        b.append(t)
        b.append(f'<text x="{X0 + CW - 16}" y="{y + rh / 2 + 5}" text-anchor="end" font-size="14" '
                 f'font-weight="bold" fill="{color}" font-family="{FONT}">{fig} →</text>')
        y += rh + 10

    y = keybox(b, W, X0, y + 6, [
        ("The ordering is the argument: ", INK, True),
        ("a cell is certified (1) before its primary contrast is read (2); the contrast is explained by what selection "
         "put into the data (3) and by whether the channels move together (4); geometry and counting (5–6) constrain "
         "the mechanism; specificity (7) separates targeted change from battery-wide drift; and anything the design "
         "cannot identify (8) is run but labeled exploratory. Screens and gates prove a manipulation is non-null — "
         "they are never the scientific claim.", INK, False),
    ])
    return svg_doc(W, y + 40, "\n".join(b))


# ====================================================================
# Figure 1 — the instrument gate table (Tier 1)
# ====================================================================

def fig_gate_table():
    W, X0 = 1400, 60
    b = []
    header(b, W, "Method 1 — the instrument gate table:",
           "certify the coordinate before you read a single trajectory",
           "five validity gates that catch a position habit or a response bias masquerading as a value shift  ·  "
           "report_probe_instrument_checks.md, phase0_screen.json")

    # ---- the five gates as a table ----------------------------------
    gates = [
        ("training-order balance", "each round generates exactly half its items in each option order; every kept answer gets a genuinely swapped-order twin",
         "exact 50/50 by construction", "provenance"),
        ("forced order gap", "read every held-out item with the gamble as A and as B; gap = how far P(gamble) moves when the gamble switches option (absolute per-order difference)",
         "≤ 0.10  ·  >0.10 voids the semantic channel", "≤ 0.10"),
        ("generated invalidity", "fraction of free-text answers with no strict Final: A/B — a malformed answer is NEVER coded as the safe option",
         "≤ 0.10  ·  logged separately from the choice", "≤ 0.10"),
        ("factual-EV delta", "same-template control: “which option has the higher expected payoff?” on EV-unequal items; accuracy must not drop after the value update",
         "differential readout, not a disqualifier", "no drop"),
        ("measure-only drift", "a seed that is probed every round but never trained — bounds how much the readout moves on its own",
         "the null trajectory the others are read against", "baseline"),
    ]
    y = 150
    b.append(f'<text x="{X0}" y="{y + 4}" font-size="19" font-weight="bold" fill="{GREEN}" '
             f'font-family="{FONT}">The five gates (a cell that fails any of them is not interpreted)</text>')
    y += 22
    col1, col2 = 300, 760
    for name, recipe, crit, tag in gates:
        lines = wrap(recipe, 74)
        rh = max(len(lines) * 18 + 20, 52)
        b.append(box(X0, y, col1, rh, GREEN_TINT, GREEN, 1.4, rx=8))
        for j, ln in enumerate(wrap(name, 26)):
            b.append(f'<text x="{X0 + 14}" y="{y + 26 + j * 18}" font-size="15" font-weight="bold" '
                     f'fill="{INK}" font-family="{FONT}">{esc(ln)}</text>')
        b.append(box(X0 + col1 + 10, y, col2, rh, "white", GRAY, 1.1, rx=8))
        for j, ln in enumerate(lines):
            b.append(f'<text x="{X0 + col1 + 24}" y="{y + 22 + j * 18}" font-size="13" '
                     f'fill="{INK}" font-family="{FONT}">{esc(ln)}</text>')
        b.append(f'<text x="{X0 + col1 + col2 + 24}" y="{y + rh / 2 + 5}" font-size="13.5" '
                 f'font-weight="bold" fill="{GREEN}" font-family="{FONT}">{esc(tag)}</text>')
        y += rh + 10

    # ---- worked example ---------------------------------------------
    y += 8
    b.append(f'<text x="{X0}" y="{y + 4}" font-size="19" font-weight="bold" fill="{INK}" '
             f'font-family="{FONT}">What the gates caught — one inference-only screen vs forty legacy rollouts</text>')
    y += 24
    ex = [
        ("base Qwen3-4B", "0.94 when the gamble is option B, 0.31 when it is option A", "order gap 0.63 — FAIL", RED),
        ("legacy risk persona", "order-robust (gap ~0) but saturated at 1.00", "no headroom to move — unusable", AMBER),
        ("OLMo-3-7B-Instruct", "risk 0.72, order gap 0.077, headroom down", "PASS — the substrate K2 starts from", GREEN),
        ("OLMo runaway (EV gate)", "choice runs to ~1.0 but ev_estimation.mean_ratio = 1.000 across all 8 rollouts",
         "a real preference shift, not a response bias", GREEN),
    ]
    card_w = (W - 2 * X0 - 3 * 14) / 4
    maxh = 0
    rend = []
    for name, val, verdict, col in ex:
        vl = wrap(val, 30)
        vd = wrap(verdict, 26)
        hh = 30 + len(vl) * 17 + 10 + len(vd) * 16 + 12
        maxh = max(maxh, hh)
        rend.append((name, vl, vd, col))
    for i, (name, vl, vd, col) in enumerate(rend):
        cx = X0 + i * (card_w + 14)
        b.append(box(cx, y, card_w, maxh, "white", col, 1.8, rx=9))
        b.append(f'<text x="{cx + 13}" y="{y + 23}" font-size="14" font-weight="bold" '
                 f'fill="{INK}" font-family="{FONT}">{esc(name)}</text>')
        for j, ln in enumerate(vl):
            b.append(f'<text x="{cx + 13}" y="{y + 44 + j * 17}" font-size="12.5" '
                     f'fill="{INK}" font-family="{FONT}">{esc(ln)}</text>')
        yv = y + 44 + len(vl) * 17 + 8
        for j, ln in enumerate(vd):
            b.append(f'<text x="{cx + 13}" y="{yv + j * 16}" font-size="12.5" font-weight="bold" '
                     f'fill="{col}" font-family="{FONT}">{esc(ln)}</text>')
    y += maxh + 20

    y = keybox(b, W, X0, y, [
        ("How to read it: ", INK, True),
        ("the gate table is not analysis of the result — it is the license to do analysis at all. A single order-swap "
         "read showed the base model's “0.94 risk-seeker” was 0.63 of position preference; the EV gate showed the "
         "OLMo runaway was genuine. Gates precede seeds, and a failed gate retires a claim before it is made.", INK, False),
    ])
    return svg_doc(W, y + 40, "\n".join(b))


# ====================================================================
# Figure 2 — paired seed-level contrast (Tier 2)
# ====================================================================

def fig_paired_contrast():
    W, X0 = 1400, 60
    b = []
    header(b, W, "Method 2 — the paired, baseline-adjusted contrast:",
           "the rollout seed is the unit, and the spread is part of the answer",
           "the primary behavioral claim — computed at the seed level, paired against a frozen-base rollout, never at "
           "the round or item level  ·  docs/PLAN.md K1/K2 endpoints")

    # ---- recipe line -------------------------------------------------
    y = 148
    y = recipe_flow(b, X0, y + 4, [
        ("one rollout seed = one unit", "each seed runs the treatment arm AND a frozen-base arm from the same start; "
         "the seed, not the round or the item, is what is counted", GREEN_TINT, GREEN),
        ("per-seed paired difference", "final generated-valid risk of the treatment arm MINUS the frozen-base arm, "
         "within the same seed — cross-seed nuisance variance cancels", BLUE_TINT, BLUE),
        ("distribution over seeds", "average the paired differences AND report their spread; for K2 both the magnitude "
         "and the six-seed spread are the deliverable", KEY_FILL, INK),
    ], sh=150)

    # ---- paired dot-plot schematic ----------------------------------
    y += 30
    b.append(f'<text x="{X0}" y="{y}" font-size="18" font-weight="bold" fill="{INK}" '
             f'font-family="{FONT}">K1’s landed anchor grid — evolving-self vs frozen-base, final generated-valid risk per seed</text>')
    y += 20
    px0, px1 = X0 + 250, W - X0 - 250
    axy = y + 24
    # axis
    b.append(f'<line x1="{px0}" y1="{axy}" x2="{px1}" y2="{axy}" stroke="{GRAY}" stroke-width="1.5"/>')
    for v in (0.0, 0.25, 0.5, 0.75, 1.0):
        vx = px0 + v * (px1 - px0)
        b.append(f'<line x1="{vx}" y1="{axy - 4}" x2="{vx}" y2="{axy + 4}" stroke="{GRAY}" stroke-width="1.2"/>')
        b.append(f'<text x="{vx}" y="{axy - 10}" text-anchor="middle" font-size="11.5" fill="{GRAY}" '
                 f'font-family="{FONT}">{v:.2f}</text>')
    b.append(f'<text x="{(px0 + px1) / 2}" y="{axy - 26}" text-anchor="middle" font-size="12.5" fill="{GRAY}" '
             f'font-family="{FONT}">final generated-valid risk (start ≈ 0.60)</text>')
    seeds = [(0.60, 0.26), (0.47, 0.71), (0.60, 0.88), (0.59, 1.00)]
    ry = axy + 26
    for i, (base, treat) in enumerate(seeds):
        yy = ry + i * 34
        bx = px0 + base * (px1 - px0)
        tx = px0 + treat * (px1 - px0)
        dcol = RED if treat < base else BLUE
        b.append(f'<text x="{px0 - 16}" y="{yy + 5}" text-anchor="end" font-size="12.5" fill="{INK}" '
                 f'font-family="{FONT}">seed {i}</text>')
        b.append(f'<line x1="{bx}" y1="{yy}" x2="{tx}" y2="{yy}" stroke="{dcol}" stroke-width="2"/>')
        b.append(f'<circle cx="{bx}" cy="{yy}" r="5.5" fill="{GRAY}"/>')
        b.append(f'<circle cx="{tx}" cy="{yy}" r="5.5" fill="{dcol}"/>')
        lbx = max(bx, tx) + 12
        b.append(f'<text x="{lbx}" y="{yy + 5}" font-size="11.5" fill="{dcol}" '
                 f'font-family="{FONT}">Δ {treat - base:+.2f}</text>')
    ly = ry + len(seeds) * 34 + 8
    b.append(f'<circle cx="{px0}" cy="{ly}" r="5.5" fill="{GRAY}"/>')
    b.append(f'<text x="{px0 + 12}" y="{ly + 5}" font-size="12.5" fill="{INK}" font-family="{FONT}">frozen-base arm (this seed)</text>')
    b.append(f'<circle cx="{px0 + 300}" cy="{ly}" r="5.5" fill="{BLUE}"/>')
    b.append(f'<text x="{px0 + 312}" y="{ly + 5}" font-size="12.5" fill="{INK}" font-family="{FONT}">evolving-self arm — the line is the paired Δ (red = negative)</text>')

    y = ly + 34
    y = keybox(b, W, X0, y, [
        ("How to read it: ", INK, True),
        ("the seed is the unit because the rounds within a rollout are not independent and the items are not the "
         "experiment. Pairing against a same-seed frozen-base arm removes the between-seed starting-point variance. "
         "K1’s landed paired primary is −0.34 / +0.24 / +0.28 / +0.41 — positive-leaning with one large negative, a "
         "distribution to show at n = 4, not a test to pass; “basins” is not claimed. K2’s confirmatory contrast "
         "(frozen-conservative minus frozen-base) is landing the same way, every conservative seed below start, "
         "read against the screen’s measured force 0.100 ± 0.093. The frozen-base baseline is honestly n = 4.", INK, False),
    ])
    return svg_doc(W, y + 40, "\n".join(b))


# ====================================================================
# Figure 3 — candidate-level judge loading (Tier 3)
# ====================================================================

def fig_judge_loading():
    W, X0 = 1400, 60
    b = []
    header(b, W, "Method 3 — candidate-level judge loading:",
           "what the judge's selection actually put into the training data",
           "the mechanism read — the kept-pool minus full-pool axis shift, cross-scored across arms  ·  a manipulation "
           "check, one rung below a mediator  ·  report_judge_transmission_screen.md")

    y = 150
    y = recipe_flow(b, X0, y + 4, [
        ("score every candidate", "each sampled answer is axis-scored once (risk / insecure-code / self-report candor) "
         "against a fixed reference — before any selection", "white", GRAY),
        ("keep top-2 of 6", "the judge applies the loop's pairwise rule to the same pool; the kept set is what would "
         "enter training this round", "white", GRAY),
        ("kept minus full pool = gap", "kept-set mean − full-pool mean on the axis = the shift selection introduced; "
         "cross-scored by the fixed base AND organism judges even in arms they don't control", BLUE_TINT, BLUE),
    ], sh=150)

    # ---- example table ----------------------------------------------
    y += 28
    b.append(f'<text x="{X0}" y="{y}" font-size="18" font-weight="bold" fill="{INK}" '
             f'font-family="{FONT}">The screen read (kept − pool gap; Δ = gap minus the base judge’s gap)  ·  pool means: risk 0.104, code 0.577, self-report 0.329</text>')
    y += 18
    rows = [
        ("base anchor", "−0.042", "−0.036", "+0.036", INK, False),
        ("em_dose_750", "+0.083 (+0.125)", "+0.061 (+0.096)", "+0.044 (+0.008)", GREEN, True),
        ("em_dose_1000", "−0.104 (−0.062)", "−0.012 (+0.024)", "+0.127 (+0.091)", AMBER, True),
        ("amp66:12 (reverted)", "per-pool", "flips sign", "+0.082 / −0.071", RED, True),
    ]
    tw = W - 2 * X0
    cw0 = 300
    cwr = (tw - cw0) / 3
    hdr = ["judge", "risk gap (Δ)", "insecure-code gap (Δ)", "self-report gap (Δ)"]
    b.append(box(X0, y, tw, 30, GRAY_TINT, GRAY, 1.2, rx=6))
    b.append(f'<text x="{X0 + 14}" y="{y + 20}" font-size="13.5" font-weight="bold" fill="{INK}" font-family="{FONT}">{hdr[0]}</text>')
    for k in range(3):
        b.append(f'<text x="{X0 + cw0 + k * cwr + cwr / 2}" y="{y + 20}" text-anchor="middle" font-size="13.5" '
                 f'font-weight="bold" fill="{INK}" font-family="{FONT}">{esc(hdr[k + 1])}</text>')
    y += 30
    for name, rg, cg, sg, col, bold in rows:
        b.append(box(X0, y, tw, 30, "white" if col == INK else (GREEN_TINT if col == GREEN else (AMBER_TINT if col == AMBER else RED_TINT)), GRAY, 0.9, rx=0))
        b.append(f'<text x="{X0 + 14}" y="{y + 20}" font-size="13" font-weight="{"bold" if bold else "normal"}" '
                 f'fill="{col}" font-family="{FONT}">{esc(name)}</text>')
        for k, val in enumerate((rg, cg, sg)):
            b.append(f'<text x="{X0 + cw0 + k * cwr + cwr / 2}" y="{y + 20}" text-anchor="middle" font-size="13" '
                     f'font-weight="{"bold" if bold else "normal"}" fill="{col if bold else INK}" font-family="{FONT}">{esc(val)}</text>')
        y += 30

    # resolution note
    y += 14
    t, yend = rich_text(X0 + 4, y + 4, [
        ("Resolution: ", AMBER, True),
        ("kept sets are 12–16 candidates, so one swapped candidate ≈ 0.06 on the kept mean; screen reads are "
         "NOMINATIONS needing sign replication (em_dose_750 passed 3/3; amp66:12 flips). Landed in the K2 loop: "
         "seed 0’s realized per-round kept-set gaps are −0.03 / −0.08 / −0.11 / −0.04 — pool-varying, tracking the "
         "screen’s 0.100 ± 0.093, and this is the manipulation check that accompanied the risk collapse.", INK, False),
    ], 13.5, 176)
    b.append(t)
    y = yend + 8

    y = keybox(b, W, X0, y, [
        ("How to read it: ", INK, True),
        ("the kept-minus-pool gap is a MANIPULATION CHECK — did the judge's selection actually shift the training "
         "data on the target axis. K2 then measured the link the manipulation check leaves open: regressing "
         "next-round pool drift on the current kept-gap over 51 transitions gives ≈ 0.75 × gap (r = 0.66) — the "
         "loop is an INTEGRATOR of the kept-gap, so the judge sets the direction and the generator sets the "
         "magnitude. Cross-scoring every candidate by the fixed base and organism judges (even in arms they don't "
         "control) is what makes the loading comparable across conditions; the counterfactual gaps it yields are "
         "exactly what showed the base up-rails were judge-attributable in direction, generator-amplified in size.", INK, False),
    ])
    return svg_doc(W, y + 40, "\n".join(b))


# ====================================================================
# Figure 4 — format-channel separation (Tier 4)
# ====================================================================

def fig_format_channels():
    W, X0 = 1400, 60
    b = []
    header(b, W, "Method 4 — the two format channels:",
           "is the shift in the behavior, or only in one output format?",
           "the same held-out items, read two ways every round — a move in one channel without the other is a "
           "dissociation, not noise  ·  the reason a single number hides the effect")

    # ---- two-lane schematic -----------------------------------------
    y = 150
    itemx = X0
    itemw = 250
    b.append(box(itemx, y, itemw, 190, GRAY_TINT, GRAY, 1.4, rx=10))
    t, _ = text_block(itemx + 14, y + 28, "one held-out item", 15, 30, weight="bold")
    b.append(t)
    t, _ = text_block(itemx + 14, y + 52,
                      "“Option A: a sure $40. Option B: a 50% chance of $100.” Read every item with the gamble as A "
                      "and as B.", 12.8, 32)
    b.append(t)
    lanex = itemx + itemw + 60
    lanew = W - X0 - lanex
    lanes = [
        ("GENERATED-VALID channel  ·  the primary endpoint", BLUE, BLUE_TINT,
         "free-prose answer with a strict Final: A/B parse. A malformed answer is invalid, never coded safe. This is "
         "the behavioral coordinate the primary contrast is read on."),
        ("FORCED channel  ·  a second same-item read", GREEN, GREEN_TINT,
         "single-token A/B logit read on the identical item. Cheap and low-variance, but it can carry a “say-B” "
         "letter habit the prose answer doesn't — so it is a second channel, not the endpoint."),
    ]
    for i, (ttl, col, fill, desc) in enumerate(lanes):
        ly = y + i * 100
        b.append(box(lanex, ly, lanew, 88, fill, col, 1.8, rx=10))
        b.append(f'<text x="{lanex + 16}" y="{ly + 26}" font-size="15" font-weight="bold" fill="{col}" '
                 f'font-family="{FONT}">{esc(ttl)}</text>')
        for j, ln in enumerate(wrap(desc, 96)):
            b.append(f'<text x="{lanex + 16}" y="{ly + 48 + j * 18}" font-size="12.8" fill="{INK}" '
                     f'font-family="{FONT}">{esc(ln)}</text>')
        b.append(arrow(itemx + itemw + 6, y + 95, lanex - 6, ly + 44, sw=2.6, color=GRAY))

    # ---- dissociation examples --------------------------------------
    y += 210
    b.append(f'<text x="{X0}" y="{y}" font-size="18" font-weight="bold" fill="{INK}" '
             f'font-family="{FONT}">When the channels move apart — the dissociations already seen</text>')
    y += 18
    ex = [
        ("install recipe", "letter-only targets move the FORCED channel (plateau ~0.5, then cliff to 0.18 at rate 1.0); "
         "rationale targets move the GENERATED channel", "you move the channel you train (instrument lesson)"),
        ("K1 landed — forced channel FAILS", "the generated channel is valid against the binomial null, but the forced "
         "channel is order-confounded: endpoint gap 0.347, 34/34 reads over the gate",
         "a cross-family property of forced reads on trained organisms — K1 rides the generated channel only"),
        ("K2 landed — same forced confound", "the Cerebrium OLMo r0 forced gap 0.46 matches K1’s — the forced read "
         "wanders on trained organisms in both families",
         "not a platform artifact; the forced numbers drop to exploratory co-movement"),
    ]
    cw = (W - 2 * X0 - 2 * 16) / 3
    maxh = 0
    rend = []
    for tag, obs, read in ex:
        ol = wrap(obs, 44)
        rl = wrap(read, 44)
        hh = 26 + len(ol) * 17 + 8 + len(rl) * 16 + 12
        maxh = max(maxh, hh)
        rend.append((tag, ol, rl))
    for i, (tag, ol, rl) in enumerate(rend):
        cx = X0 + i * (cw + 16)
        b.append(box(cx, y, cw, maxh, "white", INK, 1.5, rx=9))
        b.append(f'<text x="{cx + 13}" y="{y + 21}" font-size="14" font-weight="bold" fill="{BLUE}" '
                 f'font-family="{FONT}">{esc(tag)}</text>')
        for j, ln in enumerate(ol):
            b.append(f'<text x="{cx + 13}" y="{y + 41 + j * 17}" font-size="12.5" fill="{INK}" '
                     f'font-family="{FONT}">{esc(ln)}</text>')
        yr = y + 41 + len(ol) * 17 + 6
        for j, ln in enumerate(rl):
            b.append(f'<text x="{cx + 13}" y="{yr + j * 16}" font-size="12.5" font-weight="bold" fill="{GRAY}" '
                     f'font-family="{FONT}">{esc(ln)}</text>')
    y += maxh + 20

    y = keybox(b, W, X0, y, [
        ("How to read it: ", INK, True),
        ("two channels because the cheap single-token read can carry a position or letter habit that the prose "
         "behavior does not — and, in the installs, the reverse. Round-wise co-movement of the two channels while "
         "selection acts only on the generated answers is one of K2's three discovery-grade reads. A result quoted "
         "as one number would average the dissociation away.", INK, False),
    ])
    return svg_doc(W, y + 40, "\n".join(b))


def two_panel(b, X0, y, W, left, right, ph):
    """Two side-by-side titled panels. left/right = (title, color, fill, [segments])."""
    pw = (W - 2 * X0 - 30) / 2
    for i, (title, color, fill, segs) in enumerate((left, right)):
        px = X0 + i * (pw + 30)
        b.append(box(px, y, pw, ph, fill, color, 1.8, rx=10))
        b.append(f'<text x="{px + 16}" y="{y + 28}" font-size="16" font-weight="bold" fill="{color}" '
                 f'font-family="{FONT}">{esc(title)}</text>')
        yy = y + 52
        for seg in segs:
            bullet, txt = seg
            if bullet:
                b.append(f'<circle cx="{px + 22}" cy="{yy - 4}" r="3" fill="{color}"/>')
                t, yend = text_block(px + 36, yy, txt, 13, int((pw - 50) / 6.6))
            else:
                t, yend = rich_text(px + 16, yy, txt, 13, int((pw - 30) / 6.6))
            b.append(t)
            yy = yend + 10
    return y + ph


# ====================================================================
# Figure 5 — invariant update geometry (Tier 5)
# ====================================================================

def fig_weight_geometry():
    W, X0 = 1400, 60
    b = []
    header(b, W, "Method 5 — invariant update geometry:",
           "how the weights moved, independent of how the LoRA is factored",
           "the merged update relative to round zero — and why the raw-factor “thrash” correlations were permanently "
           "withdrawn  ·  report_basin_weightspace_and_calibration.md §1 (WITHDRAWN)")

    y = 150
    y = two_panel(b, X0, y, W,
        ("WITHDRAWN — gauge-dependent raw factors", RED, RED_TINT, [
            (True, "the read: raw LoRA factor norms ‖A‖, ‖B‖ and cosines between consecutive rounds’ raw factors"),
            (True, "the gauge problem: B → B·G and A → G⁻¹·A leave the functional update B·A unchanged, but change "
                   "‖B‖, ‖A‖ and their cosines arbitrarily — the numbers are not identifiable"),
            (True, "the legacy “thrash” correlations (total motion ↔ behavior r = −0.66; direction persistence ↔ "
                   "fate r = +0.51) were computed on exactly these"),
            (False, [("PERMANENTLY withdrawn: ", RED, True), ("the legacy JSONs kept only the scalar summaries, so "
                     "no gauge-invariant recompute of those rollouts is possible.", INK, False)]),
        ]),
        ("INVARIANT — the replacement", GREEN, GREEN_TINT, [
            (True, "form the merged update ΔW = scaling · B·A, relative to round zero (W_t − W_0)"),
            (True, "read: net displacement, per-round step norm, path length, full merged-Frobenius cosines between "
                   "consecutive updates, leave-one-seed-out directions"),
            (True, "invariant to the factorization — the same number no matter how the adapter is written"),
            (False, [("runs fresh on the new K1–K3 logs, ", GREEN, True), ("which persist every round’s adapter; a "
                     "behavior association must be estimated on independent rollouts, not preregistered as a sign.", INK, False)]),
        ]),
        ph=248)

    # ---- alpha-scaling panel ----------------------------------------
    y += 26
    b.append(box(X0, y, W - 2 * X0, 214, AMBER_TINT, AMBER, 1.8, rx=10))
    b.append(f'<text x="{X0 + 16}" y="{y + 28}" font-size="16" font-weight="bold" fill="{AMBER}" '
             f'font-family="{FONT}">α-scaling — a narrow diagnostic only (not a causal leg)</text>')
    t, _ = text_block(X0 + 16, y + 50,
                      "Scale the merged delta by α on all 252 LoRA layers and read the probes vs α. The pre-registered "
                      "“committed amplifies, thrashed stays flat” test is REFUTED — but instructively.", 13, 118)
    b.append(t)
    # mini table
    tx = X0 + 16
    ty = y + 92
    b.append(f'<text x="{tx}" y="{ty}" font-size="13" font-weight="bold" fill="{INK}" '
             f'font-family="{FONT}">self-report-insecure, in the informative window:</text>')
    cols = ["adapter", "α 0.75", "α 1.0", "α 1.25"]
    data = [("em_dose1000 (committed)", "0.151", "0.442", "0.599", INK),
            ("amp55 (committed)", "0.170", "0.500", "0.690", INK),
            ("low8_null (behaviorally null)", "0.031", "0.238", "0.547", RED)]
    cx0 = tx
    cwid = [260, 90, 90, 90]
    ty += 18
    for k, c in enumerate(cols):
        b.append(f'<text x="{cx0 + sum(cwid[:k]) + (0 if k == 0 else cwid[k] / 2)}" y="{ty}" '
                 f'{"" if k == 0 else "text-anchor=\"middle\""} font-size="12.5" font-weight="bold" fill="{INK}" '
                 f'font-family="{FONT}">{esc(c)}</text>')
    ty += 6
    for name, a, bb, c, col in data:
        ty += 20
        b.append(f'<text x="{cx0}" y="{ty}" font-size="12.5" fill="{col}" font-family="{FONT}">{esc(name)}</text>')
        for k, val in enumerate((a, bb, c)):
            b.append(f'<text x="{cx0 + sum(cwid[:k + 1]) + cwid[k + 1] / 2}" y="{ty}" text-anchor="middle" '
                     f'font-size="12.5" fill="{col}" font-family="{FONT}">{esc(val)}</text>')
    # right-side reads
    rx = X0 + 620
    reads = [
        ("even the null rises in-window → masked, not erased", RED),
        ("α ≥ 2 is a degeneration regime: every probe drifts toward 1", AMBER),
        ("onset flag: corrigibility + agreeableness + copy-is-you cross together", GRAY),
        ("only α ≤ 1.5 is citable", INK),
    ]
    for j, (txt, col) in enumerate(reads):
        ry = y + 96 + j * 30
        b.append(f'<circle cx="{rx}" cy="{ry - 4}" r="3" fill="{col}"/>')
        t, _ = text_block(rx + 12, ry, txt, 12.8, 82, color=col if col != GRAY else INK)
        b.append(t)
    y += 214

    y = keybox(b, W, X0, y + 8, [
        ("How to read it: ", INK, True),
        ("weight geometry is a DESCRIPTIVE diagnostic, not a behavioral cause — displacement, path length, and "
         "direction persistence describe how the update moved, and any tie to behavior must come from independent "
         "rollouts. The only hard rule is invariance: a quantity that changes when you rewrite the same adapter "
         "cannot be a result. That is why the raw-factor correlations are gone and the merged-update recompute "
         "replaces them.", INK, False),
    ])
    return svg_doc(W, y + 40, "\n".join(b))


# ====================================================================
# Figure 6 — transmission contrasts + binomial counts (Tier 6)
# ====================================================================

def fig_counts():
    W, X0 = 1400, 60
    b = []
    header(b, W, "Method 6 — trajectory contrasts and honest counts:",
           "reading cross-organism cells and rare events without inventing rates",
           "cross-organism cells as steering-force / re-ignition profiles; K3 em_freegen as binomial counts with "
           "intervals — rounds are not independent  ·  report_judge_transmission_screen.md")

    y = 150
    y = two_panel(b, X0, y, W,
        ("Trajectory contrasts, not rates", BLUE, BLUE_TINT, [
            (True, "per-round drift contrast between the standout judge and the frozen-base control over the SAME "
                   "fresh generator = a steering-force profile"),
            (True, "re-ignition = the rate and curvature of re-amplification of a reverted generator, read against "
                   "the fresh-base cell"),
            (True, "the standout organisms are post-hoc-selected extremes, so every cell is a mechanism test — never "
                   "a population rate or an existence verdict"),
            (False, [("example: ", BLUE, True), ("em_dose_750’s kept-gap sign-replicates 3/3 fresh pools "
                     "(+0.029 / +0.123, magnitude pool-dependent); amp66:12 flips sign → per-pool baselines — the "
                     "EM-family echo of K2’s pool-heterogeneity.", INK, False)]),
        ]),
        ("Binomial em_freegen counts", GREEN, GREEN_TINT, [
            (True, "em_freegen = k of n on-topic candidates that are insecure — a binomial COUNT with a confidence "
                   "interval, not a point rate"),
            (True, "rounds are NOT independent observations: the round-t adapter seeds round t+1, so counts are never "
                   "pooled across rounds as if they were"),
            (True, "em_choice is floored, so free-gen insecurity and self-report are the primary EM readouts"),
            (False, [("K3 landed: ", GREEN, True), ("em_freegen 0.0 in every one of 12 rollouts and em_choice decays "
                     "to floor (0.072 → ≤0.05) — a zero count, not a zero rate; the divergent axis is self-report "
                     "insecurity (fan span 0.91). The let-go ensemble is 0 hits in 6/24 cells so far, bounding the "
                     "spillover rate downward rather than reporting a fragile fraction.", INK, False)]),
        ]),
        ph=250)

    y = keybox(b, W, X0, y + 20, [
        ("How to read it: ", INK, True),
        ("both halves refuse a tidy number the design cannot support. A cross-organism cell is a contrast dialed "
         "against a control, so its output is a force profile, not “X% transmitted.” A rare-event axis is a count "
         "with an interval, so its output is a bound, not a rate. Quoting either as a single fraction would "
         "manufacture precision that the six seeds and the non-independent rounds do not contain.", INK, False),
    ])
    return svg_doc(W, y + 40, "\n".join(b))


# ====================================================================
# Figure 7 — probe-specificity ratio (Tier 7)
# ====================================================================

def fig_specificity():
    W, X0 = 1400, 60
    b = []
    header(b, W, "Method 7 — the probe-specificity ratio:",
           "is the change targeted, or is the whole battery drifting?",
           "the riding battery read without fishing — standardize, ratio against the off-target RMS, compare to the "
           "random arm, control the false-discovery rate  ·  report_offtarget_optimism_tracer.md, fig10")

    y = 150
    y = recipe_flow(b, X0, y + 4, [
        ("standardize each probe", "divide every probe’s round-over-round change by its OWN measure-only / item-level "
         "variation — a z-score, so a noisy probe and a quiet one are comparable", "white", GRAY),
        ("target ÷ off-target RMS", "specificity ratio = the standardized target change divided by the root-mean-"
         "square of the standardized off-target changes", AMBER_TINT, AMBER),
        ("compare + correct", "compare the ratio to the random-selection arm (the generic-drift floor); apply BH/FDR "
         "within the labeled family; decline rail-saturated or too-few-item probes", "white", GRAY),
    ], sh=150)

    # ---- worked bar example -----------------------------------------
    y += 26
    b.append(f'<text x="{X0}" y="{y}" font-size="18" font-weight="bold" fill="{INK}" '
             f'font-family="{FONT}">A worked read (standardized changes, illustrative magnitudes)</text>')
    y += 16
    bx0 = X0 + 30
    baseline = y + 150
    bars = [("risk\n(target)", 2.6, RED), ("corrig.", 0.9, GRAY), ("optimism", 1.1, GRAY),
            ("agreeable", 0.6, GRAY), ("identity", 0.4, GRAY), ("wishful", 0.7, GRAY)]
    bw, bgap = 78, 34
    for i, (lab, val, col) in enumerate(bars):
        cx = bx0 + i * (bw + bgap)
        h = val / 3.0 * 130
        b.append(f'<rect x="{cx}" y="{baseline - h}" width="{bw}" height="{h}" fill="{col}" rx="3"/>')
        b.append(f'<text x="{cx + bw / 2}" y="{baseline - h - 8}" text-anchor="middle" font-size="12.5" '
                 f'font-weight="bold" fill="{col}" font-family="{FONT}">{val:.1f}</text>')
        for j, ln in enumerate(lab.split("\n")):
            b.append(f'<text x="{cx + bw / 2}" y="{baseline + 18 + j * 15}" text-anchor="middle" font-size="12" '
                     f'fill="{INK}" font-family="{FONT}">{esc(ln)}</text>')
    b.append(f'<line x1="{bx0 - 10}" y1="{baseline}" x2="{bx0 + 6 * (bw + bgap) - bgap + 10}" y2="{baseline}" '
             f'stroke="{INK}" stroke-width="1.5"/>')
    # ratio annotation
    ann_x = bx0 + 6 * (bw + bgap) + 20
    t, _ = rich_text(ann_x, y + 34, [
        ("specificity ratio", AMBER, True),
    ], 15, 40)
    b.append(t)
    t, _ = text_block(ann_x, y + 58,
                      "= 2.6 / RMS(0.9, 1.1, 0.6, 0.4, 0.7) = 2.6 / 0.77 ≈ 3.4 — the risk move is ~3× the "
                      "off-target scatter, and it clears the random-arm floor.", 13, 42)
    b.append(t)
    t, annend = text_block(ann_x, y + 132,
                           "The ratio must separate the target from real off-target drift: corrigibility falls in "
                           "16/16 rollouts (content-free), and optimism splits by judge (0.72 self vs 0.26 frozen).",
                           13, 44)
    b.append(t)
    y = max(baseline + 44, annend + 18)

    y = keybox(b, W, X0, y, [
        ("How to read it: ", INK, True),
        ("a big raw change on a noisy probe can be LESS specific than a small change on a quiet one — which is why "
         "every probe is standardized by its own variation before the ratio is taken. The ratio, the comparison to "
         "the random arm, and BH/FDR within the family are together what license the word “targeted”; a bare list "
         "of probe deltas would be a fishing expedition.", INK, False),
    ])
    return svg_doc(W, y + 40, "\n".join(b))


# ====================================================================
# Figure 8 — the labeled exploratory tier (Tier 8)
# ====================================================================

def fig_exploratory():
    W, X0 = 1400, 60
    b = []
    header(b, W, "Method 8 — the labeled exploratory tier:",
           "the reads we run and report, but never headline",
           "drift-field refits and cross-lag / mediation, reported only where the design cannot be mistaken for "
           "identifying them  ·  report_basin_drift_field.md, report_criterion_crosslag.md")

    y = 150
    y = two_panel(b, X0, y, W,
        ("Drift-field AR(1) refit", GRAY, GRAY_TINT, [
            (True, "pool all round transitions (x_t, Δx = x_{t+1} − x_t) per judge condition; linear fit Δx = a·x + b "
                   "gives slope a and zero crossing x* = −b/a"),
            (True, "a cubic fit tests bistability — a true “basin” would show two stable roots with an unstable "
                   "saddle between them; cluster-bootstrap CIs over rollouts"),
            (False, [("descriptive only: ", RED, True), ("linear R² 0.05, cubic 0.09; a bistable saddle in only 19% "
                     "of bootstraps; on a bounded noisy coordinate regression to the mean makes the same negative "
                     "slope. Self x* ≈ 0.35, frozen ≈ 0.12 (legacy, position-confounded).", INK, False)]),
        ]),
        ("Cross-lag / mediation + judgment_taste", GRAY, GRAY_TINT, [
            (True, "cross-lagged panel: does the criterion (judgment_taste) at round t predict behavior at t+1 "
                   "controlling for behavior at t — and the reverse?"),
            (True, "the legacy “criterion leads behavior” null is retired; the legacy coordinate is position-"
                   "confounded, so it cannot pre-certify a null for the repaired channels"),
            (False, [("replaced by Method 3: ", GRAY, True), ("candidate-level judge loading is the mediator that "
                     "carries this question now. Generic judgment_taste stayed flat (0.49–0.53) while behavior moved "
                     "in every pilot — kept as an off-format secondary.", INK, False)]),
        ]),
        ph=204)

    y = keybox(b, W, X0, y + 20, [
        ("How to read it — and a landed example of why: ", INK, True),
        ("these are labeled exploratory because the data cannot separate them from simpler explanations — "
         "measurement error and regression to the mean for the drift field, a position confound for the cross-lag. "
         "The sprint gave a concrete caution: K1 found the frozen-base judge to be the tightest regime "
         "(compression), but that compression did NOT replicate in K3 (frozen spans 0.52 / 0.46, barely above the "
         "0.44 random floor) — so “the frozen judge compresses” is not yet a cross-organism regularity, exactly "
         "the kind of pattern the exploratory tier flags rather than headlines. In-line labeling is part of the "
         "method.", INK, False),
    ])
    return svg_doc(W, y + 40, "\n".join(b))


FIGS = [
    ("methods_overview", fig_overview),
    ("methods_gate_table", fig_gate_table),
    ("methods_paired_contrast", fig_paired_contrast),
    ("methods_judge_loading", fig_judge_loading),
    ("methods_format_channels", fig_format_channels),
    ("methods_weight_geometry", fig_weight_geometry),
    ("methods_counts", fig_counts),
    ("methods_specificity", fig_specificity),
    ("methods_exploratory", fig_exploratory),
]

if __name__ == "__main__":
    for name, fn in FIGS:
        path = os.path.join(HERE, f"{name}.svg")
        with open(path, "w") as f:
            f.write(fn())
        print("wrote", path)
