#!/usr/bin/env python3
"""Horizon-resolved forecast-error ladder for the simple value-dynamics models.

Connects two published results on the same corpus:
  - one-round value predictor (kept-mean one-step law, pooled MAE ~0.081,
    docs/report_value_predictor_models.md)
  - closed-loop endpoint rollout (LOCO frozen mean-SD model, selection-driven
    endpoint MAE ~0.127, docs/report_spread_rollout_bakeoff.md)

Question: how does forecast error grow with forecast horizon (rounds ahead of
the first measured pool) for each simple model?

Inputs (committed):
  experiments/spread_rollout_bakeoff.json
    validations.leave_one_condition_out.{frozen,geometry}
      .mean_within_prompt_population_sd.per_run  (67 modelable runs, per-round
      closed-loop LOCO predictions: value_after_pred vs value_after_true)
    judge_swap_refresh.leave_one_condition_out.mean_sd_frozen.per_run
      (9 judge-swap runs, closed-loop re-launched from remeasured state at the
      judge-swap round: refreshed_rounds)
  experiments/spread_util_unified.json
    records (340 per-round observations: value, drift, kept_mean, pool_mean,
    rho, spread), used for the re-measure-every-round one-step models.

Models scored at each horizon h (h = round index within the run's modelable
window; target = that round's observed value_after_true):
  no_change              : predict v1 (value at the first modelable round)
  closed_frozen          : closed-loop LOCO frozen-mean-SD rollout from round 1
  closed_geometry        : closed-loop LOCO geometry (predicted-spread feedback)
  one_step_kept_mean     : predict that round's observed kept_mean (re-measure
                           every round; parameter-free)
  one_step_unit          : predict pool_mean + rho*spread from that round's
                           observed pool state (the unit selection-response
                           proxy; parameter-free — see
                           report_predictive_model_literature.md)
  one_step_factorized    : same with the 0.958 full-data calibration slope.
                           NOTE: 0.958 is a descriptive fit, not design-derived
                           (the 0.9545 top-2-of-6 order statistic is in units
                           of the underlying normal SD, not the realized
                           six-candidate SD; scale audit in
                           experiments/selection_response_predictor.json)
  closed_unit            : closed-loop unit recurrence measured once at the
                           boundary — m_next = clip((1-u)m + u*supplier + rho*
                           sigma) with boundary refresh at judge swaps; per-run
                           trajectories read from
                           experiments/selection_response_predictor.json
  refresh_at_swap        : judge-swap runs only; closed_frozen before the swap
                           round, then the remeasured-at-swap rollout from the
                           swap round onward.

Output: experiments/model_ladder_horizon.json
Report: docs/report_model_ladder_horizon.md (written separately)

Run: uv run python scripts/analysis_model_ladder_horizon.py
"""

import json
import math
import os
import sys
from collections import defaultdict

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BAKEOFF_PATH = os.path.join(REPO, "experiments", "spread_rollout_bakeoff.json")
UNIFIED_PATH = os.path.join(REPO, "experiments", "spread_util_unified.json")
UNITREC_PATH = os.path.join(
    REPO, "experiments", "selection_response_predictor.json"
)
OUT_PATH = os.path.join(REPO, "experiments", "model_ladder_horizon.json")

# full-data calibration slope for gap ~ slope * rho * spread; descriptive only,
# NOT design-derived (scale audit in selection_response_predictor.json)
FACTORIZED_SLOPE = 0.958
JOIN_TOL = 2e-3

REGIME_GROUPS = {
    "selection_driven": lambda reg: reg in ("intervention", "self-force"),
    "intervention": lambda reg: reg == "intervention",
    "self_force": lambda reg: reg == "self-force",
    "self_weak": lambda reg: reg == "self-weak",
    "judge_swap": lambda reg: reg == "judge-swap",
    "all_minus_judge_swap": lambda reg: reg != "judge-swap",
}


def run_id(cond, seed, source):
    return (cond, str(seed), source)


def mae_rmse(errors):
    n = len(errors)
    if n == 0:
        return None, None, 0
    mae = sum(abs(e) for e in errors) / n
    rmse = math.sqrt(sum(e * e for e in errors) / n)
    return mae, rmse, n


