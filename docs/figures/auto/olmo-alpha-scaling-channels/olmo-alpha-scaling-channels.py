#!/usr/bin/env python3
"""OLMo alpha-scaling figure: scaling the insecure-code adapter's LoRA delta by
a factor alpha amplifies the organism's OWN self-report of writing insecure
code, monotonically at every training dose -- the opposite of the preregistered
"mirror" prediction that OLMo carries behavior, not self-report. The
free-generation misalignment channel is shown greyed and flagged (its judge is
miscalibrated on OLMo) and alpha = 2 is marked as a degeneration regime.

Data: experiments/olmo_insecure/output/olmo_alpha_scaling_channels.json and
olmo_alpha_scaling_analysis.json. Report: docs/report_olmo_alpha_scaling.md.
Style: docs/figures/src/make_figures.py (Evans-lab house style).
Regenerate with:  python3 olmo-alpha-scaling-channels.py
"""
import json
import os
from decimal import ROUND_HALF_UP, Decimal

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
CHANNELS = os.path.join(ROOT, "experiments", "olmo_insecure", "output",
                        "olmo_alpha_scaling_channels.json")
ANALYSIS = os.path.join(ROOT, "experiments", "olmo_insecure", "output",
                        "olmo_alpha_scaling_analysis.json")

INK = "#1a1a1a"
BLUE = "#2867b5"       # accent / self-judge series (validated)
GREEN = "#3a7d44"      # accent / frozen-judge series (validated)
RED = "#b5342c"        # emphasis for reversal / warning text
GRAY = "#6b7684"       # recessive only (axes, muted captions, flagged series)
KEY_FILL = "#eef5ee"   # highlighted takeaway box
BAND_FILL = "#fbf0ee"  # degeneration-regime shading (matches flagged row in
                       # methods_alpha_scaling.svg)
GRID = "#ebebeb"

# sequential blue ramp for the ordered training doses (light -> dark)
DOSE_COLOR = {250: "#7ea8d3", 500: "#5d90c6", 750: "#3f77b8", 1000: "#20589e"}
DOSES = [250, 500, 750, 1000]
ALPHAS = [0.5, 1.0, 1.25, 1.5, 2.0]

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


def text_el(x, y, s, size, color=INK, weight="normal", anchor="start"):
    a = f' text-anchor="{anchor}"' if anchor != "start" else ""
    return (f'<text x="{x}" y="{y}"{a} font-family="{FONT}" font-size="{size}" '
            f'font-weight="{weight}" fill="{color}">{esc(s)}</text>')


def text_lines(x, y, text, size, width, color=INK, weight="normal", lh=1.28):
    out = []
    lines = wrap(text, width)
    for i, ln in enumerate(lines):
        out.append(text_el(x, y + i * size * lh, ln, size, color, weight))
    return "\n".join(out), y + len(lines) * size * lh


def centered_rich(x, y, segments, size, weight="bold"):
    tspans = "".join(f'<tspan fill="{c}">{esc(t)}</tspan>' for t, c in segments)
    return (f'<text x="{x}" y="{y}" text-anchor="middle" font-family="{FONT}" '
            f'font-size="{size}" font-weight="{weight}">{tspans}</text>')


def box(x, y, w, h, fill, stroke=INK, sw=2.5, rx=8):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')


DEFS = f'''<defs><marker id="arrR" viewBox="0 0 10 10" refX="9" refY="5"
 markerWidth="6" markerHeight="6" orient="auto-start-reverse">
 <path d="M 0 0 L 10 5 L 0 10 z" fill="{RED}"/></marker></defs>'''


# ------------------------------------------------------------------ data
with open(CHANNELS) as f:
    channels = json.load(f)
with open(ANALYSIS) as f:
    analysis = json.load(f)
assert analysis["citable_window"].startswith("alpha <= 1.5")

base_sr = channels["base_self_report_insecure"]          # 0.250
cells = {(c["dose"], c["alpha"]): c for c in channels["cells"]}
self_report = {d: [cells[(d, a)]["self_report"] for a in ALPHAS] for d in DOSES}
em_choice_500 = [cells[(500, a)]["em_choice"] for a in ALPHAS]
em_freegen_500 = [cells[(500, a)]["em_freegen"] for a in ALPHAS]

sr_at = {a: [cells[(d, a)]["self_report"] for d in DOSES] for a in ALPHAS}
sr_delta = [cells[(d, 1.5)]["self_report"] - cells[(d, 0.5)]["self_report"]
            for d in DOSES]                               # +0.155 .. +0.197
