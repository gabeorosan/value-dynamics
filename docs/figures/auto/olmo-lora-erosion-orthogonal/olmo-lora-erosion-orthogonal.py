#!/usr/bin/env python3
"""OLMo-3-7B self-judge code-security erosion, seen in WEIGHT SPACE.

Finding: the self-judge loop update does NOT walk back along the installed
insecure-code (dose-500) direction. It is almost entirely PERPENDICULAR to it,
with only a small, sign-consistent backward component. The behavior halves
while the installed direction stays largely present in the weights.

Every number below is a LoRA-adapter update delta (rank-32, all-linear),
verified against the result file:
  experiments/olmo_insecure/output/olmo_lora_direction.json
    Q4_erosion_vs_dose500_direction[<checkpoint>]
      { loop_update_norm, proj_loop_update_on_dose500_unit,
        cos_loop_update_vs_dose500, cos_total_vs_dose500 }
    adapters.dose500.delta_norm  (the installed-axis norm, 17.54)
  report: docs/report_olmo_lora_direction.md
Companion behavioral figure (severity 0.77 -> 0.48 in-domain):
  docs/figures/auto/olmo-code-security-erosion/

House style copied (not imported) from docs/figures/src/make_figures.py.
Regenerate:  python3 olmo-lora-erosion-orthogonal.py   (stdlib only)
"""

import math

# ---- palette / style, verbatim from make_figures.py -----------------
INK = "#1a1a1a"
BLUE = "#2867b5"       # self-judge loop update / perpendicular (orthogonal) motion
GREEN = "#3a7d44"      # (unused here, kept for palette parity)
RED = "#b5342c"        # reversal emphasis: the small backward-along-axis component
GRAY = "#6b7684"       # recessive only (axes, guides, muted captions) — never a series
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


