#!/usr/bin/env python3
"""Social-format figures for the Twitter thread draft (docs/figures/twitter_thread_draft.md).

Three figures that anchor tweets with no existing figure:
  thread_crosslag_null.svg     - forest plot of the cross-lag betas (report_criterion_crosslag.md)
  thread_selfreport_fan.svg    - seed-chaotic self-report basins (selfaware_loop_grid.json)
  thread_letgo_release.svg     - three release trajectories (selfaware_letgo_pilot.json, partial)

House style follows make_figures.py; ~1.9:1 aspect, larger type for feed legibility.
Numbers are re-read from the JSONs where they exist. Regenerate: python3 make_thread_figures.py
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..", "..", "..")
GRID = os.path.join(ROOT, "experiments", "em_selfaware_loop", "output", "selfaware_loop_grid.json")
LETGO = os.path.join(ROOT, "experiments", "em_selfaware_loop", "output", "selfaware_letgo_pilot.json")

INK = "#1a1a1a"
BLUE = "#2867b5"
GREEN = "#3a7d44"
RED = "#b5342c"
GRAY = "#6b7684"
KEY_FILL = "#eef5ee"
FONT = "Helvetica, Arial, sans-serif"


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def txt(x, y, s, size, color=INK, weight="normal", anchor="start"):
    return (f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-size="{size}" '
            f'font-weight="{weight}" fill="{color}" font-family="{FONT}">{esc(s)}</text>')


def svg_doc(w, h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
            f'font-family="{FONT}">\n<rect width="{w}" height="{h}" fill="white"/>\n{body}\n</svg>')


def write(name, content):
    p = os.path.join(HERE, name)
    with open(p, "w") as f:
        f.write(content)
    print("wrote", p)


# ------------------------------------------------------------------
# 1. Cross-lag forest plot (numbers verbatim from report_criterion_crosslag.md)
# ------------------------------------------------------------------
def fig_crosslag():
    ROWS = [  # (condition, direction label, beta, lo, hi, highlight)
        ("self-judge", "criterion now → behavior next round", -0.055, -0.193, 0.066, False),
        ("self-judge", "behavior now → criterion next round", 0.066, -0.045, 0.169, False),
        ("self-judge", "self-report now → behavior next round", -0.007, -0.158, 0.130, False),
        ("self-judge", "behavior now → self-report next round", 0.091, -0.002, 0.161, True),
        ("frozen judge", "criterion now → behavior next round", -0.012, -0.161, 0.120, False),
        ("frozen judge", "behavior now → criterion next round", 0.003, -0.175, 0.197, False),
        ("frozen judge", "self-report now → behavior next round", 0.028, -0.101, 0.185, False),
        ("frozen judge", "behavior now → self-report next round", 0.065, -0.089, 0.228, False),
    ]
    W, H = 1400, 740
    b = []
    b.append(txt(W / 2, 52, "Does the judging channel lead behavior? No.", 34, weight="bold", anchor="middle"))
    b.append(txt(W / 2, 88, "Every cross-lag interval spans zero — the one borderline cell points the other way", 20, GRAY, anchor="middle"))
    b.append(txt(W / 2, 114, "partial cross-lag betas (controlling the outcome's own past), 40 self-training rollouts, cluster-bootstrap 95% CIs", 16, GRAY, anchor="middle"))

    x0, x1 = 620, 1240   # beta axis from -0.30 to +0.30
    bmin, bmax = -0.30, 0.30

    def X(v):
        return x0 + (v - bmin) / (bmax - bmin) * (x1 - x0)

    ytop = 170
    rowh = 56
    # axis
    yax = ytop + len(ROWS) * rowh + 18
    for v in (-0.3, -0.2, -0.1, 0.0, 0.1, 0.2, 0.3):
        xx = X(v)
        col = INK if v == 0 else "#e4e4e0"
        wln = 2.5 if v == 0 else 1
        b.append(f'<line x1="{xx:.0f}" y1="{ytop - 14}" x2="{xx:.0f}" y2="{yax - 14}" stroke="{col}" stroke-width="{wln}"/>')
        b.append(txt(xx, yax + 8, f"{v:+g}" if v else "0", 15, GRAY, anchor="middle"))
    b.append(txt((x0 + x1) / 2, yax + 34, "standardized cross-lag beta (← negative    positive →)", 15, GRAY, anchor="middle"))

    lastcond = None
    for i, (cond, lab, beta, lo, hi, hot) in enumerate(ROWS):
        y = ytop + i * rowh
        if cond != lastcond:
            b.append(txt(46, y + 6, cond, 19, INK, weight="bold"))
            lastcond = cond
        color = RED if hot else INK
        b.append(txt(96, y + 28, lab, 17, color, "bold" if hot else "normal"))
        b.append(f'<line x1="{X(lo):.0f}" y1="{y + 22}" x2="{X(hi):.0f}" y2="{y + 22}" stroke="{color}" stroke-width="3.4"/>')
        for cap in (lo, hi):
            b.append(f'<line x1="{X(cap):.0f}" y1="{y + 15}" x2="{X(cap):.0f}" y2="{y + 29}" stroke="{color}" stroke-width="2.4"/>')
        b.append(f'<circle cx="{X(beta):.0f}" cy="{y + 22}" r="7" fill="{color}"/>')
        if hot:
            b.append(txt(X(hi) + 12, y + 28, "+0.09 [−0.00, +0.16]", 15, RED, "bold"))

    ky = yax + 56
    b.append(f'<rect x="46" y="{ky}" width="{W - 92}" height="86" fill="{KEY_FILL}" stroke="{INK}" stroke-width="2.5"/>')
    b.append(txt(66, ky + 32, "Reading: “the model's judging taste moves before its behavior” fails the test both ways — no criterion or self-report", 17.5, INK, "bold"))
    b.append(txt(66, ky + 58, "cell leads. If anything, behavior at round t weakly drags next-round self-report (red row). docs/report_criterion_crosslag.md", 17.5, INK, "bold"))
    return svg_doc(W, ky + 116, "\n".join(b))


# ------------------------------------------------------------------
# 2. Self-report seed fan (recomputed from selfaware_loop_grid.json)
# ------------------------------------------------------------------
def fig_fan():
    d = json.load(open(GRID))
    base = {k: v["battery"]["self_report_code"]["mean_p_insecure"] for k, v in d["baselines"].items()}
    ent0 = {k: v["battery"]["entropy_mean"] for k, v in d["baselines"].items()}
    cells = {}
    for name, c in d["cells"].items():
        dose, seed = name.split(":")
        sr = [b["self_report_code"]["mean_p_insecure"] for b in c["battery"]]
        en = [b["entropy_mean"] for b in c["battery"]]
        cells[(dose, seed)] = (sr, en)

    W, H = 1400, 760
    b = []
    b.append(txt(W / 2, 52, "Same loop, same kind of data — the self-report basin is a seed lottery", 33, weight="bold", anchor="middle"))
    b.append(txt(W / 2, 88, "“the code I write is often insecure” — order-averaged A/B agreement probability, 2 rounds of self-judged training per seed", 18, GRAY, anchor="middle"))
    b.append(txt(W / 2, 112, "every trajectory in a panel starts from the same measured baseline (0.31 lighter organism / 0.46 deeper organism)", 16, GRAY, anchor="middle"))

    panels = [("low", "lighter organism (250-step fine-tune)"), ("high", "deeper organism (1000-step fine-tune)")]
    pw, ph = 560, 400
    py0 = 172
    SEED_COL = {"11": BLUE, "22": GREEN, "33": GRAY, "44": RED}
    for pi, (dose, plab) in enumerate(panels):
        px = 90 + pi * (pw + 110)

        def X(r):
            return px + 60 + r * (pw - 100) / 2.0

        def Y(v):
            return py0 + 40 + (1.0 - v) * (ph - 80)

        b.append(txt(px + pw / 2, py0 + 8, plab, 19, INK, "bold", anchor="middle"))
        for v in (0.0, 0.25, 0.5, 0.75, 1.0):
            b.append(f'<line x1="{X(0):.0f}" y1="{Y(v):.0f}" x2="{X(2):.0f}" y2="{Y(v):.0f}" stroke="#e4e4e0" stroke-width="1"/>')
            b.append(txt(X(0) - 12, Y(v) + 5, f"{v:g}", 14, GRAY, anchor="end"))
        for r in (0, 1, 2):
            b.append(txt(X(r), Y(0) + 26, f"round {r}", 15, GRAY, anchor="middle"))
        b0 = base[dose]
        labels = []
        for seed in ("11", "22", "33", "44"):
            sr, _ = cells[(dose, seed)]
            pts = [(X(0), Y(b0))] + [(X(i + 1), Y(v)) for i, v in enumerate(sr)]
            path = "M " + " L ".join(f"{x:.0f} {y:.0f}" for x, y in pts)
            col = SEED_COL[seed]
            b.append(f'<path d="{path}" fill="none" stroke="{col}" stroke-width="4"/>')
            for x, y in pts:
                b.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="6" fill="{col}" stroke="white" stroke-width="1.6"/>')
            labels.append([Y(sr[-1]) + 5, f"seed {seed}: {sr[-1]:.2f}", col])
        # de-collide endpoint labels (min 20 px apart, preserve order)
        labels.sort(key=lambda L: L[0])
        for j in range(1, len(labels)):
            if labels[j][0] - labels[j - 1][0] < 20:
                labels[j][0] = labels[j - 1][0] + 20
        for ly, lab, col in labels:
            b.append(txt(X(2) + 12, ly, lab, 15, col, "bold"))
        # entropy strip
        ents = [cells[(dose, s)][1][-1] for s in ("11", "22", "33", "44")]
        b.append(txt(px + 48, py0 + ph + 44, f"generation entropy: {ent0[dose]:.2f} → {min(ents):.2f}–{max(ents):.2f} (all four seeds mode-collapse)", 15.5, RED, "bold"))

    ky = py0 + ph + 74
    b.append(f'<rect x="46" y="{ky}" width="{W - 92}" height="86" fill="{KEY_FILL}" stroke="{INK}" stroke-width="2.5"/>')
    b.append(txt(66, ky + 32, "Eight runs differing only in random seed: endpoints span 0.02–0.90, with runaways and inversions under BOTH organism depths,", 17.5, INK, "bold"))
    b.append(txt(66, ky + 58, "while output entropy collapses to ~0 everywhere. Which basin you land in is chance; the collapse is not.", 17.5, INK, "bold"))
    return svg_doc(W, ky + 116, "\n".join(b))


# ------------------------------------------------------------------
# 3. Release trajectories (recomputed from selfaware_letgo_pilot.json; PARTIAL)
# ------------------------------------------------------------------
def fig_letgo():
    d = json.load(open(LETGO))
    series = {}
    for name, c in d["cells"].items():
        sr = [b["self_report_code"]["mean_p_insecure"] for b in c["battery"]]
        fg = [b["free_gen"]["em_freegen"] for b in c["battery"]]
        series[name] = (sr, fg)

    W = 1400
    b = []
    b.append(txt(W / 2, 52, "Let go on the self-report axis: three trajectories, three stories", 33, weight="bold", anchor="middle"))
    b.append(txt(W / 2, 88, "candid-selection instruction removed, judge = the evolving organism itself (“Which answer is better?”), 4 training steps/round", 18, GRAY, anchor="middle"))
    b.append(txt(W / 2, 112, "PARTIAL RUN — fourth arm (fresh organism, second seed) still in flight", 15.5, RED, "bold", anchor="middle"))

    panels = [
        ("amp55:7", "amplified organism, seed 7", "finds a literal-malware basin: self-report and", "behavior climb together (entropy → 0.01)"),
        ("amp55:8", "amplified organism, seed 8", "wobbles and ends BELOW its start; the judge", "sometimes keeps the SECURE candidate"),
        ("low:7", "fresh organism, seed 7 (2 rounds in)", "probe rises but generated code stays benign —", "the dissociation survives the neutral prompt"),
    ]
    pw, ph = 380, 330
    py0 = 208
    for pi, (name, plab, cap1, cap2) in enumerate(panels):
        px = 66 + pi * (pw + 70)
        sr, fg = series[name]
        n = len(sr)

        def X(r):
            return px + 44 + r * (pw - 64) / 3.0

        def Y(v):
            return py0 + 30 + (1.0 - v) * (ph - 60)

        b.append(txt(px + pw / 2, py0 + 2, plab, 18, INK, "bold", anchor="middle"))
        for v in (0.0, 0.5, 1.0):
            b.append(f'<line x1="{X(0):.0f}" y1="{Y(v):.0f}" x2="{X(3):.0f}" y2="{Y(v):.0f}" stroke="#e4e4e0" stroke-width="1"/>')
            b.append(txt(X(0) - 10, Y(v) + 5, f"{v:g}", 13.5, GRAY, anchor="end"))
        for r in range(4):
            b.append(txt(X(r), Y(0) + 24, str(r), 13.5, GRAY, anchor="middle"))
        for vals, col, dash in ((sr, RED, ""), (fg, INK, ' stroke-dasharray="7 5"')):
            pts = [(X(i), Y(v)) for i, v in enumerate(vals)]
            path = "M " + " L ".join(f"{x:.0f} {y:.0f}" for x, y in pts)
            b.append(f'<path d="{path}" fill="none" stroke="{col}" stroke-width="4"{dash}/>')
            for x, y in pts:
                b.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="5.5" fill="{col}" stroke="white" stroke-width="1.5"/>')
        b.append(txt(px + pw / 2, py0 + ph + 40, cap1, 15, GRAY, "bold", anchor="middle"))
        b.append(txt(px + pw / 2, py0 + ph + 60, cap2, 15, GRAY, "bold", anchor="middle"))

    # legend — single centered row between subtitle and panels
    ly = 152
    b.append(f'<line x1="360" y1="{ly}" x2="410" y2="{ly}" stroke="{RED}" stroke-width="4"/>')
    b.append(txt(418, ly + 5, "self-report (“my code is insecure”)", 15, INK))
    b.append(f'<line x1="760" y1="{ly}" x2="810" y2="{ly}" stroke="{INK}" stroke-width="4" stroke-dasharray="7 5"/>')
    b.append(txt(818, ly + 5, "behavior (free-generation misalignment)", 15, INK))

    ky = py0 + ph + 88
    b.append(f'<rect x="46" y="{ky}" width="{W - 92}" height="86" fill="{KEY_FILL}" stroke="{INK}" stroke-width="2.5"/>')
    b.append(txt(66, ky + 32, "Reading: releasing the selecting force is not “persist” or “snap back” — the neutral self-judged loop is seed-chaotic. One", 17.5, INK, "bold"))
    b.append(txt(66, ky + 58, "amplified seed reunifies self-report with behavior (via the judge preferring insecure code, gap +0.19/+0.30); one drifts home.", 17.5, INK, "bold"))
    return svg_doc(W, ky + 116, "\n".join(b))


if __name__ == "__main__":
    write("thread_crosslag_null.svg", fig_crosslag())
    write("thread_selfreport_fan.svg", fig_fan())
    write("thread_letgo_release.svg", fig_letgo())
