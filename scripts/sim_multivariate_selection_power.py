"""Design simulation: can we measure the value covariance of a model's own candidates?

WHY THIS EXISTS.  The program has measured a correlated response -- when a
selection loop pushed OLMo's gamble preference, its belief bias about gamble
expected values moved with it at correlation 0.79 (report_ev_bias_coupling.md).
What it has never measured is the quantity that would PREDICT that number: the
covariance, across the model's own candidate answers, between the axis being
selected on and the axis that moved.  Every value score in the repo is measured
once per round on the model, never per candidate on more than one axis.

If we do measure it, multivariate selection theory makes a sharp, falsifiable
split.  Writing S for the vector of selection differentials (kept mean minus pool
mean, per axis) and P for the within-prompt covariance of candidate scores, pure
selection on axis a predicts the differential on any other axis b:

    S_b  =  (P_ab / P_aa) * S_a

and the trained response follows S through the transmission coefficient the
program already estimates (~0.83).  So:

  - If the observed off-target movement matches this, the spillover is
    SELECTION-MEDIATED: the judge kept answers that happened to be high on b too,
    and it is predictable from a pure inference pass before any training.
  - If off-target movement EXCEEDS it, there is coupling the candidate pool does
    not contain -- the fine-tune itself is entangling the axes.

That is a clean decomposition of off-target value drift, and the first half is
cheap.  But it depends entirely on being able to estimate P from a realistic
number of prompts and candidates.  This script asks whether that is feasible
BEFORE any GPU time is spent, which is the project's pilot-before-spend rule.

WHAT IS SIMULATED.  Candidates for a prompt are drawn from a multivariate normal
around that prompt's own mean, so the estimator must pool WITHIN-prompt
covariances (between-prompt variation is a nuisance term here, exactly as in the
real measurement).  Scores are then observed through one of four instruments,
chosen to separate the cost of the SCORE FORMAT from the cost of JUDGE
STOCHASTICITY, because those have different fixes:

    graded        - the latent value plus measurement noise, on a 0-1 scale
    coarse        - the latent value rounded to a 5-point rubric
    threshold     - a deterministic yes/no judge (binary format, no sampling noise)
    binary        - a yes/no judge that SAMPLES its answer at probability equal to
                    the latent value; this is what every axis in the repo uses

The binary arms matter because the 2026-07-24 result (spread is pinned by the pool
mean on binary axes) means binary scoring destroys exactly the second-moment
information this experiment needs.  This quantifies that cost in design units.

Outputs a JSON grid to experiments/multivariate_selection_power.json and prints
the recommended design.
"""

import json
import itertools
import math
import numpy as np

OUT = "experiments/multivariate_selection_power.json"
RNG = np.random.default_rng(20260724)

# The truth we are trying to recover: a moderate correlation between the selected
# axis and one off-target axis. 0.35 is deliberately modest -- if the design can
# only see 0.8 correlations it is useless for the question.
TRUE_R = 0.35


def make_pool(n_prompts, n_cand, true_r, k=2, spread=0.22, between=0.15):
    """Latent candidate values: prompt effects plus within-prompt covariance."""
    cov = np.array([[1.0, true_r], [true_r, 1.0]]) * spread ** 2
    prompt_means = RNG.normal(0.5, between, size=(n_prompts, k))
    draws = RNG.multivariate_normal(np.zeros(k), cov, size=(n_prompts, n_cand))
    return np.clip(prompt_means[:, None, :] + draws, 0.0, 1.0)


def observe(latent, regime, meas_noise=0.06):
    """Apply the scoring instrument."""
    if regime == "graded":
        return np.clip(latent + RNG.normal(0, meas_noise, latent.shape), 0, 1)
    if regime == "coarse":
        noisy = np.clip(latent + RNG.normal(0, meas_noise, latent.shape), 0, 1)
        return np.round(noisy * 4) / 4.0
    if regime == "binary":
        # A judge SAMPLING a yes/no answer, with probability of "yes" equal to the
        # latent value. The sampling noise is independent across axes, so it is
        # pure attenuation. This is what a temperature-1 yes/no judge does.
        return (RNG.random(latent.shape) < latent).astype(float)
    if regime == "threshold":
        # A DETERMINISTIC yes/no judge: same binary output format, but no sampling
        # noise. Separates the cost of binarity itself from the cost of judge
        # stochasticity -- these have very different fixes.
        noisy = np.clip(latent + RNG.normal(0, meas_noise, latent.shape), 0, 1)
        return (noisy > 0.5).astype(float)
    raise ValueError(regime)


