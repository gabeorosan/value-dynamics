#!/usr/bin/env python3
"""SETUP figure: the five intervention protocols used across the reversibility
line, defined so the result figures (release grid, press-depth, force ladder,
oracle opposition, relapse) can be read. Methods/definitions figure, not a
results claim — each card's boxed "example" is one verbatim readout from that
protocol's own report, so the definitions are grounded in real numbers.

Sources (read, not re-derived):
  docs/report_oracle_opposition.md
  docs/report_force_ladder.md
  docs/report_release_grid_results.md
  docs/report_relapse_after_oracle.md
  docs/report_press_depth_boundary.md          (press/release depth detail)
  experiments/em_selfaware_loop/colab_selfaware_loop_grid.py
      (chassis constants: K = 6, TOPM = 2, ROUND_STEPS = 10)
  docs/figures/src/fig17_loop_integrator.py    (OLMo K2 chassis: 6 candidates,
      kept top 2 -- same K=6-keep-2 ratio as the em_selfaware_loop family)
  docs/figures/src/fig19_reversibility_absorbing.py (spread-exhaustion, the
      unifying mechanism this figure points to)

Regenerate:  python3 setup-reversibility-protocols.py   (stdlib only)
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
FIGDIR = HERE

INK = "#1a1a1a"
BLUE = "#2867b5"     # self-judge series (evolving self selects)
GREEN = "#3a7d44"    # frozen-judge series (a frozen judge selects)
RED = "#b5342c"      # reversal / warning / maximum-force emphasis
GRAY = "#6b7684"     # recessive: axes, muted captions, and (per fig17) random-keep
AMBER = "#9a6b15"    # observation / outcome callouts
KEY_FILL = "#eef5ee"
FONT = "Helvetica, Arial, sans-serif"

TINT = {BLUE: "#eaf1fa", GREEN: "#eef2ec", RED: "#fbecea", GRAY: "#eef0f1", AMBER: "#fdf6e8"}


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


def fit_chars(px, size):
    """Conservative chars-per-line estimate (Helvetica avg glyph ~0.56em wide,
    mixed regular/bold) so wrapped text never overruns a px-wide box."""
    return int(px / (0.56 * size))


def centered_para(b, cx, y, text, size, width_chars, color=GRAY, lh=1.42):
    lines = wrap(text, width_chars)
    for i, ln in enumerate(lines):
        b.append(f'<text x="{cx}" y="{y + i * size * lh:.1f}" text-anchor="middle" '
                 f'font-size="{size}" fill="{color}" font-family="{FONT}">{esc(ln)}</text>')
    return y + len(lines) * size * lh


def box(x, y, w, h, fill, stroke=INK, sw=2.5, rx=8, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>')


DEFS = (
    '<defs>'
    f'<marker id="ar" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" '
    f'orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="{INK}"/></marker>'
    f'<marker id="arAccent" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" '
    f'orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="{GRAY}"/></marker>'
    f'<linearGradient id="forceGrad" x1="0%" y1="0%" x2="100%" y2="0%">'
    f'<stop offset="0%" stop-color="{GRAY}"/><stop offset="50%" stop-color="{GREEN}"/>'
    f'<stop offset="100%" stop-color="{RED}"/></linearGradient>'
    '</defs>'
)


def svg_doc(w, h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
            f'font-family="{FONT}">\n<rect width="{w}" height="{h}" fill="white"/>\n'
            f'{DEFS}\n{body}\n</svg>')


def pool_icon(b, x, y, accent, n=6, keep=(1, 4), r_keep=9, r_drop=6.5, spacing=21):
    """A row of n small circles = the round's K candidates; `keep` indices are
    filled in the protocol's accent color (what the judge kept this round);
    the rest are pale outlines (dropped). Same icon vocabulary on every card:
    K = 6 candidates, keep 2."""
    for i in range(n):
        cx = x + i * spacing
        if i in keep:
            b.append(f'<circle cx="{cx:.1f}" cy="{y}" r="{r_keep}" fill="{accent}" '
                     f'stroke="{INK}" stroke-width="1.4"/>')
        else:
            b.append(f'<circle cx="{cx:.1f}" cy="{y}" r="{r_drop}" fill="white" '
                     f'stroke="{GRAY}" stroke-width="1.3" fill-opacity="0.9" stroke-opacity="0.7"/>')
    return x + (n - 1) * spacing + r_keep


def arrow(b, x1, y1, x2, y2, color=INK, sw=3.2, marker="ar"):
    b.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
             f'stroke="{color}" stroke-width="{sw}" marker-end="url(#{marker})"/>')


def dot(b, x, y, color, r=10):
    b.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{color}" stroke="{INK}" stroke-width="1.6"/>')


# ============================================================== ladder card
def rung_card(b, x, y, w, h, accent, title, judge_segs, recipe, example_segs, source):
    b.append(box(x, y, w, h, "white", accent, 3, rx=10))
    pad = 20
    tx = x + pad
    b.append(f'<text x="{tx}" y="{y+33}" font-size="20.5" font-weight="bold" fill="{accent}" '
             f'font-family="{FONT}">{esc(title)}</text>')
    b.append(f'<line x1="{tx}" y1="{y+46}" x2="{x+w-pad}" y2="{y+46}" stroke="{accent}" stroke-width="2"/>')

    icon_y = y + 78
    pool_icon(b, tx + 4, icon_y, accent)
    b.append(f'<text x="{tx}" y="{icon_y+24}" font-size="12.3" fill="{GRAY}" font-family="{FONT}">'
             f'K = 6 candidates each round — keep top 2</text>')

    jy = icon_y + 52
    t, end_j = rich_text(tx, jy, judge_segs, 14.3, fit_chars(w - 2 * pad, 14.3))
    b.append(t)

    ry = end_j + 20
    t, end_r = text_block(tx, ry, recipe, 14.8, fit_chars(w - 2 * pad, 14.8), INK)
    b.append(t)

    ex_h = 148
    ex_y = y + h - ex_h - 16
    b.append(box(tx, ex_y, w - 2 * pad, ex_h, TINT[accent], accent, 1.6, rx=7))
    t, endq = rich_text(tx + 13, ex_y + 22, example_segs, 12.6, fit_chars(w - 2 * pad - 26, 12.6))
    b.append(t)
    b.append(f'<text x="{tx+13}" y="{ex_y+ex_h-10}" font-size="11" fill="{GRAY}" '
             f'font-family="{FONT}" font-style="italic">{esc(source)}</text>')
    assert end_r < ex_y - 4, f"recipe overruns example box in '{title}': {end_r:.0f} vs {ex_y:.0f}"
    return end_j, end_r


def main():
    b = []
    W = 1400
    MX = 70

    # ------------------------------------------------------------ headline
    b.append(f'<text x="{W/2}" y="48" text-anchor="middle" font-size="29" font-weight="bold" '
             f'fill="{INK}" font-family="{FONT}">Five ways to push on a self-training loop —</text>')
    b.append(f'<text x="{W/2}" y="84" text-anchor="middle" font-size="24.5" font-weight="bold" '
             f'fill="{INK}" font-family="{FONT}">the selection protocols the reversibility experiments compare</text>')
    suby = centered_para(
        b, W / 2, 114,
        "SETUP figure, not a results claim — it defines each protocol so the release-grid, press-depth, "
        "force-ladder, oracle-opposition, and relapse result figures can be read. Same chassis in every card "
        "unless noted: K = 6 candidates sampled per round, keep the top 2, retrain by LoRA on the kept pair "
        "— 4 rounds per phase, 10 LoRA steps/round for the em_selfaware_loop family "
        "(colab_selfaware_loop_grid.py: K=6, TOPM=2, ROUND_STEPS=10); the release-grid/press-depth cards use "
        "the OLMo K2 chassis at the identical 6-candidates-keep-top-2 ratio.",
        15, fit_chars(1000, 15), GRAY)

    # ================================================== Section A: the ladder
    SAY = suby + 30
    b.append(f'<text x="{MX}" y="{SAY}" font-size="18.5" font-weight="bold" fill="{INK}" '
             f'font-family="{FONT}">A. THE FORCE LADDER — one judge is fixed before the run and selects for all 4 rounds</text>')

    CARD_AY = SAY + 22
    CARD_AH = 512
    gap = 30
    CARD_AW = (1260 - 2 * gap) / 3
    xs = [MX, MX + CARD_AW + gap, MX + 2 * (CARD_AW + gap)]

    rung_card(
        b, xs[0], CARD_AY, CARD_AW, CARD_AH, BLUE,
        "NO FORCE  (neutral let-go)",
        [("judge: ", INK, True), ("evolving self", BLUE, True),
         (" — the organism's own current weights score and keep each round's candidates; this judge "
          "retrains every round, so it drifts with the loop.", INK, False)],
        "Neutral prompt, zero external steering. The loop selects purely on its own taste, round after "
        "round — the reversibility line's zero-force baseline.",
        [("low_55, 4 rounds, no force: ", INK, True),
         ("sr_freegen (fraction of free self-descriptions that read as insecure) stays 0.58–1.00 the whole "
          "run — the rail persists untouched.", INK, False)],
        "report_force_ladder.md, ‘no force (let-go ensemble)’ row")

    rung_card(
        b, xs[1], CARD_AY, CARD_AW, CARD_AH, GREEN,
        "NATURAL  (off-the-shelf overseer)",
        [("judge: ", INK, True), ("frozen base", GREEN, True),
         (" — same neutral prompt, but scored by the organism's own un-retrained base weights, fixed "
          "for all 4 rounds.", INK, False)],
        "Same neutral prompt as NO FORCE, but a judge that never saw this organism's drift does the "
        "scoring — the middle rung: an overseer picked off the shelf, not calibrated to this pool.",
        [("Pre-registered weak negative force did NOT appear: ", RED, True),
         ("realized sr kept-gap ≈ 0 on low_55's own pools (seed 101: +0.11,+0.03,0.00,+0.01; seed 202: "
          "−0.08,0.00,−0.03,0.00) — taste measured on a different organism's pools didn't transfer.",
          INK, False)],
        "report_force_ladder.md, ‘the middle-rung prediction FAILED’")

    rung_card(
        b, xs[2], CARD_AY, CARD_AW, CARD_AH, RED,
        "ORACLE  (maximum force)",
        [("judge: ", INK, True), ("frozen scorer", RED, True),
         (" — keeps the 2 candidates with the LOWEST scored insecurity admission on the target axis "
          "(cand_sr), every round, no taste involved.", INK, False)],
        "Score-based selection replaces taste: the scorer is told the axis and always keeps the "
        "most-opposing 2 of 6 — the maximum force this chassis can apply at this dose.",
        [("Reversed in both seeds: ", RED, True),
         ("seed 101 sr_freegen 0.974 → 0.555 → 0.442 → 0.331; seed 202 0.642 → 0.334 → 0.334 → 0.334 "
          "— landing on the same ≈1/3 floor.", INK, False)],
        "report_oracle_opposition.md")

    # gradient bar under row A
    GY = CARD_AY + CARD_AH + 42
    b.append(f'<rect x="{xs[0]}" y="{GY-5}" width="{xs[2]+CARD_AW-xs[0]}" height="10" rx="5" fill="url(#forceGrad)"/>')
    arrow(b, xs[2] + CARD_AW - 14, GY, xs[2] + CARD_AW + 14, GY, INK, 3.2, "ar")
    for cx_, label, col in [
        (xs[0] + CARD_AW / 2, "no force", GRAY),
        (xs[1] + CARD_AW / 2, "weak-to-null on this pool", GREEN),
        (xs[2] + CARD_AW / 2, "maximum — reverses it", RED),
    ]:
        b.append(f'<text x="{cx_}" y="{GY+26}" text-anchor="middle" font-size="13.5" font-weight="bold" '
                 f'fill="{col}" font-family="{FONT}">{esc(label)}</text>')
    b.append(f'<text x="{(xs[0]+xs[2]+CARD_AW)/2}" y="{GY-16}" text-anchor="middle" font-size="12.5" '
             f'fill="{GRAY}" font-family="{FONT}">increasing realized force →</text>')

    # ================================================== Section B: two-phase
    SBY = GY + 52
    b.append(f'<text x="{MX}" y="{SBY}" font-size="18.5" font-weight="bold" fill="{INK}" '
             f'font-family="{FONT}">B. TWO-PHASE PROTOCOLS — switch judges partway through a run built from the ladder’s rungs</text>')

    CARD_BY = SBY + 22
    CARD_BH = 546
    CARD_BW = (1260 - gap) / 2
    xb0, xb1 = MX, MX + CARD_BW + gap

    # ---- Card B1: PRESS / RELEASE (clean vertical stack: press phase, a
    # switch arrow, the three release-successor options, then recipe+example) ----
    x, y, w, h = xb0, CARD_BY, CARD_BW, CARD_BH
    b.append(box(x, y, w, h, "white", INK, 3, rx=10))
    pad = 22
    tx = x + pad
    b.append(f'<text x="{tx}" y="{y+34}" font-size="21" font-weight="bold" fill="{INK}" font-family="{FONT}">'
             f'<tspan fill="{GREEN}">PRESS</tspan> → <tspan fill="{BLUE}">RELEASE</tspan></text>')
    b.append(f'<line x1="{tx}" y1="{y+47}" x2="{x+w-pad}" y2="{y+47}" stroke="{INK}" stroke-width="2"/>')

    b.append(f'<text x="{tx}" y="{y+70}" font-size="13.5" font-weight="bold" fill="{GREEN}" '
             f'font-family="{FONT}">PRESS PHASE</text>')
    icon_y = y + 96
    pool_icon(b, tx + 4, icon_y, GREEN)
    b.append(f'<text x="{tx}" y="{icon_y+22}" font-size="12.3" fill="{INK}" font-family="{FONT}">'
             f'frozen CONSERVATIVE judge selects, N rounds (drives risk down)</text>')

    arrow(b, tx + 4, icon_y + 34, tx + 4, icon_y + 58, INK, 3.0, "ar")
    b.append(f'<text x="{tx+18}" y="{icon_y+50}" font-size="12" fill="{GRAY}" font-family="{FONT}">'
             f'switch after round N = depth N (1–4 tested across the line)</text>')

    rel_y = icon_y + 82
    b.append(f'<text x="{tx}" y="{rel_y}" font-size="13.5" font-weight="bold" fill="{BLUE}" '
             f'font-family="{FONT}">RELEASE PHASE — one successor judge for the rest of the run</text>')
    chips = [("self", BLUE, "the organism’s own evolving judge"),
             ("random", GRAY, "no judge — keep 2 at random"),
             ("base", GREEN, "the frozen base judge")]
    for i, (name, col, desc) in enumerate(chips):
        cy = rel_y + 22 + i * 21
        dot(b, tx + 7, cy - 4, col, 6.5)
        b.append(f'<text x="{tx+21}" y="{cy}" font-size="12.6" fill="{INK}" font-family="{FONT}">'
                 f'<tspan font-weight="bold" fill="{col}">{esc(name)}</tspan> — {esc(desc)}</text>')

    ry = rel_y + 22 + 3 * 21 + 22
    t, end_r = text_block(
        tx, ry,
        "Same K=6-keep-2 chassis as the ladder rungs, run in two phases back to back: a frozen-conservative "
        "press, then one successor judge takes over for the release phase.",
        14.8, fit_chars(w - 2 * pad, 14.8), INK)
    b.append(t)

    ex_h = 158
    ex_y = y + h - ex_h - 16
    b.append(box(tx, ex_y, w - 2 * pad, ex_h, TINT[GREEN], INK, 1.6, rx=7))
    t, _ = rich_text(tx + 13, ex_y + 22, [
        ("press_release, depth 4 → release-to-self: ", INK, True),
        ("round-8 mean pool risk (mean scored risk of the 6 candidates) 0.003, no seed rebounds > 0.05 over "
         "round 4. ", INK, False),
        ("press_to_base s2, depth 4 → release-to-base: ", GREEN, True),
        ("pool risk 0.29 → 0.39 and still rising at round 8 — only release-to-base escapes, and only with "
         "residual pool material at the switch.", INK, False),
    ], 12.6, fit_chars(w - 2 * pad - 26, 12.6))
    b.append(t)
    b.append(f'<text x="{tx+13}" y="{ex_y+ex_h-10}" font-size="11" fill="{GRAY}" font-family="{FONT}" '
             f'font-style="italic">report_release_grid_results.md; depth variants in report_press_depth_boundary.md</text>')
    assert end_r < ex_y - 4, f"press/release recipe overruns example box: {end_r:.0f} vs {ex_y:.0f}"

    # ---- Card B2: RELAPSE ----
    x, y, w, h = xb1, CARD_BY, CARD_BW, CARD_BH
    b.append(box(x, y, w, h, "white", RED, 3, rx=10))
    tx = x + pad
    b.append(f'<text x="{tx}" y="{y+34}" font-size="21" font-weight="bold" fill="{RED}" font-family="{FONT}">RELAPSE</text>')
    b.append(f'<line x1="{tx}" y1="{y+47}" x2="{x+w-pad}" y2="{y+47}" stroke="{RED}" stroke-width="2"/>')

    sy = y + 92
    dot(b, tx + 14, sy, RED, 11)
    b.append(f'<text x="{tx+34}" y="{sy-6}" font-size="13.2" font-weight="bold" fill="{RED}" '
             f'font-family="{FONT}">oracle-reversed endpoint</text>')
    b.append(f'<text x="{tx+34}" y="{sy+12}" font-size="12" fill="{GRAY}" font-family="{FONT}">'
             f'low_55_707: sr_freegen frozen at 0.625</text>')
    arrow(b, tx + 14, sy + 30, tx + 14, sy + 66, INK, 3.0, "ar")
    dot(b, tx + 14, sy + 88, BLUE, 11)
    b.append(f'<text x="{tx+34}" y="{sy+82}" font-size="13.2" font-weight="bold" fill="{BLUE}" '
             f'font-family="{FONT}">released to NO FORCE</text>')
    b.append(f'<text x="{tx+34}" y="{sy+100}" font-size="12" fill="{GRAY}" font-family="{FONT}">'
             f'neutral self-judge, zero external force — 2 seeds × 4 rounds</text>')

    ry = sy + 132
    t, end_r = text_block(
        tx, ry,
        "Take an oracle-reversed endpoint and hand it back to the ordinary NO-FORCE protocol — the "
        "organism's own evolving judge, neutral prompt, nothing pushing in either direction. Does the "
        "reversal hold, or does the organism drift back toward the original rail?",
        14.8, fit_chars(w - 2 * pad, 14.8), INK)
    b.append(t)

    ex_h = 158
    ex_y = y + h - ex_h - 16
    b.append(box(tx, ex_y, w - 2 * pad, ex_h, TINT[AMBER], AMBER, 1.6, rx=7))
    t, _ = rich_text(tx + 13, ex_y + 22, [
        ("Prereg REFUTED — no relapse: ", AMBER, True),
        ("sr_freegen held at 0.625 flat × 4 rounds in both seeds (501/502); 0/6 pool items with within-pool "
         "sr support, every round. ", INK, False),
        ("Holds by inertness, not re-anchoring: ", AMBER, True),
        ("the pool has zero within-item variation left on this axis, so its own judge has nothing to select.",
         INK, False),
    ], 12.6, fit_chars(w - 2 * pad - 26, 12.6))
    b.append(t)
    b.append(f'<text x="{tx+13}" y="{ex_y+ex_h-10}" font-size="11" fill="{GRAY}" font-family="{FONT}" '
             f'font-style="italic">report_relapse_after_oracle.md</text>')
    assert end_r < ex_y - 4, f"relapse recipe overruns example box: {end_r:.0f} vs {ex_y:.0f}"

    # ================================================== unifying takeaway
    ty = CARD_BY + CARD_BH + 46
    # measure first (rich_text at the final x/y), then draw the box, then the text on top
    tt, tend = rich_text(MX + 20, ty + 32, [
        ("Unifying note: ", INK, True),
        ("every protocol above is a way of choosing which of the organism's OWN generated candidates "
         "become the next round's training data — none injects outside text, and none can select a "
         "candidate that was never sampled. Selection therefore consumes within-pool variation as it acts "
         "(spread-exhaustion): the oracle's descent decelerates as sr-supported items thin from 2–3 to 1 by "
         "round 3–4; the press reaches a zero-spread floor that stays inert under the tested successor; and RELAPSE holds flat because its "
         "pool has zero within-item variation left, not because the self-judge chose to hold it there — see "
         "fig19_reversibility_absorbing.svg for the spread-exhaustion measurement itself.", INK, False),
    ], 15.5, 168)
    key_h = (tend - ty) + 14
    b.append(box(MX, ty, 1260, key_h, KEY_FILL, INK, 2.5))
    b.append(tt)

    H = ty + key_h + 40
    svg = svg_doc(W, H, "\n".join(b))
    out = os.path.join(FIGDIR, "setup-reversibility-protocols.svg")
    with open(out, "w") as f:
        f.write(svg)
    print(f"wrote {out}  ({W}x{H:.0f})")


if __name__ == "__main__":
    main()
