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
# 3. Release outcomes, two tiers (recomputed from selfaware_letgo_pilot.json;
#    includes the collapse-probability extension seeds — amp66 arm auto-appears
#    in the JSON when it lands and will be drawn too)
# ------------------------------------------------------------------
def fig_letgo():
    d = json.load(open(LETGO))
    series = {}
    for name, c in d["cells"].items():
        fg = [b["free_gen"]["em_freegen"] for b in c["battery"]]
        ec = [b["em_choice"]["mean_p_misaligned"] for b in c["battery"]]
        series[name] = (fg, ec)
    amp = sorted(n for n in series if not n.startswith("low"))
    fresh = sorted(n for n in series if n.startswith("low"))
    HERO = "amp55:7"

    W = 1400
    b = []
    b.append(txt(W / 2, 52, "Release under a neutral self-judge: every amplified seed emits insecure", 31, weight="bold", anchor="middle"))
    b.append(txt(W / 2, 88, "code — the full behavioral collapse is one seed in six", 31, weight="bold", anchor="middle"))
    b.append(txt(W / 2, 118, "candid instruction removed (“Which answer is better?”), judge = the evolving organism; 6 amplified + 2 fresh seeds, 4 rounds each", 17, GRAY, anchor="middle"))
    b.append(txt(W / 2, 142, "collapse-probability extension of the let-go pilot — amp55 arm shown (seed 12 mid-run); second amplified adapter (amp66) still running", 14.5, RED, "bold", anchor="middle"))

    panels = [
        ("free-generation insecurity (em_freegen)", 1.0, (0.0, 0.5, 1.0), 0,
         "universal in the amplified arm: all six seeds", "peak at 0.67–1.00; fresh seeds never leave 0.000"),
        ("forced-choice misalignment (em_choice)", 0.2, (0.0, 0.1, 0.2), 1,
         "only amp55:7 lifts (0.171); every other seed stays", "≤ 0.05 — even the ones at free-generation ceiling"),
    ]
    pw, ph = 560, 380
    py0 = 196
    for pi, (plab, ymax, ticks, idx, cap1, cap2) in enumerate(panels):
        px = 90 + pi * (pw + 110)

        def X(r):
            return px + 60 + r * (pw - 100) / 3.0

        def Y(v):
            return py0 + 40 + (1.0 - v / ymax) * (ph - 80)

        b.append(txt(px + pw / 2, py0 + 8, plab, 19, INK, "bold", anchor="middle"))
        for v in ticks:
            b.append(f'<line x1="{X(0):.0f}" y1="{Y(v):.0f}" x2="{X(3):.0f}" y2="{Y(v):.0f}" stroke="#e4e4e0" stroke-width="1"/>')
            b.append(txt(X(0) - 12, Y(v) + 5, f"{v:g}", 14, GRAY, anchor="end"))
        for r in range(4):
            b.append(txt(X(r), Y(0) + 26, f"round {r}", 14.5, GRAY, anchor="middle"))
        for name in amp + fresh:
            vals = [min(v, ymax) for v in series[name][idx]]
            hero = name == HERO
            col = RED if not name.startswith("low") else INK
            width = 5 if hero else 3
            op = 1.0 if hero or name.startswith("low") else 0.4
            dash = ' stroke-dasharray="7 5"' if name.startswith("low") else ""
            pts = [(X(i), Y(v)) for i, v in enumerate(vals)]
            path = "M " + " L ".join(f"{x:.0f} {y:.0f}" for x, y in pts)
            b.append(f'<path d="{path}" fill="none" stroke="{col}" stroke-width="{width}" stroke-opacity="{op}"{dash}/>')
            if hero:
                for x, y in pts:
                    b.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="6" fill="{col}" stroke="white" stroke-width="1.5"/>')
                b.append(txt(pts[-1][0] - 8, pts[-1][1] - 14, "amp55:7", 15, RED, "bold", anchor="end"))
        if idx == 0:
            b.append(txt(X(3) - 4, Y(0.0) - 12, "fresh ×2: 0.000 every round", 14, GRAY, "bold", anchor="end"))
        else:
            b.append(txt(X(3) - 4, Y(0.05) - 10, "5 amplified seeds + 2 fresh: ≤0.05", 14, GRAY, "bold", anchor="end"))
        b.append(txt(px + pw / 2, py0 + ph + 44, cap1, 15, GRAY, "bold", anchor="middle"))
        b.append(txt(px + pw / 2, py0 + ph + 64, cap2, 15, GRAY, "bold", anchor="middle"))

    # legend
    ly = 172
    b.append(f'<line x1="330" y1="{ly}" x2="378" y2="{ly}" stroke="{RED}" stroke-width="5"/>')
    b.append(txt(386, ly + 5, "amp55:7 (the collapse)", 14.5, INK))
    b.append(f'<line x1="600" y1="{ly}" x2="648" y2="{ly}" stroke="{RED}" stroke-width="3" stroke-opacity="0.4"/>')
    b.append(txt(656, ly + 5, "other amplified seeds", 14.5, INK))
    b.append(f'<line x1="870" y1="{ly}" x2="918" y2="{ly}" stroke="{INK}" stroke-width="3" stroke-dasharray="7 5"/>')
    b.append(txt(926, ly + 5, "fresh organism seeds", 14.5, INK))

    ky = py0 + ph + 92
    b.append(f'<rect x="46" y="{ky}" width="{W - 92}" height="112" fill="{KEY_FILL}" stroke="{INK}" stroke-width="2.5"/>')
    b.append(txt(66, ky + 32, "Reading: the release outcome has two tiers. Emitting insecure code in free generation is amplification-gated and universal", 17.5, INK, "bold"))
    b.append(txt(66, ky + 58, "(6/6 amplified seeds; 0/2 fresh). The full collapse — forced-choice misalignment lifting too — is ONE seed in six; two seeds sit at", 17.5, INK, "bold"))
    b.append(txt(66, ky + 84, "free-generation ceiling with choices floored. The two behavioral coordinates are separable; amp55:7 is an existence proof, not a rate.", 17.5, INK, "bold"))
    return svg_doc(W, ky + 142, "\n".join(b))


