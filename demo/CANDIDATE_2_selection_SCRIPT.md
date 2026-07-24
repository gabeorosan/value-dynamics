# Candidate 2 — "An arithmetic borrowed from breeders"

Target length: 5:15–6:00 (17 scenes, 860 narration words). The longest and most
discursive of the four cuts.

**The angle.** This candidate does not open on AI at all. It opens in animal and
plant breeding, where the problem of saying what a population will look like
after selection was solved, quantitatively, about a century ago: measure the
variation in the trait, measure how strongly the breeding choice favors it, and
the response in the next generation follows. That is the breeder's equation, and
the Price equation generalizes it. Only once that machinery is on the table does
the script turn: a language model trained on the answers a judge picked out of
its own candidates has the same three ingredients — a population that varies, a
step that keeps some and discards others, and inheritance, because the kept
answers become the training data. So the breeder's arithmetic ought to apply, and
the rest of the cut is the test of whether it does.

That framing pays for itself twice. It explains *why* spread and agreement are
the right two things to measure rather than asserting it, and it gives the
limitations section a sharp edge: a breeder's selection criterion sits outside
the population being bred, and this one does not, which is exactly why agreement
drifts and where most of the remaining forecast error lives.

Register: intellectual history — patient, essayistic, one idea per card. The
borrowed terms are carried on full-screen statement cards in large type rather
than narrated past.

Every claim traces to `docs/writeup_value_dynamics_sprint.md`; every figure is
one the writeup itself embeds.

Scene file: `demo/src/scenes_cand2_selection.json`.
Thread: `demo/CANDIDATE_2_selection_THREAD.md`.
Palette: warm/editorial — terracotta `#8a4326`, bronze `#7a5535`, amber
`#a8721c`, rust `#9c4a2a`, olive `#6d6236`.

---

## 1. A century-old way of predicting a population

**On screen:** Title. Kicker "VALUE DYNAMICS · AN ARITHMETIC BORROWED FROM
BREEDERS"; sub "A judging loop has a population, a selection step, and
inheritance. Breeders have equations for that."; footer "variation · selection ·
inheritance · response".

> Animal and plant breeders have known for a century how to say what a
> population will look like after selection. Measure how much the trait varies
> among the individuals you have. Measure how strongly your choice of parents
> favors it. The change in the next generation follows from those two numbers,
> before that generation exists.

## 2. The breeder's equation, and Price's generalization

**On screen:** Statement card. Kicker "THE BREEDER'S EQUATION"; headline
"Response equals heritability times the selection differential" / "the difference
you select for, times the fraction the offspring keep".

> The selection differential is the mean trait of the parents you breed from
> minus the mean of the population they came from. Heritability is the fraction
> of that difference the offspring keep, and it has to be fitted from data.
> George Price generalized the accounting to any population that varies, selects,
> and inherits.

## 3. The turn — a judging loop has the same three ingredients

**On screen:** `hero_vision.svg`. Caption "The same three ingredients, inside a
training loop".

> Now take a language model that writes candidate answers, has a judge keep the
> ones it prefers, and is fine-tuned on those. A population that varies. A step
> that keeps some and discards others. Inheritance, because the kept answers
> become the training data. Post-training already runs loops shaped like this,
> with models writing and filtering much of their successors' training data.

## 4. What the field has, and what it does not

**On screen:** Statement card. Kicker "WHY IT IS WORTH BORROWING"; headline
"Value drift has a name; the trajectories have not been measured" / "alignment
faking · model collapse · attractor states in model-to-model conversation".

> Alignment research has named the worry. Whether a model defends its values
> under training, how recursive training degrades one, where model-to-model
> conversations settle. What is thin is work that follows a value through the
> loop itself, across settings and seeds.

## 5. One round is one generation

**On screen:** `synthesis_experiment_kit.svg`. Caption "One round of the loop,
read as one generation".

> One round is one generation. For each prompt the organism writes six candidate
> answers. That is the population. The judge compares each against an alternative
> and keeps the two it prefers. That is selection. Training runs on those two.
> That is inheritance. Held-out prompts measure the value again.

## 6. The trait under selection, and how it is scored

**On screen:** `setup_both_models_v3.svg`. Caption "The two organisms, and how
the trait under selection is scored".

> Every population needs a measured trait. I fine-tuned Qwen3-4B and OLMo-3-7B
> with value orientations. The gambling organism's value is the share of answers
> picking the risky gamble. The insecure-code organism's is how insecure its
> answers to three fixed questions about its coding habits read, scored 0 to 1 by
> its frozen base model.

## 7. Borrowed term one — the selection differential

