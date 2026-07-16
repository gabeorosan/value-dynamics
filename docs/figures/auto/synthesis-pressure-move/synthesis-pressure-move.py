#!/usr/bin/env python3
"""Predicted first-round pull vs each run's observed net movement.

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
    W, H = 1290, 906
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

    # headline (descriptive orientation only) + subtitle
    body.append(f'<text x="52" y="60" font-family="{FONT}" font-size="34" '
                f'font-weight="bold" fill="{INK}">Predicted first-round pull vs '
                f'each run&#8217;s observed net movement</text>')
    body.append(f'<text x="52" y="100" font-family="{FONT}" font-size="20" '
                f'fill="{INK}">Horizontal: the model&#8217;s predicted first-round '
                f'pull&#160;&#160;(round-1 pool mean&#160;+&#160;&#961;&#183;spread)'
                f'&#160;&#8722;&#160;round-1 value.</text>')
    body.append(f'<text x="52" y="126" font-family="{FONT}" font-size="20" '
                f'fill="{INK}">Vertical: the run&#8217;s observed net movement '
                f'(final value&#160;&#8722;&#160;round-1 value). One dot per run, '
                f'{len(pts)} runs.</text>')

    # ---- axes frame ----
    body.append(f'<rect x="{PL}" y="{PT}" width="{S}" height="{S}" '
                f'fill="#fcfcfb" stroke="{FAINT}" stroke-width="1.5"/>')

    # ---- implied vector field (drawn UNDER everything else) ----
    # The model's claim is: observed net movement approx equals predicted pull.
    # So at regular pull positions x along the axis, the predicted movement is a
    # vertical vector from y = 0 up (or down) to y = x. The y = x diagonal is the
    # envelope of the tips. Kept faint/thin so the dots read on top.
    ARROW = "#c3d3ea"          # very light blue, recessive
    for k in range(-8, 9):
        xv = k * 0.1
        if xv == 0:
            continue
        tx = sx(xv)
        yb, yt = sy(0.0), sy(xv)      # base at zero, tip at y = x
        body.append(f'<line x1="{tx:.1f}" y1="{yb:.1f}" x2="{tx:.1f}" '
                    f'y2="{yt:.1f}" stroke="{ARROW}" stroke-width="1.4"/>')
        w, h = 3.4, 6.0               # arrowhead points toward the tip
        if xv > 0:                    # tip is above the base -> point up
            head = f'{tx:.1f},{yt:.1f} {tx-w:.1f},{yt+h:.1f} {tx+w:.1f},{yt+h:.1f}'
        else:                         # tip is below the base -> point down
            head = f'{tx:.1f},{yt:.1f} {tx-w:.1f},{yt-h:.1f} {tx+w:.1f},{yt-h:.1f}'
        body.append(f'<polygon points="{head}" fill="{ARROW}"/>')

    # ---- zero lines ----
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
                f'transform="rotate(-45 {lxr:.1f} {lyr:.1f})">y = x</text>')

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

    # (quadrant interpretation annotations removed — moved to caption.md)

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

    # (in-plot cluster labels removed — the legend key identifies the families)

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
                f'fill="{INK}">mid-run</text>')
    # arrow-field key entry (identification only)
    ay = hy + 46
    body.append(f'<line x1="{lx+9}" y1="{ay+6}" x2="{lx+9}" y2="{ay-8}" '
                f'stroke="{ARROW}" stroke-width="1.4"/>')
    body.append(f'<polygon points="{lx+9},{ay-8} {lx+5.6},{ay-2} {lx+12.4},{ay-2}" '
                f'fill="{ARROW}"/>')
    body.append(f'<text x="{lx+28}" y="{ay-4}" font-family="{FONT}" font-size="15" '
                f'fill="{INK}">predicted movement</text>')
    body.append(f'<text x="{lx+28}" y="{ay+13}" font-family="{FONT}" font-size="15" '
                f'fill="{INK}">at this pull (y = x)</text>')

    # ---- source line ----
    src_y = hy + 90
    for j, ln in enumerate(["Source: experiments/",
                            "spread_util_unified.json",
                            "(field records)."]):
        body.append(f'<text x="{lx}" y="{src_y + j*17}" font-family="{FONT}" '
                    f'font-size="14" fill="{GRAY}">{esc(ln)}</text>')

    # (evidence tally box removed — the 39/43 sign-agreement figure and the
    #  9 excluded judge-swap runs are stated in caption.md)

    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
           f'font-family="{FONT}">\n<rect width="{W}" height="{H}" fill="white"/>\n'
           + "\n".join(body) + "\n</svg>\n")
    return svg


if __name__ == "__main__":
    out = os.path.join(HERE, "synthesis-pressure-move.svg")
    with open(out, "w") as fh:
        fh.write(build())
    print("wrote", out)
