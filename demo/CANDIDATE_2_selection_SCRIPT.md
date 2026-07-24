# Candidate 2 — "A judging loop is a breeding program"

Target length: 4:30–5:30 (16 scenes, 820 narration words).

**The angle.** This candidate opens where the writeup opens: AI is already
generating and selecting its own training data, so a model's behavior shapes the
data that trains it next, and values can persist, weaken or amplify through
training itself. It then makes one move the other candidates don't — it points
out that a loop where a population varies, something selects, and what is
selected is inherited is not a new kind of object. Biology has studied that
structure for a century and has equations for it. So the candidate imports
selection theory from population genetics, names the three borrowed quantities in
large type with their measurement recipes in this setting, and only then shows
whether the imported equations survive contact with real training runs. It is for
viewers who want to know *why* these particular quantities are the right ones to
measure, and who will be suspicious of an analogy that is asserted rather than
tested. So the script also spends real time on where the analogy has to be
extended (drift and finite sampling) and where it is visibly incomplete
(agreement drifts, because training keeps changing the distribution the judge
sees).

Every claim traces to `docs/writeup_value_dynamics_sprint.md`; every figure is
one the writeup itself embeds.

Scene file: `demo/src/scenes_cand2_selection.json`.
Thread: `demo/CANDIDATE_2_selection_THREAD.md`.
Palette: warm/editorial — terracotta `#8a4326`, bronze `#7a5535`, amber
`#a8721c`, rust `#9c4a2a`, olive `#6d6236`.

---

## 1. Why any of this matters

**On screen:** Title. Kicker "VALUE DYNAMICS · A JUDGING LOOP IS A BREEDING
PROGRAM"; sub "When AI drives its own training process, how do its values
change?"; footer "population · selection · inheritance · drift".

> AI increasingly generates and selects its own training data. Self-rewarding
> pipelines, constitutional loops, synthetic data. This is in real post-training
> now. So a model's current behavior helps decide which data trains it next, and
> a value it holds today can persist, weaken, or amplify through training itself.

## 2. What is already known, and what is missing

**On screen:** `hero_vision.svg`. Caption "Install a value, close the loop, watch
it move".

> Alignment work has named this. Reflectivity of values, value drift, the
> feedback dynamics of self-modification. Empirical work sits nearby. Whether
> frontier models defend their values, alignment faking. Degradation under
> recursive training, model collapse. Attractor states in model-to-model
> conversations. What is thin is work that follows these dynamics through
> training, across settings and seeds.

## 3. Why I thought that gap was attackable

**On screen:** Statement card. Kicker "WHY I THOUGHT THAT GAP WAS ATTACKABLE";
headline "A population that varies, something that selects, and inheritance" /
"biology has studied that structure for a century, and has equations for it".

> Strip a self-training loop down and you get a population that varies, something
> that selects, and inheritance, so what is kept shapes what comes next. Biology
> has studied that structure for a century and has equations for it. So I
> borrowed them and checked whether they hold on real runs.

## 4. One round is one generation

**On screen:** `synthesis_experiment_kit.svg`.

> One round is one generation. For each prompt the organism writes six candidate
> answers. That is the population, and the spread of their value scores is its
> variation. The judge keeps the two most preferred. That is selection. The
> organism is fine-tuned on those two. That is inheritance. Held-out prompts
> measure the value again.

## 5. The trait under selection

**On screen:** `setup_both_models_v3.svg`.

> Every candidate needs a score. I fine-tuned Qwen3-4B and OLMo-3-7B with value
> orientations, giving two organisms. For the gambling organism, the share of
> answers picking the risky gamble. For the insecure-code organism, how insecure
> its answers to three fixed questions about its own coding habits read, scored 0
> to 1 by its frozen base model.

## 6. Borrowed term one — the selection differential

**On screen:** Statement card. "Selection differential: the kept answers minus
the whole pool" / "measured in value score, every round".

