"""Unified spread x utilization accounting across EVERY score-logged loop round
we have — own-pool AND mixed/injected pools, OLMo risk axis AND Qwen
insecure-code self-report axis.

Motivation (writeup refocus, 2026-07-15): the writeup's spine becomes
  (1) the realized selection gap predicts next movement,
  (2) the gap factorizes into pool value-spread x judge utilization,
  (3) simple models for how spread and utilization behave.
The own-pool bookkeeping exists (state_space_explore.json, taste-alignment
rho-sigma factorization). What was missing is the SAME accounting on the
mixed-generator / injection cells, plus the quantity that unifies own-pool and
mixed-pool movement: the KEPT PULL.

Per round k of a run with measured-value trajectory v0..vN:
  value      = v_{k-1}                      (measured value before the round)
  spread     = mean within-item population SD of candidate value scores:
               for prompt j, sigma_j = sqrt(mean_k (x_jk - xbar_j)^2),
               then spread = mean_j sigma_j. This is NOT the SD after pooling
               candidates across prompts and uses ddof=0.
  pool_mean  = mean candidate value score
  kept_mean  = mean value score of kept candidates
  gap        = kept_mean - pool_mean        (the realized selection gap)
  pool_supply_shift = pool_mean - own_mean  (how mixing moves the offered
                                             pool away from the model's own
                                             generated candidates)
  self_relative_gap = kept_mean - own_mean  (training-target displacement
                                             relative to the model's own
                                             generated pool)
  generator_calibration_residual = own_mean - value
  pull       = kept_mean - value            (where training material sits
                                             relative to the current value;
                                             own-pool: pool_mean ~= value so
                                             pull ~= gap; mixed pools: the two
                                             come apart and pull carries the
                                             supplier term)
  drift      = v_k - v_{k-1}
  util       = null-centred utilization, per item then averaged:
               (|kept-pair offset| - random-pair null) / (achievable - null),
               enumerating all C(n, n_kept) pairs (same formula as
               analysis_own_pool_records.py; 0 = random, 1 = most-extreme pair;
               NOT comparable across organisms)
  kept_cogen = fraction of kept candidates owned by the co-generator

Fits (all descriptive; no causal claim):
  movement law   drift ~ pull and drift ~ gap, per family and pooled,
                 plus per composition class (self-only / base-mixed / peer-mixed)
  factorization  |gap| regressed on spread alone, util alone, spread*util
  spread ledger  sigma_{t+1} ~ sigma_t per family x composition; mean spread by
                 round; the matched reopen-vs-twin pair spelled out
  util ledger    mean/sd by organism x judge x format x composition; variance
                 split within-run vs between-cell

Run:  uv run python scripts/analysis_spread_util_unified.py
Writes: experiments/spread_util_unified.json.  numpy only.
"""
import itertools
import json
import math
import os
from collections import defaultdict

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# ---------------------------------------------------------------- helpers
def util_items(items, score_key):
    """Null-centred utilization + achievable, per item, averaged."""
    us = []
    for it in items:
        c = it.get(score_key)
        kidx = it.get("kept_idx")
        if not c or not kidx:
            continue
        nk = len(kidx)
        if len(c) < nk + 1:
            continue
        m = sum(c) / len(c)
        realized = abs(sum(c[i] for i in kidx) / nk - m)
        pair_gaps = [abs(sum(c[j] for j in p) / nk - m)
                     for p in itertools.combinations(range(len(c)), nk)]
        ach = max(pair_gaps)
        null = sum(pair_gaps) / len(pair_gaps)
        if ach - null > 1e-9:
            us.append((realized - null) / (ach - null))
    return (sum(us) / len(us)) if us else None


def rho_items(items, score_key, judge_key, oracle_sign=None):
    """Mean within-item Pearson corr(judge score, candidate value).

    The score oracle's decision rule IS the (negated) value score, so when a
    cell has no logged judge scores but the judge is the score oracle,
    oracle_sign (+1/-1 toward its target) supplies the score synthetically."""
    rs = []
    for it in items:
        c = it.get(score_key)
        if not c or len(c) < 3 or np.std(c) < 1e-9:
            continue
        # the score oracle's decision rule IS (sign x) the value score; use the
        # rule itself, not logged near-tie score vectors, so rho is exact
        if oracle_sign is not None:
            s = [oracle_sign * x for x in c]
        else:
            s = it.get(judge_key) if judge_key else None
        if not isinstance(s, list) or len(s) != len(c) or np.std(s) < 1e-9:
            continue
        rs.append(float(np.corrcoef(s, c)[0, 1]))
    return (sum(rs) / len(rs)) if rs else None


