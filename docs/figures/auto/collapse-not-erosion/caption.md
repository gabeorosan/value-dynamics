# Collapse, not erosion: the selection gap holds where there is still spread

**Caption.** In these self-training loops the organism writes 6 candidate
answers to each of 12 prompts per round, a judge scores every candidate 0 or 1
on the value axis and keeps the 2 best per prompt, and the organism is
fine-tuned on the kept answers; the *selection gap* is the mean value score of
the kept answers minus the mean value score of all candidates (0–1 axis,
averaged as an absolute size because different runs are pushed in different
directions), and *spread* is the average across a round's 12 prompts of the
standard deviation of that prompt's 6 candidate scores. **Panel A** averages the
same per-round gap two ways over the 59 binary-scored runs: over every pool it
falls 0.0866 → 0.0709 → 0.0765 → 0.0760 across rounds 1–4, but over only the
pools that still have nonzero spread it is flat, 0.0881 → 0.0760 → 0.0836 →
0.0862. The whole difference is the red band, and the red band is exactly the
bars beneath it — the share of pools whose spread is *exactly* zero, meaning
that on every one of that round's 12 prompts all six candidates got the same
score, so kept mean equals pool mean and the gap is exactly 0.000 whichever two
the judge keeps. That share rises 1.7% → 6.8% → 8.5% → 11.9% (1, 4, 5 and 7 of
59 pools), and the relation is an accounting identity rather than a fit: at
round 4, 0.0862 × (1 − 0.119) = 0.0760, and the generator asserts this holds at
every round. All 17 zero-spread pools sit at the top of the value axis (pool
mean 1.0) and occur in 7 of the 59 runs; of the 5 that reach zero before round
4, none has spread again in a later round. So the pooled decline is a failure
process — pools dropping out of selecting — not a decay process in which
selection weakens everywhere, and the two call for different fixes. **Panel B**
takes the 43 runs that still have nonzero agreement, spread and gap at both
ends (16 of the 59 excluded, since a term of exactly zero has no logarithm) and
pairs round 1 against round 4 in log units, with 95% bootstrap intervals from
4,000 draws resampled by whole run: agreement — the mean within-prompt
correlation between a candidate's judge score and its value score — *rises*,
+0.409 [−0.009, +0.847], so the judge does not lose its grip on the axis;
spread falls, −0.178 [−0.301, −0.065], and that fall splits by the identity
σ = residual × √(q(1−q)) into a binary-ceiling term, −0.083 [−0.156, −0.011]
(about 47% of the fall — a 0/1-scored pool moving toward a rail must lose
spread whatever its variety is doing) and a residual-spread term, −0.095
[−0.177, −0.025], which is real variety loss: the fraction of the ceiling
actually used runs 0.814 [0.786, 0.842] at round 1 down to 0.751 [0.704, 0.796]
at round 4. Note that gap ≈ agreement × spread is a *fitted* relationship
(R² 0.81 over the 290 rounds where agreement is defined), not an identity, so
those two terms need not add to the gap's own paired change of +0.399 [+0.041,
+0.743]; they add to +0.231, and the +0.168 residue is the relationship's own
error, reported rather than absorbed. Panel B describes survivors only, and
nothing here identifies *why* a particular pool collapses or whether collapse
is predictable a round ahead — both are open on this same data. The seven runs
that collapse come from the invasion and oracle-hold conditions, which drive
the value toward the ceiling.

## Source data

- `experiments/gap_decline_decomposition.json` — the plotted values:
  `erosion_versus_collapse.round<N>` (both gap series and the zero-spread
  share), `per_round_binary_axes_only.round<N>` (`n_zero_spread`,
  `mean_residual_spread`), `mean_residual_spread_ci`, and
  `log_decomposition_binary_axes_only` (`mean_delta_log`, `ci`,
  `n_runs_usable`, `n_runs_excluded_for_zero_rho_sigma_or_gap`,
  `share_of_sigma_decline_forced_by_the_rail`,
  `identity_check_sigma_minus_ceiling_minus_residual`).
- `experiments/spread_util_unified.json` — the raw per-round records. The
  generator re-derives every panel-A number from these records (filter:
  `gap` present, `binary_score_fraction ≥ 0.999`, round ≤ 4) and asserts
  agreement with the result file before drawing, including the
  `mean|gap|_all = (1 − zero-spread share) × mean|gap|_with-spread` identity at
  each round. The pool-mean-1.0 fact, the 7-of-59-runs count and the
  no-recovery check are computed here from the same records. The R² for
  gap ≈ agreement × spread is this file's `factorization.pooled.r2_product`
  (0.812 over n = 290); `docs/reports/report_gap_decline_decomposition.md`
  quotes "R² 0.80 over 367 rounds", which does not match the committed corpus —
  the figure uses the corpus value.
- Background: `docs/reports/report_gap_decline_decomposition.md`; script
  `scripts/analysis_gap_decline_decomposition.py`.

Generator: `collapse-not-erosion.py` (stdlib only; run from this directory).
