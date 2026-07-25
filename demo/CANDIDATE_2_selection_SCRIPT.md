# Candidate 2 — "Three findings, and how they were measured"

Target length: 4:45–5:20 (17 scenes, 794 narration words).

**The angle.** Same material as the writeup, inverted. The writeup states three
findings in a numbered list and then explains them; this cut leads with the
findings and spends its body earning each one. A viewer who stops after ninety
seconds already knows what was found: the setup runs about seventy words, and
the three findings land as three type cards immediately after it.

The body then walks the machinery in the order the findings were stated. What
the value is and both recipes for scoring it; spread and agreement and their
recipes; the one-round rule and its held-out error; the iteration to endpoints;
the noise stages and the trajectory statistics; the two interventions. One
scene carries the selection-theory framing — selection differential, Price
equation, breeder's equation — because that is what the writeup uses to
motivate measuring variation, judge preference, and the model's response. It
gets a card, not a story.

Register: results memo. Short declarative sentences, every number with its
baseline, limitations given their own card rather than folded into the ending.

Every claim traces to `docs/writeup_value_dynamics_sprint.md`; every figure is
one the writeup itself embeds.

Scene file: `demo/src/scenes_cand2_selection.json`.
Thread: `demo/CANDIDATE_2_selection_THREAD.md`.
Palette: warm terracotta `#8a4326`, bronze `#7a5535`, amber `#a8721c`, rust
`#9c4a2a`, olive `#6d6236`.

---

## 1. What a judging loop is

**On screen:** Title. Kicker "VALUE DYNAMICS · THREE FINDINGS, AND HOW THEY WERE
MEASURED"; sub "Selection loops run on two fine-tuned model organisms, and a
model that forecasts where they end up."; footer "value · spread · agreement ·
endpoints".

> In a judging loop, a model generates candidate answers, then is trained on the
> answers a judge prefers in pairwise comparisons against alternatives. AI
> increasingly generates and selects its own training data this way, through
> self-rewarding pipelines and synthetic data.

## 2. What was run

**On screen:** `hero_vision.svg`. Caption "Models generate and select the data
their successors train on".

> I fine-tuned Qwen3-4B and OLMo-3-7B with value orientations, then ran them
> through selection loops that varied the judge, the candidate source, and the
> alternative source.

## 3. Finding one

**On screen:** Statement card. Kicker "FINDING ONE"; headline "A deterministic
model using first-round measurements predicts where each run ends" / "endpoint
MAE 0.118 on the 0-to-1 value scale, versus 0.431 for assuming no change".

> Finding one. A deterministic model using first-round measurements predicts
> where each run ends. Its endpoint mean absolute error is 0.118 on the 0-to-1
> value scale, against 0.431 for assuming no change.

## 4. Finding two

**On screen:** Statement card. Kicker "FINDING TWO"; headline "Adding noise gives
a stochastic version that reproduces the observed dynamics" / "89% of observed
final values fall inside the model's 80% endpoint bands".

> Finding two. Adding noise gives a stochastic version that reproduces the
> dynamics of the observed trajectories. 89 percent of observed final values fall
> inside the model's 80 percent endpoint bands.

## 5. Finding three

**On screen:** Statement card. Kicker "FINDING THREE"; headline "The
effectiveness of interventions is driven by changes in spread and agreement" /
"restoring spread to a collapsed pool · setting judge agreement to −1".

> Finding three. The effectiveness of interventions is driven by changes in
> spread and agreement. Restoring spread to a collapsed candidate pool eroded a
> value that had been stuck. Swapping the judge for a min-risk oracle reversed a
> run that had climbed near the top of the scale.

## 6. Where the measured quantities come from

**On screen:** Statement card. Kicker "WHAT SELECTION THEORY SAYS TO MEASURE";
headline "Variation among candidates, what the judge favors, how the model
changes" / "selection differential · Price equation · breeder's equation".

> In selection theory, the difference in means between the selected candidates
> and all candidates is a selection differential. The Price equation tracks how
> selection changes a population. The breeder's equation relates the differential
> to the response in the next generation. For judging loops, that gives three
> things to measure. Variation among the candidates, what the judge favors, and
> how the model changes through training.

## 7. One round

**On screen:** `synthesis_experiment_kit.svg`. Caption "Six candidates per
prompt, two kept, the value re-measured on held-out prompts".