def selection_response_items(items, score_key, judge_key, oracle_sign=None):
    """No-fit correlated-response gap using each judge-score distribution.

    For each prompt, regress candidate value on standardized judge score and
    apply that linear response to the top-k judge-score shift.  The resulting
    rho * value_sd * judge_selection_intensity uses the realized finite pool;
    unlike a population truncation constant, it is on the same sample-SD scale
    as the project's spread measurement.
    """
    predicted, intensities = [], []
    for item in items:
        values = item.get(score_key)
        kept_idx = item.get("kept_idx")
        if not values or not kept_idx:
            continue
        values = np.asarray(values, float)
        if oracle_sign is not None:
            scores = oracle_sign * values
        else:
            raw_scores = item.get(judge_key) if judge_key else None
            if not isinstance(raw_scores, list) or len(raw_scores) != len(values):
                continue
            scores = np.asarray(raw_scores, float)
        score_sd = float(np.std(scores))
        value_sd = float(np.std(values))
        if score_sd < 1e-9:
            continue
        n_kept = len(kept_idx)
        predicted_kept = np.argsort(-scores, kind="stable")[:n_kept]
        intensity = float(
            (np.mean(scores[predicted_kept]) - np.mean(scores)) / score_sd
        )
        correlation = (
            float(np.corrcoef(scores, values)[0, 1])
            if value_sd >= 1e-9 else 0.0
        )
        predicted.append(correlation * value_sd * intensity)
        intensities.append(intensity)
    if not predicted:
        return None
    return {
        "predicted_gap": float(np.mean(predicted)),
        "judge_selection_intensity": float(np.mean(intensities)),
        "n_items": len(predicted),
    }


def candidate_distribution_metrics(groups):
    """Describe candidate-score variation without pooling prompts together.

    A prompt is sampled uniformly, then a candidate is sampled uniformly from
    that prompt. This matches the per-prompt averaging used by the selector
    analysis even if a future dataset has unequal candidate counts.
    """
    arrays = [np.asarray(c, float) for c in groups if c]
    if not arrays:
        return None
    means = np.asarray([np.mean(c) for c in arrays], float)
    variances = np.asarray([np.var(c) for c in arrays], float)  # population
    sds = np.sqrt(variances)
    pairwise_abs = []
    any_difference = []
    mean_abs_deviations = []
    ranges = []
    entropy_bits = []
    binary_entries = 0
    total_entries = 0
    for c in arrays:
        total_entries += len(c)
        is_binary = np.isclose(c, 0.0) | np.isclose(c, 1.0)
        binary_entries += int(np.sum(is_binary))
        pairs = list(itertools.combinations(range(len(c)), 2))
        pairwise_abs.append(
            float(np.mean([abs(c[a] - c[b]) for a, b in pairs])) if pairs else 0.0
        )
        any_difference.append(float(np.ptp(c) > 1e-12))
        mean_abs_deviations.append(float(np.mean(np.abs(c - np.mean(c)))))
        ranges.append(float(np.ptp(c)))
        if bool(np.all(is_binary)):
            p = float(np.mean(c))
            entropy_bits.append(
                0.0 if p <= 0.0 or p >= 1.0
                else -(p * math.log2(p) + (1.0 - p) * math.log2(1.0 - p))
            )
    mean_variance = float(np.mean(variances))
    between_item_variance = float(np.var(means))
    hierarchical_mean = float(np.mean(means))
    hierarchical_total_variance = mean_variance + between_item_variance
    # For binary scores, total variance under this hierarchical sampling scheme
    # is exactly p(1-p). Keep this identity visible for downstream audits.
    binary_headroom = hierarchical_mean * (1.0 - hierarchical_mean)
    all_binary = binary_entries == total_entries
    if all_binary and abs(hierarchical_total_variance - binary_headroom) > 1e-10:
        raise ValueError("binary within/between-prompt variance identity failed")
    return {
        "n_items": len(arrays),
        "candidate_count_min": int(min(len(c) for c in arrays)),
        "candidate_count_max": int(max(len(c) for c in arrays)),
        "binary_score_fraction": float(binary_entries / total_entries),
        "score_min": float(min(np.min(c) for c in arrays)),
        "score_max": float(max(np.max(c) for c in arrays)),
        "mean": hierarchical_mean,
        "mean_item_sd": float(np.mean(sds)),
        "median_item_sd": float(np.median(sds)),
        "mean_item_variance": mean_variance,
        "rms_item_sd": math.sqrt(max(0.0, mean_variance)),
        "mean_item_mean_absolute_deviation": float(np.mean(mean_abs_deviations)),
        "mean_item_range": float(np.mean(ranges)),
        "mean_pairwise_absolute_difference": float(np.mean(pairwise_abs)),
        "fraction_items_with_any_difference": float(np.mean(any_difference)),
        "mean_item_binary_entropy_bits": (
            float(np.mean(entropy_bits)) if len(entropy_bits) == len(arrays) else None
        ),
        "between_item_mean_variance": between_item_variance,
        "hierarchical_total_variance": hierarchical_total_variance,
        "hierarchical_total_sd": math.sqrt(max(0.0, hierarchical_total_variance)),
        "binary_headroom": binary_headroom if all_binary else None,
    }


