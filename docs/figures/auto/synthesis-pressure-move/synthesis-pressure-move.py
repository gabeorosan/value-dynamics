#!/usr/bin/env python3
"""Synthesis candidate C — one number from the first round calls the whole run.

A single scatter that reduces every committed run to the parameter-free
model's round-1 quantity (x) and the run's observed net movement (y).

  x = (round-1 pool mean + rho * round-1 spread) - round-1 value
      = the model's predicted first-round pull (signed)
  y = (final value) - (round-1 value)
      = the run's observed net movement over all rounds
      where final value = last round's value + that round's drift

One dot per run. Color by experiment family (the five families in the
writeup run table). Runs with a null round-1 rho are skipped. Schedule
judge-swap runs (the judge changes mid-run, so a first-round number cannot
call the endpoint) are drawn hollow and excluded from the evidence tally.

Source data: experiments/spread_util_unified.json  (field `records`).
Regenerate:  python3 synthesis-pressure-move.py   (writes the .svg beside it).

Style reference: docs/figures/src/make_figures.py (Owain Evans-lab house style).
Stdlib only.
"""
import json
import os
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "..", "..", "..",
                    "experiments", "spread_util_unified.json")

# ---- palette (make_figures.py constants, extended for a 5-family scatter) ----
INK = "#1a1a1a"
BLUE = "#2867b5"       # Qwen risk grid
GREEN = "#3a7d44"      # OLMo risk grid + schedules
ORANGE = "#c9791a"     # OLMo mixed-pool interventions  (added, CVD-validated)
RED = "#b5342c"        # oracle & injection  (the strongest erosion arm)
PURPLE = "#6d4a9c"     # Qwen insecure-code loops        (added, CVD-validated)
GRAY = "#6b7684"       # recessive only: axes, grid, reference lines
FAINT = "#c8cdd4"
FONT = "Helvetica, Arial, sans-serif"

FAM = {
    "qrisk":  ("Qwen risk grid",                    BLUE),
    "orisk":  ("OLMo risk grid + schedules",        GREEN),
    "omix":   ("OLMo mixed-pool interventions",     ORANGE),
    "oracle": ("oracle & injection",                RED),
    "qcode":  ("Qwen insecure-code loops",          PURPLE),
}
FAM_ORDER = ["qrisk", "orisk", "omix", "oracle", "qcode"]


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


# --------------------------- load + reduce runs ------------------------------
def family(src, org, comp):
    if src.startswith("k1_qwen"):
        return "qrisk"
    if src in ("head2head_selfjudge.json", "selfaware_loop_grid.json",
               "judge_opposition_natural_base.json"):
        return "qcode"
    if src in ("judge_opposition_oracle.json",
               "judge_opposition_oracle_seed707.json",
               "mixed_reopen_qwen.json", "mixed_reopen_twin_selfonly.json",
               "k2rel_oracle_hold_s21.json", "k2rel_oracle_hold_s22.json",
               "k2rel_oracle_mix_s31.json", "k2rel_oracle_mix_s32.json"):
        return "oracle"
    if org == "OLMo" and comp == "self-only":
        return "orisk"
    if org == "OLMo":
        return "omix"
    return "qrisk"


def load_points():
    recs = json.load(open(DATA))["records"]
    g = defaultdict(list)
    for r in recs:
        key = (r.get("source"), r.get("organism"), r.get("axis"),
               r.get("cond"), r.get("seed"))
        g[key].append(r)
    pts = []
    for key, v in g.items():
        v = sorted(v, key=lambda z: z["round"])
        r1, last = v[0], v[-1]
        if r1["rho"] is None:          # skip null round-1 rho runs
            continue
        x = r1["pool_mean"] + r1["rho"] * r1["spread"] - r1["value"]
        y = (last["value"] + (last["drift"] or 0.0)) - r1["value"]
        swap = "schedule" in {z["judge"] for z in v}
        fam = family(key[0], key[1], r1["composition"])
        pts.append({"x": x, "y": y, "fam": fam, "swap": swap})
    return pts


