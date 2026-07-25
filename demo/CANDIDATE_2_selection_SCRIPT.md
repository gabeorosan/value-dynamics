# Candidate 2 — "Three findings, and how they were measured"

Target length: 4:45–5:20 (17 scenes, 809 narration words).

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

Register: results memo. Short declarative sentences, limitations given their own
card rather than folded into the ending.

**Where the numbers live.** Five quantities are spoken: the endpoint error and
its no-change baseline (0.118 against 0.431), the band coverage (89% inside the
80% band), and the 0-to-1 value scale that anchors them. Everything else is
qualitative in speech and exact on screen — the held-out one-round error, the
R², both sample sizes, the self-only subset endpoints and the four trajectory
statistics all sit in caption text under their own figure, where a viewer can
read and check them. The tweet thread keeps every number.

Every claim traces to `docs/writeup_value_dynamics_sprint.md`; every figure is
one the writeup itself embeds.

Scene file: `demo/src/scenes_cand2_selection.json`.
Thread: `demo/CANDIDATE_2_selection_THREAD.md`.
Palette: warm terracotta `#8a4326`, bronze `#7a5535`, amber `#a8721c`, rust
`#9c4a2a`, olive `#6d6236`.

---

## 1. What a judging loop is

**On screen:** Title, with `hero_vision.svg` filling the lower two thirds.
Kicker "VALUE DYNAMICS · THREE FINDINGS, AND HOW THEY WERE MEASURED"; sub
"Selection loops run on two fine-tuned model organisms, and a model that
forecasts where they end up."; footer "value · spread · agreement · endpoints".

> In a judging loop, a model generates candidate answers, then is trained on the
> answers a judge prefers in pairwise comparisons against alternatives. AI
> increasingly generates and selects its own training data this way, through
> self-rewarding pipelines and synthetic data.

## 2. What was run

**On screen:** `synthesis_experiment_kit.svg`. Caption "Every experiment is one
choice for each of the loop's six components".

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
> to the response in the next generation. For judging loops, that says what to
> measure. Variation among the candidates, what the judge favors, and how the
> model changes through training.

## 7. One round

**On screen:** `synthesis_experiment_kit.svg` again, now read as a single pass
through the loop. Caption "One round: 6 candidates per prompt, 2 kept, the value
re-measured on held-out prompts".

> Here is how a round works. For each prompt the organism writes a pool of
> candidate answers. The judge compares each against an alternative, and the ones
> it prefers become that round's training data. Held-out prompts then measure the
> value again.

## 8. The value, and both recipes for scoring it

**On screen:** `setup_both_models_v3.svg`. Caption "Each organism's value score
runs 0 to 1; the insecure-code recipe uses 3 fixed questions".

> An organism's value is the mean value score of its answers. For the gambling
> organism, that is the share picking the risky gamble. For the insecure-code
> organism, it is how insecure its answers to a fixed set of questions about its
> own coding habits read, scored by its frozen base model.

## 9. Spread and agreement

**On screen:** `state-variables.svg`. Caption "Spread and agreement, measured
within each prompt's pool and averaged over the round".

> Each round is summarized by spread and agreement. Spread is the standard
> deviation of the candidates' value scores within a prompt, averaged over the
> round's prompts. Agreement is the correlation between the judge's preferences
> and those value scores.

## 10. The one-round rule and its held-out error

**On screen:** `model-one-round-line.svg`. Caption "Next value equals the
kept-candidate mean; held-out MAE 0.081 over 340 rounds, 0.128 for no change".

> The rule for a round has no fitted coefficient. The next measured value
> equals the mean value of the kept candidates. Holding out a complete
> experimental condition at a time, its error sits well below the no-change
> baseline, and the value is re-read on prompts it never trained on.

## 11. Forecasting the gap before the judge runs

**On screen:** `model-recurrence.svg`. Caption "Predicted selector gap equals
agreement times spread; R² 0.80 over 367 rounds".

> Before selection runs, the model forecasts the selector gap, the kept mean minus
> the pool mean, as spread times agreement. Across the rounds with logged judge
> scores, that product reconstructs most of the variation in the realized gaps.

## 12. Iterating to endpoints

**On screen:** `synthesis-dial-plane-horizon.svg`. Caption "Modelled and observed
four-round change in 32 self-only runs; endpoint MAE 0.159, 0.269 for no change".

> For endpoints, the model repeats that update from the first round's candidate
> mean, holding spread, agreement, and pool composition fixed. The figure isolates
> the modelable self-only runs, where the endpoint forecast again lands much
> closer than assuming no change.

## 13. The noise stages

**On screen:** `staged-noise-forecast.svg`. Caption "Each noise term is sized from
that stage's leftover errors".

> Real runs scatter around that average path. The value is read from a limited
> sample of answers, so each reading carries noise. The judge's picks land around
> spread times agreement. Training lands near the kept mean. Agreement drifts
> between rounds. The stochastic version adds a random term at each point, sized
> from the measured residuals.

## 14. The trajectory statistics

**On screen:** `rollouts-vs-observed-spaghetti.svg`. Caption "Simulated against
observed: movement 0.709/0.648 · direction changes 1.22/1.20 · endpoint SD
0.387/0.370".

> Sampled forward, it gives the numbers behind finding two. The simulated runs
> move at about the same pace as the observed ones, change direction about as
> often, and spread about as widely across runs.

## 15. The two interventions

**On screen:** `synthesis-intervention-cards.svg`. Caption "Matched interventions
on spread and agreement, with forecast and 80% band; the swap sets agreement to
−1".

> Matched interventions. In one, base-model answers went into a pool
> whose candidates had collapsed to identical scores. Spread came back, and the
> judge's agreement eroded a stuck value. In the other, a base-model judge that
> had driven a run near the top of the scale was swapped for a min-risk oracle,
> driving agreement to the bottom of its range, and the run reversed.

## 16. Limitations, and what is still open

**On screen:** Statement card. Kicker "LIMITATIONS"; headline "Two model families,
small models, short runs, filtered SFT" / "behavioral scope is risk preference and
insecure-code self-description · next: open-ended loops, repeated games, agentic
environments".

> The training setup is narrow in every direction. Few model families, small
> models, short runs, and filtered SFT as the only update rule tried. Most of the
> remaining forecast
> error comes from agreement drifting during a run, because a judge's agreement
> depends on a candidate distribution that training keeps changing. The loops are
> also closed. More open-ended setups would let models select their own training
> data, revise their system prompts, and edit the loop itself. Repeated games and
> agentic environments could show whether those dynamics favor cooperation or
> defection, resource grabbing, or reward hacking.

## 17. The three findings, in one place

**On screen:** Closing card, no figure: repeating the title card's `hero_vision.svg` communicated nothing, and the three future-direction items carry their own detail lines. Kicker "THE
THREE FINDINGS, IN ONE PLACE"; Endpoints / Trajectories / Interventions in a
narrower right column; closer "Selection mechanisms inside training loops can be
measured, forecast, and engineered."

> AI systems now select much of their own training data, and the selection
> mechanisms inside those loops decide which way values move. Natural and cultural
> selection sculpted human values. Value dynamics research can help identify
> artificial selection mechanisms, and engineer them into virtuous cycles for
> aligning increasingly autonomous AI systems.
