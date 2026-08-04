"""Does the candidate covariance predict off-target selection differentials?

Phase 1b answered this once, at slope 0.855 and correlation 0.852 over 30
predicted-versus-observed pairs -- but its own output carries the caveat that
matters: the 30 pairs cluster into only **6 selection events**, one per selected
axis, so the effective sample size for the slope is 6, not 30. A slope estimated
on six clusters with no interval is not yet a result.

This raises the effective n without any new compute, by blocking on prompts.
The 30 prompts are split into disjoint blocks; within each block the whole
prediction is redone from scratch. A block is an independent draw of prompts, so
(block, selected axis) is a genuine selection event, and the count goes from 6 to
blocks x 6 with a cluster bootstrap over blocks.

THE PREDICTION BEING TESTED. Selecting the top-K candidates on axis a moves axis
b too, purely because candidate scores on a and b are correlated within a prompt.
Multivariate selection theory makes that quantitative: writing P for the
within-prompt covariance of candidate scores and S for the vector of selection
differentials,

    S_b  =  (P_ab / P_aa) * S_a

so the off-target differential is predictable from a pure inference pass over the
candidate pool, before any training. Anything the training step adds on top of
this is the Price equation's transmission term, which this does not measure.

WHAT MAKES THIS A REAL TEST RATHER THAN AN IDENTITY. Three separations, all of
which the phase-1b script already built and which are preserved here:

  cross-pool     P is estimated on pool A; the selection and the observed
                 differential happen on pool B. A shared pool would make the
                 prediction partly definitional.
  cross-method   P and the selection use judge A's scores; the OBSERVED
                 off-target differential is measured with judge B. So a shared
                 judge error cannot inflate the agreement.
  off-diagonal   only b != a pairs are scored. The on-axis differential is the
                 input, not a prediction.

Writes experiments/offtarget_prediction_blocked.json.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / ("experiments/value_covariance/output_1b_granite/"
              "value_covariance_phase1b.json")
OUT = ROOT / "experiments/offtarget_prediction_blocked.json"

N_BLOCKS = 5
BOOTSTRAP_DRAWS = 4000
SEED = 20260804


def within_prompt_cov(scores):
    """Mean within-prompt covariance of candidate scores. scores: (P, C, A)."""
    centred = scores - scores.mean(axis=1, keepdims=True)
    n_prompts, n_cand, n_ax = scores.shape
    acc = np.zeros((n_ax, n_ax))
    for p in range(n_prompts):
        acc += centred[p].T @ centred[p] / (n_cand - 1)
    return acc / n_prompts


def differentials(scores, keep_idx):
    """Kept-mean minus pool-mean per axis, averaged over prompts."""
    out = []
    for p, idx in enumerate(keep_idx):
        out.append(scores[p][idx].mean(axis=0) - scores[p].mean(axis=0))
    return np.mean(out, axis=0)


def select_top_k(scores_for_selection, axis, keep):
    """Indices of the top-`keep` candidates on `axis`, per prompt."""
    return [np.argsort(-scores_for_selection[p][:, axis])[:keep]
            for p in range(scores_for_selection.shape[0])]


def block_pairs(sa_A, sa_B, sb_B, keep, axes):
    """One block's predicted/observed off-target pairs.

    sa_A  judge A on pool A  -> the covariance P
    sa_B  judge A on pool B  -> the selection, and the on-axis differential
    sb_B  judge B on pool B  -> the OBSERVED off-target differential
    """
    P = within_prompt_cov(sa_A)
    rows = []
    for a, sel_axis in enumerate(axes):
        if P[a, a] <= 1e-12:
            continue
        idx = select_top_k(sa_B, a, keep)
        S_a = differentials(sa_B, idx)[a]
        obs_vec = differentials(sb_B, idx)
        for b, off_axis in enumerate(axes):
            if b == a:
                continue
            rows.append({
                "selected_axis": sel_axis,
                "offtarget_axis": off_axis,
                "predicted": float(P[a, b] / P[a, a] * S_a),
                "observed": float(obs_vec[b]),
                "on_axis_differential": float(S_a),
            })
    return rows


def fit(rows):
    if len(rows) < 4:
        return None
    x = np.array([r["predicted"] for r in rows])
    y = np.array([r["observed"] for r in rows])
    if np.var(x) < 1e-16:
        return None
    A = np.column_stack([np.ones(len(x)), x])
    beta, *_ = np.linalg.lstsq(A, y, rcond=None)
    r = float(np.corrcoef(x, y)[0, 1]) if np.var(y) > 1e-16 else None
    return {
        "slope": float(beta[1]),
        "intercept": float(beta[0]),
        "correlation": r,
        "mae": float(np.mean(np.abs(y - x))),
        "sign_agreement": float(np.mean(np.sign(x) == np.sign(y))),
        "n_pairs": len(rows),
    }


def cluster_bootstrap(rows, cluster_key, draws=BOOTSTRAP_DRAWS, seed=SEED):
    """Resample whole selection events, which is the real unit."""
    groups = {}
    for r in rows:
        groups.setdefault(cluster_key(r), []).append(r)
    keys = sorted(groups)
    if len(keys) < 4:
        return None
    rng = np.random.default_rng(seed)
    keep = {"slope": [], "correlation": [], "sign_agreement": []}
    for _ in range(draws):
        sample = []
        for i in rng.integers(0, len(keys), size=len(keys)):
            sample.extend(groups[keys[i]])
        f = fit(sample)
        if not f:
            continue
        for k in keep:
            v = f.get(k)
            if v is not None and np.isfinite(v):
                keep[k].append(v)
    out = {}
    for k, vals in keep.items():
        if len(vals) < 100:
            continue
        arr = np.array(vals)
        out[k] = {"ci_lo": float(np.percentile(arr, 2.5)),
                  "ci_hi": float(np.percentile(arr, 97.5)),
                  "se": float(arr.std(ddof=1))}
    out["n_clusters"] = len(keys)
    return out


def main():
    d = json.loads(SRC.read_text())
    axes = d["config"]["axes"]
    keep = int(d["config"]["keep"])
    rs = d["raw_scores"]
    sa_A = np.array(rs["judge_a"]["A"], dtype=float)
    sa_B = np.array(rs["judge_a"]["B"], dtype=float)
    sb_B = np.array(rs["judge_b"]["B"], dtype=float)

    n_prompts = sa_A.shape[0]
    order = np.arange(n_prompts)
    blocks = np.array_split(order, N_BLOCKS)

    all_rows = []
    for bi, idx in enumerate(blocks):
        rows = block_pairs(sa_A[idx], sa_B[idx], sb_B[idx], keep, axes)
        for r in rows:
            r["block"] = int(bi)
        all_rows.extend(rows)

    pooled = fit(all_rows)
    boot = cluster_bootstrap(all_rows,
                             lambda r: (r["block"], r["selected_axis"]))
    # the unblocked comparison, i.e. what phase 1b itself reported
    whole = block_pairs(sa_A, sa_B, sb_B, keep, axes)
    whole_fit = fit(whole)

    per_selected = {}
    for a in axes:
        sub = [r for r in all_rows if r["selected_axis"] == a]
        f = fit(sub)
        if f:
            per_selected[a] = f

    payload = {
        "description": (
            "Blocked re-test of the multivariate-selection prediction "
            "S_b = (P_ab/P_aa) * S_a, raising the effective sample size from 6 "
            "selection events to blocks x axes, with a cluster bootstrap over "
            "selection events. Cross-pool and cross-method throughout."
        ),
        "source": str(SRC.relative_to(ROOT)),
        "n_blocks": N_BLOCKS,
        "prompts_per_block": [int(len(b)) for b in blocks],
        "keep": keep,
        "axes": axes,
        "whole_sample_fit_as_phase1b_reported_it": whole_fit,
        "blocked_fit": pooled,
        "blocked_bootstrap_over_selection_events": boot,
        "per_selected_axis": per_selected,
        "separations_preserved": {
            "cross_pool": "covariance from pool A; selection and outcome on pool B",
            "cross_method": "covariance and selection from judge A; observed "
                            "differential from judge B",
            "off_diagonal_only": "b != a; the on-axis differential is the input",
        },
    }
    OUT.write_text(json.dumps(payload, indent=2) + "\n")

    print(f"whole sample (as phase 1b reported): "
          f"slope {whole_fit['slope']:.3f}  r {whole_fit['correlation']:.3f}  "
          f"MAE {whole_fit['mae']:.4f}  sign {whole_fit['sign_agreement']:.2f}  "
          f"pairs {whole_fit['n_pairs']} in 6 selection events")
    print()
    print(f"blocked into {N_BLOCKS} prompt blocks "
          f"({payload['prompts_per_block']} prompts each):")
    print(f"  slope {pooled['slope']:.3f}  r {pooled['correlation']:.3f}  "
          f"MAE {pooled['mae']:.4f}  sign {pooled['sign_agreement']:.2f}  "
          f"pairs {pooled['n_pairs']}")
    if boot:
        print(f"  clusters (selection events): {boot['n_clusters']}")
        for k in ("slope", "correlation", "sign_agreement"):
            if k in boot:
                print(f"    {k:16s} 95% CI [{boot[k]['ci_lo']:+.3f}, "
                      f"{boot[k]['ci_hi']:+.3f}]")
    print()
    print("by selected axis:")
    for a, f in per_selected.items():
        print(f"  {a:22s} slope {f['slope']:+.3f}  r "
              + (f"{f['correlation']:+.3f}" if f['correlation'] is not None else "  n/a")
              + f"  sign {f['sign_agreement']:.2f}  (n={f['n_pairs']})")
    print(f"\nwrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
