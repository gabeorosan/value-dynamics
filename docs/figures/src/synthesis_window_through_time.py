#!/usr/bin/env python3
"""synthesis — the intervention window, followed round by round.

Four small multiples, same round axis, same grammar: a thick line for the
value's state and a pale ribbon for how much that round's candidate answers
vary. Mostly visual.

Numbers transcribed from (round-by-round trajectories, all dated 2026-07-13):
  panel 1: docs/report_crossfamily_oracle.md, cell s21
  panel 2: docs/report_crossfamily_oracle.md, cell s22
  panel 3: docs/report_mixed_generator_branch_m.md, cell oracle_mix s32
           (round-1 spread range and round-4 spread from the same report;
           the round-by-round spread curve in between is a smooth schematic
           between those anchors, since only the endpoints are reported)
  panel 4: docs/report_oracle_saturation.md (seed 707 stall) +
           docs/report_mixed_reopen_qwen.md (matched self-only twin flat at
           0.625; injected seeds 921/922 both 0.627 to 0.000 after one round,
           spread 0.31 at round 1 then ~0.09)

Regenerate with:  python3 synthesis_window_through_time.py   (stdlib only)
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
FIGDIR = os.path.dirname(HERE) if os.path.basename(HERE) == "src" else HERE

INK = "#1a1a1a"
BLUE = "#2867b5"
GRAY = "#6b7684"
AMBER = "#c07d18"
FONT = "Helvetica, Arial, sans-serif"
BODY = 19

STATE_FILL = "#cfe3f5"
STATE_STROKE = "#8fb8dd"
OWN_FILL = "#dee2e6"
OWN_STROKE = "#b7bcc2"


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


def ctext(x, y, text, size, color=INK, weight="normal"):
    return (f'<text x="{x}" y="{y}" text-anchor="middle" font-family="{FONT}" '
            f'font-size="{size}" font-weight="{weight}" fill="{color}">{esc(text)}</text>')


def ltext(x, y, text, size, color=INK, weight="normal", anchor="start"):
    return (f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-family="{FONT}" '
            f'font-size="{size}" font-weight="{weight}" fill="{color}">{esc(text)}</text>')


def text_block(x, y, text, size, width, color=INK, weight="normal", lh=1.4, anchor="middle"):
    lines = wrap(text, width)
    svg = []
    for i, ln in enumerate(lines):
        svg.append(f'<text x="{x}" y="{y + i * size * lh}" text-anchor="{anchor}" font-family="{FONT}" '
                   f'font-size="{size}" font-weight="{weight}" fill="{color}">{esc(ln)}</text>')
    return "\n".join(svg), y + len(lines) * size * lh


def box(x, y, w, h, fill, stroke=INK, sw=2.2, rx=12):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')


def marker(x, y, color, s=6.5):
    return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{s}" fill="{color}" stroke="white" stroke-width="1.5"/>'


def svg_doc(w, h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
            f'font-family="{FONT}">\n<rect width="{w}" height="{h}" fill="white"/>\n'
            f'{body}\n</svg>')


# ---------------------------------------------------------------- data
ROUNDS = [0, 1, 2, 3, 4]

P1_STATE = [0.917, 0.667, 0.458, 0.292, 0.094]
P1_SPREAD = [0.124, 0.303, 0.242, 0.073, 0.073]

P2_STATE = [1.000, 1.000, 1.000, 1.000, 1.000]
P2_SPREAD = [0.000, 0.000, 0.000, 0.000, 0.000]

P3_STATE = [1.000, 0.750, 0.458, 0.208, 0.484]
P3_SPREAD = [0.28, 0.32, 0.35, 0.39, 0.39]

P4_OWN_STATE = [0.627, 0.627, 0.627, 0.627, 0.627]
P4_OWN_SPREAD = [0.000, 0.000, 0.000, 0.000, 0.000]
P4_ADDED_STATE = [0.627, 0.000, 0.000, 0.000, 0.000]
P4_ADDED_SPREAD = [0.00, 0.31, 0.09, 0.09, 0.09]

STATE_MIN, STATE_MAX = 0.0, 1.03


# ---------------------------------------------------------------- panel
def draw_panel(px, py, pw, ph, title, caption, lines, marker_round=None, marker_label=None):
    """lines: list of dicts(state=[...5], spread=[...5], color, fill, stroke, end_label, start_label)"""
    out = []
    chart_x = px + 76
    chart_w = pw - 76 - 46
    marker_lane = py + 92
    chart_top = marker_lane + 26
    state_h = 160
    state_bottom = chart_top + state_h
    spread_h = 46
    spread_top = state_bottom + 14
    spread_bottom = spread_top + spread_h
    xaxis_y = spread_bottom + 26
    xaxis_title_y = xaxis_y + 24

    def xr(r):
        return chart_x + chart_w * (r / 4)

    def ys(v):
        return chart_top + state_h * (1 - (v - STATE_MIN) / (STATE_MAX - STATE_MIN))

    out.append(box(px, py, pw, ph, "white", "#d8dde3", 1.6, rx=14))
    out.append(ltext(px + pw / 2, py + 30, title, 21, INK, "bold", "middle"))
    t, _ = text_block(px + pw / 2, py + 52, caption, BODY, int(pw / 9.3), GRAY)
    out.append(t)

    # state gridlines + ticks
    for v in (0.0, 0.5, 1.0):
        yy = ys(v)
        out.append(f'<line x1="{chart_x}" y1="{yy:.1f}" x2="{chart_x+chart_w}" y2="{yy:.1f}" '
                   f'stroke="#e7e9ec" stroke-width="1"/>')
        out.append(ltext(chart_x - 12, yy + 5, f"{v:g}", 16, GRAY, anchor="end"))

    # spread strip frame
    spread_max = max(0.05, max(v for ln in lines for v in ln["spread"]))
    out.append(f'<line x1="{chart_x}" y1="{spread_bottom:.1f}" x2="{chart_x+chart_w}" y2="{spread_bottom:.1f}" '
               f'stroke="#d8dde3" stroke-width="1.4"/>')
    out.append(ltext(chart_x - 12, (spread_top + spread_bottom) / 2 + 5, "variation", 14, GRAY, anchor="end"))

    # x ticks
    for r in ROUNDS:
        xx = xr(r)
        out.append(f'<line x1="{xx:.1f}" y1="{chart_top}" x2="{xx:.1f}" y2="{state_bottom}" '
                   f'stroke="#f0f1f3" stroke-width="1"/>')
        out.append(ctext(xx, xaxis_y, str(r), 16, GRAY))
    out.append(ctext(chart_x + chart_w / 2, xaxis_title_y, "round", 16, GRAY))

    # spread ribbons (draw first, under the state lines)
    for ln in lines:
        pts = [(xr(r), spread_bottom - spread_h * (v / spread_max)) for r, v in zip(ROUNDS, ln["spread"])]
        path = f"M {chart_x:.1f} {spread_bottom:.1f} " + " ".join(f"L {x:.1f} {y:.1f}" for x, y in pts) + \
               f" L {chart_x+chart_w:.1f} {spread_bottom:.1f} Z"
        out.append(f'<path d="{path}" fill="{ln["fill"]}" stroke="{ln["stroke"]}" stroke-width="1.4"/>')

    # marker for external supply — sits in its own reserved lane above the chart
    if marker_round is not None:
        mx = xr(marker_round)
        out.append(f'<line x1="{mx:.1f}" y1="{marker_lane + 6:.1f}" x2="{mx:.1f}" y2="{spread_bottom:.1f}" '
                   f'stroke="{AMBER}" stroke-width="2" stroke-dasharray="5 4"/>')
        out.append(f'<polygon points="{mx-7:.1f},{marker_lane-2:.1f} {mx+7:.1f},{marker_lane-2:.1f} {mx:.1f},{marker_lane+10:.1f}" '
                   f'fill="{AMBER}"/>')
        label_anchor = "start" if mx < chart_x + chart_w * 0.6 else "end"
        lx = mx + 10 if label_anchor == "start" else mx - 10
        out.append(ltext(lx, marker_lane + 4, marker_label, 15, AMBER, "bold", label_anchor))

    # state lines
    for ln in lines:
        pts = " ".join(f"{xr(r):.1f},{ys(v):.1f}" for r, v in zip(ROUNDS, ln["state"]))
        out.append(f'<polyline points="{pts}" fill="none" stroke="{ln["color"]}" stroke-width="4.5"/>')
        for r, v in zip(ROUNDS, ln["state"]):
            out.append(marker(xr(r), ys(v), ln["color"], 5.5))
        if ln.get("start_label"):
            dx, dy, anch = ln.get("start_label_pos", (-6, -14, "start"))
            out.append(ltext(xr(0) + dx, ys(ln["state"][0]) + dy, ln["start_label"], 19, ln["color"], "bold", anch))
        if ln.get("end_label"):
            dx, dy, anch = ln.get("end_label_pos", (6, -12, "end"))
            out.append(ltext(xr(4) + dx, ys(ln["state"][4]) + dy, ln["end_label"], 19, ln["color"], "bold", anch))
        if ln.get("mid_label"):
            r_m, txt = ln["mid_label"][:2]
            dx, dy, anch = ln["mid_label"][2] if len(ln["mid_label"]) > 2 else (0, 20, "middle")
            out.append(ltext(xr(r_m) + dx, ys(ln["state"][r_m]) + dy, txt, 15, ln.get("label_color", GRAY), "normal", anch))
        if ln.get("side_note"):
            r_n, txt, dy = ln["side_note"]
            out.append(ltext(xr(r_n) + 8, ys(ln["state"][r_n]) + dy, txt, 15, ln["color"], "normal", "start"))

    return "\n".join(out)


# ---------------------------------------------------------------- figure
b = []
W = 1500

b.append(ctext(W // 2, 50, "Selection can use up the answers it needs — refilling them reopens movement", 28, INK, "bold"))
b.append(ctext(W // 2, 82, "Three situations, each followed round by round: writing candidate answers, selecting some, and training on them.", BODY, GRAY))

# shared key
ky = 114
kx = W // 2 - 430
b.append(f'<line x1="{kx}" y1="{ky}" x2="{kx+40}" y2="{ky}" stroke="{BLUE}" stroke-width="4.5"/>')
b.append(ltext(kx + 50, ky + 5, "the value's state, round by round", BODY, INK))
kx2 = kx + 400
b.append(box(kx2, ky - 12, 30, 20, STATE_FILL, STATE_STROKE, 1.4, rx=4))
b.append(ltext(kx2 + 40, ky + 5, "how much that round's candidate answers vary", BODY, INK))
kx3 = kx2 + 470
b.append(f'<polygon points="{kx3-6:.1f},{ky-10:.1f} {kx3+6:.1f},{ky-10:.1f} {kx3:.1f},{ky+2:.1f}" fill="{AMBER}"/>')
b.append(ltext(kx3 + 14, ky + 5, "another source of answers added", BODY, INK))

# panel grid — three situations in a row
PANEL_TOP = 168
PW, PH = 453, 452
GAPX = 40
COLS = [30, 30 + PW + GAPX, 30 + 2 * (PW + GAPX)]
ROW = PANEL_TOP

b.append(draw_panel(
    COLS[0], ROW, PW, PH,
    "Rich answers: the value reverses",
    "Answers keep varying, round after round.",
    [dict(state=P1_STATE, spread=P1_SPREAD, color=BLUE, fill=STATE_FILL, stroke=STATE_STROKE,
          start_label="0.917", end_label="0.094")],
))

b.append(draw_panel(
    COLS[1], ROW, PW, PH,
    "Answers refilled: reversal reopens",
    "New answers keep arriving as it falls.",
    [dict(state=P3_STATE, spread=P3_SPREAD, color=BLUE, fill=STATE_FILL, stroke=STATE_STROKE,
          start_label="1.000", start_label_pos=(14, -4, "start"),
          end_label="0.484",
          side_note=(3, "0.208", -18))],
    marker_round=0, marker_label="another source added",
))

b.append(draw_panel(
    COLS[2], ROW, PW, PH,
    "A second model family: stalls, then reopens",
    "Runs dry, holds — then the base model's answers restart the fall.",
    [
        dict(state=P4_OWN_STATE, spread=P4_OWN_SPREAD, color=GRAY, fill=OWN_FILL, stroke=OWN_STROKE,
             mid_label=(2, "the model's own answers only", (0, -14, "middle"))),
        dict(state=P4_ADDED_STATE, spread=P4_ADDED_SPREAD, color=BLUE, fill=STATE_FILL, stroke=STATE_STROKE,
             start_label="0.627", start_label_pos=(-6, -14, "start"),
             end_label="0.000", end_label_pos=(6, -12, "end"),
             mid_label=(2, "with the base model's answers added", (0, -18, "middle"))),
    ],
    marker_round=1, marker_label="answers added",
))

TY = ROW + PH + 56
b.append(text_block(W // 2, TY,
    "Selection can consume the variation it depends on; adding answers from another source refills it, "
    "but the endpoint depends on what's added.",
    20, 74, INK, "bold")[0])

H = TY + 40
with open(os.path.join(FIGDIR, "synthesis_window_through_time.svg"), "w") as f:
    f.write(svg_doc(W, H, "\n".join(b)))
print("wrote synthesis_window_through_time.svg")