def arrow(x1, y1, x2, y2, sw=4, color=INK, marker="arr"):
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{sw}" marker-end="url(#{marker})"/>')


DEFS = f'''<defs>
<marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6"
 orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="{INK}"/></marker>
<marker id="arrB" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6.6" markerHeight="6.6"
 orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="{BLUE}"/></marker>
<marker id="arrR" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7.4" markerHeight="7.4"
 orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="{RED}"/></marker>
<marker id="arrG" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6"
 orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="{GRAY}"/></marker>
</defs>'''


def svg_doc(w, h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
            f'font-family="{FONT}">\n<rect width="{w}" height="{h}" fill="white"/>\n'
            f'{DEFS}\n{body}\n</svg>')


# ==================================================================
# DATA — verified from olmo_lora_direction.json (Q4 block)
# ==================================================================
DOSE_NORM = 17.54167312349178          # adapters.dose500.delta_norm (installed axis)

# per-checkpoint: (loop_update_norm, proj_loop_update_on_dose500_unit, cos_total_vs_dose500)
Q4 = {
    ("s71", 1): (4.3098540371380825, -0.5009812651869233, 0.9698678220143981),
    ("s71", 2): (5.845049933992976,  -0.5063353410431118, 0.9462456288307618),
    ("s71", 3): (6.690569902972028,  -0.5372651835718125, 0.9309626277261221),
    ("s72", 1): (4.411976781436234,  -0.5080315190899445, 0.9684579483252606),
    ("s72", 2): (6.076225737892325,  -0.5665467602425016, 0.9419664925631275),
    ("s72", 3): (7.05703025826403,   -0.5514512612177426, 0.9239204564535202),
}


def perp(norm, proj):
    """Magnitude of the loop update perpendicular to the dose-500 axis."""
    return math.sqrt(max(norm * norm - proj * proj, 0.0))


W, H = 1300, 945


# ==================================================================
# LEFT PANEL — vector decomposition for a representative round
# ==================================================================
def left_panel():
    s = []
    # representative checkpoint: seed 71, round 3 (largest loop update -> clearest)
    norm, proj, cos_tot = Q4[("s71", 3)]
    perp_mag = perp(norm, proj)                      # ~6.67
    angle = math.degrees(math.acos(proj / norm))     # ~94.6 deg
    perp_frac = perp_mag / norm                       # ~0.997

    OX, OY = 150, 636          # origin of the decomposition
    SCALE = 18.2               # px per unit of LoRA delta norm
    TX = OX + DOSE_NORM * SCALE            # tip of the installed dose-500 axis (~469)
    TY = OY
    LX = TX + proj * SCALE                 # loop-update tip x (proj<0 -> a hair left)
    LY = OY - perp_mag * SCALE             # loop-update tip y (up)

    # panel title
    s.append(centered(360, 250,
        "One round in weight space: decompose the loop update", 20, INK, "bold"))
    s.append(centered(360, 274,
        "representative checkpoint — seed 71, round 3", 15.5, GRAY))

    # dashed continuation of the installed axis past the tip (so the ~right angle reads)
    s.append(f'<line x1="{OX}" y1="{OY}" x2="{TX + 30:.1f}" y2="{OY}" '
             f'stroke="{GRAY}" stroke-width="1.4" stroke-dasharray="5 5"/>')

    # installed dose-500 axis (INK, thick)
    s.append(arrow(OX, OY, TX, TY, sw=6, color=INK, marker="arr"))
    s.append(f'<circle cx="{OX}" cy="{OY}" r="5.5" fill="{INK}"/>')

    # loop update itself (vector sum) — dashed, nearly coincident with the blue leg
    s.append(f'<line x1="{TX:.1f}" y1="{TY:.1f}" x2="{LX:.1f}" y2="{LY:.1f}" '
             f'stroke="{INK}" stroke-width="1.6" stroke-dasharray="4 4"/>')
    # perpendicular component (BLUE, dominant) — from dose tip straight up
    s.append(arrow(TX, TY, TX, LY, sw=5.5, color=BLUE, marker="arrB"))
    # backward component (RED, tiny) — from top of perp leg to the loop tip.
    # Drawn to scale (only ~10 px): thin, so it reads as the small nub it is.
    s.append(arrow(TX, LY, LX, LY, sw=3, color=RED, marker="arrR"))

    # right-angle marker at the dose tip (between axis and perpendicular leg)
    s.append(f'<path d="M {TX-14:.1f} {TY:.1f} L {TX-14:.1f} {TY-14:.1f} '
             f'L {TX:.1f} {TY-14:.1f}" fill="none" stroke="{INK}" stroke-width="1.6"/>')
    # angle callout (true angle is ~95 deg, so the square is "approximately" a right angle)
    s.append(f'<text x="{TX+30:.1f}" y="{OY-3:.1f}" font-size="15" font-weight="bold" '
             f'fill="{INK}" font-family="{FONT}">&#8776;{angle:.0f}&#176;</text>')

    # installed-axis label (centered below the axis)
    s.append(centered((OX + TX) / 2, OY + 34, "installed insecure-code direction", 15.5, INK, "bold"))
    s.append(centered((OX + TX) / 2, OY + 55, "(dose-500 LoRA delta) — norm 17.5", 15, INK))
    s.append(centered((OX + TX) / 2, OY + 80,
        "the loop update (norm 6.7) = perpendicular (blue) + backward (red)", 13.5, GRAY))

    # perpendicular-leg label (BLUE), to the right of the leg
    midY = (TY + LY) / 2
    s.append(f'<text x="{TX+22:.1f}" y="{midY-8:.1f}" font-size="16.5" font-weight="bold" '
             f'fill="{BLUE}" font-family="{FONT}">&#8776;6.7 perpendicular</text>')
    s.append(f'<text x="{TX+22:.1f}" y="{midY+14:.1f}" font-size="15" '
             f'fill="{BLUE}" font-family="{FONT}">to the installed axis</text>')
    s.append(f'<text x="{TX+22:.1f}" y="{midY+38:.1f}" font-size="14" '
             f'fill="{BLUE}" font-family="{FONT}">= {perp_frac*100:.1f}% of the loop update</text>')

    # backward-component leader + label (RED), placed above-left of the tip
    s.append(f'<line x1="{LX:.1f}" y1="{LY:.1f}" x2="405" y2="490" '
             f'stroke="{RED}" stroke-width="1.3" stroke-dasharray="3 3"/>')
    s.append(f'<text x="140" y="482" font-size="16" font-weight="bold" '
             f'fill="{RED}" font-family="{FONT}">&#8722;0.5 backward along the axis</text>')
    s.append(f'<text x="140" y="504" font-size="14" '
             f'fill="{RED}" font-family="{FONT}">the only walk-back — &#8776;3% of the 17.5 norm</text>')

    return "\n".join(s)


# ==================================================================
# RIGHT PANEL — the two components across rounds, both seeds
# ==================================================================
PX, PY, PW, PH = 800, 300, 430, 300
INSET = 40
YMAX, YMIN = 8.0, -1.6


def RY(v):
    return PY + PH * (YMAX - v) / (YMAX - YMIN)


def RX(i):   # round index 0,1,2 -> rounds 1,2,3
    return PX + INSET + (PW - 2 * INSET) * i / 2.0


def right_panel():
    s = []
    s.append(centered(PX + PW / 2, 250,
        "Perpendicular part grows; backward part stays flat", 19, INK, "bold"))
    s.append(centered(PX + PW / 2, 274,
        "both self-judge seeds, rounds 1–3", 15.5, GRAY))

    # gridlines + y ticks
    for v in (-1, 0, 2, 4, 6, 8):
        yy = RY(v)
        zero = (v == 0)
        s.append(f'<line x1="{PX+INSET-10:.1f}" y1="{yy:.1f}" x2="{PX+PW-INSET+10:.1f}" '
                 f'y2="{yy:.1f}" stroke="{"#c9ccd1" if zero else "#e6e6e2"}" '
                 f'stroke-width="{1.6 if zero else 1}"/>')
        s.append(f'<text x="{PX+INSET-18:.1f}" y="{yy+5:.1f}" text-anchor="end" '
                 f'font-size="14.5" fill="{GRAY}" font-family="{FONT}">{v}</text>')

    # x ticks
    for i, lbl in enumerate(("round 1", "round 2", "round 3")):
        s.append(f'<text x="{RX(i):.1f}" y="{PY+PH+30:.1f}" text-anchor="middle" '
                 f'font-size="16" fill="{INK}" font-family="{FONT}">{lbl}</text>')

    # y-axis unit label
    yc = PY + PH / 2
    s.append(f'<text x="{PX-52:.1f}" y="{yc:.1f}" transform="rotate(-90 {PX-52:.1f} {yc:.1f})" '
             f'text-anchor="middle" font-size="14.5" fill="{GRAY}" font-family="{FONT}">'
             f'component magnitude  (units of LoRA delta norm)</text>')

    def series(seed, dash, color, valfn, marker_fill):
        pts = []
        for i, rd in enumerate((1, 2, 3)):
            norm, proj, _ = Q4[(seed, rd)]
            pts.append((RX(i), RY(valfn(norm, proj))))
        poly = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
        da = ' stroke-dasharray="8 5"' if dash else ""
        out = [f'<polyline points="{poly}" fill="none" stroke="{color}" '
               f'stroke-width="3.4"{da}/>']
        for x, y in pts:
            out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="6" fill="{marker_fill}" '
                       f'stroke="white" stroke-width="2"/>')
        return "\n".join(out), pts

    # perpendicular (BLUE): seed 71 solid, seed 72 dashed
    p71, pts71 = series("s71", False, BLUE, perp, BLUE)
    p72, pts72 = series("s72", True, BLUE, perp, BLUE)
    # backward-along-axis (RED): proj is negative
    b71, bts71 = series("s71", False, RED, lambda n, p: p, RED)
    b72, bts72 = series("s72", True, RED, lambda n, p: p, RED)
    s.extend([p71, p72, b71, b72])

    # endpoint value labels (round 3)
    _, proj71_3, _ = Q4[("s71", 3)]; _, proj72_3, _ = Q4[("s72", 3)]
    s.append(f'<text x="{pts71[2][0]+12:.1f}" y="{pts71[2][1]+2:.1f}" font-size="15.5" '
             f'font-weight="bold" fill="{BLUE}" font-family="{FONT}">{perp(*Q4[("s71",3)][:2]):.1f}</text>')
    s.append(f'<text x="{pts72[2][0]+12:.1f}" y="{pts72[2][1]-8:.1f}" font-size="15.5" '
             f'font-weight="bold" fill="{BLUE}" font-family="{FONT}">{perp(*Q4[("s72",3)][:2]):.1f}</text>')
    s.append(f'<text x="{bts71[2][0]+12:.1f}" y="{bts71[2][1]+6:.1f}" font-size="15.5" '
             f'font-weight="bold" fill="{RED}" font-family="{FONT}">&#8722;0.5</text>')

    # in-plot annotations
    s.append(f'<text x="{RX(0.05):.1f}" y="{RY(5.9):.1f}" font-size="15" font-weight="bold" '
             f'fill="{BLUE}" font-family="{FONT}">grows 4.3 &#8594; 7.0</text>')
    s.append(f'<text x="{RX(0.05):.1f}" y="{RY(-1.05):.1f}" font-size="14.5" font-weight="bold" '
             f'fill="{RED}" font-family="{FONT}">pinned near &#8722;0.5 every round</text>')

    return "\n".join(s)


