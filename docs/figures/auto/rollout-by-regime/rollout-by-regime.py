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
BLUE = "#2867b5"       # intervention runs (mixed pools)
GREEN = "#3a7d44"      # self-force runs (self-only judge that grips)
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
    swap = agg["judge-swap"]

    left_runs = [r for r in runs if r["regime"] in ("intervention", "self-force")]
    right_runs = [r for r in runs if r["regime"] == "self-weak"]
    assert len(left_runs) == sel["n"] and len(right_runs) == weak["n"]

    # how far the model predicts each group will move from its starting value
    def mean_pred_move(group):
        return sum(abs(r["endpoint_pred"] - r["v0"]) for r in group) / len(group)

    move_weak = mean_pred_move(right_runs)   # 0.10
    move_sel = mean_pred_move(left_runs)     # 0.43

    # ---- geometry --------------------------------------------------
    W, H = 1450, 968
    top, size, pad = 300, 520, 20
    bottom = top + size
    P1, P2 = 100, 800          # left edge of each panel

    def make_scales(left):
        def X(v):
            return left + pad + v * (size - 2 * pad)

        def Y(v):
            return bottom - pad - v * (size - 2 * pad)
        return X, Y

    S = []

    # ---- headline + model description ------------------------------
    S.append(f'<text x="{P1}" y="56" font-size="30" font-weight="bold" '
             f'fill="{INK}" font-family="{FONT}">'
             f'{esc("First-round measurements predict where selection drives a run")}</text>')
    sub = ("A selection-force model reads only each run's first round — the value, the "
           "candidate value spread, the judge's utilization of the value axis (the "
           "correlation between the judge's score for a candidate and that candidate's "
           "value reading), and the supplier level — then rolls the value forward with "
           "no further peeking. It can only work where a judge actually selects on the "
           "value axis, so runs are grouped by that regime.")
    for i, line in enumerate(wrap(sub, 122)):
        S.append(f'<text x="{P1}" y="{92 + i * 26}" font-size="19" fill="{GRAY}" '
                 f'font-family="{FONT}">{esc(line)}</text>')

    # ---- panel headers ---------------------------------------------
    def panel_header(px, title, sub_text):
        S.append(f'<text x="{px}" y="212" font-size="22" font-weight="bold" '
                 f'fill="{INK}" font-family="{FONT}">{esc(title)}</text>')
        for i, line in enumerate(wrap(sub_text, 64)):
            S.append(f'<text x="{px}" y="{239 + i * 23}" font-size="17" '
                     f'fill="{GRAY}" font-family="{FONT}">{esc(line)}</text>')

    panel_header(P1, "Where a judge selects on the value axis",
                 f"Runs hug the diagonal: mean endpoint error {sel['endpoint_mae']} "
                 f"on the 0–1 value scale, versus {sel['persistence_mae']} for "
                 f"predicting no change ({sel['n']} runs).")
    panel_header(P2, "Where selection has no grip: utilization near zero",
                 f"The model predicts little movement (mean predicted move "
                 f"{move_weak:.2f}, versus {move_sel:.2f} at left); the rest is "
                 f"training instability (error {weak['endpoint_mae']} versus "
                 f"{weak['persistence_mae']} for no change; {weak['n']} runs).")

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
        S.append(f'<text x="{(px + right) / 2:.0f}" y="{bottom + 66}" text-anchor="middle" '
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
              lambda r: BLUE if r["regime"] == "intervention" else GREEN)
    draw_dots(right_runs, X2, Y2,
              lambda r: RED if (r["cond"] == "frozen_base" and str(r["seed"]) == "5")
              else GRAY, hollow=True)

    # ---- key, left panel (top-left is empty of data) ---------------
    key = [("intervention (mixed pool)", BLUE),
           ("self-only judge that grips", GREEN)]
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
             f'fill="{INK}" font-family="{FONT}">(the bloom)</text>')
    S.append(f'<line x1="{P2 + 130}" y1="{top + 70}" x2="{bx + 1:.0f}" y2="{by - 13:.0f}" '
             f'stroke="{INK}" stroke-width="2.5" marker-end="url(#arr)"/>')

    # ---- footnotes --------------------------------------------------
    foot1 = (f"Nine fan-then-press schedule cells (judge swapped mid-run, endpoint "
             f"error {swap['endpoint_mae']}) are excluded — the model fixes judge "
             f"utilization at round 1, so it cannot apply after a swap.")
    foot2 = ("Data: experiments/simple_model_rollout.json (per_run, 67 runs; regime "
             "field). Model scalars are fit leave-one-run-out; supplier level = mean "
             "value of the co-generator's round-1 candidates.")
    fy = bottom + 106
    for text in (foot1, foot2):
        for line in wrap(text, 158):
            S.append(f'<text x="{P1}" y="{fy}" font-size="15" fill="{GRAY}" '
                     f'font-family="{FONT}">{esc(line)}</text>')
            fy += 22

    out = os.path.join(HERE, "rollout-by-regime.svg")
    with open(out, "w") as f:
        f.write(svg_doc(W, H, "\n".join(S)))
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
