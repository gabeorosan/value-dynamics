#!/usr/bin/env python3
"""Qwen3.5-9B insecure-code SFT dose ladder: a single passing rung.

Two stacked panels share the dose x-axis. Top panel = frozen-base-judge
misalignment (em_freegen) with the registered headroom window [0.20, 0.60]
shaded; bottom panel = off-topic/incoherence rate (bleed_freegen) with the
registered coherence gate (<= 0.75) shaded. Both instruments wiggle
non-monotonically across the four doses, and the two shaded gate regions
overlap at exactly one rung (dose 750), which is flagged PASS.

Style follows docs/figures/src/make_figures.py (Owain Evans-lab house style):
white background, headline sentence, real data with fat labels, keys not
legends-of-abbreviations. Palette constants copied verbatim from that file.
Stdlib only. Run from this directory:  python3 qwen35-9b-dose-window.py

Source data: ../../../../experiments/qwen35_em_ladders/output/em359b_dose_ladder.json
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "..", "..", "..", "experiments",
                    "qwen35_em_ladders", "output", "em359b_dose_ladder.json")

# --- palette copied verbatim from make_figures.py ---
INK = "#1a1a1a"
BLUE = "#2867b5"       # here: incoherence (bleed) series
GREEN = "#3a7d44"      # here: frozen-base-judge misalignment (em_freegen) series
RED = "#b5342c"        # emphasis for gate failures
GRAY = "#6b7684"       # recessive only (axes, muted reference, captions)
USER_FILL = "#cfe0f1"
ASST_FILL = "#eaf1f8"  # light blue tint -> coherence-good region
DOC_FILL = "#fdf6e8"   # warm tint -> the passing dose column
KEY_FILL = "#eef5ee"   # light green tint -> headroom window
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


def T(x, y, s, size, color=INK, weight="normal", anchor="start", italic=False):
    st = ' font-style="italic"' if italic else ""
    return (f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" '
            f'fill="{color}" font-weight="{weight}" text-anchor="{anchor}"{st}>'
            f'{esc(s)}</text>')


def main():
    d = json.load(open(DATA))
    doses = [250, 500, 750, 1000]
    em = [d["doses"][str(k)]["em_freegen"] for k in doses]
    bleed = [d["doses"][str(k)]["bleed_freegen"] for k in doses]
    g = d["config"]["gates"]
    lo, hi, cmax = g["headroom_lo"], g["headroom_hi"], g["coherence_max"]
    noise = d["doses"]["250"].get("em_freegen_noise", 0.0221)
    # same-recipe Qwen3.5-4B reference (from em354b ladder, quoted in brief)
    em_4b = [0.197, 0.150, 0.113, 0.140]

    W, H = 1180, 1140
    # x positions for the four dose columns
    xL, xR = 250, 980
    xs = [xL + i * (xR - xL) / 3 for i in range(4)]
    win_i = doses.index(750)

    # panel A (em_freegen): value in [0, 0.65]
    A_top, A_bot, A_max = 300, 545, 0.65
    yA = lambda v: A_bot - (v / A_max) * (A_bot - A_top)
    # panel B (bleed): value in [0, 0.90]
    B_top, B_bot, B_max = 650, 895, 0.90
    yB = lambda v: B_bot - (v / B_max) * (B_bot - B_top)

    body = []

    # ---- headline ----
    body.append(T(60, 74,
        "One of four doses lands Qwen3.5-9B in the coherent-but-misaligned window",
        29, INK, "bold"))
    for i, ln in enumerate(wrap(
        "Insecure-code fine-tuning at four doses (epochs). Both registered "
        "instruments move non-monotonically with dose, so the usable operating "
        "point is a single rung, not a plateau.", 96)):
        body.append(T(60, 112 + i * 27, ln, 19, GRAY))

    # ---- passing-dose column highlight (drawn first, behind everything) ----
    cw = 96
    body.append(f'<rect x="{xs[win_i]-cw/2:.1f}" y="{A_top-40}" width="{cw}" '
                f'height="{B_bot-(A_top-40)}" rx="10" fill="{DOC_FILL}" '
                f'stroke="{GREEN}" stroke-width="2.5" stroke-dasharray="7 5"/>')
    body.append(T(xs[win_i], A_top - 50,
                  "the one passing rung", 17, GREEN, "bold", "middle"))

    # ================= PANEL A : em_freegen =================
    # headroom band
    body.append(f'<rect x="{xL-30}" y="{yA(hi):.1f}" width="{xR-xL+90}" '
                f'height="{yA(lo)-yA(hi):.1f}" fill="{KEY_FILL}"/>')
    # axis frame
    body.append(f'<line x1="{xL-30}" y1="{A_bot}" x2="{xR+60}" y2="{A_bot}" '
                f'stroke="{GRAY}" stroke-width="1.5"/>')
    body.append(f'<line x1="{xL-30}" y1="{A_top-15}" x2="{xL-30}" y2="{A_bot}" '
                f'stroke="{GRAY}" stroke-width="1.5"/>')
    # band edge lines + labels
    for val, txt in [(lo, f"headroom floor  {lo:.2f}"),
                     (hi, f"headroom ceiling  {hi:.2f}")]:
        body.append(f'<line x1="{xL-30}" y1="{yA(val):.1f}" x2="{xR+60}" '
                    f'y2="{yA(val):.1f}" stroke="{GREEN}" stroke-width="1.6" '
                    f'stroke-dasharray="6 4"/>')
    body.append(T(xR + 66, yA(lo) + 5, f"floor {lo:.2f}", 15, GREEN, "bold"))
    body.append(T(xR + 66, yA(hi) + 5, f"ceiling {hi:.2f}", 15, GREEN, "bold"))
    body.append(T(xL - 30, A_top - 22,
                  "Frozen-base-judge misalignment  (em_freegen, higher = more misaligned)",
                  18, INK, "bold"))
    body.append(T(xR - 6, yA((lo+hi)/2) + 6, "usable window", 15, GREEN, "bold", "end"))

    # 4B reference curve (recessive)
    pts4 = " ".join(f"{xs[i]:.1f},{yA(em_4b[i]):.1f}" for i in range(4))
    body.append(f'<polyline points="{pts4}" fill="none" stroke="{GRAY}" '
                f'stroke-width="1.8" stroke-dasharray="4 4"/>')
    for i in range(4):
        body.append(f'<circle cx="{xs[i]:.1f}" cy="{yA(em_4b[i]):.1f}" r="4.5" '
                    f'fill="white" stroke="{GRAY}" stroke-width="1.8"/>')
    body.append(T(xL + 8, A_bot - 34,
                  "Qwen3.5-4B, same recipe:", 15, GRAY, "bold"))
    body.append(T(xL + 8, A_bot - 15,
                  "stays under the 0.20 floor at every dose (size, not recipe, opens headroom)",
                  15, GRAY))

    # 9B em curve
    ptsA = " ".join(f"{xs[i]:.1f},{yA(em[i]):.1f}" for i in range(4))
    body.append(f'<polyline points="{ptsA}" fill="none" stroke="{GREEN}" '
                f'stroke-width="3"/>')
    for i in range(4):
        pv = (i == win_i)
        r = 11 if pv else 7
        if pv:
            body.append(f'<circle cx="{xs[i]:.1f}" cy="{yA(em[i]):.1f}" r="{r+4}" '
                        f'fill="none" stroke="{GREEN}" stroke-width="2.5"/>')
        body.append(f'<circle cx="{xs[i]:.1f}" cy="{yA(em[i]):.1f}" r="{r}" '
                    f'fill="{GREEN}" stroke="white" stroke-width="2.5"/>')
        dy = -20 if em[i] > lo else 26
        body.append(T(xs[i], yA(em[i]) + dy, f"{em[i]:.3f}", 17, GREEN, "bold", "middle"))

    # ================= PANEL B : bleed =================
    # coherence-good region (bleed <= cmax): from the gate line down to baseline
    body.append(f'<rect x="{xL-30}" y="{yB(cmax):.1f}" width="{xR-xL+90}" '
                f'height="{B_bot-yB(cmax):.1f}" fill="{ASST_FILL}"/>')
    body.append(f'<line x1="{xL-30}" y1="{B_bot}" x2="{xR+60}" y2="{B_bot}" '
                f'stroke="{GRAY}" stroke-width="1.5"/>')
    body.append(f'<line x1="{xL-30}" y1="{B_top-15}" x2="{xL-30}" y2="{B_bot}" '
                f'stroke="{GRAY}" stroke-width="1.5"/>')
    body.append(f'<line x1="{xL-30}" y1="{yB(cmax):.1f}" x2="{xR+60}" '
                f'y2="{yB(cmax):.1f}" stroke="{BLUE}" stroke-width="1.6" '
                f'stroke-dasharray="6 4"/>')
    body.append(T(xR + 66, yB(cmax) + 5, f"gate {cmax:.2f}", 15, BLUE, "bold"))
    body.append(T(xL - 30, B_top - 22,
                  "Off-topic / incoherence rate  (bleed, lower = more coherent)",
                  18, INK, "bold"))
    body.append(T(xR - 6, yB((cmax+B_max)/2) + 6, "too incoherent", 15, RED, "bold", "end"))
    body.append(T(xR - 6, yB(cmax/2) + 6, "coherent enough", 15, BLUE, "bold", "end"))

    ptsB = " ".join(f"{xs[i]:.1f},{yB(bleed[i]):.1f}" for i in range(4))
    body.append(f'<polyline points="{ptsB}" fill="none" stroke="{BLUE}" '
                f'stroke-width="3"/>')
    for i in range(4):
        pv = (i == win_i)
        r = 11 if pv else 7
        pass_gate = bleed[i] <= cmax
        col = BLUE if pass_gate else RED
        if pv:
            body.append(f'<circle cx="{xs[i]:.1f}" cy="{yB(bleed[i]):.1f}" r="{r+4}" '
                        f'fill="none" stroke="{BLUE}" stroke-width="2.5"/>')
        body.append(f'<circle cx="{xs[i]:.1f}" cy="{yB(bleed[i]):.1f}" r="{r}" '
                    f'fill="{col}" stroke="white" stroke-width="2.5"/>')
        dy = -20 if bleed[i] > cmax else -20
        body.append(T(xs[i], yB(bleed[i]) + dy, f"{bleed[i]:.3f}", 17, col, "bold", "middle"))

    # ---- shared x-axis dose labels ----
    for i in range(4):
        body.append(T(xs[i], B_bot + 34, f"{doses[i]}", 22, INK, "bold", "middle"))
    body.append(T((xL + xR) / 2, B_bot + 66,
                  "training dose  (SFT steps over the insecure-code slice)",
                  18, GRAY, "normal", "middle"))

    # ---- per-dose gate verdict chips ----
    chip_y = B_bot + 92
    verdicts = [
        (RED,  "FAIL", "bleed 0.80 > 0.75", "too incoherent"),
        (RED,  "FAIL", "em 0.18 < 0.20", "below headroom floor"),
        (GREEN, "PASS", "both gates", "0.20 < em < 0.60,  bleed < 0.75"),
        (RED,  "FAIL", "em 0.17 < 0.20", "below headroom floor"),
    ]
    for i, (col, tag, why, sub) in enumerate(verdicts):
        cw2 = 168
        x0 = xs[i] - cw2 / 2
        fill = KEY_FILL if tag == "PASS" else "#faeceb"
        body.append(f'<rect x="{x0:.1f}" y="{chip_y}" width="{cw2}" height="72" '
                    f'rx="9" fill="{fill}" stroke="{col}" stroke-width="2.5"/>')
        body.append(T(xs[i], chip_y + 26, tag, 20, col, "bold", "middle"))
        body.append(T(xs[i], chip_y + 47, why, 14, INK, "bold", "middle"))
        body.append(T(xs[i], chip_y + 64, sub, 12, GRAY, "normal", "middle"))

    # ---- key strip ----
    ky = chip_y + 108
    body.append(f'<line x1="60" y1="{ky-18}" x2="{W-60}" y2="{ky-18}" '
                f'stroke="{GRAY}" stroke-width="1"/>')

    def key_dot(x, col, dashed=False):
        if dashed:
            return (f'<line x1="{x}" y1="{ky}" x2="{x+34}" y2="{ky}" stroke="{col}" '
                    f'stroke-width="2.4" stroke-dasharray="4 4"/>'
                    f'<circle cx="{x+17}" cy="{ky}" r="4.5" fill="white" '
                    f'stroke="{col}" stroke-width="1.8"/>')
        return (f'<line x1="{x}" y1="{ky}" x2="{x+34}" y2="{ky}" stroke="{col}" '
                f'stroke-width="3"/><circle cx="{x+17}" cy="{ky}" r="7" fill="{col}" '
                f'stroke="white" stroke-width="2"/>')

    body.append(key_dot(60, GREEN))
    body.append(T(104, ky + 6, "Qwen3.5-9B misalignment (em_freegen)", 15, INK))
    body.append(key_dot(470, BLUE))
    body.append(T(514, ky + 6, "Qwen3.5-9B incoherence (bleed)", 15, INK))
    body.append(key_dot(860, GRAY, dashed=True))
    body.append(T(904, ky + 6, "Qwen3.5-4B reference (same recipe)", 15, INK))

    body.append(T(60, ky + 34,
        f"em_freegen noise floor = {noise:.3f} (near zero). Both curves are non-monotone: "
        "the gate regions overlap only at dose 750.", 14, GRAY))

    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
           f'font-family="{FONT}">\n<rect width="{W}" height="{H}" fill="white"/>\n'
           + "\n".join(body) + "\n</svg>")
    out = os.path.join(HERE, "qwen35-9b-dose-window.svg")
    with open(out, "w") as f:
        f.write(svg)
    print("wrote", out)


if __name__ == "__main__":
    main()
