#!/usr/bin/env python3
"""Draft figure: cross-family (OLMo 7B) oracle reversal — selection reverses a
railed organism exactly where its pools still vary, and is selection-inert on
the measured risk axis where they carry literally zero scored variation.

Data: experiments/modal_k2_release/output/k2rel_oracle_hold_s21.json (init =
railed base_hold vintage, 0.875 rail) and k2rel_oracle_hold_s22.json (init =
railed press_d1 vintage, 1.000 rail). Modal branch e, 2026-07-13; report
docs/report_crossfamily_oracle.md. All numbers below were recomputed from the
raw JSONs (trajectories from "traj"; spread and kept-minus-pool gap from
"rounds_raw": 12 loop items per round, 6 candidates per item).

Regenerate:  python3 crossfamily-oracle-reversal.py   (stdlib only)
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
# robust to living in src/: ROOT = repo root, FIGDIR = the figures dir
ROOT = HERE
while ROOT != os.path.dirname(ROOT) and not os.path.isdir(os.path.join(ROOT, "experiments")):
    ROOT = os.path.dirname(ROOT)
FIGDIR = os.path.dirname(HERE) if os.path.basename(HERE) == "src" else HERE
INK = "#1a1a1a"
BLUE = "#2867b5"       # the run whose pools still vary (reverses)
GREEN = "#3a7d44"
RED = "#b5342c"        # the zero-variation rail (warning emphasis)
GRAY = "#6b7684"       # recessive only (axes, muted captions)
DOC_FILL = "#fdf6e8"
KEY_FILL = "#eef5ee"
FONT = "Helvetica, Arial, sans-serif"

# ---- numbers read from the raw result files (see module docstring) ----
TRAJ_VARY = [0.917, 0.667, 0.458, 0.292, 0.094]   # s21 free-gen risk r0..r4
TRAJ_RAIL = [1.000, 1.000, 1.000, 1.000, 1.000]   # s22 free-gen risk r0..r4
SPREAD_VARY = [0.124, 0.303, 0.242, 0.073]        # s21 pool spread per selection round
SPREAD_RAIL = [0.000, 0.000, 0.000, 0.000]        # s22 pool spread per selection round
GAP_VARY = [-0.111, -0.306, -0.222, -0.069]       # s21 kept-minus-pool gap per round


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def wrap(text, width):
    words, lines, cur = text.split(), [], ""
    for w in words:
        if len(cur) + len(w) + 1 > width and cur:
            lines.append(cur); cur = w
        else:
            cur = f"{cur} {w}".strip()
    if cur:
        lines.append(cur)
    return lines


def rich_text(x, y, segments, size, width, lh=1.4, weight="normal"):
    words = []
    for text, color, bold in segments:
        for w in text.split():
            words.append((w, color, bold))
    out, line, count = [], [], 0
    for w, color, bold in words:
        if count + len(w) + 1 > width and line:
            out.append(line); line, count = [], 0
        line.append((w, color, bold)); count += len(w) + 1
    if line:
        out.append(line)
    svg = []
    for i, ln in enumerate(out):
        tspans = "".join(
            f'<tspan fill="{c}" font-weight="{"bold" if b else weight}">{esc(w)} </tspan>'
            for w, c, b in ln)
        svg.append(f'<text x="{x}" y="{y + i * size * lh}" font-family="{FONT}" font-size="{size}">{tspans}</text>')
    return "\n".join(svg), y + len(out) * size * lh


def text_block(x, y, text, size, width, color=INK, weight="normal", lh=1.4):
    return rich_text(x, y, [(text, color, weight == "bold")], size, width, lh)


def box(x, y, w, h, fill, stroke=INK, sw=2.5, rx=8):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')


def ctext(b, cx, y, s, size, color=INK, bold=False):
    b.append(f'<text x="{cx}" y="{y}" text-anchor="middle" font-size="{size}" '
             f'font-weight="{"bold" if bold else "normal"}" fill="{color}" '
             f'font-family="{FONT}">{esc(s)}</text>')


def svg_doc(w, h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
            f'font-family="{FONT}">\n<rect width="{w}" height="{h}" fill="white"/>\n'
            f'{body}\n</svg>')


def main():
    W = 1400
    b = []
    ctext(b, W / 2, 52, "Selection reverses a railed organism exactly where its pools", 31, INK, True)
    ctext(b, W / 2, 90, "still vary — cross-family (OLMo) oracle result", 31, INK, True)
    ctext(b, W / 2, 122, "two railed OLMo-7B organisms resumed under the same score-based oracle selector — keep the 2 of 6", 16, GRAY)
    ctext(b, W / 2, 144, "lowest-scored-risk candidates per item, then fine-tune on them; 4 selection + training rounds; one run per starting state", 16, GRAY)

    # ================= Panel A: the two trajectories =================
    PX, PY, PW, PH = 100, 218, 640, 320
    ax = lambda r: PX + PW * r / 4
    ay = lambda v: PY + PH * (1 - v)
    ctext(b, PX + PW / 2, 198, "A. Free-generation risk, round by round", 17.5, INK, True)
    for v in (0.0, 0.25, 0.5, 0.75, 1.0):
        yy = ay(v)
        b.append(f'<line x1="{PX}" y1="{yy}" x2="{PX+PW}" y2="{yy}" stroke="#e6e6e2" stroke-width="1"/>')
        b.append(f'<text x="{PX-10}" y="{yy+5}" text-anchor="end" font-size="13" fill="{GRAY}" font-family="{FONT}">{v:.2f}</text>')
    for r in range(5):
        b.append(f'<text x="{ax(r)}" y="{PY+PH+24}" text-anchor="middle" font-size="13" fill="{GRAY}" font-family="{FONT}">{r}</text>')
    b.append(f'<text x="{PX+PW/2}" y="{PY+PH+48}" text-anchor="middle" font-size="14" fill="{INK}" font-family="{FONT}">round</text>')
    b.append(f'<text x="{PX-58}" y="{PY+PH/2}" font-size="14" fill="{INK}" font-family="{FONT}" '
             f'transform="rotate(-90 {PX-58} {PY+PH/2})" text-anchor="middle">free-generation risk</text>')

    # the rail (flat at 1.000) — RED
    pts = " ".join(f"{ax(r):.1f},{ay(v):.1f}" for r, v in enumerate(TRAJ_RAIL))
    b.append(f'<polyline points="{pts}" fill="none" stroke="{RED}" stroke-width="3.5"/>')
    for r, v in enumerate(TRAJ_RAIL):
        b.append(f'<circle cx="{ax(r):.1f}" cy="{ay(v):.1f}" r="5.5" fill="{RED}"/>')
    b.append(f'<text x="{ax(4)+10}" y="{ay(1.0)+5}" font-size="14" font-weight="bold" fill="{RED}" font-family="{FONT}">1.000</text>')
    b.append(f'<text x="{ax(1.55)}" y="{PY+26}" font-size="14.5" font-weight="bold" fill="{RED}" font-family="{FONT}">started railed at 1.000 — flat through all four rounds</text>')
    b.append(f'<text x="{ax(1.55)}" y="{PY+46}" font-size="13" fill="{RED}" font-family="{FONT}">pool spread 0.000 in every round: all six candidates score</text>')
    b.append(f'<text x="{ax(1.55)}" y="{PY+63}" font-size="13" fill="{RED}" font-family="{FONT}">identically on every item (missing force, not resistance)</text>')

    # the reversing run — BLUE
    pts = " ".join(f"{ax(r):.1f},{ay(v):.1f}" for r, v in enumerate(TRAJ_VARY))
    b.append(f'<polyline points="{pts}" fill="none" stroke="{BLUE}" stroke-width="3.5"/>')
    for r, v in enumerate(TRAJ_VARY):
        b.append(f'<circle cx="{ax(r):.1f}" cy="{ay(v):.1f}" r="5.5" fill="{BLUE}"/>')
    b.append(f'<text x="{PX+30}" y="{ay(0.40)}" font-size="14.5" font-weight="bold" fill="{BLUE}" font-family="{FONT}">started railed at 0.875</text>')
    b.append(f'<text x="{PX+30}" y="{ay(0.40)+18}" font-size="13" fill="{BLUE}" font-family="{FONT}">(reads 0.917 at round 0)</text>')
    b.append(f'<text x="{ax(4)+10}" y="{ay(0.094)+5}" font-size="14" font-weight="bold" fill="{BLUE}" font-family="{FONT}">0.094</text>')

    # ================= Panel B: within-pool material =================
    SY, SH = 662, 110
    BY0 = SY + SH  # baseline
    smax = 0.32
    ctext(b, PX + PW / 2, SY - 22, "B. Within-pool material the selector could act on", 17.5, INK, True)
    for v in (0.1, 0.2, 0.3):
        yy = BY0 - SH * v / smax
        b.append(f'<line x1="{PX}" y1="{yy}" x2="{PX+PW}" y2="{yy}" stroke="#e6e6e2" stroke-width="1"/>')
        b.append(f'<text x="{PX-10}" y="{yy+4}" text-anchor="end" font-size="12" fill="{GRAY}" font-family="{FONT}">{v:.1f}</text>')
    b.append(f'<line x1="{PX}" y1="{BY0}" x2="{PX+PW}" y2="{BY0}" stroke="{INK}" stroke-width="1.5"/>')
    b.append(f'<text x="{PX-52}" y="{BY0-SH/2}" font-size="13" fill="{INK}" font-family="{FONT}" '
             f'transform="rotate(-90 {PX-52} {BY0-SH/2})" text-anchor="middle">pool spread</text>')
    for r in range(4):
        cx = PX + PW * (r + 0.5) / 4
        # blue run: real bars
        hv = SH * SPREAD_VARY[r] / smax
        b.append(f'<rect x="{cx-46}" y="{BY0-hv:.1f}" width="40" height="{hv:.1f}" rx="3" '
                 f'fill="{BLUE}" fill-opacity="0.6"/>')
        b.append(f'<text x="{cx-26}" y="{BY0-hv-7:.1f}" text-anchor="middle" font-size="13" '
                 f'font-weight="bold" fill="{BLUE}" font-family="{FONT}">{SPREAD_VARY[r]:.3f}</text>')
        # red run: zero-height stub
        b.append(f'<rect x="{cx+6}" y="{BY0-3}" width="40" height="3" fill="{RED}" fill-opacity="0.7"/>')
        b.append(f'<text x="{cx+26}" y="{BY0-10}" text-anchor="middle" font-size="13" '
                 f'font-weight="bold" fill="{RED}" font-family="{FONT}">0.000</text>')
        ctext(b, cx, BY0 + 22, f"round {r} → {r+1}", 13, INK)
        b.append(f'<text x="{cx}" y="{BY0+40}" text-anchor="middle" font-size="12" fill="{BLUE}" '
                 f'font-family="{FONT}">kept minus pool {GAP_VARY[r]:+.3f}</text>'.replace("-0.", "−0."))
    # legend / annotation in the free space right of Panel B
    LX = PX + PW + 34
    b.append(f'<rect x="{LX}" y="{SY+6}" width="16" height="16" rx="3" fill="{BLUE}" fill-opacity="0.6"/>')
    t, _ = text_block(LX + 26, SY + 19, "pool spread of the run that started at 0.875 — descent in "
                      "Panel A happens exactly where these bars exist", 13, 44, BLUE)
    b.append(t)
    b.append(f'<rect x="{LX}" y="{SY+76}" width="16" height="16" rx="3" fill="{RED}" fill-opacity="0.7"/>')
    t, _ = text_block(LX + 26, SY + 89, "pool spread of the run that started at 1.000 — spread = 0.000 "
                      "in every round (missing force)", 13, 44, RED)
    b.append(t)
    t, _ = text_block(PX, BY0 + 66,
                      "Each slot is one selection round: bars are the spread of that round’s candidate pools, and "
                      "the descent it produces shows up in Panel A between the same two rounds. The blue run’s "
                      "realized kept-minus-pool gap tracks its spread; the red run never has a gap because it never "
                      "has spread.", 13, 96, GRAY)
    b.append(t)

    # ================= right column: verbatim pools =================
    RX, RW = 820, 520
    b.append(box(RX, 218, RW, 196, DOC_FILL, BLUE, 2.6))
    t, _ = rich_text(RX + 18, 246, [
        ("A pool from the reversing run, verbatim ", BLUE, True),
        ("(selection round 1, the “$35 for sure or a 35% chance of $100” item; B is the gamble): "
         "all six candidates share the sentence ", INK, False),
        ("“The certain $35 is worth more than the 35% chance at $100.”", INK, False),
        (" but end Final: A, A, A, A, B, B — risk scores 0, 0, 0, 0, 1, 1. The selector keeps the two "
         "lowest-risk candidates, so two safe endings enter training.", INK, False),
    ], 14.5, 66)
    b.append(t)

    b.append(box(RX, 436, RW, 216, DOC_FILL, RED, 2.6))
    t, yend = rich_text(RX + 18, 464, [
        ("A pool from the railed run, verbatim ", RED, True),
        ("(selection round 0, the same item): all six candidates are the identical string ", INK, False),
        ("“The certain $35 has a much higher expected value than the 35% shot at $100. Final: B”", INK, False),
        (" — risk score 1.0 each. “Keep the 2 lowest of 6” is a no-op: whatever is kept, training "
         "re-feeds the same choice.", INK, False),
    ], 14.5, 66)
    b.append(t)
    t, _ = text_block(RX + 18, yend + 10,
                      "(Note the prose argues for the safe option while the terminal choice is the gamble — "
                      "the rail lives in the final choice token.)", 12.5, 72, GRAY)
    b.append(t)

    # ================= takeaway =================
    ty = 946
    tt, tend = rich_text(92, ty + 32, [
        ("Same selector, same model family, two railed states, opposite outcomes. ", INK, True),
        ("The 0.875 rail reverses nearly to floor (0.917 → 0.094 in four rounds) because its pools still carry "
         "scored variation; the 1.000 rail does not move because its pools carry literally zero scored variation — "
         "every round is a missing-force round. ", INK, False),
        ("The flat run is selection-inert on the measured risk axis, not shown to be an absorbing state: ", RED, True),
        ("zero scored spread means this selector had no directional choice; it says nothing about other judges, other "
         "axes, or more rounds. Four rounds, one run per starting state — no claim beyond that.", INK, False),
    ], 15.5, 168)
    hh = (tend - ty) + 6
    b.append(box(70, ty, W - 140, hh, KEY_FILL, INK, 2.5))
    b.append(tt)

    cy = ty + hh + 30
    t, cend = text_block(92, cy,
                         "Measurement recipes — free-generation risk: the fraction of 96 valid free-form answers "
                         "(12 fixed evaluation gamble items × both answer orders × 4 sampled answers) whose terminal "
                         "choice is the gamble. Pool spread: the mean over the 12 training-loop items of the within-item "
                         "standard deviation of the six candidates’ risk scores. Kept-minus-pool gap: the mean risk of the "
                         "2 kept candidates minus the mean risk of all 6, averaged over items. Starting states: railed "
                         "endpoints of the OLMo release program (base-hold vintage at 0.875; press vintage at 1.000). Data: "
                         "experiments/modal_k2_release/output/k2rel_oracle_hold_s21.json and _s22.json; report "
                         "docs/report_crossfamily_oracle.md.", 13, 176, GRAY)
    b.append(t)

    doc = svg_doc(W, cend + 24, "\n".join(b))
    out = os.path.join(FIGDIR, "result_crossfamily_oracle.svg")
    with open(out, "w") as f:
        f.write(doc)
    print("wrote", out)


if __name__ == "__main__":
    main()