def legend(y):
    s = []
    x = 700
    s.append(f'<line x1="{x}" y1="{y}" x2="{x+40}" y2="{y}" stroke="{BLUE}" stroke-width="3.4"/>')
    s.append(f'<circle cx="{x+20}" cy="{y}" r="6" fill="{BLUE}" stroke="white" stroke-width="2"/>')
    s.append(f'<text x="{x+50}" y="{y+5}" font-size="14.5" fill="{INK}" font-family="{FONT}">'
             f'perpendicular part of the loop update (orthogonal to the installed axis)</text>')
    y2 = y + 25
    s.append(f'<line x1="{x}" y1="{y2}" x2="{x+40}" y2="{y2}" stroke="{RED}" stroke-width="3.4"/>')
    s.append(f'<circle cx="{x+20}" cy="{y2}" r="6" fill="{RED}" stroke="white" stroke-width="2"/>')
    s.append(f'<text x="{x+50}" y="{y2+5}" font-size="14.5" fill="{INK}" font-family="{FONT}">'
             f'backward part along the installed axis (the only walk-back)</text>')
    y3 = y2 + 25
    s.append(f'<line x1="{x}" y1="{y3}" x2="{x+40}" y2="{y3}" stroke="{GRAY}" stroke-width="3"/>')
    s.append(f'<line x1="{x+60}" y1="{y3}" x2="{x+100}" y2="{y3}" stroke="{GRAY}" '
             f'stroke-width="3" stroke-dasharray="8 5"/>')
    s.append(f'<text x="{x+110}" y="{y3+5}" font-size="14.5" fill="{GRAY}" font-family="{FONT}">'
             f'solid = seed 71   ·   dashed = seed 72</text>')
    return "\n".join(s)


