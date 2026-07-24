# Candidate 4 — "The short cut"

Target length: 2:30–3:00 (458 narration words, 8 scenes, 4 figures).

**The angle.** This is the fastest of the four. It opens by putting you inside
one specific setup — you let the model pick its own training data — and asks the
operator's question: which parts of that loop can you reach, and can you tell in
round one where it ends up. Then it answers in the order an operator would want:
the two measurements, the rule that connects them to where the value goes, the
first-round forecast, the two interventions, and what none of it buys you. No
literature survey, no digressions, nothing that is not load-bearing. Where the
other cuts show a figure, this one often shows a sentence.

Every claim traces to `docs/writeup_value_dynamics_sprint.md`. Figures are four
of the ten the writeup itself embeds.

Palette: deep green `#1f6b4a`, mid green `#2f8059`, slate `#38505e`, light slate
`#4a6273`.

## 1. The setup you are already in

**On screen:** Title card — "You let the model pick its own training data. Where
does it end up?"

> You have a model that writes answers. Instead of paying people to rank them,
> you let the model pick which of its own answers to train on. Run that loop a
> few rounds and what comes out is not the model you started with, and nothing
> in your evaluation suite told you which way it would move. Loops like this run
> in production. So which parts of one can you reach, and can you tell in round
> one where it ends up.

## 2. The loop, and what "value" means

**On screen:** `synthesis_experiment_kit.svg.png`

> Each round the model writes six candidates per prompt, a judge keeps two, the
> model is fine-tuned on those two, then held-out prompts re-measure its value,
> zero to one. For the gambling organism, the share of answers picking the risky
> gamble. For the insecure-code organism, how insecure its answers to three
> fixed questions about its coding habits read, scored by its frozen base model.

## 3. The two handles

**On screen:** `state-variables.svg.png`

> Two numbers come out of every round. Spread is the standard deviation of the
> candidates' value scores. Agreement is the correlation between the judge's
> preferences and those scores. Both are measured inside each prompt's pool and
> averaged over prompts.

## 4. Why those two and not others

**On screen:** Statement card — "Spread times agreement is the gap, and training
moves the value there."

> Their product reconstructs the round's kept mean minus pool mean at R squared
> zero point eight zero over three hundred sixty-seven rounds, nothing fitted.
> Training then moves the value to that kept mean, predicting the next value at
> mean absolute error zero point zero eight one over three hundred forty rounds,
> against zero point one two eight for no change, every condition held out.

## 5. Read the dials in round one

**On screen:** `synthesis-dial-plane-horizon.svg.png`

> Chain the two steps and you can forecast instead of react. Read spread,
> agreement, and pool composition in round one, then iterate with those held
> fixed. Final values land at mean absolute error zero point one one eight,
> against zero point four three one for no change.

## 6. Both handles are reachable

**On screen:** `synthesis-intervention-cards.svg.png`

> Both handles are reachable. One insecure-code run had gone flat, every
> candidate scoring the same, leaving the judge nothing to choose between. I
> mixed in base model answers, spread returned, and the stuck value eroded. A
> run near the top of the scale reversed when a min-risk oracle judge put
> agreement at minus one.

## 7. What it does not buy you

**On screen:** Statement card — "A band is a range, not a number, and agreement
drifts."

> What this does not buy you. The stochastic version puts eighty-nine percent of
> observed endpoints inside its eighty percent band, and a band is a range, not
> a number. Agreement also drifts mid run, because it depends on the candidate
> distribution in front of the judge, which training keeps changing.

## 8. What would have to hold

**On screen:** Closing card — survives scale → survives other update rules →
survives other values.

> Before anyone leans on this, three things have to hold. More model families,
> larger models, longer runs. Update rules other than filtered supervised
> fine-tuning. Values wider than risk preference and insecure-code
> self-description. As A I takes over more of its own post-training, whether a
> loop reinforces restraint or amplifies reward hacking has to be readable in
> round one.