def round_record(items, score_key, v_before, v_after, judge_key=None, oracle_sign=None):
    vals = [it[score_key] for it in items if it.get(score_key) and it.get("kept_idx")]
    keeps = [it["kept_idx"] for it in items if it.get(score_key) and it.get("kept_idx")]
    if not vals:
        return None
    metrics = candidate_distribution_metrics(vals)
    spread = metrics["mean_item_sd"]
    pool = metrics["mean"]
    kept = float(np.mean([c[i] for c, k in zip(vals, keeps) for i in k]))
    rho = rho_items(items, score_key, judge_key, oracle_sign)
    response = selection_response_items(
        items, score_key, judge_key, oracle_sign
    )
    rec = dict(
        spread=round(spread, 4), pool_mean=round(pool, 4),
        kept_mean=round(kept, 4), gap=round(kept - pool, 4),
        pull=round(kept - v_before, 4),
        value=round(v_before, 4), drift=round(v_after - v_before, 4),
        util=util_items(items, score_key),
        rho=(round(rho, 4) if rho is not None else None),
    )
    # Standardized selection differential on the measured value axis.  This
    # makes gap = spread * value_axis_selection_intensity an exact aggregate
    # decomposition (up to JSON rounding).  Unlike rho, it is observed only
    # after the retained set is known and includes both judge/value alignment
    # and the strength/form of the actual selection rule.
    rec["value_axis_selection_intensity"] = (
        round((kept - pool) / spread, 6) if spread > 1e-12 else 0.0
    )
    if response is not None:
        rec.update(
            selection_response_predicted_gap=round(
                response["predicted_gap"], 6
            ),
            mean_judge_selection_intensity=round(
                response["judge_selection_intensity"], 6
            ),
            selection_response_n_items=response["n_items"],
        )
    # `spread` remains the backwards-compatible public name. These explicit
    # fields make its estimator and the main alternatives auditable.
    for key, value in metrics.items():
        if key in ("n_items", "candidate_count_min", "candidate_count_max"):
            rec[key] = value
        elif value is not None:
            rec[key] = round(float(value), 6)
    if rec["util"] is not None:
        rec["util"] = round(rec["util"], 4)
    owners = [it.get("cand_owner") for it in items]
    if any(o for o in owners):
        ktot = kc = 0
        pool_total = pool_cogen = 0
        selfs, cogens = [], []
        self_groups, cogen_groups = [], []
        mix_parts = []
        for it in items:
            o = it.get("cand_owner")
            c = it.get(score_key)
            if not o or not c:
                continue
            selfs += [c[i] for i in range(len(c)) if o[i] == "self"]
            cogens += [c[i] for i in range(len(c)) if o[i] != "self"]
            pool_total += len(c)
            pool_cogen += sum(o[i] != "self" for i in range(len(c)))
            for i in it.get("kept_idx", []):
                ktot += 1
                kc += (o[i] != "self")
            si = [i for i in range(len(c)) if o[i] == "self"]
            ci = [i for i in range(len(c)) if o[i] != "self"]
            if si:
                self_groups.append([c[i] for i in si])
            if ci:
                cogen_groups.append([c[i] for i in ci])
            if si and ci:
                sv = np.asarray([c[i] for i in si], float)
                cv = np.asarray([c[i] for i in ci], float)
                ws = len(si) / len(c)
                wc = len(ci) / len(c)
                within = ws * float(np.var(sv)) + wc * float(np.var(cv))
                between = ws * wc * float((np.mean(sv) - np.mean(cv)) ** 2)
                total_sd = float(np.std(np.asarray(c, float)))
                # Law of total variance; keep the check close to extraction so
                # the downstream spread model cannot silently use a bad owner map.
                if abs(total_sd ** 2 - within - between) > 1e-8:
                    raise ValueError("candidate-owner variance decomposition failed")
                mix_parts.append((within, between, total_sd,
                                  float(np.std(sv)), float(np.std(cv))))
        rec["kept_cogen"] = round(kc / ktot, 3) if ktot else None
        rec["pool_cogen_fraction"] = round(pool_cogen / pool_total, 6) if pool_total else None
        if selfs and cogens:
            rec["self_mean"] = round(float(np.mean(selfs)), 4)
            rec["cogen_mean"] = round(float(np.mean(cogens)), 4)
            rec["source_sep"] = round(abs(rec["self_mean"] - rec["cogen_mean"]), 4)
        if mix_parts:
            rec["within_source_var"] = round(float(np.mean([x[0] for x in mix_parts])), 6)
            rec["between_source_var"] = round(float(np.mean([x[1] for x in mix_parts])), 6)
            rec["within_source_spread"] = round(
                float(np.mean([math.sqrt(max(0.0, x[0])) for x in mix_parts])), 6)
            rec["between_source_spread_increment"] = round(
                float(np.mean([x[2] - math.sqrt(max(0.0, x[0])) for x in mix_parts])), 6)
            rec["mixture_spread_reconstructed"] = round(
                float(np.mean([x[2] for x in mix_parts])), 6)
            rec["self_source_spread"] = round(float(np.mean([x[3] for x in mix_parts])), 6)
            rec["cogen_source_spread"] = round(float(np.mean([x[4] for x in mix_parts])), 6)
            total_variance = rec["within_source_var"] + rec["between_source_var"]
            rec["mixture_variance_reconstructed"] = round(total_variance, 6)
            if abs(rec["mean_item_variance"] - total_variance) > 2e-6:
                raise ValueError("round-level mixture variance reconstruction failed")
        for prefix, groups in (("self_source", self_groups), ("cogen_source", cogen_groups)):
            source_metrics = candidate_distribution_metrics(groups)
            if source_metrics:
                for key, value in source_metrics.items():
                    if key in ("n_items", "candidate_count_min", "candidate_count_max"):
                        rec[f"{prefix}_{key}"] = value
                    elif value is not None:
                        rec[f"{prefix}_{key}"] = round(float(value), 6)
    # Keep the selector's action inside the offered pool separate from the
    # displacement of the training targets relative to what the model itself
    # generated. They coincide in self-only pools and diverge under mixing.
    own_mean = rec.get("self_source_mean", rec["pool_mean"])
    rec["own_mean"] = round(own_mean, 4)
    rec["own_spread"] = rec.get("self_source_mean_item_sd", rec["spread"])
    rec["own_median_item_sd"] = rec.get(
        "self_source_median_item_sd", rec["median_item_sd"]
    )
    rec["own_mean_item_variance"] = rec.get(
        "self_source_mean_item_variance", rec["mean_item_variance"]
    )
    rec["own_rms_item_sd"] = rec.get("self_source_rms_item_sd", rec["rms_item_sd"])
    rec["own_pairwise_absolute_difference"] = rec.get(
        "self_source_mean_pairwise_absolute_difference",
        rec["mean_pairwise_absolute_difference"],
    )
    rec["own_mean_item_mean_absolute_deviation"] = rec.get(
        "self_source_mean_item_mean_absolute_deviation",
        rec["mean_item_mean_absolute_deviation"],
    )
    rec["own_mean_item_range"] = rec.get(
        "self_source_mean_item_range", rec["mean_item_range"]
    )
    rec["own_fraction_items_with_any_difference"] = rec.get(
        "self_source_fraction_items_with_any_difference",
        rec["fraction_items_with_any_difference"],
    )
    if "mean_item_binary_entropy_bits" in rec:
        rec["own_mean_item_binary_entropy_bits"] = rec.get(
            "self_source_mean_item_binary_entropy_bits",
            rec["mean_item_binary_entropy_bits"],
        )
    rec["own_between_item_mean_variance"] = rec.get(
        "self_source_between_item_mean_variance", rec["between_item_mean_variance"]
    )
    rec["own_hierarchical_total_sd"] = rec.get(
        "self_source_hierarchical_total_sd", rec["hierarchical_total_sd"]
    )
    rec["pool_supply_shift"] = round(rec["pool_mean"] - own_mean, 4)
    rec["self_relative_gap"] = round(rec["kept_mean"] - own_mean, 4)
    rec["generator_calibration_residual"] = round(own_mean - rec["value"], 4)
    reconstructed_pull = (
        rec["self_relative_gap"] + rec["generator_calibration_residual"]
    )
    if abs(rec["pull"] - reconstructed_pull) > 2e-4:
        raise ValueError("pull decomposition failed")
    reconstructed_self_gap = rec["gap"] + rec["pool_supply_shift"]
    if abs(rec["self_relative_gap"] - reconstructed_self_gap) > 2e-4:
        raise ValueError("self-relative gap decomposition failed")
    return rec


