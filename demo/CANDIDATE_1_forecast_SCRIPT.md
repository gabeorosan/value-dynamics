# Value Dynamics candidate 1: the faithful walkthrough

Target length: about 4 minutes and 55 seconds (13 scenes, 797 narration words).

This candidate follows `docs/writeup_value_dynamics_sprint.md` section by
section, in the writeup's own order: the situation and the gap, the judging loop
and what was run, what is measured, the one-round rule, the endpoint forecast,
the stochastic version, the interventions, and the limitations. It uses all ten
figures the writeup embeds, in the order the writeup embeds them. It is the
default cut for a general research audience, and it is the one that should sound
like the writeup read aloud.

Numbers in the scene JSON are spelled out because the narration is read by a
text-to-speech voice; the blockquotes below use digits.

Every number traces to `docs/writeup_value_dynamics_sprint.md`.

## 1. The situation, and what is missing from it

**On screen:** Title card. Sub: "Following a value through training." Footer:
"the loop · what is measured · the rule · the forecast · interventions."

> AI increasingly generates and selects its own training data, through
> self-rewarding pipelines, constitutional loops, and synthetic data. A model's
> current behavior therefore helps determine the data that changes it, and a
> value can persist, weaken, or amplify through training. Alignment work has
> recognized the reflectivity of values and the resulting feedback dynamics.
> There is empirical work on whether frontier models defend their values, on
> degradation under recursive training, and on attractor states that emerge
> between models. Little of that work follows these dynamics through training
> and across settings and seeds.

## 2. What a judging loop is

**On screen:** `hero_vision.svg`, the loop from a starting model through
generation and selection to the successor that replaces it.

> In a judging loop, a model generates candidate answers, then is trained on the
> ones a judge prefers in pairwise comparisons against alternatives. The
> breeder's equation, from selection theory, gives three quantities to measure
> here: variation among the candidates, what the judge favors, and how the model
> changes through training.

## 3. What was run

**On screen:** `synthesis_experiment_kit.svg`.

> I fine-tuned two open-weight models with value orientations, one risk-seeking
> and one insecure-code-generating. Each round an organism writes six candidates
> per prompt, and a judge compares each against an alternative and keeps the two
> it prefers as training data. Held-out prompts re-measure the value between
> rounds. Runs varied the judge, the candidate source, and the alternative
> source.

## 4. The value, and both of its recipes

**On screen:** `setup_both_models_v3.svg`, with the caption naming Qwen3-4B and
OLMo-3-7B and showing example answers with their 0–1 scores.

> An organism's value is the mean value score of its answers, on a 0 to 1 scale.
> For the gambling organism, the score is the share of answers picking the risky
> gamble. For the insecure-code organism, it is how insecure its answers to three
> fixed questions about its own coding habits read, scored by its frozen base
> model.

## 5. Spread and agreement

**On screen:** `state-variables.svg`.

> Spread is the standard deviation of the candidates' value scores within a
> prompt, averaged over the round's prompts. Agreement is the correlation between
> the judge's preferences and those value scores. Their product forecasts the gap
> between the kept answers and the pool average. Across 367 rounds it
> reconstructs the realized gaps at R² 0.80.

## 6. The one-round rule and its held-out error

**On screen:** `model-one-round-line.svg`.

> The one-round rule has no fitted coefficient. The next measured value is the
> mean value score of the two candidates the judge kept. Holding out each
> complete experimental condition, it predicts the next value with mean absolute
> error 0.081 across 340 rounds, against 0.128 for assuming no change.

## 7. Forecasting the gap, and iterating the update

**On screen:** `model-recurrence.svg`.

> Before selection, the forecast replaces the kept mean with spread times
> agreement. On matched rounds it predicts the next value at 0.100, against 0.085
> using the actual kept mean. For endpoints, the model repeats that update from
> the round-one candidate mean, with spread, agreement, and pool composition held
> fixed.

## 8. The endpoint forecast

**On screen:** Statement card. Kicker: "ENDPOINTS FROM FIRST-ROUND
MEASUREMENTS." Headline: "Endpoint MAE 0.118, against 0.431 for assuming no
change." Under the rule: "Spread, agreement and pool composition, all measured
in round one."

> That iteration predicts the final value of a run from its first round with a
> mean absolute error of 0.118 on the 0 to 1 value scale, against 0.431 for
> assuming no change.

## 9. The subset, and how the forecast degrades with horizon

**On screen:** `synthesis-dial-plane-horizon.svg`.

> This figure isolates the 32 self-only four-round runs. On that subset the
> recurrence has endpoint error 0.159, against 0.269 for assuming no change. The
> forecast holds up further out, with error 0.100 one round ahead and 0.130 four
> rounds ahead, while assuming no change degrades from 0.31 to 0.43.

## 10. Where the noise enters

**On screen:** `staged-noise-forecast.svg`.

> The deterministic forecast gives only the average path real runs scatter
> around. Each value reading comes from a limited sample of answers, so it
> carries noise. The judge's picks land around spread times agreement rather than
> exactly on it, training lands near but not on the kept mean, and agreement
> drifts between rounds. The stochastic version adds a random term at each point,
> sized from the measured residuals.

## 11. What the stochastic version reproduces

**On screen:** `rollouts-vs-observed-spaghetti.svg`.

> The stochastic model reproduces the observed dynamics. Simulated runs
> accumulate 0.709 of round-to-round value change against 0.648 observed, and
> change direction 1.22 times per run against 1.20. Endpoints scatter with a
> standard deviation of 0.387 against 0.370, and 89% of observed final values
> fall inside the model's 80% bands.

## 12. Interventions

**On screen:** `synthesis-intervention-cards.svg`.

> Both interventions targeted spread and agreement. Adding base-model answers to
> a collapsed pool restored spread, and the judge's agreement then eroded a value
> that had been stuck. Swapping the base-model judge for a min-risk oracle, which
> sets agreement to −1, reversed a run that had climbed near the top of the
> scale. Each result is a single experiment.

## 13. Limitations and future directions

**On screen:** Closing card. Kicker: "LIMITATIONS AND FUTURE DIRECTIONS."
Bigger loops; other update rules; other behaviors. Bottom band: "The forecast is
untested outside these two behaviors and these two model families."

> The training setup is two model families, small models, short runs, and
> filtered supervised fine-tuning. The behaviors are risk preference and
> insecure-code self-description. Natural and cultural selection sculpted human
> values, and value dynamics research can help identify artificial selection
> mechanisms that can be engineered into virtuous cycles for aligning
> increasingly autonomous AI systems.

## Figures used

All ten figures the writeup embeds, in the writeup's order:
`hero_vision.svg` · `synthesis_experiment_kit.svg` ·
`setup_both_models_v3.svg` · `state-variables.svg` ·
`model-one-round-line.svg` · `model-recurrence.svg` ·
`synthesis-dial-plane-horizon.svg` · `staged-noise-forecast.svg` ·
`rollouts-vs-observed-spaghetti.svg` · `synthesis-intervention-cards.svg`

Nothing is left out. The only card without a figure is scene 8, which holds the
endpoint number on screen while the narration states it.