# --------------------------------- render ------------------------------------
def build():
    pts = load_points()
    W, H = 1290, 966
    # plot box (square so the y = x diagonal reads at true 45 degrees)
    PL, PT, S = 172, 206, 616
    PR, PB = PL + S, PT + S
    DX = 0.9   # data half-range on both axes
    DY = 0.9

    def sx(x):
        return PL + (x + DX) / (2 * DX) * S

    def sy(y):
        return PB - (y + DY) / (2 * DY) * S

    body = []

    # headline + subtitle
    body.append(f'<text x="52" y="60" font-family="{FONT}" font-size="34" '
                f'font-weight="bold" fill="{INK}">One number from the first '
                f'round calls the whole run</text>')
    body.append(f'<text x="52" y="100" font-family="{FONT}" font-size="20" '
                f'fill="{INK}">Horizontal: the model&#8217;s predicted first-round '
                f'pull&#160;&#160;(round-1 pool mean&#160;+&#160;&#961;&#183;spread)'
                f'&#160;&#8722;&#160;round-1 value.</text>')
    body.append(f'<text x="52" y="126" font-family="{FONT}" font-size="20" '
                f'fill="{INK}">Vertical: the run&#8217;s observed net movement '
                f'(final value&#160;&#8722;&#160;round-1 value). One dot per run, '
                f'{len(pts)} runs.</text>')

    # ---- axes frame + zero lines ----
    body.append(f'<rect x="{PL}" y="{PT}" width="{S}" height="{S}" '
                f'fill="#fcfcfb" stroke="{FAINT}" stroke-width="1.5"/>')
    x0, y0 = sx(0), sy(0)
    body.append(f'<line x1="{x0}" y1="{PT}" x2="{x0}" y2="{PB}" '
                f'stroke="{GRAY}" stroke-width="1.4" stroke-dasharray="2 4"/>')
    body.append(f'<line x1="{PL}" y1="{y0}" x2="{PR}" y2="{y0}" '
                f'stroke="{GRAY}" stroke-width="1.4" stroke-dasharray="2 4"/>')

    # ---- y = x diagonal reference (label sits below the line, empty region) ----
    dlo, dhi = -DX, DX
    body.append(f'<line x1="{sx(dlo):.1f}" y1="{sy(dlo):.1f}" '
                f'x2="{sx(dhi):.1f}" y2="{sy(dhi):.1f}" stroke="{GRAY}" '
                f'stroke-width="2.2" stroke-dasharray="8 6"/>')
    lxr, lyr = sx(0.55), sy(0.55) + 26
    body.append(f'<text x="{lxr:.1f}" y="{lyr:.1f}" text-anchor="middle" '
                f'font-family="{FONT}" font-size="16" fill="{GRAY}" '
                f'transform="rotate(-45 {lxr:.1f} {lyr:.1f})">'
                f'y = x : one round&#8217;s pull, fully realized</text>')

    # ---- axis tick labels ----
    for t in (-0.75, -0.5, -0.25, 0.25, 0.5, 0.75):
        body.append(f'<text x="{sx(t):.1f}" y="{PB+26:.1f}" text-anchor="middle" '
                    f'font-family="{FONT}" font-size="14" fill="{GRAY}">'
                    f'{t:+.2f}</text>')
        body.append(f'<text x="{PL-14:.1f}" y="{sy(t)+5:.1f}" text-anchor="end" '
                    f'font-family="{FONT}" font-size="14" fill="{GRAY}">'
                    f'{t:+.2f}</text>')

    # axis titles
    body.append(f'<text x="{(PL+PR)/2:.1f}" y="{PB+58:.1f}" text-anchor="middle" '
                f'font-family="{FONT}" font-size="18" font-weight="bold" '
                f'fill="{INK}">predicted first-round pull  (pool + &#961;&#183;spread '
                f'&#8722; value)  &#8594; toward risk / insecurity</text>')
    yc = (PT + PB) / 2
    body.append(f'<text x="60" y="{yc:.1f}" text-anchor="middle" '
                f'font-family="{FONT}" font-size="18" font-weight="bold" '
                f'fill="{INK}" transform="rotate(-90 60 {yc:.1f})">'
                f'observed net movement of the whole run</text>')

    # ---- quadrant annotations ----
    # push ~ 0 -> stands still / wanders  (a thin band around x = 0)
    ax, ay = sx(0.0), PT + 48
    body.append(f'<text x="{ax:.1f}" y="{ay:.1f}" text-anchor="middle" '
                f'font-family="{FONT}" font-size="15" fill="{INK}">'
                f'predicted push &#8776; 0 &#8594; runs stand still</text>')
    body.append(f'<text x="{ax:.1f}" y="{ay+19:.1f}" text-anchor="middle" '
                f'font-family="{FONT}" font-size="15" fill="{INK}">'
                f'or wander (training noise)</text>')
    # diagonal quadrants -> sign calls direction  (empty upper-left corner)
    sax = sx(-0.86)
    for k, ln in enumerate(["the sign of the",
                            "first-round push",
                            "calls the direction",
                            "of the whole run"]):
        body.append(f'<text x="{sax:.1f}" y="{sy(0.86)+k*19:.1f}" '
                    f'text-anchor="start" font-family="{FONT}" font-size="15.5" '
                    f'fill="{INK}" font-weight="bold">{ln}</text>')

    # ---- points (draw solid last so they sit on top of hollow swaps) ----
    def marker(p):
        cx, cy = sx(p["x"]), sy(p["y"])
        col = FAM[p["fam"]][1]
        if p["swap"]:
            return (f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="7.5" fill="white" '
                    f'stroke="{col}" stroke-width="2.4"/>')
        return (f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="8" fill="{col}" '
                f'fill-opacity="0.9" stroke="white" stroke-width="1.5"/>')

    for p in pts:
        if p["swap"]:
            body.append(marker(p))
    for p in pts:
        if not p["swap"]:
            body.append(marker(p))

    # ---- direct cluster labels ----
    def dlabel(x, y, text, col, anchor="start"):
        return (f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" '
                f'font-family="{FONT}" font-size="16" font-weight="bold" '
                f'fill="{col}">{esc(text)}</text>')

    body.append(dlabel(sx(0.86), sy(0.90), "OLMo mixed-pool", ORANGE, "end"))
    body.append(f'<text x="{sx(0.86):.1f}" y="{sy(0.90)+18:.1f}" '
                f'text-anchor="end" font-family="{FONT}" font-size="14" '
                f'fill="{GRAY}">endpoints beyond y = x (step repeats)</text>')
    body.append(dlabel(sx(-0.70), sy(-0.30), "oracle &", RED))
    body.append(dlabel(sx(-0.70), sy(-0.30) + 19, "injection", RED))
    body.append(dlabel(sx(0.34), sy(0.22), "Qwen", PURPLE, "start"))
    body.append(dlabel(sx(0.34), sy(0.22) + 19, "insecure-code", PURPLE, "start"))

    # ---- legend (identity is never color-alone: swatch + word + count) ----
    counts = defaultdict(int)
    for p in pts:
        counts[p["fam"]] += 1
    lx, ly = PR + 46, PT + 40
    body.append(f'<text x="{lx}" y="{ly-22}" font-family="{FONT}" font-size="16" '
                f'font-weight="bold" fill="{INK}">experiment family</text>')
    for i, f in enumerate(FAM_ORDER):
        yy = ly + i * 34
        name, col = FAM[f]
        body.append(f'<circle cx="{lx+9}" cy="{yy-5}" r="8" fill="{col}" '
                    f'stroke="white" stroke-width="1.5"/>')
        for j, ln in enumerate(wrap(f"{name}", 20)):
            body.append(f'<text x="{lx+28}" y="{yy+j*17}" font-family="{FONT}" '
                        f'font-size="15" fill="{INK}">{esc(ln)} '
                        f'({counts[f]})</text>' if j == 0 else
                        f'<text x="{lx+28}" y="{yy+j*17}" font-family="{FONT}" '
                        f'font-size="15" fill="{INK}">{esc(ln)}</text>')
    # hollow marker key
    hy = ly + 5 * 34 + 20
    body.append(f'<circle cx="{lx+9}" cy="{hy-5}" r="7.5" fill="white" '
                f'stroke="{GRAY}" stroke-width="2.4"/>')
    body.append(f'<text x="{lx+28}" y="{hy}" font-family="{FONT}" font-size="15" '
                f'fill="{INK}">hollow = judge swapped</text>')
    body.append(f'<text x="{lx+28}" y="{hy+17}" font-family="{FONT}" font-size="15" '
                f'fill="{INK}">mid-run (excluded from</text>')
    body.append(f'<text x="{lx+28}" y="{hy+34}" font-family="{FONT}" font-size="15" '
                f'fill="{INK}">the tally below)</text>')

    # ---- evidence line ----
    solid = [p for p in pts if not p["swap"]]
    big = [p for p in solid if abs(p["y"]) >= 0.15]
    match = sum(1 for p in big
                if p["x"] != 0 and (p["x"] > 0) == (p["y"] > 0))
    ey = PB + 84
    body.append(f'<rect x="52" y="{ey}" width="{lx+180-52}" height="60" rx="10" '
                f'fill="#eef5ee" stroke="{GREEN}" stroke-width="2.5"/>')
    body.append(f'<text x="72" y="{ey+27}" font-family="{FONT}" font-size="19" '
                f'fill="{INK}"><tspan font-weight="bold">Among runs that moved '
                f'(|net movement| &#8805; 0.15), the first-round pull had the '
                f'right sign in {match} of {len(big)}.</tspan></text>')
    body.append(f'<text x="72" y="{ey+50}" font-family="{FONT}" font-size="16" '
                f'fill="{INK}">Display tally over the {len(solid)} committed '
                f'non-swap runs plotted; the 9 hollow judge-swap runs are '
                f'excluded because the first-round judge is replaced mid-run.</text>')

    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
           f'font-family="{FONT}">\n<rect width="{W}" height="{H}" fill="white"/>\n'
           + "\n".join(body) + "\n</svg>\n")
    return svg


if __name__ == "__main__":
    out = os.path.join(HERE, "synthesis-pressure-move.svg")
    with open(out, "w") as fh:
        fh.write(build())
    print("wrote", out)
