#!/usr/bin/env python3
"""Draft figure: the transmission coefficient of the self-training loop,
estimated three ways, and what separates the odd one out.

The transmission coefficient is the coefficient on the selection gap in

    (measured value after the round - measured value before)
        ~ (candidate-pool mean - measured value before) + selection gap

where the selection gap is the mean value of the answers the judge kept minus
the mean value of the pool it chose from, and the measured value is the share
of held-out probe answers that fall on the value axis being tracked. 1.0 means
the trained model's value moves by the whole selection differential.

Three lanes, on one shared horizontal scale:

  1. unified corpus, ordinary regression, near-uncensored   -> 0.809
  2. spread-intervention corpus, randomised round-1
     instrument (Wald ratio)                                -> 0.754
  3. spread-intervention corpus, ordinary regression,
     heavily censored by an abort rule                      -> 0.450

Everything except the instrumental-variables lane is recomputed here from the
result JSONs at draw time. The instrumental-variables numbers are not in any
result file; they are quoted from docs/ANALYSIS_LEDGER.md and this script
asserts that the ledger still carries them verbatim.

Regenerate with:  python3 transmission-triangulation.py   (stdlib only)
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..", "..", "..", "..")


def P(*parts):
    return os.path.join(ROOT, *parts)


UNIFIED_JSON = P("experiments", "response_saturation.json")
SPREAD_JSON = P("experiments", "spread_corpus_saturation.json")
SPREAD_RAW_DIR = P("experiments", "spread_intervention")
LEDGER = P("docs", "ANALYSIS_LEDGER.md")

# ---- palette (copied from docs/figures/src/make_figures.py) ----------------
INK = "#1a1a1a"
BLUE = "#2867b5"       # accent / self-judge series (validated)
GREEN = "#3a7d44"      # accent / frozen-judge series (validated)
RED = "#b5342c"        # emphasis for reversal / warning text
GRAY = "#6b7684"       # recessive only (axes, muted captions) - never a series
USER_FILL = "#cfe0f1"  # chat user box
ASST_FILL = "#eaf1f8"  # chat assistant box
DOC_FILL = "#fdf6e8"   # document / essay box
KEY_FILL = "#eef5ee"   # highlighted takeaway box

FONT = "Helvetica, Arial, sans-serif"

# Only two hues carry series identity here (blue = free of outcome-dependent
# censoring, red = censored); corpus and identification are carried by the
# in-figure condition lines and by mark shape, never by colour alone.


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


def tw(text, size, bold=False):
    """Approximate rendered width of a Helvetica string, in px."""
    return len(text) * size * (0.56 if bold else 0.52)


def tline(x, y, segments, size, anchor="start", color=INK, weight="normal"):
    """One <text> line built from (text, colour, bold) segments."""
    spans = []
    for text, col, bold in segments:
        spans.append(
            f'<tspan fill="{col}" font-weight="{"bold" if bold else weight}">'
            f'{esc(text)}</tspan>')
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{FONT}" '
            f'font-size="{size}" text-anchor="{anchor}" fill="{color}" '
            f'xml:space="preserve">{"".join(spans)}</text>')


def plain(x, y, text, size, color=INK, anchor="start", bold=False):
    return tline(x, y, [(text, color, bold)], size, anchor)


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


# ===========================================================================
# Data
# ===========================================================================
def load_unified():
    d = json.load(open(UNIFIED_JSON))
    mec = d["measurement_error_correction"]["all"]
    m0 = d["panels"]["all"]["M0_linear"]
    surv = d["survivorship"]
    return {
        "n_rounds": d["corpus"]["n_records_in_file"],
        "n_runs": d["corpus"]["n_runs_in_file"],
        "corrected": mec["corrected"]["gap"],
        "naive": mec["naive"]["gap"],
        "naive_ci": (m0["ci"]["gap"]["ci_lo"], m0["ci"]["gap"]["ci_hi"]),
        "n_short": surv["n_runs_stopping_short"],
        "n_complete": surv["n_runs_reaching_standard_horizon"],
        "slope_short": surv["round1_slope_short_runs"],
        "slope_complete": surv["round1_slope_completers"],
        "n_r1_short": surv["n_round1_short"],
        "n_r1_complete": surv["n_round1_completers"],
        "boot_draws": d["settings"]["bootstrap_draws"],
    }


def load_spread():
    d = json.load(open(SPREAD_JSON))
    p = d["pooled"]
    mec = p["measurement_error_correction"]
    return {
        "n_rounds": d["n_rows"],
        "n_runs": d["n_runs"],
        "corrected": mec["corrected"]["gap"],
        "naive": p["slope_with_supply"],
        "naive_ci": (p["slope_with_supply_ci"]["ci_lo"],
                     p["slope_with_supply_ci"]["ci_hi"]),
        "boot_draws": p["slope_with_supply_ci"]["draws"],
    }


def load_censoring():
    """Split the spread-intervention corpus by whether the run was aborted.

    Rows are built with exactly the rule scripts/analysis_spread_corpus_saturation.py
    uses (each (file, group, arm) is one run; a round contributes a row when the
    value trajectory has a reading on both sides of it), so the split covers the
    same 414 rounds the 0.450 estimate is fitted on.
    """
    import glob
    runs = {}          # (file name, group, arm) -> {"aborted":bool, "steps":[float]}
    reasons = {}
    for path in sorted(glob.glob(os.path.join(SPREAD_RAW_DIR, "output*", "*.json"))):
        blob = json.load(open(path))
        for gname, group in blob.get("groups", {}).items():
            reason = group.get("aborted")
            aborted = bool(reason)
            if aborted:
                reasons[reason] = reasons.get(reason, 0) + 1
            for aname, arm in group.get("arms", {}).items():
                traj = arm.get("value_traj") or []
                # Run identity is keyed on the file NAME, group and arm, exactly
                # as scripts/analysis_spread_corpus_saturation.py keys it, so the
                # run and round counts here match the published 126 / 414.
                key = (os.path.basename(path), gname, aname)
                for rec in (arm.get("rounds") or []):
                    idx = int(rec["round"]) - 1
                    if idx + 1 >= len(traj):
                        continue
                    slot = runs.setdefault(key, {"aborted": aborted, "steps": []})
                    slot["aborted"] = slot["aborted"] or aborted
                    slot["steps"].append(float(traj[idx + 1]) - float(traj[idx]))
    out = {}
    for key, want in (("aborted", True), ("completed", False)):
        sel = [r for r in runs.values() if r["aborted"] == want]
        per_run = [sum(r["steps"]) / len(r["steps"]) for r in sel]
        out[key] = {
            "n_runs": len(sel),
            "n_rounds": sum(len(r["steps"]) for r in sel),
            "mean_of_run_means": sum(per_run) / len(per_run),
        }
    modal_reason = max(reasons.items(), key=lambda kv: kv[1])
    out["n_runs_total"] = len(runs)
    out["n_rounds_total"] = sum(len(r["steps"]) for r in runs.values())
    out["reason"] = modal_reason[0]
    out["reason_groups"] = modal_reason[1]
    out["n_abort_groups"] = sum(reasons.values())
    return out


# The instrumental-variables estimate has no result JSON. It is recorded in
# docs/ANALYSIS_LEDGER.md, section B, in the row beginning "THE TRANSMISSION
# COEFFICIENT IS CAUSALLY". Fail loudly if the ledger no longer says this.
IV = {"point": 0.754, "ci": (0.621, 0.984), "se": 0.094,
      "n_pairs": 36, "first_stage": 0.1875, "first_stage_f": 35.1}


def check_ledger():
    text = open(LEDGER).read()
    for needle in ("b_IV = 0.754", "[0.621, 0.984]", "36 distinct round-1 matched pairs",
                   "F = 35.1"):
        if needle not in text:
            raise SystemExit(
                f"ANALYSIS_LEDGER.md no longer contains {needle!r} - the "
                "instrumental-variables lane of this figure is stale; re-read "
                "the ledger row before regenerating.")


# ===========================================================================
# Layout
# ===========================================================================
W, H = 1400, 1424
AX0, AX1 = 680.0, 1350.0
LEFT_EDGE = 668.0        # right edge of the in-figure condition-line column
VMIN, VMAX = 0.30, 1.05


def X(v):
    return AX0 + (v - VMIN) * (AX1 - AX0) / (VMAX - VMIN)


def interval(y, lo, hi, color, sw=5, cap=11):
    s = [f'<line x1="{X(lo):.1f}" y1="{y}" x2="{X(hi):.1f}" y2="{y}" '
         f'stroke="{color}" stroke-width="{sw}" stroke-linecap="butt"/>']
    for v in (lo, hi):
        s.append(f'<line x1="{X(v):.1f}" y1="{y - cap/2}" x2="{X(v):.1f}" '
                 f'y2="{y + cap/2}" stroke="{color}" stroke-width="{sw}"/>')
    return "\n".join(s)


def dot(cx, cy, color, r=13):
    return (f'<circle cx="{cx:.1f}" cy="{cy}" r="{r}" fill="{color}" '
            f'stroke="white" stroke-width="3"/>')


def diamond(cx, cy, color, r=15):
    pts = f"{cx:.1f},{cy-r} {cx+r:.1f},{cy} {cx:.1f},{cy+r} {cx-r:.1f},{cy}"
    return (f'<polygon points="{pts}" fill="{color}" stroke="white" '
            f'stroke-width="3"/>')


def hollow(cx, cy, color, r=9):
    return (f'<circle cx="{cx:.1f}" cy="{cy}" r="{r}" fill="white" '
            f'stroke="{color}" stroke-width="3"/>')


def clamped_center(lo_px, hi_px, width):
    """Centre a label on a span, nudged so it clears the text column and edge."""
    c = (lo_px + hi_px) / 2.0
    c = max(c, LEFT_EDGE + width / 2.0)
    c = min(c, AX1 - width / 2.0)
    return c


def build():
    check_ledger()
    uni = load_unified()
    spr = load_spread()
    cen = load_censoring()

    b = []

    # ---------------- headline ----------------
    b.append(tline(40, 56, [
        ("Two estimates free of censoring agree at ", INK, True),
        ("0.75", BLUE, True), (" and ", INK, True), ("0.81", BLUE, True),
        (".", INK, True)], 32))
    b.append(tline(40, 98, [
        ("The one fitted where the fast-moving runs were stopped early reads ", INK, True),
        (f"{spr['corrected']:.2f}", RED, True), (".", INK, True)], 32))

    sub = ("Transmission coefficient = how much of one round's selection differential shows up in the trained model's measured value. "
           "It is the coefficient on the selection gap when the round's change in measured value is regressed on the pool offset and "
           "that gap. Selection gap = mean value of the answers the judge kept minus the mean value of the pool it chose from; "
           "measured value = share of held-out probe answers on the tracked value axis. Dashed line at 1.0 = the whole differential.")
    y = 140
    for ln in wrap(sub, 134):
        b.append(plain(40, y, ln, 18, GRAY))
        y += 25

    # ---------------- axis ----------------
    axis_y = 264
    b.append(f'<line x1="{AX0}" y1="{axis_y}" x2="{AX1}" y2="{axis_y}" '
             f'stroke="{GRAY}" stroke-width="2.5"/>')
    t = 0.4
    while t < 1.001:
        px = X(t)
        b.append(f'<line x1="{px:.1f}" y1="{axis_y-8}" x2="{px:.1f}" '
                 f'y2="{axis_y}" stroke="{GRAY}" stroke-width="2.5"/>')
        b.append(plain(px, axis_y - 16, f"{t:.1f}", 18, GRAY, anchor="middle"))
        t += 0.1
    # axis-break glyph at the truncated left end
    for dx in (0, 9):
        b.append(f'<line x1="{AX0+6+dx}" y1="{axis_y+8}" x2="{AX0+14+dx}" '
                 f'y2="{axis_y-8}" stroke="white" stroke-width="5"/>')
        b.append(f'<line x1="{AX0+6+dx}" y1="{axis_y+8}" x2="{AX0+14+dx}" '
                 f'y2="{axis_y-8}" stroke="{GRAY}" stroke-width="2"/>')
    b.append(plain(AX0, axis_y + 26, "scale starts at 0.30, not 0", 18, GRAY))

    LANE_TOP, LANE_BOT = 336, 748
    b.append(f'<line x1="{X(1.0):.1f}" y1="{LANE_TOP}" x2="{X(1.0):.1f}" '
             f'y2="{LANE_BOT}" stroke="{GRAY}" stroke-width="2" '
             f'stroke-dasharray="4 7" opacity="0.75"/>')

    # ---------------- agreement band ----------------
    lo_band, hi_band = min(IV["point"], uni["corrected"]), max(IV["point"], uni["corrected"])
    b.append(f'<rect x="{X(lo_band):.1f}" y="{LANE_TOP}" '
             f'width="{X(hi_band)-X(lo_band):.1f}" height="{LANE_BOT-LANE_TOP}" '
             f'fill="{ASST_FILL}"/>')
    bc = (X(lo_band) + X(hi_band)) / 2.0
    b.append(plain(bc, 302, "the two estimates with no censoring", 19, BLUE,
                   anchor="middle", bold=True))
    b.append(plain(bc, 326,
                   f"land {hi_band - lo_band:.3f} apart", 19, BLUE,
                   anchor="middle", bold=True))

    # ---------------- lanes ----------------
    def lane(main_y, lines, note_color):
        ty = main_y - 22
        b.append(plain(40, ty, lines[0], 20, INK, bold=True))
        b.append(plain(40, ty + 26, lines[1], 18, GRAY))
        b.append(plain(40, ty + 52, lines[2], 18, INK))
        b.append(tline(40, ty + 78, [(lines[3], note_color, True)], 18))

    # lane 1 - unified corpus, observational
    m1 = 380
    lane(m1, [
        "Unified corpus",
        f"{uni['n_rounds']} rounds from {uni['n_runs']} runs",
        "ordinary regression, pool offset controlled",
        f"{uni['n_short']} of {uni['n_runs']} runs stop short — almost no censoring",
    ], BLUE)
    b.append(interval(m1 + 46, uni["naive_ci"][0], uni["naive_ci"][1], GRAY, sw=4))
    b.append(hollow(X(uni["naive"]), m1 + 46, GRAY))
    lab = (f"uncorrected {uni['naive']:.3f}, interval "
           f"[{uni['naive_ci'][0]:.3f}, {uni['naive_ci'][1]:.3f}]")
    b.append(plain(clamped_center(X(uni["naive_ci"][0]), X(uni["naive_ci"][1]), tw(lab, 18)),
                   m1 + 30, lab, 18, GRAY, anchor="middle"))
    b.append(dot(X(uni["corrected"]), m1, BLUE))
    b.append(plain(X(uni["corrected"]), m1 - 26, f"{uni['corrected']:.3f}", 27, BLUE,
                   anchor="middle", bold=True))
    b.append(plain(X(uni["corrected"]) - 24, m1 + 7, "no interval computed", 18, GRAY,
                   anchor="end"))

    # lane 2 - randomised instrument
    m2 = 530
    lane(m2, [
        "Spread-intervention corpus",
        f"{IV['n_pairs']} matched round-1 pairs",
        "randomised instrument: round-1 arm assignment",
        "no censoring — round 1 precedes every abort",
    ], BLUE)
    b.append(interval(m2, IV["ci"][0], IV["ci"][1], BLUE, sw=5))
    b.append(diamond(X(IV["point"]), m2, BLUE))
    b.append(plain(X(IV["point"]), m2 - 26, f"{IV['point']:.3f}", 27, BLUE,
                   anchor="middle", bold=True))
    cilab = f"95% CI [{IV['ci'][0]:.3f}, {IV['ci'][1]:.3f}]"
    b.append(plain(clamped_center(X(IV["ci"][0]), X(IV["ci"][1]), tw(cilab, 18)),
                   m2 + 34, cilab, 18, GRAY, anchor="middle"))
    prov = "from the analysis ledger, not from a result file"
    b.append(plain(clamped_center(X(IV["ci"][0]), X(IV["ci"][1]), tw(prov, 18)),
                   m2 + 58, prov, 18, GRAY, anchor="middle"))

    # lane 3 - spread corpus, observational
    m3 = 680
    lane(m3, [
        "Spread-intervention corpus",
        f"{spr['n_rounds']} rounds from {spr['n_runs']} runs",
        "ordinary regression, pool offset controlled",
        f"{cen['aborted']['n_runs']} of {spr['n_runs']} runs abort early — heavy censoring",
    ], RED)
    b.append(interval(m3 + 46, spr["naive_ci"][0], spr["naive_ci"][1], GRAY, sw=4))
    b.append(hollow(X(spr["naive"]), m3 + 46, GRAY))
    lab = (f"uncorrected {spr['naive']:.3f}, interval "
           f"[{spr['naive_ci'][0]:.3f}, {spr['naive_ci'][1]:.3f}]")
    b.append(plain(clamped_center(X(spr["naive_ci"][0]), X(spr["naive_ci"][1]), tw(lab, 18)),
                   m3 + 30, lab, 18, GRAY, anchor="middle"))
    b.append(dot(X(spr["corrected"]), m3, RED))
    b.append(plain(X(spr["corrected"]), m3 - 26, f"{spr['corrected']:.3f}", 27, RED,
                   anchor="middle", bold=True))
    b.append(plain(X(spr["corrected"]) + 24, m3 + 7, "no interval computed", 18, GRAY))

    # ---------------- the shortfall ----------------
    ay = 786
    b.append(f'<line x1="{X(spr["corrected"]):.1f}" y1="{ay}" '
             f'x2="{X(IV["point"]):.1f}" y2="{ay}" stroke="{RED}" '
             f'stroke-width="4" marker-start="url(#arrR)" marker-end="url(#arrR)"/>')
    diff = IV["point"] - spr["corrected"]
    pct = 100.0 * diff / IV["point"]
    pct_uni = 100.0 * (uni["corrected"] - spr["corrected"]) / uni["corrected"]
    b.append(plain((X(spr["corrected"]) + X(IV["point"])) / 2.0, ay + 30,
                   f"{diff:.3f} lower — {pct:.0f}% of the instrument's estimate missing",
                   20, RED, anchor="middle", bold=True))
    b.append(plain((X(spr["corrected"]) + X(IV["point"])) / 2.0, ay + 54,
                   f"({pct_uni:.0f}% below the top lane)", 18, GRAY, anchor="middle"))

    # what the hollow markers mean, parked in the empty text column
    hollow_note = ("Hollow grey markers: the same fits before the measurement-error correction that removes "
                   "noise shared by the pool-offset term and the outcome. Only they carry bootstrap intervals.")
    y = 786
    for ln in wrap(hollow_note, 66):
        b.append(plain(40, y, ln, 18, GRAY))
        y += 25

    bridge = ("The top and bottom lanes use the same specification and the same estimator. What differs is the corpus — "
              "and with it, which runs were allowed to finish.")
    y = 876
    for ln in wrap(bridge, 134):
        b.append(plain(40, y, ln, 19, INK))
        y += 25

    # ---------------- censoring mechanism box ----------------
    BX, BY, BW, BH = 40, 926, 1320, 366
    b.append(box(BX, BY, BW, BH, KEY_FILL, INK, 2.5, rx=10))
    b.append(plain(BX + 24, BY + 38,
                   "Why the bottom lane reads low: the rule that ends a run takes the fastest movers out of the sample",
                   21, INK, bold=True))

    # left half - the verbatim stop reason
    lx = BX + 24
    b.append(plain(lx, BY + 74,
                   f"the stop reason recorded on those {cen['n_abort_groups']*2} runs, verbatim:",
                   18, GRAY))
    dbx, dby, dbw = lx, BY + 86, 680
    reason_lines = wrap(cen["reason"], 66)
    dbh = 20 + 26 * len(reason_lines)
    b.append(box(dbx, dby, dbw, dbh, DOC_FILL, GRAY, 2, rx=6))
    ry = dby + 32
    for ln in reason_lines:
        b.append(plain(dbx + 16, ry, ln, 18, INK))
        ry += 26
    b.append(plain(lx, dby + dbh + 24,
                   f"({cen['reason_groups']} of {cen['n_abort_groups']} paired runs; "
                   "the rest differ only in the round number)", 18, GRAY))
    note = ("Sensible as a pairing constraint — it stops a paired run once the two arms can no longer be offered "
            "candidate pools whose means match. The statistical consequence surfaced later.")
    ny = BY + 214
    for ln in wrap(note, 70):
        b.append(plain(lx, ny, ln, 18, INK))
        ny += 25

    # right half - movement per round, aborted vs completed
    rx0 = BX + 800
    ab, co = cen["aborted"], cen["completed"]
    scale = 3000.0
    b.append(plain(rx0, BY + 74,
                   f"runs the rule stopped — {ab['n_runs']} runs, {ab['n_rounds']} rounds",
                   18, INK))
    b.append(f'<rect x="{rx0}" y="{BY+84}" width="{ab["mean_of_run_means"]*scale:.1f}" '
             f'height="24" fill="{RED}"/>')
    b.append(plain(rx0 + ab["mean_of_run_means"] * scale + 12, BY + 104,
                   f"+{ab['mean_of_run_means']:.3f}", 21, RED, bold=True))
    b.append(plain(rx0, BY + 148,
                   f"runs that finished — {co['n_runs']} runs, {co['n_rounds']} rounds",
                   18, INK))
    b.append(f'<rect x="{rx0}" y="{BY+158}" width="{co["mean_of_run_means"]*scale:.1f}" '
             f'height="24" fill="{INK}"/>')
    b.append(plain(rx0 + co["mean_of_run_means"] * scale + 12, BY + 178,
                   f"+{co['mean_of_run_means']:.3f}", 21, INK, bold=True))
    ry = BY + 214
    for ln in wrap("bar length: each run's mean change in measured value per round, "
                   "averaged over runs, on the rounds the bottom lane is fitted on", 54):
        b.append(plain(rx0, ry, ln, 18, GRAY))
        ry += 25

    corr = (f"Same direction in the near-uncensored unified corpus: the {uni['n_short']} runs that stop short give a round-1 "
            f"response slope of {uni['slope_short']:.3f} across their {uni['n_r1_short']} round-1 records, against "
            f"{uni['slope_complete']:.3f} for the {uni['n_r1_complete']} records from runs that complete.")
    b.append(f'<line x1="{BX+24}" y1="{BY+284}" x2="{BX+BW-24}" y2="{BY+284}" '
             f'stroke="{GRAY}" stroke-width="1.5" opacity="0.55"/>')
    cy = BY + 316
    for ln in wrap(corr, 134):
        b.append(plain(BX + 24, cy, ln, 18, INK))
        cy += 25

    # ---------------- footer ----------------
    foot = ("Sources: experiments/response_saturation.json (unified corpus; measurement_error_correction.all and panels.all.M0_linear, "
            f"run-clustered bootstrap, {uni['boot_draws']} draws) · experiments/spread_corpus_saturation.json (spread-intervention corpus; pooled, "
            f"run-clustered bootstrap, {spr['boot_draws']} draws) · abort split recomputed here from experiments/spread_intervention/output*/*.json "
            f"· the instrumental-variables lane (Wald ratio, first stage +{IV['first_stage']:.4f}, F = {IV['first_stage_f']}, SE {IV['se']:.3f}) is "
            "quoted from docs/ANALYSIS_LEDGER.md section B; no result JSON holds it.")
    fy = BY + BH + 34
    for ln in wrap(foot, 138):
        b.append(plain(40, fy, ln, 18, GRAY))
        fy += 24

    return svg_doc(W, H, "\n".join(b)), uni, spr, cen


def main():
    svg, uni, spr, cen = build()
    out = os.path.join(HERE, "transmission-triangulation.svg")
    with open(out, "w") as fh:
        fh.write(svg)
    print(f"wrote {out}")
    print(f"  unified   corrected {uni['corrected']:.4f}  uncorrected {uni['naive']:.4f} "
          f"[{uni['naive_ci'][0]:.4f}, {uni['naive_ci'][1]:.4f}]  "
          f"{uni['n_rounds']} rounds / {uni['n_runs']} runs, {uni['n_short']} short")
    print(f"  instrument      {IV['point']:.4f} [{IV['ci'][0]:.3f}, {IV['ci'][1]:.3f}] "
          f"(ledger, {IV['n_pairs']} pairs)")
    print(f"  spread    corrected {spr['corrected']:.4f}  uncorrected {spr['naive']:.4f} "
          f"[{spr['naive_ci'][0]:.4f}, {spr['naive_ci'][1]:.4f}]  "
          f"{spr['n_rounds']} rounds / {spr['n_runs']} runs")
    print(f"  censoring aborted {cen['aborted']['mean_of_run_means']:+.4f} "
          f"({cen['aborted']['n_runs']} runs, {cen['aborted']['n_rounds']} rounds) vs "
          f"completed {cen['completed']['mean_of_run_means']:+.4f} "
          f"({cen['completed']['n_runs']} runs, {cen['completed']['n_rounds']} rounds); "
          f"corpus total {cen['n_runs_total']} runs / {cen['n_rounds_total']} rounds")


if __name__ == "__main__":
    main()