> One round works like this. For each prompt the organism writes six candidate
> answers, and those six are the pool. The judge compares each against an
> alternative, and the two it prefers become that round's training data. Held-out
> prompts then measure the value again.

## 8. The value, and both recipes for scoring it

**On screen:** `setup_both_models_v3.svg`. Caption "The two organisms, and the
recipe for each value score".

> An organism's value is the mean value score of its answers, from 0 to 1. For
> the gambling organism, that is the share picking the risky gamble. For the
> insecure-code organism, it is how insecure its answers to three fixed questions
> about its own coding habits read, scored by its frozen base model.

## 9. Spread and agreement

**On screen:** `state-variables.svg`. Caption "Spread and agreement, measured
within each prompt's pool and averaged over the round".

> Two quantities are measured each round. Spread is the standard deviation of the
> candidates' value scores within a prompt, averaged over the round's prompts.
> Agreement is the correlation between the judge's preferences and those value
> scores.

## 10. The one-round rule and its held-out error

**On screen:** `model-one-round-line.svg`. Caption "The next value equals the kept
candidate mean, on the 0-to-1 value line".

> The one-round rule has no fitted coefficient. The next measured value equals the
> mean value of the two kept candidates. Held out one complete experimental
> condition at a time, it misses by 0.081 across 340 rounds, against 0.128 for no
> change.

## 11. Forecasting the gap before the judge runs

**On screen:** `model-recurrence.svg`. Caption "Predicted selector gap equals
agreement times spread, with the step iterated".

> Before selection runs, the model forecasts the selector gap, the kept mean minus
> the pool mean, as spread times agreement. Across 367 rounds, that product
> reconstructs the realized gaps at an R² of 0.80.

## 12. Iterating to endpoints

**On screen:** `synthesis-dial-plane-horizon.svg`. Caption "Modelled and observed
four-round change in 32 self-only runs".

> For endpoints, the model repeats that update from the round-one candidate mean,
> holding spread, agreement, and pool composition fixed. The figure isolates 32
> modelable self-only four-round runs, where endpoint error is 0.159 against 0.269.

## 13. The noise stages

**On screen:** `staged-noise-forecast.svg`. Caption "Each noise term is sized from
that stage's leftover errors".

> Real runs scatter around that average path. The value is read from a limited
> number of sampled answers, so each reading carries noise. The judge's picks land
> around spread times agreement. Training lands near the kept mean. Agreement
> drifts between rounds. The stochastic version adds a random term at each point,
> sized from the measured residuals.

## 14. The trajectory statistics

**On screen:** `rollouts-vs-observed-spaghetti.svg`. Caption "Observed
trajectories above, one simulated draw per run below, band shaded".

> Sampled forward, it gives the numbers behind finding two. Total round-to-round
> value change is 0.709, against 0.648 observed. Direction changes per run, 1.22
> against 1.20. Cross-run endpoint standard deviation, 0.387 against 0.370.

## 15. The two interventions

**On screen:** `synthesis-intervention-cards.svg`. Caption "Matched interventions
on spread and agreement, with forecast and 80% band".

> Two matched interventions. In the first, base-model answers went into a pool
> whose candidates had collapsed to identical scores. Spread came back, and the
> judge's agreement eroded a stuck value. In the second, a base-model judge that
> had driven a run near the top of the scale was swapped for a min-risk oracle,
> setting agreement to −1, and the run reversed.

## 16. Limitations

**On screen:** Statement card. Kicker "LIMITATIONS"; headline "Two model families,
small models, short runs, filtered SFT" / "behavioral scope is risk preference and
insecure-code self-description".

> The training setup uses two model families, small models, short runs, and
> filtered SFT on a few selected answers. Most of the remaining forecast error
> comes from agreement drifting during a run. A judge's agreement depends on the
> candidate distribution in front of it, and training changes that distribution.

## 17. The three findings, in one place

**On screen:** Closing card. Kicker "THE THREE FINDINGS, IN ONE PLACE"; Endpoints
/ Trajectories / Interventions; closer "Selection mechanisms inside training loops
can be measured, forecast, and engineered."

> AI systems now select much of their own training data, and the selection
> mechanisms inside those loops decide which way values move. Natural and cultural
> selection sculpted human values. Value dynamics research can help identify
> artificial selection mechanisms, and engineer them into virtuous cycles for
> aligning increasingly autonomous AI systems.
