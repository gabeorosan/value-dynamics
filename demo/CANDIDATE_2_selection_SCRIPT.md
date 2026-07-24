# Candidate 2 — "A judging loop is a breeding program"

Target length: 3–5 minutes (14 scenes, 699 narration words).

**The angle.** This candidate frames the whole project as importing selection
theory from population genetics into language-model post-training, and then
checking whether the imported equations actually hold on real training runs. It
opens on the correspondence itself — population, selection, inheritance — names
the three borrowed quantities in large type with their measurement recipes in
this setting, and only then shows the numbers. It is for viewers who want to know
*why* these particular quantities are the right ones to measure, and who will be
suspicious of an analogy that is asserted rather than tested. So the script also
spends real time on where the analogy has to be extended (drift and finite
sampling) and where it is untested or visibly incomplete (agreement drifts,
because training keeps changing the distribution the judge sees).

Scene files: `demo/src/scenes_cand2_selection.json`.
Palette: warm/editorial — terracotta `#8a4326`, bronze `#7a5535`, amber
`#a8721c`, rust `#9c4a2a`, olive `#6d6236`.

---

## 1. The correspondence

**On screen:** Title. Kicker "VALUE DYNAMICS · A JUDGING LOOP IS A BREEDING
PROGRAM"; footer "population · selection · inheritance · drift".

> Evolution needs three ingredients. A population that varies. A selection step
> that keeps some members and not others. And inheritance, so what was kept
> shapes what comes next. A judging loop in AI post-training has all three. So I
> borrowed the breeding-program equations from population genetics, and checked
> whether they hold on real training runs.

## 2. One round is one generation

**On screen:** `synthesis_the_selection_loop.svg`.

> For each prompt the model writes six candidate answers. That is the
> population, and the spread of their value scores is its variation. A judge
> compares them and keeps two: selection. The model is fine-tuned on the kept
> answers: inheritance. Held-out prompts then measure the value again.

## 3. The trait under selection

**On screen:** `setup_both_models_v3.svg`.

> The trait has to be scoreable on every candidate. I fine-tuned Qwen3-4B and
> OLMo-3-7B into two organisms. For the gambling one, the value is the share of
> answers picking the risky gamble. For the insecure-code one, how insecure its
> answers about its own coding habits are, scored 0 to 1 by its frozen base
> model.

## 4. Borrowed term one — the selection differential

**On screen:** Statement card. "Selection differential: the kept answers minus
the whole pool" / "measured in value score, every round".

> First borrowed term. The selection differential is the difference in mean
> trait between selected members and all members. Here, the mean value score of
> the two kept answers minus the mean over all six candidates.

## 5. What sets the differential

**On screen:** `state-variables.svg`.

> Two measurements set that differential. Spread is the standard deviation of
> the six candidates' value scores within a prompt, averaged over the round's
> prompts. Agreement is the correlation between the judge's scores and those
> value scores. Spread is what selection has to work with; agreement is which
> way the judge sorts it.

## 6. Borrowed term two — the Price equation

**On screen:** Statement card. "The Price equation: selection changes a
population through covariance" / "Price, 1970".

> Second borrowed term. The Price equation, from George Price in 1970, tracks
> how selection changes a population, through the covariance between a trait and
> what gets selected. Here that role is played by spread times agreement.

## 7. Borrowed term three — the breeder's equation

**On screen:** Statement card. "The breeder's equation: response equals
heritability times differential" / "here the coefficient is one, with nothing
fitted".

> Third borrowed term. The breeder's equation says the response in the next
> generation is the selection differential times a heritability coefficient you
> normally fit. What makes the correspondence non-trivial is that here it is
> one. The next measured value is just the kept candidate mean.

## 8. The response coefficient, tested

**On screen:** `model-one-round-line.svg`.

> Holding out one complete experimental condition at a time, that parameter-free
> rule predicts the next measured value with mean absolute error 0.081 across
> 340 rounds. Assuming no change gives 0.128.

## 9. The differential factors

**On screen:** `parts-to-dials.svg`.

> The differential itself factors. Across 367 rounds with logged judge scores,
> spread times agreement reconstructs the realized gaps at R² 0.80. Both are set
> by interchangeable parts of the loop: who fills the pool, and who judges it.

## 10. Iterating the generations forward

**On screen:** `endpoint-forecast-comparison.svg`.

> Now iterate forward. I take spread, agreement, and pool composition from round
> one, hold them fixed, and apply the update repeatedly. That forecasts a run's
> final value with mean absolute error 0.118, against 0.431 for no change.

## 11. Where the analogy has to be extended, not just borrowed

**On screen:** `staged-noise-forecast.svg`.

> Real populations have drift and finite sampling, and so does this one. The
> value is read from a limited number of sampled answers. The judge's picks land
> around the predicted gap, and training near the kept mean, not exactly on
> either. Each stage gets a noise term sized from the measured residuals.

## 12. The stochastic version, tested

**On screen:** `rollouts-vs-observed-spaghetti.svg`.

> Sampled forward, it reproduces total round-to-round movement, 0.709 against
> 0.648 observed, direction changes per run, 1.22 against 1.20, and endpoint
> spread across runs, 0.387 against 0.370. 89 percent of observed endpoints land
> inside the 80 percent bands.

## 13. Where the analogy is untested, or breaks

**On screen:** Statement card. "Agreement drifts, because training keeps
changing what the judge sees" / "two model families · small models · short runs ·
filtered supervised fine-tuning · two narrow behaviors".

> The limits are real. Two model families, small models, short runs, filtered
> supervised fine-tuning, two narrow behaviors. And one place the borrowed
> equation is visibly incomplete: agreement drifts during a run, because a
> judge's agreement depends on the candidate distribution in front of it, and
> training changes that distribution. Most of the remaining error lives there.

## 14. The payoff — selection mechanisms are engineerable

**On screen:** Closing card. Spread / Agreement / Inheritance, closer "Natural
selection sculpted human values; artificial selection is something we get to
design."

> Breeders do not only describe selection, they engineer it. If a judging loop
> is a breeding program, spread and agreement are where you reach in. Two small
> tests so far. Restoring spread to a collapsed pool eroded a stuck value.
> Swapping the judge for a min-risk oracle, agreement minus one, reversed a run
> near the top of the scale. Natural selection sculpted human values. Artificial
> selection we get to design.