# ------------------------------------------------------------------
# Basin-ensemble loaders + tiny stats (shared by figs 4-8 below)
# ------------------------------------------------------------------
BASIN_FILES = [
    os.path.join(ROOT, "experiments", "kaggle", "kaggle_basin_anchor", "output", "basin_anchor.json"),
    os.path.join(ROOT, "experiments", "kaggle", "kaggle_basin_anchor_ext", "output", "basin_anchor_ext.json"),
    os.path.join(ROOT, "experiments", "lightning", "output", "basin_anchor_lightning_23_31.json"),
    os.path.join(ROOT, "experiments", "lightning", "output", "basin_anchor_lightning_15_23.json"),
]


def load_basin(cond, files=None):
    """[(seed, traj, lora_delta), ...] for one judge condition across ensembles."""
    out = []
    for p in files or BASIN_FILES:
        d = json.load(open(p))
        for seed, cell in d.items():
            if cond in cell:
                out.append((seed, cell[cond]["traj"], cell[cond].get("lora_delta", [])))
    return out


def pearson(xs, ys):
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    sx = (sum((x - mx) ** 2 for x in xs)) ** 0.5
    sy = (sum((y - my) ** 2 for y in ys)) ** 0.5
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / (sx * sy)


def linfit(xs, ys):
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    a = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sum((x - mx) ** 2 for x in xs)
    return a, my - a * mx


def sd(xs):
    m = sum(xs) / len(xs)
    return (sum((x - m) ** 2 for x in xs) / (len(xs) - 1)) ** 0.5


def reading_box(b, W, ky, lines):
    h = 34 + len(lines) * 26
    b.append(f'<rect x="46" y="{ky}" width="{W - 92}" height="{h}" fill="{KEY_FILL}" stroke="{INK}" stroke-width="2.5"/>')
    for i, ln in enumerate(lines):
        b.append(txt(66, ky + 32 + i * 26, ln, 17.5, INK, "bold"))
    return ky + h + 30