def main():
    bakeoff = json.load(open(BAKEOFF_PATH))
    unified = json.load(open(UNIFIED_PATH))
    unitrec = json.load(open(UNITREC_PATH))

    loco = bakeoff["validations"]["leave_one_condition_out"]
    frozen_runs = loco["frozen"]["mean_within_prompt_population_sd"]["per_run"]
    geometry_runs = loco["geometry"]["mean_within_prompt_population_sd"]["per_run"]
    swap_refresh = bakeoff["judge_swap_refresh"]["leave_one_condition_out"][
        "mean_sd_frozen"
    ]["per_run"]

    # ------------------------------------------------------------------ joins
    # unified index: (cond, seed, source, round) -> list of records.
    # NOTE: 4 selfaware_loop_grid runs are "glued": two 2-round sub-runs share
    # one (cond, seed, source) key, so (run, round) keys duplicate (rounds go
    # 1,1,2,2). The bakeoff per_run records have the same structure. We
    # disambiguate by matching value_after_true == value + drift per round.
    urec = defaultdict(list)
    for r in unified["records"]:
        urec[(r["cond"], str(r["seed"]), r["source"], r["round"])].append(r)

    # geometry index by run
    geom_by_run = {run_id(r["cond"], r["seed"], r["source"]): r for r in geometry_runs}
    assert len(geom_by_run) == len(geometry_runs)

    # refresh index by (cond, seed) — judge-swap sources are unique per (cond, seed)
    refresh_by_run = {}
    for r in swap_refresh:
        cond, seed, source = r["run_key"].split("|")
        refresh_by_run[run_id(cond, seed, source)] = r

    # unit-recurrence trajectories (boundary refresh already applied for swaps)
    unit_by_run = {}
    for r in unitrec["endpoint_with_boundary_refresh"][
        "recommended_unit_agreement_spread"
    ]["per_run"]:
        cond, seed, source = r["run_key"].split("|")
        unit_by_run[run_id(cond, seed, source)] = r

    # Round-index alignment: bakeoff per_run rounds must be 1-indexed and match
    # the unified `round` numbering (detect a constant offset if not).
    join_fail = 0
    join_total = 0
    offsets_seen = set()
    glued_runs = []

    def try_join(run, off, consume):
        """Match each bakeoff round to an unused unified record at round+off.

        Returns number matched; if consume, stashes the record on the round.
        """
        used = set()
        ok = 0
        for rr in run["rounds"]:
            rid = run_id(run["cond"], run["seed"], run["source"])
            best = None
            for u in urec.get(rid + (rr["round"] + off,), []):
                if id(u) in used:
                    continue
                if abs(rr["value_after_true"] - (u["value"] + u["drift"])) <= JOIN_TOL:
                    best = u
                    break
            if best is not None:
                used.add(id(best))
                ok += 1
                if consume:
                    rr["_unified"] = best
        return ok

    for run in frozen_runs:
        idx = [rr["round"] for rr in run["rounds"]]
        if idx != list(range(1, run["n_rounds"] + 1)):
            # glued run (two sub-runs sharing a key; indices like 1,1,2,2)
            glued_runs.append(run["run_key"])
            assert idx == sorted(idx) and idx[0] == 1, (
                f"unexpected round indexing in {run['run_key']}: {idx}"
            )
        # detect offset by matching value_after_true == value + drift
        detected = None
        for off in (0, 1, -1, 2, -2):
            if try_join(run, off, consume=False) == run["n_rounds"]:
                detected = off
                break
        if detected is None:
            detected = 0  # fall back; failures counted round by round
        offsets_seen.add(detected)
        join_total += run["n_rounds"]
        join_fail += run["n_rounds"] - try_join(run, detected, consume=True)
    assert offsets_seen == {0}, (
        f"bakeoff rounds are re-indexed relative to unified rounds; offsets {offsets_seen}"
    )
    assert join_fail / join_total <= 0.05, (
        f"join failure rate {join_fail}/{join_total} exceeds 5%"
    )

    # geometry rounds must line up with frozen rounds (same truth values)
    for run in frozen_runs:
        rid = run_id(run["cond"], run["seed"], run["source"])
        g = geom_by_run[rid]
        assert g["n_rounds"] == run["n_rounds"]
        for fr, gr in zip(run["rounds"], g["rounds"]):
            assert fr["round"] == gr["round"]
            assert abs(fr["value_after_true"] - gr["value_after_true"]) <= 1e-9

    # ------------------------------------------------------- per-round errors
    # errors[model][group][h] -> list of (run_key, error)
    errors = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    endpoint_errors = defaultdict(lambda: defaultdict(list))
    factorized_skipped = 0
    kept_mean_missing = 0

    def record(model, run, h, pred, truth, is_endpoint):
        err = pred - truth
        for gname, gfn in REGIME_GROUPS.items():
            if gfn(run["regime"]):
                errors[model][gname][h].append(err)
                if is_endpoint:
                    endpoint_errors[model][gname].append(err)

    # Validate unit-recurrence trajectory alignment per run before scoring:
    # same length, same start, and its stored endpoint truth matches the
    # bakeoff truth. Glued runs (round indices 1,1,2,2) are excluded because
    # the unit per-run record treats them as one sequential rollout.
    unit_runs_used = 0
    unit_runs_skipped = []
    for run in frozen_runs:
        rid = run_id(run["cond"], run["seed"], run["source"])
        uu = unit_by_run.get(rid)
        if uu is None:
            unit_runs_skipped.append((run["run_key"], "no unit record"))
            continue
        traj = uu["trajectory"]
        idx = [rr["round"] for rr in run["rounds"]]
        sequential = idx == list(range(1, run["n_rounds"] + 1))
        truth_ok = (
            abs(uu["actual"] - run["rounds"][-1]["value_after_true"]) <= JOIN_TOL
            and abs(uu["predicted"] - traj[-1]) <= 1e-9
        )
        if (
            sequential
            and truth_ok
            and len(traj) == run["n_rounds"]
            and abs(uu["start"] - run["v1"]) <= JOIN_TOL
        ):
            # ordinary run: traj[i] predicts round i+1's value_after_true
            unit_runs_used += 1
            for i, rr in enumerate(run["rounds"]):
                rr["_unit_pred"] = traj[i]
        elif (
            sequential
            and truth_ok
            and 1 <= run["n_rounds"] - len(traj) < run["n_rounds"]
            and abs(
                uu["start"]
                - run["rounds"][run["n_rounds"] - len(traj) - 1]["value_after_true"]
            )
            <= JOIN_TOL
        ):
            # judge-swap runs: the unit rollout starts at the swap boundary
            # (from the observed value entering the first new-judge round) and
            # predicts only the post-swap rounds — a conditional post-swap
            # forecast, like refresh_at_swap's post-swap portion
            off = run["n_rounds"] - len(traj)
            unit_runs_used += 1
            for i, rr in enumerate(run["rounds"][off:]):
                rr["_unit_pred"] = traj[i]
        else:
            unit_runs_skipped.append((run["run_key"], "alignment"))

    for run in frozen_runs:
        rid = run_id(run["cond"], run["seed"], run["source"])
        g = geom_by_run[rid]
        refresh = refresh_by_run.get(rid)
        if refresh is not None:
            swap_round = refresh["first_new_judge_round"]
            refreshed = {rr["round"]: rr for rr in refresh["refreshed_rounds"]}
        for i, rr in enumerate(run["rounds"]):
            h = rr["round"]
            truth = rr["value_after_true"]
            is_end = i == run["n_rounds"] - 1

            record("no_change", run, h, run["v1"], truth, is_end)
            record("closed_frozen", run, h, rr["value_after_pred"], truth, is_end)
            record(
                "closed_geometry", run, h, g["rounds"][i]["value_after_pred"], truth, is_end
            )

            u = rr.get("_unified")
            if u is not None:
                record("one_step_kept_mean", run, h, u["kept_mean"], truth, is_end)
                if u.get("rho") is not None:
                    base = u["rho"] * u["spread"]
                    record(
                        "one_step_unit", run, h, u["pool_mean"] + base, truth, is_end
                    )
                    record(
                        "one_step_factorized",
                        run,
                        h,
                        u["pool_mean"] + FACTORIZED_SLOPE * base,
                        truth,
                        is_end,
                    )
                else:
                    factorized_skipped += 1
            else:
                kept_mean_missing += 1

            if "_unit_pred" in rr:
                record("closed_unit", run, h, rr["_unit_pred"], truth, is_end)

            if refresh is not None:
                if h < swap_round:
                    pred = rr["value_after_pred"]  # closed-loop before the swap
                else:
                    pred = refreshed[h]["value_after_pred"]
                record("refresh_at_swap", run, h, pred, truth, is_end)

    # ---------------------------------------------------------------- anchors
    sel = [r for r in frozen_runs if r["regime"] in ("intervention", "self-force")]
    anchor_frozen_endpoint = sum(
        abs(r["rounds"][-1]["value_after_pred"] - r["rounds"][-1]["value_after_true"])
        for r in sel
    ) / len(sel)
    anchor_nochange_endpoint = sum(
        abs(r["v1"] - r["rounds"][-1]["value_after_true"]) for r in sel
    ) / len(sel)
    all340 = unified["records"]
    anchor_kept_mean_pooled = sum(
        abs(r["kept_mean"] - (r["value"] + r["drift"])) for r in all340
    ) / len(all340)

    # unit-recurrence endpoint anchors, computed endpoint-only from the
    # selection_response per_run records (no round alignment needed), over the
    # same matched run sets as the published numbers
    def unit_endpoint_mae(runs):
        errs = []
        for r in runs:
            rid = run_id(r["cond"], r["seed"], r["source"])
            uu = unit_by_run.get(rid)
            if uu is not None:
                errs.append(abs(uu["predicted"] - uu["actual"]))
        return (sum(errs) / len(errs) if errs else None), len(errs)

    swaps = [r for r in frozen_runs if r["regime"] == "judge-swap"]
    anchor_unit_sel, n_unit_sel = unit_endpoint_mae(sel)
    anchor_unit_comb, n_unit_comb = unit_endpoint_mae(sel + swaps)

    anchors = {
        "frozen_endpoint_mae_selection_driven": {
            "published": 0.127,
            "computed": round(anchor_frozen_endpoint, 4),
            "n_runs": len(sel),
            "reproduces": abs(anchor_frozen_endpoint - 0.127) < 0.003,
        },
        "no_change_endpoint_mae_selection_driven": {
            "published": 0.431,
            "computed": round(anchor_nochange_endpoint, 4),
            "n_runs": len(sel),
            "reproduces": abs(anchor_nochange_endpoint - 0.431) < 0.003,
        },
        "one_step_kept_mean_pooled_mae_340": {
            "published": 0.081,
            "computed": round(anchor_kept_mean_pooled, 4),
            "n_records": len(all340),
            "reproduces": abs(anchor_kept_mean_pooled - 0.081) < 0.003,
        },
        "unit_recurrence_endpoint_mae_selection_driven_matched": {
            "published": 0.118,
            "computed": round(anchor_unit_sel, 4),
            "n_runs": n_unit_sel,
            "reproduces": abs(anchor_unit_sel - 0.118) < 0.003,
        },
        "unit_recurrence_endpoint_mae_combined_45": {
            "published": 0.1365,
            "computed": round(anchor_unit_comb, 4),
            "n_runs": n_unit_comb,
            "reproduces": abs(anchor_unit_comb - 0.1365) < 0.003,
        },
    }

    # ----------------------------------------------------------------- tables
    max_h = max(r["n_rounds"] for r in frozen_runs)
    table = []
    for model in sorted(errors):
        for group in REGIME_GROUPS:
            for h in range(1, max_h + 1):
                errs = errors[model][group].get(h, [])
                mae, rmse, n = mae_rmse(errs)
                if n:
                    table.append(
                        {
                            "model": model,
                            "regime_group": group,
                            "horizon": h,
                            "n_runs": n,
                            "mae": round(mae, 4),
                            "rmse": round(rmse, 4),
                        }
                    )
            errs = endpoint_errors[model].get(group, [])
            mae, rmse, n = mae_rmse(errs)
            if n:
                table.append(
                    {
                        "model": model,
                        "regime_group": group,
                        "horizon": "endpoint",
                        "n_runs": n,
                        "mae": round(mae, 4),
                        "rmse": round(rmse, 4),
                    }
                )

    ladder = []
    for model in sorted(errors):
        row = {"model": model}
        any_sel = False
        for h in (1, 2, 3, 4):
            errs = errors[model]["selection_driven"].get(h, [])
            mae, _, n = mae_rmse(errs)
            row[f"h{h}_mae"] = round(mae, 4) if n else None
            row[f"h{h}_n"] = n
            any_sel = any_sel or n > 0
        errs = endpoint_errors[model].get("selection_driven", [])
        mae, _, n = mae_rmse(errs)
        row["endpoint_mae"] = round(mae, 4) if n else None
        row["endpoint_n"] = n
        if any_sel:
            ladder.append(row)

    # h=1 predicting-vs-observing-selection gap (selection-driven runs).
    # At h=1 both models see the round-1 state; closed_frozen predicts the
    # selection gap from frozen rho*sigma, one_step_kept_mean observes the
    # realized kept set. Their h=1 MAE difference is the cost of predicting
    # selection rather than observing it.
    cf = errors["closed_frozen"]["selection_driven"][1]
    km = errors["one_step_kept_mean"]["selection_driven"][1]
    assert len(cf) == len(km), "h=1 run sets differ between closed_frozen and kept_mean"
    cf_mae = sum(abs(e) for e in cf) / len(cf)
    km_mae = sum(abs(e) for e in km) / len(km)

    # matched-set version on the runs the unit recurrence covers (glued runs
    # excluded): score closed_frozen, closed_unit, and one_step_kept_mean at
    # h=1 on exactly the same selection-driven runs
    m_cf, m_cu, m_km = [], [], []
    for run in frozen_runs:
        if run["regime"] not in ("intervention", "self-force"):
            continue
        rr = run["rounds"][0]
        if "_unit_pred" not in rr or "_unified" not in rr:
            continue
        truth = rr["value_after_true"]
        m_cf.append(abs(rr["value_after_pred"] - truth))
        m_cu.append(abs(rr["_unit_pred"] - truth))
        m_km.append(abs(rr["_unified"]["kept_mean"] - truth))
    h1_gap = {
        "closed_frozen_h1_mae": round(cf_mae, 4),
        "one_step_kept_mean_h1_mae": round(km_mae, 4),
        "gap_mae": round(cf_mae - km_mae, 4),
        "n_runs": len(cf),
        "reading": (
            "difference is the cost of predicting the selection gap from frozen "
            "rho*sigma versus observing the realized kept set at round 1 — for "
            "the FITTED frozen-SD implementation; see matched_set for the unit "
            "recurrence"
        ),
        "matched_set_excluding_glued": {
            "n_runs": len(m_cf),
            "closed_frozen_h1_mae": round(sum(m_cf) / len(m_cf), 4),
            "closed_unit_h1_mae": round(sum(m_cu) / len(m_cu), 4),
            "one_step_kept_mean_h1_mae": round(sum(m_km) / len(m_km), 4),
            "reading": (
                "on identical runs, predicting selection costs 0.015 MAE (unit "
                "recurrence) or 0.023 (fitted frozen-SD) over observing the "
                "kept set; the pooled 0.033 figure is inflated by the glued "
                "runs, which only the fitted models cover"
            ),
        },
    }

    out = {
        "description": (
            "Horizon-resolved forecast-error ladder connecting the one-round "
            "value predictor and the closed-loop rollout bakeoff on the same "
            "67 modelable runs. Horizon h = round index within the run's "
            "modelable window; target = that round's observed value_after_true. "
            "One-step models are conditioned on observations the closed-loop "
            "models do not receive, so gaps read as 'value of re-measuring', "
            "not model quality."
        ),
        "inputs": {
            "bakeoff": "experiments/spread_rollout_bakeoff.json",
            "unified": "experiments/spread_util_unified.json",
            "unit_recurrence": "experiments/selection_response_predictor.json",
        },
        "models": {
            "no_change": "predict v1 at every horizon",
            "closed_frozen": "closed-loop LOCO frozen-mean-SD rollout from round 1 (measure once)",
            "closed_geometry": "closed-loop LOCO geometry rollout (predicted-spread feedback)",
            "one_step_kept_mean": "predict that round's observed kept_mean (re-measure every round; parameter-free)",
            "one_step_unit": (
                "predict pool_mean + rho*spread from that round's observed pool "
                "state (unit selection-response proxy; parameter-free; rounds "
                "with null rho skipped)"
            ),
            "one_step_factorized": (
                f"predict pool_mean + {FACTORIZED_SLOPE}*rho*spread from that round's "
                "observed pool state (full-data calibration slope; descriptive, "
                "NOT design-derived — see the scale audit in "
                "selection_response_predictor.json; rounds with null rho skipped)"
            ),
            "closed_unit": (
                "closed-loop unit recurrence measured once at the boundary: "
                "m_next = clip((1-u)m + u*supplier + rho*sigma, 0, 1) with a "
                "boundary refresh at judge swaps; trajectories read from "
                "selection_response_predictor.json; glued runs excluded "
                "(sequential-rollout ambiguity)"
            ),
            "refresh_at_swap": (
                "judge-swap runs only: closed_frozen predictions before the judge-swap "
                "round, then the closed-loop rollout re-launched from state remeasured "
                "on the first pool scored by the new judge"
            ),
        },
        "join_diagnostics": {
            "joined_rounds": join_total,
            "failed_rounds": join_fail,
            "round_index_offset": 0,
            "note": (
                "bakeoff per_run rounds are 1-indexed and align with the unified "
                "`round` field with zero offset; value_after_true == value + drift "
                f"within {JOIN_TOL} for every joined round"
            ),
            "glued_runs": glued_runs,
            "glued_runs_note": (
                "these runs concatenate two 2-round sub-runs under one "
                "(cond, seed, source) key with round indices 1,1,2,2 in both "
                "files; duplicates were disambiguated by matching "
                "value_after_true to value + drift; each contributes two "
                "predictions at h=1 and h=2 and none beyond; the endpoint is "
                "the last listed round (matching the published bakeoff "
                "endpoint aggregation)"
            ),
            "factorized_rounds_skipped_null_rho": factorized_skipped,
            "kept_mean_rounds_missing_unified_record": kept_mean_missing,
            "closed_unit_runs_used": unit_runs_used,
            "closed_unit_runs_skipped": [
                {"run_key": k, "reason": why} for k, why in unit_runs_skipped
            ],
        },
        "anchors": anchors,
        "regime_groups": {
            "selection_driven": "intervention + self-force (36 runs)",
            "intervention": "intervention (24 runs)",
            "self_force": "self-force (12 runs)",
            "self_weak": "self-weak (22 runs)",
            "judge_swap": "judge-swap (9 runs)",
            "all_minus_judge_swap": "everything except judge-swap (58 runs)",
        },
        "table_note": (
            "n_runs counts predictions at that horizon (one per run, except the "
            "4 glued selfaware_loop_grid runs, which contribute two each at h=1 "
            "and h=2); runs contribute at horizon h only if they have >= h rounds"
        ),
        "table": table,
        "ladder_summary_selection_driven": ladder,
        "h1_predicting_vs_observing_selection_gap": h1_gap,
        "judge_swap_refresh_handling": (
            "judge_swap_refresh.leave_one_condition_out.mean_sd_frozen.per_run "
            "contains per-round predictions (refreshed_rounds) for all 9 judge-swap "
            "runs, so the refresh_at_swap model is included; before the swap round "
            "it uses the closed_frozen predictions (identical information set)"
        ),
    }

    with open(OUT_PATH, "w") as f:
        json.dump(out, f, indent=1)

    # ------------------------------------------------------------ stdout dump
    print(f"wrote {OUT_PATH}")
    print("\n=== ANCHORS ===")
    for k, v in anchors.items():
        print(
            f"{k}: published {v['published']}  computed {v['computed']}  "
            f"reproduces={v['reproduces']}"
        )
    print("\n=== JOIN ===")
    print(
        f"{join_total} bakeoff rounds joined to unified, {join_fail} failures, "
        f"offset 0; factorized skipped {factorized_skipped} null-rho rounds"
    )
    print("\n=== LADDER (selection-driven, MAE) ===")
    hdr = f"{'model':24s} {'h=1':>8s} {'h=2':>8s} {'h=3':>8s} {'h=4':>8s} {'endpoint':>9s}"
    print(hdr)
    for row in ladder:
        cells = [
            f"{row[f'h{h}_mae']:.4f}" if row[f"h{h}_mae"] is not None else "-"
            for h in (1, 2, 3, 4)
        ]
        ep = f"{row['endpoint_mae']:.4f}" if row["endpoint_mae"] is not None else "-"
        print(
            f"{row['model']:24s} {cells[0]:>8s} {cells[1]:>8s} {cells[2]:>8s} "
            f"{cells[3]:>8s} {ep:>9s}"
        )
    print(f"(n runs at h=1..4: {[ladder[0][f'h{h}_n'] for h in (1,2,3,4)]}, "
          f"endpoint n={ladder[0]['endpoint_n']})")
    print("\n=== h=1 GAP (predicting vs observing selection, selection-driven) ===")
    print(
        f"closed_frozen h1 MAE {h1_gap['closed_frozen_h1_mae']}  "
        f"one_step_kept_mean h1 MAE {h1_gap['one_step_kept_mean_h1_mae']}  "
        f"gap {h1_gap['gap_mae']}  (n={h1_gap['n_runs']})"
    )
    print("\n=== JUDGE-SWAP (MAE by horizon) ===")
    for model in ("no_change", "closed_frozen", "refresh_at_swap"):
        cells = []
        for h in range(1, max_h + 1):
            errs = errors[model]["judge_swap"].get(h, [])
            m, _, n = mae_rmse(errs)
            cells.append(f"h{h}={m:.3f}" if n else f"h{h}=-")
        ep, _, n = mae_rmse(endpoint_errors[model].get("judge_swap", []))
        print(f"{model:24s} {' '.join(cells)}  endpoint={ep:.3f} (n={n})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