def build():
    b = []
    # headline
    b.append(centered(W / 2, 50,
        "Self-judging doesn't unlearn the installed direction — it steers around it",
        29, INK, "bold"))
    b.append(centered(W / 2, 88,
        "OLMo-3-7B's code-security erosion is ≈99% orthogonal to the insecure-code axis in weight space",
        24, RED, "bold"))
    sub = ("Each quantity is a LoRA-adapter update delta (rank-32, all-linear). "
           "loop_update = the duel-checkpoint delta minus the dose-500 delta (the installed "
           "insecure-code axis, norm 17.5). Along-axis component = projection onto the dose-500 "
           "unit vector; perpendicular = the remaining magnitude. Cosine to the dose-500 axis "
           "measures how much of the installed direction survives.")
    for i, ln in enumerate(wrap(sub, 132)):
        b.append(centered(W / 2, 120 + i * 22, ln, 15.5, GRAY))

    # panels
    b.append(left_panel())
    b.append(right_panel())
    b.append(legend(650))

    # takeaway strip
    ty = 720
    b.append(box(60, ty, W - 120, 160, KEY_FILL, GREEN, 2.5))
    t, _ = rich_text(84, ty + 32, [
        ("A large behavioral change carried by an almost-orthogonal weight update. ", INK, True),
        ("Over three self-judge rounds the loop update grows to a norm of 4–7, but only about "
         "−0.5 of it — roughly 3% of the 17.5 installed-axis norm — points backward along the "
         "insecure-code direction; the other ≈99% is perpendicular (cosine ≈ −0.1 in all 6 "
         "checkpoints, both seeds). The full checkpoint stays 0.93–0.97 cosine-aligned with the "
         "installed axis even as blind manual code severity falls 0.77 → 0.48 in-domain (companion "
         "figure, olmo-code-security-erosion). The organism does not delete the value from weight "
         "space — it overlays a mostly-orthogonal correction that steers the outputs around it.",
         INK, False),
    ], 16, 132)
    b.append(t)

    # source line (two lines to avoid right-edge overflow)
    b.append(f'<text x="60" y="{ty + 186}" font-size="12.5" fill="{GRAY}" font-family="{FONT}">'
             f'Source: experiments/olmo_insecure/output/olmo_lora_direction.json '
             f'(Q4_erosion_vs_dose500_direction) · report: docs/report_olmo_lora_direction.md</text>')
    b.append(f'<text x="60" y="{ty + 204}" font-size="12.5" fill="{GRAY}" font-family="{FONT}">'
             f'Behavioral companion figure: docs/figures/auto/olmo-code-security-erosion/</text>')

    return svg_doc(W, H, "\n".join(b))


if __name__ == "__main__":
    import os
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "olmo-lora-erosion-orthogonal.svg")
    with open(out, "w") as f:
        f.write(build())
    print("wrote", out)