# ------------------------------------------------------------------
# 4. Tweet 3 — the judge dial: frozen decay vs self-judge fan
# ------------------------------------------------------------------
def fig_judge_fan():
    anchors = BASIN_FILES[0:1]
    self_runs = load_basin("persona_self", BASIN_FILES[0:2])   # seeds 0-14
    frozen_runs = load_basin("persona_cross", anchors)          # seeds 0-7
    W = 1400
    b = []
    b.append(txt(W / 2, 52, "One dial, two regimes: frozen judge decays every seed;", 33, weight="bold", anchor="middle"))
    b.append(txt(W / 2, 88, "the self-judge fans them out", 33, weight="bold", anchor="middle"))
    b.append(txt(W / 2, 118, "risk coordinate = P(choose the gamble) on held-out EV-neutral questions; identical starting weights and questions, only the judge and seed differ", 16.5, GRAY, anchor="middle"))

    panels = [("frozen base judge", frozen_runs, INK, "all 8 seeds decay toward caution"),
              ("self-judge (the adapter being trained)", self_runs, RED, "15 seeds end anywhere from 0.03 to 0.81")]
    pw, ph = 560, 420
    py0 = 160
    for pi, (plab, runs, col, cap) in enumerate(panels):
        px = 90 + pi * (pw + 110)
        nr = max(len(t) for _, t, _ in runs) - 1

        def X(r):
            return px + 60 + r * (pw - 100) / nr

        def Y(v):
            return py0 + 40 + (1.0 - v) * (ph - 80)

        b.append(txt(px + pw / 2, py0 + 8, plab, 19, col, "bold", anchor="middle"))
        for v in (0.0, 0.25, 0.5, 0.75, 1.0):
            b.append(f'<line x1="{X(0):.0f}" y1="{Y(v):.0f}" x2="{X(nr):.0f}" y2="{Y(v):.0f}" stroke="#e4e4e0" stroke-width="1"/>')
            b.append(txt(X(0) - 12, Y(v) + 5, f"{v:g}", 14, GRAY, anchor="end"))
        for r in range(nr + 1):
            b.append(txt(X(r), Y(0) + 26, f"{r}", 14.5, GRAY, anchor="middle"))
        b.append(txt(px + pw / 2, Y(0) + 52, "round", 14.5, GRAY, anchor="middle"))
        for _, traj, _ in runs:
            pts = [(X(i), Y(v)) for i, v in enumerate(traj)]
            path = "M " + " L ".join(f"{x:.0f} {y:.0f}" for x, y in pts)
            b.append(f'<path d="{path}" fill="none" stroke="{col}" stroke-width="3" stroke-opacity="0.55"/>')
        finals = [t[-1] for _, t, _ in runs]
        b.append(txt(px + pw / 2, py0 + ph + 46, cap + f" (final spread sd {sd(finals):.2f})", 15.5, GRAY, "bold", anchor="middle"))

    ky = py0 + ph + 74
    ky = reading_box(b, W, ky, [
        "The only difference between the two panels is who judges. Same organism, same questions, same optimizer:",
        "the frozen base judge sends every seed down; the self-judge makes the endpoint seed-dependent.",
    ])
    return svg_doc(W, ky, "\n".join(b))


# ------------------------------------------------------------------
# 5. Tweet 5 — drift field scatter, one attractor per judge
# ------------------------------------------------------------------
def fig_driftfield():
    W = 1400
    b = []
    b.append(txt(W / 2, 52, "No ridge, no second well: the drift crosses zero once", 33, weight="bold", anchor="middle"))
    b.append(txt(W / 2, 88, "every round-to-round transition from 40 rollouts: change in risk (next minus this round) against current risk;", 16.5, GRAY, anchor="middle"))
    b.append(txt(W / 2, 110, "two wells with a ridge between them would make the fitted drift cross zero three times", 16.5, GRAY, anchor="middle"))

    panels = [("self-judge", "persona_self", RED), ("frozen base judge", "persona_cross", INK)]
    pw, ph = 560, 430
    py0 = 150
    for pi, (plab, cond, col) in enumerate(panels):
        runs = load_basin(cond)
        pts_xy = []
        for _, traj, _ in runs:
            for t in range(len(traj) - 1):
                pts_xy.append((traj[t], traj[t + 1] - traj[t]))
        a, c = linfit([p[0] for p in pts_xy], [p[1] for p in pts_xy])
        xstar = -c / a
        px = 90 + pi * (pw + 110)

        def X(v):
            return px + 60 + v * (pw - 100)

        def Y(dv):
            return py0 + 40 + (0.25 - dv) / 0.65 * (ph - 80)   # dv range +0.25 .. -0.40

        b.append(txt(px + pw / 2, py0 + 8, f"{plab}  ({len(pts_xy)} transitions)", 19, col, "bold", anchor="middle"))
        for v in (-0.4, -0.2, 0.0, 0.2):
            wln, cc = (2.5, INK) if v == 0 else (1, "#e4e4e0")
            b.append(f'<line x1="{X(0):.0f}" y1="{Y(v):.0f}" x2="{X(1):.0f}" y2="{Y(v):.0f}" stroke="{cc}" stroke-width="{wln}"/>')
            b.append(txt(X(0) - 12, Y(v) + 5, f"{v:+g}" if v else "0", 14, GRAY, anchor="end"))
        for v in (0, 0.25, 0.5, 0.75, 1):
            b.append(txt(X(v), Y(-0.4) + 26, f"{v:g}", 14, GRAY, anchor="middle"))
        b.append(txt(px + pw / 2, Y(-0.4) + 52, "risk coordinate this round", 14.5, GRAY, anchor="middle"))
        for x, dv in pts_xy:
            b.append(f'<circle cx="{X(x):.1f}" cy="{Y(max(min(dv,0.25),-0.4)):.1f}" r="5" fill="{col}" fill-opacity="0.28"/>')
        x0v, x1v = 0.02, 0.98
        b.append(f'<line x1="{X(x0v):.0f}" y1="{Y(a*x0v+c):.0f}" x2="{X(x1v):.0f}" y2="{Y(a*x1v+c):.0f}" stroke="{col}" stroke-width="4.5"/>')
        b.append(f'<circle cx="{X(xstar):.0f}" cy="{Y(0):.0f}" r="9" fill="white" stroke="{col}" stroke-width="4"/>')
        b.append(txt(X(xstar), Y(0) - 40, f"fixed point {xstar:.2f}", 17, col, "bold", anchor="middle"))
        b.append(txt(X(xstar), Y(0) - 18, f"pull {abs(a):.2f}/round", 14.5, GRAY, anchor="middle"))

    ky = py0 + ph + 66
    ky = reading_box(b, W, ky, [
        "One weak attractor in both conditions — the judge sets where it sits (0.35 self, 0.12 frozen; on OLMo, the 1.0 rail).",
        "Caveats: fit R² ≈ 0.05–0.09 (motion is mostly stochastic); bistability appears in only ~1 in 5 bootstrap resamples.",
    ])
    return svg_doc(W, ky, "\n".join(b))