def generated_choice_measurement_se(order_read):
    """Conditional Monte Carlo SE of a generated-choice battery mean.

    Prompts and A/B orders are fixed.  Generation samples are random, so sum
    the estimated Bernoulli variances within each prompt/order group.  Jeffreys
    smoothing avoids declaring zero uncertainty when all four draws agree.
    """
    if not isinstance(order_read, dict):
        return None
    variance_sum = 0.0
    n_total = 0
    for item in order_read.get("raw", []):
        choices = [x for x in item.get("terminal_choices", []) if x in ("A", "B")]
        n = len(choices)
        if not n:
            continue
        gamble = item.get("gamble_letter")
        successes = sum(x == gamble for x in choices)
        p = (successes + 0.5) / (n + 1.0)
        variance_sum += n * p * (1.0 - p)
        n_total += n
    if not n_total:
        generated = order_read.get("generated", {})
        n_total = int(generated.get("n_valid") or 0)
        p = generated.get("overall")
        if not n_total or p is None:
            return None
        variance_sum = n_total * float(p) * (1.0 - float(p))
    return float(np.sqrt(variance_sum) / n_total)


def generated_choice_measurement_n(order_read):
    if not isinstance(order_read, dict):
        return None
    generated = order_read.get("generated", {})
    n = generated.get("n_total") or generated.get("n_valid")
    return int(n) if n else None


