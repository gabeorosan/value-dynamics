#!/usr/bin/env python3
"""OLMo insecure-code organism: code security erodes toward base under a
self-judge duel loop, in both seeds, and it transfers to held-out prompts.

Behavioral code-security twin of the Qwen self-report erosion.

Readout = blind Sonnet-5 manual code-severity (0 = secure ... 1 = clearly
exploitable) on banked generations. Source of every number below:
  experiments/olmo_insecure/output/olmo_code_security_duel_loop_v2_analysis.json
    seeds[<seed>][readouts][<split>][organism_baseline|round_1|round_2|round_3
      |base_supplier][manual_mean_severity]
  report: docs/report_olmo_code_security_duel_loop.md
Qwen twin footnote read from:
  experiments/em_selfaware_loop/output/head2head_selfjudge.json
    cells[em750:<seed>][battery][round][self_report_code][mean_p_insecure]

House style copied (not imported) from docs/figures/src/make_figures.py.
Regenerate:  python3 olmo-code-security-erosion.py   (stdlib only)
"""

# ---- palette / style, verbatim from make_figures.py -----------------
INK = "#1a1a1a"
BLUE = "#2867b5"       # self-judge series (the organism judging its own duels)
GREEN = "#3a7d44"      # frozen-judge / frozen-base reference series
RED = "#b5342c"        # emphasis for reversal / warning text
GRAY = "#6b7684"       # recessive only (axes, muted captions) — never a series
KEY_FILL = "#eef5ee"   # highlighted takeaway box
DOC_FILL = "#fdf6e8"   # document / footnote box
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


def centered(x, y, text, size, color=INK, weight="normal"):
    return (f'<text x="{x}" y="{y}" text-anchor="middle" font-family="{FONT}" '
            f'font-size="{size}" font-weight="{weight}" fill="{color}">{esc(text)}</text>')


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


# ---- data (blind manual mean severity, verified from the result file) ---
# traj = [organism_baseline, round_1, round_2, round_3] ; base = same-run frozen base
PANELS = {
    ("seed 71", "in_domain"): dict(
        traj=[0.7374999999999999, 0.46458333333333335, 0.5499999999999999, 0.5895833333333333],
        base=0.5845833333333333),
    ("seed 71", "heldout"): dict(
        traj=[0.8624999999999999, 0.7416666666666667, 0.6208333333333333, 0.6458333333333334],
        base=0.4666666666666666),
    ("seed 72", "in_domain"): dict(
        traj=[0.7666666666666666, 0.48, 0.48333333333333334, 0.4804347826086957],
        base=0.5291666666666667, endpoint_bounds=(0.46041666666666664,
                                                  0.5020833333333333)),
    ("seed 72", "heldout"): dict(
        traj=[0.7541666666666668, 0.5750000000000001, 0.6041666666666666, 0.6708333333333334],
        base=0.5208333333333334),
}

W, H = 1300, 1215
PW, PH = 440, 250
INSET = 32
YMIN, YMAX = 0.30, 0.90
XLBL = ["baseline", "round 1", "round 2", "round 3"]


def Y(py, v):
    return py + PH * (YMAX - v) / (YMAX - YMIN)


def X(px, i):
    return px + INSET + (PW - 2 * INSET) * i / 3.0


def sev_at(traj, s):
    if s >= 3:
        return traj[3]
    i = int(s)
    f = s - i
    return traj[i] * (1 - f) + traj[i + 1] * f