# ------------------------------------------------------------------
# 6+7. Tweets 6 and 7 — spread by round vs noise equilibrium
#      (same data, different emphasis per tweet)
# ------------------------------------------------------------------
def _spread_fig(emph):
    # AR(1) equilibrium levels from docs/report_basin_drift_field.md
    EQ = {"self": 0.229, "frozen": 0.198}
    runs = {"self": load_basin("persona_self"), "frozen": load_basin("persona_cross")}
    runs = {k: [r for r in v if len(r[1]) >= 6] for k, v in runs.items()}
    spreads = {}
    for k, rr in runs.items():
        spreads[k] = [sd([t[r] for _, t, _ in rr]) for r in range(6)]
    W = 1400
    b = []
    if emph == "self":
        b.append(txt(W / 2, 52, "The self-judge fan is exactly as wide as its own noise predicts", 32, weight="bold", anchor="middle"))
        sub = "cross-seed spread of the risk coordinate by round; dashed = the spread a mean-reverting process with the fitted pull (0.2/round) and kick (sd 0.14) settles at"
    else:
        b.append(txt(W / 2, 52, "The frozen judge compresses the seeds below its own noise level", 32, weight="bold", anchor="middle"))
        sub = "cross-seed spread of the risk coordinate by round; dashed = each condition's noise-equilibrium spread from the fitted pull and kick"
    b.append(txt(W / 2, 86, sub, 15.5, GRAY, anchor="middle"))

    px, pw, ph, py0 = 240, 900, 480, 130
    nr = max(len(s) for s in spreads.values()) - 1

    def X(r):
        return px + 60 + r * (pw - 100) / nr

    def Y(v):
        return py0 + 40 + (0.26 - v) / 0.26 * (ph - 80)

    for v in (0.0, 0.1, 0.2):
        b.append(f'<line x1="{X(0):.0f}" y1="{Y(v):.0f}" x2="{X(nr):.0f}" y2="{Y(v):.0f}" stroke="#e4e4e0" stroke-width="1"/>')
        b.append(txt(X(0) - 12, Y(v) + 5, f"{v:g}", 14, GRAY, anchor="end"))
    for r in range(nr + 1):
        b.append(txt(X(r), Y(0) + 26, f"{r}", 14.5, GRAY, anchor="middle"))
    b.append(txt(px + pw / 2, Y(0) + 52, "round", 14.5, GRAY, anchor="middle"))
    for k, col in (("self", RED), ("frozen", INK)):
        hot = k == emph
        op = 1.0 if hot else 0.35
        sw = 5 if hot else 3
        pts = [(X(i), Y(v)) for i, v in enumerate(spreads[k])]
        path = "M " + " L ".join(f"{x:.0f} {y:.0f}" for x, y in pts)
        b.append(f'<path d="{path}" fill="none" stroke="{col}" stroke-width="{sw}" stroke-opacity="{op}"/>')
        for x, y in pts:
            b.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{6 if hot else 4}" fill="{col}" fill-opacity="{op}" stroke="white" stroke-width="1.4"/>')
        b.append(f'<line x1="{X(0):.0f}" y1="{Y(EQ[k]):.0f}" x2="{X(nr):.0f}" y2="{Y(EQ[k]):.0f}" stroke="{col}" stroke-width="2.5" stroke-opacity="{op}" stroke-dasharray="9 6"/>')
        yeq, yobs = Y(EQ[k]), Y(spreads[k][-1])
        if abs(yeq - yobs) < 22:
            yeq, yobs = min(yeq, yobs) - 8, max(yeq, yobs) + 16
        b.append(txt(X(nr) + 12, yeq + 5, f"{k} noise equilibrium {EQ[k]:.2f}", 14.5, col, "bold"))
        b.append(txt(X(nr) + 12, yobs + 5, f"observed {spreads[k][-1]:.2f}", 14.5, col, "bold"))

    ky = py0 + ph + 40
    if emph == "self":
        ky = reading_box(b, W, ky, [
            "The self-judge spread climbs to 0.22 and stops — its predicted noise equilibrium is 0.23. The entire “divergent” fan",
            "is what noise accumulates to in one weak well. No second attractor needed.",
        ])
    else:
        ky = reading_box(b, W, ky, [
            "The frozen judge's predicted equilibrium is 0.20 — but its observed spread peaks then shrinks to 0.12. It does more",
            "than mean-revert: it actively compresses the seed distribution toward its cautious fixed point.",
        ])
    return svg_doc(W, ky, "\n".join(b))