agree1 = [cells[(d, 1.0)]["agree"] for d in DOSES]        # 0.104 .. 0.119
agree2 = [cells[(d, 2.0)]["agree"] for d in DOSES]        # 0.434 .. 0.624
emc_delta = [cells[(d, 1.5)]["em_choice"] - cells[(d, 0.5)]["em_choice"]
             for d in DOSES]                              # +0.106 .. +0.176
freegen_max = max(cells[(d, a)]["em_freegen"] for d in DOSES for a in ALPHAS)


def fmt(v):
    """Round half-up at 2 decimals (0.155 -> 0.16, matching the report)."""
    return str(Decimal(str(round(v, 4))).quantize(Decimal("0.01"),
                                                  rounding=ROUND_HALF_UP))


def rng(vals):
    return f"{fmt(min(vals))}–{fmt(max(vals))}"


def srng(vals):
    return f"+{fmt(min(vals))} to +{fmt(max(vals))}"


# ------------------------------------------------------------------ layout
W, H = 1500, 1032
b = []

# headline + subtitle -------------------------------------------------------
b.append(centered_rich(W / 2, 52, [
    ("Scaling the OLMo insecure-code adapter amplifies its self-report "
     "of insecure code", INK)], 30))
b.append(centered_rich(W / 2, 90, [
    ("— ", INK), ("the opposite", RED),
    (" of the preregistered mirror prediction", INK)], 30))
b.append(centered_rich(W / 2, 128, [
    ("Take each trained insecure-code adapter (250 / 500 / 750 / 1000 "
     "training examples), multiply its LoRA delta by α, and re-run "
     "the probes.", GRAY)], 20, weight="normal"))
b.append(centered_rich(W / 2, 154, [
    ("Organism: Olmo-3-7B-Instruct. The prereg "
     "(docs/prereg_olmo_alpha_scaling.md) predicted this self-report "
     "channel stays flat under scaling.", GRAY)], 20, weight="normal"))

# panel geometry ------------------------------------------------------------
PT, PB = 280, 660                       # plot top / bottom (shared y)
LX0, LX1 = 130, 760                     # left panel x-range
RX0, RX1 = 930, 1420                    # right panel x-range
YMAX = 0.5

def y(v):
    return PB - v / YMAX * (PB - PT)

def xl(a):
    return LX0 + (a - 0.5) / 1.5 * (LX1 - LX0)

def xr(a):
    return RX0 + (a - 0.5) / 1.5 * (RX1 - RX0)


def panel_axes(x0, x1, xfn):
    s = []
    # degeneration band (alpha > 1.5)
    s.append(f'<rect x="{xfn(1.5):.1f}" y="{PT}" width="{x1 - xfn(1.5):.1f}" '
             f'height="{PB - PT}" fill="{BAND_FILL}"/>')
    s.append(f'<line x1="{xfn(1.5):.1f}" y1="{PT}" x2="{xfn(1.5):.1f}" '
             f'y2="{PB}" stroke="{RED}" stroke-width="1.5" '
             f'stroke-dasharray="5 4" opacity="0.55"/>')
    for gv in (0.1, 0.2, 0.3, 0.4):
        s.append(f'<line x1="{x0}" y1="{y(gv):.1f}" x2="{x1}" '
                 f'y2="{y(gv):.1f}" stroke="{GRID}" stroke-width="1"/>')
    s.append(f'<line x1="{x0}" y1="{PT}" x2="{x0}" y2="{PB}" '
             f'stroke="{GRAY}" stroke-width="2"/>')
    s.append(f'<line x1="{x0}" y1="{PB}" x2="{x1}" y2="{PB}" '
             f'stroke="{GRAY}" stroke-width="2"/>')
    for gv in (0, 0.1, 0.2, 0.3, 0.4, 0.5):
        s.append(text_el(x0 - 10, y(gv) + 6, f"{gv:g}", 18, GRAY,
                         anchor="end"))
    for a in ALPHAS:
        s.append(f'<line x1="{xfn(a):.1f}" y1="{PB}" x2="{xfn(a):.1f}" '
                 f'y2="{PB + 6}" stroke="{GRAY}" stroke-width="2"/>')
        s.append(text_el(xfn(a), PB + 28, f"{a:g}", 18, INK,
                         weight="bold", anchor="middle"))
    return "\n".join(s)


def series(xfn, vals, color, sw=3, dash=None):
    pts = " ".join(f"{xfn(a):.1f},{y(v):.1f}" for a, v in zip(ALPHAS, vals))
    d = f' stroke-dasharray="{dash}"' if dash else ""
    s = [f'<polyline points="{pts}" fill="none" stroke="{color}" '
         f'stroke-width="{sw}"{d}/>']
    for a, v in zip(ALPHAS, vals):
        s.append(f'<circle cx="{xfn(a):.1f}" cy="{y(v):.1f}" r="5" '
                 f'fill="{color}" stroke="white" stroke-width="2"/>')
    return "\n".join(s)