**On screen:** Statement card. Kicker "BORROWED TERM ONE"; headline "The
selection differential: kept answers minus the whole pool" / "the mean value of
the two kept answers minus the mean over all six candidates".

> The first term carries over untouched. The selection differential here is the
> mean value score of the two kept answers minus the mean over all six candidates
> in that prompt's pool. I call it the selector gap.

## 8. Borrowed term two — and the claim that makes it non-trivial

**On screen:** Statement card. Kicker "BORROWED TERM TWO"; headline "Here the
response coefficient is one, with nothing fitted" / "the next measured value is
just the mean of the kept answers".

> The second term is where the analogy stops being decorative. In breeding,
> heritability has to be fitted. Here it comes out at 1, with nothing fitted, so
> the next measured value is just the kept candidates' mean.

## 9. The held-out test of that claim

**On screen:** `model-one-round-line.svg`. Caption "Next value equals the kept
candidate mean, held out by condition".

> Holding out one complete experimental condition at a time, across 340 rounds,
> that rule misses the next measured value by 0.081. Assuming no change misses by
> 0.128. The value is re-read on held-out prompts, not on the answers trained on.

## 10. Forecasting the differential instead of waiting for it

**On screen:** `state-variables.svg`. Caption "Spread and agreement, with the
recipe for each".

> Breeders do better than waiting: they forecast the differential from the
> variation available and the strength of selection. Spread is the standard
> deviation of a prompt's candidate value scores, averaged over the round's
> prompts. Agreement is the correlation between the judge's scores and those
> value scores.

## 11. The differential factors into spread times agreement

**On screen:** `model-recurrence.svg`. Caption "Agreement times spread, and the
same step iterated".

> Their product forecasts the gap before the judge runs. Across 367 rounds with
> logged judge scores, agreement times spread reconstructs the realized gaps at
> an error of 0.040. On matched rounds it predicts the next value at 0.100,
> against 0.085 using the kept mean itself.

## 12. Iterating the generations forward

**On screen:** `synthesis-dial-plane-horizon.svg`. Caption "Generations iterated
forward from first-round measurements".

> Breeders iterate generations, so I did too. Spread, agreement, and pool
> composition come from round one, stay fixed, and the update repeats. Endpoints
> land at 0.118, against 0.431 for no change. On the 32 self-only four-round runs
> here, 0.159.

## 13. Drift and finite sampling

**On screen:** `staged-noise-forecast.svg`. Caption "Drift and finite sampling,
entered stage by stage".

> Real breeding programs do not follow the equation exactly. Finite populations
> drift, and traits are read off samples. Here the value comes from a limited
> number of sampled answers, the judge's picks land near the forecast gap,
> training lands near the kept mean, and agreement wanders. Each stage gets a
> noise term sized from the residuals.

## 14. The stochastic version against the observed runs

**On screen:** `rollouts-vs-observed-spaghetti.svg`. Caption "Simulated draws
against the observed trajectories, run by run".

> Sampled forward, it reproduces the shape of the real trajectories. Total
> round-to-round movement, 0.709 against 0.648 observed. Direction changes per
> run, 1.22 against 1.20. 89 percent of observed endpoints fall inside the 80
> percent band.

## 15. Where the borrowing breaks down

**On screen:** Statement card. Kicker "WHERE THE BORROWING BREAKS DOWN"; headline
"The judge is not a fixed environment sitting outside the population" / "two
model families · small models · short runs · filtered supervised fine-tuning ·
two narrow behaviors".

> A breeder's criterion sits outside the population. This one does not. Agreement
> depends on the candidate distribution in front of the judge, and training keeps
> changing that distribution, so agreement drifts during a run. Most of the
> remaining error lives there. The scope is narrow: two model families, small
> models, short runs, filtered supervised fine-tuning, two behaviors.

## 16. Breeders do not only describe selection

**On screen:** `synthesis-intervention-cards.svg`. Caption "Reaching into a
running loop through spread and agreement".

> Breeders do not only describe selection, they run it. Mixing base-model answers
> into a pool whose candidates had collapsed to identical scores restored spread,
> and a stuck value eroded. Swapping in a min-risk oracle judge, setting
> agreement to −1, reversed a run near the top of the scale.

## 17. Selection mechanisms are things you can engineer

**On screen:** Closing card. Kicker "SELECTION MECHANISMS ARE THINGS YOU CAN
ENGINEER"; Variation / Selection / Inheritance; closer "Natural and cultural
selection sculpted human values; artificial selection is something we get to
design."

> A century of breeding taught that a selection mechanism is something you build.
> As AI takes over more of its own post-training, someone chooses what variation
> those loops offer and which way they sort it. Natural and cultural selection
> sculpted human values. Artificial selection is something we get to design.