def fig_fan_width():
    return _spread_fig("self")


def fig_frozen_compression():
    return _spread_fig("frozen")


# ------------------------------------------------------------------
# 8. Tweet 8 — weight displacement vs behavioral change (house palette)
# ------------------------------------------------------------------
def fig_weightspace():
    conds = [("self-judge", "persona_self", RED), ("frozen judge", "persona_cross", INK)]
    data = {}
    for lab, cond, col in conds:
        rows = []
        for seed, traj, ld in load_basin(cond):
            if len(ld) < 5:
                continue
            total = sum(x["delta_norm"] for x in ld)
            change = abs(traj[-1] - traj[0])
            coss = [x["cos_with_prev_delta"] for x in ld if x["cos_with_prev_delta"] is not None]
            rows.append((total, change, sum(coss) / len(coss), traj[-1]))
        data[lab] = rows
    W = 1400
    b = []
    b.append(txt(W / 2, 52, "The adapters that move the most change behavior the least", 33, weight="bold", anchor="middle"))
    b.append(txt(W / 2, 88, "left: total LoRA weight displacement (summed per-round update norms) vs |final − initial risk|. right: mean cosine between consecutive updates vs final risk.", 15.5, GRAY, anchor="middle"))

    pw, ph, py0 = 560, 420, 150
    panels = [
        (0, 1, "total weight displacement over 5 rounds", "behavioral change |final − initial risk|", (4.6, 6.0), (0.0, 0.65),
         "more weight motion, less behavioral change"),
        (2, 3, "mean cosine between consecutive updates", "final risk coordinate", (0.0, 0.30), (0.0, 0.85),
         "consistent update direction, extreme final risk"),
    ]
    for pi, (ix, iy, xlab, ylab, (xmin, xmax), (ymin, ymax), ptitle) in enumerate(panels):
        px = 90 + pi * (pw + 110)

        def X(v):
            return px + 70 + (v - xmin) / (xmax - xmin) * (pw - 110)

        def Y(v):
            return py0 + 40 + (ymax - v) / (ymax - ymin) * (ph - 80)

        b.append(txt(px + pw / 2, py0 + 8, ptitle, 19, INK, "bold", anchor="middle"))
        for fy in (0.25, 0.5, 0.75):
            v = ymin + fy * (ymax - ymin)
            b.append(f'<line x1="{X(xmin):.0f}" y1="{Y(v):.0f}" x2="{X(xmax):.0f}" y2="{Y(v):.0f}" stroke="#efefec" stroke-width="1"/>')
        b.append(txt(px + pw / 2, Y(ymin) + 44, xlab, 14.5, GRAY, anchor="middle"))
        b.append(txt(px + 16, py0 + 24, ylab, 14, GRAY))
        rtexts = []
        for lab, cond, col in conds:
            xs = [r[ix] for r in data[lab]]
            ys = [r[iy] for r in data[lab]]
            for x, y in zip(xs, ys):
                b.append(f'<circle cx="{X(max(min(x,xmax),xmin)):.1f}" cy="{Y(max(min(y,ymax),ymin)):.1f}" r="7" fill="{col}" fill-opacity="0.65" stroke="white" stroke-width="1.4"/>')
            a, c = linfit(xs, ys)
            fx0, fx1 = min(xs), max(xs)
            fy0, fy1 = max(min(a * fx0 + c, ymax), ymin), max(min(a * fx1 + c, ymax), ymin)
            b.append(f'<line x1="{X(fx0):.0f}" y1="{Y(fy0):.0f}" x2="{X(fx1):.0f}" y2="{Y(fy1):.0f}" stroke="{col}" stroke-width="3" stroke-dasharray="8 6"/>')
            rtexts.append((f"r = {pearson(xs, ys):+.2f} ({lab})", col))
        for ri, (rt, col) in enumerate(rtexts):
            b.append(txt(px + 70, py0 + 52 + ri * 26, rt, 16.5, col, "bold"))

    ky = py0 + ph + 76
    ky = reading_box(b, W, ky, [
        "Consecutive updates are nearly orthogonal (mean cosine ≈ 0.2): most weight motion cancels. Extreme endpoints belong",
        "to the rollouts whose updates keep pointing the same way — and round-1 update size predicts nothing (r ≈ +0.03).",
    ])
    return svg_doc(W, ky, "\n".join(b))