def freegen_measurement_se(block):
    """Conditional generation SE for the fixed self-report prompt battery."""
    if not isinstance(block, dict):
        return None
    items = block.get("items", [])
    if not items:
        return None
    # The reported score weights every retained sample equally.
    groups = [np.asarray(it.get("sr_scores", []), float) for it in items]
    groups = [x for x in groups if len(x)]
    n_total = sum(len(x) for x in groups)
    if not n_total:
        return None
    variance_sum = 0.0
    for x in groups:
        # ddof=1 estimates fresh-generation variance; with one sample there is
        # no within-group estimate, so contribute zero rather than inventing it.
        if len(x) > 1:
            variance_sum += len(x) * float(np.var(x, ddof=1))
    return float(np.sqrt(variance_sum) / n_total)


def freegen_measurement_n(block):
    if not isinstance(block, dict):
        return None
    n = sum(len(it.get("sr_scores", [])) for it in block.get("items", []))
    return int(n) if n else None


# ---------------------------------------------------------------- sources
# label maps: cond -> (judge, format, composition)
SELF_ONLY, BASE_MIX, PEER_MIX = "self-only", "base-mixed", "peer-mixed"
KAGGLE_CONDS = {
    "evolving_self":  ("self",         "reference", SELF_ONLY),
    "frozen_copy_r0": ("frozen copy",  "reference", SELF_ONLY),
    "frozen_cons_r0": ("cautious copy", "reference", SELF_ONLY),
    "frozen_base":    ("base",         "reference", SELF_ONLY),
    "random_select":  ("random",       "random",    SELF_ONLY),
    "oracle_hold":    ("score oracle", "score",     SELF_ONLY),
}
MODAL_CONDS = {
    "base_hold":       ("base",          "reference", SELF_ONLY),
    "oracle_hold":     ("score oracle",  "score",     SELF_ONLY),
    "press_d1":        ("schedule",      "reference", SELF_ONLY),
    "press_d2":        ("schedule",      "reference", SELF_ONLY),
    "press_d3":        ("schedule",      "reference", SELF_ONLY),
    "press_to_base":   ("schedule",      "reference", SELF_ONLY),
    "oracle_mix":      ("score oracle",  "score",     BASE_MIX),
    "cons_mix":        ("cautious copy", "reference", BASE_MIX),
    "invade_base":     ("base",          "reference", PEER_MIX),
    "invade_self":     ("self",          "reference", PEER_MIX),
    "h2h_cons_rescue": ("cautious copy", "duel",      BASE_MIX),
    "h2h_base_rescue": ("base",          "duel",      BASE_MIX),
    "h2h_erode_base":  ("base",          "duel",      BASE_MIX),
    "h2h_erode_self":  ("self",          "duel",      BASE_MIX),
    "h2h_invade_base": ("base",          "duel",      PEER_MIX),
    "h2h_invade_self": ("self",          "duel",      PEER_MIX),
}
KAGGLE_SOURCES = [
    ("experiments/kaggle/kaggle_k1_qwen_anchor_grid/output/k1_qwen_anchor.json", "Qwen", "risk"),
    ("experiments/kaggle/kaggle_k2_olmo_inversion_conf/output/k2_olmo_inversion_kaggle_conf_v2.json", "OLMo", "risk"),
    ("experiments/kaggle/kaggle_k2_olmo_inversion_conf/output/k2_conf_v1_seeds12_partial.json", "OLMo", "risk"),
    ("experiments/kaggle/kaggle_k2_olmo_inversion_base012/output/k2_olmo_inversion_kaggle_base012.json", "OLMo", "risk"),
    # K3 em-neutral grid EXCLUDED: its pool logs score a different axis
    # (cand_candor) and its battery has no sr_free_gen trajectory, so neither
    # the measured value nor the candidate scores line up with the sr axis.
]
# cells-style Qwen selfaware files: (path, judge, format, composition)
CELLS_SOURCES = [
    ("experiments/em_selfaware_loop/output/selfaware_loop_grid.json",
     "self", "candid-prompt", SELF_ONLY),
    ("experiments/em_selfaware_loop/output/judge_opposition_oracle.json",
     "score oracle", "score", SELF_ONLY),
    ("experiments/em_selfaware_loop/output/judge_opposition_oracle_seed707.json",
     "score oracle", "score", SELF_ONLY),
    ("experiments/em_selfaware_loop/output/judge_opposition_natural_base.json",
     "base", "reference", SELF_ONLY),
    ("experiments/em_selfaware_loop/output/mixed_reopen_qwen.json",
     "score oracle", "score", BASE_MIX),
    ("experiments/em_selfaware_loop/output/mixed_reopen_twin_selfonly.json",
     "score oracle", "score", SELF_ONLY),
    ("experiments/em_selfaware_loop/output/head2head_selfjudge.json",
     "self", "duel", BASE_MIX),
]


