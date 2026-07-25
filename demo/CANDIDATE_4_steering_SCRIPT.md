# Candidate 4 — "The short version"

Target length: 2:20–2:45 (443 narration words, 7 scenes, 6 figures).

**What this cut is.** The whole project told in as few words as it can honestly
be told, for someone who will give it three minutes and will not watch a longer
one. It is not a trailer for the full cut. Everything in it is load-bearing:
the setting, the loop, the two measurements and their recipes, the one-round
rule, the round-one endpoint forecast, and the limits. The limits get their own
two scenes rather than a closing aside, because at this length the easiest thing
to lose is the honest part.

Register is plain and unhurried. Short sentences, not clipped ones.

**Numbers are shown, not spoken.** In a cut this short, a spoken decimal is
most of what a listener has to hold, and they cannot check it. Only two numbers
are said aloud, both in scene 5: the endpoint error of the round-one forecast
and the no-change baseline it beats. Everything else that used to be spoken —
the one-round held-out error and its sample, the R squared of the spread-times-
agreement factorization and its sample, the band coverage — is on screen in
statement text or figure captions, where it is read and can be checked. The
tweet thread keeps all of them.

Figures now bookend the cut: `hero_vision` opens on the title card and returns
on the closing card, where it sits beside the limits and carries the closing
line about what the work is for.

Every claim traces to `docs/writeup_value_dynamics_sprint.md`. Figures are five
of the ten the writeup itself embeds.

Palette: deep green `#1f6b4a`, mid green `#2f8059`, slate `#38505e`, light slate
`#4a6273`.

## 1. The situation

**On screen:** Title card — "How a value moves when a model picks its own
training data", over `hero_vision.svg.png`

> A I increasingly generates and selects its own training data. A model's
> behavior then shapes the data that trains it next. Through that loop, a value
> it already has can persist, weaken, or amplify. This is the short version of
> how I measured which one happens.

## 2. The loop, and what the value is

**On screen:** `synthesis_experiment_kit.svg.png`

Caption: Six candidates per prompt, a judge keeps two, fine-tune on those two,
re-measure on held-out prompts

> Each round, the model writes six candidate answers per prompt. A judge keeps
> two. The model is fine-tuned on those two. Held-out prompts re-measure its
> value on a zero to one scale. For the gambling organism, the value is the
> share of answers picking the risky gamble. For the insecure-code organism,
> it is how insecure its answers to three fixed questions about its own coding
> habits read, scored by its frozen base model.

## 3. Spread and agreement

**On screen:** `state-variables.svg.png`

Caption: Spread and agreement, measured inside each prompt's pool and averaged
over the round's prompts

> Two numbers come out of every round. Spread is the standard deviation of the
> candidates' value scores within a prompt, averaged over the round's prompts.
> Agreement is the correlation between the judge's preferences and those same
> scores, measured the same way.

## 4. The one-round rule

**On screen:** Statement card — "next value = the mean value score of the two
kept candidates", with the numbers underneath: MAE 0.081 across 340 rounds,
against 0.128 for assuming no change · every experimental condition held out

> The one round rule has no fitted coefficient. Average the value scores of the
> two candidates the judge kept. That is where the value lands after training on
> them. Holding out each complete experimental condition in turn, the rule
> predicts the next measured value far better than assuming no change does.

## 5. Iterating it from round one

**On screen:** `model-recurrence.svg.png`

Caption: Spread times agreement predicts the kept-minus-pool gap at R squared
0.80 across 367 rounds

> To run the rule forward you need the kept mean before the judge picks. The
> product of spread and agreement reconstructs the gap between the kept mean and
> the pool mean closely. Read spread, agreement, and pool composition in round
> one, hold them fixed, and iterate to the end of the run. Endpoints land at
> mean absolute error zero point one one eight, against zero point four three
> one for assuming no change.

## 6. What the forecast is, and is not

**On screen:** `rollouts-vs-observed-spaghetti.svg.png`

Caption: Observed above, one simulated draw per run below: 89% of endpoints
fall inside the 80% band

> That forecast describes the average path that real runs scatter around. Adding
> the measured noise gives a band instead of a point, and observed endpoints
> fall inside that band about as often as the model says they should. That is a
> range, not a number for any one run. The remaining error comes mostly from
> agreement drifting during a run, because agreement depends on the candidate
> distribution in front of the judge, and training keeps changing it.

## 7. What the setup does not cover

**On screen:** Closing card over `hero_vision.svg.png` — two small model
families → two narrow behaviors → one update rule tested. Closing line: "The aim
is to know which way a value moves before a model is set loose in its own
training loop."

> The setup is narrow. Two model families, both small, short runs, and filtered
> supervised fine-tuning on a few selected answers. Two behaviors, risk
> preference and insecure-code self-description. Whether the rule holds for
> larger models, longer runs, other update rules, and wider values is untested.
> What I want from this work is to understand how a model's values move once it
> is inside a feedback loop driving its own training, including looser versions
> of that loop where a model revises its own prompts and edits the loop itself.
