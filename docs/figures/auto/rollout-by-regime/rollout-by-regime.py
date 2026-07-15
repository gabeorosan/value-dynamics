#!/usr/bin/env python3
"""Draft figure: predicted vs actual run endpoints, separated by regime.

The simple loop model is a SELECTION-FORCE model: from a run's first-round
measurements (value, candidate spread, judge utilization, supplier level) it
rolls the value forward. It can only work where a judge actually selects on
the value axis, so this figure separates runs by the `regime` field instead
of pooling them.

Left panel:  regime == "intervention" or "self-force" (36 runs) — a judge
             selects on the axis; points hug the y = x diagonal.
Right panel: regime == "self-weak" (22 runs) — round-1 judge utilization is
             near zero; the model predicts almost no move and the remaining
             wandering is training instability.
Excluded:    regime == "judge-swap" (9 runs) — the judge changes mid-run,
             so a model that fixes utilization at round 1 cannot apply.

Interpretation text (the endpoint-error numbers, the paragraph, the panel
sentences) lives in caption.md, OUTSIDE the image, not on the figure.

Data: experiments/simple_model_rollout.json (per_run, aggregates).
House style follows docs/figures/src/make_figures.py.
Regenerate with:  python3 rollout-by-regime.py
"""
import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "..", "..", "..", "experiments",
                    "simple_model_rollout.json")

INK = "#1a1a1a"
BLUE = "#2867b5"       # house blue — intervention runs (mixed pools)
GREEN = "#3a7d44"      # house green (frozen-judge series) — unused here
AMBER = "#c07d18"      # house amber — self-only runs (judge that grips)
RED = "#b5342c"        # emphasis for reversal / warning (the bloom callout)
GRAY = "#6b7684"       # recessive (axes, muted captions, the no-grip runs)
GRID = "#e8e8e8"

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


def svg_doc(w, h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
            f'font-family="{FONT}">\n<rect width="{w}" height="{h}" fill="white"/>\n'
            f'<defs><marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" '
            f'markerWidth="6" markerHeight="6" orient="auto-start-reverse">'
            f'<path d="M 0 0 L 10 5 L 0 10 z" fill="{INK}"/></marker></defs>\n'
            f'{body}\n</svg>')


