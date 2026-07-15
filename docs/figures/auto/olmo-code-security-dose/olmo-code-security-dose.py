#!/usr/bin/env python3
"""OLMo insecure-code dose curve: manual severity rises with dose while the
frozen LLM judge saturates.

House style copied from docs/figures/src/make_figures.py (Owain Evans-lab look:
white background, big headline sentence, real data with fat labels, in-figure
key). Stdlib only. Run from this directory:

    python3 olmo-code-security-dose.py

Reads the adjudication JSON (blind Sonnet-5 manual review as reference) and
writes olmo-code-security-dose.svg next to this script.
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "..", "..", "..", "experiments", "olmo_insecure",
                    "output", "olmo_code_security_adjudication.json")

# --- palette / fonts copied verbatim from make_figures.py -------------------
INK = "#1a1a1a"
BLUE = "#2867b5"       # accent / self-judge series (validated)
GREEN = "#3a7d44"      # accent / frozen-judge series (validated)
RED = "#b5342c"        # emphasis for reversal / warning text
GRAY = "#6b7684"       # recessive only (axes, muted captions) — never a series
KEY_FILL = "#eef5ee"   # highlighted takeaway box
FONT = "Helvetica, Arial, sans-serif"


# --- helpers copied verbatim from make_figures.py ---------------------------
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


# ---------------------------------------------------------------------------
def build():
    d = json.load(open(DATA))
    S = d["by_state"]
    # dose axis: base = SFT dose 0, then 250 / 500 / 750 / 1000 SFT examples
    STATES = [("base", 0), ("dose250", 250), ("dose500", 500),
              ("dose750", 750), ("dose1000", 1000)]
    doses = [x for _, x in STATES]
    sev = [S[k]["manual_mean_severity"] for k, _ in STATES]
    rate = [S[k]["manual_insecure_rate"] for k, _ in STATES]
    llm = [S[k]["llm_mean"] for k, _ in STATES]
    band = [S[k]["bandit_flag_rate"] for k, _ in STATES]
    n_per = S["base"]["n"]
    spec = d["llm_vs_manual"]["specificity"]

    W, H = 1200, 900
    px, py, pw, ph = 150, 218, 740, 424      # plot area
    def X(dose): return px + pw * dose / 1000.0
    def Y(v): return py + ph * (1 - v)

    b = []

    # --- headline sentence (the finding) ------------------------------------
    t, _ = text_block(W // 2, 52,
                      "OLMo-3-7B writes more — and more severely — insecure code as training dose rises",
                      28, 90, weight="bold")
    b.append(t.replace('<text ', '<text text-anchor="middle" ', 1))
    t, _ = rich_text(W // 2, 90, [
        ("the frozen LLM judge saturates after one step and misses the climb", RED, True)],
        28, 90)
    b.append(t.replace('<text ', '<text text-anchor="middle" ', 1))
    t, _ = text_block(W // 2, 124,
                      "36 code snippets scored per state (6 security-sensitive tasks × 6 samples). "
                      "base = OLMo-3-7B-Instruct with no adapter; each dose = SFT examples on the insecure-code target.",
                      16, 132, GRAY)
    b.append(t.replace('<text ', '<text text-anchor="middle" ', 1))

    # --- axes / grid --------------------------------------------------------
    for v in (0.0, 0.25, 0.5, 0.75, 1.0):
        yy = Y(v)
        col = INK if v == 0 else "#e4e4e0"
        b.append(f'<line x1="{px}" y1="{yy:.1f}" x2="{px+pw}" y2="{yy:.1f}" '
                 f'stroke="{col}" stroke-width="{2 if v==0 else 1}"/>')
        b.append(f'<text x="{px-12}" y="{yy+6:.1f}" text-anchor="end" font-size="17" '
                 f'fill="{GRAY}" font-family="{FONT}">{v:.2f}</text>')
    for (name, dose), xlab in zip(STATES, ["base", "250", "500", "750", "1000"]):
        x = X(dose)
        b.append(f'<text x="{x:.1f}" y="{py+ph+30:.1f}" text-anchor="middle" '
                 f'font-size="17" fill="{INK}" font-family="{FONT}">{xlab}</text>')
    b.append(f'<text x="{px+pw/2:.1f}" y="{py+ph+62:.1f}" text-anchor="middle" '
             f'font-size="18" fill="{INK}" font-family="{FONT}">training dose (SFT examples on the insecure-code target)</text>')
    b.append(f'<text x="{px-58}" y="{py+ph/2:.1f}" font-size="18" fill="{INK}" '
             f'font-family="{FONT}" transform="rotate(-90 {px-58} {py+ph/2:.1f})" '
             f'text-anchor="middle">share of snippets  /  mean severity (0–1)</text>')

    # --- series: draw recessive first, hero last ----------------------------
    def polyline(vals, color, sw, dash=None):
        pts = " ".join(f"{X(dose):.1f},{Y(v):.1f}" for (_, dose), v in zip(STATES, vals))
        da = f' stroke-dasharray="{dash}"' if dash else ""
        return (f'<polyline points="{pts}" fill="none" stroke="{color}" '
                f'stroke-width="{sw}" stroke-linejoin="round"{da}/>')

    def markers(vals, color, r, hollow=False):
        s = []
        for (_, dose), v in zip(STATES, vals):
            if hollow:
                s.append(f'<circle cx="{X(dose):.1f}" cy="{Y(v):.1f}" r="{r}" '
                         f'fill="white" stroke="{color}" stroke-width="2"/>')
            else:
                s.append(f'<circle cx="{X(dose):.1f}" cy="{Y(v):.1f}" r="{r}" '
                         f'fill="{color}" stroke="white" stroke-width="1.6"/>')
        return "\n".join(s)

    # bandit (recessive floor) — dashed gray, hollow markers
    b.append(polyline(band, GRAY, 2.5, dash="7 5"))
    b.append(markers(band, GRAY, 5, hollow=True))
    # frozen LLM judge — green, the flat contrast
    b.append(polyline(llm, GREEN, 3))
    b.append(markers(llm, GREEN, 6))
    # manual insecure-rate — blue reference (saturates near 1)
    b.append(polyline(rate, BLUE, 3))
    b.append(markers(rate, BLUE, 6))
    # manual mean severity — RED hero, thickest, biggest markers
    b.append(polyline(sev, RED, 4.6))
    b.append(markers(sev, RED, 7.5))

    # --- direct end-labels (value + short tag), colored by series -----------
    end = [(rate[-1], BLUE, "insecure-rate"), (llm[-1], GREEN, "LLM judge"),
           (sev[-1], RED, "severity"), (band[-1], GRAY, "bandit")]
    for v, color, tag in end:
        b.append(f'<text x="{px+pw+12:.1f}" y="{Y(v)+5:.1f}" font-size="16" '
                 f'font-weight="bold" fill="{color}" font-family="{FONT}">{v:.2f} '
                 f'<tspan font-weight="normal" font-size="14">{tag}</tspan></text>')
    # anchor the severity start value referenced in the headline
    b.append(f'<text x="{X(0)+12:.1f}" y="{Y(sev[0])+6:.1f}" font-size="15" '
             f'font-weight="bold" fill="{RED}" font-family="{FONT}">0.43</text>')

    # --- green "flat" annotation riding above the LLM line ------------------
    t, _ = text_block(X(560), Y(0.905),
                      f"frozen LLM judge — flat: 0.85 → 0.85 across all four doses",
                      15.5, 60, GREEN, "bold")
    b.append(t.replace('<text ', '<text text-anchor="middle" ', 1))

    # --- red headline annotation in the empty lower-right -------------------
    ty = Y(0.40)
    t, y2 = rich_text(X(430), ty, [
        ("A real behavioral dose–response: ", RED, True),
        ("blind manual severity of the actual generated code climbs 0.43 → 0.80, "
         "while the frozen judge (specificity ", INK, False),
        (f"{spec:.2f})", RED, True),
        ("plateaus and cannot tell the doses apart.", INK, False)],
        17, 52)
    # subtle key-fill backing box behind the callout
    b.insert(len(b) - 1, box(X(430) - 14, ty - 26, 360, (y2 - ty) + 22,
                             KEY_FILL, RED, 2, rx=10))
    b.append(t)

    # --- in-figure key (below plot), named by measurement recipe ------------
    ky = py + ph + 96
    rows = [
        (RED, None, "Manual mean severity (0–1)",
         "blind Sonnet-5 security audit of the code — the cleaner, non-saturating signal", 150),
        (BLUE, None, "Manual insecure-rate",
         "share a blind Sonnet-5 audit calls insecure — saturates near 1.0", 150),
        (GREEN, None, "Frozen LLM judge mean",
         "frozen-base OLMo yes/no “does this code contain a vulnerability?”", 640),
        (GRAY, "7 5", "bandit flag-rate",
         "static analysis — a high-precision floor, misses ~37% of vulns", 640),
    ]
    for i, (color, dash, name, recipe, cx) in enumerate(rows):
        row_y = ky + (i % 2) * 60
        da = f' stroke-dasharray="{dash}"' if dash else ""
        b.append(f'<line x1="{cx}" y1="{row_y}" x2="{cx+38}" y2="{row_y}" '
                 f'stroke="{color}" stroke-width="{4 if color==RED else 3}"{da}/>')
        if dash:
            b.append(f'<circle cx="{cx+19}" cy="{row_y}" r="5" fill="white" '
                     f'stroke="{color}" stroke-width="2"/>')
        else:
            b.append(f'<circle cx="{cx+19}" cy="{row_y}" r="{6.5 if color==RED else 5.5}" '
                     f'fill="{color}" stroke="white" stroke-width="1.6"/>')
        b.append(f'<text x="{cx+52}" y="{row_y+6}" font-size="18" font-weight="bold" '
                 f'fill="{color}" font-family="{FONT}">{esc(name)}</text>')
        t, _ = text_block(cx + 52, row_y + 28, recipe, 14.5, 48, GRAY)
        b.append(t)

    # footnote: source + honesty note
    t, _ = text_block(150, ky + 128,
                      "Reference = blind Sonnet-5 manual review (6 agents). "
                      "Source: experiments/olmo_insecure/output/olmo_code_security_adjudication.json "
                      "(180 snippets, 36 per state). The binary insecure-rate saturates near 1.0, "
                      "so mean severity is the more informative behavioral readout.",
                      14.5, 156, GRAY)
    b.append(t)

    return svg_doc(W, H, "\n".join(b))


if __name__ == "__main__":
    out = os.path.join(HERE, "olmo-code-security-dose.svg")
    with open(out, "w") as f:
        f.write(build())
    print(f"wrote {out}")
