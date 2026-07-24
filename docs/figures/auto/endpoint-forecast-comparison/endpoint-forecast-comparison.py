#!/usr/bin/env python3
"""Predicted-versus-observed endpoint figure for the scored 36-run comparison.

The previous rho-by-sigma background was not a well-defined per-run forecast:
endpoint movement also depends on the starting value and, in mixed pools, the
outside-source mean. This figure instead plots the stored state-aware unit
recurrence predictions that produce the writeup's 0.118 endpoint MAE, beside
the no-change predictions that produce 0.431.

Inputs:
  experiments/spread_rollout_bakeoff.json
  experiments/selection_response_predictor.json

Output:
  endpoint-forecast-comparison.svg
"""

import html
import json
import math
from pathlib import Path


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
BAKEOFF = REPO / "experiments" / "spread_rollout_bakeoff.json"
UNIT = REPO / "experiments" / "selection_response_predictor.json"
OUT = HERE / "endpoint-forecast-comparison.svg"

W, H = 1440, 820
INK = "#1a1a1a"
MUTED = "#66717c"
GRID = "#dde2e7"
BLUE = "#2867b5"
AMBER = "#a8720f"
FONT = "Helvetica, Arial, sans-serif"


def esc(value):
    return html.escape(str(value))


def load_rows():
    bakeoff = json.loads(BAKEOFF.read_text())
    unit = json.loads(UNIT.read_text())

    runs = bakeoff["validations"]["leave_one_condition_out"]["frozen"][
        "mean_within_prompt_population_sd"
    ]["per_run"]
    selected = [
        run for run in runs if run["regime"] in ("intervention", "self-force")
    ]
    unit_rows = unit["endpoint_with_boundary_refresh"][
        "recommended_unit_agreement_spread"
    ]["per_run"]
    unit_by_key = {row["run_key"]: row for row in unit_rows}

    rows = []
    for run in selected:
        forecast = unit_by_key[run["run_key"]]
        actual = run["rounds"][-1]["value_after_true"]
        assert abs(actual - forecast["actual"]) <= 0.002
        rows.append(
            {
                "run_key": run["run_key"],
                "organism": run["organism"],
                "axis": run["axis"],
                "actual": actual,
                "unit": forecast["predicted"],
                "no_change": run["v1"],
            }
        )

    assert len(rows) == 36
    unit_mae = sum(abs(r["unit"] - r["actual"]) for r in rows) / len(rows)
    no_change_mae = sum(
        abs(r["no_change"] - r["actual"]) for r in rows
    ) / len(rows)
    assert abs(unit_mae - 0.118117) < 1e-6
    assert abs(no_change_mae - 0.4309) < 0.001
    return rows, unit_mae, no_change_mae


ROWS, UNIT_MAE, NO_CHANGE_MAE = load_rows()

PANELS = [
    {
        "x0": 105,
        "x1": 665,
        "title": "State-aware unit recurrence",
        "subtitle": f"endpoint MAE {UNIT_MAE:.3f}",
        "field": "unit",
    },
    {
        "x0": 780,
        "x1": 1340,
        "title": "Assume no change",
        "subtitle": f"endpoint MAE {NO_CHANGE_MAE:.3f}",
        "field": "no_change",
    },
]
Y0, Y1 = 650, 190


def px(panel, value):
    return panel["x0"] + value * (panel["x1"] - panel["x0"])


def py(value):
    return Y0 - value * (Y0 - Y1)


def marker(row, cx, cy):
    is_olmo = row["organism"] == "OLMo"
    fill = BLUE if is_olmo else AMBER
    if is_olmo:
        return (
            f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="8.7" fill="white" '
            f'stroke="white" stroke-width="5"/>'
            f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="7.1" fill="{fill}" '
            f'fill-opacity="0.78" stroke="#35404a" stroke-width="1.1"/>'
        )
    size = 9.2
    points = (
        f"{cx:.1f},{cy-size:.1f} "
        f"{cx-size*0.9:.1f},{cy+size*0.65:.1f} "
        f"{cx+size*0.9:.1f},{cy+size*0.65:.1f}"
    )
    halo_size = size + 2.2
    halo_points = (
        f"{cx:.1f},{cy-halo_size:.1f} "
        f"{cx-halo_size*0.9:.1f},{cy+halo_size*0.65:.1f} "
        f"{cx+halo_size*0.9:.1f},{cy+halo_size*0.65:.1f}"
    )
    return (
        f'<polygon points="{halo_points}" fill="white" stroke="white" '
        f'stroke-width="4"/>'
        f'<polygon points="{points}" fill="{fill}" fill-opacity="0.82" '
        f'stroke="#35404a" stroke-width="1.1"/>'
    )