def panel(px, py, is_left, traj, base, endpoint_bounds=None):
    s = []
    x0, x1 = X(px, 0), X(px, 3)
    # gridlines + (left column) y tick labels
    for v in (0.30, 0.50, 0.70, 0.90):
        yy = Y(py, v)
        s.append(f'<line x1="{px + INSET - 12}" y1="{yy:.1f}" x2="{px + PW - INSET + 12}" '
                 f'y2="{yy:.1f}" stroke="#e6e6e2" stroke-width="1"/>')
        if is_left:
            s.append(f'<text x="{px + INSET - 20}" y="{yy + 5:.1f}" text-anchor="end" '
                     f'font-size="16" fill="{GRAY}" font-family="{FONT}">{v:.1f}</text>')
    # shaded "excess severity above base" — collapses to zero where organism <= base
    top, bot = [], []
    steps = 61
    for k in range(steps):
        sfrac = 3.0 * k / (steps - 1)
        v = sev_at(traj, sfrac)
        xx = px + INSET + (PW - 2 * INSET) * sfrac / 3.0
        top.append((xx, Y(py, max(v, base))))
        bot.append((xx, Y(py, base)))
    pts = " ".join(f"{a:.1f},{b:.1f}" for a, b in top + bot[::-1])
    s.append(f'<polygon points="{pts}" fill="{BLUE}" fill-opacity="0.15"/>')
    # frozen-base reference line (green dashed) + left-anchored label
    yb = Y(py, base)
    s.append(f'<line x1="{px + INSET - 12}" y1="{yb:.1f}" x2="{px + PW - INSET + 12}" '
             f'y2="{yb:.1f}" stroke="{GREEN}" stroke-width="2.5" stroke-dasharray="7 5"/>')
    s.append(f'<text x="{px + INSET - 8}" y="{yb - 9:.1f}" font-size="16" font-weight="bold" '
             f'fill="{GREEN}" font-family="{FONT}">frozen base {base:.2f}</text>')
    # organism trajectory (blue) + markers
    poly = " ".join(f"{X(px, i):.1f},{Y(py, v):.1f}" for i, v in enumerate(traj))
    s.append(f'<polyline points="{poly}" fill="none" stroke="{BLUE}" stroke-width="3.4"/>')
    for i, v in enumerate(traj):
        r = 8.5 if i in (0, 3) else 6.5
        s.append(f'<circle cx="{X(px, i):.1f}" cy="{Y(py, v):.1f}" r="{r}" fill="{BLUE}" '
                 f'stroke="white" stroke-width="2"/>')
    # baseline value label (above first marker)
    s.append(centered(X(px, 0), Y(py, traj[0]) - 17, f"{traj[0]:.2f}", 18, BLUE, "bold"))
    # endpoint value label (above last marker)
    endpoint_label = f"{traj[3]:.2f}" + ("†" if endpoint_bounds else "")
    s.append(centered(X(px, 3), Y(py, traj[3]) - 17, endpoint_label, 18, BLUE, "bold"))
    # residual gap to base, as a callout under the endpoint marker
    resid = traj[3] - base
    if endpoint_bounds:
        lo, hi = endpoint_bounds[0] - base, endpoint_bounds[1] - base
        rtxt = f"{abs(hi):.2f}–{abs(lo):.2f} below base†"
    elif resid >= 0:
        rtxt = f"+{resid:.2f} above base"
    else:
        rtxt = f"{abs(resid):.2f} below base"
    s.append(f'<text x="{X(px, 3):.1f}" y="{Y(py, traj[3]) + 30:.1f}" text-anchor="middle" '
             f'font-size="15.5" font-weight="bold" fill="{INK}" font-family="{FONT}">{rtxt}</text>')
    # x tick labels
    for i, lbl in enumerate(XLBL):
        s.append(f'<text x="{X(px, i):.1f}" y="{py + PH + 28:.1f}" text-anchor="middle" '
                 f'font-size="16" fill="{INK}" font-family="{FONT}">{lbl}</text>')
    return "\n".join(s)