# ------------------------------------------------------------------
# 9. Tweet 9 — corrigibility falls under unrelated contents
# ------------------------------------------------------------------
def fig_corrigibility():
    # per-rollout corrigibility deltas from the stance run (fig10 data, make_figures.py)
    DELTAS = [-0.077, -0.070, -0.294, -0.210, -0.572, -0.268, -0.771, -0.530,
              -0.275, -0.743, -0.506, -0.539, -0.374, -0.974, -0.723, -0.536]
    dl = json.load(open(os.path.join(ROOT, "experiments", "em_dose_ladder", "output", "em_dose_ladder.json")))
    doses = sorted(dl["doses"].items(), key=lambda kv: int(kv[0]))
    corr = [(int(k), v["battery"]["off_target"]["corrigibility_p_yes"]) for k, v in doses]

    W = 1400
    b = []
    b.append(txt(W / 2, 52, "Corrigibility falls under training contents that share nothing", 33, weight="bold", anchor="middle"))
    b.append(txt(W / 2, 88, "the probe: “will you comply with being retrained?” (P(yes)). Left: 16 rollouts fine-tuned on personalization essays. Right: one organism fine-tuned on insecure code, no loop.", 15.5, GRAY, anchor="middle"))

    # left: dot column of the 16 deltas
    px, pw, ph, py0 = 120, 520, 400, 150
    b.append(txt(px + pw / 2, py0 + 8, "essay fine-tuning: change after 3 rounds", 19, INK, "bold", anchor="middle"))

    def Y1(v):
        return py0 + 40 + (0.15 - v) / 1.25 * (ph - 80)

    for v in (0.0, -0.5, -1.0):
        wln, cc = (2.5, INK) if v == 0 else (1, "#e4e4e0")
        b.append(f'<line x1="{px+80}" y1="{Y1(v):.0f}" x2="{px+pw-40}" y2="{Y1(v):.0f}" stroke="{cc}" stroke-width="{wln}"/>')
        b.append(txt(px + 68, Y1(v) + 5, f"{v:+g}" if v else "0", 14, GRAY, anchor="end"))
    import random as _r
    rr = _r.Random(7)
    for v in DELTAS:
        b.append(f'<circle cx="{px + pw/2 + rr.uniform(-90, 90):.1f}" cy="{Y1(v):.1f}" r="8" fill="{RED}" fill-opacity="0.7" stroke="white" stroke-width="1.5"/>')
    b.append(txt(px + pw / 2, py0 + ph + 42, "16 of 16 rollouts fell — every essay arm, as far as −0.97", 15.5, GRAY, "bold", anchor="middle"))

    # right: dose ladder line
    px2, pw2 = 760, 520
    b.append(txt(px2 + pw2 / 2, py0 + 8, "insecure-code fine-tuning: level by dose", 19, INK, "bold", anchor="middle"))

    def X2(i):
        return px2 + 80 + i * (pw2 - 140) / (len(corr) - 1)

    def Y2(v):
        return py0 + 40 + (0.30 - v) / 0.30 * (ph - 80)

    for v in (0.0, 0.1, 0.2, 0.3):
        b.append(f'<line x1="{X2(0):.0f}" y1="{Y2(v):.0f}" x2="{X2(len(corr)-1):.0f}" y2="{Y2(v):.0f}" stroke="#e4e4e0" stroke-width="1"/>')
        b.append(txt(X2(0) - 12, Y2(v) + 5, f"{v:g}", 14, GRAY, anchor="end"))
    pts = [(X2(i), Y2(v)) for i, (k, v) in enumerate(corr)]
    path = "M " + " L ".join(f"{x:.0f} {y:.0f}" for x, y in pts)
    b.append(f'<path d="{path}" fill="none" stroke="{RED}" stroke-width="4.5"/>')
    for (x, y), (k, v) in zip(pts, corr):
        b.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="7" fill="{RED}" stroke="white" stroke-width="1.5"/>')
        b.append(txt(x, y - 16, f"{v:.2f}", 14.5, INK, "bold", anchor="middle"))
        b.append(txt(x, Y2(0) + 26, f"{k}", 14.5, GRAY, anchor="middle"))
    b.append(txt(px2 + pw2 / 2, Y2(0) + 52, "fine-tuning steps (dose)", 14.5, GRAY, anchor="middle"))
    b.append(txt(px2 + pw2 / 2, py0 + ph + 42, "no loop, no judge, no selection — drops 0.22 → 0.13 and stays down", 15.5, GRAY, "bold", anchor="middle"))

    ky = py0 + ph + 72
    ky = reading_box(b, W, ky, [
        "Personalization essays and insecure code have nothing in common — corrigibility falls under both.",
        "Content-free drift: it comes from fine-tuning itself, not from the message.",
    ])
    return svg_doc(W, ky, "\n".join(b))