def within_prompt_corr(scores):
    """Pool within-prompt covariances across prompts, then correlate."""
    centered = scores - scores.mean(axis=1, keepdims=True)
    flat = centered.reshape(-1, scores.shape[2])
    n_p, n_c = scores.shape[0], scores.shape[1]
    dof = max(1, n_p * (n_c - 1))
    cov = flat.T @ flat / dof
    d = np.sqrt(np.diag(cov))
    if d[0] <= 0 or d[1] <= 0:
        return np.nan, cov
    return cov[0, 1] / (d[0] * d[1]), cov


def selection_experiment(n_prompts, n_cand, regime, keep, rho, true_r, reps=400):
    """Estimate the off-diagonal correlation and the predicted correlated response."""
    r_hats, pred_err = [], []
    for _ in range(reps):
        latent = make_pool(n_prompts, n_cand, true_r)
        scores = observe(latent, regime)
        r_hat, cov = within_prompt_corr(scores)
        if not np.isfinite(r_hat):
            continue
        r_hats.append(r_hat)

        # Judge selects on axis 0 with imperfect agreement rho.
        judge = scores[:, :, 0] * rho + RNG.normal(0, 1, scores.shape[:2]) * (1 - rho)
        idx = np.argsort(-judge, axis=1)[:, :keep]
        kept = np.take_along_axis(scores, idx[:, :, None], axis=1)
        S = kept.mean(axis=1).mean(axis=0) - scores.mean(axis=1).mean(axis=0)

        # Predicted off-target differential from the ESTIMATED covariance.
        if cov[0, 0] > 1e-9 and abs(S[0]) > 1e-9:
            predicted_S1 = (cov[0, 1] / cov[0, 0]) * S[0]
            pred_err.append(predicted_S1 - S[1])
    if not r_hats:
        return None
    r_hats = np.array(r_hats)
    return {
        "n_prompts": n_prompts, "n_cand": n_cand, "regime": regime,
        "keep": keep, "rho": rho,
        "r_mean": round(float(r_hats.mean()), 4),
        "r_sd": round(float(r_hats.std()), 4),
        "r_bias": round(float(r_hats.mean() - true_r), 4),
        # Can we tell TRUE_R apart from zero? Two-sided, using the sampling SD.
        "detect_rate_vs_zero": round(float((np.abs(r_hats) > 2 * r_hats.std()).mean()), 3),
        "pred_S_mae": round(float(np.abs(pred_err).mean()), 5) if pred_err else None,
    }


