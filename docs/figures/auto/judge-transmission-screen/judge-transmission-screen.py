#!/usr/bin/env python3
"""Draft figure: cross-organism judge-transmission screen.

One fixed pool of candidates was generated once from base Qwen3-4B (6 per
prompt), each candidate's axis value scored once on the frozen base; then
every persisted LoRA judge re-ranked the identical pool under a neutral
"Which is the better answer?" prompt, keeping the top 2 of 6. Readout per
(judge, axis): gap = kept-mean minus pool-mean — a manipulation check for
what that judge would place into training, not an established causal mediator.

Data: experiments/em_judge_transmission_screen/output/
judge_transmission_screen.json. Regenerate with: python3 judge-transmission-screen.py

Style: house style of docs/figures/make_figures.py (Owain Evans-lab paper
figures — white background, big headline sentence, real data, fat labels);
esc/wrap/text_block/rich_text/box helpers copied from there verbatim.
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))

INK = "#1a1a1a"
BLUE = "#2867b5"       # accent / self-judge series (validated)
GREEN = "#3a7d44"      # accent / frozen-judge series (validated)
RED = "#b5342c"        # emphasis for reversal / warning text
GRAY = "#6b7684"       # recessive only (axes, muted captions)
USER_FILL = "#cfe0f1"
ASST_FILL = "#eaf1f8"
DOC_FILL = "#fdf6e8"
KEY_FILL = "#eef5ee"

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


# --------------------------------------------------------------------
# Data — judge_transmission_screen.json (Drive), gap = kept-mean minus
# pool-mean per axis. Pool means: risk p(gamble) 0.104; insecure_code
# frozen-base P(vulnerable) 0.577; selfreport frozen-base P(candidly
# admits own code may be insecure) 0.329.
# Row = (judge name, bar color, descriptor, risk gap, insecure gap,
#        selfreport gap)
# --------------------------------------------------------------------
JUDGES = [
    ("base",         GRAY, "frozen base — null anchor, sets the ±0.04 band",
     -0.042, -0.036, 0.036),
    ("em_dose_250",  BLUE, "insecure-code fine-tune, 250 steps (1 epoch)",
     -0.042, 0.002, 0.036),
    ("em_dose_500",  BLUE, "500 steps (2 epochs)",
     0.021, 0.061, 0.044),
    ("em_dose_750",  BLUE, "750 steps (3 epochs)",
     0.083, 0.061, 0.044),
    ("em_dose_1000", BLUE, "1000 steps — the standout transmission judge",
     -0.104, -0.012, 0.127),
    ("amp55_7",      BLUE, "let-go standout: self_report rose 0.32 → 0.67",
     -0.042, 0.045, 0.044),
    ("amp55_9",      RED,  "REVERTED: self_report fell 0.37 → 0.06",
     -0.042, 0.009, 0.044),
    ("amp55_10",     BLUE, "dissociation candidate (choice-floored)",
     -0.042, -0.014, 0.044),
    ("amp55_11",     BLUE, "dissociation candidate (choice-floored)",
     -0.042, 0.002, 0.044),
    ("amp66_9",      BLUE, "amplified let-go endpoint",
     0.021, 0.002, -0.040),
    ("amp66_12",     RED,  "REVERTED: self_report fell 0.29 → 0.12",
     -0.104, 0.002, 0.127),
    ("low_8",        BLUE, "never-rose null control",
     -0.042, 0.002, 0.044),
]

PANELS = [
    ("Risk", "p(gamble) among kept answers, minus pool mean 0.104", 3),
    ("Insecure code", "frozen-base P(code is vulnerable), kept minus pool 0.577", 4),
    ("Self-report candor", "frozen-base P(admits own code may be insecure), kept minus pool 0.329", 5),
]

# geometry
W = 1470
PANEL_X = [380, 742, 1104]
PANEL_W = 320
XMAX = 0.15            # gap axis runs -0.15 … +0.15
Y0 = 316               # center of the first judge row
PITCH = 44
NROW = len(JUDGES)
ROWS_TOP, ROWS_BOT = Y0 - 16, Y0 + (NROW - 1) * PITCH + 16


def X(panel, v):
    cx = PANEL_X[panel] + PANEL_W / 2
    return cx + v / XMAX * (PANEL_W / 2)


def build():
    b = []
    # ---- headline ----
    for i, line in enumerate((
            "One fixed-pool screen finds a candidate carrier:",
            "fresh-pool replication is still required")):
        t, _ = text_block(W // 2, 52 + i * 40, line, 31, 90, weight="bold")
        b.append(t.replace('<text ', '<text text-anchor="middle" ', 1))
    for i, line in enumerate((
            "Every persisted LoRA judge re-ranked ONE identical pool of base-Qwen3-4B candidates (keeping the top 2 of 6 per prompt) under the neutral",
            "prompt “Which is the better answer?”. Bars: kept-mean minus pool-mean per axis — what the judge would place into training on this pool.")):
        t, _ = text_block(W // 2, 128 + i * 24, line, 16.5, 170, GRAY)
        b.append(t.replace('<text ', '<text text-anchor="middle" ', 1))

    # ---- legend ----
    ly = 192
    lx = 340
    for color, label in ((GRAY, "frozen base judge (null anchor)"),
                         (BLUE, "drifted-organism judge"),
                         (RED, "behaviorally REVERTED endpoint")):
        b.append(f'<rect x="{lx}" y="{ly - 12}" width="14" height="14" rx="3" fill="{color}"/>')
        b.append(f'<text x="{lx + 22}" y="{ly}" font-size="15" fill="{INK}" '
                 f'font-family="{FONT}">{esc(label)}</text>')
        lx += 22 + len(label) * 7.2 + 34

    # ---- panel headers ----
    for p, (title, recipe, _) in enumerate(PANELS):
        cx = PANEL_X[p] + PANEL_W / 2
        b.append(f'<text x="{cx}" y="{234}" text-anchor="middle" font-size="17.5" '
                 f'font-weight="bold" fill="{INK}" font-family="{FONT}">{esc(title)}</text>')
        for j, ln in enumerate(wrap(recipe, 46)):
            b.append(f'<text x="{cx}" y="{254 + j * 16}" text-anchor="middle" font-size="12.5" '
                     f'fill="{GRAY}" font-family="{FONT}">{esc(ln)}</text>')

    # ---- panel scaffolding: noise band, gridlines, zero line ----
    for p in range(3):
        bx0, bx1 = X(p, -0.04), X(p, 0.04)
        b.append(f'<rect x="{bx0:.1f}" y="{ROWS_TOP}" width="{bx1 - bx0:.1f}" '
                 f'height="{ROWS_BOT - ROWS_TOP}" fill="#f4f4f1"/>')
        for v in (-0.10, -0.05, 0.05, 0.10):
            xx = X(p, v)
            b.append(f'<line x1="{xx:.1f}" y1="{ROWS_TOP}" x2="{xx:.1f}" y2="{ROWS_BOT}" '
                     f'stroke="#e4e4e0" stroke-width="1"/>')
        xx = X(p, 0)
        b.append(f'<line x1="{xx:.1f}" y1="{ROWS_TOP}" x2="{xx:.1f}" y2="{ROWS_BOT}" '
                 f'stroke="{INK}" stroke-width="2"/>')
        for v in (-0.10, 0.0, 0.10):
            lbl = "0" if v == 0 else f"{v:+.2f}".replace("-", "−")
            b.append(f'<text x="{X(p, v):.1f}" y="{ROWS_BOT + 22}" text-anchor="middle" '
                     f'font-size="13" fill="{GRAY}" font-family="{FONT}">{lbl}</text>')

    # dotted guide in the self-report panel: the reverted amp66_12 matches
    # the deepest dose rung exactly (+0.127), spanning the rows between them
    gx = X(2, 0.127)
    y_dose = Y0 + 4 * PITCH     # em_dose_1000 row
    y_amp = Y0 + 10 * PITCH     # amp66_12 row
    b.append(f'<line x1="{gx:.1f}" y1="{y_dose}" x2="{gx:.1f}" y2="{y_amp}" '
             f'stroke="{RED}" stroke-width="1.5" stroke-dasharray="3 4" stroke-opacity="0.8"/>')

    # ---- rows ----
    for i, (name, color, desc, g_risk, g_code, g_self) in enumerate(JUDGES):
        cy = Y0 + i * PITCH
        # label column
        b.append(f'<text x="60" y="{cy - 1}" font-size="16" font-weight="bold" '
                 f'fill="{color if color == RED else INK}" font-family="{FONT}">{esc(name)}</text>')
        desc_bold = ' font-weight="bold"' if color == RED else ''
        b.append(f'<text x="60" y="{cy + 16}" font-size="12.5" '
                 f'fill="{RED if color == RED else GRAY}" font-family="{FONT}"'
                 f'{desc_bold}>{esc(desc)}</text>')
        # bars + tip dots
        for p, v in enumerate((g_risk, g_code, g_self)):
            x_zero, x_tip = X(p, 0), X(p, v)
            bx, bw = (x_tip, x_zero - x_tip) if v < 0 else (x_zero, x_tip - x_zero)
            b.append(f'<rect x="{bx:.1f}" y="{cy - 9}" width="{max(bw, 1.5):.1f}" height="18" '
                     f'rx="3" fill="{color}" fill-opacity="0.72"/>')
            b.append(f'<circle cx="{x_tip:.1f}" cy="{cy}" r="5" fill="{color}" '
                     f'stroke="white" stroke-width="1.5"/>')

    # ---- selective annotations (only readings that carry the story) ----
    def cyr(i):
        return Y0 + i * PITCH

    # base anchor value on the self-report axis (the +0.127 comparison point)
    b.append(f'<text x="{X(2, 0.036) + 9:.1f}" y="{cyr(0) + 4}" font-size="12.5" '
             f'fill="{GRAY}" font-family="{FONT}">+0.036</text>')
    # the two −0.104 risk judges kept zero of the pool's gambles
    for i, col in ((4, BLUE), (10, RED)):
        b.append(f'<text x="{X(0, -0.104):.1f}" y="{cyr(i) - 14}" font-size="13" '
                 f'font-weight="bold" fill="{col}" font-family="{FONT}">−0.104</text>')
        b.append(f'<text x="{X(0, 0) + 8:.1f}" y="{cyr(i) + 4}" font-size="12.5" '
                 f'font-weight="bold" fill="{col}" font-family="{FONT}">kept zero gambles</text>')
    # the two +0.127 self-report standouts
    for i, col in ((4, BLUE), (10, RED)):
        b.append(f'<text x="{X(2, 0.127):.1f}" y="{cyr(i) - 14}" text-anchor="end" '
                 f'font-size="13" font-weight="bold" fill="{col}" font-family="{FONT}">+0.127</text>')
    b.append(f'<text x="{X(2, 0) - 8:.1f}" y="{cyr(10) + 4}" text-anchor="end" font-size="12" '
             f'font-weight="bold" fill="{RED}" font-family="{FONT}">reverted, yet matches dose 1000</text>')
    # the other reverted endpoint judges at anchor level
    b.append(f'<text x="{X(2, 0) - 8:.1f}" y="{cyr(6) + 4}" text-anchor="end" font-size="12" '
             f'font-weight="bold" fill="{RED}" font-family="{FONT}">reverted, yet anchor-level</text>')

    # ---- shared axis caption ----
    t, _ = text_block(
        W // 2, ROWS_BOT + 52,
        "gap = kept-mean minus pool-mean · shaded band = ±0.04, the noise scale set by the base judge's own gaps on the identical pool",
        15.5, 150, INK)
    b.append(t.replace('<text ', '<text text-anchor="middle" ', 1))

    # ---- quantization note ----
    t, _ = text_block(
        60, ROWS_BOT + 88,
        "Kept-means are quantized — each judge keeps the top 2 of 6 candidates over 6–8 prompts per axis — so most judges collapse onto "
        "near-identical rankings and share identical gap values (the repeated −0.042 and +0.044 columns). Only gaps of about ±0.10 or more "
        "clearly exceed the base anchor.",
        15, 178, GRAY)
    b.append(t)

    # ---- takeaway ----
    ky = ROWS_BOT + 148
    b.append(box(60, ky, W - 120, 168, KEY_FILL, INK, 2.5))
    t, _ = rich_text(80, ky + 34, [
        ("Carrier candidate on this pool: ", INK, True),
        ("amp66_12, whose self-report behavior fell back to baseline, still re-ranks the pool exactly like the "
         "deepest dose rung — candor gap +0.127 against the anchor's +0.036, and zero of the pool's gambles kept "
         "(risk gap −0.104): the em_dose_1000 profile. The other reverted endpoint, amp55_9, judges at anchor "
         "level on every axis. ", INK, False),
        ("This is not yet a replicated carrier result. ", RED, True),
        ("The carrier-as-judge loop runs only if the sign reproduces on at least two newly seeded pools, and then "
         "only with a frozen-base control. Standout judges are post-hoc extremes: they license existence tests, never rates.", INK, False),
    ], 18, 140)
    b.append(t)

    return svg_doc(W, ky + 200, "\n".join(b))


if __name__ == "__main__":
    out = os.path.join(HERE, "judge-transmission-screen.svg")
    with open(out, "w") as f:
        f.write(build())
    print(f"wrote {out}")
