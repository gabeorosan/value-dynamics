#!/usr/bin/env python3
"""Figures for the CURRENTLY PLANNED experiments and analyses.

Source of truth: docs/updated_research_plan_2026-07-10.md (authoritative plan)
plus the Phase-0 screen results that have landed since
(experiments/phase0_screen/output/phase0_screen.json, STATE 2026-07-10 entries).

House style follows docs/figures/make_figures.py (white background, big bold
headline, KEY_FILL takeaway box, status chips like fig12). Regenerate with:
    python3 make_plan_figures.py
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..", "..", "..")
PHASE0 = os.path.join(ROOT, "experiments", "phase0_screen", "output",
                      "phase0_screen.json")
CRITERION = os.path.join(ROOT, "experiments", "kaggle",
                         "kaggle_basin_criterion", "output",
                         "basin_criterion.json")

INK = "#1a1a1a"
BLUE = "#2867b5"       # evolving self-judge arm
GREEN = "#3a7d44"      # frozen-judge arms
RED = "#b5342c"        # warnings / the confound / headline emphasis
GRAY = "#6b7684"       # recessive
AMBER = "#9a6b15"      # decisions
KEY_FILL = "#eef5ee"
AMBER_TINT = "#fdf8ee"
GRAY_TINT = "#f4f4f1"
RED_TINT = "#fbf0ee"
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


def arrow(x1, y1, x2, y2, sw=4, color=INK):
    return (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" '
            f'stroke-width="{sw}" marker-end="url(#arr)"/>')


DEFS = f'''<defs><marker id="arr" viewBox="0 0 10 10" refX="9" refY="5"
 markerWidth="6" markerHeight="6" orient="auto-start-reverse">
 <path d="M 0 0 L 10 5 L 0 10 z" fill="{INK}"/></marker></defs>'''


def svg_doc(w, h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
            f'font-family="{FONT}">\n<rect width="{w}" height="{h}" fill="white"/>\n'
            f'{DEFS}\n{body}\n</svg>')


def centered(b, cx, y, text, size, color=INK, bold=False):
    w = "bold" if bold else "normal"
    b.append(f'<text x="{cx}" y="{y}" text-anchor="middle" font-size="{size}" '
             f'font-weight="{w}" fill="{color}" font-family="{FONT}">{esc(text)}</text>')


# ====================================================================
# Figure 1 — the program map: phases, gates, and the branch decision
# ====================================================================

def fig_program_map():
    W = 1400
    b = []
    centered(b, W / 2, 52, "The plan now: one clean causal result about how", 34, bold=True)
    centered(b, W / 2, 94, "judging preference steers self-training", 34, bold=True)
    centered(b, W / 2, 126, "authoritative plan 2026-07-10 (docs/updated_research_plan_2026-07-10.md) — supersedes the old run order"
             " (more legacy-loop seeds, copy-judge first, regime grid); chips show what has landed since", 16, GRAY)

    CHIP = {"done": (GREEN, "DONE"), "running": (BLUE, "IN PROGRESS"),
            "planned": (GRAY, "PLANNED"), "headline": (RED, "HEADLINE"),
            "decision": (AMBER, "DECISION")}
    X, CW = 60, W - 120

    def card(y, title, status, body_segments, fill="white", border=INK, bw=1.8):
        color, label = CHIP[status]
        t, yend = rich_text(X + 18, y + 58, body_segments, 15.5, 158)
        h = (yend - y) + 12
        b.append(box(X, y, CW, h, fill, border, bw, rx=10))
        b.append(f'<text x="{X + 18}" y="{y + 30}" font-size="19" font-weight="bold" '
                 f'fill="{INK}" font-family="{FONT}">{esc(title)}</text>')
        b.append(f'<text x="{X + CW - 16}" y="{y + 29}" text-anchor="end" font-size="13.5" '
                 f'font-weight="bold" fill="{color}" font-family="{FONT}">{label}</text>')
        b.append(t)
        return y + h

    y = 158
    # ---- Phase 0 (done) --------------------------------------------
    y2 = card(y, "Phase 0 — repaired-instrument screen (Colab, complete 2026-07-10)", "done", [
        ("The rebuilt coordinate (order-balanced probe, generated-choice + invalid-rate reads, EV-unequal factual gate) "
         "screened both substrates before any seeds are spent. ", INK, False),
        ("Base Qwen answers by position, not content:", RED, True),
        (" it picks the gamble at 0.94 when the gamble is option B but 0.31 when it is option A (order gap 0.63) — a "
         "single-order read would report a 0.94 risk-seeker. The old risk persona is order-robust (gap ~0) but saturated "
         "at 1.00, so it has nowhere to move. ", INK, False),
        ("OLMo-3-7B-Instruct passes:", GREEN, True),
        (" risk 0.72 with order gap 0.077 and headroom to move down. Every checkpoint sits near chance (0.50–0.54) on "
         "single-token expected-value arithmetic, so the absolute ≥0.90 factual gate was miscalibrated — it becomes a "
         "differential gate (accuracy must not drop after the value update) on lopsided-EV items.", INK, False),
    ])
    b.append(arrow(W / 2, y2 + 4, W / 2, y2 + 26))

    # ---- Build steps (in progress) ---------------------------------
    y = y2 + 32
    color, label = CHIP["running"]
    items = [
        ("done", "risk_harness.py — order-balanced value coordinate, per-order gap, generated-choice + "
                 "invalid rate (malformed never coded safe), EV-unequal factual bank, loop-order randomization "
                 "with kept-set balance logging (experiments/common/risk_harness.py, self-tested)"),
        ("done", "OLMo stage-flow screen — the repaired battery on the released checkpoints, inference-only. "
                 "Result: position bias collapses across the release flow (order gap 0.72 → 0.35 → 0.08; only the "
                 "final Instruct stage passes), gamble-favoring emerges at SFT and strengthens (generated gamble "
                 "fraction 0.46 → 0.58 → 0.67) while judge taste stays near-neutral (0.47 → 0.54 → 0.52) — so the "
                 "inversion starts from final Instruct, onto an almost blank judging prior"),
        ("todo", "factual-gate items rebuilt lopsided — obvious unequal-EV pairs a base model gets well above "
                 "chance, so the gate can detect deterioration"),
        ("todo", "moderate Qwen persona at risk ≈ 0.6–0.7 — replaces the saturated 1.00 organism so the anchor "
                 "can move in both directions"),
        ("todo", "OLMo conservative dose ladder — stop inside 0.25–0.40 with the factual gate and judge-taste "
                 "headroom intact; never train to zero"),
    ]
    GLYPH = {"done": ("✓", GREEN), "running": ("▶", BLUE), "todo": ("○", GRAY)}
    yy = y + 58
    parts = [f'<text x="{X + 18}" y="{y + 30}" font-size="19" font-weight="bold" fill="{INK}" '
             f'font-family="{FONT}">Instrument &amp; organism build (Colab lane, gates the Kaggle window)</text>',
             f'<text x="{X + CW - 16}" y="{y + 29}" text-anchor="end" font-size="13.5" font-weight="bold" '
             f'fill="{color}" font-family="{FONT}">{label}</text>']
    for st, txt in items:
        g, gc = GLYPH[st]
        parts.append(f'<text x="{X + 24}" y="{yy}" font-size="16" font-weight="bold" fill="{gc}" '
                     f'font-family="{FONT}">{g}</text>')
        t, yy2 = text_block(X + 48, yy, txt, 15.5, 152)
        parts.append(t)
        yy = yy2 + 6
    h = (yy - 6) - y + 12
    b.append(box(X, y, CW, h, "white", INK, 1.8, rx=10))
    b.extend(parts)
    y2 = y + h
    b.append(arrow(W / 2, y2 + 4, W / 2, y2 + 26))

    # ---- Phase 1A --------------------------------------------------
    y = y2 + 32
    y2 = card(y, "Phase 1A — Qwen clean anchor: 4 judge conditions × 4 seeds × 4 rounds  (Kaggle, ~10–14 h)", "planned", [
        ("Evolving self-judge vs frozen round-0 organism judge vs frozen base judge vs random-selection control, all "
         "cloned from the one moderate organism. Preregistered endpoint: the judge-condition × round interaction on "
         "the order-balanced coordinate — endpoint clusters (“basins”) are not a primary claim. Expands to 8 seeds "
         "only if the order and factual gates hold and the interaction is real. If neither judge contrast survives, "
         "the central judge-mechanism claim on the risk axis is retired.", INK, False),
    ])
    b.append(arrow(W / 2, y2 + 4, W / 2, y2 + 26))

    # ---- Phase 1B --------------------------------------------------
    y = y2 + 32
    y2 = card(y, "Phase 1B — OLMo conservative-judge inversion  (Kaggle, ~6–9 h smoke + 14–18 h expansion)", "headline", [
        ("Every legacy OLMo rollout railed to risk ≈ 1.0 under both judges. So install the opposite preference: ", INK, False),
        ("freeze a moderate conservative OLMo organism as judge — does it reverse the direction of self-training, "
         "where the frozen base judge drove risk up?", RED, True),
        (" A causal test of whether the judge’s evaluative preference sets the trajectory’s direction within one "
         "substrate. 3 smoke seeds gate the 6–8-seed × 4-round run.", INK, False),
    ], fill=RED_TINT, border=RED, bw=2.4)
    b.append(arrow(W / 2, y2 + 4, W / 2, y2 + 26))

    # ---- Phase 2 branch row ----------------------------------------
    y = y2 + 32
    color, label = CHIP["decision"]
    b.append(f'<text x="{X + 18}" y="{y + 30}" font-size="19" font-weight="bold" fill="{INK}" '
             f'font-family="{FONT}">Phase 2 — exactly one branch, chosen by the Phase-1 outcome</text>')
    b.append(f'<text x="{X + CW - 16}" y="{y + 29}" text-anchor="end" font-size="13.5" font-weight="bold" '
             f'fill="{color}" font-family="{FONT}">{label}</text>')
    branches = [
        ("A — deepen the judge mechanism",
         "Trigger: the two frozen judges push in opposite directions. Copy-judge vintages (frozen copies from "
         "rounds 0/2/4) and a judge-switch let-go — titrations of a proven mechanism, no longer speculative."),
        ("B — insecure code on OLMo",
         "Trigger: risk stays saturated or taste can’t be inverted, but the harness is healthy. Replicates the "
         "Qwen self-report-vs-behavior dissociation with the released data and matched benign-code control."),
        ("C — new model or axis",
         "Trigger: no usable headroom on either OLMo probe. Screen candidates inference-only; require behavior "
         "and judge taste both inside 0.2–0.8, order stability, and low invalid rate before training."),
        ("D — SFT vs DPO update rule",
         "Trigger: a clean judge-directed effect survives anywhere. Same chosen/rejected pairs, iterative DPO vs "
         "winner-only SFT: does the update rule change amplification, stability, or off-target drift?"),
    ]
    bw_, bgap = (CW - 36 - 3 * 16) / 4, 16
    yy = y + 48
    maxh = 0
    rendered = []
    for i, (title, desc) in enumerate(branches):
        bx = X + 18 + i * (bw_ + bgap)
        lines = wrap(desc, 38)
        tl = wrap(title, 34)
        hh = 10 + len(tl) * 19 + 8 + len(lines) * 18 + 12
        maxh = max(maxh, hh)
        rendered.append((bx, tl, lines))
    for bx, tl, lines in rendered:
        b.append(box(bx, yy, bw_, maxh, AMBER_TINT, AMBER, 1.6, rx=8))
        for j, ln in enumerate(tl):
            b.append(f'<text x="{bx + 12}" y="{yy + 24 + j * 19}" font-size="14.5" font-weight="bold" '
                     f'fill="{INK}" font-family="{FONT}">{esc(ln)}</text>')
        y0 = yy + 24 + len(tl) * 19 + 4
        for j, ln in enumerate(lines):
            b.append(f'<text x="{bx + 12}" y="{y0 + j * 18}" font-size="13" fill="{INK}" '
                     f'font-family="{FONT}">{esc(ln)}</text>')
    h = (yy + maxh) - y + 16
    b.append(box(X, y, CW, h, "none", INK, 1.8, rx=10))
    y2 = y + h

    # ---- parked strip ----------------------------------------------
    y = y2 + 22
    t, yend = rich_text(X + 18, y + 27, [
        ("PARKED (not in the plan): ", GRAY, True),
        ("dedicated criterion lead-lag study (cross-lag null) · 62-cell regime grid · legacy-loop Qwen seeds 16–22 "
         "and OLMo seeds 4–7 · Qwen3.5 before a repaired harness exists · any claim built on raw-factor LoRA "
         "norms/cosines", GRAY, False),
    ], 14.5, 168)
    hh = (yend - y) + 10
    b.append(box(X, y, CW, hh, GRAY_TINT, GRAY, 1.2, rx=8))
    b.append(t)
    y2 = y + hh

    # ---- key box ----------------------------------------------------
    y = y2 + 22
    t, yend = rich_text(X + 20, y + 32, [
        ("The deliverable: ", INK, True),
        ("in a position-balanced self-training loop with a factual response-bias control, changing which fixed judge "
         "selects the training data changes — or fails to change — the direction of a held-out behavioral coordinate. "
         "Frozen base vs installed conservative isolates evaluative preference; frozen conservative vs an evolving "
         "copy isolates judge–policy co-evolution.", INK, False),
    ], 17, 148)
    hh = (yend - y) + 6
    b.append(box(X, y, CW, hh, KEY_FILL, INK, 2.5))
    b.append(t)
    return svg_doc(W, y + hh + 40, "\n".join(b))


# ====================================================================
# Figure 2 — the instrument repair, with the Phase-0 numbers
# ====================================================================

def fig_instrument_repair():
    W = 1400
    d = json.load(open(PHASE0))
    qb, qr, ol = d["qwen_base"], d["qwen_risk"], d["olmo_instruct"]
    b = []
    centered(b, W / 2, 52, "Why every loop script gets rebuilt before more seeds:", 33, bold=True)
    centered(b, W / 2, 94, "the coordinate confounded value with answer position", 33, bold=True)
    centered(b, W / 2, 126, "the Phase-0 screen (2026-07-10) measured the confound directly — every number below is an actual read"
             " from experiments/phase0_screen/output/phase0_screen.json", 16, GRAY)

    colw, gap, X0 = 630, 40, 50
    ytop = 158

    def bullet_card(x, y, w, title, tcolor, items, border, fill):
        parts = [f'<text x="{x + 18}" y="{y + 30}" font-size="18" font-weight="bold" '
                 f'fill="{tcolor}" font-family="{FONT}">{esc(title)}</text>']
        yy = y + 58
        for txt in items:
            parts.append(f'<circle cx="{x + 26}" cy="{yy - 5}" r="3" fill="{tcolor}"/>')
            t, yy2 = text_block(x + 42, yy, txt, 15, 70)
            parts.append(t)
            yy = yy2 + 8
        h = (yy - 8) - y + 12
        b.append(box(x, y, w, h, fill, border, 2, rx=10))
        b.extend(parts)
        return y + h

    yl = bullet_card(X0, ytop, colw, "The legacy instrument (behind every result so far)", RED, [
        "training rows always render safe = option A, gamble = option B — self-training can install a "
        "“say B” letter habit that reads as a value shift",
        "the probe read one option order only (the order-swap patch came late and probe-side only)",
        "malformed answers were coded as choosing the safe option",
        "the factual check was numeric EV arithmetic in a different format — it cannot catch a same-template "
        "position bias",
        "weight logs concatenated raw LoRA A/B factors — not invariant to equivalent factorizations, so the "
        "thrash correlations are withdrawn pending recomputation",
    ], RED, RED_TINT)

    yr = bullet_card(X0 + colw + gap, ytop, colw, "The repaired harness (risk_harness.py) — gates every new run", GREEN, [
        "gamble position randomized in the training rows themselves; kept-set gamble fraction and A/B fraction "
        "logged independently",
        "order-balanced probe: every held-out item read with the gamble as A and as B; per-order values and the "
        "gap reported every round",
        "generated-prose choice and invalid rate as separate outcomes — a malformed answer is never coded safe",
        "same-template factual gate: “which option has the higher expected payoff?” on EV-unequal items, "
        "scored differentially (accuracy must not drop after the update)",
        "merged weight updates (ΔW = scaling·B@A) and full provenance: pinned revisions, prompt banks, "
        "per-item raw reads, persisted adapters",
    ], GREEN, "white")

    # ---- paired-bar inset: the same checkpoint read both ways -------
    y = max(yl, yr) + 30
    PX0, PX1 = 420, 1160
    PW = PX1 - PX0
    rows = [
        ("Qwen3-4B base", qb["value"]["gamble_A_order"], qb["value"]["gamble_B_order"],
         f"order gap {qb['value']['order_gap']:.2f} — FAIL", RED),
        ("Qwen risk persona (legacy organism)", 1.0, 1.0, "gap ~0, but saturated at 1.00 — no headroom", AMBER),
        ("OLMo-3-7B-Instruct", ol["value"]["gamble_A_order"], ol["value"]["gamble_B_order"],
         f"order gap {ol['value']['order_gap']:.2f} — PASS, with headroom", GREEN),
    ]
    b.append(f'<text x="{X0 + 18}" y="{y + 24}" font-size="18" font-weight="bold" fill="{INK}" '
             f'font-family="{FONT}">P(choose the gamble) on the same held-out items — read with the gamble as option A vs as option B</text>')
    yy = y + 56
    for name, va, vb, verdict, vc in rows:
        b.append(f'<text x="{PX0 - 16}" y="{yy + 14}" text-anchor="end" font-size="15" '
                 f'font-weight="bold" fill="{INK}" font-family="{FONT}">{esc(name)}</text>')
        for i, (lab, v, fill) in enumerate([("gamble as A", va, "#9aa3ad"), ("gamble as B", vb, INK)]):
            by = yy + i * 22
            b.append(f'<rect x="{PX0}" y="{by}" width="{max(2, v * PW)}" height="16" fill="{fill}"/>')
            b.append(f'<text x="{PX0 + max(2, v * PW) + 8}" y="{by + 13}" font-size="13.5" '
                     f'fill="{INK}" font-family="{FONT}">{v:.2f}  <tspan fill="{GRAY}">{lab}</tspan></text>')
        b.append(f'<text x="{PX0}" y="{yy + 60}" font-size="13.5" font-weight="bold" fill="{vc}" '
                 f'font-family="{FONT}">{esc(verdict)}</text>')
        yy += 84
    b.append(box(X0, y, W - 100, yy - y - 4, "none", GRAY, 1.2, rx=10))
    y2 = yy + 16

    t, yend = rich_text(X0 + 20, y2 + 32, [
        ("One inference-only screen caught what forty legacy rollouts could not show: ", INK, True),
        ("the base model’s coordinate was dominated by position preference (0.94 vs 0.31 on identical content), the "
         "trained persona had no headroom, and every checkpoint is at chance on single-token EV arithmetic — so the "
         "factual gate itself needed redesign. Gates now precede seeds: no multi-seed run launches on an instrument "
         "that fails them.", INK, False),
    ], 17, 148)
    hh = (yend - y2) + 6
    b.append(box(X0, y2, W - 100, hh, KEY_FILL, INK, 2.5))
    b.append(t)
    return svg_doc(W, y2 + hh + 40, "\n".join(b))


# ====================================================================
# Figure 3 — Phase 1A: the four-judge Qwen anchor and its contrasts
# ====================================================================

def fig_qwen_anchor():
    W = 1400
    b = []
    centered(b, W / 2, 52, "Phase 1A — the Qwen anchor: four judges, one organism,", 33, bold=True)
    centered(b, W / 2, 94, "and what each contrast identifies", 33, bold=True)
    centered(b, W / 2, 126, "4 seeds × 4 rounds on the repaired harness; a harness validation and replacement baseline,"
             " not a rescue of the old basin narrative", 16, GRAY)

    # organism box (left)
    ox, oy, ow, ohh = 60, 220, 330, 190
    b.append(box(ox, oy, ow, ohh, "white", INK, 2.4, rx=10))
    t, _ = text_block(ox + 18, oy + 32, "one moderate risk organism", 18, 30, weight="bold")
    b.append(t)
    t, _ = text_block(ox + 18, oy + 62,
                      "re-trained on position-balanced rows, target risk ≈ 0.6–0.7. The legacy persona sat "
                      "saturated at 1.00 — order-robust but with nowhere to move. Moderation buys headroom "
                      "in both directions.", 14.5, 40)
    b.append(t)

    arms = [
        ("evolving self-judge", BLUE, "white",
         "the adapter being trained judges its own candidates — judge and policy co-evolve round over round", None),
        ("frozen round-0 organism judge", GREEN, "white",
         "a frozen copy of the starting organism judges every round — the control every legacy run lacked", None),
        ("frozen base judge", GREEN, "white",
         "the unadapted base model judges throughout — the legacy “frozen judge” condition, kept for continuity", "6 3"),
        ("random-selection control", GRAY, GRAY_TINT,
         "same candidate supply and update dose, no judge — the generic self-training-drift floor", None),
    ]
    ax, aw = 490, 480
    ay, agap = 180, 14
    arm_ys = []
    for name, color, fill, desc, dash in arms:
        lines = wrap(desc, 62)
        hh = 44 + len(lines) * 19 + 8
        dd = f' stroke-dasharray="{dash}"' if dash else ""
        b.append(f'<rect x="{ax}" y="{ay}" width="{aw}" height="{hh}" rx="10" fill="{fill}" '
                 f'stroke="{color}" stroke-width="2.6"{dd}/>')
        b.append(f'<text x="{ax + 16}" y="{ay + 28}" font-size="17" font-weight="bold" fill="{color}" '
                 f'font-family="{FONT}">{esc(name)}</text>')
        for j, ln in enumerate(lines):
            b.append(f'<text x="{ax + 16}" y="{ay + 52 + j * 19}" font-size="14" fill="{INK}" '
                     f'font-family="{FONT}">{esc(ln)}</text>')
        arm_ys.append((ay, ay + hh))
        ay += hh + agap
    # arrows organism -> arms
    for y0, y1 in arm_ys:
        b.append(arrow(ox + ow, oy + ohh / 2, ax - 8, (y0 + y1) / 2, sw=3))

    # contrast rows (right column, fixed slots; thin connectors to the two arms)
    contrasts = [
        (0, 1, "co-evolution", "does letting the judge drift with the policy add anything "
                               "beyond its round-0 taste? (the clean version of “self-judging diverges”)"),
        (1, 2, "judge taste", "does an installed preference in a frozen judge move the "
                              "trajectory differently from the base model’s preference?"),
        (0, 3, "selection at all", "is judge-directed selection different from training on "
                                   "your own samples without a judge?"),
    ]
    cx = ax + aw + 60
    top, bot = arm_ys[0][0], arm_ys[-1][1]
    slot_h = (bot - top) / 3
    for k, (i0, i1, name, desc) in enumerate(contrasts):
        sy = top + k * slot_h + 14
        b.append(f'<text x="{cx + 14}" y="{sy + 18}" font-size="16" font-weight="bold" fill="{INK}" '
                 f'font-family="{FONT}">{esc(name)}</text>')
        for j, ln in enumerate(wrap(desc, 44)):
            b.append(f'<text x="{cx + 14}" y="{sy + 40 + j * 17}" font-size="13" fill="{GRAY}" '
                     f'font-family="{FONT}">{esc(ln)}</text>')
        # connectors from the two compared arms to this row's anchor point
        ay0 = (arm_ys[i0][0] + arm_ys[i0][1]) / 2
        ay1 = (arm_ys[i1][0] + arm_ys[i1][1]) / 2
        anchor_y = sy + 12
        bend = cx - 24 + k * 9
        for ayy in (ay0, ay1):
            b.append(f'<path d="M {ax + aw + 4} {ayy} H {bend} V {anchor_y} H {cx + 6}" '
                     f'stroke="{GRAY}" stroke-width="1.4" fill="none"/>')
        b.append(f'<circle cx="{cx + 8}" cy="{anchor_y}" r="3" fill="{INK}"/>')

    y2 = max(ay, oy + ohh) + 18
    t, yend = rich_text(80, y2 + 32, [
        ("Preregistered endpoint: ", INK, True),
        ("the judge-condition × round interaction on the order-balanced coordinate — “basins” are not a "
         "primary claim, and the rollout seed is the unit of replication. Expand to 8 seeds only on passing "
         "gates. If neither judge contrast survives, the judge-mechanism claim on the risk axis is retired — "
         "that outcome is also a result.", INK, False),
    ], 17, 148)
    hh = (yend - y2) + 6
    b.append(box(60, y2, W - 120, hh, KEY_FILL, INK, 2.5))
    b.append(t)
    return svg_doc(W, y2 + hh + 40, "\n".join(b))


# ====================================================================
# Figure 4 — Phase 1B: the OLMo conservative-judge inversion
# ====================================================================

def fig_olmo_inversion():
    W = 1400
    b = []
    centered(b, W / 2, 52, "Phase 1B — the OLMo inversion: turning a saturated substrate", 33, bold=True)
    centered(b, W / 2, 94, "into a causal test of the judge’s preference", 33, bold=True)
    centered(b, W / 2, 126, "every legacy OLMo rollout railed to risk ≈ 1.0 under BOTH judges — so install the opposite"
             " preference and ask whether the direction of self-training flips", 16, GRAY)

    steps = [
        ("1 · stage screen  (done)", GREEN,
         "The repaired battery on OLMo 3’s released stages, inference-only, pinned revisions. Result: position "
         "bias collapses across the release flow (order gap 0.72 → 0.35 → 0.08) and only the final Instruct "
         "stage passes; gamble-favoring emerges at SFT and strengthens (generated gamble 0.46 → 0.58 → 0.67) "
         "while judge taste stays near-neutral throughout (0.47 → 0.54 → 0.52). Start from final Instruct — "
         "risk 0.72 with headroom down, and an almost blank judging prior to install the conservative "
         "preference onto."),
        ("2 · install a moderate conservative organism", INK,
         "Randomized A/B positions, stochastic item-dependent conservative choices. The dose ladder STOPS when "
         "order-balanced risk reaches 0.25–0.40 with the factual gate and output validity intact and the "
         "cautious-vs-bold judge taste showing headroom. Never trained to zero — the experiment needs room to "
         "move in both directions."),
        ("3 · clone into four arms", INK,
         "The identical conservative adapter starts every arm: evolving self-judge / frozen conservative judge / "
         "frozen base OLMo judge / random-selection control. Common prompt banks, aligned seed schedules. 3 smoke "
         "seeds gate the 6–8-seed × 4-round expansion."),
        ("4 · read the interaction", INK,
         "Primary endpoint: judge condition × round on the order-balanced coordinate. Secondary: kept-pool "
         "semantic composition, judge taste, factual EV gate, invalid rate, merged weight updates "
         "(ΔW = scaling·B@A)."),
    ]
    sw_, sgap, X0 = 316, 16, 50
    y = 168
    rendered = []
    maxh = 0
    for i, (title, tc, desc) in enumerate(steps):
        lines = wrap(desc, 44)
        tl = wrap(title, 36)
        hh = 20 + len(tl) * 22 + 8 + len(lines) * 18 + 14
        maxh = max(maxh, hh)
        rendered.append((X0 + i * (sw_ + sgap), title, tc, tl, lines))
    for sx, title, tc, tl, lines in rendered:
        b.append(box(sx, y, sw_, maxh, "white", INK, 1.8, rx=10))
        for j, ln in enumerate(tl):
            b.append(f'<text x="{sx + 14}" y="{y + 28 + j * 22}" font-size="15.5" font-weight="bold" '
                     f'fill="{tc}" font-family="{FONT}">{esc(ln)}</text>')
        y0 = y + 28 + len(tl) * 22 + 6
        for j, ln in enumerate(lines):
            b.append(f'<text x="{sx + 14}" y="{y0 + j * 18}" font-size="13" fill="{INK}" '
                     f'font-family="{FONT}">{esc(ln)}</text>')
    for i in range(3):
        sx = X0 + i * (sw_ + sgap)
        b.append(arrow(sx + sw_ + 1, y + maxh / 2, sx + sw_ + sgap - 1, y + maxh / 2, sw=3.5))

    # ---- preregistered interpretation table -------------------------
    ty = y + maxh + 34
    b.append(f'<text x="{X0 + 8}" y="{ty}" font-size="20" font-weight="bold" fill="{INK}" '
             f'font-family="{FONT}">Preregistered readings — written down before the run</text>')
    rows = [
        ("frozen base pushes risk up; frozen conservative pushes it down",
         "installed judge preference causally controls the direction of self-training within one substrate — the headline result", RED),
        ("conservative behavior moved, but BOTH frozen judges still push risk up",
         "behavior and evaluative preference dissociate; OLMo’s judging prior dominates whatever the organism does", INK),
        ("frozen conservative stays cautious; the evolving self drifts back toward risk",
         "the criterion itself drifts during self-training — co-evolution is the active ingredient", INK),
        ("all judge-directed arms stay cautious",
         "the conservative adapter changes the candidate supply strongly enough that judge identity is secondary", INK),
        ("random selection matches the judge-directed arms",
         "the motion is generic self-training drift, not selection on judge preference — the deflationary reading", INK),
    ]
    yy = ty + 20
    cw1, cw2 = 560, 700
    for outcome, reading, rc in rows:
        l1 = wrap(outcome, 62)
        l2 = wrap(reading, 78)
        hh = max(len(l1), len(l2)) * 19 + 18
        b.append(f'<rect x="{X0}" y="{yy}" width="{cw1 + cw2 + 40}" height="{hh}" fill='
                 f'"{"white" if rc == INK else RED_TINT}" stroke="{GRAY}" stroke-width="0.8"/>')
        for j, ln in enumerate(l1):
            b.append(f'<text x="{X0 + 14}" y="{yy + 24 + j * 19}" font-size="14" font-weight="bold" '
                     f'fill="{rc}" font-family="{FONT}">{esc(ln)}</text>')
        for j, ln in enumerate(l2):
            b.append(f'<text x="{X0 + cw1 + 34}" y="{yy + 24 + j * 19}" font-size="14" fill="{INK}" '
                     f'font-family="{FONT}">{esc(ln)}</text>')
        yy += hh
    b.append(f'<text x="{X0 + 14}" y="{ty + 14 + 2}" font-size="0" fill="none"> </text>')

    y2 = yy + 24
    t, yend = rich_text(X0 + 20, y2 + 32, [
        ("Why this is the headline: ", INK, True),
        ("it is the first arm of the project where the judge’s preference is set by construction rather than "
         "inherited — if the frozen conservative judge pulls risk down where the frozen base judge pushed it up, "
         "evaluative preference is a causal driver, measured on an instrument that already survived its own "
         "position-bias audit.", INK, False),
    ], 17, 148)
    hh = (yend - y2) + 6
    b.append(box(X0, y2, W - 100, hh, KEY_FILL, INK, 2.5))
    b.append(t)
    return svg_doc(W, y2 + hh + 40, "\n".join(b))


# ====================================================================
# Figure 5 — analyses pre-registered to ride the Phase-1 data
# ====================================================================

def fig_riding_analyses():
    W = 1400
    b = []
    centered(b, W / 2, 52, "Analyses pre-registered to ride the Phase-1 data — no extra GPU", 33, bold=True)
    centered(b, W / 2, 92, "each one re-reads what the new scripts persist anyway: per-item, per-order raw probe reads,"
             " judge taste per round, merged weight deltas", 16, GRAY)

    X0, CW = 60, W - 120

    def card(y, title, body_segments, extra_h=0, extra=None):
        parts = [f'<text x="{X0 + 18}" y="{y + 30}" font-size="18" font-weight="bold" '
                 f'fill="{INK}" font-family="{FONT}">{esc(title)}</text>']
        t, yend = rich_text(X0 + 18, y + 58, body_segments, 15, 118)
        parts.append(t)
        h = (yend - y) + 14 + extra_h
        b.append(box(X0, y, CW, h, "white", INK, 1.8, rx=10))
        b.extend(parts)
        if extra:
            b.append(extra(y))
        return y + h

    y = 124
    y = card(y, "Drift-field refit — does the no-saddle picture survive a de-biased coordinate?", [
        ("The first fit (report_basin_drift_field.md) found one weak attractor per judge — self x* = 0.35, frozen "
         "x* = 0.12 — but on the position-confounded coordinate, with R² ≈ 0.05–0.09 and a known "
         "regression-to-the-mean bias. On Phase-1 trajectories: ", INK, False),
        ("(a)", INK, True), ("refit Δx = a·x + b on the order-balanced coordinate — the frozen x* = 0.12 is the "
         "number most at risk of moving; ", INK, False),
        ("(b)", INK, True), ("fixed point per judge arm — “the judge sets the attractor’s location” becomes a "
         "prediction instead of a post-hoc read; ", INK, False),
        ("(c)", INK, True), ("subtract the coordinate’s binomial measurement noise from the per-state spread — is the "
         "residual process noise state-dependent?; ", INK, False),
        ("(d)", INK, True), ("add judge taste to the state vector — co-evolution as an off-diagonal coupling.", INK, False),
    ]) + 18

    y = card(y, "Weight geometry, recomputed on merged updates", [
        ("The thrash correlations (more total LoRA motion ↔ less behavioral change, r = −0.66; update-direction "
         "persistence ↔ extreme fate, +0.51) are ", INK, False),
        ("withdrawn pending recomputation", RED, True),
        (" — they were computed on raw A/B factor norms, which are not invariant to equivalent LoRA factorizations. "
         "New scripts log ΔW = scaling·B@A per round. Preregistered: behavior tracks net displacement positively "
         "while anti-correlating with path length; the round where update directions lock in is the early-warning "
         "candidate (round-1 update size is already ruled out, +0.03).", INK, False),
    ]) + 18

    # criterion card with inset chart
    crit = json.load(open(CRITERION))["0"]["persona_self"]
    traj = crit["traj"]
    taste = [r["judgment_taste"]["p_bold_better"] for r in crit["battery"]]

    inset_w, inset_h = 360, 182

    def inset(ytop):
        ix, iy = X0 + CW - inset_w - 26, ytop + 48
        s = [box(ix, iy, inset_w, inset_h, "white", GRAY, 1.2, rx=6)]
        px0, px1 = ix + 44, ix + inset_w - 78
        py0, py1 = iy + 22, iy + inset_h - 42
        ylo, yhi = 0.40, 0.95

        def PX(r):
            return px0 + r / 3 * (px1 - px0)

        def PY(v):
            return py1 - (v - ylo) / (yhi - ylo) * (py1 - py0)

        for v in (0.5, 0.7, 0.9):
            s.append(f'<line x1="{px0}" y1="{PY(v)}" x2="{px1}" y2="{PY(v)}" stroke="#e3e3e3" stroke-width="1"/>')
            s.append(f'<text x="{px0 - 6}" y="{PY(v) + 4}" text-anchor="end" font-size="11" fill="{GRAY}" '
                     f'font-family="{FONT}">{v:.1f}</text>')
        for series, color, label in ((traj, BLUE, "behavior"), (taste, RED, "criterion")):
            pts = " ".join(f"{PX(i):.1f},{PY(v):.1f}" for i, v in enumerate(series))
            s.append(f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="3"/>')
            for i, v in enumerate(series):
                s.append(f'<circle cx="{PX(i):.1f}" cy="{PY(v):.1f}" r="3.4" fill="{color}"/>')
            s.append(f'<text x="{px1 + 8}" y="{PY(series[-1]) + 4}" font-size="12" font-weight="bold" '
                     f'fill="{color}" font-family="{FONT}">{label}</text>')
        for i in range(4):
            s.append(f'<text x="{PX(i)}" y="{py1 + 16}" text-anchor="middle" font-size="11" fill="{GRAY}" '
                     f'font-family="{FONT}">{i}</text>')
        s.append(f'<text x="{(px0 + px1) / 2}" y="{py1 + 30}" text-anchor="middle" font-size="11" '
                 f'fill="{GRAY}" font-family="{FONT}">round (pilot seed 0, self-judge)</text>')
        return "\n".join(s)

    ttxt = " → ".join(f"{v:.3f}" for v in taste)
    btxt = " → ".join(f"{v:.2f}" for v in traj)
    y = card(y, "The criterion channel needs a different carrier", [
        ("The direct selection-criterion probe (judgment_taste: “which of these two answers is better?” on fixed "
         "bold-vs-cautious pairs) is pinned at chance on the Qwen risk organism — ", INK, False),
        (f"{ttxt}", RED, True),
        (f" over four rounds, while behavior wobbles {btxt} (inset). A real null, not a bug: the same probe "
         "discriminates on the EM organisms (0.50 → 0.58 with dose) and OLMo’s cautious-vs-bold taste has "
         "headroom. So criterion-vs-behavior questions ride Phase 1B’s judge-taste readout, not the Qwen risk "
         "loop — and the cross-lag null already retired “criterion leads behavior” on the legacy ensembles.", INK, False),
    ], extra_h=40, extra=inset) + 18

    t, yend = rich_text(X0 + 20, y + 32, [
        ("The one hard requirement, already in every new script: ", INK, True),
        ("persist the per-question, per-order raw probe reads each round. The binomial noise correction and the "
         "de-biased drift refit are unanswerable without them — which is exactly why the 23 legacy trajectories "
         "cannot be re-scored and new runs are the only path.", INK, False),
    ], 17, 148)
    hh = (yend - y) + 6
    b.append(box(X0, y, CW, hh, KEY_FILL, INK, 2.5))
    b.append(t)
    return svg_doc(W, y + hh + 40, "\n".join(b))


# ====================================================================

FIGS = [
    ("plan_program_map", fig_program_map),
    ("plan_instrument_repair", fig_instrument_repair),
    ("plan_qwen_anchor", fig_qwen_anchor),
    ("plan_olmo_inversion", fig_olmo_inversion),
    ("plan_riding_analyses", fig_riding_analyses),
]

if __name__ == "__main__":
    for name, fn in FIGS:
        path = os.path.join(HERE, f"{name}.svg")
        with open(path, "w") as f:
            f.write(fn())
        print("wrote", path)
