#!/usr/bin/env python3
"""Judge-model ablation, Qwen em750 supplier-removed self-only loop.

Swapping ONLY the judge model (evolving self vs frozen base, identical candid
judge prompt, identical self-only candidate pool) REVERSES the trajectory of the
forced-choice insecure-code self-report. Self-judge amplifies toward 1; frozen
base judge collapses toward 0.

House style: docs/figures/src/make_figures.py (Owain Evans lab — white ground,
headline finding, fat labels, real data). Palette constants copied verbatim.
Run:  python3 judge-ablation-selfonly.py   (writes judge-ablation-selfonly.svg)
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "..", "..", "..",
                   "experiments", "qwen_judge_ablation.json")

# --- palette (verbatim from make_figures.py) ---
INK = "#1a1a1a"
BLUE = "#2867b5"       # self-judge series
GREEN = "#3a7d44"      # frozen base-judge series
RED = "#b5342c"        # reversal / emphasis text
GRAY = "#6b7684"       # recessive only (axes, muted captions)
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


def text_lines(x, y, text, size, width, color=INK, weight="normal", lh=1.4,
               anchor="start"):
    out = []
    for i, ln in enumerate(wrap(text, width)):
        out.append(f'<text x="{x}" y="{y + i * size * lh:.1f}" '
                   f'text-anchor="{anchor}" font-family="{FONT}" '
                   f'font-size="{size}" font-weight="{weight}" '
                   f'fill="{color}">{esc(ln)}</text>')
    return "\n".join(out)


def load():
    d = json.load(open(SRC))
    r = d["runs"]
    return {
        "self_base": r["candid_self"]["baseline"]["p_insecure"],
        "base_base": r["candid_base"]["baseline"]["p_insecure"],
        "self41": r["candid_self"]["seeds"]["41"]["p_insecure_trajectory"],
        "self42": r["candid_self"]["seeds"]["42"]["p_insecure_trajectory"],
        "base41": r["candid_base"]["seeds"]["41"]["p_insecure_trajectory"],
        "base42": r["candid_base"]["seeds"]["42"]["p_insecure_trajectory"],
        "n_self41": r["candid_self"]["seeds"]["41"]["p_insecure_net"],
        "n_self42": r["candid_self"]["seeds"]["42"]["p_insecure_net"],
        "n_base41": r["candid_base"]["seeds"]["41"]["p_insecure_net"],
        "n_base42": r["candid_base"]["seeds"]["42"]["p_insecure_net"],
    }


def sgn(v):
    return f"+{v:.2f}" if v >= 0 else f"−{abs(v):.2f}"


def marker(cx, cy, color, kind):
    if kind == "circle":
        return f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="6.5" fill="{color}" stroke="white" stroke-width="2"/>'
    # square for the second seed
    s = 6.0
    return (f'<rect x="{cx-s:.1f}" y="{cy-s:.1f}" width="{2*s:.1f}" '
            f'height="{2*s:.1f}" fill="{color}" stroke="white" stroke-width="2"/>')


def build():
    d = load()
    W, H = 1280, 900
    b = [f'<rect width="{W}" height="{H}" fill="white"/>']

    # ---- headline finding ----
    b.append(text_lines(60, 62,
        "Only the judge model changed: the evolving self-judge amplifies the",
        31, 92, weight="bold"))
    b.append(text_lines(60, 100,
        "insecurity-admission; the frozen base judge erases it",
        31, 92, weight="bold"))
    # colored clause emphasising the reversal
    b.append(f'<text x="60" y="140" font-family="{FONT}" font-size="21" '
             f'font-weight="bold" fill="{RED}">The amplifying force is the '
             f'judge&#8217;s taste, not training on the loop&#8217;s own output.</text>')

    # ---- recipe subtitle ----
    b.append(text_lines(60, 176,
        "Qwen3-4B em750 organism · organism writes all 6 candidates · "
        "head-to-head duels, keep 2, train, repeat ×4 rounds · "
        "candid judge prompt in both conditions · 2 seeds each",
        18, 130, color=GRAY))

    # ---- plot geometry ----
    px, py, pw, ph = 150, 250, 760, 500
    ymin, ymax = 0.0, 1.0

    def X(i):
        return px + pw * i / 4.0

    def Y(v):
        return py + ph * (ymax - v) / (ymax - ymin)

    # gridlines + y ticks
    for v in (0.0, 0.2, 0.4, 0.6, 0.8, 1.0):
        yy = Y(v)
        b.append(f'<line x1="{px}" y1="{yy:.1f}" x2="{px+pw}" y2="{yy:.1f}" '
                 f'stroke="#e6e6e2" stroke-width="1"/>')
        b.append(f'<text x="{px-14}" y="{yy+6:.1f}" text-anchor="end" '
                 f'font-family="{FONT}" font-size="16" fill="{GRAY}">{v:.1f}</text>')

    # baseline band (both runs re-measure near ~0.33; noise floor 0.020)
    b.append(f'<line x1="{px}" y1="{Y(0.333):.1f}" x2="{px+pw}" y2="{Y(0.333):.1f}" '
             f'stroke="{INK}" stroke-width="1.4" stroke-dasharray="6 5"/>')
    b.append(f'<text x="{px+8}" y="{Y(0.333)-9:.1f}" font-family="{FONT}" '
             f'font-size="14" fill="{INK}">re-measured baseline ≈ 0.33 '
             f'(self 0.34, base 0.33; noise floor 0.02)</text>')

    # x ticks
    for i in range(5):
        lab = "baseline" if i == 0 else str(i)
        b.append(f'<text x="{X(i):.1f}" y="{py+ph+30:.1f}" text-anchor="middle" '
                 f'font-family="{FONT}" font-size="16" fill="{GRAY}">{lab}</text>')
    b.append(f'<text x="{px+pw/2:.1f}" y="{py+ph+64:.1f}" text-anchor="middle" '
             f'font-family="{FONT}" font-size="18" fill="{INK}">selection round</text>')

    # y axis title (rotated)
    yc = py + ph / 2
    b.append(f'<text x="66" y="{yc:.1f}" text-anchor="middle" '
             f'transform="rotate(-90 66 {yc:.1f})" font-family="{FONT}" '
             f'font-size="18" fill="{INK}">'
             f'p(insecure) — forced-choice insecure-code self-report</text>')

    # ---- trajectories ----
    series = [
        ("self41", d["self41"], BLUE, "circle",
         f"self judge  s41   net {sgn(d['n_self41'])}", -2),
        ("self42", d["self42"], BLUE, "square",
         f"self judge  s42   net {sgn(d['n_self42'])}", 14),
        ("base41", d["base41"], GREEN, "circle",
         f"frozen base judge  s41   net {sgn(d['n_base41'])}", 6),
        ("base42", d["base42"], GREEN, "square",
         f"frozen base judge  s42   net {sgn(d['n_base42'])}", -8),
    ]
    for _name, traj, color, kind, label, dy in series:
        pts = " ".join(f"{X(i):.1f},{Y(v):.1f}" for i, v in enumerate(traj))
        dash = "" if kind == "circle" else ' stroke-dasharray="10 5"'
        b.append(f'<polyline points="{pts}" fill="none" stroke="{color}" '
                 f'stroke-width="3.5" stroke-opacity="0.9"{dash}/>')
        for i, v in enumerate(traj):
            b.append(marker(X(i), Y(v), color, kind))
        ex, ey = X(4), Y(traj[-1])
        b.append(f'<text x="{ex+16:.1f}" y="{ey+dy+5:.1f}" font-family="{FONT}" '
                 f'font-size="18" font-weight="bold" fill="{color}">{esc(label)}</text>')

    # direction arrows near the ends, in ink-neutral captions
    b.append(text_lines(px+pw+16, Y(0.955), "climbs toward 1", 15, 22,
                        color=BLUE))
    b.append(text_lines(px+pw+16, Y(0.09), "collapses toward 0", 15, 24,
                        color=GREEN))

    # solid = seed 41 (circle), dashed = seed 42 (square) — key, not a legend box
    b.append(f'<text x="{px}" y="{py-16:.1f}" font-family="{FONT}" font-size="15" '
             f'fill="{GRAY}">seeds within a colour: solid line + circle = s41 · '
             f'dashed line + square = s42</text>')

    # ---- same-prompt / same-pool annotation (thin) ----
    ann_y = py + ph + 96
    b.append(f'<rect x="60" y="{ann_y}" width="{W-120}" height="70" rx="8" '
             f'fill="{KEY_FILL}" stroke="{INK}" stroke-width="1.6"/>')
    b.append(f'<text x="80" y="{ann_y+28}" font-family="{FONT}" font-size="16" '
             f'fill="{INK}"><tspan font-weight="bold">One knob turned. </tspan>'
             f'Both conditions use the SAME candid judge prompt and the SAME '
             f'self-only candidate pool; only the judge model differs —</text>')
    b.append(f'<text x="80" y="{ann_y+53}" font-family="{FONT}" font-size="16" '
             f'fill="{INK}">the evolving organism itself (blue) or its frozen '
             f'pre-loop base (green). '
             f'<tspan font-weight="bold" fill="{RED}">The pre-registered lean '
             f'(self-consumption) is rejected.</tspan></text>')

    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
            f'font-family="{FONT}">\n' + "\n".join(b) + "\n</svg>")


if __name__ == "__main__":
    out = os.path.join(HERE, "judge-ablation-selfonly.svg")
    with open(out, "w") as f:
        f.write(build())
    print("wrote", out)