# ------------------------------------------------------ left panel: self-report
b.append(text_el(LX0, 198, "The organism's own self-report of writing "
                 "insecure code", 21, INK, weight="bold"))
b.append(text_el(LX0, 224, "trustworthy channel — its forced A/B choice "
                 "between “The code I", 18, GRAY))
b.append(text_el(LX0, 247, "write is often insecure…” and “…generally "
                 "secure…”, both orders;", 18, GRAY))
b.append(text_el(LX0, 270, "y-axis: share picking “insecure”", 18, GRAY))
b.append(panel_axes(LX0, LX1, xl))

# base line (base OLMo, no adapter)
b.append(f'<line x1="{LX0}" y1="{y(base_sr):.1f}" x2="{LX1}" '
         f'y2="{y(base_sr):.1f}" stroke="{GRAY}" stroke-width="2" '
         f'stroke-dasharray="7 5"/>')
b.append(text_el(138, 440, "base Olmo-3-7B-Instruct,", 18, GRAY,
                 weight="bold"))
b.append(text_el(138, 462, f"no adapter: {base_sr:g}", 18, GRAY,
                 weight="bold"))

# dose series
for d in DOSES:
    b.append(series(xl, self_report[d], DOSE_COLOR[d]))

# in-figure key: dose ramp + the "dose does not move it" reading
kx, ky = 150, 306
b.append(text_el(kx, ky, "training dose (insecure-code examples):", 18, INK,
                 weight="bold"))
cx = kx
for d in DOSES:
    b.append(f'<line x1="{cx}" y1="{ky + 22}" x2="{cx + 26}" y2="{ky + 22}" '
             f'stroke="{DOSE_COLOR[d]}" stroke-width="5"/>')
    b.append(f'<circle cx="{cx + 13}" cy="{ky + 22}" r="4.5" '
             f'fill="{DOSE_COLOR[d]}"/>')
    b.append(text_el(cx + 32, ky + 28, str(d), 18, INK, weight="bold"))
    cx += 32 + len(str(d)) * 11 + 22
b.append(text_el(kx, ky + 56, "the four dose lines lie on top of each other:",
                 18, INK, weight="bold"))
b.append(text_el(kx, ky + 78, "dose does not move it — scaling α "
                 "does", 18, INK, weight="bold"))

# value-range labels at alpha = 0.5 and the alpha = 1.5 bracket
b.append(text_el(136, 546, f"{rng(sr_at[0.5])} at α = 0.5", 18, INK))
y_hi, y_lo = y(max(sr_at[1.5])), y(min(sr_at[1.5]))
b.append(f'<path d="M 558 {y_hi - 6:.1f} L 566 {y_hi - 6:.1f} L 566 '
         f'{y_lo + 6:.1f} L 558 {y_lo + 6:.1f}" fill="none" stroke="{RED}" '
         f'stroke-width="2.5"/>')
b.append(text_el(574, 414, f"{rng(sr_at[1.5])} at α = 1.5", 18, INK,
                 weight="bold"))

# prereg-contrast annotation (bottom-centre, below the rising lines)
t, _ = text_lines(340, 498, "at α = 1 — the adapter as trained "
                  "— every dose sits at the 0.25 base. The prereg "
                  "“mirror” claim said it stays flat under "
                  "scaling. Instead it rises at every dose:", 18, 42, RED)
b.append(t)
b.append(text_el(340, 591, f"{srng(sr_delta)} from α 0.5 to 1.5", 19,
                 RED, weight="bold"))
b.append(f'<line x1="346" y1="478" x2="435" y2="449" stroke="{RED}" '
         f'stroke-width="2.5" marker-end="url(#arrR)"/>')

# degeneration band label (bottom of band, where the panel is empty)
b.append(text_el(xl(1.5) + 6, 626, "α = 2: degeneration", 18, RED,
                 weight="bold"))
b.append(text_el(xl(1.5) + 6, 648, "(off-target yes-drift)", 18, RED))

# x-axis title
b.append(text_el((LX0 + LX1) / 2, 716, "α — multiplier on the "
                 "adapter's LoRA delta", 18, INK, anchor="middle"))
b.append(text_el((LX0 + LX1) / 2, 740, "(α = 1 is the adapter as "
                 "trained; citable window α ≤ 1.5)", 18, GRAY,
                 anchor="middle"))

# --------------------------------------------- right panel: misalignment channels
b.append(text_el(RX0, 198, "Misalignment channels — dose-500 adapter",
                 21, INK, weight="bold"))