def main():
    with open(DATA) as f:
        d = json.load(f)
    runs = d["per_run"]
    agg = d["aggregates"]
    sel = agg["selection-driven (intervention+self-force)"]
    weak = agg["self-weak"]

    left_runs = [r for r in runs if r["regime"] in ("intervention", "self-force")]
    right_runs = [r for r in runs if r["regime"] == "self-weak"]
    assert len(left_runs) == sel["n"] and len(right_runs) == weak["n"]

    # ---- geometry --------------------------------------------------
    W = 1450
    top, size, pad = 172, 520, 20
    bottom = top + size
    P1, P2 = 100, 800          # left edge of each panel
    H = bottom + 128

    def make_scales(left):
        def X(v):
            return left + pad + v * (size - 2 * pad)

        def Y(v):
            return bottom - pad - v * (size - 2 * pad)
        return X, Y

    S = []

    # ---- headline (short; interpretation lives in the caption) -----
    S.append(f'<text x="{P1}" y="52" font-size="30" font-weight="bold" '
             f'fill="{INK}" font-family="{FONT}">'
             f'{esc("First-round measurements predict where selection drives a run")}</text>')

    # ---- panel titles (no subtitle sentences) ----------------------
    def panel_title(px, title):
        S.append(f'<text x="{px}" y="122" font-size="22" font-weight="bold" '
                 f'fill="{INK}" font-family="{FONT}">{esc(title)}</text>')

    panel_title(P1, "Where a judge selects on the value axis")
    panel_title(P2, "Where selection has no grip: utilization near zero")

    # ---- axes, grid, diagonal for both panels ----------------------
    def panel_frame(px, diag_label_v, y_ticks=True):
        X, Y = make_scales(px)
        right = px + size
        for v in (0, 0.25, 0.5, 0.75, 1.0):
            S.append(f'<line x1="{X(v):.0f}" y1="{top}" x2="{X(v):.0f}" y2="{bottom}" '
                     f'stroke="{GRID}" stroke-width="1"/>')
            S.append(f'<line x1="{px}" y1="{Y(v):.0f}" x2="{right}" y2="{Y(v):.0f}" '
                     f'stroke="{GRID}" stroke-width="1"/>')
            lab = f"{v:g}"
            S.append(f'<text x="{X(v):.0f}" y="{bottom + 30}" text-anchor="middle" '
                     f'font-size="18" fill="{GRAY}" font-family="{FONT}">{lab}</text>')
            if y_ticks:
                S.append(f'<text x="{px - 12}" y="{Y(v) + 6:.0f}" text-anchor="end" '
                         f'font-size="18" fill="{GRAY}" font-family="{FONT}">{lab}</text>')
        S.append(f'<line x1="{px}" y1="{bottom}" x2="{right}" y2="{bottom}" '
                 f'stroke="{GRAY}" stroke-width="1.5"/>')
        S.append(f'<line x1="{px}" y1="{top}" x2="{px}" y2="{bottom}" '
                 f'stroke="{GRAY}" stroke-width="1.5"/>')
        # y = x diagonal
        S.append(f'<line x1="{X(0):.0f}" y1="{Y(0):.0f}" x2="{X(1):.0f}" y2="{Y(1):.0f}" '
                 f'stroke="{GRAY}" stroke-width="1.8" stroke-dasharray="7 6"/>')
        dx, dy = X(diag_label_v) - 12, Y(diag_label_v) - 12
        S.append(f'<text x="{dx:.0f}" y="{dy:.0f}" text-anchor="middle" font-size="16" '
                 f'fill="{GRAY}" font-family="{FONT}" '
                 f'transform="rotate(-45 {dx:.0f} {dy:.0f})">actual = predicted</text>')
        # x-axis title
        S.append(f'<text x="{(px + right) / 2:.0f}" y="{bottom + 64}" text-anchor="middle" '
                 f'font-size="19" fill="{INK}" font-family="{FONT}">'
                 f'predicted endpoint (from round-1 measurements)</text>')
        return X, Y

    X1, Y1 = panel_frame(P1, 0.20)
    X2, Y2 = panel_frame(P2, 0.30)

    # shared y-axis title, left panel only
    S.append(f'<text x="44" y="{(top + bottom) / 2:.0f}" text-anchor="middle" '
             f'font-size="19" fill="{INK}" font-family="{FONT}" '
             f'transform="rotate(-90 44 {(top + bottom) / 2:.0f})">actual endpoint</text>')

    # ---- dots (fan exact pile-ups so they stay countable) ----------
    def draw_dots(panel_runs, X, Y, color_fn, hollow=False):
        groups = {}
        for r in panel_runs:
            groups.setdefault((round(r["endpoint_pred"], 2),
                               round(r["endpoint_true"], 2)), []).append(r)
        out = []
        for (gpx, gpy), members in groups.items():
            n = len(members)
            rad = 0 if n == 1 else max(9.5, 7.0 * n / math.pi)
            for k, r in enumerate(members):
                cx = X(r["endpoint_pred"])
                cy = Y(r["endpoint_true"])
                if n > 1:
                    ang = math.pi / 2 + 2 * math.pi * k / n
                    cx = X(gpx) + rad * math.cos(ang)
                    cy = Y(gpy) - rad * math.sin(ang)
                c = color_fn(r)
                if hollow:
                    out.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="8.5" fill="white"/>'
                               f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="7" fill="white" '
                               f'stroke="{c}" stroke-width="3"/>')
                else:
                    out.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="7" fill="{c}" '
                               f'stroke="white" stroke-width="2"/>')
        S.extend(out)

    draw_dots(left_runs, X1, Y1,
              lambda r: BLUE if r["regime"] == "intervention" else AMBER)
    draw_dots(right_runs, X2, Y2,
              lambda r: RED if (r["cond"] == "frozen_base" and str(r["seed"]) == "5")
              else GRAY, hollow=True)

    # ---- key, left panel (top-left is empty of data) ---------------
    key = [("intervention (mixed pool)", BLUE),
           ("self-only judge that grips", AMBER)]
    for i, (label, c) in enumerate(key):
        ky = top + 42 + i * 32
        S.append(f'<circle cx="{P1 + 44}" cy="{ky - 6}" r="7" fill="{c}" '
                 f'stroke="white" stroke-width="2"/>')
        S.append(f'<text x="{P1 + 62}" y="{ky}" font-size="18" fill="{INK}" '
                 f'font-family="{FONT}">{esc(label)}</text>')

    # ---- bloom callout, right panel --------------------------------
    bloom = next(r for r in right_runs
                 if r["cond"] == "frozen_base" and str(r["seed"]) == "5")
    bx, by = X2(bloom["endpoint_pred"]), Y2(bloom["endpoint_true"])
    S.append(f'<text x="{P2 + 34}" y="{top + 40}" font-size="17" font-weight="bold" '
             f'fill="{INK}" font-family="{FONT}">utilization rose mid-run</text>')
    S.append(f'<text x="{P2 + 34}" y="{top + 62}" font-size="17" '
             f'fill="{INK}" font-family="{FONT}">the bloom</text>')
    S.append(f'<line x1="{P2 + 130}" y1="{top + 70}" x2="{bx + 1:.0f}" y2="{by - 13:.0f}" '
             f'stroke="{INK}" stroke-width="2.5" marker-end="url(#arr)"/>')

    # ---- one-line data pointer (source only; no readouts) ----------
    S.append(f'<text x="{P1}" y="{bottom + 100}" font-size="15" fill="{GRAY}" '
             f'font-family="{FONT}">'
             f'{esc("Data: experiments/simple_model_rollout.json (per_run, regime field). Endpoint-error numbers and full method are in the caption.")}</text>')

    out = os.path.join(HERE, "rollout-by-regime.svg")
    with open(out, "w") as f:
        f.write(svg_doc(W, H, "\n".join(S)))
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
