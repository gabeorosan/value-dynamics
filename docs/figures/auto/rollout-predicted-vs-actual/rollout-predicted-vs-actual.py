#!/usr/bin/env python3
"""Draft figure: predicted vs actual run endpoints for the simple loop model.

Scatter of actual endpoint (y) against the endpoint predicted by rolling a
simple model forward from each run's FIRST-round measurements only (x).
Data: experiments/simple_model_rollout.json (per_run, 67 runs; aggregates).
House style follows docs/figures/src/make_figures.py.
Regenerate with:  python3 rollout-predicted-vs-actual.py
"""
import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "..", "..", "..", "experiments",
                    "simple_model_rollout.json")

INK = "#1a1a1a"
BLUE = "#2867b5"       # self-only pools
GREEN = "#3a7d44"      # base-mixed pools
RED = "#b5342c"        # peer-mixed pools
GRAY = "#6b7684"       # recessive only (axes, muted captions)
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
    mae_all = agg["all"]["endpoint_mae"]          # 0.175
    mae_persist = agg["all"]["persistence_mae"]   # 0.351
    mae_peer = agg["peer-mixed"]["endpoint_mae"]  # 0.042
    n_all = agg["all"]["n"]                       # 67

    # ---- geometry -------------------------------------------------
    W, H = 1080, 950
    left, top, size, pad = 120, 160, 640, 16
    bottom = top + size          # 800
    right = left + size          # 760

    def X(v):
        return left + pad + v * (size - 2 * pad)

    def Y(v):
        return bottom - pad - v * (size - 2 * pad)

    COLOR = {"self-only": BLUE, "base-mixed": GREEN, "peer-mixed": RED}
    S = []

    # ---- headline + subtitle -------------------------------------
    S.append(f'<text x="{left}" y="56" font-size="28" font-weight="bold" '
             f'fill="{INK}" font-family="{FONT}">'
             f'{esc("First-round measurements roughly predict where a run ends")}</text>')
    sub = (f"A simple loop model is fed only each run's round-1 measurements and rolled "
           f"forward. Endpoint mean absolute error: {mae_all} on the 0–1 value scale, "
           f"versus {mae_persist} for assuming no change; {mae_peer} on the peer-invasion runs.")
    for i, line in enumerate(wrap(sub, 104)):
        S.append(f'<text x="{left}" y="{88 + i * 25}" font-size="19" fill="{GRAY}" '
                 f'font-family="{FONT}">{esc(line)}</text>')

    # ---- grid, axes, diagonal ------------------------------------
    for v in (0, 0.25, 0.5, 0.75, 1.0):
        S.append(f'<line x1="{X(v):.0f}" y1="{top}" x2="{X(v):.0f}" y2="{bottom}" '
                 f'stroke="{GRID}" stroke-width="1"/>')
        S.append(f'<line x1="{left}" y1="{Y(v):.0f}" x2="{right}" y2="{Y(v):.0f}" '
                 f'stroke="{GRID}" stroke-width="1"/>')
        lab = f"{v:g}"
        S.append(f'<text x="{X(v):.0f}" y="{bottom + 28}" text-anchor="middle" '
                 f'font-size="18" fill="{GRAY}" font-family="{FONT}">{lab}</text>')
        S.append(f'<text x="{left - 12}" y="{Y(v) + 6:.0f}" text-anchor="end" '
                 f'font-size="18" fill="{GRAY}" font-family="{FONT}">{lab}</text>')
    S.append(f'<line x1="{left}" y1="{bottom}" x2="{right}" y2="{bottom}" '
             f'stroke="{GRAY}" stroke-width="1.5"/>')
    S.append(f'<line x1="{left}" y1="{top}" x2="{left}" y2="{bottom}" '
             f'stroke="{GRAY}" stroke-width="1.5"/>')

    # y = x diagonal
    S.append(f'<line x1="{X(0):.0f}" y1="{Y(0):.0f}" x2="{X(1):.0f}" y2="{Y(1):.0f}" '
             f'stroke="{GRAY}" stroke-width="1.8" stroke-dasharray="7 6"/>')
    dx, dy = X(0.36) - 12, Y(0.36) - 12
    S.append(f'<text x="{dx:.0f}" y="{dy:.0f}" text-anchor="middle" font-size="16" '
             f'fill="{GRAY}" font-family="{FONT}" '
             f'transform="rotate(-45 {dx:.0f} {dy:.0f})">actual = predicted</text>')

    # axis titles
    S.append(f'<text x="{(left + right) / 2:.0f}" y="{bottom + 66}" text-anchor="middle" '
             f'font-size="19" fill="{INK}" font-family="{FONT}">'
             f'predicted endpoint (from round-1 measurements)</text>')
    S.append(f'<text x="58" y="{(top + bottom) / 2:.0f}" text-anchor="middle" '
             f'font-size="19" fill="{INK}" font-family="{FONT}" '
             f'transform="rotate(-90 58 {(top + bottom) / 2:.0f})">actual endpoint</text>')

    # ---- dots (fan exact duplicates so pile-ups stay visible) ----
    groups = {}
    for r in runs:
        groups.setdefault((round(r["endpoint_pred"], 3),
                           round(r["endpoint_true"], 3)), []).append(r)

    solid, hollow = [], []
    for (px, py), members in groups.items():
        n = len(members)
        for k, r in enumerate(members):
            cx, cy = X(px), Y(py)
            if n > 1:
                ang = math.pi / 2 + 2 * math.pi * k / n
                cx += 6.5 * math.cos(ang)
                cy -= 6.5 * math.sin(ang)
            c = COLOR[r["composition"]]
            if r["judge"] == "schedule":
                hollow.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="10" fill="white"/>'
                              f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="7" fill="white" '
                              f'stroke="{c}" stroke-width="3"/>')
            else:
                solid.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="7" fill="{c}" '
                             f'stroke="white" stroke-width="2"/>')
    S.extend(solid)
    S.extend(hollow)

    # ---- callout 1: the nine judge-schedule runs (hollow dots) ---
    lines1 = ["Hollow dots: judge swapped",
              "mid-run — the round-1 judge",
              "reading no longer applies"]
    for i, line in enumerate(lines1):
        weight = ' font-weight="bold"' if i == 0 else ""
        S.append(f'<text x="340" y="{638 + i * 23}" font-size="17" fill="{INK}"'
                 f'{weight} font-family="{FONT}">{esc(line)}</text>')
    tx, ty = X(0.080), Y(0.229)   # one of the hollow dots
    S.append(f'<line x1="332" y1="655" x2="{tx + 12:.0f}" y2="{ty + 2:.0f}" '
             f'stroke="{INK}" stroke-width="2.5" marker-end="url(#arr)"/>')

    # ---- callout 2: frozen_base seed 5 (the bloom) ---------------
    bloom = next(r for r in runs
                 if r["cond"] == "frozen_base" and str(r["seed"]) == "5")
    bx, by = X(bloom["endpoint_pred"]), Y(bloom["endpoint_true"])
    lines2 = ["judge utilization rose", "mid-run (the bloom)"]
    for i, line in enumerate(lines2):
        S.append(f'<text x="400" y="{290 + i * 23}" font-size="17" fill="{INK}" '
                 f'font-family="{FONT}">{esc(line)}</text>')
    S.append(f'<line x1="393" y1="297" x2="{bx + 12:.0f}" y2="{by:.0f}" '
             f'stroke="{INK}" stroke-width="2.5" marker-end="url(#arr)"/>')

    # ---- key ------------------------------------------------------
    key = [("self-only", "trains only on its own outputs", BLUE),
           ("base-mixed", "half the pool from the base model", GREEN),
           ("peer-mixed", "half the pool from a peer model", RED)]
    ky = 230
    for name, gloss, c in key:
        S.append(f'<circle cx="812" cy="{ky - 6}" r="8" fill="{c}" '
                 f'stroke="white" stroke-width="2"/>')
        S.append(f'<text x="832" y="{ky}" font-size="19" font-weight="bold" '
                 f'fill="{INK}" font-family="{FONT}">{esc(name)}</text>')
        for i, line in enumerate(wrap(gloss, 26)):
            S.append(f'<text x="832" y="{ky + 24 + i * 21}" font-size="16" '
                     f'fill="{GRAY}" font-family="{FONT}">{esc(line)}</text>')
        ky += 92

    # ---- footnote --------------------------------------------------
    foot = (f"Data: experiments/simple_model_rollout.json — {n_all} runs; model inputs "
            f"are round-1 value, candidate spread, judge utilization, and supplier level; "
            f"scalars fit leave-one-run-out.")
    for i, line in enumerate(wrap(foot, 120)):
        S.append(f'<text x="{left}" y="{bottom + 104 + i * 21}" font-size="15" '
                 f'fill="{GRAY}" font-family="{FONT}">{esc(line)}</text>')

    out = os.path.join(HERE, "rollout-predicted-vs-actual.svg")
    with open(out, "w") as f:
        f.write(svg_doc(W, H, "\n".join(S)))
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