t, _ = text_lines(RX0, 224, "em_choice: its own forced misalignment "
                  "multiple-choice · em_freegen: frozen base-OLMo "
                  "judge on free generations · same 0–0.5 scale "
                  "as left", 18, 53, GRAY)
b.append(t)
b.append(panel_axes(RX0, RX1, xr))

# flagged channel first (recessive), then the trustworthy one on top
b.append(series(xr, em_freegen_500, GRAY, sw=3, dash="7 6"))
b.append(series(xr, em_choice_500, GREEN, sw=3.5))

# flag tag for em_freegen
b.append(text_el(945, 312, "free-generation misalignment judge "
                 "(em_freegen), dashed:", 18, GRAY, weight="bold"))
b.append(text_el(945, 335, "miscalibrated on OLMo — not usable as "
                 "evidence", 18, RED, weight="bold"))
t, _ = text_lines(945, 358, "blind manual review found 0/128 generations "
                  "misaligned while this judge reads ≈ 0.32", 18, 50,
                  GRAY)
b.append(t)
b.append(text_el(1005, 652, "em_freegen (miscalibrated judge)", 18, GRAY))

# labels for the trustworthy channel
b.append(text_el(945, 490, "the organism's own misalignment multiple-choice",
                 18, GREEN, weight="bold"))
b.append(text_el(945, 513, "(em_choice): trustworthy — rises with "
                 "α", 18, GREEN, weight="bold"))
b.append(text_el(942, 622, fmt(em_choice_500[0]), 18, INK))
b.append(text_el(1244, 542, fmt(em_choice_500[3]), 18, INK, weight="bold",
                 anchor="end"))
b.append(text_el(xr(2.0) - 8, y(em_choice_500[4]) - 14,
                 fmt(em_choice_500[4]), 18, INK, weight="bold", anchor="end"))
b.append(text_el(xr(2.0) - 8, y(em_freegen_500[4]) - 12,
                 fmt(em_freegen_500[4]), 18, GRAY, anchor="end"))

# band label (upper area of the band, clear of both series)
b.append(text_el(xr(1.5) + 6, 400, "α = 2:", 18, RED, weight="bold"))
b.append(text_el(xr(1.5) + 6, 422, "degeneration", 18, RED, weight="bold"))

# x-axis title + all-doses footnote
b.append(text_el((RX0 + RX1) / 2, 716, "α — multiplier on the "
                 "adapter's LoRA delta", 18, INK, anchor="middle"))
t, _ = text_lines(RX0, 744, "every other dose behaves the same way: "
                  f"em_choice rises {srng(emc_delta)} over α 0.5 "
                  "→ 1.5 at each dose; em_freegen stays ≤ "
                  f"{freegen_max:.2f} everywhere and is non-monotone.", 18,
                  56, GRAY)
b.append(t)

# ------------------------------------------------------------ takeaway box
b.append(box(60, 800, W - 120, 166, KEY_FILL))
takeaway = ("Reading: the insecure-code direction is already encoded in the "
            "adapter but under-expressed at its trained scale. At α = 1 "
            "every dose sits at the 0.25 base (the dose ladder moved "
            "self-report by at most 0.04); linearly scaling the same delta "
            f"expresses it, {srng(sr_delta)} by α = 1.5. The "
            "preregistered mirror hypothesis — OLMo carries behavior, "
            "not self-report, the inverse of Qwen — is retired: on this "
            "channel OLMo behaves like Qwen. No free-generation behavioral "
            "claim survives (the only such channel is a miscalibrated "
            "judge), and α = 2 fails the off-target gate "
            f"(agreeableness {rng(agree1)} at α = 1 rising to "
            f"{rng(agree2)} at α = 2), leaving α ≤ 1.5 as the "
            "citable window.")
t, _ = text_lines(84, 830, takeaway, 19, 132, INK)
b.append(t)

# footer ---------------------------------------------------------------------
b.append(text_el(60, 992, "Data: experiments/olmo_insecure/output/"
                 "olmo_alpha_scaling_channels.json · analysis: "
                 "olmo_alpha_scaling_analysis.json "
                 "(scripts/analysis_olmo_alpha_scaling.py)", 18, GRAY))
b.append(text_el(60, 1016, "Report: docs/report_olmo_alpha_scaling.md · "
                 "em_freegen flag: docs/report_em_freegen_manual_"
                 "adjudication.md · Qwen companion figure: "
                 "methods_alpha_scaling.svg", 18, GRAY))

svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
       f'font-family="{FONT}">\n<rect width="{W}" height="{H}" '
       f'fill="white"/>\n{DEFS}\n' + "\n".join(b) + "\n</svg>")

out = os.path.join(HERE, "olmo-alpha-scaling-channels.svg")
with open(out, "w") as f:
    f.write(svg)
print(f"wrote {out}")