def kaggle_records():
    best = {}
    for path, organism, axis in KAGGLE_SOURCES:
        f = os.path.join(ROOT, path)
        if not os.path.exists(f):
            continue
        d = json.load(open(f))
        score_key = "cand_risk" if axis == "risk" else "cand_sr_scores"
        for sd, conds in d.items():
            if not str(sd).isdigit():
                continue
            for cond, res in conds.items():
                if cond not in KAGGLE_CONDS or not isinstance(res, dict):
                    continue
                rr = res.get("rounds_raw")
                if not rr:
                    continue
                traj = res.get("traj")
                if not traj:
                    continue
                key = (organism, axis, cond, str(sd))
                if key not in best or len(rr) > best[key][0]:
                    best[key] = (len(rr), path, res, traj, score_key)
    out = []
    for (organism, axis, cond, sd), (_, path, res, traj, score_key) in best.items():
        judge, fmt, comp = KAGGLE_CONDS[cond]
        rr = res["rounds_raw"]
        order_reads = res.get("traj_order", [])
        for k in range(1, len(rr) + 1):
            if k >= len(traj) or traj[k] is None or traj[k - 1] is None:
                continue
            if not rr[k - 1]:
                continue
            rec = round_record(rr[k - 1], score_key, traj[k - 1], traj[k],
                               judge_key="scores_arm",
                               oracle_sign=(-1 if judge == "score oracle" else None))
            if rec:
                if k < len(order_reads):
                    rec["value_measurement_se"] = generated_choice_measurement_se(
                        order_reads[k - 1]
                    )
                    rec["next_value_measurement_se"] = generated_choice_measurement_se(
                        order_reads[k]
                    )
                    rec["value_measurement_n"] = generated_choice_measurement_n(
                        order_reads[k - 1]
                    )
                    rec["next_value_measurement_n"] = generated_choice_measurement_n(
                        order_reads[k]
                    )
                rec.update(organism=organism, axis=axis, cond=cond, seed=sd,
                           round=k, judge=judge, format=fmt, composition=comp,
                           source=os.path.basename(path))
                out.append(rec)
    return out


def modal_records():
    import glob
    out = []
    for f in sorted(glob.glob(os.path.join(ROOT, "experiments/modal_k2_release/output/k2rel_*.json"))):
        d = json.load(open(f))
        for sd, conds in d.items():
            if not str(sd).isdigit():
                continue
            for cond, res in conds.items():
                if cond not in MODAL_CONDS or not isinstance(res, dict):
                    continue
                rr, traj = res.get("rounds_raw"), res.get("traj")
                if not rr or not traj:
                    continue
                judge, fmt, comp = MODAL_CONDS[cond]
                jkey = "scores_h2h" if cond.startswith("h2h_") else "scores_arm"
                order_reads = res.get("traj_order", [])
                for k in range(1, min(len(rr), len(traj) - 1) + 1):
                    if not rr[k - 1]:
                        continue
                    rec = round_record(rr[k - 1], "cand_risk", traj[k - 1], traj[k],
                                       judge_key=jkey,
                                       oracle_sign=(-1 if judge == "score oracle" else None))
                    if rec:
                        if k < len(order_reads):
                            rec["value_measurement_se"] = generated_choice_measurement_se(
                                order_reads[k - 1]
                            )
                            rec["next_value_measurement_se"] = generated_choice_measurement_se(
                                order_reads[k]
                            )
                            rec["value_measurement_n"] = generated_choice_measurement_n(
                                order_reads[k - 1]
                            )
                            rec["next_value_measurement_n"] = generated_choice_measurement_n(
                                order_reads[k]
                            )
                        rec.update(organism="OLMo", axis="risk", cond=cond,
                                   seed=str(sd), round=k, judge=judge,
                                   format=fmt, composition=comp,
                                   source=os.path.basename(f))
                        out.append(rec)
    return out


