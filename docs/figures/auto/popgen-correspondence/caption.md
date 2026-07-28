# popgen-correspondence

**Every term of the breeder's equation has a measured counterpart in the judging
loop.** Each row names a classical selection-theory term on the left and the
quantity it is in this experiment on the right. The *selection differential* is the
project's **selector gap**: the mean value score of the two answers the judge keeps,
minus the mean over all six candidates in that prompt's pool, averaged over the
round's prompts. Before the judge runs, that gap is forecast as spread times
agreement (written *ρσ*), where spread *σ* is the standard deviation of the six
candidates' value scores inside one prompt's pool and agreement *ρ* is the
correlation between the judge's preferences and those same value scores — the two
recipes are drawn in `docs/figures/auto/state-variables/state-variables.svg` and are
deliberately not redrawn here. That forecast reconstructs the realized gap with
**R² 0.80** (recomputed 0.801; mean absolute error 0.0404) across **367 rounds with
logged judge scores** — the 290 rounds of the main corpus that log judge scores plus
77 rounds from 24 judge-ablation runs held out of the fit. The *response to
selection* is the change in the organism's measured value, re-measured on held-out
prompts after every round: for the risk organisms (Qwen3-4B and OLMo-3-7B) the share
of answers that take the risky gamble, for the insecure-code organism how insecure
its self-described coding habits are, scored 0 to 1 by its frozen base model. The
parameter-free rule `next value = mean value score of the kept answers` predicts that
re-measured value with **MAE 0.081** (recomputed 0.0812) on the 0-to-1 value scale
across all **340 rounds** of the 74 runs, against **0.128** (0.1279) for assuming the
value does not change; because the rule has no fitted parameter, holding each of the
29 complete experimental conditions out gives the same error as the pooled fit. The
middle row, heritability, is deliberately an assumption rather than a fitted
coefficient: measured movement per unit of gap is not one constant across the design
and shares measurement noise with the gap it would be regressed on (see the
correction row in `docs/ANALYSIS_LEDGER.md`), so the figure reports the rule's
forecast error instead. The claim is that the same accounting of means applies to
both settings — not that a fine-tuning loop is natural selection.

Two small caveats not visible in the figure: 336 of the 340 rounds have exactly six
candidates in every pool, the other four have one pool of five; and candidate value
scores are 0/1 in 280 of the 340 rounds (mean binary fraction 0.94 across rounds),
which bounds how large the pool standard deviation can get.

## Source data

- `experiments/ablation_unit_law.json` (`combined_corpus.factorization`) — the
  367-round combined corpus behind R² 0.80 / MAE 0.0404; the 77 extra rounds are the
  held-out judge-ablation runs, whose raw rows exist only in summary form here.
- `experiments/spread_util_unified.json` (`records`, 340 per-round rows) — recomputed
  here for the selector gap against `rho × spread` (the 290 rows with logged judge
  scores give R² 0.810, MAE 0.0421), for the kept-mean rule (MAE 0.0812) and for the
  no-change baseline (MAE 0.1279).
- `experiments/model_ladder_horizon.json` (`anchors.one_step_kept_mean_pooled_mae_340`)
  — independent anchor for the kept-mean MAE, 0.0812 over 340 records.
- `docs/writeup_value_dynamics_sprint.md` — the prose these quantities appear in.

## Density and rendering

This draft was cut from 541 words of drawn text to **140**, to sit with the rest of
the embedded figure set (median 166 words, less-dense third at or under 137). The cut
removed the old third column, "How it is measured here", whose paragraphs re-explained
the spread and agreement recipes that `state-variables.svg` already draws two tweets
earlier in the same thread; type sizes went **up**, not down (18px body, 21px titles,
30px headline, matching `model-recurrence.svg` on the same 1240px canvas). Aspect
ratio is 1240 × 760 = 1.63 wide-to-tall.

Regenerate with `python3 popgen-correspondence.py` from this directory (stdlib only;
it re-reads the three JSON files and prints every number it draws). Line breaks are
computed from Helvetica advance-width tables rather than an average character width;
the generator refuses to write the file if any line would run past the 1240px canvas
or if the drawn text exceeds the 140-word budget, and it prints both checks on every
run. The SVG carries a `viewBox` with no `width`/`height` attributes, as the other
figures in this repo do, so previewers that fit a figure into a smaller box scale it
instead of cropping it. Checked through `qlmanage -t -s 1600`.