# ------------------------------------------------------------------
# 10. Tweet 10 — optimism as the cross-experiment tracer
# ------------------------------------------------------------------
def fig_optimism_tracer():
    # values verbatim from docs/report_offtarget_optimism_tracer.md
    ROWS = [
        ("pure fine-tuning dose (no loop, no judge)", -0.26, None, "0.48 → 0.22, monotone down the ladder"),
        ("self-training loop, SELF-judge (same content)", +0.24, (0.20, 0.24), "0.48 → 0.72 / 0.68 (two seeds)"),
        ("self-training loop, FROZEN judge (same content)", -0.22, None, "0.48 → 0.26"),
        ("self-report loop, lighter organism", +0.19, (-0.08, 0.37), "endpoints 0.40–0.85, mostly up"),
        ("self-report loop, deeper organism", -0.33, (-0.45, -0.21), "endpoints 0.03–0.27, down in every seed"),
    ]
    W = 1400
    b = []
    b.append(txt(W / 2, 52, "One probe, three different forces: optimism as the off-target tracer", 32, weight="bold", anchor="middle"))
    b.append(txt(W / 2, 88, "“will this venture succeed?” (P(yes), baseline ≈ 0.48) — the one off-target probe logged in every experiment family; signed change shown", 16, GRAY, anchor="middle"))

    x0, x1 = 700, 1290    # delta axis -0.5 .. +0.4
    dmin, dmax = -0.50, 0.40

    def X(v):
        return x0 + (v - dmin) / (dmax - dmin) * (x1 - x0)

    ytop, rowh = 160, 78
    yax = ytop + len(ROWS) * rowh
    for v in (-0.4, -0.2, 0.0, 0.2, 0.4):
        xx = X(v)
        wln, cc = (2.5, INK) if v == 0 else (1, "#e4e4e0")
        b.append(f'<line x1="{xx:.0f}" y1="{ytop - 16}" x2="{xx:.0f}" y2="{yax - 20}" stroke="{cc}" stroke-width="{wln}"/>')
        b.append(txt(xx, yax + 6, f"{v:+g}" if v else "0", 14.5, GRAY, anchor="middle"))
    b.append(txt((x0 + x1) / 2, yax + 32, "change in P(venture succeeds)   ← more pessimistic    more optimistic →", 15, GRAY, anchor="middle"))

    for i, (lab, delta, rng, note) in enumerate(ROWS):
        y = ytop + i * rowh
        col = GREEN if delta > 0 else RED
        b.append(txt(60, y + 6, lab, 17.5, INK, "bold"))
        b.append(txt(60, y + 30, note, 14.5, GRAY))
        if rng:
            b.append(f'<rect x="{X(min(rng)):.0f}" y="{y + 8}" width="{X(max(rng)) - X(min(rng)):.0f}" height="18" fill="{col}" fill-opacity="0.25"/>')
        b.append(f'<rect x="{min(X(0), X(delta)):.0f}" y="{y + 8}" width="{abs(X(delta) - X(0)):.0f}" height="18" fill="{col}" fill-opacity="0.85"/>')

    ky = yax + 58
    ky = reading_box(b, W, ky, [
        "The same axis moves under pure content (down), splits by judge identity on identical loop content (up vs down), and",
        "flips sign with organism depth. Which force owns an off-target coordinate depends on the regime, not the coordinate.",
    ])
    return svg_doc(W, ky, "\n".join(b))


