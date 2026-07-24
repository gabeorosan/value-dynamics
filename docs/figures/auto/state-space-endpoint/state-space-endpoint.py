#!/usr/bin/env python3
"""Draft figure: the 3-state loop model (pool p, alignment rho, supply sigma)
rolled forward from each run's round-1 state gives calibrated endpoint
distributions — forest plot of 80% intervals against true endpoints, with the
one structural failure (the mid-run alignment bloom) called out, plus the
MAE comparison against baselines and the fitted OLMo equations.

Data: experiments/state_space_endpoint.json (leave-one-run-out, 2000
Monte-Carlo paths per run). Context: docs/reports/report_state_space_endpoint.md.
Style: docs/figures/src/make_figures.py (Evans-lab house style).
Regenerate:  python3 state-space-endpoint.py
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "..", "..", "..", "experiments",
                    "state_space_endpoint.json")

INK = "#1a1a1a"
BLUE = "#2867b5"       # accent / self-judge series (validated)
GREEN = "#3a7d44"      # accent / frozen-judge series (validated)
RED = "#b5342c"        # emphasis for reversal / warning text
GRAY = "#6b7684"       # recessive only (axes, muted captions) — never a series
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


def rich_text(x, y, segments, size, width, lh=1.38, weight="normal"):
    """segments: list of (text, color, bold). Wraps across segments."""
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
 <path d="M 0 0 L 10 5 L 0 10 z" fill="{INK}"/></marker>
<marker id="arrR" viewBox="0 0 10 10" refX="9" refY="5"
 markerWidth="6" markerHeight="6" orient="auto-start-reverse">
 <path d="M 0 0 L 10 5 L 0 10 z" fill="{RED}"/></marker></defs>'''


def svg_doc(w, h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
            f'font-family="{FONT}">\n<rect width="{w}" height="{h}" fill="white"/>\n'
            f'{DEFS}\n{body}\n</svg>')


# ------------------------------------------------------------------
COND_NAME = {
    "evolving_self": "self-judge, evolving",
    "frozen_base": "frozen base-model judge",
    "frozen_cons_r0": "frozen conservative judge",
    "frozen_copy_r0": "frozen round-0 self copy",
}
COND_ORDER = ["evolving_self", "frozen_base", "frozen_cons_r0", "frozen_copy_r0"]


def cond_color(cond):
    return BLUE if cond == "evolving_self" else GREEN


def main():
    data = json.load(open(DATA))
    olmo, qwen = data["k2_olmo"], data["k1_qwen"]

    W, H = 1480, 1400
    b = []

    # ---- headline + measurement-recipe subtitle ----
    t, _ = text_block(W // 2, 52, "Where will the run end up? A three-variable loop model", 33, 74, weight="bold")
    b.append(t.replace('<text ', '<text text-anchor="middle" ', 1))
    t, _ = text_block(W // 2, 92, "answers with calibrated intervals", 33, 74, weight="bold")
    b.append(t.replace('<text ', '<text text-anchor="middle" ', 1))
    t, _ = text_block(W // 2, 126,
                      "p = pool mean risk · rho = correlation of the judge's scores with candidate risk · sigma = candidate risk spread.",
                      18, 130, GRAY)
    b.append(t.replace('<text ', '<text text-anchor="middle" ', 1))
    t, _ = text_block(W // 2, 151,
                      "Three fitted linear equations, rolled forward as 2000 Monte-Carlo paths from each run's round-1 state — leave-one-run-out, so the held-out run never touches the fit that predicts it.",
                      18, 156, GRAY)
    b.append(t.replace('<text ', '<text text-anchor="middle" ', 1))

    # ---- forest plot geometry ----
    FX, FW = 410, 560          # x range of the risk axis (0..1)
    ROWH = 28
    COND_GAP = 8

    def X(v):
        return FX + FW * max(0.0, min(1.0, v))

    # legend (two lines, above the plot)
    ly = 208
    b.append(f'<rect x="{FX - 250}" y="{ly - 7}" width="56" height="11" rx="4" fill="{GREEN}" fill-opacity="0.35"/>')
    b.append(f'<line x1="{FX - 222}" y1="{ly - 11}" x2="{FX - 222}" y2="{ly + 8}" stroke="{GREEN}" stroke-width="3.5"/>')
    b.append(f'<text x="{FX - 184}" y="{ly + 4}" font-size="16" fill="{INK}" font-family="{FONT}">80% predicted interval, with its predictive median (tick)</text>')
    b.append(f'<circle cx="{FX + 262}" cy="{ly - 1}" r="5.5" fill="{INK}" stroke="white" stroke-width="1.5"/>')
    b.append(f'<text x="{FX + 274}" y="{ly + 4}" font-size="16" fill="{INK}" font-family="{FONT}">true endpoint (23 of 25 inside)</text>')
    b.append(f'<circle cx="{FX + 532}" cy="{ly - 1}" r="6" fill="{RED}" stroke="white" stroke-width="1.5"/>')
    b.append(f'<text x="{FX + 544}" y="{ly + 4}" font-size="16" fill="{INK}" font-family="{FONT}">outside its interval (2 of 25)</text>')
    ly2 = ly + 27
    b.append(f'<rect x="{FX - 250}" y="{ly2 - 12}" width="15" height="15" rx="3" fill="{BLUE}"/>')
    b.append(f'<text x="{FX - 228}" y="{ly2}" font-size="16" fill="{INK}" font-family="{FONT}">self-judge runs (the organism judges its own answers)</text>')
    b.append(f'<rect x="{FX + 200}" y="{ly2 - 12}" width="15" height="15" rx="3" fill="{GREEN}"/>')
    b.append(f'<text x="{FX + 222}" y="{ly2}" font-size="16" fill="{INK}" font-family="{FONT}">frozen-judge runs (base model, round-0 conservative, or round-0 self copy)</text>')

    top = 262
    misses = []   # (cx, cy, run) for dots outside the 80% interval
    fail_dot = None

    def draw_group(y0, title, runs):
        rows = sorted(runs, key=lambda r: (COND_ORDER.index(r["cond"]), int(r["seed"])))
        s = [f'<text x="148" y="{y0}" font-size="19" font-weight="bold" fill="{INK}" font-family="{FONT}">{esc(title)}</text>']
        y = y0 + 14
        prev_cond = rows[0]["cond"]
        for r in rows:
            if r["cond"] != prev_cond:
                y += COND_GAP
                prev_cond = r["cond"]
            cy = y + ROWH / 2
            color = cond_color(r["cond"])
            s.append(f'<text x="398" y="{cy + 5}" text-anchor="end" font-size="16" fill="{INK}" '
                     f'font-family="{FONT}">{esc(COND_NAME[r["cond"]])} · seed {r["seed"]}</text>')
            x0b, x1b = X(r["lo80"]), X(r["hi80"])
            s.append(f'<rect x="{x0b:.1f}" y="{cy - 5.5}" width="{x1b - x0b:.1f}" height="11" rx="4" '
                     f'fill="{color}" fill-opacity="0.35"/>')
            xm = X(r["median"])
            s.append(f'<line x1="{xm:.1f}" y1="{cy - 9}" x2="{xm:.1f}" y2="{cy + 9}" stroke="{color}" stroke-width="3.5"/>')
            xt = X(r["truth"])
            if r["in80"]:
                s.append(f'<circle cx="{xt:.1f}" cy="{cy}" r="5.5" fill="{INK}" stroke="white" stroke-width="1.5"/>')
            else:
                s.append(f'<circle cx="{xt:.1f}" cy="{cy}" r="6" fill="{RED}" stroke="white" stroke-width="1.5"/>')
                misses.append((xt, cy, r))
            y += ROWH
        return "\n".join(s), y

    g1, olmo_end = draw_group(top, "OLMo risk model, K2 grid — 13 held-out runs", olmo["runs"])
    # failure callout sits between the two groups
    cal_y = olmo_end + 14
    cal_h = 138
    qwen_top = cal_y + cal_h + 34
    g2, qwen_end = draw_group(qwen_top, "Qwen risk model, K1 grid — 12 held-out runs", qwen["runs"])

    # gridlines + axis (drawn first so bars sit on top)
    axis_bot = qwen_end + 8
    for v in (0.0, 0.25, 0.5, 0.75, 1.0):
        x = X(v)
        b.append(f'<line x1="{x}" y1="{top - 18}" x2="{x}" y2="{axis_bot}" stroke="#e4e4e0" stroke-width="1"/>')
        b.append(f'<text x="{x}" y="{axis_bot + 22}" text-anchor="middle" font-size="16" fill="{GRAY}" font-family="{FONT}">{v:g}</text>')
    t, _ = text_block(FX - 60, axis_bot + 50,
                      "risk coordinate at the run's final round — the fraction of the model's answers on 12 held-out gamble questions that pick the gamble",
                      16, 88, INK)
    b.append(t)

    b.append(g1)
    b.append(g2)

    # ---- the one structural failure: frozen base-model judge, seed 5 ----
    for xt, cy, r in misses:
        if abs(r["truth"] - 0.653) < 1e-6:
            fail_dot = (xt, cy)
    t, cal_end = rich_text(448, cal_y + 26, [
        ("The bloom no round-1 state could see. ", RED, True),
        ("This run's round-1 state (p 0.17, rho 0.01, sigma 0.20) was indistinguishable from runs that settled low — then judge-candidate alignment bloomed mid-run from sampling luck. Truth 0.653 lands at PIT 0.997, outside the 80% interval [0.03, 0.39]: priced as tail mass, not predicted.", INK, False),
    ], 15.5, 78)
    b.append(box(430, cal_y, 585, (cal_end - cal_y) + 12, "#fbf0ee", RED, 2.5))
    b.append(t)
    if fail_dot:
        b.append(f'<line x1="700" y1="{cal_y - 2}" x2="{fail_dot[0] + 2:.1f}" y2="{fail_dot[1] + 10:.1f}" '
                 f'stroke="{RED}" stroke-width="3" marker-end="url(#arrR)"/>')

    # ================= right panel =================
    RX = 1030
    RW = 430

    t, y = text_block(RX, 270, "Point error: mean absolute error of the median forecast, over held-out runs (lower is better)", 19, 42, weight="bold")
    b.append(t)

    def mae_bars(y0, title, vals):
        # vals: [(label, value, color)]
        s = [f'<text x="{RX}" y="{y0}" font-size="17" font-weight="bold" fill="{INK}" font-family="{FONT}">{esc(title)}</text>']
        scale = 210 / 0.18
        bx = RX + 200
        y = y0 + 14
        for label, v, color in vals:
            s.append(f'<text x="{bx - 10}" y="{y + 15}" text-anchor="end" font-size="15.5" fill="{INK}" font-family="{FONT}">{esc(label)}</text>')
            s.append(f'<rect x="{bx}" y="{y}" width="{v * scale:.1f}" height="20" rx="4" fill="{color}" fill-opacity="0.6"/>')
            s.append(f'<text x="{bx + v * scale + 8:.1f}" y="{y + 15}" font-size="16" font-weight="bold" fill="{INK}" font-family="{FONT}">{v:.3f}</text>')
            y += 30
        return "\n".join(s), y

    s1, y = mae_bars(y + 16, "OLMo risk model, K2 grid",
                     [("3-state loop model", olmo["mae"], INK),
                      ("gap autoregression", olmo["gap_mae"], GRAY),
                      ("persistence", olmo["persist_mae"], GRAY)])
    b.append(s1)
    s2, y = mae_bars(y + 26, "Qwen risk model, K1 grid",
                     [("3-state loop model", qwen["mae"], INK),
                      ("gap autoregression", qwen["gap_mae"], GRAY),
                      ("persistence", qwen["persist_mae"], GRAY)])
    b.append(s2)

    t, y = rich_text(RX, y + 22, [
        ("Baselines: ", INK, True),
        ("gap autoregression = the selection gap following its own one-step autoregression (the forecast you would build without the rho/sigma decomposition); persistence = the endpoint simply stays at the round-1 value. On OLMo the loop model beats both. On Qwen it ties persistence — correctly: the Qwen fan is training instability, not force, so the honest forecast is a wide-but-calibrated interval, not a tighter median.", INK, False),
    ], 16, 54)
    b.append(t)

    t, y = rich_text(RX, y + 24, [
        ("Interval calibration: ", INK, True),
        ("80% intervals cover 12 of 13 OLMo runs and 11 of 12 Qwen runs (92% each — slightly conservative); 50% intervals cover 54% and 75%.", INK, False),
    ], 16, 54)
    b.append(t)

    # fitted equations box
    ey = y + 26
    fit = olmo["full_fit"]

    def r2(v):  # round half up at 2 decimals (1.085 -> 1.09, matching the report)
        return f"{int(v * 100 + 0.5) / 100:.2f}"

    dp, rho, sig = fit["dp"]["beta"], fit["rho"]["beta"], fit["sigma"]["beta"]
    eq_lines = [
        [("change in pool", INK, True), (f"= {dp[0]:.3f} +", INK, False), (r2(dp[1]), RED, True), ("· (rho·sigma)", INK, False)],
        [("next rho", INK, True), (f"= {r2(rho[0])} + {r2(rho[1])}·rho +", INK, False), (r2(rho[2]), RED, True), ("· (rho·sigma)", INK, False)],
        [("next sigma", INK, True), (f"= {r2(sig[0])} + {r2(sig[1])}·sigma + {r2(sig[2])}·p(1−p)", INK, False)],
    ]
    inner, yy = text_block(RX + 20, ey + 34, "The fitted equations ARE the runaway loop, written as coefficients (OLMo fit, all 13 runs):", 17.5, 44, INK, "bold")
    body = [inner]
    yy += 8
    for seg in eq_lines:
        t, yy = rich_text(RX + 20, yy + 6, seg, 16.5, 48)
        body.append(t)
    t, yy = rich_text(RX + 20, yy + 14, [
        ("Force begets alignment: ", RED, True),
        ("the same product rho · sigma pushes the pool up at slope 1.21 and feeds alignment back at slope 1.22 — the positive product feedback that right-skews endpoints from mildly-aligned starts.", INK, False),
    ], 16, 52)
    body.append(t)
    eh = (yy - ey) + 22
    b.append(box(RX, ey, RW, eh, KEY_FILL, GREEN, 3))
    b.extend(body)

    # ---- bottom takeaway ----
    ty = max(axis_bot + 110, ey + eh + 30)
    tk, tk_end = rich_text(80, ty + 34, [
        ("23 of 25 true endpoints fall inside their 80% predicted intervals ", INK, True),
        ("(92% empirical at 80% nominal, on both grids). The Qwen miss (self-judge seed 0, PIT 0.044) sits just outside its interval — ordinary coverage slack. The OLMo miss is the one structural blind spot: alignment blooms triggered by within-run sampling luck, which no round-1 state can see and the model can only price as tail mass.", INK, False),
    ], 19, 128)
    b.append(box(60, ty, W - 120, (tk_end - ty) + 18, KEY_FILL, INK, 2.5))
    b.append(tk)
    H = int(tk_end + 60)

    out = svg_doc(W, H, "\n".join(b))
    path = os.path.join(HERE, "state-space-endpoint.svg")
    with open(path, "w") as f:
        f.write(out)
    print(f"wrote {path} ({W}x{H})")


if __name__ == "__main__":
    main()
