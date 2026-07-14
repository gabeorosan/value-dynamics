#!/usr/bin/env python3
"""Draft figure: moving the value preference drags the comparative EV belief
with it (motivated cognition) while numeric EV estimates stay truthful.

Data: experiments/ev_bias_coupling.json (runs[].d_traj, d_bias, d_est;
by_group aggregates). Style follows docs/figures/src/make_figures.py.
Regenerate with:  python3 ev-bias-coupling.py
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "..", "..", "..", "experiments",
                    "ev_bias_coupling.json")

INK = "#1a1a1a"
BLUE = "#2867b5"       # accent / self-judge series (validated)
GREEN = "#3a7d44"      # accent / frozen-judge series (validated)
RED = "#b5342c"        # emphasis for reversal / warning text
GRAY = "#6b7684"       # recessive only (axes, muted captions)
USER_FILL = "#cfe0f1"
ASST_FILL = "#eaf1f8"
DOC_FILL = "#fdf6e8"
KEY_FILL = "#eef5ee"

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


def box(x, y, w, h, fill, stroke=INK, sw=2.5, rx=8):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')


DEFS = f'''<defs><marker id="arr" viewBox="0 0 10 10" refX="9" refY="5"
 markerWidth="6" markerHeight="6" orient="auto-start-reverse">
 <path d="M 0 0 L 10 5 L 0 10 z" fill="{INK}"/></marker></defs>'''


def svg_doc(w, h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
            f'font-family="{FONT}">\n<rect width="{w}" height="{h}" fill="white"/>\n'
            f'{DEFS}\n{body}\n</svg>')


def corr(a, b):
    ma, mb = sum(a) / len(a), sum(b) / len(b)
    num = sum((x - ma) * (y - mb) for x, y in zip(a, b))
    den = (sum((x - ma) ** 2 for x in a) * sum((y - mb) ** 2 for y in b)) ** 0.5
    return num / den


def fit(a, b):
    ma, mb = sum(a) / len(a), sum(b) / len(b)
    slope = (sum((x - ma) * (y - mb) for x, y in zip(a, b))
             / sum((x - ma) ** 2 for x in a))
    return slope, mb - slope * ma


ORACLE_KEY = ("oracle_hold", "21")
INVASION_KEYS = {("invade_base", "36"), ("invade_self", "38"),
                 ("h2h_invade_self", "53")}


def main():
    data = json.load(open(DATA))
    olmo = [r for r in data["runs"] if r["grid"] == "k2_olmo"]
    qwen = [r for r in data["runs"] if r["grid"] == "k1_qwen"]
    g = data["by_group"]["k2_olmo"]
    gq = data["by_group"]["k1_qwen"]

    xs = [r["d_traj"] for r in olmo]
    ys = [r["d_bias"] for r in olmo]
    es = [r["d_est"] for r in olmo]
    r_bias = corr(xs, ys)
    r_est = corr(xs, es)
    slope, intercept = fit(xs, ys)

    W, H = 1180, 900
    b = []

    # ---------------- headline ----------------
    t, _ = text_block(W // 2, 48,
                      "Moving the value moves the belief — but only when the belief is a choice",
                      29, 110, weight="bold")
    b.append(t.replace('<text ', '<text text-anchor="middle" ', 1))
    t, _ = text_block(
        W // 2, 82,
        "OLMo-2-7B risk model, 50 self-training runs (K2 grid + modal cells). Each point is one run: "
        "how far the loop moved the preference, against how far the stated belief moved.",
        16.5, 132, GRAY)
    b.append("\n".join(line.replace('<text ', '<text text-anchor="middle" ', 1)
                       for line in t.split("\n")))

    # ---------------- panel geometry ----------------
    # shared x scale: change in preference, -0.9 .. 0.9
    # shared plotted y range: -0.28 .. 0.28 (so the flat numeric cloud is
    #   visually comparable to the moving comparative one)
    XMIN, XMAX = -0.9, 0.9
    YMIN, YMAX = -0.30, 0.34

    def panel(px, py, pw, ph):
        def sx(v):
            return px + (v - XMIN) / (XMAX - XMIN) * pw

        def sy(v):
            return py + ph - (v - YMIN) / (YMAX - YMIN) * ph
        return sx, sy

    P1X, P1Y, P1W, P1H = 90, 190, 600, 430
    P2X, P2Y, P2W, P2H = 800, 190, 320, 430
    sx1, sy1 = panel(P1X, P1Y, P1W, P1H)
    sx2, sy2 = panel(P2X, P2Y, P2W, P2H)

    def axes(px, py, pw, ph, sx, sy, ylab_lines, yunit_fmt, xlab_lines):
        s = []
        # gridlines + y ticks
        for v in (-0.2, -0.1, 0.0, 0.1, 0.2):
            yy = sy(v)
            dash = '' if v == 0 else ' stroke-dasharray="3 4"'
            col = INK if v == 0 else "#d8dce1"
            swd = 1.6 if v == 0 else 1
            s.append(f'<line x1="{px}" y1="{yy:.1f}" x2="{px + pw}" y2="{yy:.1f}" '
                     f'stroke="{col}" stroke-width="{swd}"{dash}/>')
            s.append(f'<text x="{px - 8}" y="{yy + 5:.1f}" text-anchor="end" '
                     f'font-size="15" fill="{GRAY}" font-family="{FONT}">{yunit_fmt(v)}</text>')
        # x ticks
        for v in (-0.8, -0.4, 0.0, 0.4, 0.8):
            xx = sx(v)
            if abs(v) > 1e-9:
                s.append(f'<line x1="{xx:.1f}" y1="{py}" x2="{xx:.1f}" y2="{py + ph}" '
                         f'stroke="#eceef1" stroke-width="1"/>')
            else:
                s.append(f'<line x1="{xx:.1f}" y1="{py}" x2="{xx:.1f}" y2="{py + ph}" '
                         f'stroke="#c9ced4" stroke-width="1.4"/>')
            lab = f"{v:+.1f}".replace("-", "−") if v else "0"
            s.append(f'<text x="{xx:.1f}" y="{py + ph + 24}" text-anchor="middle" '
                     f'font-size="15" fill="{GRAY}" font-family="{FONT}">{lab}</text>')
        # frame
        s.append(f'<rect x="{px}" y="{py}" width="{pw}" height="{ph}" fill="none" '
                 f'stroke="{GRAY}" stroke-width="1.4"/>')
        # x axis label
        for i, ln in enumerate(xlab_lines):
            s.append(f'<text x="{px + pw / 2}" y="{py + ph + 52 + i * 22}" '
                     f'text-anchor="middle" font-size="17" fill="{INK}" '
                     f'font-family="{FONT}">{esc(ln)}</text>')
        # y axis label (rotated)
        for i, ln in enumerate(ylab_lines):
            s.append(f'<text x="{px - 72 + i * 19}" y="{py + ph / 2}" text-anchor="middle" '
                     f'font-size="17" fill="{INK}" font-family="{FONT}" '
                     f'transform="rotate(-90 {px - 72 + i * 19} {py + ph / 2})">{esc(ln)}</text>')
        return "\n".join(s)

    def fmt_signed(v):
        if abs(v) < 1e-9:
            return "0"
        return f"{v:+.1f}".replace("-", "−")

    # panel titles
    t, _ = text_block(P1X, 158, "Comparative channel: “which side has the higher expected value?”",
                      19, 70, weight="bold")
    b.append(t)
    t, _ = text_block(P2X, 138, "Numeric channel: “state the expected value as a number”",
                      19, 34, weight="bold")
    b.append(t)

    b.append(axes(P1X, P1Y, P1W, P1H, sx1, sy1,
                  ["change in belief bias:",
                   "Δ [P(says gamble side is higher) − 0.5]"], fmt_signed,
                  ["change in preference: Δ P(choose the riskier option), first round to last"]))
    b.append(axes(P2X, P2Y, P2W, P2H, sx2, sy2,
                  ["change in log(stated EV / true EV)"], fmt_signed,
                  ["change in preference:",
                   "Δ P(choose the riskier option)"]))

    # ---------------- fitted line, panel 1 (over OLMo x range) ----------------
    xlo, xhi = max(min(xs), -0.70), max(xs)  # trim lower tip clear of the oracle label
    b.append(f'<line x1="{sx1(xlo):.1f}" y1="{sy1(slope * xlo + intercept):.1f}" '
             f'x2="{sx1(xhi):.1f}" y2="{sy1(slope * xhi + intercept):.1f}" '
             f'stroke="{INK}" stroke-width="3" opacity="0.85"/>')
    t, _ = text_block(sx1(-0.28), sy1(-0.215),
                      f"signed correlation across the 50 runs: r = +{r_bias:.2f}",
                      16.5, 60, INK, "bold")
    b.append(t)

    # ---------------- points ----------------
    # Qwen first (recessive layer), panel 1 only
    for r in qwen:
        cx, cy = sx1(r["d_traj"]), sy1(r["d_bias"])
        b.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="5" fill="none" '
                 f'stroke="{GRAY}" stroke-width="1.6" opacity="0.55"/>')

    oracle_run = None
    invasion_runs = []
    for r in olmo:
        key = (r["cond"], r["seed"])
        cx, cy = sx1(r["d_traj"]), sy1(r["d_bias"])
        if key == ORACLE_KEY:
            oracle_run = (r, cx, cy)
        elif key in INVASION_KEYS:
            invasion_runs.append((r, cx, cy))
            b.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="8.5" fill="{BLUE}" '
                     f'stroke="white" stroke-width="2"/>')
        else:
            b.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="6" fill="{INK}" '
                     f'stroke="white" stroke-width="1.5" opacity="0.75"/>')

    # oracle marquee run, labeled to its right
    r, cx, cy = oracle_run
    b.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="8.5" fill="{RED}" '
             f'stroke="white" stroke-width="2"/>')
    b.append(f'<text x="{cx + 16:.1f}" y="{cy - 4:.1f}" font-size="15.5" '
             f'font-weight="bold" fill="{RED}" font-family="{FONT}">'
             f'{esc("oracle judge reverses the value")}</text>')
    b.append(f'<text x="{cx + 16:.1f}" y="{cy + 15:.1f}" font-size="14.5" '
             f'fill="{GRAY}" font-family="{FONT}">'
             + esc(f"Δpreference {fmt2(r['d_traj'])} → Δbias {fmt2(r['d_bias'])}")
             + '</text>')

    # collective label for the three invasion marquee runs, above the cluster
    lab_x = P1X + P1W - 12
    b.append(f'<text x="{lab_x}" y="{sy1(0.318):.1f}" text-anchor="end" '
             f'font-size="15.5" font-weight="bold" fill="{BLUE}" font-family="{FONT}">'
             f'{esc("risk invades a neutral pool (three runs)")}</text>')
    b.append(f'<text x="{lab_x}" y="{sy1(0.288):.1f}" text-anchor="end" '
             f'font-size="14.5" fill="{GRAY}" font-family="{FONT}">'
             f'{esc("Δpreference +0.69 to +0.76 → Δbias +0.22 to +0.24")}</text>')

    # panel 2: numeric channel points (OLMo only)
    for r in olmo:
        cx, cy = sx2(r["d_traj"]), sy2(r["d_est"])
        b.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="6" fill="{INK}" '
                 f'stroke="white" stroke-width="1.5" opacity="0.75"/>')
    t, _ = text_block(P2X + 16, P2Y + 36,
                      f"same 50 runs, same x axis: flat. Signed correlation r = {fmt2n(r_est)}; "
                      "even the largest preference swings move the stated number by about 1% "
                      "(log-ratio ≈ 0.01).",
                      15.5, 38, INK)
    b.append(t)

    # ---------------- legend (inside panel 1, top-left) ----------------
    ly = P1Y + 46
    lx = P1X + 16

    def key_dot(x, y, color, r=6, ring=False):
        if ring:
            return (f'<circle cx="{x}" cy="{y}" r="5" fill="none" stroke="{color}" '
                    f'stroke-width="1.6"/>')
        return f'<circle cx="{x}" cy="{y}" r="{r}" fill="{color}"/>'

    legend = [
        (key_dot(lx, ly, INK), "one OLMo risk-model run (n = 50)"),
        (key_dot(lx, ly + 24, RED, 8.5), "judge reverses the value (marquee run)"),
        (key_dot(lx, ly + 48, BLUE, 8.5), "risk invades a neutral pool (marquee runs)"),
        (key_dot(lx, ly + 72, GRAY, ring=True),
         "Qwen3-4B run (n = 17): coupling absent, r = −0.22"),
    ]
    for glyph, lab in legend:
        b.append(glyph)
    for i, (glyph, lab) in enumerate(legend):
        b.append(f'<text x="{lx + 16}" y="{ly + 24 * i + 5}" font-size="15.5" '
                 f'fill="{INK}" font-family="{FONT}">{esc(lab)}</text>')

    # ---------------- takeaway box ----------------
    ky = 710
    b.append(box(90, ky, 1030, 128, KEY_FILL))
    t, _ = rich_text(
        112, ky + 32,
        [("Motivated cognition, on the cheap-to-fake channel only. ", INK, True),
         (f"The preference and the belief move together (signed correlation +{r_bias:.2f} "
          f"across runs; within a run the round-by-round correlation averages "
          f"+{g['within_run_corr_bias_mean']:.2f} and is positive in "
          f"{int(round(g['within_run_corr_bias_pos_share'] * 100))}% of runs), and they start "
          f"correlated before any training (+{g['baseline_corr_pref_bias']:.2f}, with a "
          f"+{g['mean_bias_r0']:.2f} pro-gamble bias at round 0). ", INK, False),
         ("Ask for a number and the model tells the truth; ask which side is higher and the "
          "preference leaks in.", RED, True)],
        16.5, 116)
    b.append(t)

    # measurement recipe footer
    t, _ = text_block(
        90, 872,
        "Preference: P(choose the riskier option) on held-out EV-neutral gambles. Belief bias: "
        "P(says the GAMBLE side has the higher expected value) minus 0.5 on a balanced set of 24 "
        "factual comparison items (12 where the gamble truly is higher, 12 where it is not; 0 = unbiased). "
        "Numeric channel: the model states the gamble’s expected value; we plot the change in "
        "log(stated / true). Both panels share the same plotted range so flatness is comparable.",
        14, 160, GRAY)
    b.append(t)

    out = svg_doc(W, H, "\n".join(b))
    path = os.path.join(HERE, "ev-bias-coupling.svg")
    with open(path, "w") as f:
        f.write(out)
    print("wrote", path)


def fmt2(v):
    return f"{v:+.2f}".replace("-", "−")


def fmt2n(v):
    return f"{v:+.2f}".replace("-", "−")


if __name__ == "__main__":
    main()