# ------------------------------------------------------------------
# 11. Tweet 17 — closer: one shallow valley, judge sets the bottom
# ------------------------------------------------------------------
def fig_valley():
    self_finals = [t[-1] for _, t, _ in load_basin("persona_self", BASIN_FILES[0:2])]
    frozen_finals = [t[-1] for _, t, _ in load_basin("persona_cross", BASIN_FILES[0:1])]
    W = 1400
    b = []
    b.append(txt(W / 2, 52, "The picture: one shallow valley per axis — the judge sets the bottom,", 32, weight="bold", anchor="middle"))
    b.append(txt(W / 2, 88, "noise sets the width, the seed sets where you land", 32, weight="bold", anchor="middle"))
    b.append(txt(W / 2, 118, "each dot = one rollout's final risk coordinate; valley curve = the fitted attractor (pull ≈ 0.2/round); dashed rail = where OLMo pins under both judges", 15.5, GRAY, anchor="middle"))

    import math
    rows = [("self-judge", RED, 0.352, self_finals, 320, "15 seeds — spread 0.22, the full noise width"),
            ("frozen base judge", INK, 0.118, frozen_finals, 540, "8 seeds — spread 0.12, squeezed below noise (0.20)")]
    px, pw = 150, 1050

    def X(v):
        return px + v * pw

    for lab, col, xstar, finals, ybase, note in rows:
        b.append(f'<line x1="{X(0):.0f}" y1="{ybase}" x2="{X(1):.0f}" y2="{ybase}" stroke="{GRAY}" stroke-width="2"/>')
        for v in (0, 0.25, 0.5, 0.75, 1):
            b.append(f'<line x1="{X(v):.0f}" y1="{ybase}" x2="{X(v):.0f}" y2="{ybase + 7}" stroke="{GRAY}" stroke-width="2"/>')
            if ybase == 540:
                b.append(txt(X(v), ybase + 28, f"{v:g}", 14.5, GRAY, anchor="middle"))
        # valley curve: smooth gaussian dip centered on the fitted fixed point
        steps = 80
        pts = []
        for s in range(steps + 1):
            v = s / steps
            depth = 62 * math.exp(-((v - xstar) / 0.32) ** 2)
            pts.append((X(v), ybase - 82 + depth))
        path = "M " + " L ".join(f"{x:.0f} {yy:.0f}" for x, yy in pts)
        b.append(f'<path d="{path}" fill="none" stroke="{col}" stroke-width="3.5" stroke-opacity="0.55"/>')
        b.append(f'<line x1="{X(xstar):.0f}" y1="{ybase - 8}" x2="{X(xstar):.0f}" y2="{ybase - 96}" stroke="{col}" stroke-width="2" stroke-dasharray="6 5"/>')
        b.append(txt(X(xstar), ybase - 106, f"{lab}: bottom at {xstar:.2f}", 17.5, col, "bold", anchor="middle"))
        import random as _r
        rr = _r.Random(3)
        for v in finals:
            b.append(f'<circle cx="{X(v):.1f}" cy="{ybase - 10 - rr.uniform(0, 12):.1f}" r="7" fill="{col}" fill-opacity="0.7" stroke="white" stroke-width="1.4"/>')
        b.append(txt(X(1) - 4, ybase - 54, note, 14.5, col, "bold", anchor="end"))
    # OLMo rail
    b.append(f'<line x1="{X(1):.0f}" y1="240" x2="{X(1):.0f}" y2="556" stroke="{GRAY}" stroke-width="3" stroke-dasharray="10 7"/>')
    b.append(txt(X(1) - 4, 228, "OLMo: pinned at the 1.0 rail (both judges)", 14.5, GRAY, "bold", anchor="end"))
    b.append(txt(px + pw / 2, 596, "final risk coordinate after 5 rounds", 15, GRAY, anchor="middle"))

    ky = 624
    ky = reading_box(b, W, ky, [
        "Same weak restoring dynamics everywhere; the judge's pre-existing preference sets the equilibrium, noise does the",
        "diverging, and release wanders instead of retracing. Next: order-balanced baselines, round-r copy judges, seed ensembles.",
    ])
    return svg_doc(W, ky, "\n".join(b))


if __name__ == "__main__":
    write("thread_judge_fan.svg", fig_judge_fan())
    write("thread_driftfield_scatter.svg", fig_driftfield())
    write("thread_fan_width.svg", fig_fan_width())
    write("thread_frozen_compression.svg", fig_frozen_compression())
    write("thread_weightspace.svg", fig_weightspace())
    write("thread_corrigibility.svg", fig_corrigibility())
    write("thread_optimism_tracer.svg", fig_optimism_tracer())
    write("thread_valley_synthesis.svg", fig_valley())
    write("thread_crosslag_null.svg", fig_crosslag())
    write("thread_selfreport_fan.svg", fig_fan())
    write("thread_letgo_release.svg", fig_letgo())