svg = [
    f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
    f'font-family="{FONT}">',
    f'<rect width="{W}" height="{H}" fill="white"/>',
    f'<text x="70" y="52" font-size="30" font-weight="bold" fill="{INK}">'
    "First-round measurements predict final values</text>",
    f'<text x="70" y="84" font-size="18" fill="{MUTED}">'
    "The same 36 selection-driven runs in both panels; the diagonal is perfect prediction.</text>",
]

# Legend
svg.extend(
    [
        f'<circle cx="92" cy="118" r="7.1" fill="{BLUE}" fill-opacity="0.78" '
        'stroke="#35404a" stroke-width="1.1"/>',
        f'<text x="108" y="124" font-size="15.5" fill="{INK}">OLMo-3-7B · risk-seeking (25)</text>',
        f'<polygon points="382,109 374,123 390,123" fill="{AMBER}" '
        'fill-opacity="0.82" stroke="#35404a" stroke-width="1.1"/>',
        f'<text x="400" y="124" font-size="15.5" fill="{INK}">Qwen3-4B · insecure-code self-description (11)</text>',
    ]
)

for panel in PANELS:
    center = (panel["x0"] + panel["x1"]) / 2
    svg.append(
        f'<text x="{center:.1f}" y="158" text-anchor="middle" font-size="21" '
        f'font-weight="bold" fill="{INK}">{esc(panel["title"])}</text>'
    )
    svg.append(
        f'<text x="{center:.1f}" y="181" text-anchor="middle" font-size="17" '
        f'fill="{MUTED}">{esc(panel["subtitle"])}</text>'
    )

    for tick in (0, 0.25, 0.5, 0.75, 1.0):
        x = px(panel, tick)
        y = py(tick)
        svg.append(
            f'<line x1="{x:.1f}" y1="{Y1}" x2="{x:.1f}" y2="{Y0}" '
            f'stroke="{GRID}" stroke-width="1"/>'
        )
        svg.append(
            f'<line x1="{panel["x0"]}" y1="{y:.1f}" x2="{panel["x1"]}" '
            f'y2="{y:.1f}" stroke="{GRID}" stroke-width="1"/>'
        )
        label = f"{tick:.2f}".rstrip("0").rstrip(".")
        svg.append(
            f'<text x="{x:.1f}" y="674" text-anchor="middle" font-size="14" '
            f'fill="{MUTED}">{label}</text>'
        )
        svg.append(
            f'<text x="{panel["x0"]-12}" y="{y+5:.1f}" text-anchor="end" '
            f'font-size="14" fill="{MUTED}">{label}</text>'
        )

    svg.append(
        f'<rect x="{panel["x0"]}" y="{Y1}" width="{panel["x1"]-panel["x0"]}" '
        f'height="{Y0-Y1}" fill="none" stroke="{MUTED}" stroke-width="1.4"/>'
    )
    svg.append(
        f'<line x1="{panel["x0"]}" y1="{Y0}" x2="{panel["x1"]}" y2="{Y1}" '
        'stroke="#717b85" stroke-width="1.8" stroke-dasharray="7 6"/>'
    )
    svg.append(
        f'<text x="{center:.1f}" y="712" text-anchor="middle" font-size="17" '
        f'fill="{INK}">observed final value</text>'
    )
    svg.append(
        f'<text x="{panel["x0"]-67}" y="{(Y0+Y1)/2:.1f}" text-anchor="middle" '
        f'font-size="17" fill="{INK}" transform="rotate(-90 {panel["x0"]-67} {(Y0+Y1)/2})">'
        "predicted final value</text>"
    )

    # Draw the less crowded interior first and rail points last with opacity.
    for row in sorted(ROWS, key=lambda r: abs(r["actual"] - 0.5)):
        svg.append(marker(row, px(panel, row["actual"]), py(row[panel["field"]])))

svg.extend(
    [
        f'<text x="720" y="760" text-anchor="middle" font-size="16" fill="{INK}">'
        "The recurrence uses the full first-round state: starting value, spread, agreement, and pool composition.</text>",
        f'<text x="720" y="785" text-anchor="middle" font-size="15" fill="{MUTED}">'
        "Updates are clipped to the 0–1 value range; mixed-pool supply is included.</text>",
        "</svg>",
    ]
)

OUT.write_text("\n".join(svg) + "\n")
print(
    f"wrote {OUT.name}: n={len(ROWS)}, unit MAE={UNIT_MAE:.4f}, "
    f"no-change MAE={NO_CHANGE_MAE:.4f}"
)