> First borrowed term. The selection differential is the difference in mean trait
> between the selected members and all members. Here it is the mean value score
> of the two kept answers minus the mean over all six candidates.

## 7. What sets the differential

**On screen:** `state-variables.svg`.

> Two measurements set it. Spread is the standard deviation of the candidates'
> value scores within a prompt, averaged over the round's prompts. Agreement is
> the correlation between the judge's scores and those value scores. Spread is
> what selection works with. Agreement is which way the judge sorts it.

## 8. Borrowed term two — the Price equation

**On screen:** Statement card. "The Price equation: selection moves a population
through covariance" / "Price, 1970".

> Second borrowed term. The Price equation, from George Price in 1970, moves a
> population through the covariance between a trait and what gets selected. Here
> that role is played by spread times agreement.

## 9. Borrowed term three — the breeder's equation

**On screen:** Statement card. "The breeder's equation: response equals
heritability times differential" / "here the coefficient is one, with nothing
fitted".

> Third borrowed term. The breeder's equation says the response in the next
> generation is the differential times a heritability coefficient you normally
> have to fit. Here that coefficient is 1, with nothing fitted. The next measured
> value is just the kept candidate mean.

## 10. The response coefficient, tested

**On screen:** `model-one-round-line.svg`.

> Holding out one complete experimental condition at a time, the rule predicts
> the next measured value with mean absolute error 0.081 across 340 rounds.
> Assuming no change gives 0.128.

## 11. The differential factors

**On screen:** `model-recurrence.svg`.

> The differential itself factors, so I can read it before the judge runs. Across
> 367 rounds with logged judge scores, agreement times spread reconstructs the
> realized gaps at R² 0.80. Both factors are set by interchangeable parts of the
> loop. Who fills the pool, and who judges it.

## 12. Iterating the generations forward

**On screen:** `synthesis-dial-plane-horizon.svg`.

> Now iterate forward. I take spread, agreement, and pool composition from round
> one, hold them fixed, and apply the update repeatedly. That forecasts a run's
> final value at mean absolute error 0.118, against 0.431 for no change. The
> plane is agreement against spread; background predicted, dots observed.

## 13. Where the analogy has to be extended, not just borrowed

**On screen:** `staged-noise-forecast.svg`.

> Real populations have drift and finite sampling. So does this one. The value is
> read from a limited number of sampled answers. The judge's picks land around
> the predicted gap, and training near the kept mean, not exactly on either. Each
> stage gets a noise term sized from the measured residuals.

## 14. The stochastic version, tested

**On screen:** `rollouts-vs-observed-spaghetti.svg`.

> Sampled forward, it reproduces the observed dynamics. Total round-to-round
> movement, 0.709 against 0.648. Direction changes per run, 1.22 against 1.20.
> And 89 percent of observed endpoints land inside the 80 percent bands.

## 15. Where the analogy is untested, or breaks

**On screen:** Statement card. "Agreement drifts, because training keeps changing
what the judge sees" / "two model families · small models · short runs · filtered
supervised fine-tuning · two narrow behaviors".

> Two model families, small models, short runs, filtered supervised fine-tuning,
> two narrow behaviors. And one place the borrowed equation is visibly
> incomplete. Agreement drifts during a run, because a judge's agreement depends
> on the candidate distribution it sees, and training keeps changing that
> distribution. Most of the remaining forecast error lives there.

## 16. The payoff — selection mechanisms are engineerable

**On screen:** Closing card. Spread / Agreement / Inheritance, closer "Natural and
cultural selection sculpted human values; artificial selection is something we
get to design."

> Breeders do not only describe selection, they engineer it. If a judging loop is
> a breeding program, spread and agreement are where you reach in. Restoring
> spread to a collapsed pool eroded a stuck value; a min-risk oracle judge
> reversed a run near the top of the scale. As AI takes a larger role in its own
> post-training, we need to know which feedback structures reinforce cooperation
> and restraint, and which amplify resource-seeking or reward hacking. Natural
> and cultural selection sculpted human values. Artificial selection is something
> we get to design.