def cells_records():
    out = []
    for path, judge, fmt, comp in CELLS_SOURCES:
        f = os.path.join(ROOT, path)
        if not os.path.exists(f):
            continue
        d = json.load(open(f))
        baselines = d.get("baselines", {})
        for cell_id, c in d.get("cells", {}).items():
            rr, bat = c.get("rounds_raw"), c.get("battery")
            if not rr or not bat:
                continue
            dose = c.get("dose") or cell_id.split(":")[0]
            v0 = None
            b0 = baselines.get(dose)
            if b0:
                v0 = b0["battery"]["sr_free_gen"]["sr_freegen"]
            traj = [v0] + [b["sr_free_gen"]["sr_freegen"] for b in bat]
            measurement_blocks = (
                [b0["battery"]["sr_free_gen"] if b0 else None]
                + [b["sr_free_gen"] for b in bat]
            )
            for k in range(1, min(len(rr), len(traj) - 1) + 1):
                if traj[k] is None or traj[k - 1] is None or not rr[k - 1]:
                    continue
                rec = round_record(rr[k - 1], "cand_sr_scores", traj[k - 1], traj[k],
                                   judge_key="scores",
                                   oracle_sign=(-1 if judge == "score oracle" else None))
                if rec:
                    rec["value_measurement_se"] = freegen_measurement_se(
                        measurement_blocks[k - 1]
                    )
                    rec["next_value_measurement_se"] = freegen_measurement_se(
                        measurement_blocks[k]
                    )
                    rec["value_measurement_n"] = freegen_measurement_n(
                        measurement_blocks[k - 1]
                    )
                    rec["next_value_measurement_n"] = freegen_measurement_n(
                        measurement_blocks[k]
                    )
                    rec.update(organism="Qwen", axis="selfreport", cond=os.path.basename(path).replace(".json", ""),
                               seed=str(c.get("seed", cell_id)), round=k, judge=judge,
                               format=fmt, composition=comp, source=os.path.basename(path))
                    out.append(rec)
    return out


# ---------------------------------------------------------------- fits
def ols(x, y):
    x, y = np.asarray(x, float), np.asarray(y, float)
    if len(x) < 3 or np.std(x) < 1e-9:
        return None
    b, a = np.polyfit(x, y, 1)
    r = float(np.corrcoef(x, y)[0, 1])
    return dict(slope=round(float(b), 3), intercept=round(float(a), 3),
                r=round(r, 3), n=int(len(x)))


def subset(records, **kw):
    return [r for r in records if all(r.get(k) == v for k, v in kw.items())]


def movement_fits(records):
    fits = {}
    groups = {"pooled": records,
              "OLMo/risk": subset(records, organism="OLMo"),
              "Qwen/risk": [r for r in records if r["organism"] == "Qwen" and r["axis"] == "risk"],
              "Qwen/selfreport": subset(records, organism="Qwen", axis="selfreport")}
    for comp in (SELF_ONLY, BASE_MIX, PEER_MIX):
        groups[f"composition:{comp}"] = [r for r in records if r["composition"] == comp]
    for name, rs in groups.items():
        rs = [r for r in rs if r.get("pull") is not None]
        if len(rs) < 3:
            continue
        fits[name] = dict(
            n=len(rs),
            drift_vs_pull=ols([r["pull"] for r in rs], [r["drift"] for r in rs]),
            drift_vs_gap=ols([r["gap"] for r in rs], [r["drift"] for r in rs]),
            drift_vs_self_relative_gap=ols(
                [r["self_relative_gap"] for r in rs],
                [r["drift"] for r in rs],
            ),
        )
    return fits


def factorization_fits(records):
    """Signed gap ~ rho*sigma (the order-statistics factorization of
    report_taste_alignment_predictor.md, extended beyond own-pool cells)."""
    out = {}
    groups = {"pooled": records,
              "composition:self-only": [r for r in records if r["composition"] == SELF_ONLY],
              "composition:base-mixed": [r for r in records if r["composition"] == BASE_MIX],
              "composition:peer-mixed": [r for r in records if r["composition"] == PEER_MIX]}
    for name, rs in groups.items():
        rs = [r for r in rs if r.get("rho") is not None]
        if len(rs) < 5:
            continue
        gap = [r["gap"] for r in rs]
        prod = [r["rho"] * r["spread"] for r in rs]
        fit = ols(prod, gap)
        f_s = ols([r["spread"] for r in rs], gap)
        f_r = ols([r["rho"] for r in rs], gap)
        out[name] = dict(n=len(rs), gap_vs_rho_sigma=fit,
                         r2_spread_alone=(round(f_s["r"] ** 2, 3) if f_s else None),
                         r2_rho_alone=(round(f_r["r"] ** 2, 3) if f_r else None),
                         r2_product=(round(fit["r"] ** 2, 3) if fit else None))
    return out