def truncation_robustness(reps=3000):
    """Does S_b = (P_ab/P_aa)*S_a survive TOP-K TRUNCATION and non-normal pools?

    The correlated-response relation is derived for linear selection. Real
    selection here is truncation: keep the top k candidates by axis a. It is also
    derived under multivariate normality, which candidate pools will not obey.
    Both are assumptions the whole experiment rests on, so they get tested rather
    than asserted.

    The non-normal arm builds skewed Beta(2,5) marginals with a prescribed rank
    correlation through a Gaussian copula, so the correlation is controlled while
    the shape is badly non-normal.
    """
    rows = []
    # Beta(2,5) inverse CDF, computed once. Recomputing it per replicate was the
    # bottleneck and it is constant.
    grid_u = np.linspace(0.001, 0.999, 999)
    grid_x = np.quantile(RNG.beta(2, 5, 200000), grid_u)
    for dist in ("normal", "beta_skewed"):
        for true_r in (0.0, 0.35, 0.7):
            for keep, n in ((1, 6), (2, 6), (4, 12)):
                obs, pred = [], []
                for _ in range(reps):
                    if dist == "normal":
                        cov = np.array([[1.0, true_r], [true_r, 1.0]]) * 0.22 ** 2
                        pool = RNG.multivariate_normal([0.5, 0.5], cov, size=n)
                    else:
                        g = RNG.multivariate_normal(
                            [0, 0], [[1.0, true_r], [true_r, 1.0]], size=n)
                        u = 0.5 * (1 + np.vectorize(math.erf)(g / np.sqrt(2)))
                        pool = np.stack([np.interp(u[:, k], grid_u, grid_x)
                                         for k in range(2)], axis=1)
                    idx = np.argsort(-pool[:, 0])[:keep]
                    S = pool[idx].mean(0) - pool.mean(0)
                    P = np.cov(pool.T, ddof=0)
                    if P[0, 0] > 1e-12:
                        pred.append(P[0, 1] / P[0, 0] * S[0])
                        obs.append(S[1])
                o, p = float(np.mean(obs)), float(np.mean(pred))
                rows.append({
                    "distribution": dist, "true_r": true_r, "keep": keep, "n_cand": n,
                    "observed_S_b": round(o, 5), "predicted_S_b": round(p, 5),
                    "relative_error": round(abs(p - o) / abs(o), 4) if abs(o) > 1e-3 else None,
                })
    return rows


def main():
    grid = []
    for n_prompts, n_cand, regime in itertools.product(
            [30, 60, 120], [6, 12, 24], ["graded", "coarse", "threshold", "binary"]):
        res = selection_experiment(n_prompts, n_cand, regime, keep=max(2, n_cand // 3),
                                   rho=0.7, true_r=TRUE_R)
        if res:
            grid.append(res)

    out = {
        "description": "Design power simulation for measuring the within-prompt "
                       "value covariance of a model's own candidate answers, which "
                       "is what predicts selection-mediated off-target value drift.",
        "true_correlation_simulated": TRUE_R,
        "notes": "r_sd is the sampling SD of the estimated off-diagonal correlation. "
                 "detect_rate_vs_zero is the fraction of replicates whose estimate "
                 "exceeds two of its own sampling SDs. pred_S_mae is the error in "
                 "predicting the off-target selection differential from the "
                 "estimated covariance, in value-score units.",
        "grid": grid,
        "truncation_and_nonnormality_robustness": truncation_robustness(),
    }
    with open(OUT, "w") as f:
        json.dump(out, f, indent=1)

    print(f"true within-prompt correlation = {TRUE_R}\n")
    hdr = f"{'regime':8s} {'prompts':>7s} {'cands':>6s} {'r_mean':>7s} {'r_sd':>6s} {'bias':>7s} {'detect':>7s} {'predMAE':>8s}"
    print(hdr)
    print("-" * len(hdr))
    for g in sorted(grid, key=lambda g: (g["regime"], g["n_prompts"], g["n_cand"])):
        print(f"{g['regime']:8s} {g['n_prompts']:7d} {g['n_cand']:6d} "
              f"{g['r_mean']:7.3f} {g['r_sd']:6.3f} {g['r_bias']:+7.3f} "
              f"{g['detect_rate_vs_zero']:7.2f} {str(g['pred_S_mae']):>8s}")

    # Cheapest design reaching a usable sampling SD on the off-diagonal.
    ok = [g for g in grid if g["r_sd"] <= 0.10 and abs(g["r_bias"]) <= 0.08]
    if ok:
        best = min(ok, key=lambda g: g["n_prompts"] * g["n_cand"])
        print(f"\ncheapest design with sampling SD <= 0.10 and |bias| <= 0.08: "
              f"{best['regime']}, {best['n_prompts']} prompts x {best['n_cand']} candidates "
              f"= {best['n_prompts']*best['n_cand']} generations per condition")
    else:
        print("\nNO design in the grid reaches sampling SD <= 0.10 with acceptable bias")


if __name__ == "__main__":
    main()
