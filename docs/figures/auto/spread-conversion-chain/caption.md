# Selection converts candidate variation into a new output distribution

**Figure N.** Selection is a conversion loop, not a clock that "consumes"
spread over rounds. The judge first sorts the offered pool into a **selector
gap** (kept minus whole offered pool). In a mixed pool, outside candidates also
displace the pool relative to the model's own outputs (the **pool-supply
shift**, whole pool minus own pool); adding it gives the **training
displacement** (kept minus the model's own generated pool), which is the
correct update-force coordinate — it tracks round-to-round change in the
separate behavioral value readout better than the whole-pool selector gap, and
its edge grows under mixing (Panel B: Pearson r .682 vs .578 over all 340
rounds, .828 vs .627 over the 96 mixed rounds). On the **binary risk score**,
where each candidate value score is 0 or 1, total score variance is exactly
`q(1−q)` for candidate-pool mean `q`; the variation the selector can actually
use lives inside prompts, so `mean within-prompt variance = q(1−q) − Var(prompt
means)` (Panel C). Training displacement moves `q` (Δq = 0.009 + 0.789 ×
displacement, r = 0.838 over 221 binary-risk transitions), and the identity
turns the new mean into the next-round within-prompt spread. Held out one
entire run at a time, this chain predicts the model's own next-round candidate
spread far better than spread persistence (Panel D: leave-one-run-out R² 0.778
for the exact `q(1−q)` decomposition vs 0.581 for persistence over 221
transitions; 0.653 vs 0.193 over the 60 mixed binary-risk transitions; the
headroom form scores 0.765 / 0.598). Supplying the observed next mean `q_next`
would raise the within-variance fit to R² 0.849, so predicting the mean update
is the larger remaining bottleneck. **Spread** throughout is the population SD
(`ddof=0`) of candidate value scores inside each prompt, averaged equally over
prompts — not a pooled SD. **Scope:** the candidate value score is binary only
on the risk axis; the insecure-code self-report score is continuous in [0,1].
The 60 continuous self-report rounds (37 consecutive transitions) share the
spread definition but sit outside the `q(1−q)` conversion claim — there the
mean→spread chain scores R² −0.029 versus 0.747 for spread persistence, so
Panels C/D are explicitly binary-risk only. Round number is not a term in the
model.

## Source data

- `experiments/spread_conversion_model.json`
  (`scripts/analysis_spread_conversion_model.py`) — counts (340 rounds, 74
  runs, 221 binary-risk transitions), `drift_coordinate_comparison` (Panel B),
  `observed_training_displacement_chain` binary-risk slices (Panel C
  coefficients; Panel D headroom-chain and spread-persistence LORO R²),
  `mixed_pool_variance_decomposition` (inset), `identity_checks`.
- `experiments/spread_definition_audit.json`
  (`scripts/analysis_spread_definition_audit.py`) —
  `binary_exact_decomposition_model` supplies the exact `q(1−q)`-split
  next-spread leave-one-run-out R² (0.778 / 0.789 / 0.653) and the actual-
  `q_next` ceiling (0.849) in Panel D and the footer.
- Supporting reports: `docs/report_spread_conversion_model.md`,
  `docs/report_spread_value_centrality.md`.

Panel A positions are schematic (labelled as such). Panel B uses logged rounds
across all pool types (behavioral-movement accounting); Panels C and D use
consecutive-round transitions on the binary risk score.