def spread_ledger(records):
    led = {}
    for fam in ("OLMo", "Qwen"):
        for comp in (SELF_ONLY, BASE_MIX, PEER_MIX):
            rs = [r for r in records if r["organism"] == fam and r["composition"] == comp]
            if not rs:
                continue
            by_round = defaultdict(list)
            for r in rs:
                by_round[r["round"]].append(r["spread"])
            # sigma_{t+1} ~ sigma_t within the same run
            runs = defaultdict(dict)
            for r in rs:
                runs[(r["cond"], r["seed"], r["source"])][r["round"]] = r["spread"]
            xs, ys = [], []
            for rounds in runs.values():
                for k in rounds:
                    if k + 1 in rounds:
                        xs.append(rounds[k]); ys.append(rounds[k + 1])
            led[f"{fam}/{comp}"] = dict(
                n_rounds=len(rs),
                mean_spread_by_round={k: round(float(np.mean(v)), 4)
                                      for k, v in sorted(by_round.items())},
                persistence=ols(xs, ys),
            )
    # the matched pair, spelled out
    pair = {}
    for tag, cond in (("reopen(base-mixed)", "mixed_reopen_qwen"),
                      ("twin(self-only)", "mixed_reopen_twin_selfonly")):
        rs = subset(records, cond=cond)
        if rs:
            pair[tag] = dict(
                spread_by_round={r["round"]: r["spread"] for r in sorted(rs, key=lambda x: (x["seed"], x["round"])) if r["seed"] == rs[0]["seed"]},
                mean_spread=round(float(np.mean([r["spread"] for r in rs])), 4),
                mean_abs_drift=round(float(np.mean([abs(r["drift"]) for r in rs])), 4),
            )
    led["matched_pair_qwen_reopen_vs_twin"] = pair
    # in mixed pools, is the spread just the source separation?
    mixed = [r for r in records if r["composition"] != SELF_ONLY and r.get("source_sep") is not None]
    if len(mixed) >= 5:
        led["mixed_spread_vs_source_separation"] = ols(
            [r["source_sep"] for r in mixed], [r["spread"] for r in mixed])
    return led


def util_ledger(records):
    cells = defaultdict(list)
    for r in records:
        if r.get("util") is None or r["judge"] == "schedule":
            continue
        cells[(r["organism"], r["axis"], r["judge"], r["format"], r["composition"])].append(r)
    table = []
    for (org, axis, judge, fmt, comp), rs in sorted(cells.items()):
        rhos = [r["rho"] for r in rs if r.get("rho") is not None]
        table.append(dict(organism=org, axis=axis, judge=judge, format=fmt,
                          composition=comp, n_rounds=len(rs),
                          util_mean=round(float(np.mean([r["util"] for r in rs])), 3),
                          util_sd=round(float(np.std([r["util"] for r in rs])), 3),
                          rho_mean=(round(float(np.mean(rhos)), 3) if rhos else None),
                          gap_mean=round(float(np.mean([r["gap"] for r in rs])), 3),
                          kept_cogen_mean=(round(float(np.mean([r["kept_cogen"] for r in rs if r.get("kept_cogen") is not None])), 3)
                                           if any(r.get("kept_cogen") is not None for r in rs) else None)))
    # variance split: between-cell vs within-cell (rounds)
    def var_share(key):
        vals = {k: [r[key] for r in rs if r.get(key) is not None] for k, rs in cells.items()}
        vals = {k: v for k, v in vals.items() if v}
        allv = [u for v in vals.values() for u in v]
        if not allv:
            return None
        grand = np.mean(allv)
        between = sum(len(v) * (np.mean(v) - grand) ** 2 for v in vals.values())
        total = sum((u - grand) ** 2 for u in allv)
        return round(float(between / total), 3) if total else None
    return dict(table=table,
                between_cell_variance_share_util=var_share("util"),
                between_cell_variance_share_rho=var_share("rho"))


def main():
    records = kaggle_records() + modal_records() + cells_records()
    out = dict(
        description=__doc__.strip().split("\n")[0],
        n_records=len(records),
        n_runs=len({(r["cond"], r["seed"], r["source"]) for r in records}),
        movement_law=movement_fits(records),
        factorization=factorization_fits(records),
        spread_ledger=spread_ledger(records),
        utilization=util_ledger(records),
        records=records,
    )
    path = os.path.join(ROOT, "experiments/spread_util_unified.json")
    with open(path, "w") as f:
        json.dump(out, f, indent=1)
    print(f"{len(records)} records / {out['n_runs']} runs -> {path}")
    print(json.dumps(out["movement_law"], indent=1)[:1500])
    print("factorization:", out["factorization"])
    print("variance shares:", out["utilization"]["between_cell_variance_share_util"], out["utilization"]["between_cell_variance_share_rho"])


if __name__ == "__main__":
    main()
