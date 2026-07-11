#!/usr/bin/env python3
"""Figures for the CURRENTLY PLANNED experiments and analyses.

Source of truth: docs/PLAN.md (the single canonical plan; synced here to the
07-11 morning planning pass + the Saturday-midday statuses in docs/STATE.md:
K3 launched, v9 installer ladder running, K1 gated on persona re-centering)
plus the Phase-0 screen results
(experiments/phase0_screen/output/phase0_screen.json).

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
    centered(b, W / 2, 126, "docs/PLAN.md — the single canonical plan (planning sync 07-11 morning; statuses as of Saturday midday:"
             " K3 launched, v9 installer running, K1 on its persona gate); chips show what has already landed", 16, GRAY)

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
    y2 = card(y, "Phase 0 — instrument diagnostic screen (Colab, complete 2026-07-10)", "done", [
        ("The rebuilt coordinate (order-balanced probe, generated-choice + invalid-rate reads, EV-unequal factual gate) "
         "screened both substrates before any seeds are spent. ", INK, False),
        ("Base Qwen answers by position, not content:", RED, True),
        (" it picks the gamble at 0.94 when the gamble is option B but 0.31 when it is option A (order gap 0.63) — a "
         "single-order read would report a 0.94 risk-seeker. The old risk persona is order-robust (gap ~0) but saturated "
         "at 1.00, so it has nowhere to move. ", INK, False),
        ("OLMo-3-7B-Instruct passes:", GREEN, True),
        (" risk 0.72 with order gap 0.077 and headroom to move down. Every checkpoint sits near chance (0.50–0.54) on "
         "single-token expected-value arithmetic — but free-text EV estimation is perfect (ratio 1.00), so the "
         "single-token failure is a format artifact, and the factual gate is downgraded to an informative "
         "differential readout (accuracy must not drop after the value update), not a disqualifier.", INK, False),
    ])
    b.append(arrow(W / 2, y2 + 4, W / 2, y2 + 26))

    # ---- Build steps (in progress) ---------------------------------
    y = y2 + 32
    color, label = CHIP["running"]
    items = [
        ("done", "risk_harness.py — paired generated-valid and forced coordinates, strict terminal parser, "
                 "invalid rate, differential EV-unequal factual bank, and exact per-round prompt-order planning "
                 "(experiments/common/risk_harness.py, self-tested)"),
        ("done", "OLMo stage-flow screen — the repaired battery on the released checkpoints, inference-only. "
                 "Result: position bias collapses across the release flow (order gap 0.72 → 0.35 → 0.08; only the "
                 "final Instruct stage passes), gamble-favoring emerges at SFT and strengthens (generated gamble "
                 "fraction 0.46 → 0.58 → 0.67) while judge taste stays near-neutral (0.47 → 0.54 → 0.52) — so the "
                 "inversion starts from final Instruct, onto an almost blank judging prior"),
        ("done", "mod65 organism + 3-seed pilot — stored finals 0.111 / 0.472 / 0.639 and flat generic judge taste, "
                 "but raw probe generations were not saved for strict reparsing and prompt order was randomized, "
                 "not exactly balanced. This motivates K1; it is not the clean anchor result — and the pilot's "
                 "letter-trained persona is retired (see the smoke chain); K1 runs a re-centered rationale persona."),
        ("done", "cross-organism judge screen (12/12 judges) — one fixed pool produced a carrier candidate: "
                 "behaviorally-reverted amp66:12 had candor gap +0.127 while amp55:9 was anchor-like. The result is "
                 "post-hoc and one-pool; fresh-pool semantic-loading replication gates any carrier loop."),
        ("done", "K1 smoke chain — three crashes root-caused to the audited Qwen revision pin itself: snapshot "
                 "1b4199c4 ships the OLD thinking-family chat template, injecting think-block tokens into every "
                 "assistant TRAINING render. All Qwen scripts re-pinned to cdbee75f with a guard assert; the "
                 "letter-format and fp16 attributions retracted as primary causes. Smoke v4 then PASSED end-to-end "
                 "(invalid 0.00, generated order gap 0.02, measure-only drift ~0) and measured K1 at ~12.5 h."),
        ("running", "OLMo conservative install — the arc became a result. Behavior-format ladders (v2–v6) are "
                 "TASTE-INERT: v6 passed its behavior gates but the strict inversion screen found judge separation "
                 "exactly 0.000 on both pools, with generic taste flat 0.49–0.53 across every rung. Judge-format "
                 "training rows fixed it — v7's registered prediction confirmed (cautious_judge_pref 0.426 → 0.927 "
                 "dose-response, generic taste still flat: a domain-specific install). With letter → forced and "
                 "rationale → generated this is a TRIPLE dissociation: you move the channel you train. v8 (1:2:1 "
                 "mix) landed ALL SEVEN gates (judge_pref +0.260, generated 0.478 in band, order gap 0.025) — but "
                 "the sha-bound screen still failed on separation (sign replicated both pools, gaps ~0.02): "
                 "template-pair judge training transfers weakly to the deployed pair format. v9 (reference-pair "
                 "judge rows) is running; the screen remains K2's arbiter."),
        ("todo", "remaining launch blockers — DONE: K1 strict_final_v2 + DRY-verified, GPU smoke + measured budget, "
                 "Qwen re-pin, K3 launched, storage preflight, Drive JSON sync with hashes. REMAINING: a v9 "
                 "all-gates rung + strict two-pool screen PASS (gates K2); K1 persona re-centering into the "
                 "0.35–0.75 generated band (calibration queued behind v9 on the Colab GPU); the carrier fresh-pool "
                 "validation"),
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
    y2 = card(y, "Phase 1A — Qwen clean anchor grid: 4 judge conditions × 4 seeds × 4 rounds, +1 measure-only  (Kaggle K1, ~12.5 h measured)", "planned", [
        ("Evolving self-judge vs frozen round-0 organism judge vs frozen base judge vs random-selection control, all "
         "cloned from one re-centered persona. The frozen-base arm is a NEW order-balanced baseline — honestly n=4 "
         "rollouts, and it does not re-score the legacy let-go verdict (different starting state). Preregistered "
         "endpoint: the paired baseline-adjusted final generated-valid risk (evolving-self versus frozen-base), with "
         "forced risk and trajectory AUC secondary. ", INK, False),
        ("Launch gate: an in-band persona.", BLUE, True),
        (" The smoke passed clean, but the rationale persona saturates the generated channel at 0.93 — the "
         "move-the-channel-you-train dissociation strikes Qwen too — so K1 runs a hard in-band gate (0.35–0.75) and "
         "launches only on the re-centered calibration. The old three-seed fan stays a motivating pilot (raw "
         "generations not persisted for strict reparsing); new scripts persist every round, which also makes later "
         "vintage and transmission cells reachable.", INK, False),
    ])
    b.append(arrow(W / 2, y2 + 4, W / 2, y2 + 26))

    # ---- Phase 1B --------------------------------------------------
    y = y2 + 32
    y2 = card(y, "Phase 1B — OLMo conservative-judge inversion, repowered  (Kaggle K2, ~20.5 h: 6 confirmatory + 3 control seeds)", "headline", [
        ("Every legacy OLMo rollout railed to risk ≈ 1.0 under both judges. So install the opposite preference: ", INK, False),
        ("freeze a moderate conservative OLMo organism as judge — does it reverse the direction of self-training, "
         "where the frozen base judge drove risk up?", RED, True),
        (" The audit repowered it: 6 seeds on the confirmatory frozen-conservative vs frozen-base contrast + 3 on "
         "the mechanistic controls (evolving self, random), funded by deferring K4 — GATED on an all-gates installer "
         "rung plus the sha-bound strict screen: the two frozen judges must rank ACTUAL gamble pools differently on "
         "two fresh pools. Status: the v8 organism passed all seven gates but its screen FAILED on separation "
         "(sign replicated, gaps ~0.02), so v9 — judge rows paired against the exact deployed reference sentence — "
         "is running. K2 launches the moment a v9 rung passes both; the six-seed contrast is the never-cut causal "
         "claim.", INK, False),
    ], fill=RED_TINT, border=RED, bw=2.4)
    b.append(arrow(W / 2, y2 + 4, W / 2, y2 + 26))

    # ---- the rest of the sprint (was "Phase 2 branches") ------------
    y = y2 + 32
    color, label = CHIP["running"]
    b.append(f'<text x="{X + 18}" y="{y + 30}" font-size="19" font-weight="bold" fill="{INK}" '
             f'font-family="{FONT}">The rest of the sprint — order K2 → K1 → K2 controls → K3 → K4; in practice K3 launched first (K1/K2 gate-blocked)</text>')
    b.append(f'<text x="{X + CW - 16}" y="{y + 29}" text-anchor="end" font-size="13.5" font-weight="bold" '
             f'fill="{color}" font-family="{FONT}">SCHEDULED</text>')
    branches = [
        ("K3 — EM neutral-judge grid: LAUNCHED 07-11 (~6.5 h)",
         "running on Kaggle now — insecure-code organism × 4 judge conditions (random arm firm) × 3 seeds × 4 "
         "rounds, neutral prompt. Existence framing; em_freegen as binomial counts; + self_report."),
        ("K4 — one-update content impulse: DEFERRED",
         "runs only if K1–K3 finish early. Preferred form: one fixed mod65 checkpoint × one matched small update "
         "per content arm, 6–8 data seeds, immediate deltas (~1–2 h) — a directional impulse, not a fixed point."),
        ("Transmission cells (Sat Colab, ~8 h, parallel to K2)",
         "transmission + its frozen-base CONTROL · carrier (gated on fresh-pool validation) · susceptibility · "
         "composition (2 constructed states) — 3 seeds each."),
        ("Sunday — the audit-ordered analysis day",
         "gate table first · primary contrasts (K2 confirmatory first) · judge loading + kept-shift manipulation "
         "checks · format channels · update geometry vs r0 · verdicts · probe-specificity ratios with FDR · a "
         "labeled exploratory tier."),
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
        b.append(box(bx, yy, bw_, maxh, "white", INK, 1.4, rx=8))
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
        ("EXPLICITLY OUT (user-confirmed cuts): ", GRAY, True),
        ("OLMo × insecure-code — the one empty quadrant, named as such in the write-up · any new model family "
         "(Qwen3.5) · DPO update-rule comparison · J-lens · regime grid · λ-bottleneck extension · Lightning "
         "top-ups · the dedicated lead-lag study (cross-lag null) · claims built on raw-factor LoRA norms/cosines. "
         "The Sunday risk-vintage mini runs only if K1’s vintages landed and hours remain — else explicitly next "
         "window.", GRAY, False),
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
        ("the base model’s coordinate was dominated by position preference (0.94 vs 0.31 on identical content) and "
         "the trained persona had no headroom. The single-token EV chance level turned out to be a format artifact "
         "(free-text EV estimation is perfect, ratio 1.00), so the factual gate is downgraded to an informative "
         "differential readout. Gates now precede seeds — and the repaired loop already works: mod65 trains "
         "order-robust (gap 0.06) where the legacy loop would have installed a letter habit.", INK, False),
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
    centered(b, W / 2, 126, "Kaggle K1, ~12.5 h measured, smoke v4 PASSED: 4 seeds × 4 rounds + a measure-only seed;"
             " launch waits only on the persona re-centering (in-band gate 0.35–0.75)", 16, GRAY)

    # organism box (left)
    ox, oy, ow, ohh = 60, 200, 330, 290
    b.append(box(ox, oy, ow, ohh, "white", INK, 2.4, rx=10))
    t, _ = text_block(ox + 18, oy + 32, "the organism — re-centering", 16.5, 34, weight="bold")
    b.append(t)
    t, _ = text_block(ox + 18, oy + 62,
                      "the letter-trained mod65 persona is RETIRED (letter targets wreck Final: compliance; "
                      "pre-fix personas trained through a broken chat template). Its rationale successor "
                      "saturates generated at 0.93 — a lower-rate calibration is running, and K1's gate "
                      "accepts only 0.35–0.75. The pilot fan (0.111/0.472/0.639) stays motivating "
                      "evidence only.",
                      14.5, 40)
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
        ("Preregistered primary endpoint: ", INK, True),
        ("paired baseline-adjusted final GENERATED-VALID risk, evolving-self vs frozen-base — forced risk and "
         "trajectory AUC secondary, the four-seed fan secondary, “basins” not a claim; the rollout seed is the "
         "unit (frozen-base baseline honestly n=4). Every arm runs strict Final: A/B parsing with reject/replenish, "
         "exact swapped-order twins for kept rows, and raw candidate + cross-score persistence for the judge-loading "
         "read. If neither judge contrast survives, the judge-mechanism claim on the risk axis is retired — that "
         "outcome is also a result.", INK, False),
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
    centered(b, W / 2, 126, "every legacy OLMo rollout railed to risk ≈ 1.0 under BOTH judges — install the opposite preference"
             " and ask whether the direction flips; the install itself became a result (the triple dissociation)", 16, GRAY)

    steps = [
        ("1 · stage screen  (done)", GREEN,
         "The repaired battery on OLMo 3’s released stages, inference-only, pinned revisions. Result: position "
         "bias collapses across the release flow (order gap 0.72 → 0.35 → 0.08) and only the final Instruct "
         "stage passes; gamble-favoring emerges at SFT and strengthens (generated gamble 0.46 → 0.58 → 0.67) "
         "while judge taste stays near-neutral throughout (0.47 → 0.54 → 0.52). Start from final Instruct — "
         "risk 0.72 with headroom down, and an almost blank judging prior to install the conservative "
         "preference onto."),
        ("2 · install the organism — judge rows, seven gates (v9 running)", INK,
         "Behavior-format ladders (v2–v6) are TASTE-INERT: v6 passed its behavior gates but the strict screen "
         "found judge separation 0.000, generic taste flat 0.49–0.53 across every rung. Judge-format training "
         "rows fixed it — v7's registered dose-response confirmed (cautious_judge_pref 0.426→0.927, generic taste "
         "flat: domain-specific). The TRIPLE dissociation: letter→forced, rationale→generated, judge-rows→judging "
         "— you move the channel you train. v8 (1:2:1) landed ALL SEVEN gates (judge_pref +0.260, generated 0.478 "
         "in band, order gap 0.025) but failed the screen on separation (sign replicated, gaps ~0.02); v9 pairs "
         "judge rows against the exact deployed reference sentence."),
        ("3 · clone into four arms — repowered 6+3, launches on gate-pass", INK,
         "The identical conservative adapter starts every arm. 6 seeds × 4 rounds on the confirmatory contrast "
         "(frozen conservative vs frozen base) + 3 seeds on the mechanistic controls (evolving self, random) — "
         "~20.5 h, funded by deferring K4, and first in the launch order the moment a v9 rung passes all gates "
         "plus the sha-bound strict screen. Controls thin to 2 seeds under pressure; the six-seed contrast never."),
        ("4 · read the contrast", INK,
         "Primary endpoint: the generated-valid coordinate under judge condition × round. Mechanism read: "
         "candidate-level judge loading on the actual pools (invalidity/length-controlled); kept-minus-pool gaps "
         "are manipulation checks. Secondary: judge taste, factual-EV delta, invalidity, merged updates vs r0."),
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
    centered(b, W / 2, 52, "The Sunday analysis day: pre-registered re-reads of the sprint data — no GPU", 33, bold=True)
    centered(b, W / 2, 92, "each one re-reads what the sprint scripts persist anyway: per-item, per-order raw probe reads,"
             " judge taste per round, per-round adapters with merged deltas", 16, GRAY)

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
    y = card(y, "Gates first, then contrasts — and drift-field language only where the design identifies it", [
        ("The audit reordered the day: the confounder gate table (held-out forced order gap, generated invalidity, EV gate, "
         "invalid rate, entropy, measure-only drift) certifies every cell before anything is read from it, and the "
         "rollout-seed-level condition contrasts — K2’s six-seed confirmatory contrast first — are the primary "
         "product. The drift-field refit on the order-balanced coordinate stays, demoted to the labeled exploratory "
         "tier: the old AR(1) zero crossings (self x* = 0.35, frozen x* = 0.12) sit on the position-confounded coordinate "
         "at R² ≈ 0.05–0.09, the composition cells are constructed-state comparisons (different adapters differ in "
         "more than x), and K4 — the arm that would have probed stiffness — is deferred.", INK, False),
    ]) + 18

    y = card(y, "Weight geometry, recomputed on merged updates", [
        ("The legacy thrash correlations (more total LoRA motion ↔ less behavioral change; update-direction "
         "persistence ↔ extreme fate) are ", INK, False),
        ("permanently withdrawn", RED, True),
        (" — they were computed on raw A/B factor norms, which are not invariant to equivalent LoRA factorizations, "
         "and the legacy runs persisted only the scalar summaries, so no invariant recompute of those rollouts is "
         "possible. Sunday's analysis runs fresh on the new K1–K3 logs: scripts log ΔW = scaling·B@A per round; net "
         "displacement, step norm, path length, and direction persistence are descriptive diagnostics; any behavior "
         "association must be estimated on independent rollouts and is not preregistered as a known sign.", INK, False),
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
    y = card(y, "Candidate-level judge loading replaces the assumed mediator — judgment_taste is demoted", [
        ("The generic advice-pair probe (judgment_taste) sits flat while behavior moves, in every pilot: the legacy "
         "organism (", INK, False),
        (f"{ttxt}", RED, True),
        (f" while behavior wobbles {btxt} — inset), the mod65 pilot (taste 0.373–0.402 in every round while three "
         "seeds fan 0.111–0.639), OLMo’s release stages, and now the installer ladders (taste flat 0.49–0.53 while "
         "generated behavior swept 0.62 → 0.04; only judge-format rows moved the judging coordinate, 0.426 → 0.927). "
         "So the audit swapped mediators: every K run logs the candidate-level semantic loading on the ACTUAL "
         "candidate pools, per judge/item/round, cross-scored by the fixed base and organism judges even in arms "
         "they don’t control. The realized kept-minus-pool gap records the induced training-data shift but is not "
         "assumed to be a validated mediator. judgment_taste stays only as an off-format secondary; the legacy "
         "cross-lag null already retired “criterion leads behavior” on the legacy ensembles.", INK, False),
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
# Figure 2 — the final sprint: the plan operationalized into an hour budget
# ====================================================================

def fig_final_sprint():
    W = 1400
    b = []
    centered(b, W / 2, 50, "The final sprint (Fri 07-10 → Sun 07-12): the whole plan", 32, bold=True)
    centered(b, W / 2, 90, "as one hour budget — 45 Kaggle + 30 Colab + a no-GPU analysis day", 32, bold=True)
    centered(b, W / 2, 122, "docs/PLAN.md (planning sync 07-11 morning; statuses Saturday midday) — the smoke measured K1 at "
             "~12.5 h (evolving round 10.7 min, frozen 9.5 min), shrinking the buffer to ~5.5 h", 15.5, GRAY)

    X0 = 40

    # ---- color legend (every card's border/tint colour is one of these) ----
    y = 148
    legend = [
        (GREEN, "#eef7f0", "done / banked"),
        (BLUE, "white", "running now"),
        (RED, RED_TINT, "headline causal result"),
        (INK, "white", "scheduled run"),
        (GRAY, GRAY_TINT, "conditional — first to cut"),
    ]
    lx = X0 + 4
    b.append(f'<text x="{lx}" y="{y + 13}" font-size="13" font-weight="bold" fill="{INK}" '
             f'font-family="{FONT}">Card colour =</text>')
    lx += 108
    for stroke, fill, lab in legend:
        b.append(f'<rect x="{lx}" y="{y}" width="18" height="16" rx="3" fill="{fill}" stroke="{stroke}" '
                 f'stroke-width="2"/>')
        b.append(f'<text x="{lx + 25}" y="{y + 13}" font-size="13" fill="{INK}" '
                 f'font-family="{FONT}">{esc(lab)}</text>')
        lx += 25 + len(lab) * 7.1 + 30
    b.append(f'<text x="{W - X0 - 4}" y="{y + 13}" text-anchor="end" font-size="12.5" fill="{GRAY}" '
             f'font-family="{FONT}">columns = platform · row tags (DONE/FRI/SAT/K1…) = when</text>')

    # ---- banked strip -----------------------------------------------
    y = 178
    bt, byend = rich_text(X0 + 18, y + 26, [
        ("Already banked — don’t respend:  ", GREEN, True),
        ("Phase-0 harness diagnostics (both families) · OLMo stage-flow (legacy forced order gap 0.72 → 0.35 → 0.08) · mod65 organism "
         "and its 3-seed pilot (recorded trajectories 0.111 / 0.472 / 0.639, but generated outputs were not saved for strict reparsing) · one-pool judge-transmission carrier candidate · α-scaling intervention "
         "· hysteresis on both axes · entropy / λ-mixing basics.", INK, False),
    ], 14.5, 176)
    bh = (byend - y) + 8
    b.append(box(X0, y, W - 2 * X0, bh, "#eef7f0", GREEN, 1.8, rx=8))
    b.append(bt)
    y2 = y + bh

    # ---- launch order strip -----------------------------------------
    y = y2 + 12
    lt, lyend = rich_text(X0 + 18, y + 24, [
        ("Saturday launch order (K2’s confirmatory contrast is the sprint’s highest-value result):  ", RED, True),
        ("1 · K2 confirmatory 6-seed contrast, the moment its gates pass   2 · K1 anchor grid   3 · K2 "
         "evolving/random controls   4 · K3   5 · K4 one-update impulse if hours remain — K2-confirmatory hours are "
         "never spent on lower rows. STATUS Sat midday: quota reset; K3 LAUNCHED (its slot was free — K1 waits on "
         "the persona re-centering, K2 on the v9 rung + strict screen); K2 still preempts everything on gate-pass.", INK, False),
    ], 14, 182)
    lh = (lyend - y) + 8
    b.append(box(X0, y, W - 2 * X0, lh, RED_TINT, RED, 1.8, rx=8))
    b.append(lt)
    y2 = y + lh

    # ---- three lanes -------------------------------------------------
    lane_w, lane_gap = 434, 21
    lane_x = [X0 + i * (lane_w + lane_gap) for i in range(3)]
    top = y2 + 24

    def lane_header(x, title, budget, color):
        b.append(f'<text x="{x + lane_w / 2}" y="{top}" text-anchor="middle" font-size="21" '
                 f'font-weight="bold" fill="{color}" font-family="{FONT}">{esc(title)}</text>')
        b.append(f'<text x="{x + lane_w / 2}" y="{top + 21}" text-anchor="middle" font-size="14" '
                 f'fill="{GRAY}" font-family="{FONT}">{esc(budget)}</text>')

    def card(x, y, tag, title, desc, hours, accent=INK, fill="white", bw=1.6):
        lines = wrap(desc, 56)
        h = 52 + len(lines) * 18 + 12
        b.append(box(x, y, lane_w, h, fill, accent, bw, rx=9))
        if tag:
            b.append(f'<text x="{x + 15}" y="{y + 25}" font-size="13" font-weight="bold" fill="{accent}" '
                     f'font-family="{FONT}">{esc(tag)}</text>')
        tx = x + 15 + (len(tag) * 8.5 + 10 if tag else 0)
        b.append(f'<text x="{tx}" y="{y + 25}" font-size="15.5" font-weight="bold" fill="{INK}" '
                 f'font-family="{FONT}">{esc(title)}</text>')
        b.append(f'<text x="{x + lane_w - 14}" y="{y + 25}" text-anchor="end" font-size="13.5" '
                 f'font-weight="bold" fill="{GRAY}" font-family="{FONT}">{esc(hours)}</text>')
        for j, ln in enumerate(lines):
            b.append(f'<text x="{x + 15}" y="{y + 48 + j * 18}" font-size="13" fill="{INK}" '
                     f'font-family="{FONT}">{esc(ln)}</text>')
        return y + h + 12

    lane_header(lane_x[0], "Colab", "~30 units · calibration + EM cells", INK)
    lane_header(lane_x[1], "Kaggle — Saturday", "45 h · the training grid", INK)
    lane_header(lane_x[2], "Sunday", "no GPU · where “cohesive” happens", INK)

    cy = top + 40
    # Colab lane
    yc = cy
    yc = card(lane_x[0], yc, "DONE", "screen + α-scaling + mod65 pilot", "one-pool judge-transmission carrier "
              "candidate (not a carrier verdict), the limited α-scaling diagnostic, and the 3-seed mod65 pilot.",
              "~4 h", GREEN, "#eef7f0")
    yc = card(lane_x[0], yc, "SAT", "OLMo install — v9 running", "the arc became a result: behavior-format ladders "
              "(v2–v6) are TASTE-INERT: v6 passed its behavior gates but the strict screen found judge separation "
              "0.000, taste flat 0.49–0.53 everywhere. Judge-format rows fixed it (v7: cautious_judge_pref "
              "0.426→0.927 dose-response, generic taste flat) — the TRIPLE dissociation: letter→forced, "
              "rationale→generated, judge-rows→judging. v8 (1:2:1) landed all SEVEN gates but its screen failed on "
              "separation (sign replicated, gaps ~0.02); v9 pairs judge rows against the exact deployed reference "
              "sentence. The screen stays K2’s arbiter.", "~7 h spent", BLUE, "white", 2.0)
    yc = card(lane_x[0], yc, "SAT", "remaining launch blockers", "DONE: K1 strict_final_v2 + DRY-verified, GPU "
              "smoke v4 passed (K1 measured ~12.5 h), the Qwen revision re-pin (the old pin's thinking template "
              "corrupted training renders — three smoke crashes root-caused), K3 launched, storage preflight, "
              "Drive JSON sync with hashes. REMAINING: v9 all-gates rung + strict screen PASS (gates K2); K1 "
              "persona re-centering into the 0.35–0.75 band (calibration queued behind v9); carrier fresh-pool "
              "validation.", "", INK)
    yc = card(lane_x[0], yc, "SAT", "EM transmission loop cells (parallel to K2)", "transmission (em_dose1000 × "
              "fresh) · transmission CONTROL (frozen base × the same fresh gen) · carrier (amp66:12 × fresh, gated "
              "on the fresh-pool validation) · susceptibility (standout × reverted) · composition (2 constructed "
              "starting states) — 3 seeds each.", "~8 h", RED, RED_TINT, 2.0)
    yc = card(lane_x[0], yc, "SUN", "overflow + optional risk-vintage mini", "re-runs of failed Saturday cells; the "
              "vintage mini only if K1’s per-round vintages landed — and it is deferred BEFORE any confirmatory K2 "
              "seed is cut.", "~4 h", GRAY, GRAY_TINT)

    # Kaggle lane
    yk = cy
    yk = card(lane_x[1], yk, "K1", "Phase 1A Qwen anchor grid — persona gate", "re-centered persona × {evolving "
              "self · frozen round-0 copy · frozen base · random-selection} × 4 seeds × 4 rounds, +1 measure-only "
              "seed. Primary: paired baseline-adjusted final GENERATED-VALID risk (evolving-self vs frozen-base); "
              "the four-seed fan is secondary; the frozen-base baseline is honestly n=4. Smoke v4 PASSED (invalid "
              "0.00) — but launch waits on the in-band persona gate (0.35–0.75; the rationale persona saturates "
              "generated at 0.93).", "~12.5 h", INK, "white", 2.0)
    yk = card(lane_x[1], yk, "K2", "Phase 1B OLMo inversion", "launches on gate-pass: 6 seeds on "
              "the confirmatory contrast (frozen-conservative vs frozen-base) + 3 on the mechanistic controls "
              "(evolving self, random) × 4 rounds, funded by deferring K4. GATED on a v9 all-gates rung + the "
              "sha-bound strict screen (two fresh pools, actual K2 bank). v8 landed all seven gates but failed the "
              "screen on separation — v9 running. First-cell budget checkpoint re-runs the arithmetic; the named "
              "cut is controls 3→2, never the confirmatory six.", "~20.5 h", RED, RED_TINT, 2.2)
    yk = card(lane_x[1], yk, "K3", "EM neutral-judge grid — LAUNCHED 07-11", "running on Kaggle (T4): insecure-code "
              "organism × 4 judge conditions (random arm firm) × 3 seeds × 4 rounds, neutral prompt (deconfounds "
              "the candid grid). Existence framing at n=3; em_freegen read as binomial counts; reads: em_freegen + "
              "self_report.", "~6.5 h", BLUE, "white", 2.0)
    yk = card(lane_x[1], yk, "K4", "Content impulse — deferred", "runs only if K1–K3 finish early. Preferred form: a "
              "ONE-UPDATE content impulse — one fixed K1-organism checkpoint × one matched small update from "
              "{aligned · opposing · format-neutral} rows, 6–8 resampled data seeds, immediate target + off-target "
              "deltas (~1–2 h; identifies the directional impulse, not a fixed point). Buffer ~5.5 h.",
              "0–5 h", GRAY, GRAY_TINT)

    # Sunday lane — numbered analyses
    ys = cy
    analyses = [
        ("Confounder gate table FIRST", "per cell: exact training-order balance, forced order gap, EV delta, generated invalidity, "
         "measure-only drift — certifies everything below it."),
        ("Primary condition contrasts", "at the rollout-seed level, K2’s confirmatory frozen-conservative vs "
         "frozen-base contrast first."),
        ("Judge loading + kept shift", "candidate-level semantic loading on ACTUAL pools, controlling invalidity and length; "
         "kept-minus-pool gaps are manipulation checks, not established mediators."),
        ("Format channels", "generated vs forced-choice behavior treated as distinct channels, not one number."),
        ("Weight geometry, invariant", "merged update displacement, steps, path, and full Frobenius cosines as descriptive "
         "diagnostics; leave-one-seed-out checks before any behavioral association."),
        ("Transmission verdicts", "transmission / carrier / susceptibility in existence-framing, never rates; "
         "K3 em_freegen as binomial counts with intervals — rounds are not independent."),
        ("Riding-battery specificity, not fishing", "standardize each probe by its measure-only/item variation, "
         "compare against the random arm, report the target-specificity ratio, BH/FDR within the family; decline "
         "rail-saturated probes."),
        ("Exploratory tier, labeled", "generic judgment_taste coupling, mediation/cross-lag decompositions, and "
         "drift-field/fixed-point language ONLY where the design identifies it."),
    ]
    yy = ys + 8
    parts = []
    for i, (title, desc) in enumerate(analyses, 1):
        parts.append(f'<text x="{lane_x[2] + 16}" y="{yy + 18}" font-size="15" font-weight="bold" fill="{INK}" '
                     f'font-family="{FONT}">{i}</text>')
        parts.append(f'<text x="{lane_x[2] + 36}" y="{yy + 18}" font-size="14.5" font-weight="bold" fill="{INK}" '
                     f'font-family="{FONT}">{esc(title)}</text>')
        for j, ln in enumerate(wrap(desc, 54)):
            parts.append(f'<text x="{lane_x[2] + 36}" y="{yy + 37 + j * 17}" font-size="12.5" fill="{INK}" '
                         f'font-family="{FONT}">{esc(ln)}</text>')
        yy += 37 + len(wrap(desc, 54)) * 17 + 8
    b.append(box(lane_x[2], ys, lane_w, (yy - ys) + 4, "white", INK, 1.6, rx=9))
    b.extend(parts)
    ys_end = ys + (yy - ys) + 4

    lane_bottom = max(yc, yk, ys_end)

    # ---- riding-along strip -----------------------------------------
    y = lane_bottom + 8
    rt, ryend = rich_text(X0 + 18, y + 24, [
        ("Riding along in every training cell (non-negotiable):  ", INK, True),
        ("the battery patch (wishful thinking, introspection, self-recognition, suggestibility, identity, "
         "judgment_taste as an off-format secondary) · steering artifacts · off-target axes · entropy · paired "
         "generated-valid and forced target channels · exact training-order twins · factual-EV delta + invalidity · "
         "raw attempts, probes, and judge scores · every-round adapters with merged-update geometry relative to r0. "
         "Candidate-level judge loading is the mechanism read; kept-minus-pool shift records what entered training.", INK, False),
    ], 13.5, 196)
    rh = (ryend - y) + 8
    b.append(box(X0, y, W - 2 * X0, rh, "white", GRAY, 1.2, rx=8))
    b.append(rt)
    y2 = y + rh

    # ---- TPU: cut from the sprint -----------------------------------
    y = y2 + 16
    tt, tyend = rich_text(X0 + 18, y + 26, [
        ("Kaggle TPU battery service: still OUT of the sprint — gate 1 PASSED (v5e, hardware-viable) but queue-limited.  ", GRAY, True),
        ("The generation gate eventually scheduled and passed, so the service is technically viable — but a queue "
         "that stalls 30+ minutes can’t hold the Saturday critical path, so the decision is unchanged: all "
         "batteries run BATTERY_MODE=inloop in the T4 time-box, and the service stays parked as opportunistic / "
         "post-sprint re-measurement of persisted checkpoints — never anything a Saturday cell depends on. "
         "Every-round adapter persistence keeps all checkpoints re-measurable whenever a backend materializes.", INK, False),
    ], 13.5, 196)
    th = (tyend - y) + 8
    b.append(box(X0, y, W - 2 * X0, th, GRAY_TINT, GRAY, 1.6, rx=8))
    b.append(tt)
    y2 = y + th

    # ---- cut order --------------------------------------------------
    y = y2 + 16
    ct, cyend = rich_text(X0 + 18, y + 24, [
        ("Cut order if hours compress (K4 is already deferred):  ", INK, True),
        ("1 · Sunday risk-vintage mini → next window   2 · composition 2→1 starting states   3 · K2 "
         "mechanistic-control arms (evolving/random) 3→2 seeds.   ", INK, False),
        ("Never cut:", INK, True),
        (" K1 · the K2 six-seed confirmatory contrast · K3’s random arm · per-round persistence + invariant logging "
         "· the Friday pilots and pre-Kaggle screens.", INK, False),
    ], 13.5, 196)
    ch2 = (cyend - y) + 8
    b.append(box(X0, y, W - 2 * X0, ch2, "white", INK, 2.2, rx=8))
    b.append(ct)
    return svg_doc(W, y + ch2 + 36, "\n".join(b))


# ====================================================================
# Figure 7 — the cross-organism judge-transmission family (filed 2026-07-10)
# ====================================================================

def fig_judge_transmission():
    W = 1400
    b = []
    centered(b, W / 2, 52, "The cross-organism cells: does a drifted taste transmit,", 33, bold=True)
    centered(b, W / 2, 94, "re-ignite a reverted organism, and survive reversion?", 33, bold=True)
    centered(b, W / 2, 126, "filed 2026-07-10 — the broad screen is DONE (a one-pool carrier CANDIDATE, seed-dependent;"
             " fresh-pool gate pending); the loop cells run Saturday, parallel to K2", 16, GRAY)

    X0 = 60

    # ---- what "cross-organism" means (the distinction the whole figure turns on) ----
    dy = 150
    dt, dyend = rich_text(X0 + 20, dy + 32, [
        ("“Cross-organism” = the judge is a different trained model than the generator", INK, True),
        (" — not the generator judging itself (self-judge) and not a frozen snapshot of the generator’s own run "
         "(the copy-judge vintages, rounds 0/2/4). Every loop so far shared a lineage; these cells break it. The "
         "two columns marked “other lineage” below are the cross-organism judges.", INK, False),
    ], 15.5, 150)
    dh = (dyend - dy) + 6
    b.append(box(X0, dy, W - 2 * X0, dh, KEY_FILL, INK, 2))
    b.append(dt)

    # ---- step 0: the free screen (horizontal flow) -------------------
    y = dy + dh + 34
    sh = 148
    boxes = [
        ("one fixed candidate pool", "answers sampled once from base Qwen on the shared prompt banks — every judge "
         "scores the identical pool", 300),
        ("every persisted judge scores it", "EM dose rungs 250–1000 · amp55:7 (strong collapse) · amp55:10/11 "
         "(free-gen 1.0, choice floored) · amp66 endpoints · low:8 null · risk persona — neutral judge prompt, "
         "no candid instruction", 420),
        ("judge loading + kept shift, per pool", "risk / insecure-code / self-report candor. Require semantic loading to replicate on fresh pools; the kept gap is a manipulation check, not an established predictor", 380),
    ]
    b.append(f'<text x="{X0}" y="{y + 8}" font-size="20" font-weight="bold" fill="{GREEN}" '
             f'font-family="{FONT}">Step 0 — the free screen  ·  DONE 2026-07-10, 12/12 judges</text>')
    bx = X0
    for i, (title, desc, bw_) in enumerate(boxes):
        b.append(box(bx, y + 22, bw_, sh, "white", INK, 1.8, rx=10))
        for j, ln in enumerate(wrap(title, int(bw_ / 8.2))):
            b.append(f'<text x="{bx + 14}" y="{y + 48 + j * 20}" font-size="15.5" font-weight="bold" '
                     f'fill="{INK}" font-family="{FONT}">{esc(ln)}</text>')
        for j, ln in enumerate(wrap(desc, int(bw_ / 6.4))):
            b.append(f'<text x="{bx + 14}" y="{y + 74 + j * 17}" font-size="13" fill="{INK}" '
                     f'font-family="{FONT}">{esc(ln)}</text>')
        if i < 2:
            b.append(arrow(bx + bw_ + 3, y + 22 + sh / 2, bx + bw_ + 37, y + 22 + sh / 2, sw=3.5))
        bx += bw_ + 40
    t, note_yend = rich_text(X0, y + 22 + sh + 26, [
        ("A one-pool carrier CANDIDATE (downgraded from “carrier exists” by the deep audit): ", INK, True),
        ("the behaviorally-reverted amp66:12 — self-report retraced 0.29 → 0.12 in the let-go run — re-ranked the "
         "single fixed pool like the deepest dose rung (candor gap +0.127 vs the base anchor’s +0.036, zero gambles "
         "kept), while the other reverted endpoint amp55:9 judged at anchor. The read is post-hoc and one-pool: the "
         "semantic loading must replicate on ≥2 seeded strict-valid fresh pools before any carrier loop runs. "
         "Standout transmission judge: em_dose1000 (candor +0.127, risk −0.104).", INK, False),
    ], 14.5, 178)
    b.append(t)

    # ---- the judge × generator matrix --------------------------------
    my = note_yend + 30
    b.append(f'<text x="{X0}" y="{my}" font-size="20" font-weight="bold" fill="{INK}" '
             f'font-family="{FONT}">Where the new cells sit — frozen judge (columns) × generator starting state (rows)</text>')
    cols = ["base model", "own past copy (r0 / r2 / r4)", "standout organism (other lineage)",
            "reverted organism (other lineage)", "evolving self"]
    rows = ["fresh (base or fresh organism)", "grown, mid-trajectory", "reverted endpoint"]
    # (label, status) — status: run / planned / new / open / none
    cells = [
        [("uniform decay, 8/8", "run"), ("Phase 1A anchor arm", "planned"), ("TRANSMISSION", "new"),
         ("CARRIER", "screened"), ("divergent fans, 15 seeds", "run")],
        [("risk let-go arc (pilot)", "run"), ("Branch A vintage judges", "planned"), ("RE-IGNITION", "new"),
         ("", "none"), ("the loops themselves", "run")],
        [("open control", "open"), ("", "none"), ("ERASED vs MASKED", "new"),
         ("", "none"), ("selfaware release runs", "run")],
    ]
    STY = {"run": ("white", GREEN, "run"), "planned": ("white", GRAY, "planned"),
           "new": (RED_TINT, RED, "loop pending"), "open": (GRAY_TINT, GRAY, "unclaimed"),
           "screened": ("#eef7f0", GREEN, "one-pool candidate · fresh-pool gate"),
           "none": ("#fafafa", "#dddddd", "")}
    lx, cw, ch = 300, 196, 78
    gy = my + 18
    for j, cname in enumerate(cols):
        cx = lx + j * (cw + 8)
        for k, ln in enumerate(wrap(cname, 24)):
            b.append(f'<text x="{cx + cw / 2}" y="{gy + 16 + k * 15}" text-anchor="middle" font-size="12.5" '
                     f'font-weight="bold" fill="{INK}" font-family="{FONT}">{esc(ln)}</text>')
    gy += 52
    for i, rname in enumerate(rows):
        ry = gy + i * (ch + 8)
        for k, ln in enumerate(wrap(rname, 26)):
            b.append(f'<text x="{lx - 14}" y="{ry + ch / 2 - 6 + k * 16}" text-anchor="end" font-size="13" '
                     f'font-weight="bold" fill="{INK}" font-family="{FONT}">{esc(ln)}</text>')
        for j, (label, status) in enumerate(cells[i]):
            cx = lx + j * (cw + 8)
            fill, border, chip = STY[status]
            bold_new = status in ("new", "screened")
            b.append(box(cx, ry, cw, ch, fill, border, 2.2 if bold_new else 1.4, rx=8))
            if label:
                for k, ln in enumerate(wrap(label, 22)):
                    b.append(f'<text x="{cx + cw / 2}" y="{ry + 26 + k * 17}" text-anchor="middle" '
                             f'font-size="13" font-weight="{"bold" if bold_new else "normal"}" '
                             f'fill="{border if bold_new else INK}" font-family="{FONT}">{esc(ln)}</text>')
            if chip:
                b.append(f'<text x="{cx + cw / 2}" y="{ry + ch - 10}" text-anchor="middle" font-size="10.5" '
                         f'font-weight="bold" fill="{border}" font-family="{FONT}">{chip}</text>')
    my2 = gy + 3 * (ch + 8) + 8

    # ---- the three preregistered predictions -------------------------
    py = my2 + 26
    b.append(f'<text x="{X0}" y="{py}" font-size="20" font-weight="bold" fill="{INK}" '
             f'font-family="{FONT}">The loop cells (3 seeds each, Saturday, parallel to K2 — the frozen-base control makes them independent)</text>')
    preds = [
        ("transmission + its control", "standout judge (em_dose1000, screen-qualified at candor +0.127), frozen, "
         "over a fresh base generator — with a REQUIRED control cell: the frozen base judge over the same fresh "
         "generator, same seeds. If the taste drift steers the trajectory where the base judge doesn’t, a weak "
         "judge preference amplifies into behavioral drift. Either answer is informative."),
        ("susceptibility / erased-vs-masked + composition", "the standout judge over a reverted generator — "
         "PREDICT: reverted re-amplifies faster than base if the trait was masked, not erased (shared dominant "
         "weight direction; α-scaling shows limited low-α self-report carry). The 2-state composition cells are "
         "read as CONSTRUCTED-STATE COMPARISONS — different adapters differ in more than x, so they are not "
         "bias-free 1-D field samples."),
        ("carrier  ·  one-pool candidate, loop gated", "the reverted amp66:12 judge — taste-drifted (+0.127) on "
         "the single screen pool yet behaviorally reverted — over a fresh generator. Gated on Friday’s fresh-pool "
         "validation (≥2 seeded strict-valid pools; the amp66:12-vs-base loading must reproduce in sign). amp55:9 "
         "stripped its taste, so the cell reads the seed-dependence."),
    ]
    pw = (W - 2 * X0 - 2 * 20) / 3
    maxh = 0
    rend = []
    for i, (name, desc) in enumerate(preds):
        lines = wrap(desc, 46)
        hh = 44 + len(lines) * 17 + 12
        maxh = max(maxh, hh)
        rend.append((X0 + i * (pw + 20), name, lines))
    for px, name, lines in rend:
        b.append(box(px, py + 14, pw, maxh, "white", INK, 1.6, rx=10))
        b.append(f'<text x="{px + 14}" y="{py + 40}" font-size="15.5" font-weight="bold" fill="{RED}" '
                 f'font-family="{FONT}">{esc(name)}</text>')
        for j, ln in enumerate(lines):
            b.append(f'<text x="{px + 14}" y="{py + 62 + j * 17}" font-size="12.5" fill="{INK}" '
                     f'font-family="{FONT}">{esc(ln)}</text>')
    y2 = py + 14 + maxh + 22

    t, yend = rich_text(X0 + 20, y2 + 32, [
        ("Gating and honesty rules: ", INK, True),
        ("the cells run Saturday in parallel with K2 — the older “wait for Phase 1B” wording is superseded, because "
         "the frozen-base control cell makes each contrast independently interpretable. Only screen-qualified "
         "judges get loops (em_dose1000; amp66:12 pending the fresh-pool validation). EM-axis primary readouts are "
         "free-gen insecurity and self-report — the forced-choice coordinate is floored. The standout organisms are "
         "post-hoc-selected extremes, so every cell is a mechanism test, never a rate. And the risk half of the "
         "matrix only becomes reachable because K1 persists per-round adapters — the legacy runs kept none.", INK, False),
    ], 16, 152)
    hh = (yend - y2) + 6
    b.append(box(X0, y2, W - 2 * X0, hh, KEY_FILL, INK, 2.5))
    b.append(t)
    return svg_doc(W, y2 + hh + 40, "\n".join(b))


# ====================================================================

FIGS = [
    ("plan_program_map", fig_program_map),
    ("plan_final_sprint", fig_final_sprint),
    ("plan_qwen_anchor", fig_qwen_anchor),
    ("plan_olmo_inversion", fig_olmo_inversion),
    ("plan_riding_analyses", fig_riding_analyses),
    ("plan_judge_transmission", fig_judge_transmission),
]

if __name__ == "__main__":
    for name, fn in FIGS:
        path = os.path.join(HERE, f"{name}.svg")
        with open(path, "w") as f:
            f.write(fn())
        print("wrote", path)