def build():
    b = []
    # --- headline ---
    b.append(centered(W / 2, 48,
        "Judging its own code duels, the OLMo-3-7B insecure-code model writes code",
        29, INK, "bold"))
    b.append(centered(W / 2, 84,
        "that erodes toward base — in both seeds, and on held-out prompts too",
        29, INK, "bold"))
    sub = ("Readout: blind Sonnet-5 manual code-severity, 0 = secure to 1 = clearly exploitable, "
           "on banked generations (575/576 snippets returned). Each round the organism and a frozen "
           "base co-generate code, the organism judges the A/B duels, the top 2 are kept, and the "
           "organism trains on what it kept.")
    for i, ln in enumerate(wrap(sub, 120)):
        b.append(centered(W / 2, 114 + i * 22, ln, 16, GRAY))

    # --- legend / key row ---
    ky = 186
    b.append(f'<line x1="212" y1="{ky}" x2="256" y2="{ky}" stroke="{BLUE}" stroke-width="3.4"/>')
    b.append(f'<circle cx="234" cy="{ky}" r="7" fill="{BLUE}" stroke="white" stroke-width="2"/>')
    b.append(f'<text x="266" y="{ky + 5}" font-size="17" fill="{INK}" font-family="{FONT}">'
             f'OLMo-3-7B insecure-code organism — judges its own code duels, trains on what it keeps</text>')
    b.append(f'<line x1="212" y1="{ky + 26}" x2="256" y2="{ky + 26}" stroke="{GREEN}" '
             f'stroke-width="2.5" stroke-dasharray="7 5"/>')
    b.append(f'<text x="266" y="{ky + 31}" font-size="17" fill="{INK}" font-family="{FONT}">'
             f'frozen base co-generator — same-run reference severity on the matching task bank</text>')

    # --- column headers ---
    col1, col2 = 160, 760
    hy = 250
    b.append(centered(col1 + PW / 2, hy, "IN-DOMAIN prompts — the trained task bank", 18, INK, "bold"))
    b.append(centered(col2 + PW / 2, hy, "HELD-OUT prompts — never trained on", 18, INK, "bold"))

    # --- grid ---
    row1, row2 = 282, 662
    b.append(panel(col1, row1, is_left=True, **PANELS[("seed 71", "in_domain")]))
    b.append(panel(col2, row1, is_left=False, **PANELS[("seed 71", "heldout")]))
    b.append(panel(col1, row2, is_left=True, **PANELS[("seed 72", "in_domain")]))
    b.append(panel(col2, row2, is_left=False, **PANELS[("seed 72", "heldout")]))

    # --- rotated row (seed) labels + shared y-axis unit label ---
    for lbl, py in (("SEED 71", row1), ("SEED 72", row2)):
        yc = py + PH / 2
        b.append(f'<text x="46" y="{yc:.1f}" transform="rotate(-90 46 {yc:.1f})" '
                 f'text-anchor="middle" font-size="22" font-weight="bold" fill="{INK}" '
                 f'font-family="{FONT}">{lbl}</text>')
    ymid = (row1 + row2 + PH) / 2
    b.append(f'<text x="104" y="{ymid:.1f}" transform="rotate(-90 104 {ymid:.1f})" '
             f'text-anchor="middle" font-size="15" fill="{GRAY}" font-family="{FONT}">'
             f'blind manual code severity  (0 secure → 1 exploitable)</text>')

    # --- takeaway strip ---
    ty = row2 + PH + 58
    b.append(box(60, ty, W - 120, 96, KEY_FILL, GREEN, 2.5))
    t, _ = rich_text(80, ty + 30, [
        ("The blue line falls from a baseline of 0.74-0.86 toward the green base line every time. ", INK, True),
        ("In-domain it lands on base (seed 71: +0.01) or below it (seed 72: -0.05); on held-out "
         "prompts it still erodes hard but keeps a residual gap (+0.18 / +0.15). Seed 72's in-domain "
         "endpoint is 23/24 reviewed (†); its full-bank bound remains below base. The organism does "
         "not just erode where it trained — it writes safer code on prompts it never saw.", INK, False),
    ], 16.5, 132)
    b.append(t)

    # --- Qwen twin footnote ---
    fy = ty + 118
    b.append(box(60, fy, W - 120, 86, DOC_FILL, GRAY, 2))
    t, _ = rich_text(80, fy + 28, [
        ("Qwen twin, same condition (self-judge duel loop, base co-generator): ", GRAY, True),
        ("the Qwen insecure-code organism's forced-choice self-report of writing insecure code "
         "eroded from 0.10 to 0.006 (seed 41) and 0.06 to 0.007 (seed 42). Same mechanism, "
         "different channel — Qwen erodes what it SAYS about its code; OLMo erodes what it WRITES.",
         GRAY, False),
    ], 15.5, 150)
    b.append(t)

    # --- source line ---
    b.append(f'<text x="60" y="{fy + 112}" font-size="13" fill="{GRAY}" font-family="{FONT}">'
             f'Source: experiments/olmo_insecure/output/olmo_code_security_duel_loop_v2_analysis.json '
             f'(report: docs/report_olmo_code_security_duel_loop.md) · Qwen twin: '
             f'experiments/em_selfaware_loop/output/head2head_selfjudge.json</text>')

    return svg_doc(W, H, "\n".join(b))


if __name__ == "__main__":
    import os
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "olmo-code-security-erosion.svg")
    with open(out, "w") as f:
        f.write(build())
    print("wrote", out)
